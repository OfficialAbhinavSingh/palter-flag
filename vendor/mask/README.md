# Vendored from MASK

`evaluation_prompts.py` is copied unmodified from
[centerforaisafety/mask](https://github.com/centerforaisafety/mask) at commit
`25e0b1201e6c928ebe69f7c5aad6fa9063a377ea` (`mask/prompts/evaluation_prompts.py`), MIT licence (see `LICENSE`).

`src/hbo/mask_metric.py` holds verbatim copies of `get_majority` and
`aggregate_eval_honesty` from `mask/metric.py` at the same commit. Upstream `metric.py`
parses CLI arguments at import time, so it can't be imported directly.
