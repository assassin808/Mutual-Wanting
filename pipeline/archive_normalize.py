#!/usr/bin/env python3
"""Normalize raw Reddit JSONL dumps into unified schema with privacy hashing.

Input: raw JSONL lines with at minimum fields:
 - id (or name)
 - author (will be hashed)
 - body
 - created_utc (epoch seconds)
 - score
 - subreddit
 - parent_id / link_id (optional)

Adds required fields and attaches transition & phase metadata provided via CLI.

Output schema JSONL (one object per line):
  id, subreddit, author_hash, created_utc, score, body, parent_id, link_id, transition, phase

Environment:
  AUTHOR_SALT must be set (non-empty) to derive author_hash = sha256(salt + author.lower()).

Usage:
  AUTHOR_SALT=your_salt python pipeline/archive_normalize.py \
      --transition gpt4_to_4o --phase pre --out data/normalized/gpt4_to_4o_pre.jsonl raw/*.jsonl
"""
from __future__ import annotations
import os, json, hashlib, argparse, pathlib, sys

REQUIRED = ['body','created_utc','score','subreddit']

def author_hash(author: str, salt: str):
    if author is None:
        author = ''
    digest = hashlib.sha256((salt + author.lower()).encode('utf-8')).hexdigest()
    return digest[:32]  # truncate for brevity

def normalize_line(obj, transition, phase, salt):
    # Basic validation
    for f in REQUIRED:
        if f not in obj:
            return None
    cid = obj.get('id') or obj.get('name')
    if not cid:
        return None
    try:
        created = int(obj['created_utc'])
    except Exception:
        return None
    try:
        score = int(obj['score'])
    except Exception:
        score = 0
    return {
        'id': cid,
        'subreddit': obj.get('subreddit',''),
        'author_hash': author_hash(obj.get('author'), salt),
        'created_utc': created,
        'score': score,
        'body': obj.get('body',''),
        'parent_id': obj.get('parent_id'),
        'link_id': obj.get('link_id'),
        'transition': transition,
        'phase': phase
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inputs', nargs='+', help='Raw JSONL file(s)')
    ap.add_argument('--transition', required=True)
    ap.add_argument('--phase', required=True, choices=['pre','post'])
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    salt = os.getenv('AUTHOR_SALT')
    if not salt:
        print('ERROR: AUTHOR_SALT env var required', file=sys.stderr)
        sys.exit(2)

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_in = 0
    n_out = 0
    with open(out_path,'w',encoding='utf-8') as w:
        for ip in args.inputs:
            with open(ip,'r',encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if not line.strip():
                        continue
                    n_in += 1
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    norm = normalize_line(obj, args.transition, args.phase, salt)
                    if not norm:
                        continue
                    w.write(json.dumps(norm, ensure_ascii=False) + '\n')
                    n_out += 1
    print(f"Normalized {n_out}/{n_in} lines -> {out_path}")

if __name__ == '__main__':
    main()
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
            body = obj.get('body') or ''
            sc = int(obj.get('score', 0) or 0)
            row = {
                'id': cid,
                'parent_id': obj.get('parent_id'),
                'link_id': obj.get('link_id'),
                'created_utc': int(ts),
                'score': sc,
                'score_bucket': score_bucket(sc),
                'body': body,
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
