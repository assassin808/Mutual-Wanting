#!/usr/bin/env python3
"""List disagreements between two annotated CSVs for targeted guideline refinement."""
from __future__ import annotations
import argparse, csv, json

TAGS = ["warmth", "creativity", "helpfulness", "hedging", "complaint"]

def load(path):
    data = {}
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            data[row['id']] = row
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--out')
    args = ap.parse_args()

    A = load(args.a)
    B = load(args.b)
    shared = sorted(set(A.keys()) & set(B.keys()))
    disagreements = []
    for i in shared:
        ra, rb = A[i], B[i]
        diff_tags = []
        for t in TAGS:
            av = (ra.get(t) or '').strip().lower()
            bv = (rb.get(t) or '').strip().lower()
            if av == '' and bv == '':
                continue
            if av != bv:
                diff_tags.append(t)
        if diff_tags:
            disagreements.append({
                'id': i,
                'diff_tags': diff_tags,
                'a': {t: A[i].get(t,'') for t in TAGS},
                'b': {t: B[i].get(t,'') for t in TAGS},
                # body omitted to avoid duplicating user text when producing shareable artifacts
            })
    out_obj = { 'n_disagreements': len(disagreements), 'items': disagreements }
    if args.out:
        with open(args.out,'w',encoding='utf-8') as f:
            json.dump(out_obj, f, indent=2)
        print(f"Disagreement report -> {args.out}")
    else:
        print(json.dumps(out_obj, indent=2))

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Generate a focused disagreement report to guide annotation refinement cycles.

Inputs (either):
    1. Two annotated CSV files (same format as *_A.csv / *_B.csv) via --a / --b
    2. An existing agreement JSON (output of agreement.py) via --agreement-json

Modes:
    --mode comment (default) expects id field 'comment_id'
    --mode pilot expects id field 'id'

If raw CSVs provided we internally compute confusion (mirroring agreement.py logic) so that
this tool can be run immediately after an overlap batch is labeled.

Outputs:
  JSON ( --out-json ) containing:
    - kappa (if computed)
    - top_confusions: list of {pair, count, proportion_of_overlap}
    - confusion_pairs_ranked (full, excluding identical label pairs and MISSING)
    - guidance: heuristic remediation suggestions (up to N)

Heuristic remediation rules:
  - If a pair accounts for >15% of off-diagonal disagreements -> recommend clarifying boundary examples.
  - If a label appears in >40% of confusion pairs -> recommend tightening its primary definition.
  - Always surface the 3 most frequent confusion pairs.

This report is cited in the annotation refinement protocol as an artifact to update labeling_guidelines.md.
"""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from typing import Dict, List, Tuple

MISSING = '__MISSING__'


def load_map(path: str, id_field: str) -> Dict[str, str]:
    m = {}
    with open(path, 'r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            cid = row.get(id_field)
            if cid:
                m[cid] = (row.get('primary_tag') or '').strip() or MISSING
    return m


def cohen_kappa(labels_a: List[str], labels_b: List[str]) -> float:
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    agree = sum(1 for x, y in zip(labels_a, labels_b) if x == y)
    po = agree / n if n else 0.0
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    pe = sum((counts_a[l] / n) * (counts_b[l] / n) for l in set(labels_a + labels_b))
    if pe == 1:
        return 0.0
    return (po - pe) / (1 - pe) if (1 - pe) else 0.0


def confusion_pairs(labels_a: List[str], labels_b: List[str]) -> Counter:
    c = Counter()
    for a, b in zip(labels_a, labels_b):
        if a == b:
            continue
        if a == MISSING or b == MISSING:
            continue
        key = tuple(sorted((a, b)))
        c[key] += 1
    return c


def build_from_raw(a_path: str, b_path: str, id_field: str):
    A = load_map(a_path, id_field)
    B = load_map(b_path, id_field)
    shared = sorted(set(A) & set(B))
    la = [A[i] for i in shared]
    lb = [B[i] for i in shared]
    kappa = cohen_kappa(la, lb)
    pairs = confusion_pairs(la, lb)
    return kappa, len(shared), pairs


def derive_guidance(pairs: Counter, total_overlap: int, top_confusions: List[Dict]) -> List[str]:
    guidance = []
    if not total_overlap:
        return guidance
    total_offdiag = sum(pairs.values()) or 1
    # Rule 1: high-share pairs
    for entry in top_confusions:
        if entry['proportion_of_overlap'] >= 0.05 or entry['count'] / total_offdiag >= 0.15:
            guidance.append(f"Clarify boundary with contrasting examples for label pair {entry['pair']}")
    # Rule 2: labels with broad confusion presence
    label_presence = Counter()
    for (a, b), cnt in pairs.items():
        label_presence[a] += 1
        label_presence[b] += 1
    for lab, occ in label_presence.most_common():
        if occ >= max(2, int(0.4 * len(label_presence))):
            guidance.append(f"Refine definition scope for label '{lab}' (appears in {occ} confusion pairs)")
    # Always recap top 3
    if top_confusions:
        trio = ', '.join(t['pair'] for t in top_confusions[:3])
        guidance.append(f"Prioritize adjudication session on pairs: {trio}")
    # Deduplicate preserving order
    seen = set()
    uniq = []
    for g in guidance:
        if g not in seen:
            seen.add(g)
            uniq.append(g)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', help='Annotator A CSV')
    ap.add_argument('--b', help='Annotator B CSV')
    ap.add_argument('--agreement-json', help='Existing agreement JSON (optional)')
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--mode', choices=['comment','pilot'], default='comment')
    args = ap.parse_args()

    if args.agreement_json:
        with open(args.agreement_json, 'r', encoding='utf-8') as f:
            agree_data = json.load(f)
        # Reconstruct pairs from confusion
        confusion = agree_data.get('confusion', {})
        pairs_counter = Counter()
        for a, row in confusion.items():
            for b, cnt in row.items():
                if a == b or a == MISSING or b == MISSING:
                    continue
                key = tuple(sorted((a, b)))
                pairs_counter[key] += cnt
        kappa = agree_data.get('kappa')
        n_shared = agree_data.get('n_shared', 0)
    else:
        if not (args.a and args.b):
            raise SystemExit('Provide either --agreement-json or both --a and --b')
    id_field = 'comment_id' if args.mode == 'comment' else 'id'
    kappa, n_shared, pairs_counter = build_from_raw(args.a, args.b, id_field)

    total_overlap = n_shared
    ranked = []
    for (a, b), cnt in pairs_counter.most_common():
        ranked.append({
            'pair': f'{a} vs {b}',
            'count': cnt,
            'proportion_of_overlap': cnt / total_overlap if total_overlap else 0.0
        })
    top_confusions = ranked[: args.top]

    guidance = derive_guidance(pairs_counter, total_overlap, top_confusions)

    out = {
        'kappa': kappa,
        'n_overlap': total_overlap,
        'top_confusions': top_confusions,
        'confusion_pairs_ranked': ranked,
        'guidance': guidance
    }
    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    kappa_str = f"{kappa:.3f}" if kappa is not None else 'NA'
    print(f"Disagreement report -> {args.out_json} (mode={args.mode}, kappa={kappa_str})")

if __name__ == '__main__':
    main()
