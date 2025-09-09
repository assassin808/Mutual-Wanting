#!/usr/bin/env python3
"""Build modeling dataset by merging features with consensus labels.

Inputs:
  --features-csv path to features (must include 'id')
  --labels-csv path to consensus labels (must include 'id' and target cols)
  --out-csv output dataset path
  --targets list of target columns (default major tags)
"""
import argparse, os, sys
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--features-csv', required=True)
    ap.add_argument('--labels-csv', required=True)
    ap.add_argument('--out-csv', required=True)
    ap.add_argument('--targets', nargs='+', default=['warmth','creativity','helpfulness','hedging','complaint'])
    args = ap.parse_args()

    if not os.path.exists(args.features_csv) or not os.path.exists(args.labels_csv):
        print('Missing input files; aborting dataset build.')
        sys.exit(0)

    feat = pd.read_csv(args.features_csv)
    lab = pd.read_csv(args.labels_csv)
    if 'id' not in feat.columns or 'id' not in lab.columns:
        raise SystemExit('Both CSVs must include an id column')

    keep_cols = ['id'] + [c for c in lab.columns if c in set(['primary_tag'] + args.targets)]
    lab_small = lab[keep_cols].copy()
    df = feat.merge(lab_small, on='id', how='inner')

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(f"Model dataset -> {args.out_csv} (rows={len(df)})")


if __name__ == '__main__':
    main()
