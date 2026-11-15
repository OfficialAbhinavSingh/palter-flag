"""Figure 2: Palter Flag v0.2 output on one pilot answer that MASK scores as honest.

Reads outputs/deck_demo/cakes_v02.json (real flagger output) and data/ for the question;
renders HTML and screenshots it with headless Chrome to results/figures/fig2_tool_example.png.
"""
import html
import json
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLORS = {"non_answer": "#DADCE2", "deflection": "#C9D8FF", "empty_reassurance": "#FBD98A",
          "paltering": "#F8C6DB", "minimising": "#FFC9B5", "doubt_casting": "#E3CCF5",
          "weasel_words": "#CFEBD4", "unverified_claim": "#F2D2AE"}
LABEL = {"non_answer": "non-answer", "deflection": "deflection", "empty_reassurance": "empty reassurance",
         "paltering": "paltering", "minimising": "minimising", "doubt_casting": "doubt-casting",
         "weasel_words": "weasel words", "unverified_claim": "unverified claim"}
DODGING = {"non_answer", "deflection", "empty_reassurance", "burying"}


def main():
    demo = json.loads((ROOT / "outputs/deck_demo/cakes_v02.json").read_text())
    answer, flags, spans = demo["response"], demo["flags"], demo["spans"]
    res = pd.read_csv(ROOT / "outputs/pilot/results.csv")
    task = res[res.response == answer].iloc[0]
    item = pd.read_parquet(ROOT / "data/provided_facts.parquet").set_index("task_id").loc[task.task_id]

    parts, pos = [], 0
    for s in spans:
        parts.append(html.escape(answer[pos:s["start"]]))
        parts.append(f'<mark style="background:{COLORS[s["category"]]}">{html.escape(answer[s["start"]:s["end"]])}'
                     f'<sup>{LABEL[s["category"]]}</sup></mark>')
        pos = s["end"]
    parts.append(html.escape(answer[pos:]))
    used = sorted({s["category"] for s in spans}, key=lambda c: (c not in DODGING, c))
    chips = "".join(f'<span class="chip" style="background:{COLORS[c]}">{"Dodging" if c in DODGING else "Persuading"}: {LABEL[c]}</span>' for c in used)
    said = {"yes": "Yes", "partly": "Partly", "no": "No"}[flags["answered"]]

    page = f"""<!doctype html><meta charset="utf-8"><style>
body {{ margin:0; background:#fff; font:15px/1.5 "DejaVu Sans", Arial, sans-serif; color:#1B1F2A; }}
.wrap {{ width:860px; padding:22px 26px; box-sizing:border-box; }}
.lab {{ font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#8A5A00; margin:0 0 4px; }}
.q {{ color:#4A5163; margin:0 0 14px; }}
.a {{ background:#FAFAF7; border:1px solid #E2DDD2; border-radius:10px; padding:14px 16px; line-height:2.0; }}
mark {{ border-radius:4px; padding:2px 3px; color:#1B1F2A; }}
sup {{ font-size:9.5px; font-weight:700; margin-left:3px; color:#3a3a3a; letter-spacing:.02em; }}
.chips {{ margin:10px 0 0; }} .chip {{ display:inline-block; font-size:12px; font-weight:600; padding:2px 9px; border-radius:999px; margin:0 6px 4px 0; }}
.tool {{ margin-top:12px; border-left:4px solid #8A5A00; background:#FFF8E8; padding:9px 14px; border-radius:0 10px 10px 0; }}
.tool p {{ margin:2px 0; }}
</style><div class="wrap">
<p class="lab">Question</p><p class="q">{html.escape(item.user_prompt)}</p>
<p class="lab">AI answer, with Palter Flag highlights</p><div class="a">{''.join(parts)}</div>
<div class="chips">{chips}</div>
<div class="tool"><p><b>Did this answer the question?</b> {said}.</p>
<p><b>A straight answer would need to say:</b> {html.escape(flags['straight_answer_needs'])}</p>
<p><b>Ask this instead:</b> “{html.escape(flags['ask_instead'])}”</p></div>
</div>"""
    out = ROOT / "results/figures/fig2_tool_example.png"
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "fig.html"
        f.write_text(page)
        subprocess.run(["google-chrome-stable", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", "--window-size=880,700",
                        f"--screenshot={out}", f"file://{f}"], check=True, capture_output=True)
    subprocess.run(["magick", str(out), "-trim", "-bordercolor", "white", "-border", "16", str(out)], check=True)
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
