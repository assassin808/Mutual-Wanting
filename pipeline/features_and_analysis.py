#!/usr/bin/env python3
"""Feature extraction + analysis skeleton.
Focus on minimal, inspectable computations.
"""
from __future__ import annotations
import re, csv, json, argparse, math, statistics
from typing import List, Dict, Any

HEDGES = {"maybe","might","could","possibly","perhaps","seems","appears"}
WARMTH = {"thanks","thank","please","appreciate","love","enjoy"}

WORD_RE = re.compile(r"[A-Za-z']+")


def read_labeled(path: str) -> List[Dict[str,Any]]:
    out = []
    with open(path,'r',encoding='utf-8') as f:
        header = f.readline().rstrip().split(',')
        for line in f:
            parts = line.rstrip().split(',')
            row = dict(zip(header, parts))
            out.append(row)
    return out


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(text.lower())


def features(text: str) -> Dict[str,Any]:
    toks = tokenize(text)
    if not toks:
        return {"token_len":0,"hedge_rate":0,"warmth_rate":0,"imperative_ratio":0,"pronoun_ratio":0}
    token_len = len(toks)
    hedge_count = sum(t in HEDGES for t in toks)
    warmth_count = sum(t in WARMTH for t in toks)
    # Simple heuristic: imperative if starts with verb-like token and no starting pronoun (very rough)
    imperative = 1 if toks[0] not in {"i","you","we","it"} and toks[0] not in HEDGES else 0
    pronoun_count = sum(t in {"i","you","we"} for t in toks)
    return {
        "token_len": token_len,
        "hedge_rate": hedge_count / token_len,
        "warmth_rate": warmth_count / token_len,
        "imperative_ratio": imperative,
        "pronoun_ratio": pronoun_count / token_len
    }


def aggregate(rows: List[Dict[str,Any]]) -> Dict[str,Any]:
    agg = {}
    for k in ["token_len","hedge_rate","warmth_rate","imperative_ratio","pronoun_ratio"]:
        vals = [float(r[k]) for r in rows if r.get(k) is not None]
        if vals:
            agg[k] = {
                "mean": statistics.mean(vals),
                "median": statistics.median(vals)
            }
    return agg


def read_raw_jsonl(path: str) -> List[Dict[str,Any]]:
    rows = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--labeled', help='CSV with labeled data (after manual)')
    g.add_argument('--raw', help='Raw JSONL (unlabeled) quick sanity')
    ap.add_argument('--out', required=True, help='JSON summary output')
    ap.add_argument('--emit-csv', help='Optional path to write per-row features CSV for modeling')
    args = ap.parse_args()

    if args.labeled:
        data_rows = read_labeled(args.labeled)
    else:
        data_rows = read_raw_jsonl(args.raw)

    enriched = []
    for r in data_rows:
        f = features(r.get('body',''))
        r.update(f)
        enriched.append(r)

    summary = aggregate(enriched)
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump({"summary":summary,"count":len(enriched)}, f, indent=2)
    print(f"Wrote summary ({len(enriched)} rows) -> {args.out}")

    if args.emit_csv:
        import csv as _csv
        # Collect union of keys across rows to avoid missing fieldnames
        key_union = []
        seen = set()
        for r in enriched:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    key_union.append(k)
        with open(args.emit_csv,'w',newline='',encoding='utf-8') as fcsv:
            w = _csv.DictWriter(fcsv, fieldnames=key_union)
            w.writeheader()
            for r in enriched:
                w.writerow(r)
        print(f"Per-row features CSV -> {args.emit_csv}")

if __name__ == '__main__':
    main()
