#!/usr/bin/env python3
"""Prepare figure-ready CSV slices from analysis JSON artifacts.

Emits simple CSVs to plug into plotting scripts (Python/R/JS):
 - confusion_heatmap.csv from agreement.json
 - coverage_per_day_pre.csv and coverage_per_day_post.csv from coverage.json

Usage:
  python pipeline/fig_prep.py --agreement pipeline/outputs/pilot_agreement.json \
      --coverage pipeline/outputs/coverage_pilot.json --out-dir pipeline/outputs/figs
"""
from __future__ import annotations
import argparse, json, os, csv
from pathlib import Path


def load(path: str):
    if not path or not os.path.isfile(path):
        return None
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)


def write_csv(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8',newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    print(f"Fig data -> {path}")


def fig_confusion(agreement, outdir: Path):
    if not agreement:
        return
    matrix = agreement.get('confusion') or {}
    classes = sorted(matrix.keys())
    rows=[['true','pred','count']]
    for t in classes:
        for p, c in (matrix.get(t) or {}).items():
            rows.append([t, p, c])
    write_csv(outdir/'confusion_heatmap.csv', rows[0], rows[1:])


def fig_coverage(coverage, outdir: Path):
    if not coverage:
        return
    for phase in ['pre','post']:
        d = coverage.get(phase)
        if not d:
            continue
        pdc = d.get('per_day_counts',{})
        rows=[['date','count']]
        for day in sorted(pdc.keys()):
            rows.append([day, pdc[day]])
        write_csv(outdir/f'coverage_per_day_{phase}.csv', rows[0], rows[1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agreement')
    ap.add_argument('--coverage')
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    agreement = load(args.agreement)
    coverage = load(args.coverage)

    fig_confusion(agreement, outdir)
    fig_coverage(coverage, outdir)

if __name__ == '__main__':
    main()
