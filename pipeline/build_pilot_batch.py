#!/usr/bin/env python3
"""Construct a 60-item pilot annotation batch from `recent_corpus_merged.jsonl`.

Goals (Paper Link):
  * Rapidly stress-test complaint persona taxonomy on *real, contemporaneous* data.
  * Produce early inter-annotator reliability estimate (kappa) to refine guidelines.
  * Empirically ground narrative section (Methods: "Pilot Calibration Phase") before historical windows arrive.

Selection Principles:
  - Balance across core subreddits.
  - Balance score buckets (hi/mid/lo) for diversity of visibility contexts.
  - Enrich for probable complaints via complaint_focus_lexicon keyword hits while retaining a background slice.

Outputs:
  pipeline/data/pilot_batch.csv (rows with placeholder annotation columns)
  pipeline/data/pilot_selection_manifest.json (counts & enrichment stats)

Usage:
  python pipeline/build_pilot_batch.py \
    --merged pipeline/data/recent_corpus_merged.jsonl \
    --lexicon pipeline/complaint_focus_lexicon.txt \
    --out-dir pipeline/data --total 60 --seed 123
"""
from __future__ import annotations
import argparse, json, random, csv, pathlib
from typing import List, Dict, Any

CORE_SUBS = ["ChatGPT","OpenAI","LocalLLaMA","MachineLearning","PromptEngineering"]
BUCKETS = ["hi","mid","lo"]


def load_lexicon(path: str) -> List[str]:
    terms = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'): continue
            terms.append(line.lower())
    return terms


def iter_jsonl(path: str):
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def enrich_flag(row: Dict[str,Any], terms) -> bool:
    blob = f"{row.get('title','')}\n{row.get('selftext','')}".lower()
    return any(t in blob for t in terms)


def select(rows: List[Dict[str,Any]], total: int, seed: int, lex_terms: List[str]):
    rng = random.Random(seed)
    # Partition by (sub, bucket)
    grid: Dict[str, Dict[str, List[Dict[str,Any]]]] = {s:{b:[] for b in BUCKETS} for s in CORE_SUBS}
    for r in rows:
        sub = r.get('source_sub')
        if sub not in grid: continue
        b = r.get('score_bucket')
        if b not in grid[sub]: continue
        r['_enriched'] = enrich_flag(r, lex_terms)
        grid[sub][b].append(r)
    # Target equal allocation: total / (len(subs)*len(buckets))
    slots_per_cell = max(1, total // (len(CORE_SUBS)*len(BUCKETS)))
    chosen = []
    stats = { 'cells': {}, 'total_target': total }
    for sub in CORE_SUBS:
        stats['cells'][sub] = {}
        for b in BUCKETS:
            cell = grid[sub][b]
            rng.shuffle(cell)
            # Enrichment: try to take half enriched if possible
            enriched = [r for r in cell if r['_enriched']]
            plain = [r for r in cell if not r['_enriched']]
            half = slots_per_cell // 2
            pick = []
            if enriched:
                pick.extend(enriched[:half])
            if len(pick) < slots_per_cell:
                needed = slots_per_cell - len(pick)
                pick.extend(plain[:needed])
            # If still under (cell sparse) top up from any remaining
            if len(pick) < slots_per_cell:
                leftovers = enriched[half:] + plain[len(pick)-half:]
                rng.shuffle(leftovers)
                pick.extend(leftovers[:slots_per_cell-len(pick)])
            stats['cells'][sub][b] = {
                'selected': len(pick),
                'enriched_selected': sum(1 for r in pick if r['_enriched']),
                'available': len(cell),
                'available_enriched': len(enriched)
            }
            chosen.extend(pick)
    # If under total due to sparsity, fill from remainder pool
    if len(chosen) < total:
        remainder = [r for sub in CORE_SUBS for b in BUCKETS for r in grid[sub][b] if r not in chosen]
        rng.shuffle(remainder)
        chosen.extend(remainder[:total-len(chosen)])
    # Truncate if slight over
    chosen = chosen[:total]
    return chosen, stats


def build(args):
    lex_terms = load_lexicon(args.lexicon)
    rows = list(iter_jsonl(args.merged))
    selected, stats = select(rows, args.total, args.seed, lex_terms)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Write batch CSV with annotation columns
    csv_path = out_dir / 'pilot_batch.csv'
    fieldnames = ['id','source_sub','score','score_bucket','created_utc','title','selftext','enriched_flag','primary_tag','secondary_flags','annotator_id']
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in selected:
            w.writerow({
                'id': r.get('id',''),
                'source_sub': r.get('source_sub',''),
                'score': r.get('score',''),
                'score_bucket': r.get('score_bucket',''),
                'created_utc': r.get('created_utc',''),
                'title': (r.get('title') or '').replace('\n',' ').strip(),
                'selftext': (r.get('selftext') or '').replace('\n',' ').strip(),
                'enriched_flag': int(r.get('_enriched', False)),
                'primary_tag': '',
                'secondary_flags': '',
                'annotator_id': ''
            })
    manifest_path = out_dir / 'pilot_selection_manifest.json'
    with manifest_path.open('w',encoding='utf-8') as f:
        json.dump({
            'total_selected': len(selected),
            'target_total': args.total,
            'cells': stats['cells'],
            'lexicon_terms': len(lex_terms),
            'seed': args.seed
        }, f, indent=2)
    print(f"Pilot batch {len(selected)} rows -> {csv_path}")
    print(f"Manifest -> {manifest_path}")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--merged', required=True)
    ap.add_argument('--lexicon', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--total', type=int, default=60)
    ap.add_argument('--seed', type=int, default=123)
    return ap.parse_args()

if __name__ == '__main__':
    build(parse_args())
