#!/usr/bin/env python3
"""Preliminary descriptive statistics over current raw filtered datasets.
Combines 'pre' (live_raw_window.jsonl) and 'post' (live_raw_kw.jsonl) runs as a provisional window test.
Outputs JSON summary and optional Markdown report.

Usage:
  python pipeline/prelim_descriptives.py \
    --pre pipeline/data/live_raw_window.jsonl \
    --post pipeline/data/live_raw_kw.jsonl \
    --out-json pipeline/data/prelim_descriptives.json \
    --out-md pipeline/data/prelim_descriptives.md

NOTE: The current 'pre'/'post' division is artificial (different collection passes); interpret cautiously.
"""
from __future__ import annotations
import json, argparse, re, statistics
from collections import Counter
from typing import List, Dict

WORD_RE = re.compile(r"[A-Za-z']+")

COMPLAINT_LEXEMES = {
    'warmth','colder','cold','soulless','bland','personality','drift','worse','regressed',
    'creativity','creative','hedging','uncertain','uncertainty','safety','refusal','refusing',
    'memory','verbose','verbosity','slower','latency','slow','trust','honest','honesty','hallucinate','hallucination'
}

def load_jsonl(path: str) -> List[Dict]:
    rows = []
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def tokenize(text: str):
    return [t.lower() for t in WORD_RE.findall(text)]


def stats(rows: List[Dict]):
    lengths = []
    lex_counter = Counter()
    complaint_counter = Counter()
    score_buckets = Counter()
    empty = 0
    for r in rows:
        body = (r.get('body') or '')
        toks = tokenize(body)
        if not toks:
            empty += 1
            continue
        lengths.append(len(toks))
        lex_counter.update(toks)
        complaint_counter.update([t for t in toks if t in COMPLAINT_LEXEMES])
        score_buckets[r.get('score_bucket','UNK')] += 1
    out = {
        'count': len(rows),
        'empty_bodies': empty,
        'score_bucket_dist': dict(score_buckets),
        'token_length_mean': statistics.mean(lengths) if lengths else 0,
        'token_length_median': statistics.median(lengths) if lengths else 0,
        'top_complaint_terms': complaint_counter.most_common(12),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pre', required=True)
    ap.add_argument('--post', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-md')
    args = ap.parse_args()

    pre_rows = load_jsonl(args.pre)
    post_rows = load_jsonl(args.post)

    pre_stats = stats(pre_rows)
    post_stats = stats(post_rows)

    combined = {
        'pre': pre_stats,
        'post': post_stats,
        'notes': 'Pre/post division is provisional (different collection passes; release anchor artificial).'
    }

    with open(args.out_json,'w',encoding='utf-8') as f:
        json.dump(combined,f,indent=2)

    if args.out_md:
        def fmt_terms(lst):
            return ', '.join(f"{w}({c})" for w,c in lst)
        lines = [
            '# Preliminary Descriptives (Provisional)',
            '',
            f"Pre count: {pre_stats['count']} (empty {pre_stats['empty_bodies']}) | Post count: {post_stats['count']} (empty {post_stats['empty_bodies']})",
            f"Pre score buckets: {pre_stats['score_bucket_dist']} | Post score buckets: {post_stats['score_bucket_dist']}",
            f"Pre token length mean/median: {pre_stats['token_length_mean']:.1f}/{pre_stats['token_length_median']} | Post: {post_stats['token_length_mean']:.1f}/{post_stats['token_length_median']}",
            f"Top complaint terms (pre): {fmt_terms(pre_stats['top_complaint_terms'])}",
            f"Top complaint terms (post): {fmt_terms(post_stats['top_complaint_terms'])}",
            '',
            '_Interpretation_: Initial filtered sample skews heavily to low-score items and exhibits sparse high-salience complaint lexemes; need broader retrieval + targeted enrichment for robust comparative analysis.'
        ]
        with open(args.out_md,'w',encoding='utf-8') as f:
            f.write('\n'.join(lines)+'\n')

if __name__ == '__main__':
    main()
