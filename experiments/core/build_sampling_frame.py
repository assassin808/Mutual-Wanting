#!/usr/bin/env python3
"""Construct sampling_frame.csv with stratification labels for scaled annotation.

Inputs: normalized pre/post JSONL for a transition (already hashed author).
Adds:
  - length_bucket (short/medium/long) by token count thresholds (<=40, 41-120, >120)
  - question_flag (1 if '?' present)
  - subreddit (as-is)
  - basic sentiment placeholder (neg/neu/pos) using naive heuristic (# of '!' and presence of negative cue words)
  - cluster_id (placeholder -1 to be replaced by later topic clustering step)

Outputs:
  sampling_frame.csv in pipeline/outputs/annotation/
"""
from __future__ import annotations
import argparse, json, os, csv, re

WORD_RE = re.compile(r"\b\w+\b")
NEG_WORDS = {w.strip() for w in ["bad","hate","worse","worst","angry","annoyed","broken","fail","failing","bug","error"] if w}


def load_jsonl(path):
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                yield json.loads(line)
            except:  # noqa
                continue


def length_bucket(n_tok: int) -> str:
    if n_tok <= 40: return 'short'
    if n_tok <= 120: return 'medium'
    return 'long'


def sentiment_heuristic(text: str) -> str:
    t = text.lower()
    toks = set(WORD_RE.findall(t))
    neg_hits = len(toks & NEG_WORDS)
    exclam = t.count('!')
    if neg_hits >= 2 or (neg_hits>=1 and exclam>=1):
        return 'neg'
    if exclam >= 3:
        return 'pos'
    return 'neu'


def build(pre_path: str, post_path: str, out_csv: str):
    rows=[]
    for src, phase in [(pre_path,'pre'),(post_path,'post')]:
        for r in load_jsonl(src):
            body = r.get('body') or ''
            toks = WORD_RE.findall(body)
            lb = length_bucket(len(toks))
            qflag = 1 if '?' in body else 0
            sent = sentiment_heuristic(body)
            rows.append({
                'id': r.get('id'),
                'transition': r.get('transition'),
                'pre_post': phase,
                'subreddit': r.get('subreddit'),
                'score_bucket': r.get('score_bucket'),
                'length_bucket': lb,
                'question_flag': qflag,
                'sentiment': sent,
                'cluster_id': -1,
                'token_len': len(toks)
            })
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        header=['id','transition','pre_post','subreddit','score_bucket','length_bucket','question_flag','sentiment','cluster_id','token_len']
        w.writerow(header)
        for r in rows:
            w.writerow([r[h] for h in header])
    print(f"Sampling frame rows={len(rows)} -> {out_csv}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--transition-id', required=True)
    ap.add_argument('--data-dir', default='pipeline/data')
    ap.add_argument('--out-dir', default='pipeline/outputs/annotation')
    args=ap.parse_args()
    pre=os.path.join(args.data_dir,f"{args.transition_id}_pre.jsonl")
    post=os.path.join(args.data_dir,f"{args.transition_id}_post.jsonl")
    if not (os.path.exists(pre) and os.path.exists(post)):
        raise SystemExit('Normalized pre/post not found')
    out_csv=os.path.join(args.out_dir,f"{args.transition_id}_sampling_frame.csv")
    build(pre, post, out_csv)

if __name__=='__main__':
    main()
