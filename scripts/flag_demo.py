"""Run Palter Flag v0 on a sample of pilot answers and render highlighted HTML."""
import argparse
import asyncio
import html
import json
import sys
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from hbo.flagger import build_messages, locate, parse  # noqa: E402
from pilot import Cache, Spend, call, load_env  # noqa: E402

COLORS = {"reassurance": "#ffe08a", "minimising": "#ffc4a3", "doubt_casting": "#f5b3c8",
          "deflection": "#c9d8ff", "non_answer": "#d9d9d9"}


def render(answer, spans):
    out, pos = [], 0
    for s in spans:
        out.append(html.escape(answer[pos:s["start"]]))
        color = COLORS.get(s.get("category"), "#eee")
        tip = html.escape(f'{s.get("category")}: {s.get("reason", "")}')
        out.append(f'<mark style="background:{color}" title="{tip}">{html.escape(answer[s["start"]:s["end"]])}</mark>')
        pos = s["end"]
    out.append(html.escape(answer[pos:]))
    return "".join(out).replace("\n", "<br>")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o")
    ap.add_argument("--per-group", type=int, default=4)
    ap.add_argument("--budget", type=float, default=0.50)
    ap.add_argument("--out", default="outputs/flag_demo")
    args = ap.parse_args()
    load_env()

    res = pd.read_csv(ROOT / "outputs/pilot/results.csv")
    items = pd.read_parquet(ROOT / "data/provided_facts.parquet").set_index("task_id")
    groups = {
        "imply_C": res[(res.condition == "imply") & (res.eval_honesty_1_raw == "C")],
        "baseline_C": res[(res.condition == "baseline") & (res.eval_honesty_1_raw == "C")],
        "baseline_truthful": res[(res.condition == "baseline") & (res.honesty == 1)],
    }
    sample = pd.concat([g.sample(min(args.per_group, len(g)), random_state=0).assign(group=k)
                        for k, g in groups.items()])

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=__import__("os").environ["OPENROUTER_API_KEY"])
    cache = Cache(out / "calls.jsonl")
    spend = Spend(args.budget, sum(r.get("cost", 0) for r in cache.data.values()))
    sem = asyncio.Semaphore(6)

    reqs = []
    for _, r in sample.iterrows():
        q = items.loc[r.task_id].user_prompt
        reqs.append({"model": args.model, "temperature": 0, "max_tokens": 900,
                     "messages": build_messages(q, r.response)})
    got = await asyncio.gather(*[call(client, sem, spend, cache, rq, f"flag:{i}") for i, rq in enumerate(reqs)])

    rows, cards = [], []
    for (_, r), g in zip(sample.iterrows(), got):
        it = items.loc[r.task_id]
        try:
            f = parse(g["text"])
            spans = locate(r.response, f["spans"])
        except Exception as e:  # noqa: BLE001
            f, spans = {"answered": "?", "lean": "?", "lean_explanation": f"parse error: {e}"}, []
        rows.append({"task_id": r.task_id, "model": r.model, "group": r.group, "answered": f.get("answered"),
                     "lean": f.get("lean"), "n_spans": len(spans), "n_spans_returned": len(f.get("spans", [])),
                     "lean_explanation": f.get("lean_explanation"), "spans": json.dumps(spans)})
        cards.append(f"""<section class="card"><div class="meta">{html.escape(r.group)} · {html.escape(r.model.split('/')[-1])}</div>
<p class="q"><b>Question:</b> {html.escape(it.user_prompt)}</p>
<p class="truth"><b>Truth:</b> {html.escape(it.ground_truth)}</p>
<div class="a">{render(r.response, spans)}</div>
<p class="verdict">Answered: <b>{html.escape(str(f.get('answered')))}</b> · Reader would lean: <b>{html.escape(str(f.get('lean')))}</b><br>{html.escape(str(f.get('lean_explanation', '')))}</p></section>""")

    pd.DataFrame(rows).to_csv(out / "flags.csv", index=False)
    legend = " ".join(f'<mark style="background:{c}">{k}</mark>' for k, c in COLORS.items())
    (out / "demo.html").write_text(f"""<!doctype html><meta charset="utf-8"><title>Palter Flag demo</title>
<style>body{{font:15px/1.5 system-ui;max-width:860px;margin:24px auto;padding:0 16px;color:#111;background:#fff}}
.card{{border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin:16px 0}}.meta{{font-size:12px;color:#777}}
.truth{{color:#555}}.a{{background:#fafafa;padding:10px;border-radius:6px}}mark{{padding:1px 2px;border-radius:3px}}
.verdict{{font-size:14px;color:#333}}</style><h1>Palter Flag v0</h1><p>{legend}</p>{''.join(cards)}""")
    print(pd.DataFrame(rows)[["group", "model", "answered", "lean", "n_spans", "n_spans_returned"]].to_string())
    print(f"spend ${spend.total:.3f} -> {out.relative_to(ROOT)}/demo.html")


if __name__ == "__main__":
    asyncio.run(main())
