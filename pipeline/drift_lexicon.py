#!/usr/bin/env python3
"""Compute provisional lexical drift between two corpora (pre vs post).
Applies log-odds with an informative Dirichlet prior (Monroe et al. 2008 style) with symmetric prior.
Outputs JSON listing top tokens favoring each side.

Usage:
  python pipeline/drift_lexicon.py --pre pipeline/data/live_raw_window.jsonl \
    --post pipeline/data/live_raw_kw.jsonl \
    --out-json pipeline/data/drift_log_odds.json --top 30

NOTE: Current data may not be temporally authentic; interpret cautiously.
"""
from __future__ import annotations
import json, argparse, math, re, os
from collections import Counter
from typing import Dict, List, Tuple

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
                rows.append(json.loads(line))
    return rows

def tokens(rows: List[Dict]) -> List[str]:
    out=[]
    for r in rows:
        body=(r.get('body') or '').lower()
        for w in WORD_RE.findall(body):
            if w in STOP:
                continue
            if len(w) < 3:
                continue
            out.append(w)
    return out

def log_odds(f_pre: Counter, f_post: Counter, alpha: float = 0.01) -> List[Tuple[str,float,float]]:
    # Combine vocabulary
    vocab = set(f_pre) | set(f_post)
    n_pre = sum(f_pre.values())
    n_post = sum(f_post.values())
    alpha_0 = alpha * len(vocab)
    results=[]
    for w in vocab:
        a = f_pre.get(w,0) + alpha
        b = f_post.get(w,0) + alpha
        denom_pre = n_pre + alpha_0 - (f_pre.get(w,0) + alpha)
        denom_post = n_post + alpha_0 - (f_post.get(w,0) + alpha)
        # log odds difference
        logit_pre = math.log(a/denom_pre)
        logit_post = math.log(b/denom_post)
        delta = logit_pre - logit_post
        # variance approximation
        var = 1/(a) + 1/(b)
        z = delta / math.sqrt(var) if var>0 else 0.0
        results.append((w, delta, z))
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pre', required=True)
    ap.add_argument('--post', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--restrict-lexicon', help='Optional file with one token per line to restrict vocabulary (case-insensitive)')
    args = ap.parse_args()

    pre_rows = load_jsonl(args.pre)
    post_rows = load_jsonl(args.post)
    pre_toks = tokens(pre_rows)
    post_toks = tokens(post_rows)
    if args.restrict_lexicon and os.path.isfile(args.restrict_lexicon):
        lex = set()
        with open(args.restrict_lexicon,'r',encoding='utf-8') as lf:
            for line in lf:
                line=line.strip().lower()
                if line and not line.startswith('#'):
                    lex.add(line)
        pre_toks = [t for t in pre_toks if t in lex]
        post_toks = [t for t in post_toks if t in lex]
    f_pre = Counter(pre_toks)
    f_post = Counter(post_toks)
    res = log_odds(f_pre, f_post)
    # Sort by z-score
    pre_favor = sorted(res, key=lambda x: x[2], reverse=True)[:args.top]
    post_favor = sorted(res, key=lambda x: x[2])[:args.top]

    out = {
        'pre_total_tokens': sum(f_pre.values()),
        'post_total_tokens': sum(f_post.values()),
        'top_pre_tokens': [{'token':w,'delta':d,'z':z,'pre_freq':f_pre[w],'post_freq':f_post.get(w,0)} for w,d,z in pre_favor],
        'top_post_tokens': [{'token':w,'delta':d,'z':z,'pre_freq':f_pre[w],'post_freq':f_post.get(w,0)} for w,d,z in post_favor]
    }
    with open(args.out_json,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Drift output -> {args.out_json}")

if __name__ == '__main__':
    main()
