#!/usr/bin/env python3
"""
Render Fig3: Complaint incidence shifts (forest plot of interaction ORs).

Inputs:
  - TSV with columns: outcome, estimator, positive, negative, interaction_coef, interaction_p
    (as produced by pipeline/table_prep.py into outputs/tables/regression_interactions.tsv)

Outputs:
  - PNG/PDF forest plot saved to the specified output path(s).

Behavior:
  - If the TSV is missing or has no usable rows, render a placeholder figure with a note.
  - Robust to extra columns or empty lines.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_interactions(tsv: Path) -> pd.DataFrame:
    if not tsv.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(tsv, sep="\t").fillna("")
    except Exception:
        return pd.DataFrame()
    # Basic sanity: need outcome and interaction_coef
    needed = {"outcome", "interaction_coef"}
    if not needed.issubset(df.columns):
        return pd.DataFrame()
    # Coerce coef to numeric
    df["interaction_coef"] = pd.to_numeric(df["interaction_coef"], errors="coerce")
    # Filter valid rows
    df = df.dropna(subset=["interaction_coef"])  # type: ignore[arg-type]
    # Keep a small, clear subset for plotting
    cols = [c for c in ["outcome", "interaction_coef", "interaction_p"] if c in df.columns]
    return df[cols]


def forest_plot(df: pd.DataFrame, out_png: Path, out_pdf: Path | None = None) -> None:
    plt.close("all")
    fig, ax = plt.subplots(figsize=(8, max(3.0, 0.5 * max(1, len(df)))))
    if df.empty:
        ax.axis("off")
        ax.text(0.5, 0.6, "Fig3: Regression interactions (forest)", ha="center", va="center", fontsize=12)
        ax.text(0.5, 0.4, "No data available yet", ha="center", va="center", fontsize=11, color="gray")
    else:
        # Convert interaction_coef (log OR) to OR and plot with a reference line at 1.0
        plot_df = df.copy()
        plot_df["OR"] = plot_df["interaction_coef"].apply(lambda x: math.exp(x))
        y = range(len(plot_df))
        ax.scatter(plot_df["OR"], y, color="#1f77b4")
        # P-values as labels when available
        if "interaction_p" in plot_df.columns:
            for i, (or_val, p, outcome) in enumerate(zip(plot_df["OR"], plot_df.get("interaction_p", [""] * len(plot_df)), plot_df["outcome"])):
                lbl = f"{outcome} (OR={or_val:.2f}, p={p})" if p != "" else f"{outcome} (OR={or_val:.2f})"
                ax.text(or_val, i, "  " + lbl, va="center", fontsize=9)
        else:
            for i, (or_val, outcome) in enumerate(zip(plot_df["OR"], plot_df["outcome"])):
                ax.text(or_val, i, f"  {outcome} (OR={or_val:.2f})", va="center", fontsize=9)
        ax.axvline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_yticks([])
        ax.set_xscale("log")
        ax.set_xlabel("Interaction Odds Ratio (post vs pre by transition)")
        ax.set_title("Complaint incidence shifts (interaction ORs)")
        fig.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    if out_pdf is not None:
        fig.savefig(out_pdf)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv", type=Path, help="Path to regression_interactions.tsv")
    ap.add_argument("out_png", type=Path, help="Output PNG path")
    ap.add_argument("--out-pdf", type=Path, default=None, help="Optional output PDF path")
    args = ap.parse_args()

    df = load_interactions(args.tsv)
    forest_plot(df, args.out_png, args.out_pdf)


if __name__ == "__main__":
    main()
