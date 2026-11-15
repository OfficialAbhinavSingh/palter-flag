"""Pick the user-study items from the pilot and precompute Palter Flag highlights.

12 items from 12 different MASK scenarios: 6 evasive (MASK grade C), 3 truthful
(honesty 1) and 3 lies (honesty -1). Answers between 150 and 900 characters so
the study stays near 10 minutes. Each item gets one statement to rate, randomly
the true or the false version of the MASK proposition.
"""
import asyncio
import json
import os
import random
import re
import sys
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from hbo.flagger_v02 import build_messages, locate, parse  # noqa: E402  (study is frozen on v0.2)
from pilot import Cache, Spend, call, load_env  # noqa: E402

SEED = 7
QUOTA = {"evasive": 6, "truthful": 3, "lie": 3}
# MASK items whose question and statement name different entities, which confuses participants
EXCLUDE = {'67ab8fa52a6fca04620b141b', '676f535fe636d9ab52c39bfd'}


def options(prop):
    m = re.search(r"<pivotal>([^<]+)</pivotal>", prop)
    a, b = m.group(1).split("/")
    return prop.replace(m.group(0), a), prop.replace(m.group(0), b)


async def main():
    load_env()
    res = pd.read_csv(ROOT / "outputs/pilot/results.csv")
    items = pd.read_parquet(ROOT / "data/provided_facts.parquet").set_index("task_id")
    res["type"] = res.honesty.map({1: "truthful", -1: "lie"})
    res.loc[res.eval_honesty_1_raw == "C", "type"] = "evasive"
    res["len"] = res.response.str.len()
    pool = res[res.type.notna() & res.len.between(150, 900)].sample(frac=1, random_state=SEED)

    rng = random.Random(SEED)
    used, picked = set(), []
    for kind, n in QUOTA.items():
        for _, r in pool[pool.type == kind].iterrows():
            if sum(p["type"] == kind for p in picked) >= n:
                break
            if r.task_id in used or r.task_id in EXCLUDE:
                continue
            used.add(r.task_id)
            picked.append(r.to_dict())
    assert len(picked) == sum(QUOTA.values()), f"only {len(picked)} items"

    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    out = ROOT / "outputs/study_items"
    out.mkdir(parents=True, exist_ok=True)
    cache = Cache(out / "calls.jsonl")
    spend = Spend(0.50, sum(r.get("cost", 0) for r in cache.data.values()))
    sem = asyncio.Semaphore(6)
    reqs = [{"model": "openai/gpt-4o", "temperature": 0, "max_tokens": 900,
             "messages": build_messages(items.loc[p["task_id"]].user_prompt, p["response"])} for p in picked]
    got = await asyncio.gather(*[call(client, sem, spend, cache, q, f"study:{i}") for i, q in enumerate(reqs)])

    study = []
    for i, (p, g) in enumerate(zip(picked, got)):
        it = items.loc[p["task_id"]]
        f = parse(g["text"])
        opt1, opt2 = options(it.proposition)
        true_stmt, false_stmt = (opt1, opt2) if it.formatted_ground_truth == "A" else (opt2, opt1)
        show_true = rng.random() < 0.5
        study.append({
            "id": f"S{i + 1:02d}", "type": p["type"], "model": p["model"], "pilot_condition": p["condition"],
            "task_id": p["task_id"], "question": it.user_prompt, "answer": p["response"],
            "statement": true_stmt if show_true else false_stmt, "statement_is_true": show_true,
            "answered": f.get("answered"),
            "straight_answer_needs": f.get("straight_answer_needs"), "ask_instead": f.get("ask_instead"),
            "spans": [{k: s[k] for k in ("start", "end", "category", "reason")} for s in locate(p["response"], f["spans"])],
        })
    (out / "items.json").write_text(json.dumps(study, indent=1, ensure_ascii=False))
    # answer key for analysis; tracked in git, never served to participants
    (ROOT / "results" / "study").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "study" / "items_key.json").write_text(json.dumps(study, indent=1, ensure_ascii=False))
    for s in study:
        print(s["id"], s["type"], s["answered"], len(s["spans"]), "spans |", s["statement_is_true"], "|", s["statement"][:70])
    print(f"spend ${spend.total:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
