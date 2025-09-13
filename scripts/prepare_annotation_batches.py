#!/usr/bin/env python3
"""Prepare annotation batch CSVs from selection_final.csv for dual annotators with overlap.

Steps:
 1. Load selection_final.csv (multi-transition stratified sample).
 2. Convert to labeling schema fields required by existing split tool.
 3. Write batch master CSV.
 4. Invoke split_for_dual_annotation.py with overlap proportion flag.

Usage:
  python scripts/prepare_annotation_batches.py --selection pipeline/outputs/annotation/selection_final.csv \
      --out pipeline/data/label_batch1.csv --overlap-frac 0.15 --seed 42
"""
from __future__ import annotations
import argparse, csv, os, math, subprocess, sys

LABEL_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post","primary_tag","secondary_flags","annotator_id"]


def build_label_row(r):
    # Placeholder mapping; selection file lacks thread_id/parent/body text in current schema.
    # We map id -> comment_id and leave thread_id/parent_id blank (limitation documented).
    return {
        'comment_id': r['id'],
        'thread_id': '',
        'parent_id': '',
        'created_utc': '',
        'score': '',
        'score_bucket': r.get('score_bucket',''),
        'body': '',  # body text not present; requires future enrichment step.
        'transition': r.get('transition',''),
        'pre_post': r.get('pre_post',''),
        'primary_tag': '',
        'secondary_flags': '',
        'annotator_id': ''
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--selection', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--overlap-frac', type=float, default=0.15)
    ap.add_argument('--seed', type=int, default=42)
    args=ap.parse_args()

    rows=[]
    with open(args.selection,'r',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        for r in reader:
            rows.append(build_label_row(r))

    n=len(rows)
    overlap=max(1, int(math.floor(n*args.overlap_frac)))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=LABEL_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Master batch written {args.out} (n={n}, planned overlap={overlap})")

    split_script='pipeline/split_for_dual_annotation.py'
    cmd=['python', split_script, '--in', args.out, '--out-prefix', args.out.rsplit('.csv',1)[0], '--overlap', str(overlap), '--seed', str(args.seed)]
    r=subprocess.run(cmd, text=True)
    if r.returncode!=0:
        print('Split script failed', file=sys.stderr)

if __name__=='__main__':
    main()
