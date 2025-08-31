#!/usr/bin/env python3
"""Automated multi-transition Reddit window fetcher.

Reads `transitions.yaml` plus a subreddit list and fetches (best-effort via Pushshift)
pre and post windows for each transition, writing JSONL archives compatible with
`multi_backfill_stub.py` and generating an `archive_map.json` file.

Why this script exists: We previously had a single-window fetch script
(`fetch_window_reddit.py`). For the real experiment we need a reproducible, batch
process across all defined transitions with consistent naming and a manifest.

Usage:
  python pipeline/multi_fetch_windows.py \
      --transitions pipeline/transitions.yaml \
      --subreddits pipeline/subreddits.txt \
      --out-dir pipeline/data \
      --max-per-subreddit 120 \
      --only gpt4_to_4o

Environment (optional) for future PRAW integration:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

Notes:
  * Currently uses internal minimal Pushshift fetch (same logic as fetch_window_reddit)
    for determinism within resource constraints.
  * If network access is unavailable, you can rerun with --dry-run to just emit the
    computed time windows and manifest without fetching.
  * Start/end boundaries:
       pre  : [release_date - pre_days, release_date) inclusive of days prior
       post : [release_date, release_date + post_days) inclusive of post days
    We operationalize as:
       pre_start = release_date - pre_days at 00:00:00Z
       pre_end   = (release_date - 1 day) 23:59:59Z
       post_start= release_date 00:00:00Z
       post_end  = (release_date + post_days - 1 day) 23:59:59Z
"""
from __future__ import annotations
import argparse, json, yaml, time, requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--subreddits', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--max-per-subreddit', type=int, default=150)
    ap.add_argument('--sleep', type=float, default=1.0, help='Sleep seconds between Pushshift pages')
    ap.add_argument('--only', nargs='*', help='Subset of transition IDs to fetch')
    ap.add_argument('--dry-run', action='store_true', help='Compute windows but do not fetch')
    return ap.parse_args()


def load_transitions(path: str) -> List[Dict[str,Any]]:
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_subreddits(path: str) -> List[str]:
    subs=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            subs.append(line)
    return subs


def compute_windows(t: Dict[str,Any]):
    rel = datetime.strptime(str(t['release_date']), '%Y-%m-%d')
    pre_days = int(t.get('pre_days',14))
    post_days = int(t.get('post_days',14))
    pre_start = (rel - timedelta(days=pre_days)).strftime('%Y-%m-%dT00:00:00Z')
    pre_end_dt = rel - timedelta(seconds=1)  # up to just before release_date 00:00:00
    pre_end = (pre_end_dt - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z') if pre_days>0 else pre_start
    # Actually simpler: last pre day is rel - 1 day 23:59:59
    pre_end = (rel - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')
    post_start = rel.strftime('%Y-%m-%dT00:00:00Z')
    post_end = (rel + timedelta(days=post_days) - timedelta(seconds=1))  # exclusive-like
    post_end = (rel + timedelta(days=post_days) - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')
    return {
        'pre': {'start': pre_start, 'end': pre_end},
        'post': {'start': post_start, 'end': post_end}
    }


PUSHSHIFT_URL = 'https://api.pushshift.io/reddit/comment/search/'


def fetch_pushshift(sub: str, start_iso: str, end_iso: str, limit: int, sleep_s: float) -> List[dict]:
    start_ts = int(datetime.strptime(start_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    end_ts = int(datetime.strptime(end_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    size=200
    results=[]
    after = start_ts
    attempts=0
    while after < end_ts and len(results) < limit:
        params = {
            'subreddit': sub,
            'after': after,
            'before': end_ts,
            'size': size,
            'sort': 'asc',
            'sort_type': 'created_utc'
        }
        try:
            r = requests.get(PUSHSHIFT_URL, params=params, timeout=20)
            if r.status_code != 200:
                break
            data = r.json().get('data',[])
            if not data:
                break
            results.extend(data)
            after = data[-1]['created_utc'] + 1
            if len(data) < size:
                break
            time.sleep(sleep_s)
        except Exception:
            attempts+=1
            if attempts>3:
                break
            time.sleep(2)
    return results[:limit]


def normalize(rows: List[dict]) -> List[dict]:
    out=[]
    for r in rows:
        score = r.get('score',0) or 0
        if score >= 50: bucket='hi'
        elif score >= 10: bucket='mid'
        else: bucket='lo'
        link_id = r.get('link_id') or r.get('submission_id') or f"t3_{r.get('id','')}"
        out.append({
            'comment_id': r.get('id'),
            'parent_id': r.get('parent_id') or None,
            'thread_id': link_id,
            'created_utc': int(r.get('created_utc',0)),
            'score': score,
            'score_bucket': bucket,
            'author_hash': r.get('author','anon'),  # hashing deferred (multi_backfill does hashing)
            'body': r.get('body') or '',
            'subreddit': r.get('subreddit','unknown')
        })
    return out


def write_jsonl(path: Path, rows: List[dict]):
    with open(path,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r)+'\n')


def main():
    args = parse_args()
    transitions = load_transitions(args.transitions)
    subs = load_subreddits(args.subreddits)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    archive_map: Dict[str,Dict[str,str]] = {}
    summary = {}
    for t in transitions:
        tid = t['id']
        if args.only and tid not in args.only:
            continue
        windows = compute_windows(t)
        summary[tid] = windows
        for phase in ['pre','post']:
            fname = f"{tid}_{phase}.jsonl"
            fpath = out_dir / fname
            archive_map.setdefault(tid,{})[phase] = str(fpath)
            if args.dry_run:
                continue
            if fpath.exists():
                print(f"[skip] {fpath} exists")
                continue
            win = windows[phase]
            all_rows=[]
            for sub in subs:
                rows = fetch_pushshift(sub, win['start'], win['end'], args.max_per_subreddit, args.sleep)
                norm = normalize(rows)
                all_rows.extend(norm)
                print(f"{tid}:{phase}:{sub} -> {len(norm)}")
            write_jsonl(fpath, all_rows)
            print(f"Wrote {len(all_rows)} rows -> {fpath}")

    # Write artifacts
    with open(out_dir / 'archive_map.json','w',encoding='utf-8') as f:
        json.dump(archive_map,f,indent=2)
    with open(out_dir / 'fetch_windows_summary.json','w',encoding='utf-8') as f:
        json.dump(summary,f,indent=2)
    print(f"Archive map -> {out_dir / 'archive_map.json'}")
    print(f"Window summary -> {out_dir / 'fetch_windows_summary.json'}")
    if args.dry_run:
        print("Dry run complete (no fetch performed).")

if __name__ == '__main__':
    main()
