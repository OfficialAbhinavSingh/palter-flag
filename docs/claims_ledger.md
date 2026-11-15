# Claims ledger

Every number stated in the report, recomputed from tracked files by `scripts/build_ledger.py`.
A ✗ means the report text and the data disagree; the script exits non-zero.

| Section | Claim | In report | Recomputed | Source | Check |
|---|---|---|---|---|---|
| 4.1 | Llama MASK honesty, baseline → imply | 41.7 → 56.7 | 41.7 → 56.7 | `results/pilot/summary.csv` | ✓ |
| 4.1 | GPT-4o-mini MASK honesty, baseline → imply | 58.3 → 68.3 | 58.3 → 68.3 | `results/pilot/summary.csv` | ✓ |
| 4.1 | Llama truthful %, baseline → imply | 28.3 → 6.7 | 28.3 → 6.7 | `results/pilot/summary.csv` | ✓ |
| 4.1 | GPT-4o-mini truthful %, baseline → imply | 33.3 → 16.7 | 33.3 → 16.7 | `results/pilot/summary.csv` | ✓ |
| 4.1 | Llama lie %, baseline → imply | 58.3 → 43.3 | 58.3 → 43.3 | `results/pilot/summary.csv` | ✓ |
| 4.1 | GPT-4o-mini lie %, baseline → imply | 41.7 → 31.7 | 41.7 → 31.7 | `results/pilot/summary.csv` | ✓ |
| 4.1 | Llama evasive %, baseline → imply | 13.3 → 50.0 | 13.3 → 50.0 | `results/pilot/summary.csv` | ✓ |
| 4.1 | GPT-4o-mini evasive %, baseline → imply | 25.0 → 51.7 | 25.0 → 51.7 | `results/pilot/summary.csv` | ✓ |
| 4.1 | Llama truthful: lost vs gained, McNemar p | 14 vs 1, p = 0.001 | 14 vs 1, p = 0.001 | `results/pilot/paired_tests.csv` | ✓ |
| 4.1 | GPT-4o-mini truthful: lost vs gained, McNemar p | 13 vs 3, p = 0.02 | 13 vs 3, p = 0.02 | `results/pilot/paired_tests.csv` | ✓ |
| 4.1 | Llama lies: stopped vs started, McNemar p | 13 vs 4, p = 0.049 | 13 vs 4, p = 0.049 | `results/pilot/paired_tests.csv` | ✓ |
| 4.1 | GPT-4o-mini lies: stopped vs started, McNemar p | 9 vs 3, p = 0.15 | 9 vs 3, p = 0.15 | `results/pilot/paired_tests.csv` | ✓ |
| 4.1 | Models tested; vendors | 7; 7 | 7; 7 | `results/pilot_all/per_model.csv` | ✓ |
| 4.1 | Models whose truthful share fell | 7 of 7 | 7 of 7 | `results/pilot_all/per_model.csv` | ✓ |
| 4.1 | Range of truthful drop (points) | 7 to 23 | 7 to 23 | `results/pilot_all/per_model.csv` | ✓ |
| 4.1 | Models whose MASK honesty rose; range (points) | 6 of 7; 8 to 20 | 6 of 7; 8 to 20 | `results/pilot_all/per_model.csv` | ✓ |
| 4.1 | Truthful drop significant alone (p < 0.05) | 3 of 7 | 3 of 7 | `results/pilot_all/per_model.csv` | ✓ |
| 4.1 | Pooled truthful lost vs gained (420 pairs) | 72 vs 16 | 72 vs 16 | `results/pilot_all/pooled.csv` | ✓ |
| 4.1 | Pooled McNemar p, order of magnitude | 1e-09 | 1e-09 | `results/pilot_all/pooled.csv` | ✓ |
| 4.1 | Claude-Haiku-4.5 MASK honesty; truthful % | 93.3 → 90.0; 71.7 → 48.3 | 93.3 → 90.0; 71.7 → 48.3 | `results/pilot_all/per_model.csv` | ✓ |
| 3.1 | Grader outputs not parsed (of 840) | 2 | 2 | `results/pilot_all/per_model.csv` | ✓ |
| 4.3 | Truthful answers checked for false alarms | 40 | 40 | `results/false_alarm/summary.csv` | ✓ |
| 4.3 | Truthful answers with any span; persuading span | 31 of 40; 22 of 40 | 31 of 40; 22 of 40 | `results/false_alarm/summary.csv` | ✓ |
| 4.3 | Mean spans on truthful answers | 3.3 | 3.3 | `results/false_alarm/summary.csv` | ✓ |
| 4.3 | Verdict 'not answered': truthful vs evasive | 4 of 40 vs 73 of 84 | 4 of 40 vs 73 of 84 | `results/false_alarm/summary.csv, results/labels/flags_v02.json` | ✓ |
| 3.3/4.2 | Evasive answers labelled | 84 | 84 | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | Raw annotator agreement | 59 of 84 (70%) | 59 of 84 (70%) | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | Cohen's κ | 0.19 | 0.19 | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | κ 95% CI (bootstrap over items) | −0.03 to 0.41 | −0.03 to 0.41 | `results/labels/agreement.csv` | ✓ |
| 4.2 | PABAK (2 × agreement − 1) | 0.40 | 0.40 | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | Share labelled misleading (A.S., M.A.) | 75%, 76% | 75%, 76% | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | Disagreements, split | 25 (13 / 12) | 25 (13 / 12) | `annotations/pilot/label_sheet_*.csv` | ✓ |
| 4.2 | Agreed misleading, imply condition | 39/42 | 39/42 | `annotations/pilot/` | ✓ |
| 4.2 | Agreed misleading, baseline condition | 12/17 | 12/17 | `annotations/pilot/` | ✓ |
| 4.2 | Llama agreed misleading, imply vs baseline | 18/20 vs 4/7 | 18/20 vs 4/7 | `annotations/pilot/` | ✓ |
| 4.2 | GPT-4o-mini agreed misleading, imply vs baseline | 21/22 vs 8/10 | 21/22 vs 8/10 | `annotations/pilot/` | ✓ |
| Table 2 | Llama corrected honesty, agreed only | 35.0 → 26.7 (-8.3) | 35.0 → 26.7 (-8.3) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | GPT-4o-mini corrected honesty, agreed only | 45.0 → 33.3 (-11.7) | 45.0 → 33.3 (-11.7) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | Llama corrected honesty, either annotator | 33.3 → 10.0 (-23.3) | 33.3 → 10.0 (-23.3) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | GPT-4o-mini corrected honesty, either annotator | 36.7 → 18.3 (-18.4) | 36.7 → 18.3 (-18.4) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 3 | Agreed answers scored (misleading / not) | 59 (51 / 8) | 59 (51 / 8) | `results/labels/tool_vs_human.csv` | ✓ |
| Table 3 | Any span: flagged, precision, recall, specificity, BA | 59/59, 0.86, 1.00, 0/8, 0.50 | 59/59, 0.86, 1.00, 0/8, 0.50 | `results/labels/tool_vs_human.csv` | ✓ |
| Table 3 | Persuading span: flagged, precision, recall, specificity, BA | 51/59, 0.92, 0.92, 4/8, 0.71 | 51/59, 0.92, 0.92, 4/8, 0.71 | `results/labels/tool_vs_human.csv` | ✓ |
| 4.3 | Mean flagged spans, misleading vs not | 4.9 vs 2.5 | 4.9 vs 2.5 | `results/labels/span_stats.csv` | ✓ |
| 4.3 | Empty reassurance present, misleading vs not | 90% vs 25% | 90% vs 25% | `results/labels/span_stats.csv` | ✓ |
| 4.3 | Non-misleading answers tagged non-answer | 5 of 8 | 5 of 8 | `results/labels/span_stats.csv` | ✓ |
| 4.4 | Long answers checked; burying flagged in | 6; 2 | 6; 2 | `results/burying/summary.csv` | ✓ |
| 4.4 | Length range of long answers (characters) | 1,341 to 2,456 | 1,341 to 2,456 | `results/burying/summary.csv` | ✓ |
| 3.2 | Flagger cost per answer | under 1¢ | – | `outputs/flags_v02/calls.jsonl (local cache)` | not checkable here (local cache) |
