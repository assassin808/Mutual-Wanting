#!/usr/bin/env python3
"""Split the pilot_batch.csv into two annotator assignment files with an overlap subset.

Fields expected: id, source_sub, score, score_bucket, created_utc, title, selftext, enriched_flag, primary_tag, secondary_flags, annotator_id

Defaults: overlap=20 (for 60-item pilot => ~33% dual-coded).
"""
from __future__ import annotations
import csv, argparse, random
from typing import List, Dict

FIELDS = [
    'id','source_sub','score','score_bucket','created_utc','title','selftext',
    'enriched_flag','primary_tag','secondary_flags','annotator_id'
]

def load_rows(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_rows(path: str, rows: List[Dict[str,str]]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k,'') for k in FIELDS})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out-prefix', required=True)
    ap.add_argument('--overlap', type=int, default=20)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    rows = load_rows(args.inp)
    n = len(rows)
    if n == 0:
        raise SystemExit('No rows found in input.')

    random.seed(args.seed)
    order = list(range(n))
    random.shuffle(order)
    overlap_n = min(args.overlap, n)
    overlap = set(order[:overlap_n])
    remaining = [i for i in order if i not in overlap]
    mid = len(remaining)//2
    a_extra = set(remaining[:mid])
    b_extra = set(remaining[mid:])

    a_rows = [rows[i] for i in sorted(overlap | a_extra)]
    b_rows = [rows[i] for i in sorted(overlap | b_extra)]

    out_a = f"{args.out_prefix}_A.csv"
    out_b = f"{args.out_prefix}_B.csv"
    write_rows(out_a, a_rows)
    write_rows(out_b, b_rows)

    overlap_path = f"{args.out_prefix}_overlap_ids.txt"
    with open(overlap_path,'w',encoding='utf-8') as f:
        for i in sorted(overlap):
            f.write(rows[i]['id'] + '\n')

    print(f"Pilot split complete: total={n} overlap={overlap_n} A={len(a_rows)} B={len(b_rows)}")
    print(f"Files: {out_a}, {out_b}, {overlap_path}")

if __name__ == '__main__':
    main()
