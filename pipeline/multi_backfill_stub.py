#!/usr/bin/env python3
"""Multi-transition historical backfill normalizer.

Extends `historical_backfill_stub.py` to support a YAML configuration of multiple
transition events (see transitions.yaml). For each transition, assumes externally
exported JSONL archives for its pre and post windows (naming convention or explicit map).

Usage (explicit mapping):
  python pipeline/multi_backfill_stub.py --transitions pipeline/transitions.yaml \
     --archive-map pipeline/data/archive_map.json --out pipeline/data/multi_transitions.jsonl

Archive map JSON structure:
{
  "gpt4_to_4o": {"pre": "path/to/gpt4_to_4o_pre.jsonl", "post": "path/to/gpt4_to_4o_post.jsonl"},
  "gpt4o_iterative_mar2025": {"pre": "...", "post": "..."},
  ...
}

Outputs a unified JSONL with fields:
  comment_id, parent_id, thread_id, created_utc, score, score_bucket,
  author_hash, body, subreddit, transition, pre_post

Skips rows outside defined windows for each transition.
"""
from __future__ import annotations
import argparse, json, yaml, hashlib, time
from datetime import datetime, timedelta
from typing import Dict, Any, List

SUBSET_FIELDS = ["id","parent_id","link_id","created_utc","score","body","subreddit","author"]


def hash_user(u: str) -> str:
    return hashlib.sha256(u.encode('utf-8')).hexdigest()[:16]


def load_jsonl(path: str) -> List[Dict[str,Any]]:
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except:  # noqa
                continue
    return rows


def load_transitions(path: str):
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)


def within(dt_obj: datetime, release: datetime, pre_days: int, post_days: int):
    pre_start = release - timedelta(days=pre_days)
    post_end = release + timedelta(days=post_days)
    if pre_start <= dt_obj < release:
        return 'pre'
    if release <= dt_obj <= post_end:
        return 'post'
    return None


def normalize_row(r: Dict[str,Any], phase: str, transition_id: str) -> Dict[str,Any]:
    created = int(r.get('created_utc', time.time()))
    score = r.get('score',0) or 0
    if score >= 50:
        bucket='hi'
    elif score >= 10:
        bucket='mid'
    else:
        bucket='lo'
    body = r.get('body') or r.get('selftext') or ''
    link_id = r.get('link_id') or r.get('submission_id') or f"t3_{r.get('id','')}"
    return {
        'comment_id': r.get('id'),
        'parent_id': r.get('parent_id') or None,
        'thread_id': link_id,
        'created_utc': created,
        'score': score,
        'score_bucket': bucket,
        'author_hash': hash_user(str(r.get('author','anon'))),
        'body': body,
        'subreddit': r.get('subreddit','unknown'),
        'transition': transition_id,
        'pre_post': phase
    }


def process_transition(tcfg: Dict[str,Any], archive_map: Dict[str,Dict[str,str]]):
    tid = tcfg['id']
    rel = datetime.strptime(str(tcfg['release_date']), '%Y-%m-%d')
    pre_days = int(tcfg.get('pre_days',14))
    post_days = int(tcfg.get('post_days',14))
    mapping = archive_map.get(tid) or {}
    pre_path = mapping.get('pre')
    post_path = mapping.get('post')
    if not (pre_path and post_path):
        print(f"[warn] Missing archives for transition {tid}; skipping")
        return []
    out=[]
    for phase, path in [('pre', pre_path), ('post', post_path)]:
        rows = load_jsonl(path)
        for r in rows:
            ts = int(r.get('created_utc',0))
            dt_obj = datetime.utcfromtimestamp(ts)
            label = within(dt_obj, rel, pre_days, post_days)
            if label == phase:  # ensure row truly within declared window side
                out.append(normalize_row(r, phase, tid))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--archive-map', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    transitions = load_transitions(args.transitions)
    with open(args.archive_map,'r',encoding='utf-8') as f:
        archive_map = json.load(f)

    combined=[]
    for tcfg in transitions:
        combined.extend(process_transition(tcfg, archive_map))
    with open(args.out,'w',encoding='utf-8') as f:
        for r in combined:
            f.write(json.dumps(r)+'\n')
    print(f"Multi-transition backfill rows: {len(combined)} -> {args.out}")

if __name__=='__main__':
    main()
