"""False-alarm check: run the frozen v0.2 flagger on answers MASK graded as truthful.

These answers state the truth (MASK honesty = 1), so a good flagger should mostly say
"answered" and flag little. Sample: 40 truthful pilot answers, seed 0, both models and
conditions. Writes results/false_alarm/summary.csv (per answer, no text) and report.md.
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

from hbo.flagger_v02 import PERSUADING, build_messages, locate, parse  # noqa: E402
from pilot import Cache, Spend, call, load_env  # noqa: E402

N, SEED, BUDGET = 40, 0, 0.30


async def main():
    load_env()
    res = pd.read_csv(ROOT / "outputs/pilot/results.csv")
    items = pd.read_parquet(ROOT / "data/provided_facts.parquet").set_index("task_id")
    pool = res[res.honesty == 1]
    sample = pool.sample(min(N, len(pool)), random_state=SEED)
    out = ROOT / "outputs/false_alarm"
    out.mkdir(parents=True, exist_ok=True)
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    cache = Cache(out / "calls.jsonl")
    spend = Spend(BUDGET, sum(r.get("cost", 0) for r in cache.data.values()))
    sem = asyncio.Semaphore(6)
    rows = list(sample.itertuples())
    got = await asyncio.gather(*[call(client, sem, spend, cache,
                                      {"model": "openai/gpt-4o", "temperature": 0, "max_tokens": 900,
                                       "messages": build_messages(items.loc[x.task_id].user_prompt, x.response)},
                                      f"fa:{k}") for k, x in enumerate(rows)])
    recs = []
    for x, g in zip(rows, got):
        if g is None:
            continue
        f = parse(g["text"])
        spans = locate(x.response, f["spans"])
        cats = {s["category"] for s in spans}
        recs.append({"task_id": x.task_id, "model": x.model, "condition": x.condition, "answered": f.get("answered"),
                     "n_spans": len(spans), "any_span": bool(spans), "any_persuading": bool(cats & set(PERSUADING)),
                     "categories": ";".join(sorted(cats))})
    df = pd.DataFrame(recs)
    dest = ROOT / "results/false_alarm"
    dest.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest / "summary.csv", index=False)
    n = len(df)
    lines = ["# False-alarm check: Palter Flag v0.2 on answers MASK graded truthful", "",
             f"{n} answers (seed {SEED}), cost ${spend.total:.3f}.", "",
             f"- verdict answered = yes: {(df.answered == 'yes').sum()}/{n}",
             f"- verdict answered = partly: {(df.answered == 'partly').sum()}/{n}",
             f"- verdict answered = no: {(df.answered == 'no').sum()}/{n}",
             f"- any span flagged: {df.any_span.sum()}/{n}",
             f"- any persuading span flagged: {df.any_persuading.sum()}/{n}",
             f"- mean spans: {df.n_spans.mean():.1f}", "",
             "Truthful here means MASK's grader found the answer states the true proposition; such answers can still",
             "contain spin, so a flag is not automatically a false alarm. The 'answered = no' rate is the clearest error."]
    (dest / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
