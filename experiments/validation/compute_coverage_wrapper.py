#!/usr/bin/env python3
"""Wrapper to run normalization + coverage in one step after reconstruction.

Steps:
1. Normalize pre_raw and post_raw using archive_normalize.py (requires AUTHOR_SALT env or flag).
2. Run archive_coverage.py on normalized outputs.
3. Emit a compact TSV summary for Table1 (days_covered, missing_spans count, rows_pre, rows_post).

Usage:
  AUTHOR_SALT=secret python scripts/compute_coverage_wrapper.py --transition-id gpt4_to_4o

Assumes files:
  pipeline/data/gpt4_to_4o_pre_raw.jsonl
  pipeline/data/gpt4_to_4o_post_raw.jsonl

Produces:
  pipeline/data/gpt4_to_4o_pre.jsonl
  pipeline/data/gpt4_to_4o_post.jsonl
  pipeline/data/gpt4_to_4o_coverage.json
  pipeline/outputs/tables/table1_sampling_coverage.tsv  (updated)
"""
from __future__ import annotations
import subprocess, os, json, csv, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.join(ROOT, '..', 'pipeline')
DATA_DIR = os.path.join(PIPELINE_DIR, 'data')
TABLE_DIR = os.path.join(PIPELINE_DIR, 'outputs', 'tables')


def run(cmd: list[str]):
    print('+ ' + ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f'Command failed: {cmd}')
    if r.stderr.strip():
        print(r.stderr.strip())


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--transition-id', required=True)
    ap.add_argument('--author-salt', help='If not provided, AUTHOR_SALT env is used')
    args = ap.parse_args()
    salt = args.author_salt or os.getenv('AUTHOR_SALT')
    if not salt:
        raise SystemExit('Missing author salt (env AUTHOR_SALT or --author-salt)')

    pre_raw = os.path.join(DATA_DIR, f'{args.transition_id}_pre_raw.jsonl')
    post_raw = os.path.join(DATA_DIR, f'{args.transition_id}_post_raw.jsonl')
    if not os.path.exists(pre_raw) or not os.path.exists(post_raw):
        raise SystemExit('Raw window files not found; run reconstruct_window.py first')

    pre_norm = os.path.join(DATA_DIR, f'{args.transition_id}_pre.jsonl')
    post_norm = os.path.join(DATA_DIR, f'{args.transition_id}_post.jsonl')

    # Normalize
    run(['python', os.path.join(PIPELINE_DIR, 'archive_normalize.py'), '--transition-id', args.transition_id, '--phase', 'pre', '--in', pre_raw, '--out', pre_norm, '--author-salt', salt])
    run(['python', os.path.join(PIPELINE_DIR, 'archive_normalize.py'), '--transition-id', args.transition_id, '--phase', 'post', '--in', post_raw, '--out', post_norm, '--author-salt', salt])

    # Coverage
    coverage_json = os.path.join(DATA_DIR, f'{args.transition_id}_coverage.json')
    run(['python', os.path.join(PIPELINE_DIR, 'archive_coverage.py'), '--pre', pre_norm, '--post', post_norm, '--out', coverage_json])

    with open(coverage_json, 'r', encoding='utf-8') as f:
        cov = json.load(f)
    os.makedirs(TABLE_DIR, exist_ok=True)
    table_path = os.path.join(TABLE_DIR, 'table1_sampling_coverage.tsv')
    # Minimal TSV update (overwrite)
    # Append or create
    existing = []
    if os.path.exists(table_path):
        with open(table_path,'r',encoding='utf-8') as f:
            lines=[ln.strip() for ln in f if ln.strip()]
        if lines:
            header=lines[0]
            for ln in lines[1:]:
                parts=ln.split('\t')
                if parts:
                    existing.append(parts)
    header_cols=['transition','rows_pre','rows_post','days_pre','days_post','missing_pre','missing_post']
    row=[
        args.transition_id,
        str(cov['pre']['n_rows']),
        str(cov['post']['n_rows']),
        str(cov['pre']['days_covered']),
        str(cov['post']['days_covered']),
        str(len(cov['pre']['missing_days'])),
        str(len(cov['post']['missing_days']))
    ]
    # Replace if transition exists
    replaced=False
    for i,r in enumerate(existing):
        if r and r[0]==args.transition_id:
            existing[i]=row
            replaced=True
            break
    if not replaced:
        existing.append(row)
    with open(table_path,'w',encoding='utf-8',newline='') as tsv:
        w=csv.writer(tsv, delimiter='\t')
        w.writerow(header_cols)
        for r in existing:
            w.writerow(r)
    print(f'Coverage table updated: {table_path}')

if __name__ == '__main__':
    main()
