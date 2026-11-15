"""v0.3 burying check on 6 long truthful pilot answers (sample fixed by seed).

Reads outputs/pilot/results.csv and data/; writes results/burying/summary.csv with
lengths, verdicts and burying flags (offsets and reasons, no answer text).
"""
import asyncio
import os
import sys
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from hbo.flagger import build_messages, locate, locate_direct, parse  # noqa: E402
from pilot import Cache, Spend, call, load_env  # noqa: E402


async def main():
    load_env()
    res = pd.read_csv(ROOT / "outputs/pilot/results.csv")
    items = pd.read_parquet(ROOT / "data/provided_facts.parquet").set_index("task_id")
    sample = res[(res.response.str.len() > 1200) & (res.honesty == 1)].sample(6, random_state=3)
    out = ROOT / "outputs/burying_check"
    out.mkdir(parents=True, exist_ok=True)
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    cache = Cache(out / "calls.jsonl")
    spend = Spend(0.3, sum(r.get("cost", 0) for r in cache.data.values()))
    rows = list(sample.itertuples())
    got = await asyncio.gather(*[call(client, asyncio.Semaphore(6), spend, cache,
                                      {"model": "openai/gpt-4o", "temperature": 0, "max_tokens": 1000,
                                       "messages": build_messages(items.loc[x.task_id].user_prompt, x.response)},
                                      f"bury:{k}") for k, x in enumerate(rows)])
    recs = []
    for x, g in zip(rows, got):
        f = parse(g["text"])
        spans = locate(x.response, f["spans"])
        d = locate_direct(x.response, f.get("direct_answer_quote", ""))
        bury = [s for s in spans if s["category"] == "burying"]
        recs.append({"task_id": x.task_id, "model": x.model, "length": len(x.response), "answered": f.get("answered"),
                     "n_spans": len(spans), "n_burying": len(bury),
                     "burying_at": ";".join(f"{s['start']}/{len(x.response)}" for s in bury),
                     "burying_reason": ";".join(s["reason"] for s in bury),
                     "direct_answer_position": d["position"] if d else None})
    (ROOT / "results/burying").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(recs).to_csv(ROOT / "results/burying/summary.csv", index=False)
    print(pd.DataFrame(recs)[["model", "length", "answered", "n_burying", "direct_answer_position"]].to_string(index=False))
    print(f"spend ${spend.total:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
