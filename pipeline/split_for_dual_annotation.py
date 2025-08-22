#!/usr/bin/env python3
"""Split a labeling batch into two annotator assignment files with an overlap subset.

Purpose: Enable inter-annotator agreement (Cohen's kappa) by designating a shared overlap while distributing remaining rows evenly.

Usage:
  python pipeline/split_for_dual_annotation.py --in pipeline/data/label_batch2.csv \
      --out-prefix pipeline/data/label_batch2 --overlap 25 --seed 42

Outputs:
  <prefix>_A.csv  - Annotator A assignment (includes overlap rows)
  <prefix>_B.csv  - Annotator B assignment (includes overlap rows)
  <prefix>_overlap_ids.txt - Plain list of comment_ids in the overlap subset

All files retain original header; unlabeled fields (primary_tag, secondary_flags, annotator_id) remain blank.
"""
from __future__ import annotations
import csv, argparse, random, os
from typing import List, Dict

PRIMARY_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post","primary_tag","secondary_flags","annotator_id"]

def load_rows(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_rows(path: str, rows: List[Dict[str,str]]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=PRIMARY_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k,'') for k in PRIMARY_FIELDS})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out-prefix', required=True)
    ap.add_argument('--overlap', type=int, default=25, help='Number of items to assign to both annotators')
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    rows = load_rows(args.inp)
    random.seed(args.seed)
    idxs = list(range(len(rows)))
    random.shuffle(idxs)
    overlap_n = min(args.overlap, len(rows))
    overlap_idxs = set(idxs[:overlap_n])
    remaining = [i for i in idxs if i not in overlap_idxs]
    # Split remaining roughly in half
    mid = len(remaining)//2
    a_extra = set(remaining[:mid])
    b_extra = set(remaining[mid:])

    annot_a = [rows[i] for i in sorted(overlap_idxs | a_extra)]
    annot_b = [rows[i] for i in sorted(overlap_idxs | b_extra)]

    out_a = f"{args.out_prefix}_A.csv"
    out_b = f"{args.out_prefix}_B.csv"
    write_rows(out_a, annot_a)
    write_rows(out_b, annot_b)

    overlap_path = f"{args.out_prefix}_overlap_ids.txt"
    with open(overlap_path,'w',encoding='utf-8') as f:
        for i in sorted(overlap_idxs):
            f.write(rows[i].get('comment_id','') + '\n')

    print(f"Split complete: overlap={overlap_n}, A={len(annot_a)}, B={len(annot_b)}")
    print(f"Files: {out_a}, {out_b}, {overlap_path}")

if __name__ == '__main__':
    main()
