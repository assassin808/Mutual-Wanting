#!/usr/bin/env python3
"""Build a recent (API-accessible) submission corpus for exploratory labeling.

Inputs:
  - Directory of per-subreddit *_aggregate.jsonl files (from limited_historical_scrape.py)
  - Optional subreddit allowlist (default: heuristic core set)
  - Optional keyword include filter (case-insensitive OR over title+selftext)
  - Optional keyword exclude filter (remove obvious off-topic noise)
  - Maximum rows per subreddit to balance class distribution

Outputs:
  pipeline/data/recent_corpus_merged.jsonl (union of filtered submissions)
  pipeline/data/recent_corpus_manifest.json (counts, filters applied)
  pipeline/data/recent_sample_for_labeling.csv (stratified sample scaffold)

Sampling Strategy:
  * Score buckets: hi (>=50), mid (10-49), lo (<10) using Reddit score field.
  * Attempt near-equal per bucket within each core subreddit until cap reached.
  * Random without replacement. No synthetic augmentation.

Use this only for exploratory schema calibration; not a substitute for historical pre/post.
"""
from __future__ import annotations
import argparse, json, random, re, csv, pathlib
from typing import List, Dict, Any, Iterable

CORE_SUBS = ["ChatGPT","OpenAI","LocalLLaMA","MachineLearning","PromptEngineering"]

SCORE_BUCKETS = [
    ("hi", lambda s: s is not None and s >= 50),
    ("mid", lambda s: s is not None and 10 <= s < 50),
    ("lo", lambda s: s is not None and s < 10),
]


def iter_jsonl(path):
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def text_match(row: Dict[str,Any], includes: List[str], excludes: List[str]) -> bool:
    blob = f"{row.get('title','')}\n{row.get('selftext','')}".lower()
    if includes and not any(k in blob for k in includes):
        return False
    if excludes and any(k in blob for k in excludes):
        return False
    return True


def bucket(score):
    for name, pred in SCORE_BUCKETS:
        if pred(score):
            return name
    return "unknown"


def sample_balanced(rows: List[Dict[str,Any]], per_sub_cap: int, rng: random.Random) -> List[Dict[str,Any]]:
    if len(rows) <= per_sub_cap:
        return rows
    # Partition by bucket
    by_bucket: Dict[str,List[Dict[str,Any]]] = {b:[] for b,_ in SCORE_BUCKETS}
    for r in rows:
        b = bucket(r.get('score'))
        if b in by_bucket:
            by_bucket[b].append(r)
    # Target equal share
    target_each = per_sub_cap // len(SCORE_BUCKETS)
    sampled = []
    for b in by_bucket:
        rng.shuffle(by_bucket[b])
        sampled.extend(by_bucket[b][:target_each])
    # Fill remainder from combined pool
    if len(sampled) < per_sub_cap:
        remaining = [r for b in by_bucket for r in by_bucket[b][target_each:]]
        rng.shuffle(remaining)
        need = per_sub_cap - len(sampled)
        sampled.extend(remaining[:need])
    return sampled


def build(args):
    rng = random.Random(args.seed)
    data_dir = pathlib.Path(args.scrape_dir)
    includes = [k.lower() for k in args.include.split(',') if k.strip()] if args.include else []
    excludes = [k.lower() for k in args.exclude.split(',') if k.strip()] if args.exclude else []
    subs = CORE_SUBS if not args.subreddits else [s.strip() for s in args.subreddits.split(',') if s.strip()]

    merged_rows: List[Dict[str,Any]] = []
    manifest: Dict[str,Any] = {"subs":{},"filters":{"include":includes,"exclude":excludes},"per_sub_cap":args.per_sub_cap}

    for sub in subs:
        agg_path = data_dir / f"{sub}_aggregate.jsonl"
        if not agg_path.exists():
            continue
        rows = [r for r in iter_jsonl(str(agg_path)) if text_match(r, includes, excludes)]
        sampled = sample_balanced(rows, args.per_sub_cap, rng)
        for r in sampled:
            r['score_bucket'] = bucket(r.get('score'))
            r['source_sub'] = sub
        manifest['subs'][sub] = {"available": len(rows), "sampled": len(sampled)}
        merged_rows.extend(sampled)

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    merged_path = out_dir / 'recent_corpus_merged.jsonl'
    with merged_path.open('w',encoding='utf-8') as f:
        for r in merged_rows:
            f.write(json.dumps(r)+'\n')

    manifest_path = out_dir / 'recent_corpus_manifest.json'
    with manifest_path.open('w',encoding='utf-8') as f:
        json.dump(manifest,f,indent=2)

    # Build sampling CSV scaffold for manual labeling (one row per submission)
    csv_path = out_dir / 'recent_sample_for_labeling.csv'
    fieldnames = ['id','source_sub','created_utc','score','score_bucket','title','selftext']
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in merged_rows:
            w.writerow({k: r.get(k,'') for k in fieldnames})

    print(f"Merged {len(merged_rows)} rows across {len(subs)} subs -> {merged_path}")
    print(f"Sample CSV -> {csv_path}")
    print(f"Manifest -> {manifest_path}")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scrape-dir', required=True, help='Directory containing *_aggregate.jsonl outputs')
    ap.add_argument('--out-dir', default='pipeline/data', help='Output directory root')
    ap.add_argument('--subreddits', help='Comma list override of core subreddits (optional)')
    ap.add_argument('--include', help='Comma list of include keywords (case-insensitive OR)')
    ap.add_argument('--exclude', help='Comma list of exclude keywords')
    ap.add_argument('--per-sub-cap', type=int, default=400, help='Max sampled rows per subreddit')
    ap.add_argument('--seed', type=int, default=42)
    return ap.parse_args()

if __name__ == '__main__':
    build(parse_args())
