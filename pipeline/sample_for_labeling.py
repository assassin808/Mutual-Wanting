#!/usr/bin/env python3
"""Sampling script with stratification.
Groups by (transition, pre_post, score_bucket) and samples proportionally.
"""
from __future__ import annotations
import json, csv, random, argparse, math
from typing import List, Dict, Any, Tuple, DefaultDict
from collections import defaultdict

PRIMARY_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post"]

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def group(rows: List[Dict[str,Any]]) -> DefaultDict[Tuple[str,str,str], List[Dict[str,Any]]]:
    buckets = defaultdict(list)
    for r in rows:
        key = (r.get("transition"), r.get("pre_post"), r.get("score_bucket"))
        if None in key:
            continue
        buckets[key].append(r)
    return buckets


def stratified_sample(rows: List[Dict[str,Any]], n: int) -> List[Dict[str,Any]]:
    buckets = group(rows)
    total = sum(len(v) for v in buckets.values()) or 1
    out: List[Dict[str,Any]] = []
    for k, items in buckets.items():
        share = len(items) / total
        take = min(len(items), max(1, int(round(share * n))))
        out.extend(random.sample(items, take))
    random.shuffle(out)
    return out[:n]


def write_csv(path: str, rows: List[Dict[str,Any]]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        header = PRIMARY_FIELDS + ["primary_tag","secondary_flags","annotator_id"]
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(k,"") for k in PRIMARY_FIELDS] + ["", "", ""])  # blanks for labeling


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', nargs='+', required=True, help='Raw JSONL files')
    ap.add_argument('--out', required=True, help='Output CSV for labeling')
    ap.add_argument('--n', type=int, default=600, help='Target total sample size')
    args = ap.parse_args()

    all_rows = []
    for p in args.raw:
        all_rows.extend(load_jsonl(p))
    sampled = stratified_sample(all_rows, args.n)
    write_csv(args.out, sampled)
    print(f"Sampled {len(sampled)} / {len(all_rows)} -> {args.out}")

if __name__ == '__main__':
    main()
