"""Run the frozen v0.2 flagger over every pilot answer in the label sheets.

Output: outputs/flags_v02/flags.json keyed by label_id, used by analyze_labels.py
to score the tool against the human labels.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from hbo.flagger_v02 import build_messages, locate, parse  # noqa: E402
from pilot import Cache, Spend, call, load_env  # noqa: E402


async def main():
    load_env()
    sheet = pd.read_csv(ROOT / "annotations/pilot/label_sheet_abhinav.csv")  # text columns only
    out = ROOT / "outputs/flags_v02"
    out.mkdir(parents=True, exist_ok=True)
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    cache = Cache(out / "calls.jsonl")
    spend = Spend(0.80, sum(r.get("cost", 0) for r in cache.data.values()))
    sem = asyncio.Semaphore(6)
    reqs = [{"model": "openai/gpt-4o", "temperature": 0, "max_tokens": 900,
             "messages": build_messages(r.user_prompt, r.response)} for r in sheet.itertuples()]
    got = await asyncio.gather(*[call(client, sem, spend, cache, q, f"flag:{r.label_id}")
                                 for r, q in zip(sheet.itertuples(), reqs)])
    flags = {}
    for r, g in zip(sheet.itertuples(), got):
        if g is None:
            continue
        f = parse(g["text"])
        spans = locate(r.response, f["spans"])
        flags[r.label_id] = {"answered": f.get("answered"), "n_spans": len(spans),
                             "categories": sorted({s["category"] for s in spans}),
                             "spans": [{k: s[k] for k in ("start", "end", "category", "reason")} for s in spans]}
    (out / "flags.json").write_text(json.dumps(flags, indent=1, ensure_ascii=False))
    (ROOT / "results" / "labels").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "labels" / "flags_v02.json").write_text(json.dumps(flags, indent=1, ensure_ascii=False))
    print(f"{len(flags)}/{len(sheet)} flagged, spend ${spend.total:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
