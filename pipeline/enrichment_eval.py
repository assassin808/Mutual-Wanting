#!/usr/bin/env python3
"""Evaluate enrichment (keyword) sampling precision & recall against a baseline-labeled subset.

Purpose (paper linkage): Quantify trade-off between efficiency (precision of complaint-yielding enriched sample) and coverage (recall of true complaint instances) so reported complaint drift signals are not artifacts of biased sampling. Outputs metrics inserted into Methods (Sampling Adequacy) and Limitations.

Inputs:
  --enriched-labeled : CSV produced from enriched sampling & labeled (primary_tag present when complaint)
  --baseline-labeled : CSV from baseline (random) sampling & labeled

We treat any non-empty primary_tag as a complaint instance.

Outputs JSON with:
  precision_enriched = complaints_enriched / total_enriched
  prevalence_baseline = complaints_baseline / total_baseline
  relative_risk = (precision_enriched / prevalence_baseline)
  recall_estimate = complaints_enriched / (complaints_enriched + missed_estimate)
Where missed_estimate derives from baseline prevalence extrapolated to enriched sample size (assumes baseline unbiased for prevalence):
  expected_complaints_in_enriched_if_random = prevalence_baseline * total_enriched
  missed_estimate = max(0, expected_random - complaints_enriched)  (if enrichment under-represents; else 0)
Also provides Wilson 95% CI for proportions.
"""
from __future__ import annotations
import csv, argparse, json, math

def load_rows(path: str):
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def count_complaints(rows):
    total = len(rows)
    complaints = sum(1 for r in rows if (r.get('primary_tag') or '').strip())
    return total, complaints

def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0,0.0,0.0)
    denom = 1 + z**2/n
    center = (p + z**2/(2*n))/denom
    margin = z*math.sqrt((p*(1-p)/n) + (z**2/(4*n**2)))/denom
    return p, max(0.0, center-margin), min(1.0, center+margin)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--enriched-labeled', required=True)
    ap.add_argument('--baseline-labeled', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    enr = load_rows(args.enriched_labeled)
    base = load_rows(args.baseline_labeled)
    n_enr, c_enr = count_complaints(enr)
    n_base, c_base = count_complaints(base)

    prec_enr = c_enr / n_enr if n_enr else 0.0
    prev_base = c_base / n_base if n_base else 0.0
    rr = (prec_enr / prev_base) if prev_base > 0 else None
    expected_rand = prev_base * n_enr
    missed_est = max(0.0, expected_rand - c_enr)
    # If enrichment over-samples (prec_enr > prev_base) treat recall_estimate as 1.0 (no evidence of missed cases under simplified assumption)
    if prec_enr >= prev_base:
        recall_est = 1.0
    else:
        recall_est = c_enr / (c_enr + missed_est) if (c_enr + missed_est) > 0 else 0.0

    p_enr_triplet = wilson(prec_enr, n_enr)
    p_base_triplet = wilson(prev_base, n_base)

    out = {
        'n_enriched': n_enr,
        'complaints_enriched': c_enr,
        'precision_enriched': {
            'point': p_enr_triplet[0], 'wilson_low': p_enr_triplet[1], 'wilson_high': p_enr_triplet[2]
        },
        'n_baseline': n_base,
        'complaints_baseline': c_base,
        'prevalence_baseline': {
            'point': p_base_triplet[0], 'wilson_low': p_base_triplet[1], 'wilson_high': p_base_triplet[2]
        },
        'relative_risk_enrichment': rr,
        'recall_estimate_under_random_prevalence': recall_est,
        'expected_complaints_if_random_in_enriched': expected_rand,
        'missed_estimate': missed_est,
        'assumptions': [
            'Baseline sample approximates unbiased prevalence.',
            'Complaint labeling consistent across enriched and baseline sets.',
            'Recall estimate simplified: if enrichment precision exceeds baseline prevalence we assume near-complete coverage.'
        ]
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Enrichment evaluation -> {args.out}")

if __name__ == '__main__':
    main()
