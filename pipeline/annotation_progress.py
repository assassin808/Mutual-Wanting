#!/usr/bin/env python3
"""Compute annotation progress for a pilot batch CSV.

Counts per tag (y/n/blank), completion %, and overlap label density if overlap id list provided.

Usage:
  python pipeline/annotation_progress.py --csv pipeline/data/pilot_batch_A.csv --out pipeline/outputs/pilot_A_progress.json --overlap-ids pipeline/data/pilot_batch_overlap_ids.txt
"""
from __future__ import annotations
import argparse, csv, json, pathlib

TAGS = ["warmth","creativity","helpfulness","hedging","complaint"]

def load_overlap(path: str):
    if not path:
        return set()
    s = set()
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            if ln.strip():
                s.add(ln.strip())
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--overlap-ids')
    args = ap.parse_args()

    overlap = load_overlap(args.overlap_ids)
    total = 0
    labeled = 0
    tag_counts = {t: {'y':0,'n':0,'blank':0} for t in TAGS}
    overlap_total = len(overlap)
    overlap_labeled = 0
    with open(args.csv,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            total += 1
            any_tag = False
            for t in TAGS:
                val = (row.get(t) or '').strip().lower()
                if val == 'y':
                    tag_counts[t]['y'] += 1
                    any_tag = True
                elif val == 'n':
                    tag_counts[t]['n'] += 1
                    any_tag = True
                else:
                    tag_counts[t]['blank'] += 1
            if any_tag:
                labeled += 1
            if overlap and row.get('id') in overlap:
                # count overlap as labeled if any tag present
                if any((row.get(t) or '').strip().lower() in {'y','n'} for t in TAGS):
                    overlap_labeled += 1
    out = {
        'file': args.csv,
        'total_rows': total,
        'rows_with_any_tag': labeled,
        'completion_pct': (labeled/total*100) if total else 0.0,
        'tag_counts': tag_counts,
        'overlap_total': overlap_total,
        'overlap_labeled': overlap_labeled,
        'overlap_completion_pct': (overlap_labeled/overlap_total*100) if overlap_total else None
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Annotation progress -> {args.out}")

if __name__ == '__main__':
    main()
