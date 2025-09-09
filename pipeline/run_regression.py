#!/usr/bin/env python3
"""Fit logistic models per target: target ~ pre_post * transition + subreddit + score_bucket (+ optional cluster).

Requires a dataset CSV with columns: id, pre_post, transition, subreddit, score_bucket, feature columns, and target columns.
"""
import argparse, json, os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset-csv', required=True)
    ap.add_argument('--targets', nargs='+', default=['complaint'])
    ap.add_argument('--min-class', type=int, default=8)
    ap.add_argument('--out-json', required=True)
    args = ap.parse_args()

    if not os.path.exists(args.dataset_csv):
        print('Dataset not found; skipping regression.')
        return
    df = pd.read_csv(args.dataset_csv)

    # Identify columns
    cat_cols = [c for c in ['pre_post','transition','subreddit','score_bucket'] if c in df.columns]
    num_cols = [c for c in df.columns if c not in (['id'] + cat_cols + args.targets + ['primary_tag'])]

    results = { 'targets': {}, 'n_rows': int(len(df)) }
    for t in args.targets:
        if t not in df.columns:
            continue
        # Drop missing targets
        sub = df.dropna(subset=[t]).copy()
        # Ensure binary 0/1
        sub[t] = sub[t].map(lambda x: 1 if str(x).strip().lower() in ('1','true','yes','y') else 0)
        cls_counts = sub[t].value_counts().to_dict()
        if min(cls_counts.values()) < args.min_class:
            results['targets'][t] = {'skipped': True, 'reason': f'class count < {args.min_class}', 'counts': cls_counts}
            continue
        pre = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
                ('num', 'passthrough', num_cols),
            ]
        )
        model = LogisticRegression(max_iter=200, solver='lbfgs')
        pipe = Pipeline(steps=[('pre', pre), ('clf', model)])
        X = sub[cat_cols + num_cols]
        y = sub[t]
        pipe.fit(X, y)
        yhat = pipe.predict(X)
        report = classification_report(y, yhat, output_dict=True)
        results['targets'][t] = {
            'counts': cls_counts,
            'train_report': report,
            'note': 'Interaction OR extraction TBD once consensus labels available.'
        }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Regression results -> {args.out_json}")


if __name__ == '__main__':
    main()
