#!/usr/bin/env python3
"""Drift trend helper across multiple transitions.

Aggregates per-transition stable drift tokens (requires each transition pre/post JSONL) and
computes token-level sign consistency across events plus per-transition z-scores.

Usage:
  python pipeline/drift_trend.py --transitions pipeline/transitions.yaml --archive-map pipeline/data/archive_map.json \
      --freq-floor 10 --boots 100 --out pipeline/outputs/drift_trend.json
"""
from __future__ import annotations
import argparse, json, math, yaml, re, random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

WORD_RE = re.compile(r"[A-Za-z']+")
STOP = { 'the','a','an','and','or','of','to','in','it','is','for','on','you','i','that','this','with','be','are','as','was','but','if','so','we','they','at','have','has','had','from','by','about' }

def load_jsonl(path: str) -> List[Dict[str,Any]]:
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

def load_transitions(path: str):
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def tokens(rows: List[Dict[str,Any]]) -> List[str]:
    out=[]
    for r in rows:
        body=(r.get('body') or '').lower()
        for w in WORD_RE.findall(body):
            if w in STOP or len(w)<3:
                continue
            out.append(w)
    return out

def log_odds(f_pre: Counter, f_post: Counter, alpha: float=0.01) -> Dict[str,Tuple[float,float]]:
    vocab=set(f_pre)|set(f_post)
    n_pre=sum(f_pre.values())
    n_post=sum(f_post.values())
    alpha_0=alpha*len(vocab)
    out={}
    for w in vocab:
        a=f_pre.get(w,0)+alpha
        b=f_post.get(w,0)+alpha
        denom_pre=n_pre+alpha_0-(f_pre.get(w,0)+alpha)
        denom_post=n_post+alpha_0-(f_post.get(w,0)+alpha)
        logit_pre=math.log(a/denom_pre)
        logit_post=math.log(b/denom_post)
        delta=logit_pre-logit_post
        var=1/a + 1/b
        z=delta/math.sqrt(var) if var>0 else 0.0
        out[w]=(delta,z)
    return out

def per_transition_stats(pre_rows, post_rows, freq_floor):
    pre_toks=tokens(pre_rows)
    post_toks=tokens(post_rows)
    f_pre=Counter(pre_toks)
    f_post=Counter(post_toks)
    vocab=[w for w in f_pre if f_pre[w]>=freq_floor and f_post.get(w,0)>=freq_floor]
    res=log_odds(Counter({w:f_pre[w] for w in vocab}), Counter({w:f_post[w] for w in vocab}))
    return {w:res[w] for w in vocab}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--archive-map', required=True)
    ap.add_argument('--freq-floor', type=int, default=10)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()

    with open(args.archive_map,'r',encoding='utf-8') as f:
        amap=json.load(f)
    transitions=load_transitions(args.transitions)

    trend=defaultdict(dict)  # token -> transition -> z
    for tcfg in transitions:
        tid=tcfg['id']
        mapping=amap.get(tid)
        if not mapping:
            continue
        pre=load_jsonl(mapping.get('pre',''))
        post=load_jsonl(mapping.get('post',''))
        stats=per_transition_stats(pre,post,args.freq_floor)
        for w, (_, z) in stats.items():
            trend[w][tid]=z
    # compute consistency across transitions for each token
    out_tokens={}
    for w, trans_map in trend.items():
        zs=list(trans_map.values())
        if not zs:
            continue
        mean=sum(zs)/len(zs)
        sign=1 if mean>=0 else -1
        sign_consistency=sum(1 for z in zs if (z>=0)==(sign>0))/len(zs)
        out_tokens[w]={
            'mean_z': mean,
            'sign_consistency': sign_consistency,
            'per_transition': trans_map
        }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump({'freq_floor': args.freq_floor, 'tokens': out_tokens}, f, indent=2)
    print(f"Drift trend -> {args.out} (tokens={len(out_tokens)})")

if __name__=='__main__':
    main()
