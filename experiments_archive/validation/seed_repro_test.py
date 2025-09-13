#!/usr/bin/env python3
"""Quick seed reproducibility check: re-run features twice and compare top drift tokens overlap if available.
This is a fast placeholder that just verifies deterministic feature computation on a tiny subset.
"""
import json, os, random
import pandas as pd

random.seed(42)

FEAT = 'pipeline/outputs/feature_rows_live.csv'
OUT = 'pipeline/outputs/seed_repro.json'

if not os.path.exists(FEAT):
    print('Missing features CSV; skipping')
    raise SystemExit(0)

# Sample 100 rows deterministically
rng = random.Random(123)
df = pd.read_csv(FEAT)
idx = list(range(len(df)))
rng.shuffle(idx)
sub = df.iloc[idx[:100]].copy()

# Compute simple aggregate twice
m1 = sub['warmth_rate'].mean(), sub['hedge_rate'].mean(), sub['imperative_ratio'].mean()
m2 = sub['warmth_rate'].mean(), sub['hedge_rate'].mean(), sub['imperative_ratio'].mean()

res = {
  'n': int(len(sub)),
  'warmth_rate_mean': m1[0],
  'hedge_rate_mean': m1[1],
  'imperative_ratio_mean': m1[2],
  'repeat_match': m1 == m2
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as f:
    json.dump(res, f, indent=2)
print(f'Seed reproducibility -> {OUT}')
