#!/usr/bin/env python3
"""Sampling script with stratification.
Groups by (transition, pre_post, score_bucket) and samples proportionally.
"""
from __future__ import annotations
import json, csv, random, argparse, math, time, re, os
from typing import List, Dict, Any, Tuple, DefaultDict
from collections import defaultdict

PRIMARY_FIELDS = ["comment_id","thread_id","parent_id","created_utc","score","score_bucket","body","transition","pre_post","enriched","source_file"]

WORD_RE = re.compile(r"\b\w+\b")

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def group(rows: List[Dict[str,Any]]) -> DefaultDict[Tuple[str,str,str], List[Dict[str,Any]]]:
    buckets = defaultdict(list)
    for r in rows:
        key = (r.get("transition"), r.get("pre_post"), r.get("score_bucket"))
        if None in key:
            continue
        buckets[key].append(r)
    return buckets


def stratified_sample(rows: List[Dict[str,Any]], n: int, enrichment_frac: float) -> List[Dict[str,Any]]:
    buckets = group(rows)
    total = sum(len(v) for v in buckets.values()) or 1
    out: List[Dict[str,Any]] = []
    for k, items in buckets.items():
        share = len(items) / total
        alloc = min(len(items), max(1, int(round(share * n))))
        if alloc <= 0:
            continue
        enriched = [r for r in items if r.get('enriched') == 1]
        baseline = [r for r in items if r.get('enriched') != 1]
        target_enr = int(round(alloc * enrichment_frac))
        take_enr = min(target_enr, len(enriched))
        take_base = alloc - take_enr
        if take_base > len(baseline):
            # backfill from remaining enriched if baseline shortage
            deficit = take_base - len(baseline)
            take_base = len(baseline)
            extra_enr = min(deficit, len(enriched) - take_enr)
            take_enr += extra_enr
        chosen = []
        if take_enr > 0:
            chosen.extend(random.sample(enriched, take_enr))
        if take_base > 0:
            chosen.extend(random.sample(baseline, take_base))
        out.extend(chosen)
    random.shuffle(out)
    return out[:n]


def write_csv(path: str, rows: List[Dict[str,Any]]):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        header = PRIMARY_FIELDS + ["primary_tag","secondary_flags","annotator_id"]
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(k,"") for k in PRIMARY_FIELDS] + ["", "", ""])  # blanks for labeling


def assign_score_bucket(score: int, lo_lt: int, mid_lt: int) -> str:
    if score < lo_lt:
        return 'lo'
    if score < mid_lt:
        return 'mid'
    return 'hi'


def mark_enrichment(row: Dict[str,Any], keywords: List[str]) -> int:
    body = (row.get('body') or '').lower()
    tokens = set(WORD_RE.findall(body))
    for kw in keywords:
        if kw in tokens:
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', nargs='+', required=True, help='Raw JSONL files')
    ap.add_argument('--out', required=True, help='Output CSV for labeling')
    ap.add_argument('--n', type=int, default=600, help='Target total sample size')
    ap.add_argument('--enrichment-fraction', type=float, default=0.5, help='Target fraction of each stratum from enrichment hits')
    ap.add_argument('--keywords', help='Path to keyword file for enrichment (one per line)')
    ap.add_argument('--score-thresholds', nargs=2, type=int, metavar=('LO_LT','MID_LT'), help='Override default static thresholds (<lo_lt, <mid_lt)')
    ap.add_argument('--manifest-json', help='Optional manifest JSON output path')
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    lo_lt, mid_lt = 10, 50
    if args.score_thresholds:
        lo_lt, mid_lt = args.score_thresholds

    keywords: List[str] = []
    if args.keywords:
        with open(args.keywords,'r',encoding='utf-8') as f:
            keywords = [ln.strip().lower() for ln in f if ln.strip()]

    all_rows = []
    for p in args.raw:
        for r in load_jsonl(p):
            r['source_file'] = os.path.basename(p)
            s = int(r.get('score',0) or 0)
            r['score_bucket'] = r.get('score_bucket') or assign_score_bucket(s, lo_lt, mid_lt)
            if keywords:
                r['enriched'] = mark_enrichment(r, keywords)
            else:
                r['enriched'] = 0
            all_rows.append(r)

    sampled = stratified_sample(all_rows, args.n, args.enrichment_fraction)
    write_csv(args.out, sampled)
    print(f"Sampled {len(sampled)} / {len(all_rows)} -> {args.out}")

    if args.manifest_json:
        strata_counts = {}
        for r in sampled:
            key = f"{r.get('transition')}|{r.get('pre_post')}|{r.get('score_bucket')}"
            strata_counts[key] = strata_counts.get(key,0)+1
        enr_frac = sum(1 for r in sampled if r.get('enriched')==1)/len(sampled) if sampled else 0.0
        manifest = {
            'generated_utc': int(time.time()),
            'static_thresholds': {'lo_lt': lo_lt, 'mid_lt': mid_lt},
            'dynamic_score_thresholds': False,  # placeholder (could add dynamic logic)
            'target_n': args.n,
            'actual_n': len(sampled),
            'enrichment_fraction': enr_frac,
            'strata_counts': strata_counts,
            'seed': args.seed,
            'keywords_used': len(keywords)
        }
        with open(args.manifest_json,'w',encoding='utf-8') as f:
            json.dump(manifest,f,indent=2)
        print(f"Manifest -> {args.manifest_json}")

if __name__ == '__main__':
    main()
