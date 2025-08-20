#!/usr/bin/env python3
"""Minimal Reddit fetcher skeleton with transition window tagging.

Fill in real API calls where indicated. Keeps output lean for labeling pipeline.
"""
from __future__ import annotations
import os, json, time, argparse, sys, hashlib
from datetime import datetime, timedelta
from typing import Iterable, Dict, Any, List, Tuple

# Transition release dates (UTC, placeholder adjust as needed)
RELEASES = {
    "gpt3_5_to_4": datetime(2023, 3, 14),
    "gpt4_to_4o": datetime(2024, 5, 13),
    "gpt4o_to_5": datetime(2025, 8, 1),  # placeholder
}
PRE_DAYS = 14
POST_DAYS = 28

# Placeholder: implement actual retrieval via official Reddit API or pushshift mirror.

def hash_user(user: str) -> str:
    return hashlib.sha256(user.encode('utf-8')).hexdigest()[:16]


def window_for(ts: int) -> Tuple[str, str] | Tuple[None, None]:
    dt = datetime.utcfromtimestamp(ts)
    for trans, rel in RELEASES.items():
        if rel - timedelta(days=PRE_DAYS) <= dt < rel:
            return trans, "pre"
        if rel <= dt <= rel + timedelta(days=POST_DAYS):
            return trans, "post"
    return None, None


def emit(comment: Dict[str, Any]) -> Dict[str, Any]:
    trans, phase = window_for(comment.get("created_utc", int(time.time())))
    # score bucket coarse
    score = comment.get("score", 0) or 0
    if score >= 50:
        bucket = "hi"
    elif score >= 10:
        bucket = "mid"
    else:
        bucket = "lo"
    return {
        "comment_id": comment.get("id"),
        "parent_id": comment.get("parent_id"),
        "thread_id": comment.get("link_id"),
        "created_utc": comment.get("created_utc"),
        "score": score,
        "score_bucket": bucket,
        "author_hash": hash_user(comment.get("author","anon")),
        "body": comment.get("body"),
        "subreddit": comment.get("subreddit"),
        "transition": trans,
        "pre_post": phase
    }


def fake_stream(limit: int) -> Iterable[Dict[str, Any]]:
    now = int(time.time())
    # spread timestamps over recent window for demo
    for i in range(limit):
        yield {
            "id": f"c{i}",
            "parent_id": f"p{i//5}",
            "link_id": f"t{i//10}",
            "created_utc": now - (i * 3600),
            "score": i % 87,
            "author": f"user{i%7}",
            "body": "Example comment body about model feeling colder now.",
            "subreddit": "exampleSub"
        }


def write_jsonl(path: str, rows: Iterable[Dict[str, Any]]):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='Output JSONL file')
    ap.add_argument('--limit', type=int, default=50)
    args = ap.parse_args()

    rows = [emit(c) for c in fake_stream(args.limit)]
    write_jsonl(args.out, rows)
    print(f"Wrote {len(rows)} rows -> {args.out}")

if __name__ == '__main__':
    main()
