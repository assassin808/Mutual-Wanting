#!/usr/bin/env python3
"""Minimal leakage guard: ensure no feature column appears derived from label columns.

Heuristic:
  - For features CSV, gather column names.
  - Flag any column containing substrings of known tag names or 'primary_tag' other than the expected feature set.
  - Optional: if labels CSV provided, ensure no identical value distribution match score >0.999 between feature column and label column (simple exact match ratio).

Outputs JSON with pass/fail and any flagged columns.
"""
from __future__ import annotations
import argparse, csv, json

TAGS = ["warmth","creativity","helpfulness","hedging","complaint","primary_tag"]
ALLOWED_PREFIXES = {"token_len","hedge_rate","warmth_rate","imperative_ratio","pronoun_ratio","style_cluster"}

def load_rows(path):
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--features-csv',required=True)
    ap.add_argument('--labels-csv')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()

    rows = load_rows(args.features_csv)
    if not rows:
        raise SystemExit('No rows in features CSV')
    cols = set(rows[0].keys())
    flagged = []
    for c in cols:
        if c in ALLOWED_PREFIXES: continue
        if any(t in c.lower() for t in TAGS):
            if c not in ALLOWED_PREFIXES:
                flagged.append(c)
    leakage_pairs=[]
    if args.labels_csv:
        lrows = load_rows(args.labels_csv)
        if lrows:
            # Compare distributions
            for c in cols:
                feats=[r[c] for r in rows if r.get(c) is not None]
                for tag in TAGS:
                    if tag in rows[0]:
                        labs=[r[tag] for r in rows if r.get(tag) is not None]
                        if feats and labs and len(feats)==len(labs):
                            match=sum(1 for a,b in zip(feats,labs) if a==b)/len(feats)
                            if match > 0.999:
                                leakage_pairs.append({'feature': c,'label': tag,'match_ratio': match})
    status = 'pass' if not flagged and not leakage_pairs else 'fail'
    out={
        'status': status,
        'flagged_columns': flagged,
        'leakage_pairs': leakage_pairs
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Leak check -> {args.out} status={status}")

if __name__=='__main__':
    main()
