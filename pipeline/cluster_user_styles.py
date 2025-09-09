#!/usr/bin/env python3
"""Cluster user style features (optional exploratory step).

Input options:
  --features-csv  CSV produced by features_and_analysis.py (with token_len, hedge_rate, warmth_rate, imperative_ratio, pronoun_ratio)

Outputs:
  JSON summary with cluster centers & sizes
  CSV with added column style_cluster

Safeguards:
  - Skips clustering if < 30 rows (insufficient for stable k=5)
  - Drops rows with all-zero features to avoid singular clusters

Assumptions:
  - No personally identifying information in rows (author handles already hashed earlier in pipeline).
"""
from __future__ import annotations
import argparse, csv, json, math, statistics, pathlib

FEATURE_COLS = ["token_len","hedge_rate","warmth_rate","imperative_ratio","pronoun_ratio"]

def read_csv(path: str):
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        rows = list(r)
    return rows

def write_csv(path: str, fieldnames, rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def to_matrix(rows):
    X = []
    keep_idx = []
    for i,r in enumerate(rows):
        try:
            vec = [float(r.get(c,0) or 0) for c in FEATURE_COLS]
        except ValueError:
            vec = [0.0]*len(FEATURE_COLS)
        if all(v==0 for v in vec):
            continue
        X.append(vec)
        keep_idx.append(i)
    return X, keep_idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--features-csv', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-csv', required=True)
    ap.add_argument('--k', type=int, default=5)
    args = ap.parse_args()

    try:
        rows = read_csv(args.features_csv)
    except FileNotFoundError:
        summary = {"skipped": True, "reason": f"missing features CSV: {args.features_csv}"}
        with open(args.out_json,'w',encoding='utf-8') as f:
            json.dump(summary,f,indent=2)
        print(f"Cluster skipped (missing file) -> {args.out_json}")
        return
    X, keep_idx = to_matrix(rows)
    if len(X) < max(30, args.k*5):
        summary = {"skipped": True, "reason": f"insufficient rows ({len(X)}) for stable clustering"}
        with open(args.out_json,'w',encoding='utf-8') as f:
            json.dump(summary,f,indent=2)
        print(f"Cluster skipped (n={len(X)}) -> {args.out_json}")
        return
    try:
        from sklearn.cluster import KMeans
    except ImportError:
        summary = {"skipped": True, "reason": "scikit-learn not installed"}
        with open(args.out_json,'w',encoding='utf-8') as f:
            json.dump(summary,f,indent=2)
        print("Cluster skipped (missing scikit-learn)")
        return
    km = KMeans(n_clusters=args.k, n_init='auto', random_state=42)
    labels = km.fit_predict(X)
    for lbl, i in zip(labels, keep_idx):
        rows[i]['style_cluster'] = int(lbl)
    # Non-retained rows get -1 label
    for i,r in enumerate(rows):
        if 'style_cluster' not in r:
            r['style_cluster'] = -1
    # Summaries
    cluster_sizes = {}
    for l in labels:
        cluster_sizes[int(l)] = cluster_sizes.get(int(l),0)+1
    centers = []
    for c in km.cluster_centers_:
        centers.append({FEATURE_COLS[i]: float(c[i]) for i in range(len(FEATURE_COLS))})
    out_summary = {
        'k': args.k,
        'n_rows_used': len(X),
        'cluster_sizes': cluster_sizes,
        'centers': centers
    }
    with open(args.out_json,'w',encoding='utf-8') as f:
        json.dump(out_summary,f,indent=2)
    fieldnames = list(rows[0].keys())
    if 'style_cluster' not in fieldnames:
        fieldnames.append('style_cluster')
    write_csv(args.out_csv, fieldnames, rows)
    print(f"Clusters -> {args.out_json}; labeled CSV -> {args.out_csv}")

if __name__ == '__main__':
    main()
