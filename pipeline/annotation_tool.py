#!/usr/bin/env python3
"""Minimal CLI annotation helper.
Reads a CSV (like label_batch1.csv), presents unlabeled rows, allows setting primary_tag and secondary_flags.
Writes in-place updates to a new CSV (adds _annotated suffix if --out unspecified).

Usage:
  python annotation_tool.py --in pipeline/data/label_batch1.csv --out pipeline/data/label_batch1_annotated.csv --annotator you
Controls:
  n - skip (next)
  q - quit
  number selections for primary tag
  s - set secondary flags (comma list)
"""
from __future__ import annotations
import csv, argparse, os, sys
from typing import List, Dict

PRIMARY_TAGS = [
    'warmth_regression', 'creativity_regression', 'helpfulness_regression',
    'hedging_shift', 'safety_refusal_shift', 'memory_continuity',
    'verbosity_change', 'latency_speed', 'access_limit', 'other'
]

SECONDARY_FLAGS = [
    'positive', 'negative', 'mixed', 'question', 'meta', 'humor'
]

def load_rows(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        return list(r)

def save_rows(path: str, rows: List[Dict[str,str]], fieldnames: List[str]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

def print_menu():
    print("Primary Tags:")
    for i,t in enumerate(PRIMARY_TAGS, start=1):
        print(f"  {i}. {t}")

def annotate(rows: List[Dict[str,str]], annotator: str):
    updated = 0
    for idx, row in enumerate(rows):
        if row.get('primary_tag'):
            continue
        body = row.get('body','')[:500]
        print("\n--- Item", idx, '---')
        print(body)
        print_menu()
        while True:
            sel = input("Select tag number (n=skip, q=quit, s=secondary): ").strip()
            if sel == 'q':
                return updated
            if sel == 'n':
                break
            if sel == 's':
                fl = input(f"Secondary flags (comma) options {SECONDARY_FLAGS}: ").strip()
                row['secondary_flags'] = ','.join([f.strip() for f in fl.split(',') if f.strip()])
                continue
            if sel.isdigit():
                num = int(sel)
                if 1 <= num <= len(PRIMARY_TAGS):
                    row['primary_tag'] = PRIMARY_TAGS[num-1]
                    row['annotator_id'] = annotator
                    updated += 1
                    break
            print("Invalid input.")
    return updated

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out')
    ap.add_argument('--annotator', required=True)
    args = ap.parse_args()

    rows = load_rows(args.inp)
    out_path = args.out or args.inp.replace('.csv','_annotated.csv')
    updated = annotate(rows, args.annotator)
    save_rows(out_path, rows, fieldnames=rows[0].keys())
    print(f"Updated {updated} items. Saved -> {out_path}")

if __name__ == '__main__':
    main()
