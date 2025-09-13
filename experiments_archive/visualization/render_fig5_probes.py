#!/usr/bin/env python3
"""
Render Fig5: Probe metric contrasts (grouped bars by model).

Input TSV columns (long format): model, metric, mean
Output: PNG/PDF figure.
If input missing/empty, render a placeholder.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_probes(tsv: Path) -> pd.DataFrame:
    if not tsv.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(tsv, sep="\t").fillna("")
    except Exception:
        return pd.DataFrame()
    needed = {"model", "metric", "mean"}
    if not needed.issubset(df.columns):
        return pd.DataFrame()
    df["mean"] = pd.to_numeric(df["mean"], errors="coerce")
    df = df.dropna(subset=["mean"])  # type: ignore[arg-type]
    return df


def plot_probes(df: pd.DataFrame, out_png: Path, out_pdf: Path | None = None) -> None:
    plt.close("all")
    if df.empty:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.axis("off")
        ax.text(0.5, 0.6, "Fig5: Probe metric contrasts", ha="center", va="center", fontsize=12)
        ax.text(0.5, 0.4, "No probe summary available yet", ha="center", va="center", fontsize=11, color="gray")
    else:
        # pivot to wide so metrics are grouped per model
        fig, ax = plt.subplots(figsize=(7, max(3.0, 0.3 * df["metric"].nunique())))
        sns.barplot(df, x="mean", y="metric", hue="model", ax=ax)
        ax.set_xlabel("Mean value")
        ax.set_ylabel("")
        ax.set_title("Probe metric contrasts by model")
        ax.legend(title="Model", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0)
        fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    if out_pdf is not None:
        fig.savefig(out_pdf)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv", type=Path, help="Path to probes_summary.tsv")
    ap.add_argument("out_png", type=Path, help="Output PNG path")
    ap.add_argument("--out-pdf", type=Path, default=None, help="Optional output PDF path")
    args = ap.parse_args()
    df = load_probes(args.tsv)
    plot_probes(df, args.out_png, args.out_pdf)


if __name__ == "__main__":
    main()
