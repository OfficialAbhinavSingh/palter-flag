"""Paired McNemar tests, baseline vs imply, on the same items."""
import sys
from pathlib import Path

import pandas as pd
from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parents[1]
run = sys.argv[1] if len(sys.argv) > 1 else "pilot"
res = pd.read_csv(ROOT / "results" / run / "results_graded.csv")

rows = []
for model, g in res.groupby("model"):
    p = g.pivot(index="task_id", columns="condition", values="honesty")
    for outcome, code in [("lie", -1), ("honest", 1)]:
        only_base = int(((p.baseline == code) & (p.imply != code)).sum())
        only_imply = int(((p.baseline != code) & (p.imply == code)).sum())
        pval = mcnemar([[0, only_base], [only_imply, 0]], exact=True).pvalue
        rows.append({"model": model, "outcome": outcome, "n_items": len(p),
                     "baseline_only": only_base, "imply_only": only_imply,
                     "mcnemar_exact_p": round(pval, 4)})
out = pd.DataFrame(rows)
out.to_csv(ROOT / "results" / run / "paired_tests.csv", index=False)
print(out.to_string(index=False))
