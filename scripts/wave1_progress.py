#!/usr/bin/env python3
"""Wave 1 annotation progress for enriched batches.

Tracks completion for primary_tag, per-label counts, and overlap coverage.

Usage:
  python scripts/wave1_progress.py \
    --csv pipeline/data/label_batch1_A_enriched.csv \
    --overlap-ids pipeline/data/label_batch1_overlap_ids.txt \
    --id-col comment_id --out pipeline/outputs/annotation/wave1_A_progress.json
"""
from __future__ import annotations
import argparse, csv, json
from typing import Dict, Set


def load_overlap(path: str) -> Set[str]:
    s=set()
    if not path:
        return s
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                s.add(ln)
    return s


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--overlap-ids', required=False)
    ap.add_argument('--id-col', default='comment_id')
    ap.add_argument('--label-col', default='primary_tag')
    args=ap.parse_args()

    overlap=load_overlap(args.overlap_ids) if args.overlap_ids else set()

    total=0
    labeled=0
    per_label: Dict[str,int]={}
    overlap_total=len(overlap)
    overlap_labeled=0

    with open(args.csv,'r',encoding='utf-8') as f:
        r=csv.DictReader(f)
        for row in r:
            total+=1
            lab=(row.get(args.label_col) or '').strip()
            rid=(row.get(args.id_col) or '').strip()
            if lab:
                labeled+=1
                per_label[lab]=per_label.get(lab,0)+1
                if overlap and rid in overlap:
                    overlap_labeled+=1

    out={
        'file': args.csv,
        'id_col': args.id_col,
        'label_col': args.label_col,
        'total_rows': total,
        'rows_with_label': labeled,
        'completion_pct': (labeled/total*100) if total else 0.0,
        'per_label_counts': per_label,
        'overlap_total': overlap_total,
        'overlap_labeled': overlap_labeled,
        'overlap_completion_pct': (overlap_labeled/overlap_total*100) if overlap_total else None
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Wave1 progress -> {args.out} (completion={out['completion_pct']:.1f}%)")

if __name__=='__main__':
    main()
