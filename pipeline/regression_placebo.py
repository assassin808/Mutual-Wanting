#!/usr/bin/env python3
"""Placebo test for regression interaction effects.

Shuffles the pre_post label within each transition to break true temporal structure.
Runs the regression scaffold and records distribution of interaction coefficients
across multiple permutations for the 'any_complaint' model.

Usage:
  python pipeline/regression_placebo.py --labeled pipeline/outputs/features_rows.csv --iters 200 --out pipeline/outputs/regression_placebo.json
"""
from __future__ import annotations
import argparse, json, random
import pandas as pd
from regression_skeleton import run_models

TARGET_OUTCOME = 'any_complaint'
INTERACTION_KEY_HINT = ':'  # look for first param name containing ':'


def extract_interaction(result):
    params = result.get('params',{})
    for k,v in params.items():
        if INTERACTION_KEY_HINT in k and isinstance(v,(int,float)):
            return k, v
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--labeled', required=True)
    ap.add_argument('--iters', type=int, default=200)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    df = pd.read_csv(args.labeled)
    if 'pre_post' not in df.columns or 'transition' not in df.columns:
        raise SystemExit('Expected columns pre_post and transition in labeled CSV.')

    coefs=[]
    for i in range(args.iters):
        df_shuff = df.copy()
        # shuffle pre_post within each transition group
        shuffled=[]
        for trans, grp in df_shuff.groupby('transition'):
            vals = grp['pre_post'].tolist()
            random.shuffle(vals)
            shuffled.extend(vals)
        df_shuff['pre_post'] = shuffled
        res = run_models(df_shuff)
        outcome_res = res.get(TARGET_OUTCOME, {})
        k, coef = extract_interaction(outcome_res)
        if coef is not None:
            coefs.append(coef)
    summary = {
        'n_iters': args.iters,
        'interaction_coef_samples': coefs,
        'mean': sum(coefs)/len(coefs) if coefs else None,
        'std': (sum((c-(sum(coefs)/len(coefs)))**2 for c in coefs)/len(coefs))**0.5 if coefs else None
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(summary,f,indent=2)
    print(f"Placebo test -> {args.out} ({len(coefs)} interaction samples)")

if __name__=='__main__':
    main()
