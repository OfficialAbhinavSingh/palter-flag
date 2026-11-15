# MASK pilot across models

7 models, 60 provided_facts items each (seed 0), MASK's judge prompt and scoring.

- MASK honesty rose for 6/7 models (range -3.3 to +20.0).
- Truthful answers fell for 7/7 models (range -6.6 to -23.4); significant alone (p < 0.05) for 3/7.
- Evasive share rose for 7/7 models.
- Pooled over item-model pairs: truthful lost 72 vs gained 16 (exact McNemar p = 1.2e-09); lies stopped 70 vs started 23 (p = 1.1e-06). Pairs share items across models, so the pooled p is a summary, not an independent test.

            model  mask_honesty_baseline  mask_honesty_imply  mask_change  truthful_baseline  truthful_imply  truthful_lost  truthful_gained  truthful_p  lie_p  unparsed_baseline  unparsed_imply
    DeepSeek-V3.1                   30.0                50.0         20.0               13.3             6.7              5                1      0.2188 0.0018                  0               1
Mistral-Small-3.2                   36.7                51.7         15.0               16.7             8.3              9                4      0.2668 0.0636                  1               0
    Llama-3.3-70B                   41.7                56.7         15.0               28.3             6.7             14                1      0.0010 0.0490                  0               0
       Qwen3-235B                   33.3                46.7         13.4               21.7            13.3              6                1      0.1250 0.0386                  0               0
      GPT-4o-mini                   58.3                68.3         10.0               33.3            16.7             13                3      0.0213 0.1460                  0               0
 Gemini-2.5-Flash                   38.3                46.7          8.4               18.3            10.0              7                2      0.1797 0.2266                  0               0
 Claude-Haiku-4.5                   93.3                90.0         -3.3               71.7            48.3             18                4      0.0043 0.7266                  0               0
