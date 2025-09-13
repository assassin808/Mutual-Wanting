#!/usr/bin/env python3
"""
Render Fig2 confusion heatmap from CSV or JSON matrix; supports row normalization and PDF output.
Default CSV path: pipeline/outputs/figs/confusion_heatmap.csv
Default PNG path: pipeline/outputs/figs/fig2_confusion_heatmap.png
"""
import argparse
import json
import os
import sys
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def load_matrix(path: str) -> Tuple[List[str], List[str], np.ndarray]:
    if not os.path.exists(path):
        print(f"Missing input: {path}")
        sys.exit(0)
    if path.lower().endswith(".json"):
        with open(path, "r") as f:
            obj = json.load(f)
        labels = [str(x) for x in obj["labels"]]
        mat = np.array(obj["matrix"], dtype=float)
        return labels, labels, mat
    # CSV path
    df = pd.read_csv(path)
    # common long format: true,pred,count
    if set(["true", "pred", "count"]).issubset(df.columns):
        pivot = df.pivot_table(index="true", columns="pred", values="count", fill_value=0)
        return [str(x) for x in pivot.index], [str(x) for x in pivot.columns], pivot.to_numpy(dtype=float)
    # wide-format matrix: first column as row labels, remaining as value columns
    if len(df.columns) > 2 and not set(["true","pred","count"]).issubset(df.columns):
        rows = [str(x) for x in df.iloc[:,0]]
        cols = [str(x) for x in df.columns[1:]]
        mat = df.iloc[:,1:].to_numpy(dtype=float)
        return rows, cols, mat
    # alt naming (label_a/label_b)
    col_true = "true" if "true" in df.columns else ("label_a" if "label_a" in df.columns else df.columns[0])
    col_pred = "pred" if "pred" in df.columns else ("label_b" if "label_b" in df.columns else df.columns[1])
    value_col = "count" if "count" in df.columns else df.columns[-1]
    pivot = df.pivot_table(index=col_true, columns=col_pred, values=value_col, fill_value=0)
    return [str(x) for x in pivot.index], [str(x) for x in pivot.columns], pivot.to_numpy(dtype=float)


def normalize_rows(mat: np.ndarray) -> np.ndarray:
    sums = mat.sum(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        props = np.divide(mat, sums, where=(sums != 0))
    props[np.isnan(props)] = 0.0
    return props


def render_heatmap(rows: List[str], cols: List[str], mat: np.ndarray, out_png: str, out_pdf: str | None = None, title: str | None = None, cmap: str = "Blues", annotate: bool = True, fmt: str = ".2f"):
    plt.figure(figsize=(6.5, 5.2))
    ax = sns.heatmap(mat, xticklabels=cols, yticklabels=rows, cmap=cmap, annot=annotate, fmt=fmt, vmin=0.0, vmax=1.0, cbar_kws={"label": "Proportion"})
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    if title:
        ax.set_title(title)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=200)
    if out_pdf:
        plt.savefig(out_pdf)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_path", nargs="?", default="pipeline/outputs/figs/confusion_heatmap.csv")
    ap.add_argument("out_png", nargs="?", default="pipeline/outputs/figs/fig2_confusion_heatmap.png")
    ap.add_argument("--out-pdf")
    ap.add_argument("--normalize", action="store_true")
    ap.add_argument("--title", default="Annotation Reliability: Confusion Matrix")
    args = ap.parse_args()

    rows, cols, mat = load_matrix(args.in_path)
    if args.normalize:
        mat = normalize_rows(mat)
    # choose annotation format: proportions or counts
    fmt = ".2f" if args.normalize else ".0f"
    render_heatmap(rows, cols, mat, args.out_png, args.out_pdf, args.title, fmt=fmt)
    print(f"Saved {args.out_png}" + (f" and {args.out_pdf}" if args.out_pdf else ""))


if __name__ == "__main__":
    main()
