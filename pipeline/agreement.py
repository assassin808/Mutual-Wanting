#!/usr/bin/env python3
"""Inter-annotator agreement utility.
Given two annotated CSVs with identical comment_id ordering or at least matching ids,
computes Cohen's kappa and per-class confusion matrix.

Usage:
  python pipeline/agreement.py --a label_batch1_annotated_A.csv --b label_batch1_annotated_B.csv --out pipeline/data/agreement.json
"""
from __future__ import annotations
import csv, argparse, json
from collections import Counter
from typing import Dict, List, Tuple

MISSING = '__MISSING__'

def load_map(path: str) -> Dict[str,str]:
    m = {}
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            cid = row.get('comment_id')
            if cid:
                m[cid] = row.get('primary_tag','').strip() or MISSING
    return m

def cohen_kappa(labels_a: List[str], labels_b: List[str]) -> float:
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    agree = sum(1 for x,y in zip(labels_a, labels_b) if x==y)
    po = agree / n if n else 0.0
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    pe = sum((counts_a[l]/n)*(counts_b[l]/n) for l in set(labels_a+labels_b))
    if pe == 1:
        return 0.0
    return (po - pe)/(1 - pe) if (1-pe) else 0.0


def confusion(labels_a: List[str], labels_b: List[str]) -> Dict[str,Dict[str,int]]:
    matrix = {}
    classes = sorted(set(labels_a + labels_b))
    for c in classes:
        matrix[c] = {d:0 for d in classes}
    for a,b in zip(labels_a, labels_b):
        matrix[a][b] += 1
    return matrix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    A = load_map(args.a)
    B = load_map(args.b)
    shared = sorted(set(A.keys()) & set(B.keys()))
    labels_a = [A[c] for c in shared]
    labels_b = [B[c] for c in shared]

    kappa = cohen_kappa(labels_a, labels_b)
    matrix = confusion(labels_a, labels_b)

    result = {
        'n_shared': len(shared),
        'kappa': kappa,
        'confusion': matrix,
        'label_dist_a': dict(Counter(labels_a)),
        'label_dist_b': dict(Counter(labels_b))
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(f"Agreement results -> {args.out} (kappa={kappa:.3f})")

if __name__ == '__main__':
    main()
