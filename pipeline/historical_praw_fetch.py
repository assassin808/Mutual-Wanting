#!/usr/bin/env python3
"""Historical Reddit comment fetcher using native Reddit API (no Pushshift).

Strategy:
  1. Authenticate via PRAW to obtain OAuth token.
  2. For each subreddit and time window, chunk the window (default 1 day) and
     issue Cloudsearch syntax queries against /r/{sub}/search with
       q = 'timestamp:{start}..{end}'  (epoch seconds range)
       syntax=cloudsearch, restrict_sr=1, sort=new, limit=100
  3. Collect unique submission IDs; for each submission retrieve comments
     (replace_more=0) and filter comments whose created_utc lies within the
     global window (avoid spillover from edited / stale threads).
  4. Stop early per subreddit if cap reached.

Outputs: JSONL comment file with fields expected by downstream backfill:
  id, parent_id, link_id, created_utc, score, body, subreddit, author

Example:
  python pipeline/historical_praw_fetch.py \
    --subreddits ChatGPT OpenAI \
    --start 2024-04-29T00:00:00Z \
    --end 2024-05-12T23:59:59Z \
    --out pipeline/data/gpt4_to_4o_pre.jsonl \
    --per-subreddit-cap 1200

Notes:
  * Requires env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
  * Cloudsearch syntax is documented in legacy Reddit search; still functional for
    timestamp range queries. We chunk to avoid hitting 1000 search cap limits.
  * This script is intentionally conservative (no multithreading) for transparency.
"""
from __future__ import annotations
import argparse, os, time, json, math
try:
    from . import env_loader  # type: ignore
except Exception:
    import env_loader  # fallback when run as script
env_loader.load_env_once()
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Set

try:
    import praw  # type: ignore
except ImportError:
    raise SystemExit("praw not installed; see requirements.txt")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subreddits', nargs='+', required=True)
    ap.add_argument('--start', required=True, help='ISO UTC e.g. 2024-04-29T00:00:00Z')
    ap.add_argument('--end', required=True, help='ISO UTC inclusive end e.g. 2024-05-12T23:59:59Z')
    ap.add_argument('--out', required=True)
    ap.add_argument('--chunk-hours', type=int, default=24, help='Window chunk size (hours) for search pagination')
    ap.add_argument('--per-subreddit-cap', type=int, default=5000)
    ap.add_argument('--sleep', type=float, default=1.0, help='Sleep between search requests (sec)')
    ap.add_argument('--keywords', nargs='*', default=['gpt','chatgpt','openai','model','update','prompt'],
                    help='Optional keyword list to seed queries when pure timestamp yields nothing')
    return ap.parse_args()


def iso_to_epoch(iso: str) -> int:
    return int(datetime.strptime(iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc).timestamp())


def epoch_to_iso(ts: int) -> str:
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%SZ')


def get_reddit():
    cid=os.getenv('REDDIT_CLIENT_ID'); cs=os.getenv('REDDIT_CLIENT_SECRET'); ua=os.getenv('REDDIT_USER_AGENT')
    if not (cid and cs and ua):
        raise SystemExit('Missing Reddit credentials in environment')
    return praw.Reddit(client_id=cid, client_secret=cs, user_agent=ua, check_for_async=False)


def _search_chunk(reddit, subreddit: str, start_epoch: int, end_epoch: int, keywords: List[str]) -> List[str]:
    """Issue progressively broader cloudsearch queries for a time slice.

    We keep queries minimal to reduce request count; stop on first yielding hits.
    """
    base = f"timestamp:{start_epoch}..{end_epoch}"
    queries = [
        f"{base} AND author:*",
        f"({base}) AND (self:yes OR self:no)",
        base,
        f"{base} AND *",
    ]
    # Add keyword seeded variants (helps subs with sparse generic titles)
    for kw in keywords[:4]:
        queries.append(f"({base}) AND {kw}")
    # Final ultra-broad wildcard (rarely needed, but prevents silent misses)
    queries.append(f"{base} AND title:*")
    out_ids: Set[str] = set()
    for qi, q in enumerate(queries):
        try:
            # IMPORTANT: positional first arg is the query string; previous errors omitted it.
            results = reddit.subreddit(subreddit).search(q, syntax='cloudsearch', sort='new', limit=100, params={'restrict_sr':1})
            pulled=0
            for s in results:
                pulled+=1
                created = int(getattr(s,'created_utc',0))
                if start_epoch <= created <= end_epoch:
                    out_ids.add(s.id)
            if pulled:
                if qi>0:
                    print(f"    [search-hit] sub={subreddit} q_variant={qi} q='{q[:60]}' ids={len(out_ids)}")
                break
        except Exception as e:
            print(f"[warn] search query error sub={subreddit} variant={qi} q='{q}': {e}")
            continue
    return list(out_ids)


