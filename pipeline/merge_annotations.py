#!/usr/bin/env python3
"""Merge multiple annotated CSVs into a consensus labeled dataset.

Functions:
  - Loads any number of *_annotated.csv files (same schema produced by annotation_tool.py)
  - Aligns by comment_id
  - Computes per-item:
       * set of provided primary_tag values (excluding empty)
       * consensus tag (majority; ties -> '__TIE__')
       * number of distinct tags
       * annotator coverage count
  - Emits:
       1. consensus CSV with chosen primary_tag (blank if none) and disagreement metadata
       2. JSON summary (label prevalence, disagreement rate, tie list)

Usage:
  python pipeline/merge_annotations.py --inputs file1.csv file2.csv --out-csv pipeline/data/labels_consensus.csv --out-json pipeline/data/labels_consensus_summary.json
"""
from __future__ import annotations
import csv, argparse, json, collections
from typing import Dict, List

TIE_TOKEN = '__TIE__'
MISSING = ''

PRIMARY_COL = 'primary_tag'
ID_COL = 'comment_id'


def load(path: str) -> Dict[str, Dict[str,str]]:
    out = {}
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            cid = row.get(ID_COL)
            if not cid:
                continue
            out[cid] = row
    return out


def majority(tags: List[str]) -> str:
    filt = [t for t in tags if t]
    if not filt:
        return MISSING
    counter = collections.Counter(filt)
    top = counter.most_common()
    if len(top) == 1:
        return top[0][0]
    if len(top) > 1 and top[0][1] == top[1][1]:
        return TIE_TOKEN
    return top[0][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', nargs='+', required=True)
    ap.add_argument('--out-csv', required=True)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()

    maps = [load(p) for p in args.inputs]
    all_ids = sorted(set().union(*[m.keys() for m in maps]))

    rows_out = []
    disagreement = 0
    tie_ids = []
    label_counter = collections.Counter()

    for cid in all_ids:
        tag_list = [m.get(cid, {}).get(PRIMARY_COL, '') for m in maps]
        consensus = majority(tag_list)
        if consensus == TIE_TOKEN:
            disagreement += 1
            tie_ids.append(cid)
        if consensus and consensus != TIE_TOKEN:
            label_counter[consensus] += 1
        rows_out.append({
            ID_COL: cid,
            'consensus_primary_tag': consensus,
            'distinct_tag_count': len(set([t for t in tag_list if t])),
            'annotator_count': sum(1 for t in tag_list if t),
            'raw_tags': '|'.join(tag_list)
        })

    disagreement_rate = disagreement / len(all_ids) if all_ids else 0.0

    # Write CSV
    with open(args.out_csv,'w',newline='',encoding='utf-8') as f:
        fieldnames = [ID_COL,'consensus_primary_tag','distinct_tag_count','annotator_count','raw_tags']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    summary = {
        'n_items': len(all_ids),
        'disagreement_rate': disagreement_rate,
        'tie_ids': tie_ids,
        'label_distribution': dict(label_counter)
    }
    with open(args.out_json,'w',encoding='utf-8') as f:
        json.dump(summary,f,indent=2)
    print(f"Consensus built over {len(all_ids)} items; disagreement_rate={disagreement_rate:.3f} -> {args.out_csv}")

if __name__ == '__main__':
    main()
