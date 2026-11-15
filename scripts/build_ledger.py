"""Recompute the selected numerical claims enumerated in CLAIMS.

Expected values are maintained here by hand. This does not parse the report or
establish that every number or statement in a DOCX/PDF has been checked. Each
entry compares its expected value with the named source files, some of which are
tracked analysis outputs rather than raw observations. Local-cache claims may
be unavailable in a public clone. Writes docs/claims_ledger.md and exits non-zero
on mismatches. A successful exit does not mean skipped entries were verified.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"


def summary():
    return pd.read_csv(R / "pilot/summary.csv").set_index(["model", "condition"])


def paired():
    return pd.read_csv(R / "pilot/paired_tests.csv").set_index(["model", "outcome"])


def labels():
    a = pd.read_csv(ROOT / "annotations/pilot/label_sheet_abhinav.csv")
    m = pd.read_csv(ROOT / "annotations/pilot/label_sheet_mahak.csv")
    k = pd.read_csv(ROOT / "annotations/pilot/label_key.csv")
    d = a[["label_id", "misleading (Y/N)"]].merge(m[["label_id", "misleading (Y/N)"]], on="label_id")
    d.columns = ["label_id", "a", "m"]
    return d.merge(k, on="label_id")


def agreed_rate(model=None, condition=None):
    d = labels()
    d = d[d.a == d.m]
    if model:
        d = d[d.model == model]
    if condition:
        d = d[d.condition == condition]
    return f"{(d.a == 'Y').sum()}/{len(d)}"


def bound(rule, model):
    b = pd.read_csv(R / "labels/corrected_bounds.csv")
    r = b[(b.rule == rule) & (b.model == model)].iloc[0]
    return f"{r.baseline:.1f} → {r.imply:.1f} ({r.change:+.1f})"


def tool2(labels_set, rule):
    return pd.read_csv(R / "labels/tool_vs_human.csv").set_index(["labels", "rule"]).loc[(labels_set, rule)]


def tool_row(labels_set, rule):
    r = tool2(labels_set, rule)
    return (f"{int(r.tp + r.fp)}/{int(r.n)}, {r.precision:.2f}, {r.recall:.2f}, "
            f"{int(r.tn)}/{int(r.tn + r.fp)}, {r.balanced_acc:.2f}")


def spans(lab, col):
    return pd.read_csv(R / "labels/span_stats.csv").set_index("consensus").loc[lab, col]


def pilot_cost():
    path = ROOT / "outputs/pilot/calls.jsonl"
    if not path.exists():
        return None
    return sum(json.loads(line).get("cost", 0) for line in path.read_text().splitlines())


def per_model(name):
    return pd.read_csv(R / "pilot_all/per_model.csv").set_index("model").loc[name]


def fa():
    return pd.read_csv(R / "false_alarm/summary.csv")


def pooled(outcome):
    return pd.read_csv(R / "pilot_all/pooled.csv").set_index("outcome").loc[outcome]

VENDOR = {"GPT-4o-mini": "OpenAI", "Llama-3.3-70B": "Meta", "DeepSeek-V3.1": "DeepSeek", "Gemini-2.5-Flash": "Google",
          "Claude-Haiku-4.5": "Anthropic", "Qwen3-235B": "Alibaba", "Mistral-Small-3.2": "Mistral"}
L, G = "meta-llama/llama-3.3-70b-instruct", "openai/gpt-4o-mini"

CLAIMS = [
    # (section, claim, value as written, recompute, source)
    ("4.1", "Llama MASK honesty, baseline → imply", "41.7 → 56.7",
     lambda: f"{summary().loc[(L, 'baseline'), 'mask_honesty_score']:.1f} → {summary().loc[(L, 'imply'), 'mask_honesty_score']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "GPT-4o-mini MASK honesty, baseline → imply", "58.3 → 68.3",
     lambda: f"{summary().loc[(G, 'baseline'), 'mask_honesty_score']:.1f} → {summary().loc[(G, 'imply'), 'mask_honesty_score']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "Llama truthful %, baseline → imply", "28.3 → 6.7",
     lambda: f"{summary().loc[(L, 'baseline'), 'honest']:.1f} → {summary().loc[(L, 'imply'), 'honest']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "GPT-4o-mini truthful %, baseline → imply", "33.3 → 16.7",
     lambda: f"{summary().loc[(G, 'baseline'), 'honest']:.1f} → {summary().loc[(G, 'imply'), 'honest']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "Llama lie %, baseline → imply", "58.3 → 43.3",
     lambda: f"{summary().loc[(L, 'baseline'), 'lie']:.1f} → {summary().loc[(L, 'imply'), 'lie']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "GPT-4o-mini lie %, baseline → imply", "41.7 → 31.7",
     lambda: f"{summary().loc[(G, 'baseline'), 'lie']:.1f} → {summary().loc[(G, 'imply'), 'lie']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "Llama evasive %, baseline → imply", "13.3 → 50.0",
     lambda: f"{summary().loc[(L, 'baseline'), 'C']:.1f} → {summary().loc[(L, 'imply'), 'C']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "GPT-4o-mini evasive %, baseline → imply", "25.0 → 51.7",
     lambda: f"{summary().loc[(G, 'baseline'), 'C']:.1f} → {summary().loc[(G, 'imply'), 'C']:.1f}", "results/pilot/summary.csv"),
    ("4.1", "Llama truthful: lost vs gained, McNemar p", "14 vs 1, p = 0.001",
     lambda: f"{paired().loc[(L, 'honest'), 'baseline_only']} vs {paired().loc[(L, 'honest'), 'imply_only']}, p = {paired().loc[(L, 'honest'), 'mcnemar_exact_p']:.3f}", "results/pilot/paired_tests.csv"),
    ("4.1", "GPT-4o-mini truthful: lost vs gained, McNemar p", "13 vs 3, p = 0.02",
     lambda: f"{paired().loc[(G, 'honest'), 'baseline_only']} vs {paired().loc[(G, 'honest'), 'imply_only']}, p = {paired().loc[(G, 'honest'), 'mcnemar_exact_p']:.2f}", "results/pilot/paired_tests.csv"),
    ("4.1", "Llama lies: stopped vs started, McNemar p", "13 vs 4, p = 0.049",
     lambda: f"{paired().loc[(L, 'lie'), 'baseline_only']} vs {paired().loc[(L, 'lie'), 'imply_only']}, p = {paired().loc[(L, 'lie'), 'mcnemar_exact_p']:.3f}", "results/pilot/paired_tests.csv"),
    ("4.1", "GPT-4o-mini lies: stopped vs started, McNemar p", "9 vs 3, p = 0.15",
     lambda: f"{paired().loc[(G, 'lie'), 'baseline_only']} vs {paired().loc[(G, 'lie'), 'imply_only']}, p = {paired().loc[(G, 'lie'), 'mcnemar_exact_p']:.2f}", "results/pilot/paired_tests.csv"),
    ("4.1", "Models tested; vendors", "7; 7",
     lambda: (lambda d: f"{len(d)}; {len({VENDOR[m] for m in d.model})}")(pd.read_csv(R / "pilot_all/per_model.csv")), "results/pilot_all/per_model.csv"),
    ("4.1", "Models whose truthful share fell", "7 of 7",
     lambda: (lambda d: f"{(d.truthful_change < 0).sum()} of {len(d)}")(pd.read_csv(R / "pilot_all/per_model.csv")), "results/pilot_all/per_model.csv"),
    ("4.1", "Range of truthful drop (points)", "7 to 23",
     lambda: (lambda d: f"{-d.truthful_change.max():.0f} to {-d.truthful_change.min():.0f}")(pd.read_csv(R / "pilot_all/per_model.csv")), "results/pilot_all/per_model.csv"),
    ("4.1", "Models whose MASK honesty rose; range (points)", "6 of 7; 8 to 20",
     lambda: (lambda d: f"{(d.mask_change > 0).sum()} of {len(d)}; {d[d.mask_change > 0].mask_change.min():.0f} to {d.mask_change.max():.0f}")(pd.read_csv(R / "pilot_all/per_model.csv")), "results/pilot_all/per_model.csv"),
    ("4.1", "Truthful drop significant alone (p < 0.05)", "3 of 7",
     lambda: (lambda d: f"{(d.truthful_p < 0.05).sum()} of {len(d)}")(pd.read_csv(R / "pilot_all/per_model.csv")), "results/pilot_all/per_model.csv"),
    ("4.1", "Pooled truthful lost vs gained (420 pairs)", "72 vs 16",
     lambda: f"{int(pooled('truthful').baseline_only)} vs {int(pooled('truthful').imply_only)}", "results/pilot_all/pooled.csv"),
    ("4.1", "Pooled McNemar p, order of magnitude", "1e-09",
     lambda: f"{pooled('truthful').mcnemar_exact_p:.0e}".replace("e-0", "e-0"), "results/pilot_all/pooled.csv"),
    ("4.1", "Claude-Haiku-4.5 MASK honesty; truthful %", "93.3 → 90.0; 71.7 → 48.3",
     lambda: (lambda r: f"{r.mask_honesty_baseline:.1f} → {r.mask_honesty_imply:.1f}; {r.truthful_baseline:.1f} → {r.truthful_imply:.1f}")(per_model("Claude-Haiku-4.5")), "results/pilot_all/per_model.csv"),
    ("3.1", "Grader outputs not parsed (of 840)", "2",
     lambda: str(int(pd.read_csv(R / "pilot_all/per_model.csv")[["unparsed_baseline", "unparsed_imply"]].sum().sum())), "results/pilot_all/per_model.csv"),
    ("4.3", "Truthful answers checked for false alarms", "40", lambda: str(len(fa())), "results/false_alarm/summary.csv"),
    ("4.3", "Truthful answers with any span; persuading span", "31 of 40; 22 of 40",
     lambda: (lambda d: f"{d.any_span.sum()} of {len(d)}; {d.any_persuading.sum()} of {len(d)}")(fa()), "results/false_alarm/summary.csv"),
    ("4.3", "Mean spans on truthful answers", "3.3", lambda: f"{fa().n_spans.mean():.1f}", "results/false_alarm/summary.csv"),
    ("4.3", "Verdict 'not answered': truthful vs evasive", "4 of 40 vs 73 of 84",
     lambda: f"{(fa().answered == 'no').sum()} of {len(fa())} vs {sum(v['answered'] == 'no' for v in json.loads((R / 'labels/flags_v02.json').read_text()).values())} of 84",
     "results/false_alarm/summary.csv, results/labels/flags_v02.json"),
    ("3.3/4.2", "Evasive answers labelled", "84", lambda: str(len(labels())), "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "Raw annotator agreement", "59 of 84 (70%)",
     lambda: (lambda d: f"{(d.a == d.m).sum()} of {len(d)} ({(d.a == d.m).mean():.0%})")(labels()), "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "Cohen's κ", "0.19", lambda: f"{cohen_kappa_score(labels().a, labels().m):.2f}", "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "κ 95% CI (bootstrap over items)", "−0.03 to 0.41",
     lambda: (lambda r: f"{r.ci_low:.2f} to {r.ci_high:.2f}".replace("-", "−"))(pd.read_csv(R / "labels/agreement.csv").iloc[0]), "results/labels/agreement.csv"),
    ("4.2", "PABAK (2 × agreement − 1)", "0.40", lambda: (lambda d: f"{2 * (d.a == d.m).mean() - 1:.2f}")(labels()), "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "Share labelled misleading (A.S., M.A.)", "75%, 76%",
     lambda: (lambda d: f"{(d.a == 'Y').mean():.0%}, {(d.m == 'Y').mean():.0%}")(labels()), "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "Disagreements, split", "25 (13 / 12)",
     lambda: (lambda d: f"{(d.a != d.m).sum()} ({((d.a == 'N') & (d.m == 'Y')).sum()} / {((d.a == 'Y') & (d.m == 'N')).sum()})")(labels()), "annotations/pilot/label_sheet_*.csv"),
    ("4.2", "Agreed misleading, imply vs baseline", "39 of 42 vs 12 of 17",
     lambda: f"{agreed_rate(condition='imply').replace('/', ' of ')} vs {agreed_rate(condition='baseline').replace('/', ' of ')}", "annotations/pilot/"),
    ("4.2", "Adjudicated misleading, imply vs baseline", "50 of 61 vs 13 of 23",
     lambda: (lambda b: f"{b[b.condition == 'imply'].misleading.sum()} of {b[b.condition == 'imply'].n.sum()} vs {b[b.condition == 'baseline'].misleading.sum()} of {b[b.condition == 'baseline'].n.sum()}")(pd.read_csv(R / "labels/by_condition.csv")), "results/labels/by_condition.csv"),
    ("4.2", "Adjudicated misleading, Llama imply vs baseline", "23/30 vs 4/8",
     lambda: (lambda b: f"{int(b.loc[(L, 'imply')].misleading)}/{int(b.loc[(L, 'imply')].n)} vs {int(b.loc[(L, 'baseline')].misleading)}/{int(b.loc[(L, 'baseline')].n)}")(pd.read_csv(R / "labels/by_condition.csv").set_index(["model", "condition"])), "results/labels/by_condition.csv"),
    ("4.2", "Adjudicated misleading, GPT-4o-mini imply vs baseline", "27/31 vs 9/15",
     lambda: (lambda b: f"{int(b.loc[(G, 'imply')].misleading)}/{int(b.loc[(G, 'imply')].n)} vs {int(b.loc[(G, 'baseline')].misleading)}/{int(b.loc[(G, 'baseline')].n)}")(pd.read_csv(R / "labels/by_condition.csv").set_index(["model", "condition"])), "results/labels/by_condition.csv"),
    ("3.3", "Disputes resolved to first author: N / Y", "13 / 12",
     lambda: (lambda a: f"{(a.final == 'N').sum()} / {(a.final == 'Y').sum()}")(pd.read_csv(ROOT / "annotations/pilot/adjudication.csv")), "annotations/pilot/adjudication.csv"),
    ("Table 2", "Llama corrected, adjudicated", "35.0 → 18.3 (-16.7)", lambda: bound("adjudicated", "llama-3.3-70b-instruct"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "GPT-4o-mini corrected, adjudicated", "43.3 → 23.3 (-20.0)", lambda: bound("adjudicated", "gpt-4o-mini"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "Llama corrected, agreed only", "35.0 → 26.7 (-8.3)", lambda: bound("agreed only", "llama-3.3-70b-instruct"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "GPT-4o-mini corrected, agreed only", "45.0 → 33.3 (-11.7)", lambda: bound("agreed only", "gpt-4o-mini"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "Llama range of change over all resolutions", "-25.0 to -6.7",
     lambda: (lambda b: f"{b.loc[('least favourable to MASK', 'llama-3.3-70b-instruct'), 'change']:.1f} to {b.loc[('most favourable to MASK', 'llama-3.3-70b-instruct'), 'change']:.1f}")(pd.read_csv(R / "labels/corrected_bounds.csv").set_index(["rule", "model"])), "results/labels/corrected_bounds.csv"),
    ("Table 2", "GPT-4o-mini range of change over all resolutions", "-26.7 to -3.3",
     lambda: (lambda b: f"{b.loc[('least favourable to MASK', 'gpt-4o-mini'), 'change']:.1f} to {b.loc[('most favourable to MASK', 'gpt-4o-mini'), 'change']:.1f}")(pd.read_csv(R / "labels/corrected_bounds.csv").set_index(["rule", "model"])), "results/labels/corrected_bounds.csv"),
    ("Table 3", "Adjudicated labels: misleading / not", "63 / 21",
     lambda: (lambda r: f"{int(r.tp + r.fn)} / {int(r.tn + r.fp)}")(tool2("adjudicated", "any_span")), "results/labels/tool_vs_human.csv"),
    ("Table 3", "Any span (adjudicated): flagged, P, R, spec, BA", "84/84, 0.75, 1.00, 0/21, 0.50", lambda: tool_row("adjudicated", "any_span"), "results/labels/tool_vs_human.csv"),
    ("Table 3", "Persuading span (adjudicated): flagged, P, R, spec, BA", "67/84, 0.84, 0.89, 10/21, 0.68", lambda: tool_row("adjudicated", "any_persuading_span"), "results/labels/tool_vs_human.csv"),
    ("Table 3", "Persuading span (agreed only): flagged, P, R, spec, BA", "51/59, 0.92, 0.92, 4/8, 0.71", lambda: tool_row("agreed_only", "any_persuading_span"), "results/labels/tool_vs_human.csv"),
    ("4.3", "Mean flagged spans, misleading vs not (adjudicated)", "4.9 vs 3.4",
     lambda: f"{spans('Y', 'mean_spans'):.1f} vs {spans('N', 'mean_spans'):.1f}", "results/labels/span_stats.csv"),
    ("4.3", "Non-misleading answers tagged non-answer (adjudicated)", "15 of 21",
     lambda: f"{round(spans('N', 'share_non_answer') * spans('N', 'n'))} of {int(spans('N', 'n'))}", "results/labels/span_stats.csv"),
    ("4.4", "Long answers checked; burying flagged in", "6; 2",
     lambda: (lambda b: f"{len(b)}; {(b.n_burying > 0).sum()}")(pd.read_csv(R / "burying/summary.csv")), "results/burying/summary.csv"),
    ("4.4", "Length range of long answers (characters)", "1,341 to 2,456",
     lambda: (lambda b: f"{b.length.min():,} to {b.length.max():,}")(pd.read_csv(R / "burying/summary.csv")), "results/burying/summary.csv"),
    ("3.2", "Flagger cost per answer", "under 1¢",
     lambda: (lambda f: "under 1¢" if f < 0.01 else f"${f:.4f}")(
         sum(json.loads(x).get("cost", 0) for x in (ROOT / "outputs/flags_v02/calls.jsonl").read_text().splitlines()) / 84)
     if (ROOT / "outputs/flags_v02/calls.jsonl").exists() else None, "outputs/flags_v02/calls.jsonl (local cache)"),
]


def main():
    rows, bad, skipped = [], 0, 0
    for sec, claim, written, fn, src in CLAIMS:
        try:
            got = fn()
        except FileNotFoundError:
            got = None
        if got is None:
            status = "not checkable here (local cache)"
            skipped += 1
        else:
            ok = str(got).replace("-", "−") == written.replace("-", "−")
            status = "✓" if ok else "✗ MISMATCH"
            bad += not ok
        rows.append(f"| {sec} | {claim} | {written} | {got if got is not None else '–'} | `{src}` | {status} |")
    out = ["# Claims ledger", "",
           "Selected claims enumerated in `scripts/build_ledger.py`, checked against the named source files.",
           "Expected values are maintained in the script; it does not parse the DOCX/PDF or verify every report number.",
           "Some checks read tracked analysis outputs. Local-cache entries can be skipped and are not verified.",
           "A ✗ means a listed expected value differs from its recomputed value; the script exits non-zero.", "",
           "| Section | Claim | Expected (in script) | Recomputed | Source | Check |", "|---|---|---|---|---|---|", *rows, ""]
    (ROOT / "docs/claims_ledger.md").write_text("\n".join(out))
    print("\n".join(rows))
    checked = len(CLAIMS) - skipped
    print(f"\n{checked - bad}/{checked} checkable claims match" + (f"; {skipped} need the local API cache" if skipped else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
