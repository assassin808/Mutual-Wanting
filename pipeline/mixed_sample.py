#!/usr/bin/env python3
"""Create a mixed sample: enriched (filtered) + baseline (random) for labeling.
Supply one or more enriched JSONL files and one or more baseline JSONL files.
Per target size n, allocate 60% enriched, 40% baseline (adjust if one side insufficient).

Usage:
  python pipeline/mixed_sample.py --enriched pipeline/data/live_raw_kw_expanded.jsonl \
      --baseline pipeline/data/live_raw.jsonl --out pipeline/data/label_batch2.csv --n 140
"""
from __future__ import annotations
import json, csv, argparse, random
from typing import List, Dict

PRIMARY_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post"]


def load_jsonl(path: str) -> List[Dict]:
    out = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                out.append(json.loads(line))
    return out


def dedup(rows: List[Dict]) -> List[Dict]:
    seen = set()
    uniq = []
    for r in rows:
        cid = r.get('comment_id')
        if cid and cid not in seen:
            seen.add(cid)
            uniq.append(r)
    return uniq


def sample(rows: List[Dict], k: int) -> List[Dict]:
    if k >= len(rows):
        return rows.copy()
    return random.sample(rows, k)


def write_csv(path: str, rows: List[Dict]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(PRIMARY_FIELDS + ["primary_tag","secondary_flags","annotator_id"])
        for r in rows:
            w.writerow([r.get(f,'') for f in PRIMARY_FIELDS] + ["","",""])  # blanks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--enriched', nargs='+', required=True)
    ap.add_argument('--baseline', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=140)
    args = ap.parse_args()

    enr_rows = []
    for p in args.enriched:
        enr_rows.extend(load_jsonl(p))
    base_rows = []
    for p in args.baseline:
        base_rows.extend(load_jsonl(p))

    enr_rows = dedup(enr_rows)
    base_rows = dedup(base_rows)

    target_enr = int(args.n * 0.6)
    target_base = args.n - target_enr

    chosen_enr = sample(enr_rows, target_enr)
    chosen_base = sample(base_rows, target_base)

    combined = chosen_enr + chosen_base
    random.shuffle(combined)

    write_csv(args.out, combined)
    print(f"Mixed sample written: {len(combined)} rows (enriched={len(chosen_enr)}, baseline={len(chosen_base)}) -> {args.out}")

if __name__ == '__main__':
    main()
