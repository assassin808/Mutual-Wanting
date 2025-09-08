#!/usr/bin/env python3
"""Exact + near-duplicate filtering orchestrator.

Steps:
 1. Exact duplicate removal (hash of normalized body).
 2. (Optional) Near-duplicate detection via MinHash (text_minhash.py logic imported) to flag pairs.

Outputs:
 - deduped.jsonl (exact duplicates removed; keeps first occurrence)
 - duplicates_report.json (counts + list of removed ids + near-dup pairs if requested)

Usage:
  python pipeline/dedupe_text.py --in raw.jsonl --out deduped.jsonl --report duplicates_report.json --near --near-threshold 0.9
"""
from __future__ import annotations
import argparse, json, hashlib, re
from typing import Dict, List

NORMALIZE_RE = re.compile(r"\s+")

def norm_text(t: str) -> str:
    return NORMALIZE_RE.sub(' ', (t or '').strip().lower())

def text_hash(t: str) -> str:
    return hashlib.sha256(t.encode('utf-8')).hexdigest()

def load_jsonl(path: str):
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def save_jsonl(path: str, rows: List[dict]):
    with open(path,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

def minhash_pairs(rows: List[dict], jaccard_min: float):
    try:
        from text_minhash import shingles, hash_shingle, make_hash_funcs, signature, approx_jaccard
    except ImportError:
        return []
    k_hash = 60
    bands = 20
    rows_per_band = k_hash // bands
    hash_funcs = make_hash_funcs(k_hash)
    sigs = {}
    shingle_map = {}
    for r in rows:
        rid = str(r.get('id'))
        sh = [hash_shingle(s) for s in shingles(r.get('body',''), 3)]
        shingle_map[rid] = sh
        sigs[rid] = signature(sh, hash_funcs)
    # LSH buckets
    buckets = {}
    for rid, sig in sigs.items():
        for b in range(bands):
            chunk = tuple(sig[b*rows_per_band:(b+1)*rows_per_band])
            key = (b, hash(chunk))
            buckets.setdefault(key, []).append(rid)
    pairs = set()
    for ids in buckets.values():
        if len(ids) > 1:
            ids = sorted(ids)
            for i in range(len(ids)):
                for j in range(i+1, len(ids)):
                    a,b = ids[i], ids[j]
                    if (a,b) in pairs: continue
                    jac = approx_jaccard(shingle_map[a], shingle_map[b])
                    if jac >= jaccard_min:
                        pairs.add((a,b,jac))
    return [{'id_a': a, 'id_b': b, 'approx_jaccard': j} for a,b,j in pairs]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--near', action='store_true', help='Also compute near-duplicate pairs (slower)')
    ap.add_argument('--near-threshold', type=float, default=0.9)
    args = ap.parse_args()

    seen_hash = {}
    kept = []
    removed = []
    for row in load_jsonl(args.inp):
        body_norm = norm_text(row.get('body',''))
        h = text_hash(body_norm)
        if h in seen_hash:
            removed.append({'id': row.get('id'), 'duplicate_of': seen_hash[h]})
            continue
        seen_hash[h] = row.get('id')
        kept.append(row)

    near_pairs = []
    if args.near:
        near_pairs = minhash_pairs(kept, args.near_threshold)

    save_jsonl(args.out, kept)
    report = {
        'input_path': args.inp,
        'output_path': args.out,
        'n_input': len(kept)+len(removed),
        'n_kept': len(kept),
        'n_exact_dups': len(removed),
        'exact_duplicates': removed[:100],  # cap for brevity
        'near_pairs': near_pairs,
        'n_near_pairs': len(near_pairs)
    }
    with open(args.report,'w',encoding='utf-8') as f:
        json.dump(report,f,indent=2)
    print(f"Dedupe -> {args.out} kept={len(kept)} exact_dups={len(removed)} near_pairs={len(near_pairs)}")

if __name__ == '__main__':
    main()
