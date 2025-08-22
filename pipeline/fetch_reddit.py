#!/usr/bin/env python3
"""Minimal Reddit fetcher skeleton with transition window tagging and optional live fetch.

Usage:
  python fetch_reddit.py --out pipeline/data/raw.jsonl --limit 500
If environment variables REDDIT_CLIENT_ID/SECRET/USER_AGENT exist and PRAW installed, will fetch live posts/comments.
Else uses synthetic generator.
"""
from __future__ import annotations
import os, json, time, argparse, sys, hashlib, importlib, importlib.util, re
from datetime import datetime, timedelta
from typing import Iterable, Dict, Any, List, Tuple

# Attempt dynamic import
def _load_env_file(path: str = ".env"):
    if not os.path.isfile(path):
        return
    try:
        with open(path,'r',encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k,v = line.split('=',1)
                if k not in os.environ:  # do not override already exported vars
                    os.environ[k]=v
    except Exception as e:
        print(f"[warn] could not parse .env: {e}")

_load_env_file()

praw_spec = importlib.util.find_spec("praw")
if praw_spec:
    import praw  # type: ignore
else:
    praw = None  # fallback

# Transition release dates (UTC, placeholder adjust as needed)
RELEASES = {
    "gpt3_5_to_4": datetime(2023, 3, 14),
    "gpt4_to_4o": datetime(2024, 5, 13),
    "gpt4o_to_5": datetime(2025, 8, 15),  # adjust closer to present for tagging
}
PRE_DAYS = 14
POST_DAYS = 28

# Placeholder: implement actual retrieval via official Reddit API or pushshift mirror.

def hash_user(user: str) -> str:
    return hashlib.sha256(user.encode('utf-8')).hexdigest()[:16]


def load_subreddits(path: str = "pipeline/subreddits.txt") -> List[str]:
    if os.path.isfile(path):
        with open(path,'r',encoding='utf-8') as f:
            return [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return ["ChatGPT"]


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


def auth_client():
    cid = os.getenv("REDDIT_CLIENT_ID")
    secret = os.getenv("REDDIT_CLIENT_SECRET")
    ua = os.getenv("REDDIT_USER_AGENT")
    if not (cid and secret and ua and praw):
        return None
    # Optional script auth
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    if username and password:
        return praw.Reddit(client_id=cid, client_secret=secret, user_agent=ua, username=username, password=password)
    return praw.Reddit(client_id=cid, client_secret=secret, user_agent=ua)


def iter_submissions(r, subreddits: List[str], limit: int) -> Iterable[Any]:
    per_sub = max(1, limit // max(1,len(subreddits)))
    for s in subreddits:
        try:
            for submission in r.subreddit(s).new(limit=per_sub):
                yield submission
        except Exception as e:  # catch forbidden / rate / etc.
            print(f"[warn] skipping subreddit {s}: {e}")


def expand_comments(submission, max_comments: int = 50) -> Iterable[Any]:
    submission.comments.replace_more(limit=0)
    count = 0
    for c in submission.comments.list():
        if count >= max_comments:
            break
        yield c
        count += 1


def normalize_comment(c) -> Dict[str, Any]:
    sub = getattr(c, 'subreddit', 'unknown')
    if not isinstance(sub, str):
        try:
            sub = getattr(sub, 'display_name', str(sub))
        except Exception:
            sub = 'unknown'
    return {
        "id": getattr(c, 'id', None),
        "parent_id": getattr(c, 'parent_id', None),
        "link_id": getattr(c, 'link_id', f"t3_{getattr(c,'link_id', '')}"),
        "created_utc": int(getattr(c, 'created_utc', time.time())),
        "score": getattr(c, 'score', 0),
        "author": getattr(c.author, 'name', 'anon') if getattr(c, 'author', None) else 'anon',
        "body": getattr(c, 'body', ''),
        "subreddit": sub
    }


def live_stream(limit: int) -> Iterable[Dict[str, Any]]:
    r = auth_client()
    if r is None:
        return []
    subs = load_subreddits()
    collected = 0
    try:
        for submission in iter_submissions(r, subs, limit):
            yield normalize_comment(submission)  # treat submission body as comment analog
            collected += 1
            for c in expand_comments(submission):
                yield normalize_comment(c)
                collected += 1
                if collected >= limit:
                    return
    except Exception as e:
        print(f"[warn] live fetch aborted early due to error: {e}")
        return []


def fake_stream(limit: int) -> Iterable[Dict[str, Any]]:
    now = int(time.time())
    for i in range(limit):
        yield {
            "id": f"c{i}",
            "parent_id": f"p{i//5}",
            "link_id": f"t{i//10}",
            "created_utc": now - (i * 86400 // 60),  # spread across days
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
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=200)
    ap.add_argument('--live', action='store_true', help='Attempt live Reddit fetch')
    ap.add_argument('--keywords', nargs='*', help='If set, only retain comments containing any keyword (case-insensitive)')
    ap.add_argument('--keywords-file', help='Optional file with one keyword per line')
    ap.add_argument('--min-len', type=int, default=0, help='Minimum body character length after strip')
    ap.add_argument('--no-bots', action='store_true', help='Filter out likely bot/moderator comments (author contains bot/mod, or body matches common patterns)')
    ap.add_argument('--summary-out', help='Optional JSON summary stats path')
    ap.add_argument('--override-release', nargs='*', help='Override release dates: key=YYYY-MM-DD (e.g., gpt4o_to_5=2025-08-18)')
    args = ap.parse_args()

    # Apply overrides
    if args.override_release:
        for spec in args.override_release:
            if '=' in spec:
                k,v = spec.split('=',1)
                k=k.strip(); v=v.strip()
                try:
                    RELEASES[k] = datetime.strptime(v,'%Y-%m-%d')
                except ValueError:
                    print(f"[warn] invalid date for {k}: {v} (expected YYYY-MM-DD)")

    if args.live:
        raw_rows = [emit(c) for c in live_stream(args.limit)]
        if not raw_rows:
            print("Live fetch unavailable; falling back to synthetic.")
            raw_rows = [emit(c) for c in fake_stream(args.limit)]
    else:
        raw_rows = [emit(c) for c in fake_stream(args.limit)]

    # Build keyword set
    kw_set = set()
    if args.keywords_file and os.path.isfile(args.keywords_file):
        with open(args.keywords_file,'r',encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if line and not line.startswith('#'):
                    kw_set.add(line.lower())
    if args.keywords:
        kw_set.update(k.lower() for k in args.keywords)

    bot_re = re.compile(r"bot|automoderator|mod|helper", re.IGNORECASE)
    def passes_filters(r: dict) -> bool:
        body = (r.get('body') or '').strip()
        if len(body) < args.min_len:
            return False
        if kw_set:
            low = body.lower()
            if not any(k in low for k in kw_set):
                return False
        if args.no_bots:
            if bot_re.search(r.get('author_hash','')):  # hashed, so cannot detect; skip
                return False
            # crude heuristic: moderation notice pattern
            if body.startswith('Hey /u/') and 'action was performed automatically' in body:
                return False
        return True

    rows = [r for r in raw_rows if passes_filters(r)]

    with open(args.out,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(f"Wrote {len(rows)} rows (from {len(raw_rows)} raw) -> {args.out}")

    if args.summary_out:
        # Simple counts by (transition, pre_post, score_bucket)
        from collections import Counter
        combo = Counter((r['transition'], r['pre_post'], r['score_bucket']) for r in rows)
        transitions = Counter(r['transition'] for r in rows if r['transition'])
        summary = {
            'total_raw': len(raw_rows),
            'total_retained': len(rows),
            'by_transition_phase_bucket': {f"{k[0]}|{k[1]}|{k[2]}": v for k,v in combo.items()},
            'by_transition': dict(transitions),
            'keyword_filter': sorted(list(kw_set)),
            'min_len': args.min_len,
            'no_bots': args.no_bots
        }
        with open(args.summary_out,'w',encoding='utf-8') as sf:
            json.dump(summary, sf, indent=2)
        print(f"Summary -> {args.summary_out}")

if __name__ == '__main__':
    main()
