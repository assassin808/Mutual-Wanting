#!/usr/bin/env python3
#!/usr/bin/env python3
"""Multi-transition Reddit window fetcher (Pushshift + PRAW fallback).

Clean reimplementation after corruption.
"""
from __future__ import annotations
import argparse, json, yaml, time, requests, os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    import praw  # type: ignore
except ImportError:  # pragma: no cover
    praw = None

PUSHSHIFT_URL = 'https://api.pushshift.io/reddit/comment/search/'


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--subreddits', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--max-per-subreddit', type=int, default=200)
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--refetch-empty', action='store_true')
    return ap.parse_args()


def load_yaml(path: str):
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_subs(path: str) -> List[str]:
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
    return {
        'pre': {
            'start': (rel - timedelta(days=pre_days)).strftime('%Y-%m-%dT00:00:00Z'),
            'end': (rel - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')
        },
        'post': {
            'start': rel.strftime('%Y-%m-%dT00:00:00Z'),
            'end': (rel + timedelta(days=post_days) - timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')
        }
    }


def fetch_pushshift(sub: str, start_iso: str, end_iso: str, limit: int, sleep_s: float) -> List[dict]:
    start_ts = int(datetime.strptime(start_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    end_ts = int(datetime.strptime(end_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    results=[]
    size=200
    after=start_ts
    attempts=0
    while after < end_ts and len(results) < limit:
        params={'subreddit':sub,'after':after,'before':end_ts,'size':size,'sort':'asc','sort_type':'created_utc'}
        try:
            r=requests.get(PUSHSHIFT_URL, params=params, timeout=15)
            if r.status_code!=200:
                break
            data=r.json().get('data',[])
            if not data:
                break
            results.extend(data)
            after=data[-1]['created_utc']+1
            if len(data)<size:
                break
            time.sleep(sleep_s)
        except Exception:
            attempts+=1
            if attempts>3: break
            time.sleep(2)
    return results[:limit]


def fetch_praw(sub: str, start_iso: str, end_iso: str, limit: int) -> List[dict]:
    client_id=os.getenv('REDDIT_CLIENT_ID'); client_secret=os.getenv('REDDIT_CLIENT_SECRET'); ua=os.getenv('REDDIT_USER_AGENT','MutualWantingStudy/0.1')
    if praw is None or not (client_id and client_secret):
        return []
    start_ts=int(datetime.strptime(start_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    end_ts=int(datetime.strptime(end_iso.replace('Z',''), '%Y-%m-%dT%H:%M:%S').timestamp())
    reddit=praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=ua, check_for_async=False)
    out={}
    try:
        for submission in reddit.subreddit(sub).submissions(start_ts,end_ts):  # type: ignore[attr-defined]
            submission.comment_sort='top'
            submission.comments.replace_more(limit=0)
            for c in submission.comments.list():
                if len(out)>=limit: break
                created=int(getattr(c,'created_utc',0))
                if created<start_ts or created> end_ts: continue
                cid=getattr(c,'id',None)
                if not cid or cid in out: continue
                out[cid]={
                    'id':cid,
                    'parent_id':getattr(c,'parent_id',None),
                    'link_id':getattr(c,'link_id',f"t3_{submission.id}"),
                    'created_utc':created,
                    'score':getattr(c,'score',0) or 0,
                    'body':getattr(c,'body','') or '',
                    'subreddit':sub,
                    'author':str(getattr(c,'author','anon'))
                }
            if len(out)>=limit: break
    except Exception:
        return list(out.values())
    return list(out.values())


def normalize(rows: List[dict]) -> List[dict]:
    out=[]
    for r in rows:
        score=r.get('score',0) or 0
        if score>=50: bucket='hi'
        elif score>=10: bucket='mid'
        else: bucket='lo'
        link_id=r.get('link_id') or r.get('submission_id') or f"t3_{r.get('id','')}"
        out.append({
            'id':r.get('id'),
            'parent_id':r.get('parent_id') or None,
            'link_id':link_id,
            'created_utc':int(r.get('created_utc',0)),
            'score':score,
            'body':r.get('body') or '',
            'subreddit':r.get('subreddit','unknown'),
            'author':r.get('author','anon'),
            'score_bucket':bucket
        })
    return out


def write_jsonl(path: Path, rows: List[dict]):
    with open(path,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r)+'\n')


def validate_subs(subs: List[str]) -> (List[str], List[str]):
    invalid=[]
    if praw is None:
        return subs, invalid
    client_id=os.getenv('REDDIT_CLIENT_ID'); client_secret=os.getenv('REDDIT_CLIENT_SECRET'); ua=os.getenv('REDDIT_USER_AGENT','MutualWantingStudy/0.1')
    if not (client_id and client_secret):
        return subs, invalid
    reddit=praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=ua, check_for_async=False)
    valid=[]
    for s in subs:
        try:
            _=reddit.subreddit(s).id
            valid.append(s)
        except Exception:
            invalid.append(s)
    return valid, invalid


def main():
    args=parse_args()
    transitions=load_yaml(args.transitions)
    subs=load_subs(args.subreddits)
    out_dir=Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    subs, invalid = validate_subs(subs)
    if invalid:
        print(f"[warn] Skipping invalid subreddits: {invalid}")

    archive_map={}
    summary={}
    for t in transitions:
        tid=t['id']
        if args.only and tid not in args.only:
            continue
        windows=compute_windows(t)
        summary[tid]=windows
        for phase in ['pre','post']:
            fname=f"{tid}_{phase}.jsonl"; fpath=out_dir/fname
            archive_map.setdefault(tid,{})[phase]=str(fpath)
            if args.dry_run:
                continue
            if fpath.exists():
                if fpath.stat().st_size>0 or not args.refetch_empty:
                    print(f"[skip] {fpath} exists")
                    continue
                else:
                    print(f"[refetch-empty] {fpath} size=0; re-fetch")
            win=windows[phase]
            all_rows=[]
            for sub in subs:
                rows=fetch_pushshift(sub, win['start'], win['end'], args.max_per_subreddit, args.sleep)
                source='pushshift'
                if not rows:
                    rows=fetch_praw(sub, win['start'], win['end'], args.max_per_subreddit)
                    source='praw' if rows else 'none'
                norm=normalize(rows)
                all_rows.extend(norm)
                print(f"{tid}:{phase}:{sub} -> {len(norm)} ({source})")
            write_jsonl(fpath, all_rows)
            print(f"Wrote {len(all_rows)} rows -> {fpath}")

    with open(out_dir/'archive_map.json','w',encoding='utf-8') as f:
        json.dump(archive_map,f,indent=2)
    with open(out_dir/'fetch_windows_summary.json','w',encoding='utf-8') as f:
        json.dump(summary,f,indent=2)
    print(f"Archive map -> {out_dir/'archive_map.json'}")
    print(f"Window summary -> {out_dir/'fetch_windows_summary.json'}")
    if args.dry_run:
        print('Dry run only (no fetch performed).')

if __name__=='__main__':
    main()
