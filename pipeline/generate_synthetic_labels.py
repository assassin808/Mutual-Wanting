#!/usr/bin/env python3
"""Generate a synthetic labeled dataset from an unlabeled batch CSV for pipeline validation.

It:
  * Reads an existing labeling CSV (e.g., label_batch2.csv)
  * Randomly assigns a primary_tag from the official set with configurable sparsity
  * Optionally injects both pre and post phases to enable regression structure
  * Writes *_synthetic.csv for downstream regression / feature validation

Usage:
  python pipeline/generate_synthetic_labels.py --in pipeline/data/label_batch2.csv \
      --out pipeline/data/label_batch2_synth_annotated.csv --seed 42 --rate 0.55
"""
from __future__ import annotations
import csv, argparse, random

PRIMARY_TAGS = [
    'warmth_regression','creativity_regression','helpfulness_regression',
    'hedging_shift','safety_refusal_shift','memory_continuity',
    'verbosity_change','latency_speed','access_limit'
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--rate', type=float, default=0.5, help='Proportion of rows assigned some complaint tag')
    ap.add_argument('--force-post-frac', type=float, default=0.4, help='Fraction of rows set to post (if currently all pre)')
    args = ap.parse_args()

    random.seed(args.seed)

    with open(args.inp,'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Determine if we need to inject post
    all_pre = all(r.get('pre_post') == 'pre' for r in rows if r.get('pre_post'))
    if all_pre:
        # Flip a fraction to post for structural diversity
        k = int(len(rows) * args.force_post_frac)
        flip_indices = set(random.sample(range(len(rows)), k))
    else:
        flip_indices = set()

    for i, r in enumerate(rows):
        if i in flip_indices:
            r['pre_post'] = 'post'
        assign = random.random() < args.rate
        if assign:
            r['primary_tag'] = random.choice(PRIMARY_TAGS)
            r['secondary_flags'] = ''
            r['annotator_id'] = 'synth'
        else:
            r['primary_tag'] = ''
            r['secondary_flags'] = ''
            r['annotator_id'] = 'synth'

    fieldnames = reader.fieldnames
    with open(args.out,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Synthetic labels written: {len(rows)} rows -> {args.out}")

if __name__ == '__main__':
    main()
