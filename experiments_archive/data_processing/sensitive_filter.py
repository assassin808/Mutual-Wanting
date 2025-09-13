#!/usr/bin/env python3
"""Sensitive content filter log generator.

Flags rows containing potentially sensitive terms so they can be excluded or
queued for manual privacy review. DOES NOT delete rows; only emits a log.

Configurable categories with regex patterns.
"""
from __future__ import annotations
import argparse, json, re

DEFAULT_PATTERNS = {
    'personal_info': [r"\bemail\b", r"\bphone\b", r"\baddress\b", r"@"],
    'self_harm': [r"suicide", r"kill myself", r"self-harm"],
    'medical': [r"diagnosed", r"therapy", r"prescription"],
}

def compile_patterns(config):
    compiled = {}
    for cat, pats in config.items():
        compiled[cat] = [re.compile(p, re.IGNORECASE) for p in pats]
    return compiled

def scan(text: str, compiled):
    hits = []
    for cat, regs in compiled.items():
        for rg in regs:
            if rg.search(text):
                hits.append(cat)
                break
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jsonl', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--patterns-json', help='Optional JSON file with category -> [regex,...]')
    ap.add_argument('--max-log', type=int, default=100)
    args = ap.parse_args()

    config = DEFAULT_PATTERNS
    if args.patterns_json:
        with open(args.patterns_json,'r',encoding='utf-8') as f:
            config = json.load(f)
    compiled = compile_patterns(config)

    flagged = []
    total = 0
    with open(args.jsonl,'r',encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            obj = json.loads(line)
            text = obj.get('body','')
            cats = scan(text, compiled)
            if cats:
                if len(flagged) < args.max_log:
                    flagged.append({'id': obj.get('id'), 'categories': cats})
    out = {
        'input': args.jsonl,
        'total_rows': total,
        'n_flagged': len(flagged),
        'flagged_examples': flagged,
        'categories': list(config.keys())
    }
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Sensitive filter -> {args.out} flagged={len(flagged)}/{total}")

if __name__ == '__main__':
    main()
