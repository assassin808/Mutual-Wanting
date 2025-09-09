#!/usr/bin/env python3
"""Produce Table1: Sampling & Coverage summary (TSV).

Inputs:
  --coverage JSON (e.g., pipeline/outputs/coverage_pilot.json)
  --sampling-manifest JSON (optional; if missing, outputs coverage-only rows)

Output:
  --out-tsv path to write a small TSV with key stats
"""
import argparse, json, os, sys


def load_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--coverage', required=True)
    ap.add_argument('--sampling-manifest', help='Optional manifest JSON from sampler')
    ap.add_argument('--out-tsv', required=True)
    args = ap.parse_args()

    cov = load_json(args.coverage) or {}
    man = load_json(args.sampling_manifest) or {}

    cov_rows = cov.get('per_day', []) if isinstance(cov, dict) else []
    days_covered = len(cov_rows)
    missing_spans = (cov.get('missing_spans') or []) if isinstance(cov, dict) else []
    n_missing_spans = len(missing_spans)

    # Try to extract sampled counts if available
    sampled_total = None
    enriched_n = None
    baseline_n = None
    if isinstance(man, dict):
        sampled_total = man.get('total_sampled')
        if isinstance(man.get('strata_counts'), dict):
            # optional detail
            pass
        enriched_n = man.get('enriched_n')
        baseline_n = man.get('baseline_n')

    lines = []
    lines.append("metric\tvalue")
    lines.append(f"days_covered\t{days_covered}")
    lines.append(f"missing_spans\t{n_missing_spans}")
    if sampled_total is not None:
        lines.append(f"sampled_total\t{sampled_total}")
    if enriched_n is not None:
        lines.append(f"sampled_enriched\t{enriched_n}")
    if baseline_n is not None:
        lines.append(f"sampled_baseline\t{baseline_n}")

    os.makedirs(os.path.dirname(args.out_tsv), exist_ok=True)
    with open(args.out_tsv, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    print(f"Table1 -> {args.out_tsv}")


if __name__ == '__main__':
    main()
