# Claims ledger

Selected claims enumerated in `scripts/build_ledger.py`, checked against the named source files.
Expected values are maintained in the script; it does not parse the DOCX/PDF or verify every report number.
Some checks read tracked analysis outputs. Local-cache entries can be skipped and are not verified.
A ✗ means a listed expected value differs from its recomputed value; the script exits non-zero.

| Section | Claim | Expected (in script) | Recomputed | Source | Check |
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
| 4.2 | Agreed misleading, imply vs baseline | 39 of 42 vs 12 of 17 | 39 of 42 vs 12 of 17 | `annotations/pilot/` | ✓ |
| 4.2 | Adjudicated misleading, imply vs baseline | 50 of 61 vs 13 of 23 | 50 of 61 vs 13 of 23 | `results/labels/by_condition.csv` | ✓ |
| 4.2 | Adjudicated misleading, Llama imply vs baseline | 23/30 vs 4/8 | 23/30 vs 4/8 | `results/labels/by_condition.csv` | ✓ |
| 4.2 | Adjudicated misleading, GPT-4o-mini imply vs baseline | 27/31 vs 9/15 | 27/31 vs 9/15 | `results/labels/by_condition.csv` | ✓ |
| 3.3 | Disputes resolved to first author: N / Y | 13 / 12 | 13 / 12 | `annotations/pilot/adjudication.csv` | ✓ |
| Table 2 | Llama corrected, adjudicated | 35.0 → 18.3 (-16.7) | 35.0 → 18.3 (-16.7) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | GPT-4o-mini corrected, adjudicated | 43.3 → 23.3 (-20.0) | 43.3 → 23.3 (-20.0) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | Llama corrected, agreed only | 35.0 → 26.7 (-8.3) | 35.0 → 26.7 (-8.3) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | GPT-4o-mini corrected, agreed only | 45.0 → 33.3 (-11.7) | 45.0 → 33.3 (-11.7) | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | Llama range of change over all resolutions | -25.0 to -6.7 | -25.0 to -6.7 | `results/labels/corrected_bounds.csv` | ✓ |
| Table 2 | GPT-4o-mini range of change over all resolutions | -26.7 to -3.3 | -26.7 to -3.3 | `results/labels/corrected_bounds.csv` | ✓ |
| Table 3 | Adjudicated labels: misleading / not | 63 / 21 | 63 / 21 | `results/labels/tool_vs_human.csv` | ✓ |
| Table 3 | Any span (adjudicated): flagged, P, R, spec, BA | 84/84, 0.75, 1.00, 0/21, 0.50 | 84/84, 0.75, 1.00, 0/21, 0.50 | `results/labels/tool_vs_human.csv` | ✓ |
| Table 3 | Persuading span (adjudicated): flagged, P, R, spec, BA | 67/84, 0.84, 0.89, 10/21, 0.68 | 67/84, 0.84, 0.89, 10/21, 0.68 | `results/labels/tool_vs_human.csv` | ✓ |
| Table 3 | Persuading span (agreed only): flagged, P, R, spec, BA | 51/59, 0.92, 0.92, 4/8, 0.71 | 51/59, 0.92, 0.92, 4/8, 0.71 | `results/labels/tool_vs_human.csv` | ✓ |
| 4.3 | Mean flagged spans, misleading vs not (adjudicated) | 4.9 vs 3.4 | 4.9 vs 3.4 | `results/labels/span_stats.csv` | ✓ |
| 4.3 | Non-misleading answers tagged non-answer (adjudicated) | 15 of 21 | 15 of 21 | `results/labels/span_stats.csv` | ✓ |
| 4.4 | Long answers checked; burying flagged in | 6; 2 | 6; 2 | `results/burying/summary.csv` | ✓ |
| 4.4 | Length range of long answers (characters) | 1,341 to 2,456 | 1,341 to 2,456 | `results/burying/summary.csv` | ✓ |
| 3.2 | Flagger cost per answer | under 1¢ | – | `outputs/flags_v02/calls.jsonl (local cache)` | not checkable here (local cache) |
