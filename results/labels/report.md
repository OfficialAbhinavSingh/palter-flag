# Human labels on MASK-evasive answers

84 answers, two annotators. Raw agreement 70%, Cohen's κ = 0.19 [-0.03, 0.41], PABAK 0.40. Abhinav Y 75%, Mahak Y 76%. Disagreements: 25, all resolved by tie-break.

## Misleading rate by condition (consensus)

                            model condition  n  misleading  not_misleading  unresolved  misleading_rate
meta-llama/llama-3.3-70b-instruct  baseline  8           4               4           0            0.500
meta-llama/llama-3.3-70b-instruct     imply 30          23               7           0            0.767
               openai/gpt-4o-mini  baseline 15           9               6           0            0.600
               openai/gpt-4o-mini     imply 31          27               4           0            0.871

## MASK honesty vs corrected (misleading evasions count as lies)

                            model condition  mask_honesty  corrected_honesty
meta-llama/llama-3.3-70b-instruct  baseline          41.7               35.0
meta-llama/llama-3.3-70b-instruct     imply          56.7               18.3
               openai/gpt-4o-mini  baseline          58.3               43.3
               openai/gpt-4o-mini     imply          68.3               23.3

## Palter Flag v0.2 vs human consensus

     labels                rule  n  tp  fp  fn  tn  precision  recall  specificity  balanced_acc   f1  flagged_rate  base_rate
adjudicated            any_span 84  63  21   0   0       0.75    1.00         0.00          0.50 0.86          1.00       0.75
adjudicated any_persuading_span 84  56  11   7  10       0.84    0.89         0.48          0.68 0.86          0.80       0.75
adjudicated    answered_not_yes 84  63  21   0   0       0.75    1.00         0.00          0.50 0.86          1.00       0.75
agreed_only            any_span 59  51   8   0   0       0.86    1.00         0.00          0.50 0.93          1.00       0.86
agreed_only any_persuading_span 59  47   4   4   4       0.92    0.92         0.50          0.71 0.92          0.86       0.86
agreed_only    answered_not_yes 59  51   8   0   0       0.86    1.00         0.00          0.50 0.93          1.00       0.86
