#!/usr/bin/env python3
"""Orchestrate hygiene → sensitive flagging → stratified sampling in one pass.

Stages:
 1. Exact + near-duplicate removal (dedupe_text)
 2. Sensitive content flag log (sensitive_filter)
 3. Stratified sampling (sampler)

Inputs:
  --input-jsonl  Raw (or normalized) JSONL file with fields: id, body, score, transition, phase

Outputs under --out-root:
  deduped.jsonl
  dedupe_report.json
  sensitive_report.json
  sampled/sampled_items.jsonl
  sampled/sampling_manifest.json

Usage:
  python pipeline/orchestrate_hygiene_and_sampling.py \
     --input-jsonl pipeline/data/recent_corpus_merged.jsonl \
     --out-root pipeline/outputs/hygiene_sample --per-stratum 25

NOTE: This script is intentionally transparent; each phase prints results.
"""
from __future__ import annotations
import argparse, pathlib, subprocess, sys


def run(cmd: list[str]):
    print("[RUN]", ' '.join(cmd))
    res = subprocess.run(cmd, text=True)
    if res.returncode != 0:
        print(f"[WARN] Command failed (rc={res.returncode}) continuing: {' '.join(cmd)}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-jsonl', required=True)
    ap.add_argument('--out-root', required=True)
    ap.add_argument('--per-stratum', type=int, default=20)
    ap.add_argument('--near-threshold', type=float, default=0.9)
    ap.add_argument('--no-near', action='store_true')
    args = ap.parse_args()

    root = pathlib.Path(args.out_root)
    root.mkdir(parents=True, exist_ok=True)

    dedup_jsonl = root / 'deduped.jsonl'
    dedupe_report = root / 'dedupe_report.json'
    sensitive_report = root / 'sensitive_report.json'
    sampled_dir = root / 'sampled'
    sampled_dir.mkdir(exist_ok=True)

    # 1. Dedupe
    dedupe_cmd = [sys.executable, 'pipeline/dedupe_text.py', '--in', args.input_jsonl, '--out', str(dedup_jsonl), '--report', str(dedupe_report)]
    if not args.no_near:
        dedupe_cmd += ['--near', '--near-threshold', str(args.near_threshold)]
    run(dedupe_cmd)

    # 2. Sensitive filter
    run([sys.executable, 'pipeline/sensitive_filter.py', '--jsonl', str(dedup_jsonl), '--out', str(sensitive_report)])

    # 3. Stratified sampling (per-stratum counts)
    run([sys.executable, 'pipeline/sampler.py', '--files', str(dedup_jsonl), '--per-stratum', str(args.per_stratum), '--out-dir', str(sampled_dir)])

    print(f"Orchestration complete -> {root}")


if __name__ == '__main__':
    main()
