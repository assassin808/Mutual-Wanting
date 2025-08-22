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
    'warmth_regression','creativity_regression','helpfulness_regression',
    'hedging_shift','safety_refusal_shift','memory_continuity',
    'verbosity_change','latency_speed','access_limit'
]

def load_df(path: str):
    return pd.read_csv(path)

def run_models(df):
    results = {}
    # Omnibus complaint vs other
    df['any_complaint'] = df['primary_tag'].apply(lambda x: 0 if (pd.isna(x) or x=='') else 1)
    try:
        m_any = smf.logit("any_complaint ~ C(transition) * C(pre_post) + C(score_bucket)", data=df).fit(disp=False)
        results['any_complaint'] = {
            'n': int(df.shape[0]),
            'params': m_any.params.to_dict(),
            'pvalues': m_any.pvalues.to_dict(),
            'aic': m_any.aic
        }
    except Exception as e:
        results['any_complaint'] = {'error': str(e)}

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
