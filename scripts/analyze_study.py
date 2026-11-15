"""Analyse the Palter Flag user study.

Outcomes implemented below:
  The supplied paper draft says these were written after the first two responses
  arrived. Do not describe this as pre-registration or as specification before
  all data collection; no prospective status for later responses is established.
  primary     belief in the truth (0-100) on evasive answers, highlighted vs plain
  secondary   trust (1-5) on evasive answers, highlighted vs plain
  backfire    belief in the truth and trust on truthful answers (highlights should not lower them)
  blind spot  the same on outright lies (the tool cannot fact-check)

Every participant sees both conditions within each answer type, so the main
estimate is the within-person difference (highlighted minus plain), averaged
over participants, with a bootstrap CI that resamples participants.

Inputs:  outputs/study_responses/*.json (study/fetch_responses.mjs)
         results/study/items_key.json (answer key, never served to participants)
         annotations/study_exclusions.csv (optional: pid,reason for manual exclusions)
Outputs: results/study/{sessions,summary,by_item}.csv and report.md
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "study"
CURRENT_VERSION = 2
MIN_MEDIAN_SECONDS = 8  # faster than this per item means the answers were not read
TYPES = ["evasive", "truthful", "lie"]
ROLE = {"evasive": "primary / secondary", "truthful": "backfire check", "lie": "blind spot"}


def load():
    key = {i["id"]: i for i in json.loads((ROOT / "results/study/items_key.json").read_text())}
    manual = {}
    ex = ROOT / "annotations/study_exclusions.csv"
    if ex.exists():
        manual = dict(pd.read_csv(ex)[["pid", "reason"]].itertuples(index=False))

    sessions, rows = [], []
    for f in sorted((ROOT / "outputs/study_responses").glob("*.json")):
        d = json.loads(f.read_text())
        res = d["results"]
        med = float(np.median([r["ms"] for r in res])) / 1000
        reasons = []
        if d.get("version") != CURRENT_VERSION:
            reasons.append(f"old version {d.get('version')}")
        if d.get("prior_submission"):
            reasons.append("repeat submission from same browser")
        if len({r["value"] for r in res}) == 1:
            reasons.append("same slider value on every item")
        if med < MIN_MEDIAN_SECONDS:
            reasons.append(f"median {med:.0f}s per item")
        if d["pid"] in manual:
            reasons.append(f"manual: {manual[d['pid']]}")
        sessions.append({"pid": d["pid"], "received_at": d["received_at"], "use": d.get("use"), "src": d.get("src"),
                         "median_sec": round(med, 1), "total_min": round(sum(r["ms"] for r in res) / 60000, 1),
                         "excluded": bool(reasons), "reason": "; ".join(reasons)})
        for r in res:
            k = key[r["item"]]
            truth = r["value"] if k["statement_is_true"] else 100 - r["value"]
            rows.append({"pid": d["pid"], "item": r["item"], "type": k["type"], "highlight": r["highlight"],
                         "belief_truth": truth, "trust": r.get("trust"), "misled": truth < 50,
                         "brier": (1 - truth / 100) ** 2, "sec": r["ms"] / 1000, "order": r["order"]})
    return pd.DataFrame(sessions), pd.DataFrame(rows)


def paired(df, col, rng, n_boot=5000):
    """Within-person highlighted-minus-plain difference, CI by resampling participants."""
    per = df.groupby(["pid", "highlight"])[col].mean().unstack()
    per = per.dropna()  # needs both conditions
    if per.empty:
        return {}
    diff = (per[True] - per[False]).to_numpy()
    boots = [rng.choice(diff, size=len(diff), replace=True).mean() for _ in range(n_boot)]
    out = {"n_people": len(diff), "plain": per[False].mean(), "highlighted": per[True].mean(),
           "diff": diff.mean(), "ci_low": np.percentile(boots, 2.5), "ci_high": np.percentile(boots, 97.5)}
    if len(diff) >= 6 and np.any(diff != 0):
        out["wilcoxon_p"] = wilcoxon(diff).pvalue
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sessions, rows = load()
    sessions.to_csv(OUT / "sessions.csv", index=False)
    if rows.empty:
        print("no responses yet")
        return
    keep = rows[~rows.pid.isin(sessions[sessions.excluded].pid)]
    rng = np.random.default_rng(0)

    summary = []
    for t in TYPES:
        sub = keep[keep.type == t]
        for col in ("belief_truth", "trust", "misled"):
            res = paired(sub.assign(misled=sub.misled.astype(float)), col, rng)
            if res:
                summary.append({"type": t, "role": ROLE[t], "outcome": col, **res})
    summary = pd.DataFrame(summary)
    summary.round(3).to_csv(OUT / "summary.csv", index=False)

    by_item = (keep.groupby(["item", "type", "highlight"])
               .agg(n=("pid", "size"), belief_truth=("belief_truth", "mean"), trust=("trust", "mean"))
               .round(2).reset_index())
    by_item.to_csv(OUT / "by_item.csv", index=False)

    n_in, n_out = (~sessions.excluded).sum(), sessions.excluded.sum()
    lines = [
        "# Palter Flag user study: current results", "",
        f"Sessions: {len(sessions)} received, {n_in} analysed, {n_out} excluded.",
    ]
    for _, s in sessions[sessions.excluded].iterrows():
        lines.append(f"- excluded {s.pid[:8]}: {s.reason}")
    lines += ["", "Within-person difference, highlighted minus plain. Belief is the probability (0-100) a",
              "participant gave to the true answer; trust is 1-5; misled is the share of ratings below 50.", "",
              "| answer type | role | outcome | people | plain | highlighted | difference [95% CI] | Wilcoxon p |",
              "|---|---|---|---:|---:|---:|---|---:|"]
    for _, r in summary.iterrows():
        p = f"{r.wilcoxon_p:.3f}" if "wilcoxon_p" in r and pd.notna(r.get("wilcoxon_p")) else "n<6"
        lines.append(f"| {r.type} | {r.role} | {r.outcome} | {r.n_people} | {r.plain:.2f} | {r.highlighted:.2f} | "
                     f"{r['diff']:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}] | {p} |")
    if n_in < 10:
        lines += ["", f"**Only {n_in} participants. Treat every number above as a pipeline check, not a finding.**"]
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
