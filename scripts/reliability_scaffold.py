#!/usr/bin/env python3
"""Reliability scaffold for Wave 1 dual annotation batches.

Functions:
  - discover overlap ids from *overlap_ids.txt
  - load enriched A/B batch CSVs
  - compute Cohen's kappa (nominal) over primary label column (configurable)
  - compute Krippendorff's alpha (nominal) using simple coincidence matrix
  - emit JSON with per-metric, counts, and per-label confusion

Usage:
  python scripts/reliability_scaffold.py \
     --a pipeline/data/label_batch1_A_enriched.csv \
     --b pipeline/data/label_batch1_B_enriched.csv \
     --overlap pipeline/data/label_batch1_overlap_ids.txt \
     --label-col primary_tag --out pipeline/outputs/annotation/reliability_wave1.json

Assumptions:
  - Overlap file contains one id per line matching 'id' column in both CSVs.
  - Missing or empty labels excluded from pair counts.
"""
from __future__ import annotations
import csv, argparse, json, math, os
from collections import Counter, defaultdict
from typing import List, Dict, Tuple


def read_csv(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_overlap_ids(path: str) -> List[str]:
    ids=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                ids.append(line)
    return ids


def cohen_kappa(a: List[str], b: List[str]) -> float:
    assert len(a)==len(b)
    n=len(a)
    if n==0:
        return float('nan')
    agree=sum(x==y for x,y in zip(a,b)) / n
    labels=sorted(set(a)|set(b))
    pa=0.0
    for L in labels:
        pa_i=(a.count(L)/n)*(b.count(L)/n)
        pa+=pa_i
    if pa==1:
        return 1.0
    return (agree - pa) / (1 - pa) if (1-pa)!=0 else float('nan')


def krippendorff_alpha_nominal(judgments: List[Tuple[str,str]]) -> float:
    """Two coder nominal alpha using coincidence matrix definition.
    judgments: list of (coderA_label, coderB_label) for overlapping items.
    """
    # Build coincidence counts (each pair contributes 2 to matrix diagonals/off-diagonals symmetrically)
    counts=Counter()
    labels=set()
    for a,b in judgments:
        labels.update([a,b])
        if a==b:
            counts[(a,a)]+=2  # double count diagonal as per coincidence definition
        else:
            counts[(a,b)]+=1
            counts[(b,a)]+=1
    if not labels:
        return float('nan')
    label_list=sorted(labels)
    # Observed disagreement Do
    Do=0.0
    n_total=sum(counts.values())
    if n_total==0:
        return float('nan')
    for i,li in enumerate(label_list):
        for j,lj in enumerate(label_list):
            if i<j:
                Dij=1  # nominal metric: 1 if different
                Do += counts[(li,lj)] * Dij
    Do = Do / (n_total - 1) if n_total>1 else float('nan')
    # Expected disagreement De
    marginals=Counter()
    for (i,j),v in counts.items():
        marginals[i]+=v
    De=0.0
    N=sum(marginals.values())
    if N<=1:
        return float('nan')
    for i,li in enumerate(label_list):
        for j,lj in enumerate(label_list):
            if i<j:
                Dij=1
                De += (marginals[li]*marginals[lj]) * Dij
    De = De / (N*(N-1)) if N>1 else float('nan')
    if De==0:
        return 1.0
    return 1 - (Do/De)


def build_confusion(a: List[str], b: List[str]) -> Dict[str,Dict[str,int]]:
    labels=sorted(set(a)|set(b))
    matrix={la:{lb:0 for lb in labels} for la in labels}
    for x,y in zip(a,b):
        matrix[x][y]+=1
    return matrix


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--overlap', required=True)
    ap.add_argument('--label-col', default='primary_tag')
    ap.add_argument('--out', required=True)
    args=ap.parse_args()

    rows_a=read_csv(args.a)
    rows_b=read_csv(args.b)
    overlap_ids=set(load_overlap_ids(args.overlap))
    by_id_a={r['id']:r for r in rows_a if r.get('id') in overlap_ids}
    by_id_b={r['id']:r for r in rows_b if r.get('id') in overlap_ids}

    pairs=[]
    for i in sorted(overlap_ids):
        ra=by_id_a.get(i)
        rb=by_id_b.get(i)
        if not ra or not rb:
            continue
        la=(ra.get(args.label_col,'') or '').strip()
        lb=(rb.get(args.label_col,'') or '').strip()
        if la and lb:
            pairs.append((la,lb))

    if not pairs:
        res={"n_pairs":0,"kappa":None,"alpha":None,"confusion":{},"labels":[]}
    else:
        a_labels=[p[0] for p in pairs]
        b_labels=[p[1] for p in pairs]
        kappa=cohen_kappa(a_labels,b_labels)
        alpha=krippendorff_alpha_nominal(pairs)
        confusion=build_confusion(a_labels,b_labels)
        res={
            "n_pairs": len(pairs),
            "kappa": kappa,
            "krippendorff_alpha": alpha,
            "labels": sorted(set(a_labels)|set(b_labels)),
            "confusion": confusion
        }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(res,f,indent=2)
    kappa_str=f"{res['kappa']:.3f}" if res['kappa'] is not None and not math.isnan(res['kappa']) else 'NA'
    alpha_val=res.get('krippendorff_alpha')
    alpha_str=f"{alpha_val:.3f}" if alpha_val is not None and not math.isnan(alpha_val) else 'NA'
    print(f"Reliability -> {args.out} (n_pairs={res['n_pairs']} kappa={kappa_str} alpha={alpha_str})")

if __name__=='__main__':
    main()
