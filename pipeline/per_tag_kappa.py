#!/usr/bin/env python3
"""Compute per-tag Cohen's kappa for major binary tags across two annotation CSVs.

Usage:
  python3 pipeline/per_tag_kappa.py --a pipeline/data/pilot_batch_A.csv \
    --b pipeline/data/pilot_batch_B.csv --out pipeline/outputs/per_tag_kappa.json \
    --tags warmth creativity helpfulness hedging --id-field id
"""
import argparse, csv, json
from collections import Counter
from typing import List, Dict


def to_bool(x: str) -> str:
    if x is None:
        return "__MISSING__"
    s = str(x).strip().lower()
    if s in ("", "na", "n/a", "none"):
        return "__MISSING__"
    if s in ("1", "y", "yes", "true", "t", "pos", "positive"):
        return "1"
    if s in ("0", "n", "no", "false", "f", "neg", "negative"):
        return "0"
    # Fallback: any non-empty value counts as positive
    return "1"


def read_rows(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cohen_kappa(labels_a: List[str], labels_b: List[str]) -> float:
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    if n == 0:
        return 0.0
    agree = sum(1 for x, y in zip(labels_a, labels_b) if x == y)
    po = agree / n
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    pe = sum((counts_a[l] / n) * (counts_b[l] / n) for l in set(labels_a + labels_b))
    if pe == 1:
        return 0.0
    return (po - pe) / (1 - pe) if (1 - pe) else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--tags", nargs="+", default=["warmth", "creativity", "helpfulness", "hedging"]) 
    ap.add_argument("--id-field", default="id")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows_a = read_rows(args.a)
    rows_b = read_rows(args.b)
    map_a = {r.get(args.id_field): r for r in rows_a if r.get(args.id_field)}
    map_b = {r.get(args.id_field): r for r in rows_b if r.get(args.id_field)}
    shared = sorted(set(map_a) & set(map_b))

    result = {"n_shared": len(shared), "per_tag": {}, "meta": {"id_field": args.id_field}}
    for t in args.tags:
        la, lb = [], []
        for i in shared:
            va = to_bool(map_a[i].get(t))
            vb = to_bool(map_b[i].get(t))
            if va == "__MISSING__" or vb == "__MISSING__":
                continue
            la.append(va)
            lb.append(vb)
        k = cohen_kappa(la, lb) if la else 0.0
        result["per_tag"][t] = {
            "kappa": round(k, 6),
            "n_pairs": len(la)
        }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Per-tag kappa -> {args.out} (n_shared={result['n_shared']})")


if __name__ == "__main__":
    main()
