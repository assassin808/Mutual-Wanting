#!/usr/bin/env python3
"""Quick labeling progress + distribution report for annotation batches.

Purpose: Provide real-time monitoring of labeling throughput and emerging class balance to decide when to trigger reliability computation and modeling.

Usage:
  python pipeline/labeling_progress.py --files pipeline/data/label_batch2_A.csv pipeline/data/label_batch2_B.csv --out pipeline/data/labeling_progress.json
"""
from __future__ import annotations
import csv, argparse, json, collections, os, time

PRIMARY_COL = 'primary_tag'

def scan_file(path: str):
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        total = 0
        labeled = 0
        dist = collections.Counter()
        for row in r:
            total += 1
            tag = (row.get(PRIMARY_COL) or '').strip()
            if tag:
                labeled += 1
                dist[tag] += 1
        return {
            'file': os.path.basename(path),
            'total': total,
            'labeled': labeled,
            'pct_labeled': labeled/total if total else 0.0,
            'label_dist': dist
        }

def merge_dists(reports):
    total = sum(r['total'] for r in reports)
    labeled = sum(r['labeled'] for r in reports)
    dist = collections.Counter()
    for r in reports:
        dist.update(r['label_dist'])
    return {
        'total': total,
        'labeled': labeled,
        'pct_labeled': labeled/total if total else 0.0,
        'label_dist': dist
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    per = [scan_file(p) for p in args.files]
    merged = merge_dists(per)
    # Convert counters to plain dicts
    for r in per:
        r['label_dist'] = dict(r['label_dist'])
    merged['label_dist'] = dict(merged['label_dist'])
    report = {
        'timestamp': time.time(),
        'per_file': per,
        'aggregate': merged
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(report,f,indent=2)
    print(f"Labeling progress -> {args.out} (aggregate pct labeled={merged['pct_labeled']:.2%})")

if __name__ == '__main__':
    main()
