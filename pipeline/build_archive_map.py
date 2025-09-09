#!/usr/bin/env python3
"""Construct archive_map.json from integrity report + transitions plan.

Inputs:
  --integrity pipeline/data/archive_integrity_report.json
  --plan pipeline/archive_plan.json (contains transition windows)

Output:
  archive_map.json with entries: {file, sha256, n_lines, first_created_utc, last_created_utc, transition_label (if overlaps)}

Logic:
  - For each file, assign transition label if its time span overlaps any window (pre/post) in plan.
  - Windows in plan: each {name, pre_start, pre_end, post_start, post_end} or similar (fallback keys derived if missing).
  - Overlap priority: first matching window; if spans both pre & post, tag 'spans_multiple'.

Limitations: simplistic overlap; assumes non-overlapping transition windows.
"""
from __future__ import annotations
import argparse, json, pathlib

def load_json(path):
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

def in_range(ts, start, end):
    return (start is None or ts >= start) and (end is None or ts <= end)

def label_span(first_ts, last_ts, plan_windows):
    for w in plan_windows:
        pre_start = w.get('pre_start') or w.get('pre_window_start')
        pre_end = w.get('pre_end') or w.get('pre_window_end')
        post_start = w.get('post_start') or w.get('post_window_start')
        post_end = w.get('post_end') or w.get('post_window_end')
        name = w.get('name') or w.get('transition')
        if first_ts is None or last_ts is None:
            continue
        overlaps_pre = pre_start and pre_end and not (last_ts < pre_start or first_ts > pre_end)
        overlaps_post = post_start and post_end and not (last_ts < post_start or first_ts > post_end)
        if overlaps_pre and overlaps_post:
            return f"{name}:spans_pre_post"
        if overlaps_pre:
            return f"{name}:pre"
        if overlaps_post:
            return f"{name}:post"
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--integrity', required=True)
    ap.add_argument('--plan', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    integ = load_json(args.integrity)
    plan = load_json(args.plan)
    plan_windows = plan.get('transitions') or plan.get('windows') or plan

    files = integ.get('files') or []
    out_entries = []
    for f in files:
        first_ts = f.get('first_created_utc') or f.get('first_ts')
        last_ts = f.get('last_created_utc') or f.get('last_ts')
        label = label_span(first_ts, last_ts, plan_windows)
        out_entries.append({
            'file': f.get('path') or f.get('file'),
            'sha256': f.get('sha256'),
            'n_lines': f.get('n_lines') or f.get('line_count'),
            'first_created_utc': first_ts,
            'last_created_utc': last_ts,
            'transition_label': label
        })
    out_obj = {'entries': out_entries}
    with open(args.out,'w',encoding='utf-8') as fp:
        json.dump(out_obj, fp, indent=2)
    print(f"Archive map -> {args.out} ({len(out_entries)} files)")

if __name__ == '__main__':
    main()
