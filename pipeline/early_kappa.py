#!/usr/bin/env python3
"""Early (partial) Cohen's kappa computation for pilot overlap rows.

Inputs:
  --a  Annotator A CSV (pilot_batch_A.csv)
  --b  Annotator B CSV (pilot_batch_B.csv)
  --overlap-ids  TXT listing overlap ids (one per line)
  --out JSON path

Assumptions:
  Columns per tag are binary 'y'/'n' or blank.
  Tags: warmth, creativity, helpfulness, hedging, complaint.

Behavior:
  - Restricts to overlap IDs only.
  - For each tag keeps rows where BOTH annotators provided y/n.
  - Computes Cohen's kappa per tag (simple nominal, two categories y/n).
  - Flags tags with <5 overlapping labeled pairs as 'insufficient'.
  - Reports overall (pooled across tags) kappa treating each tag decision as separate item.

Output JSON fields:
  n_overlap_ids, per_tag:{ tag:{n_pairs,kappa,status}}, overall:{n_pairs,kappa}
"""
from __future__ import annotations
import argparse, csv, json, math

TAGS = ["warmth","creativity","helpfulness","hedging","complaint"]

def load_overlap(path: str):
    s=set()
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                s.add(ln)
    return s

def load_csv(path: str):
    rows={}
    with open(path,'r',encoding='utf-8') as f:
        r=csv.DictReader(f)
        for row in r:
            rows[row['id']]=row
    return rows

def cohen_kappa(a, b):
    assert len(a)==len(b)
    if not a:
        return float('nan')
    n=len(a)
    agree=sum(1 for x,y in zip(a,b) if x==y)
    po=agree/n
    ya=a.count('y'); na=a.count('n')
    yb=b.count('y'); nb=b.count('n')
    pe=((ya/n)*(yb/n))+((na/n)*(nb/n))
    if math.isclose(1-pe,0.0):
        return float('nan')
    return (po-pe)/(1-pe)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--a',required=True)
    ap.add_argument('--b',required=True)
    ap.add_argument('--overlap-ids',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--min-pairs',type=int,default=5)
    args=ap.parse_args()

    overlap=load_overlap(args.overlap_ids)
    A=load_csv(args.a)
    B=load_csv(args.b)
    per_tag={}
    pooled_a=[]; pooled_b=[]
    for tag in TAGS:
        a_vals=[]; b_vals=[]
        for oid in overlap:
            ra=A.get(oid); rb=B.get(oid)
            if not ra or not rb: continue
            av=(ra.get(tag) or '').strip().lower()
            bv=(rb.get(tag) or '').strip().lower()
            if av in {'y','n'} and bv in {'y','n'}:
                a_vals.append(av); b_vals.append(bv)
        status='ok'
        if len(a_vals) < args.min_pairs:
            status='insufficient'
        kappa = cohen_kappa(a_vals,b_vals) if a_vals else float('nan')
        per_tag[tag]={
            'n_pairs': len(a_vals),
            'kappa': kappa,
            'status': status
        }
        # Only pool if not insufficient
        pooled_a.extend(a_vals)
        pooled_b.extend(b_vals)
    overall_k = cohen_kappa(pooled_a, pooled_b) if pooled_a else float('nan')
    out={
        'n_overlap_ids': len(overlap),
        'per_tag': per_tag,
        'overall': {'n_pairs': len(pooled_a), 'kappa': overall_k},
        'min_pairs_threshold': args.min_pairs
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Early kappa -> {args.out}")

if __name__=='__main__':
    main()
