#!/usr/bin/env python3
"""Historical backfill scaffold for authentic GPT-4 -> GPT-4o transition.

This script does NOT fetch historical Reddit data itself (Pushshift-like APIs are
outside current scope and may require separate tooling). Instead it:
 1. Defines canonical release date and pre/post window boundaries.
 2. Validates presence of provided pre/post JSONL archives (previously exported
    via external tool) containing Reddit submissions/comments with 'created_utc'.
 3. Normalizes rows into the existing schema and tags transition + phase.
 4. Emits combined JSONL ready for downstream sampling / labeling.

Expected external step (documented): Use a Pushshift-compatible export tool to
retrieve Reddit comments/posts for target subreddits with:
   after=2024-04-29 00:00:00 UTC (14 days before) and before=2024-05-27 23:59:59 UTC (14 days after)
   (If you prefer a longer post window, extend POST_DAYS accordingly.)

Usage:
  python pipeline/historical_backfill_stub.py \
    --pre-archive path/to/pre_window.jsonl \
    --post-archive path/to/post_window.jsonl \
    --out pipeline/data/historical_gpt4_to_4o.jsonl

Archive format assumption: Each line is a JSON object with at minimum:
  id, created_utc (epoch seconds), score, body (or selftext), subreddit, author.
If 'body' missing but 'selftext' present, it is copied.
"""
from __future__ import annotations
import json, argparse, os, time, hashlib
from datetime import datetime, timedelta
from typing import Iterable, Dict, Any, List

RELEASE = datetime(2024, 5, 13)  # GPT-4o public release date
PRE_DAYS = 14
POST_DAYS = 28  # could shorten to 14 for parity
TRANSITION_KEY = "gpt4_to_4o"

SUBSET_FIELDS = ["id","parent_id","link_id","created_utc","score","body","subreddit","author"]


def hash_user(user: str) -> str:
    return hashlib.sha256(user.encode('utf-8')).hexdigest()[:16]


def load_jsonl(path: str) -> List[Dict[str,Any]]:
    rows = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def tag_phase(ts: int):
    dt = datetime.utcfromtimestamp(ts)
    if RELEASE - timedelta(days=PRE_DAYS) <= dt < RELEASE:
        return 'pre'
    if RELEASE <= dt <= RELEASE + timedelta(days=POST_DAYS):
        return 'post'
    return None


def normalize(row: Dict[str,Any]) -> Dict[str,Any]:
    created = int(row.get('created_utc', time.time()))
    phase = tag_phase(created)
    if phase is None:
        return {}
    score = row.get('score', 0) or 0
    if score >= 50:
        bucket = 'hi'
    elif score >= 10:
        bucket = 'mid'
    else:
        bucket = 'lo'
    body = row.get('body') or row.get('selftext') or ''
    parent_id = row.get('parent_id') or None
    link_id = row.get('link_id') or row.get('submission_id') or f"t3_{row.get('id','')}"
    return {
        'comment_id': row.get('id'),
        'parent_id': parent_id,
        'thread_id': link_id,
        'created_utc': created,
        'score': score,
        'score_bucket': bucket,
        'author_hash': hash_user(str(row.get('author','anon'))),
        'body': body,
        'subreddit': row.get('subreddit','unknown'),
        'transition': TRANSITION_KEY,
        'pre_post': phase
    }


def process(archives: List[str]) -> List[Dict[str,Any]]:
    out = []
    for path in archives:
        if not os.path.isfile(path):
            print(f"[warn] archive not found: {path}")
            continue
        for r in load_jsonl(path):
            n = normalize(r)
            if n:
                out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pre-archive', required=True, help='JSONL exported for pre window')
    ap.add_argument('--post-archive', required=True, help='JSONL exported for post window')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    rows = process([args.pre_archive, args.post_archive])
    if not rows:
        print("No rows retained; ensure archives contain expected fields and fall inside window.")
    with open(args.out,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(f"Historical backfill combined rows: {len(rows)} -> {args.out}")

if __name__ == '__main__':
    main()
