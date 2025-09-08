#!/usr/bin/env python3
"""Compute Cohen's kappa across two annotation CSVs.

Assumes same id universe; rows missing in one file are skipped.
Per-tag kappas + overall majority tag presence kappa.
"""
from __future__ import annotations
import argparse, csv, math, collections, json, pathlib

TAGS = ["warmth", "creativity", "helpfulness", "hedging", "complaint"]

def load(path):
    rows = {}
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows[row['id']] = row
    return rows

def cohen_kappa(a_labels, b_labels):
    assert len(a_labels) == len(b_labels)
    if not a_labels:
        return float('nan')
    agree = sum(1 for x,y in zip(a_labels,b_labels) if x == y)
    p0 = agree / len(a_labels)
    # Expected agreement
    counts_a = collections.Counter(a_labels)
    counts_b = collections.Counter(b_labels)
    pe = 0.0
    for k in set(counts_a.keys()) | set(counts_b.keys()):
        pe += (counts_a[k]/len(a_labels)) * (counts_b[k]/len(b_labels))
    if math.isclose(1-pe, 0.0):
        return float('nan')
    return (p0 - pe) / (1 - pe)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--out')
    args = ap.parse_args()

    A = load(args.a)
    B = load(args.b)
    shared_ids = sorted(set(A.keys()) & set(B.keys()))
    results = { 'n_shared': len(shared_ids), 'per_tag': {} }
    overall_a = []
    overall_b = []
    for tag in TAGS:
        a_labels = []
        b_labels = []
        for i in shared_ids:
            av = (A[i].get(tag) or '').strip().lower()
            bv = (B[i].get(tag) or '').strip().lower()
            if av == '' and bv == '':
                continue
            a_labels.append(av)
            b_labels.append(bv)
        kappa = cohen_kappa(a_labels, b_labels) if a_labels else float('nan')
        results['per_tag'][tag] = kappa
        overall_a.extend(a_labels)
        overall_b.extend(b_labels)
    results['kappa_overall'] = cohen_kappa(overall_a, overall_b) if overall_a else float('nan')
    if args.out:
        with open(args.out,'w',encoding='utf-8') as f:
            json.dump(results,f,indent=2)
        print(f"Agreement -> {args.out}")
    else:
        print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Inter-annotator agreement utility.

Supports two schemas:
    * Comment batch (default): id column 'comment_id'
    * Pilot submission batch: id column 'id' (invoke with --mode pilot)

Computes Cohen's kappa (overall), per-class confusion matrix, and per-class
pairwise agreement rates (optional diagnostic) across shared IDs only.

Usage:
    python pipeline/agreement.py --a label_batch1_annotated_A.csv --b label_batch1_annotated_B.csv \
            --out pipeline/data/agreement.json
    python pipeline/agreement.py --mode pilot --a pipeline/data/pilot_batch_A_annotated.csv \
            --b pipeline/data/pilot_batch_B_annotated.csv --out pipeline/data/pilot_agreement.json
"""
from __future__ import annotations
import csv, argparse, json
from collections import Counter
from typing import Dict, List, Tuple

MISSING = '__MISSING__'

def load_map(path: str, id_field: str) -> Dict[str,str]:
    m: Dict[str,str] = {}
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            cid = row.get(id_field)
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
    ap.add_argument('--mode', choices=['comment','pilot'], default='comment', help='Schema mode')
    args = ap.parse_args()

    id_field = 'comment_id' if args.mode == 'comment' else 'id'
    A = load_map(args.a, id_field)
    B = load_map(args.b, id_field)
    shared = sorted(set(A.keys()) & set(B.keys()))
    if not shared:
        raise SystemExit('No shared IDs between annotation files.')
    labels_a = [A[c] for c in shared]
    labels_b = [B[c] for c in shared]

    kappa = cohen_kappa(labels_a, labels_b)
    matrix = confusion(labels_a, labels_b)

    # Per-class raw agreement (diagonal / class total in shared positions for that class in either annotator)
    per_class_agree = {}
    classes = set(labels_a + labels_b)
    for cls in classes:
        total_cls = sum(1 for a,b in zip(labels_a, labels_b) if (a == cls or b == cls))
        diag = matrix[cls][cls]
        per_class_agree[cls] = diag / total_cls if total_cls else 0.0

    result = {
        'mode': args.mode,
        'id_field': id_field,
        'n_shared': len(shared),
        'kappa': kappa,
        'confusion': matrix,
        'label_dist_a': dict(Counter(labels_a)),
        'label_dist_b': dict(Counter(labels_b)),
        'per_class_agreement': per_class_agree
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(f"Agreement results -> {args.out} (mode={args.mode}, kappa={kappa:.3f})")

if __name__ == '__main__':
    main()
