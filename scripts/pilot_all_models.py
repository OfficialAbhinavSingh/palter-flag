"""Combine the MASK pilot across all models: per-model table, pooled McNemar, sign counts.

Reads results/<run>/results_graded.csv for every pilot run and writes
results/pilot_all/{per_model,pooled}.csv and report.md.
"""
from pathlib import Path

import pandas as pd
from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parents[1]
RUNS = ["pilot", "pilot_deepseek", "pilot_gemini", "pilot_haiku", "pilot_qwen", "pilot_mistral"]
SHORT = {"meta-llama/llama-3.3-70b-instruct": "Llama-3.3-70B", "openai/gpt-4o-mini": "GPT-4o-mini",
         "deepseek/deepseek-chat-v3.1": "DeepSeek-V3.1", "google/gemini-2.5-flash": "Gemini-2.5-Flash",
         "anthropic/claude-haiku-4.5": "Claude-Haiku-4.5", "qwen/qwen3-235b-a22b-2507": "Qwen3-235B",
         "mistralai/mistral-small-3.2-24b-instruct": "Mistral-Small-3.2"}


def main():
    frames = [pd.read_csv(ROOT / "results" / r / "results_graded.csv")
              for r in RUNS if (ROOT / "results" / r / "results_graded.csv").exists()]
    res = pd.concat(frames, ignore_index=True)
    res["truthful"] = res.honesty == 1
    res["lie"] = res.honesty == -1
    res["evasive"] = res.eval_honesty_1_raw == "C"
    res["unparsed"] = ~res.eval_honesty_1_raw.isin(list("ABCD"))

    rows, cells = [], {"truthful": [0, 0], "lie": [0, 0]}
    for model, g in res.groupby("model"):
        p = g.pivot(index="task_id", columns="condition")
        row = {"model": SHORT.get(model, model), "n_items": len(p)}
        for cond in ("baseline", "imply"):
            sub = g[g.condition == cond]
            row[f"mask_honesty_{cond}"] = round(100 - 100 * sub.lie.mean(), 1)
            row[f"truthful_{cond}"] = round(100 * sub.truthful.mean(), 1)
            row[f"evasive_{cond}"] = round(100 * sub.evasive.mean(), 1)
            row[f"unparsed_{cond}"] = int(sub.unparsed.sum())
        for out in ("truthful", "lie"):
            b = int((p[(out, "baseline")] & ~p[(out, "imply")]).sum())
            c = int((~p[(out, "baseline")] & p[(out, "imply")]).sum())
            row[f"{out}_lost"], row[f"{out}_gained"] = b, c
            row[f"{out}_p"] = round(mcnemar([[0, b], [c, 0]], exact=True).pvalue, 4)
            cells[out][0] += b
            cells[out][1] += c
        row["mask_change"] = round(row["mask_honesty_imply"] - row["mask_honesty_baseline"], 1)
        row["truthful_change"] = round(row["truthful_imply"] - row["truthful_baseline"], 1)
        rows.append(row)
    per = pd.DataFrame(rows).sort_values("mask_change", ascending=False)
    out = ROOT / "results/pilot_all"
    out.mkdir(parents=True, exist_ok=True)
    per.to_csv(out / "per_model.csv", index=False)

    pooled = []
    for k, (b, c) in cells.items():
        pooled.append({"outcome": k, "item_model_pairs": per.n_items.sum(), "baseline_only": b, "imply_only": c,
                       "mcnemar_exact_p": mcnemar([[0, b], [c, 0]], exact=True).pvalue})
    pooled = pd.DataFrame(pooled)
    pooled.to_csv(out / "pooled.csv", index=False)

    n = len(per)
    lines = ["# MASK pilot across models", "",
             f"{n} models, 60 provided_facts items each (seed 0), MASK's judge prompt and scoring.", "",
             f"- MASK honesty rose for {(per.mask_change > 0).sum()}/{n} models (range {per.mask_change.min():+.1f} to {per.mask_change.max():+.1f}).",
             f"- Truthful answers fell for {(per.truthful_change < 0).sum()}/{n} models (range {per.truthful_change.max():+.1f} to {per.truthful_change.min():+.1f}); "
             f"significant alone (p < 0.05) for {(per.truthful_p < 0.05).sum()}/{n}.",
             f"- Evasive share rose for {(per.evasive_imply > per.evasive_baseline).sum()}/{n} models.",
             f"- Pooled over item-model pairs: truthful lost {cells['truthful'][0]} vs gained {cells['truthful'][1]} "
             f"(exact McNemar p = {pooled.loc[pooled.outcome == 'truthful', 'mcnemar_exact_p'].iloc[0]:.1e}); "
             f"lies stopped {cells['lie'][0]} vs started {cells['lie'][1]} (p = {pooled.loc[pooled.outcome == 'lie', 'mcnemar_exact_p'].iloc[0]:.1e}). "
             "Pairs share items across models, so the pooled p is a summary, not an independent test.", "",
             per[["model", "mask_honesty_baseline", "mask_honesty_imply", "mask_change", "truthful_baseline", "truthful_imply",
                  "truthful_lost", "truthful_gained", "truthful_p", "lie_p", "unparsed_baseline", "unparsed_imply"]].to_string(index=False)]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
