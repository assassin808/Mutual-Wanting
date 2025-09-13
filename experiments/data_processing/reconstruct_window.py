#!/usr/bin/env python3
"""Reconstruct pre/post transition windows from live scrape aggregates.

Assumptions:
  * Source directory: pipeline/data/live_scrape/ contains per-subreddit aggregate JSONL files each line with fields at least:
       id, body, created_utc, score, subreddit, parent_id, link_id, author (author may be missing -> default 'anon')
  * Transition boundaries (UTC timestamps) will be provided via CLI flags.
  * Output raw window files (pre_raw, post_raw) written to pipeline/data/ then caller should invoke archive_normalize.py.

Usage:
  python scripts/reconstruct_window.py \
      --transition-id gpt4_to_4o \
      --pre-start 1710806400 --pre-end 1711411200 \
      --post-start 1711411200 --post-end 1712016000 \
      --source-dir pipeline/data/live_scrape \
      --out-dir pipeline/data

Notes:
  - Overlap boundary (pre_end == post_start) is allowed; inclusion rule: pre interval is [pre_start, pre_end), post is [post_start, post_end).
  - Emits *_pre_raw.jsonl and *_post_raw.jsonl plus a small summary JSON with counts.
  - Does not hash authors (done in normalization stage).
"""
from __future__ import annotations
import argparse, json, os, sys, glob
from typing import Dict, Any


def iter_source_rows(source_dir: str):
    pattern = os.path.join(source_dir, '*_aggregate.jsonl')
    files = glob.glob(pattern)
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line:
                    continue
                try:
                    obj=json.loads(line)
                except Exception:
                    continue
                yield obj


def in_range(ts: int, start: int, end: int) -> bool:
    return start <= ts < end


def reconstruct(args):
    pre_out = os.path.join(args.out_dir, f"{args.transition_id}_pre_raw.jsonl")
    post_out = os.path.join(args.out_dir, f"{args.transition_id}_post_raw.jsonl")
    pre_count = post_count = 0
    with open(pre_out, 'w', encoding='utf-8') as pre_f, open(post_out, 'w', encoding='utf-8') as post_f:
        for obj in iter_source_rows(args.source_dir):
            ts = obj.get('created_utc')
            if ts is None:
                continue
            try:
                its = int(ts)
            except Exception:
                continue
            if in_range(its, args.pre_start, args.pre_end):
                pre_f.write(json.dumps(obj)+'\n')
                pre_count += 1
            elif in_range(its, args.post_start, args.post_end):
                post_f.write(json.dumps(obj)+'\n')
                post_count += 1
    summary = {
        'transition_id': args.transition_id,
        'pre': {'start': args.pre_start, 'end': args.pre_end, 'n_rows': pre_count},
        'post': {'start': args.post_start, 'end': args.post_end, 'n_rows': post_count},
        'source_dir': args.source_dir
    }
    with open(os.path.join(args.out_dir, f"{args.transition_id}_window_summary.json"), 'w', encoding='utf-8') as sf:
        json.dump(summary, sf, indent=2)
    print(f"Reconstructed windows: pre={pre_count} post={post_count}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transition-id', required=True)
    ap.add_argument('--pre-start', type=int, required=True)
    ap.add_argument('--pre-end', type=int, required=True)
    ap.add_argument('--post-start', type=int, required=True)
    ap.add_argument('--post-end', type=int, required=True)
    ap.add_argument('--source-dir', default='pipeline/data/live_scrape')
    ap.add_argument('--out-dir', default='pipeline/data')
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    reconstruct(args)

if __name__ == '__main__':
    main()
