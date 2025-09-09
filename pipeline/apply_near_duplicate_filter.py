#!/usr/bin/env python3
"""Apply near-duplicate removal given MinHash candidate pairs.

Input: JSONL corpus (each line JSON with at least `id` and `body`).
Pairs JSON: output of `text_minhash.py` (schema: {"pairs": [{id_a, id_b, approx_jaccard}, ...]})

Heuristic:
  * For each pair treat as undirected edge, build connected components.
  * Within each component keep the row with the longest body token length; ties broken by
    lexicographic lowest id (stable & deterministic).
  * All other ids in component are removed (singletons always kept).

Outputs:
  * Filtered JSONL corpus.
  * Removal report JSON with: n_in, n_out, n_components, n_multi_components, removed_ids (list),
    component_examples (first up to 10 components with size>1 and their member ids + lengths).

Usage:
  python pipeline/apply_near_duplicate_filter.py \
      --jsonl pipeline/data/recent_corpus_tagged.jsonl \
      --pairs pipeline/outputs/near_pairs.json \
      --out-jsonl pipeline/data/recent_corpus_merged_nearclean.jsonl \
      --report pipeline/data/near_duplicate_filter_report.json
"""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict, deque


def load_pairs(path: str):
    try:
        with open(path,'r',encoding='utf-8') as f:
            obj = json.load(f)
        return obj.get('pairs', [])
    except FileNotFoundError:
        return []


def build_components(pairs):
    graph = defaultdict(set)
    for p in pairs:
        a = str(p.get('id_a'))
        b = str(p.get('id_b'))
        if not a or not b:
            continue
        graph[a].add(b)
        graph[b].add(a)
    visited = set()
    components = []
    for node in list(graph.keys()):
        if node in visited:
            continue
        comp = []
        dq = deque([node])
        visited.add(node)
        while dq:
            cur = dq.popleft()
            comp.append(cur)
            for nb in graph[cur]:
                if nb not in visited:
                    visited.add(nb)
                    dq.append(nb)
        components.append(sorted(comp))
    # Add singleton nodes that never appeared in any edge? They are implicit; we handle later.
    return components


def token_length(text: str) -> int:
    return len((text or '').split())


def select_kept_ids(components, id_to_body):
    kept = set()
    removed = set()
    comp_examples = []
    for comp in components:
        if not comp:
            continue
        best = None
        best_len = -1
        for cid in comp:
            length = token_length(id_to_body.get(cid, ''))
            if length > best_len or (length == best_len and (best is None or cid < best)):
                best = cid
                best_len = length
        for cid in comp:
            if cid == best:
                kept.add(cid)
            else:
                removed.add(cid)
        if len(comp) > 1 and len(comp_examples) < 10:
            comp_examples.append({
                'members': comp,
                'chosen': best,
                'lengths': {cid: token_length(id_to_body.get(cid,'')) for cid in comp}
            })
    return kept, removed, comp_examples


def tokens(text: str):
    return set((text or '').lower().split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jsonl', required=True, help='Input corpus JSONL')
    ap.add_argument('--pairs', required=True, help='Pairs JSON from MinHash (text_minhash.py)')
    ap.add_argument('--out-jsonl', required=True, help='Filtered corpus output JSONL')
    ap.add_argument('--report', required=True, help='Removal report JSON')
    ap.add_argument('--mode', choices=['component','pairwise'], default='pairwise', help='Removal strategy')
    ap.add_argument('--removal-cap-frac', type=float, default=0.03, help='Max fraction of rows removable (pairwise mode)')
    ap.add_argument('--min-tokens', type=int, default=6, help='Skip removal for very short texts')
    ap.add_argument('--secondary-jaccard-min', type=float, default=0.88, help='Secondary exact token Jaccard to validate pairs')
    args = ap.parse_args()

    pairs = load_pairs(args.pairs)
    # Load corpus
    rows = []
    id_to_row = {}
    id_to_body = {}
    with open(args.jsonl,'r',encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid = str(obj.get('id'))
            if not rid:
                continue
            rows.append(obj)
            id_to_row[rid] = obj
            id_to_body[rid] = obj.get('body','')

    # Build components only among ids appearing in pairs
    removed_ids_all = set()
    comp_examples = []
    components = []
    if args.mode == 'component':
        components = build_components(pairs)
        kept_ids, removed_ids, comp_examples = select_kept_ids(components, id_to_body)
        removed_ids_all = set(removed_ids)
    else:
        # Conservative greedy pairwise removal with cap and secondary check
        # Precompute token sets for secondary check
        id_to_tokens = {rid: tokens(txt) for rid, txt in id_to_body.items()}
        # Sort pairs by provided approx_jaccard desc
        def pj(p):
            try:
                return float(p.get('approx_jaccard', 0.0))
            except Exception:
                return 0.0
        pairs_sorted = sorted(pairs, key=pj, reverse=True)
        max_remove = int(len(rows) * max(0.0, min(args.removal_cap_frac, 0.5)))
        removed_count = 0
        for p in pairs_sorted:
            a = str(p.get('id_a'))
            b = str(p.get('id_b'))
            if not a or not b:
                continue
            if a in removed_ids_all or b in removed_ids_all:
                continue
            # Skip short texts
            if token_length(id_to_body.get(a,'')) < args.min_tokens or token_length(id_to_body.get(b,'')) < args.min_tokens:
                continue
            # Secondary exact token Jaccard
            ta = id_to_tokens.get(a, set())
            tb = id_to_tokens.get(b, set())
            if not ta or not tb:
                continue
            inter = len(ta & tb)
            union = len(ta | tb) or 1
            sec_j = inter / union
            if sec_j < args.secondary_jaccard_min:
                continue
            # Remove the shorter one (by tokens); tie-break lexicographically higher id removed
            len_a = len(ta)
            len_b = len(tb)
            if len_a > len_b or (len_a == len_b and a < b):
                to_remove = b
            else:
                to_remove = a
            removed_ids_all.add(to_remove)
            removed_count += 1
            if removed_count >= max_remove:
                break

    # Write filtered corpus
    kept_rows = []
    for r in rows:
        rid = str(r.get('id'))
        if rid in removed_ids_all:
            continue
        kept_rows.append(r)
    with open(args.out_jsonl,'w',encoding='utf-8') as w:
        for r in kept_rows:
            w.write(json.dumps(r, ensure_ascii=False) + '\n')

    report = {
        'input': args.jsonl,
        'pairs_file': args.pairs,
        'n_in': len(rows),
        'n_pairs': len(pairs),
    'n_components': len(components) if components else 0,
    'n_multi_components': sum(1 for c in components if len(c)>1) if components else 0,
        'removed_count': len(removed_ids_all),
        'removed_ids': sorted(list(removed_ids_all))[:200],  # cap list to avoid huge output
        'output': args.out_jsonl,
        'n_out': len(kept_rows),
    'component_examples': comp_examples,
    'mode': args.mode,
    'removal_cap_frac': args.removal_cap_frac
    }
    with open(args.report,'w',encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Near-duplicate filter: {len(rows)} -> {len(kept_rows)} (removed {len(removed_ids_all)})")


if __name__ == '__main__':
    main()
