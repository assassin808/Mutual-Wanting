#!/usr/bin/env python3
"""Compute coverage statistics for a normalized archive window.

Inputs: one or more normalized JSONL files (fields include created_utc, transition, phase, body, score).
Required CLI args for window boundaries (ISO date): --start-date YYYY-MM-DD --end-date YYYY-MM-DD

Outputs JSON with:
 - n_rows
 - min_day, max_day
 - days_covered (count of distinct days with ≥1 row)
 - missing_days (list)
 - sparse_days (list of days with < sparse_threshold rows)
 - token_length_median

Usage:
  python pipeline/archive_coverage.py --files data/normalized/gpt4_to_4o_pre.jsonl \
      --start-date 2024-04-29 --end-date 2024-05-12 --out pipeline/coverage_gpt4_to_4o_pre.json
"""
from __future__ import annotations
import argparse, json, pathlib, statistics, datetime as dt

def day_from_ts(ts: int):
    return dt.datetime.utcfromtimestamp(ts).date()

def iter_rows(files):
    for fp in files:
        with open(fp,'r',encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

def daterange(start: dt.date, end: dt.date):
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--start-date', required=True)
    ap.add_argument('--end-date', required=True)
    ap.add_argument('--sparse-threshold', type=int, default=10)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    start = dt.date.fromisoformat(args.start_date)
    end = dt.date.fromisoformat(args.end_date)

    per_day_counts = {}
    lengths = []
    n_rows = 0
    for obj in iter_rows(args.files):
        ts = obj.get('created_utc')
        if not isinstance(ts, int):
            continue
        d = day_from_ts(ts)
        if d < start or d > end:
            continue
        per_day_counts[d] = per_day_counts.get(d, 0) + 1
        body = obj.get('body') or ''
        lengths.append(len(body.split()))
        n_rows += 1

    covered_days = sorted(per_day_counts.keys())
    missing_days = [d.isoformat() for d in daterange(start,end) if d not in per_day_counts]
    sparse_days = [d.isoformat() for d,c in per_day_counts.items() if c < args.sparse_threshold]
    out_obj = {
        'n_rows': n_rows,
        'min_day': covered_days[0].isoformat() if covered_days else None,
        'max_day': covered_days[-1].isoformat() if covered_days else None,
        'days_covered': len(covered_days),
        'missing_days': missing_days,
        'sparse_days': sparse_days,
        'token_length_median': statistics.median(lengths) if lengths else None
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path,'w',encoding='utf-8') as f:
        json.dump(out_obj, f, indent=2)
    print(f"Coverage report -> {out_path}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Archive coverage validator for historical pre/post Reddit windows.

Given two JSONL archives (pre, post) expected to cover contiguous calendar day ranges
this script reports:
  - Counts per calendar day (UTC)
  - Missing days relative to inferred min/max date
  - Total rows, token counts (approx), median comment length (chars, tokens)
  - Score bucket distribution per phase
  - Basic sanity flags (sparse_day if < threshold rows)

Usage:
  python pipeline/archive_coverage.py --pre pre_window.jsonl --post post_window.jsonl --out coverage_report.json

Threshold heuristics are intentionally minimal and can be tuned.
"""
from __future__ import annotations
import json, argparse, datetime as dt, statistics, re
from collections import defaultdict, Counter
from typing import List, Dict, Any

WORD_RE = re.compile(r"[A-Za-z']+")


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


def day_key(ts: int) -> str:
    return dt.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')


def summarize(rows: List[Dict[str,Any]]):
    per_day=defaultdict(int)
    lengths=[]
    token_counts=[]
    score_buckets=Counter()
    for r in rows:
        ts=r.get('created_utc')
        if ts is None:
            continue
        per_day[day_key(int(ts))]+=1
        body=(r.get('body') or '')
        lengths.append(len(body))
        toks=WORD_RE.findall(body.lower())
        token_counts.append(len(toks))
        sb=r.get('score_bucket') or _score_bucket(r.get('score',0))
        score_buckets[sb]+=1
    if per_day:
        min_day=min(per_day)
        max_day=max(per_day)
        span=(dt.datetime.strptime(max_day,'%Y-%m-%d')-dt.datetime.strptime(min_day,'%Y-%m-%d')).days+1
    else:
        min_day=max_day=None
        span=0
    expected_days=set()
    if min_day and max_day:
        start=dt.datetime.strptime(min_day,'%Y-%m-%d')
        for i in range(span):
            expected_days.add((start+dt.timedelta(days=i)).strftime('%Y-%m-%d'))
    missing=sorted(expected_days - set(per_day.keys()))
    sparse=[d for d,c in per_day.items() if c<10]
    return {
        'n_rows': len(rows),
        'days_covered': len(per_day),
        'min_day': min_day,
        'max_day': max_day,
        'expected_span_days': span,
        'missing_days': missing,
        'sparse_days': sparse,
        'per_day_counts': dict(per_day),
        'char_length_median': statistics.median(lengths) if lengths else 0,
        'token_length_median': statistics.median(token_counts) if token_counts else 0,
        'score_bucket_dist': dict(score_buckets)
    }


def _score_bucket(score):
    try:
        s=int(score)
    except Exception:
        s=0
    if s>=50:
        return 'hi'
    if s>=10:
        return 'mid'
    return 'lo'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pre', required=True)
    ap.add_argument('--post', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()

    pre_rows=load_jsonl(args.pre)
    post_rows=load_jsonl(args.post)
    pre_sum=summarize(pre_rows)
    post_sum=summarize(post_rows)

    coverage={
        'pre': pre_sum,
        'post': post_sum,
        'ratio_rows_post_pre': (post_sum['n_rows']/pre_sum['n_rows']) if pre_sum['n_rows'] else None
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(coverage,f,indent=2)
    print(f"Archive coverage -> {args.out}")

if __name__=='__main__':
    main()
