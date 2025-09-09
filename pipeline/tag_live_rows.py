#!/usr/bin/env python3
"""Tag rows from the live supplement so they can be excluded from authentic transition analyses.

Adds field: source_tag = 'live_pilot_only'

Usage:
  python pipeline/tag_live_rows.py --in pipeline/data/recent_corpus_merged_dedup2.jsonl --out pipeline/data/recent_corpus_tagged.jsonl
"""
from __future__ import annotations
import argparse, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--tag', default='live_pilot_only')
    args = ap.parse_args()
    n=0
    with open(args.inp,'r',encoding='utf-8') as fin, open(args.out,'w',encoding='utf-8') as fout:
        for line in fin:
            if not line.strip():
                continue
            obj = json.loads(line)
            obj['source_tag'] = args.tag
            fout.write(json.dumps(obj, ensure_ascii=False)+'\n')
            n+=1
    print(f"Tagged {n} rows -> {args.out}")

if __name__ == '__main__':
    main()
