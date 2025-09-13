#!/usr/bin/env python3
"""Stratified sampler with enrichment vs baseline allocation.

Input: One or more normalized JSONL files (fields: id, body, score, created_utc, transition, phase).

Outputs:
 - sampled_items.jsonl
 - sampling_manifest.json (counts & shortfalls)

No synthetic data is generated; this only subsamples provided authentic rows.
"""
from __future__ import annotations
import argparse, json, random, re, pathlib
from collections import defaultdict

LEXICON = [
    r"complaint", r"broken", r"worse", r"degrad", r"slow", r"error", r"hallucinat", r"unsafe", r"rude", r"unhelpful", r"jailbroken"
]

def score_bucket(score: int):
    if score < 10:
        return 'lo'
    if score < 50:
        return 'mid'
    return 'hi'

def keyword_hits(text: str):
    hits = []
    lower = text.lower()
    for pat in LEXICON:
        if re.search(pat, lower):
            hits.append(pat)
    return hits

def load_rows(paths):
    for p in paths:
        with open(p,'r',encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                row['source_file'] = p
                yield row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--per-stratum', type=int, default=20, help='Target total (enriched + baseline) per (transition,phase,bucket).')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    random.seed(args.seed)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    strata = defaultdict(list)
    for row in load_rows(args.files):
        if 'transition' not in row or 'phase' not in row or 'score' not in row or 'body' not in row:
            continue
        sb = score_bucket(int(row['score']))
        hits = keyword_hits(row['body'])
        row['score_bucket'] = sb
        row['enriched'] = bool(hits)
        row['keyword_hits'] = hits
        key = (row['transition'], row['phase'], sb)
        strata[key].append(row)

    selected = []
    manifest = { 'strata': [] }
    for key, rows in strata.items():
        t, phase, bucket = key
        enriched_rows = [r for r in rows if r['enriched']]
        baseline_rows = [r for r in rows if not r['enriched']]
        target_total = args.per_stratum
        target_enriched = target_total // 2
        random.shuffle(enriched_rows)
        random.shuffle(baseline_rows)
        chosen_enriched = enriched_rows[:target_enriched]
        remaining_slots = target_total - len(chosen_enriched)
        chosen_baseline = baseline_rows[:remaining_slots]
        shortfall_enriched = max(0, target_enriched - len(chosen_enriched))
        shortfall_total = target_total - (len(chosen_enriched) + len(chosen_baseline))
        block = {
            'transition': t,
            'phase': phase,
            'score_bucket': bucket,
            'n_pool': len(rows),
            'n_pool_enriched': len(enriched_rows),
            'n_pool_baseline': len(baseline_rows),
            'selected_enriched': len(chosen_enriched),
            'selected_baseline': len(chosen_baseline),
            'shortfall_enriched': shortfall_enriched,
            'shortfall_total': shortfall_total
        }
        manifest['strata'].append(block)
        selected.extend(chosen_enriched + chosen_baseline)

    # Write outputs
    out_sample = out_dir / 'sampled_items.jsonl'
    with open(out_sample,'w',encoding='utf-8') as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(out_dir / 'sampling_manifest.json','w',encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"Sample -> {out_sample} (n={len(selected)})")
    print(f"Manifest -> {out_dir / 'sampling_manifest.json'}")

if __name__ == '__main__':
    main()
