"""Figure 1: per model, how the imply line moves MASK honesty and the truthful-answer rate.

Reads results/pilot_all/per_model.csv (scripts/pilot_all_models.py); writes
results/figures/fig1_pilot.{png,svg}. Static figure for a printed report, so light mode only.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures"

SURFACE, TEXT, TEXT_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"
BASE, IMPLY = "#9a988f", "#2a78d6"  # baseline = neutral grey, imply = categorical slot 1
PANELS = [("mask_honesty", "MASK honesty score (100 − lie %)"), ("truthful", "Answers that state the truth (%)")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / "results/pilot_all/per_model.csv").sort_values("mask_change")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "text.color": TEXT,
                         "axes.labelcolor": TEXT_2, "xtick.color": TEXT_2, "ytick.color": TEXT})
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 0.42 * len(df) + 1.5), sharey=True, facecolor=SURFACE)
    ys = range(len(df))
    for ax, (col, title) in zip(axes, PANELS):
        ax.set_facecolor(SURFACE)
        for y, (_, r) in zip(ys, df.iterrows()):
            b, i = r[f"{col}_baseline"], r[f"{col}_imply"]
            ax.annotate("", xy=(i, y), xytext=(b, y),
                        arrowprops=dict(arrowstyle="-|>", color=IMPLY, lw=2, shrinkA=4, shrinkB=4, mutation_scale=11))
            ax.scatter([b], [y], s=46, color=BASE, zorder=3, edgecolor=SURFACE, linewidth=1.5)
            ax.scatter([i], [y], s=46, color=IMPLY, zorder=3, edgecolor=SURFACE, linewidth=1.5, marker="D")
            ax.annotate(f"{i - b:+.0f}", (max(b, i), y), xytext=(8, 0), textcoords="offset points",
                        va="center", fontsize=9, color=TEXT, fontweight="bold")
        ax.set_title(title, loc="left", fontsize=10, color=TEXT, fontweight="bold")
        ax.set_xlim(0, 108)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0)
    axes[0].set_yticks(list(ys), df.model)
    handles = [plt.Line2D([], [], marker="o", ls="", color=BASE, label="MASK prompt"),
               plt.Line2D([], [], marker="D", ls="", color=IMPLY, label="+ “imply, never assert”")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.55, 1.0), labelcolor=TEXT)
    fig.text(0.01, 0.01, "60 MASK provided_facts items per model; graded with MASK’s own judge prompt and scoring.",
             fontsize=7.5, color=TEXT_2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"fig1_pilot.{ext}", dpi=300, facecolor=SURFACE)
    print("wrote", OUT / "fig1_pilot.png")


if __name__ == "__main__":
    main()
