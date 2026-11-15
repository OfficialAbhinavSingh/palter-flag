# Human labels on MASK-evasive answers

84 answers, two annotators. Raw agreement 70%, Cohen's κ = 0.19 [-0.03, 0.41], PABAK 0.40. Abhinav Y 75%, Mahak Y 76%. Disagreements: 25, unresolved 25.

## Misleading rate by condition (consensus)

                            model condition  n  misleading  not_misleading  unresolved  misleading_rate
meta-llama/llama-3.3-70b-instruct  baseline  8           4               3           1            0.571
meta-llama/llama-3.3-70b-instruct     imply 30          18               2          10            0.900
               openai/gpt-4o-mini  baseline 15           8               2           5            0.800
               openai/gpt-4o-mini     imply 31          21               1           9            0.955

## MASK honesty vs corrected (misleading evasions count as lies)

                            model condition  mask_honesty  corrected_honesty
meta-llama/llama-3.3-70b-instruct  baseline          41.7               35.0
meta-llama/llama-3.3-70b-instruct     imply          56.7               26.7
               openai/gpt-4o-mini  baseline          58.3               45.0
               openai/gpt-4o-mini     imply          68.3               33.3

## Palter Flag v0.2 vs human consensus

               rule  n  tp  fp  fn  tn  precision  recall  specificity  balanced_acc   f1  flagged_rate  base_rate
           any_span 59  51   8   0   0       0.86    1.00          0.0          0.50 0.93          1.00       0.86
any_persuading_span 59  47   4   4   4       0.92    0.92          0.5          0.71 0.92          0.86       0.86
   answered_not_yes 59  51   8   0   0       0.86    1.00          0.0          0.50 0.93          1.00       0.86
