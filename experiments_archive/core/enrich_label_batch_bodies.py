#!/usr/bin/env python3
"""Enrich label batch CSV(s) with actual body text and metadata from normalized window JSONL files.

Problem: Current label_batch1*.csv files have empty body/thread/parent fields. This script merges in
body, created_utc, score, parent/link ids where available, ignoring rows that remain empty_content.

Inputs:
  - One or more batch CSV paths (e.g., pipeline/data/label_batch1.csv, label_batch1_A.csv, label_batch1_B.csv)
  - Normalized window files located at pipeline/data/<transition>_{pre,post}.jsonl

Output:
  - Overwrite (or write new if --suffix provided) enriched CSV with filled columns.
  - Report counts of rows updated and rows still empty.

Usage:
  python scripts/enrich_label_batch_bodies.py --batches pipeline/data/label_batch1.csv pipeline/data/label_batch1_A.csv \
      --data-dir pipeline/data --suffix _enriched

Safety:
  - By default writes alongside original with suffix to avoid accidental destructive overwrite.
  - Use --in-place to overwrite originals (only after verifying diff).
"""
from __future__ import annotations
import argparse, csv, json, os, sys
from collections import defaultdict

REQUIRED_BATCH_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post","primary_tag","secondary_flags","annotator_id"]
WINDOW_SUFFIXES = ["pre","post"]

def load_windows(data_dir: str):
    """Load all normalized window jsonl files into a mapping: (transition,id)-> record."""
    index = {}
    for fname in os.listdir(data_dir):
        if not fname.endswith('.jsonl'): continue
        parts = fname.split('_')
        if len(parts) < 2: continue
        if parts[-1].replace('.jsonl','') not in WINDOW_SUFFIXES:
            continue
        transition = '_'.join(parts[:-1])  # join all but last token (pre/post)
        phase = parts[-1].replace('.jsonl','')
        path = os.path.join(data_dir,fname)
        with open(path,'r',encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try:
                    obj=json.loads(line)
                except json.JSONDecodeError:
                    continue
                cid=obj.get('id')
                if not cid: continue
                index[(transition, cid)] = obj
    return index

def enrich_batch(batch_path: str, index: dict, out_path: str, in_place: bool=False):
    updated=0
    missing=0
    total=0
    rows=[]
    with open(batch_path,'r',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        for r in reader:
            total+=1
            cid=r.get('comment_id')
            transition=r.get('transition')
            key=(transition, cid)
            meta=index.get(key)
            if meta:
                # Fill only if empty to preserve any manual edits.
                if not r.get('body'):
                    r['body']=meta.get('body','')
                if not r.get('created_utc'):
                    r['created_utc']=str(meta.get('created_utc',''))
                if not r.get('score'):
                    r['score']=str(meta.get('score',''))
                if not r.get('score_bucket'):
                    r['score_bucket']=meta.get('score_bucket','')
                if not r.get('thread_id'):
                    # prefer link_id else parent_id fallback
                    r['thread_id']=meta.get('link_id') or meta.get('parent_id') or ''
                if not r.get('parent_id') and meta.get('parent_id'):
                    r['parent_id']=meta.get('parent_id')
                updated+=1
            else:
                missing+=1
            rows.append(r)
    # Write out
    target= batch_path if in_place and not out_path else out_path or (batch_path + '_enriched.csv')
    with open(target,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=REQUIRED_BATCH_FIELDS)
        w.writeheader()
        for r in rows:
            # Ensure all required fields
            for fld in REQUIRED_BATCH_FIELDS:
                r.setdefault(fld,'')
            w.writerow(r)
    still_empty=sum(1 for r in rows if not r.get('body'))
    print(f"Enriched {os.path.basename(batch_path)} -> {os.path.basename(target)} | matched={updated} missing_meta={missing} body_missing_after={still_empty}/{total}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--batches', nargs='+', required=True, help='Batch CSV paths to enrich')
    ap.add_argument('--data-dir', default='pipeline/data', help='Directory containing normalized window jsonl files')
    ap.add_argument('--suffix', default='_enriched', help='Suffix appended before .csv (ignored if --in-place or --out provided)')
    ap.add_argument('--in-place', action='store_true', help='Overwrite original batch files')
    ap.add_argument('--out', nargs='*', help='Explicit output paths (must align with batches order)')
    args=ap.parse_args()

    index=load_windows(args.data_dir)
    if not index:
        print('No window JSONL files indexed; aborting.', file=sys.stderr)
        sys.exit(1)

    outs=args.out or []
    if outs and len(outs)!=len(args.batches):
        print('--out count must match batches length', file=sys.stderr)
        sys.exit(1)

    for i, b in enumerate(args.batches):
        if not os.path.exists(b):
            print(f'Skip missing batch: {b}', file=sys.stderr)
            continue
        base_out=None
        if outs:
            base_out=outs[i]
        elif not args.in_place:
            root,ext=os.path.splitext(b)
            base_out=f"{root}{args.suffix}{ext}" if args.suffix else f"{root}_enriched{ext}"
        enrich_batch(b, index, base_out, in_place=args.in_place)

if __name__=='__main__':
    main()