def search_submissions_cloud(reddit, subreddit: str, start_ts: int, end_ts: int, chunk_hours: int, sleep_s: float, keywords: List[str]) -> List[str]:
    """Return unique submission IDs using adaptive chunking.

    Strategy:
      Start with requested chunk size. For empty slices, recursively contract:
        H -> H/2 until < 3h, then accept emptiness.
    """
    ids: Set[str] = set()
    end_dt = datetime.utcfromtimestamp(end_ts)

    def process_window(win_start: datetime, win_end: datetime, hours: int):
        if hours < 3:
            return
        cursor = win_start
        while cursor <= win_end:
            seg_end = min(cursor + timedelta(hours=hours) - timedelta(seconds=1), win_end)
            se_start = int(cursor.timestamp())
            se_end = int(seg_end.timestamp())
            seg_ids = _search_chunk(reddit, subreddit, se_start, se_end, keywords)
            if not seg_ids and hours > 3:
                # contract
                smaller = hours//2
                if smaller >=3:
                    process_window(cursor, seg_end, smaller)
            else:
                if seg_ids:
                    ids.update(seg_ids)
            cursor = seg_end + timedelta(seconds=1)
            try:
                limits = getattr(reddit.auth, 'limits', None)
                if limits:
                    remaining = limits.get('remaining')
                    if remaining is not None:
                        print(f"    [rl] rem={remaining}")
            except Exception:
                pass
            time.sleep(sleep_s)

    process_window(datetime.utcfromtimestamp(start_ts), end_dt, chunk_hours)
    return list(ids)


def collect_comments(reddit, subreddit: str, submission_ids: List[str], start_ts: int, end_ts: int, cap: int) -> List[Dict]:
    out=[]
    for sid in submission_ids:
        if len(out) >= cap:
            break
        try:
            submission = reddit.submission(id=sid)
            submission.comment_sort='top'
            submission.comments.replace_more(limit=0)
            for c in submission.comments.list():
                if len(out) >= cap:
                    break
                created = int(getattr(c,'created_utc',0))
                if created < start_ts or created > end_ts:
                    continue
                body = getattr(c,'body','') or ''
                out.append({
                    'id': getattr(c,'id',None),
                    'parent_id': getattr(c,'parent_id',None),
                    'link_id': getattr(c,'link_id', f"t3_{sid}"),
                    'created_utc': created,
                    'score': getattr(c,'score',0) or 0,
                    'body': body,
                    'subreddit': subreddit,
                    'author': str(getattr(c,'author','anon'))
                })
        except Exception as e:
            print(f"[warn] submission fetch error {sid}: {e}")
    return out


def main():
    args=parse_args()
    start_ts=iso_to_epoch(args.start)
    end_ts=iso_to_epoch(args.end)
    reddit=get_reddit()
    all_rows=[]
    for sub in args.subreddits:
        print(f"[subreddit] {sub} window {args.start} -> {args.end}")
        ids = search_submissions_cloud(reddit, sub, start_ts, end_ts, args.chunk_hours, args.sleep, args.keywords)
        print(f"  submissions found: {len(ids)}")
        if not ids:
            continue
        comments = collect_comments(reddit, sub, ids, start_ts, end_ts, args.per_subreddit_cap)
        print(f"  comments collected: {len(comments)}")
        all_rows.extend(comments)
    # Write
    with open(args.out,'w',encoding='utf-8') as f:
        for r in all_rows:
            f.write(json.dumps(r)+'\n')
    print(f"Total comments written: {len(all_rows)} -> {args.out}")

if __name__=='__main__':
    main()
