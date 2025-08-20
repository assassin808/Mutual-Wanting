#!/usr/bin/env python3
"""Regression scaffold (placeholder) once labels available.
Uses statsmodels if installed; otherwise prints guidance.
"""
from __future__ import annotations
import argparse, csv, sys
try:
    import pandas as pd
    import statsmodels.formula.api as smf
except ImportError:
    pd = None

PRIMARY_TAGS = [
    "WARMTH_LOSS","CREATIVITY_DROP","HELPFULNESS_REGRESSION","HEDGING_SHIFT",
    "SAFETY_REFUSAL_SHIFT","MEMORY_CONTINUITY","VERBOSITY_CHANGE","LATENCY_SPEED","ACCESS_LIMITS"
]

def load_df(path: str):
    return pd.read_csv(path)

def run_models(df):
    results = {}
    for tag in PRIMARY_TAGS:
        df[tag + '_bin'] = (df['primary_tag'] == tag).astype(int)
        formula = f"{tag}_bin ~ C(transition) * C(pre_post) + C(score_bucket)"
        try:
            m = smf.logit(formula, data=df).fit(disp=False)
            results[tag] = {
                'n': int(df.shape[0]),
                'params': m.params.to_dict(),
                'pvalues': m.pvalues.to_dict(),
                'aic': m.aic
            }
        except Exception as e:
            results[tag] = {'error': str(e)}
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--labeled', required=True, help='CSV with final labels')
    ap.add_argument('--out', required=True, help='JSON output path')
    args = ap.parse_args()
    if pd is None:
        print("statsmodels/pandas not installed. Install to run regressions.")
        sys.exit(0)
    df = load_df(args.labeled)
    res = run_models(df)
    import json
    with open(args.out,'w') as f:
        json.dump(res, f, indent=2)
    print(f"Wrote regression results to {args.out}")

if __name__ == '__main__':
    main()
