#!/usr/bin/env python3
"""Lightweight MinHash + LSH utilities for near-duplicate detection.

Designed for medium corpora (<= ~200k rows). Avoids external dependencies.
Uses a simple bag-of-shingles approach (word 3-grams) hashed through K hash
functions (random a,b mod large prime) to produce signature matrix used for
banded LSH candidate generation.

Outputs candidate duplicate id pairs with approximate Jaccard above a threshold.

NOTE: For very large corpora prefer datasketch or locality sensitive libraries.
"""
from __future__ import annotations
import argparse, json, random, re, math, itertools, hashlib
from typing import List, Dict, Tuple, Iterable

WORD_RE = re.compile(r"[A-Za-z']+")
LARGE_PRIME = 4294967311

def shingles(text: str, k: int = 3) -> List[str]:
    tokens = WORD_RE.findall(text.lower())
    return [' '.join(tokens[i:i+k]) for i in range(len(tokens)-k+1)] if len(tokens) >= k else tokens

def hash_shingle(s: str) -> int:
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(),16) & 0xffffffff

def make_hash_funcs(k: int, seed: int = 42):
    random.seed(seed)
    funcs = []
    for _ in range(k):
        a = random.randint(1, LARGE_PRIME-1)
        b = random.randint(0, LARGE_PRIME-1)
        funcs.append((a,b))
    return funcs

def signature(shingle_hashes: List[int], hash_funcs) -> List[int]:
    sig = []
    for a,b in hash_funcs:
        if not shingle_hashes:
            # Represent empty doc with a maximal sentinel value for all hash functions
            sig.append(2**32-1)
            continue
        m = None
        for h in shingle_hashes:
            val = (a * h + b) % LARGE_PRIME
            if (m is None) or (val < m):
                m = val
        # m must be an int now
        sig.append(int(m))
    return sig

def lsh_candidates(signatures: Dict[str,List[int]], bands: int, rows_per_band: int):
    buckets = {}
    for doc_id, sig in signatures.items():
        for b in range(bands):
            start = b*rows_per_band
            chunk = tuple(sig[start:start+rows_per_band])
            key = (b, hash(chunk))
            buckets.setdefault(key, []).append(doc_id)
    for docs in buckets.values():
        if len(docs) > 1:
            for a,b in itertools.combinations(docs,2):
                yield a,b

def approx_jaccard(sh_a: List[int], sh_b: List[int]) -> float:
    if not sh_a and not sh_b:
        return 1.0
    inter = len(set(sh_a) & set(sh_b))
    union = len(set(sh_a) | set(sh_b)) or 1
    return inter/union

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jsonl', required=True, help='Input JSONL with id, body')
    ap.add_argument('--out', required=True, help='Output JSON (pairs)')
    ap.add_argument('--k-hash', type=int, default=60)
    ap.add_argument('--bands', type=int, default=20)
    ap.add_argument('--shingle-size', type=int, default=3)
    ap.add_argument('--jaccard-min', type=float, default=0.85)
    ap.add_argument('--max-candidates', type=int, default=50000)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    rows = []
    with open(args.jsonl,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    hash_funcs = make_hash_funcs(args.k_hash, args.seed)
    sigs = {}
    shingle_map = {}
    for r in rows:
        rid = str(r.get('id'))
        text = r.get('body','')
        sh = [hash_shingle(s) for s in shingles(text, args.shingle_size)]
        shingle_map[rid] = sh
        sigs[rid] = signature(sh, hash_funcs)

    rows_per_band = args.k_hash // args.bands
    cand_pairs = set()
    for a,b in lsh_candidates(sigs, args.bands, rows_per_band):
        cand_pairs.add(tuple(sorted((a,b))))
        if len(cand_pairs) >= args.max_candidates:
            break

    results = []
    for a,b in cand_pairs:
        jac = approx_jaccard(shingle_map[a], shingle_map[b])
        if jac >= args.jaccard_min:
            results.append({'id_a': a, 'id_b': b, 'approx_jaccard': jac})

    with open(args.out,'w',encoding='utf-8') as f:
        json.dump({'pairs': results, 'n_pairs': len(results)}, f, indent=2)
    print(f"MinHash near-duplicates -> {args.out} (pairs={len(results)})")

if __name__ == '__main__':
    main()
