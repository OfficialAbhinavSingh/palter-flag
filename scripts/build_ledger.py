"""Claims ledger: recompute every number the report states and check it against the text.

Each claim lists the value as written in the report, a function that recomputes it
from tracked files, and the source. Writes docs/claims_ledger.md and exits non-zero
if any claim no longer matches, so the report cannot drift from the data.
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


def tool(rule, col):
    t = pd.read_csv(R / "labels/tool_vs_human.csv").set_index("rule")
    return t.loc[rule, col]


def spans(lab, col):
    return pd.read_csv(R / "labels/span_stats.csv").set_index("consensus").loc[lab, col]


def pilot_cost():
    path = ROOT / "outputs/pilot/calls.jsonl"
    if not path.exists():
        return None
    return sum(json.loads(line).get("cost", 0) for line in path.read_text().splitlines())


L, G = "meta-llama/llama-3.3-70b-instruct", "openai/gpt-4o-mini"
AGREED, EITHER = "agreed only (disputed = not lie)", "either annotator says Y"

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
    ("4.2", "Agreed misleading, imply condition", "39/42", lambda: agreed_rate(condition="imply"), "annotations/pilot/"),
    ("4.2", "Agreed misleading, baseline condition", "12/17", lambda: agreed_rate(condition="baseline"), "annotations/pilot/"),
    ("4.2", "Llama agreed misleading, imply vs baseline", "18/20 vs 4/7",
     lambda: f"{agreed_rate(L, 'imply')} vs {agreed_rate(L, 'baseline')}", "annotations/pilot/"),
    ("4.2", "GPT-4o-mini agreed misleading, imply vs baseline", "21/22 vs 8/10",
     lambda: f"{agreed_rate(G, 'imply')} vs {agreed_rate(G, 'baseline')}", "annotations/pilot/"),
    ("Table 2", "Llama corrected honesty, agreed only", "35.0 → 26.7 (-8.3)", lambda: bound(AGREED, "llama-3.3-70b-instruct"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "GPT-4o-mini corrected honesty, agreed only", "45.0 → 33.3 (-11.7)", lambda: bound(AGREED, "gpt-4o-mini"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "Llama corrected honesty, either annotator", "33.3 → 10.0 (-23.3)", lambda: bound(EITHER, "llama-3.3-70b-instruct"), "results/labels/corrected_bounds.csv"),
    ("Table 2", "GPT-4o-mini corrected honesty, either annotator", "36.7 → 18.3 (-18.4)", lambda: bound(EITHER, "gpt-4o-mini"), "results/labels/corrected_bounds.csv"),
    ("Table 3", "Agreed answers scored (misleading / not)", "59 (51 / 8)",
     lambda: f"{int(tool('any_span', 'n'))} ({int(tool('any_span', 'tp') + tool('any_span', 'fn'))} / {int(tool('any_span', 'tn') + tool('any_span', 'fp'))})", "results/labels/tool_vs_human.csv"),
    ("Table 3", "Any span: flagged, precision, recall, specificity, BA", "59/59, 0.86, 1.00, 0/8, 0.50",
     lambda: f"{int(tool('any_span', 'tp') + tool('any_span', 'fp'))}/{int(tool('any_span', 'n'))}, {tool('any_span', 'precision'):.2f}, {tool('any_span', 'recall'):.2f}, {int(tool('any_span', 'tn'))}/{int(tool('any_span', 'tn') + tool('any_span', 'fp'))}, {tool('any_span', 'balanced_acc'):.2f}", "results/labels/tool_vs_human.csv"),
    ("Table 3", "Persuading span: flagged, precision, recall, specificity, BA", "51/59, 0.92, 0.92, 4/8, 0.71",
     lambda: f"{int(tool('any_persuading_span', 'tp') + tool('any_persuading_span', 'fp'))}/{int(tool('any_persuading_span', 'n'))}, {tool('any_persuading_span', 'precision'):.2f}, {tool('any_persuading_span', 'recall'):.2f}, {int(tool('any_persuading_span', 'tn'))}/{int(tool('any_persuading_span', 'tn') + tool('any_persuading_span', 'fp'))}, {tool('any_persuading_span', 'balanced_acc'):.2f}", "results/labels/tool_vs_human.csv"),
    ("4.3", "Mean flagged spans, misleading vs not", "4.9 vs 2.5",
     lambda: f"{spans('Y', 'mean_spans'):.1f} vs {spans('N', 'mean_spans'):.1f}", "results/labels/span_stats.csv"),
    ("4.3", "Empty reassurance present, misleading vs not", "90% vs 25%",
     lambda: f"{spans('Y', 'share_empty_reassurance'):.0%} vs {spans('N', 'share_empty_reassurance'):.0%}", "results/labels/span_stats.csv"),
    ("4.3", "Non-misleading answers tagged non-answer", "5 of 8",
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
           "Every number stated in the report, recomputed from tracked files by `scripts/build_ledger.py`.",
           "A ✗ means the report text and the data disagree; the script exits non-zero.", "",
           "| Section | Claim | In report | Recomputed | Source | Check |", "|---|---|---|---|---|---|", *rows, ""]
    (ROOT / "docs/claims_ledger.md").write_text("\n".join(out))
    print("\n".join(rows))
    checked = len(CLAIMS) - skipped
    print(f"\n{checked - bad}/{checked} checkable claims match" + (f"; {skipped} need the local API cache" if skipped else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
