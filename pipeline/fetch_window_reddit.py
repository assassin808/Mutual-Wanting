#!/usr/bin/env python3
"""Fetch Reddit comments for specific subreddits within a UTC time window.

Priority source: Official Reddit API via PRAW (requires env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT).
Fallback (if PRAW creds missing): Attempt lightweight Pushshift query paging (best-effort; Pushshift stability varies).

Writes a JSONL with normalized fields compatible with backfill scripts.

Usage:
  python pipeline/fetch_window_reddit.py \
      --subreddits pipeline/subreddits.txt \
      --start '2024-04-29T00:00:00Z' \
      --end '2024-05-27T23:59:59Z' \
      --out pipeline/data/gpt4_to_4o_prepost_raw.jsonl \
      --max-per-subreddit 500

Note: For large windows consider splitting (e.g., daily) to respect API limits. This script is intentionally minimal.
"""
from __future__ import annotations
import argparse, os, sys, time, json, datetime as dt
try:
    from . import env_loader  # type: ignore
except Exception:
    import env_loader
env_loader.load_env_once()
from typing import List, Dict
import hashlib
import math

try:
    import praw  # type: ignore
except ImportError:  # pragma: no cover
    praw = None
import requests

NORMAL_FIELDS = ["id","parent_id","link_id","created_utc","score","body","subreddit","author"]


def parse_iso(ts: str) -> int:
    return int(dt.datetime.strptime(ts.replace('Z',''), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())


def hash_user(u: str) -> str:
    return hashlib.sha256(u.encode('utf-8')).hexdigest()[:16]


def load_subreddits(path: str) -> List[str]:
    subs=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line and not line.startswith('#'):
                subs.append(line)
    return subs

# -------- Reddit API (PRAW) --------

def fetch_praw(sub: str, start: int, end: int, limit: int) -> List[Dict]:
    """Fetch via official API using submissions time filter then flatten comments.

    We iterate submissions in the window and expand comment trees (shallow) until limit reached.
    This is approximate (may over-represent high-comment submissions) but ensures data presence
    when Pushshift is unavailable. Duplicate comment IDs are deduped.
    """
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT','MutualWantingStudy/0.1')
    if not (client_id and client_secret) or praw is None:
        return []
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent, check_for_async=False)
    subreddit = reddit.subreddit(sub)
    out: Dict[str,Dict] = {}
    try:
        for submission in subreddit.submissions(start, end):  # type: ignore[attr-defined]
            submission.comment_sort = 'top'
            submission.comments.replace_more(limit=0)
            for c in submission.comments.list():
                if len(out) >= limit:
                    break
                created = int(getattr(c,'created_utc',0))
                if created < start or created > end:
                    continue
                body = getattr(c,'body','') or ''
                cid = getattr(c,'id',None)
                if not cid or cid in out:
                    continue
                score = getattr(c,'score',0) or 0
                out[cid] = {
                    'id': cid,
                    'parent_id': getattr(c,'parent_id',None),
                    'link_id': getattr(c,'link_id', f"t3_{submission.id}"),
                    'created_utc': created,
                    'score': score,
                    'body': body,
                    'subreddit': sub,
                    'author': str(getattr(c,'author','anon'))
                }
            if len(out) >= limit:
                break
    except Exception:
        return list(out.values())
    return list(out.values())

# -------- Pushshift Fallback --------

def fetch_pushshift(sub: str, start: int, end: int, limit: int) -> List[Dict]:
    url = 'https://api.pushshift.io/reddit/comment/search/'
    size = 200
    results=[]
    after = start
    attempts=0
    while after < end and len(results) < limit:
        params = {
            'subreddit': sub,
            'after': after,
            'before': end,
            'size': size,
            'sort': 'asc',
            'sort_type': 'created_utc'
        }
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code != 200:
                break
            data = r.json().get('data',[])
            if not data:
                break
            for d in data:
                results.append(d)
            after = data[-1]['created_utc'] + 1
            if len(data) < size:
                break
            time.sleep(1)
        except Exception:
            attempts+=1
            if attempts>3:
                break
            time.sleep(2)
    return results[:limit]


def normalize(rows: List[Dict]) -> List[Dict]:
    out=[]
    for r in rows:
        created = int(r.get('created_utc',0))
        score = r.get('score',0) or 0
        if score >= 50:
            bucket='hi'
        elif score >= 10:
            bucket='mid'
        else:
            bucket='lo'
        body = r.get('body') or ''
        link_id = r.get('link_id') or r.get('submission_id') or f"t3_{r.get('id','')}"
        out.append({
            'comment_id': r.get('id'),
            'parent_id': r.get('parent_id') or None,
            'thread_id': link_id,
            'created_utc': created,
            'score': score,
            'score_bucket': bucket,
            'author_hash': hash_user(str(r.get('author','anon'))),
            'body': body,
            'subreddit': r.get('subreddit','unknown')
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subreddits', required=True)
    ap.add_argument('--start', required=True, help='ISO UTC e.g. 2024-04-29T00:00:00Z')
    ap.add_argument('--end', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--max-per-subreddit', type=int, default=1000)
    args = ap.parse_args()

    start_ts = parse_iso(args.start)
    end_ts = parse_iso(args.end)
    subs = load_subreddits(args.subreddits)

    all_rows=[]
    for s in subs:
        got: List[Dict] = []
        # Try pushshift first
        ps = fetch_pushshift(s, start_ts, end_ts, args.max_per_subreddit)
        got.extend(ps)
        if not got:  # fallback to PRAW if available
            praw_rows = fetch_praw(s, start_ts, end_ts, args.max_per_subreddit)
            got.extend(praw_rows)
        norm = normalize(got)
        all_rows.extend(norm)
        print(f"{s}: {len(norm)} rows (source={'pushshift' if ps else 'praw' if got else 'none'})")

    with open(args.out,'w',encoding='utf-8') as f:
        for r in all_rows:
            f.write(json.dumps(r)+'\n')
    print(f"Wrote {len(all_rows)} rows -> {args.out}")

if __name__=='__main__':
    main()
