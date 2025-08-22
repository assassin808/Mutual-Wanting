#!/usr/bin/env python3
"""Regression scaffold for complaint drift analysis.

Purpose in paper: quantify whether complaint categories (warmth, creativity, safety, etc.) and overall complaint incidence differ across model transition (transition x pre/post interaction) while controlling for engagement proxy (score_bucket). Provides effect size estimates feeding manuscript Results (mutual wanting alignment shifts) and checks for over-time persona drift vs expectation renegotiation.

Robustness additions:
 - Skip models with insufficient minority class (< MIN_CLASS) to avoid separation artifacts.
 - Fallback to L2-penalized logistic regression (scikit-learn) when statsmodels logit fails (singular matrix / perfect separation) capturing coefficients without p-values.
 - Annotate result entries with `estimator` ('statsmodels' or 'sklearn') and class balance.
"""
from __future__ import annotations
import argparse, csv, sys
try:
    import pandas as pd
    import statsmodels.formula.api as smf
except ImportError:  # pragma: no cover
    pd = None
try:
    from sklearn.linear_model import LogisticRegression
except ImportError:  # pragma: no cover
    LogisticRegression = None

PRIMARY_TAGS = [
    'warmth_regression','creativity_regression','helpfulness_regression',
    'hedging_shift','safety_refusal_shift','memory_continuity',
    'verbosity_change','latency_speed','access_limit'
]

MIN_CLASS = 8  # minimum positive AND negative counts required per binary model

def load_df(path: str):
    return pd.read_csv(path)

def _sklearn_fallback(y_col: str, df):
    """Run penalized logistic regression via scikit-learn as fallback.
    Returns dict with coefficients; no p-values available.
    """
    if LogisticRegression is None:
        return {'error': 'sklearn not installed for fallback'}
    # One-hot encode categorical predictors
    X = pd.get_dummies(df[['transition','pre_post','score_bucket']], drop_first=True)
    y = df[y_col].astype(int)
    lr = LogisticRegression(penalty='l2', solver='liblinear', max_iter=1000)
    try:
        lr.fit(X, y)
    except Exception as e:
        return {'error': f'sklearn_fit_failed: {e}'}
    coefs = {f'coef::{col}': float(c) for col, c in zip(X.columns, lr.coef_[0])}
    coefs['intercept'] = float(lr.intercept_[0])
    return {
        'estimator': 'sklearn',
        'n': int(len(y)),
        'positive': int(y.sum()),
        'negative': int((1-y).sum()),
        'params': coefs
    }


def _statsmodels_logit(formula: str, df):
    m = smf.logit(formula, data=df).fit(disp=False)
    return {
        'estimator': 'statsmodels',
        'n': int(df.shape[0]),
        'params': m.params.to_dict(),
        'pvalues': m.pvalues.to_dict(),
        'aic': m.aic
    }


def run_models(df):
    results = {}
    # Omnibus complaint vs other
    df['any_complaint'] = df['primary_tag'].apply(lambda x: 0 if (pd.isna(x) or x=='') else 1)
    pos = int(df['any_complaint'].sum())
    neg = int(df.shape[0] - pos)
    if min(pos, neg) < MIN_CLASS:
        results['any_complaint'] = {'skipped': 'insufficient_class_counts', 'positive': pos, 'negative': neg}
    else:
        try:
            results['any_complaint'] = _statsmodels_logit("any_complaint ~ C(transition) * C(pre_post) + C(score_bucket)", df)
        except Exception as e:
            fb = _sklearn_fallback('any_complaint', df)
            fb['fallback_error'] = str(e) if 'error' in fb else None
            results['any_complaint'] = fb

    for tag in PRIMARY_TAGS:
        bin_col = tag + '_bin'
        df[bin_col] = (df['primary_tag'] == tag).astype(int)
        pos = int(df[bin_col].sum())
        neg = int(df.shape[0] - pos)
        if min(pos, neg) < MIN_CLASS:
            results[tag] = {'skipped': 'insufficient_class_counts', 'positive': pos, 'negative': neg}
            continue
        formula = f"{bin_col} ~ C(transition) * C(pre_post) + C(score_bucket)"
        try:
            res = _statsmodels_logit(formula, df)
            res['positive'] = pos
            res['negative'] = neg
            results[tag] = res
        except Exception as e:
            fb = _sklearn_fallback(bin_col, df)
            fb['fallback_error'] = str(e) if 'error' in fb else None
            results[tag] = fb
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
