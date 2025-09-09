#!/usr/bin/env python3
"""
Render Fig2 (Annotation reliability heatmap) from pipeline/outputs/figs/confusion_heatmap.csv.
Generates a simple PNG using matplotlib/seaborn.
"""
import os, sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main(csv_path='pipeline/outputs/figs/confusion_heatmap.csv', out_png='pipeline/outputs/figs/fig2_confusion_heatmap.png'):
    if not os.path.exists(csv_path):
        print(f"Missing CSV: {csv_path}")
        sys.exit(0)
    df = pd.read_csv(csv_path)
    # Expect columns: true,pred,count
    col_true = 'true' if 'true' in df.columns else 'label_a'
    col_pred = 'pred' if 'pred' in df.columns else 'label_b'
    pivot = df.pivot_table(index=col_true, columns=col_pred, values='count', fill_value=0)
    plt.figure(figsize=(6,5))
    # Cast to integers if possible for cleaner labels
    try:
        pivot_anno = pivot.astype(int)
        fmt = 'd'
    except Exception:
        pivot_anno = pivot
        fmt = '.0f'
    sns.heatmap(pivot_anno, annot=True, fmt=fmt, cmap='Blues', cbar=False, linewidths=0.5)
    plt.title('Annotation Reliability: Confusion Matrix (Pilot)')
    plt.xlabel('Annotator B')
    plt.ylabel('Annotator A')
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    print(f"Saved {out_png}")


if __name__ == '__main__':
    csv = sys.argv[1] if len(sys.argv) > 1 else 'pipeline/outputs/figs/confusion_heatmap.csv'
    out = sys.argv[2] if len(sys.argv) > 2 else 'pipeline/outputs/figs/fig2_confusion_heatmap.png'
    main(csv, out)
