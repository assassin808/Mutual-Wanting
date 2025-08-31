#!/usr/bin/env python3
"""Bootstrap stability analysis for lexical drift tokens.

Given the same pre/post JSONL inputs used by `drift_lexicon.py`, this script:
1. Samples with replacement B bootstrap replicates from each side (token-level resampling of documents).
2. Re-computes log-odds z-scores per replicate.
3. Aggregates per-token: sign consistency rate, mean z, std z.
4. Emits JSON with stability metrics; tokens below stability threshold can be filtered out before reporting.

Usage:
  python pipeline/drift_bootstrap.py --pre pre.jsonl --post post.jsonl --restrict-lexicon complaint_focus_lexicon.txt \
    --freq-floor 10 --boots 200 --out pipeline/data/drift_bootstrap.json

Note: For efficiency we operate on token lists rather than re-parsing raw bodies each replicate.
"""
from __future__ import annotations
import json, argparse, math, re, random
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

WORD_RE = re.compile(r"[A-Za-z']+")
STOP = {
    'the','a','an','and','or','of','to','in','it','is','for','on','you','i','that','this','with','be','are','as','was','but','if','so','we','they','at','have','has','had','from','by','about'
}

def load_jsonl(path: str) -> List[Dict]:
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except:  # noqa
                    continue
    return rows


def doc_tokens(rows: List[Dict], restrict: set|None) -> List[List[str]]:
    docs=[]
    for r in rows:
        body=(r.get('body') or '').lower()
        toks=[]
        for w in WORD_RE.findall(body):
            if w in STOP or len(w) < 3:
                continue
            if restrict and w not in restrict:
                continue
            toks.append(w)
        if toks:
            docs.append(toks)
    return docs


def log_odds(f_pre: Counter, f_post: Counter, alpha: float = 0.01) -> Dict[str,Tuple[float,float]]:
    vocab = set(f_pre) | set(f_post)
    n_pre = sum(f_pre.values())
    n_post = sum(f_post.values())
    alpha_0 = alpha * len(vocab)
    out={}
    for w in vocab:
        a = f_pre.get(w,0) + alpha
        b = f_post.get(w,0) + alpha
        denom_pre = n_pre + alpha_0 - (f_pre.get(w,0) + alpha)
        denom_post = n_post + alpha_0 - (f_post.get(w,0) + alpha)
        logit_pre = math.log(a/denom_pre)
        logit_post = math.log(b/denom_post)
        delta = logit_pre - logit_post
        var = 1/(a) + 1/(b)
        z = delta / math.sqrt(var) if var>0 else 0.0
        out[w] = (delta, z)
    return out


def bootstrap(pre_docs: List[List[str]], post_docs: List[List[str]], freq_floor: int, boots: int) -> Dict[str,Dict]:
    # Build baseline frequency to filter vocabulary by symmetric floor
    base_pre = Counter(t for doc in pre_docs for t in doc)
    base_post = Counter(t for doc in post_docs for t in doc)
    vocab = [w for w in base_pre if base_pre[w] >= freq_floor and base_post.get(w,0) >= freq_floor]
    stats = {w:{'z':[], 'sign_consistency':0} for w in vocab}
    for b in range(boots):
        # Resample documents with replacement
        sample_pre = random.choices(pre_docs, k=len(pre_docs))
        sample_post = random.choices(post_docs, k=len(post_docs))
        f_pre = Counter(t for doc in sample_pre for t in doc)
        f_post = Counter(t for doc in sample_post for t in doc)
        res = log_odds(f_pre, f_post)
        for w in vocab:
            z = res.get(w,(0.0,0.0))[1]
            stats[w]['z'].append(z)
    # Compute stability metrics
    for w, d in stats.items():
        zs = d['z']
        mean_z = sum(zs)/len(zs)
        sign = 1 if mean_z>=0 else -1
        consistent = sum(1 for z in zs if (z>=0) == (sign>0)) / len(zs)
        d['mean_z'] = mean_z
        d['std_z'] = (sum((z-mean_z)**2 for z in zs)/len(zs))**0.5
        d['sign_consistency'] = consistent
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pre', required=True)
    ap.add_argument('--post', required=True)
    ap.add_argument('--restrict-lexicon')
    ap.add_argument('--freq-floor', type=int, default=10)
    ap.add_argument('--boots', type=int, default=200)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    restrict=set()
    if args.restrict_lexicon:
        try:
            with open(args.restrict_lexicon,'r',encoding='utf-8') as f:
                for line in f:
                    line=line.strip().lower()
                    if line and not line.startswith('#'):
                        restrict.add(line)
        except FileNotFoundError:
            restrict=None
    else:
        restrict=None

    pre_rows = load_jsonl(args.pre)
    post_rows = load_jsonl(args.post)
    pre_docs = doc_tokens(pre_rows, restrict)
    post_docs = doc_tokens(post_rows, restrict)

    stats = bootstrap(pre_docs, post_docs, args.freq_floor, args.boots)
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump({
            'freq_floor': args.freq_floor,
            'boots': args.boots,
            'tokens': {w:{'mean_z':d['mean_z'],'std_z':d['std_z'],'sign_consistency':d['sign_consistency']} for w,d in stats.items()}
        }, f, indent=2)
    print(f"Bootstrap drift stability -> {args.out} (tokens={len(stats)})")

if __name__ == '__main__':
    main()
