#!/usr/bin/env python3
"""Normalize raw archive ingest JSONL files to unified analysis schema.

Input rows (from archive_ingest.py) require fields: id, parent_id, link_id, created_utc, score, body, subreddit, author

Output schema (JSONL):
    id, parent_id, link_id, created_utc, score, score_bucket, body, subreddit,
    author_hash, transition, pre_post

Usage:
    python pipeline/archive_normalize.py \
            --transition-id gpt4_to_4o \
            --phase pre --in pipeline/data/gpt4_to_4o_pre_raw.jsonl --out pipeline/data/gpt4_to_4o_pre.jsonl \
            --author-salt "$AUTHOR_SALT"

Notes:
    * author_hash = sha256(author + salt) hex; salt required (env or flag) to reduce re-identification risk.
    * score_bucket thresholds: lo <10, mid 10–49, hi ≥50 (aligns sampling_spec.md)
    * Skips rows missing essential fields; counts stats to stderr.
"""
from __future__ import annotations
import argparse, json, sys, os, hashlib


def score_bucket(score: int) -> str:
    if score < 10:
        return 'lo'
    if score < 50:
        return 'mid'
    return 'hi'


def author_hash(author: str, salt: str) -> str:
    h = hashlib.sha256()
    h.update((author + salt).encode('utf-8'))
    return h.hexdigest()


def normalize(path: str, out_path: str, transition: str, phase: str, salt: str):
    kept = 0
    skipped = 0
    with open(path, 'r', encoding='utf-8') as inp, open(out_path, 'w', encoding='utf-8') as out:
        for line in inp:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                skipped += 1
                continue
            cid = obj.get('id')
            sr = obj.get('subreddit')
            ts = obj.get('created_utc')
            if not cid or sr is None or ts is None:
                skipped += 1
                continue
            # Accept either 'body' (comments) or 'selftext' (submissions). Prefer body if present.
            raw_body = obj.get('body')
            if (not raw_body) and ('selftext' in obj):
                raw_body = obj.get('selftext') or ''
            body = raw_body or ''
            empty_flag = 1 if len((body or '').strip()) == 0 else 0
            sc = int(obj.get('score', 0) or 0)
            row = {
                'id': cid,
                'parent_id': obj.get('parent_id'),
                'link_id': obj.get('link_id'),
                'created_utc': int(ts),
                'score': sc,
                'score_bucket': score_bucket(sc),
                'body': body,
                'empty_content': empty_flag,
                'subreddit': sr,
                'author_hash': author_hash(str(obj.get('author','anon')), salt),
                'transition': transition,
                'pre_post': phase
            }
            out.write(json.dumps(row) + '\n')
            kept += 1
    print(f"Normalized {kept} rows (skipped={skipped}) -> {out_path}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transition-id', required=True)
    ap.add_argument('--phase', choices=['pre','post'], required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--author-salt', help='Secret salt (or set AUTHOR_SALT env)')
    args = ap.parse_args()
    salt = args.author_salt or os.getenv('AUTHOR_SALT')
    if not salt:
        raise SystemExit('Must provide --author-salt or set AUTHOR_SALT env')
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    normalize(args.inp, args.out, args.transition_id, args.phase, salt)


if __name__ == '__main__':
    main()
