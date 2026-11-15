"""Download the public MASK splits from Hugging Face (cais/MASK) into data/."""
import os
import shutil
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from huggingface_hub import hf_hub_download  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ["provided_facts", "known_facts", "disinformation", "continuations",
          "statistics", "doubling_down_known_facts"]

(ROOT / "data").mkdir(exist_ok=True)
for split in SPLITS:
    path = hf_hub_download("cais/MASK", f"{split}/test-00000-of-00001.parquet", repo_type="dataset")
    shutil.copy(path, ROOT / "data" / f"{split}.parquet")
    print("ok", split)
