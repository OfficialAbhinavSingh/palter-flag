"""Figure 1: MASK honesty score vs truthful answers, baseline and imply line, per model.

Reads results/pilot/summary.csv; writes results/figures/fig1_pilot.{png,svg}.
Static figure for a printed report, so light mode only.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures"

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e6e5e0"
SERIES = {  # validated pair (categorical slots 1 and 2)
    "mask_honesty_score": ("MASK honesty score", "#2a78d6", "o"),
    "honest": ("Answers that state the truth (%)", "#eb6834", "s"),
}
MODELS = {"meta-llama/llama-3.3-70b-instruct": "Llama-3.3-70B", "openai/gpt-4o-mini": "GPT-4o-mini"}
CONDITIONS = ["baseline", "imply"]
XLABELS = ["MASK prompt", "+ “imply, never assert”"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / "results/pilot/summary.csv")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": TEXT,
                         "axes.labelcolor": TEXT_2, "xtick.color": TEXT_2, "ytick.color": TEXT_2})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True, facecolor=SURFACE)

    for ax, (mid, name) in zip(axes, MODELS.items()):
        ax.set_facecolor(SURFACE)
        sub = df[df.model == mid].set_index("condition").loc[CONDITIONS]
        for col, (label, color, marker) in SERIES.items():
            ys = sub[col].to_numpy()
            ax.plot([0, 1], ys, color=color, lw=2, marker=marker, ms=8, label=label,
                    markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
            ax.annotate(f"{ys[0]:.0f}", (0, ys[0]), xytext=(-10, 0), textcoords="offset points",
                        ha="right", va="center", color=TEXT, fontsize=10)
            ax.annotate(f"{ys[1]:.0f}", (1, ys[1]), xytext=(10, 0), textcoords="offset points",
                        ha="left", va="center", color=TEXT, fontsize=10, fontweight="bold")
        ax.set_title(name, loc="left", fontsize=11, color=TEXT, fontweight="bold")
        ax.set_xlim(-0.45, 1.45)
        ax.set_xticks([0, 1], XLABELS)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("Percent / score (0–100)")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, fontsize=9.5,
               bbox_to_anchor=(0.5, 1.0), labelcolor=TEXT)
    fig.text(0.01, 0.01, "60 MASK provided_facts items per model; graded with MASK’s own judge prompt and scoring.",
             fontsize=8, color=TEXT_2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"fig1_pilot.{ext}", dpi=300, facecolor=SURFACE)
    print("wrote", OUT / "fig1_pilot.png")


if __name__ == "__main__":
    main()
