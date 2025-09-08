#!/usr/bin/env python3
"""Derive pre/post archive windows from transitions.yaml.

Produces JSON with, for each transition:
  - transition
  - release_date
  - pre: {start, end}
  - post: {start, end}

Default window sizes:
  PRE_DAYS = 14 (ending the day before release)
  POST_DAYS = 28 (starting the day of release)

Adjust via CLI flags if needed.

Usage:
  python pipeline/plan_archives.py --transitions pipeline/transitions.yaml --out pipeline/archive_plan.json
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import pathlib
import yaml


def load_transitions(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise SystemExit("transitions.yaml must be a list of dicts")
    out = []
    for row in data:
        try:
            name = row['name']
            date = dt.date.fromisoformat(str(row['date']))
        except Exception as e:
            raise SystemExit(f"Invalid row {row}: {e}")
        out.append({
            'name': name,
            'date': date,
            'description': row.get('description','')
        })
    return out


def build_plan(transitions, pre_days: int, post_days: int):
    plan = []
    for t in transitions:
        release = t['date']
        pre_start = release - dt.timedelta(days=pre_days)
        pre_end = release - dt.timedelta(days=1)
        post_start = release
        post_end = release + dt.timedelta(days=post_days-1)
        plan.append({
            'transition': t['name'],
            'release_date': str(release),
            'description': t['description'],
            'pre': {
                'start': str(pre_start),
                'end': str(pre_end)
            },
            'post': {
                'start': str(post_start),
                'end': str(post_end)
            }
        })
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--pre-days', type=int, default=14)
    ap.add_argument('--post-days', type=int, default=28)
    args = ap.parse_args()

    transitions = load_transitions(args.transitions)
    plan = build_plan(transitions, args.pre_days, args.post_days)
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'windows': plan}, f, indent=2)
    print(f"Archive plan -> {out_path}")


if __name__ == '__main__':
    main()
