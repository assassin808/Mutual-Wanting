#!/usr/bin/env python3
"""Validate JSONL rows against a minimal required schema.

Usage:
  python pipeline/jsonl_schema_check.py --jsonl pipeline/data/recent_corpus_normalized_pilot.jsonl \
      --required id subreddit author_hash created_utc score body --max-errors 50
"""
from __future__ import annotations
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jsonl', required=True)
    ap.add_argument('--required', nargs='+', required=True)
    ap.add_argument('--max-errors', type=int, default=20)
    args = ap.parse_args()

    missing_examples = []
    total = 0
    bad = 0
    with open(args.jsonl,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            total += 1
            try:
                obj=json.loads(line)
            except Exception:
                bad += 1
                if len(missing_examples) < args.max_errors:
                    missing_examples.append({'line': total, 'error': 'json_decode'})
                continue
            missing=[k for k in args.required if k not in obj]
            if missing:
                bad += 1
                if len(missing_examples) < args.max_errors:
                    missing_examples.append({'line': total, 'missing': missing})
    out={
        'file': args.jsonl,
        'total_rows': total,
        'invalid_rows': bad,
        'valid_rows': total-bad,
        'examples': missing_examples
    }
    print(json.dumps(out, indent=2))

if __name__=='__main__':
    main()
