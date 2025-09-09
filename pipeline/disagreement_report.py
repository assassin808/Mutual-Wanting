#!/usr/bin/env python3
from __future__ import annotations
"""Generate disagreement diagnostics to guide annotation refinement.

Supports two modes:
  1) pilot-multitag: compares binary columns across TAGS per id and lists diff_tags (legacy output)
  2) pilot/comment (default=pilot for our use): uses a single 'primary_tag' to compute confusion pairs, kappa, and guidance

CLI compatibility:
  - Accepts --out or --out-json (synonyms)
  - Accepts raw CSVs via --a / --b, or --agreement-json
"""

import argparse, csv, json
from collections import Counter
from typing import Dict, List

TAGS = ["warmth", "creativity", "helpfulness", "hedging", "complaint"]
MISSING = "__MISSING__"


def load_rows(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_map_primary(path: str, id_field: str) -> Dict[str, str]:
    m: Dict[str, str] = {}
    for row in load_rows(path):
        cid = row.get(id_field)
        if not cid:
            continue
        m[cid] = (row.get("primary_tag") or "").strip() or MISSING
    return m


def cohen_kappa(labels_a: List[str], labels_b: List[str]) -> float:
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    if n == 0:
        return 0.0
    agree = sum(1 for x, y in zip(labels_a, labels_b) if x == y)
    po = agree / n
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    pe = sum((counts_a[l] / n) * (counts_b[l] / n) for l in set(labels_a + labels_b))
    if pe == 1:
        return 0.0
    return (po - pe) / (1 - pe) if (1 - pe) else 0.0


def confusion_pairs(labels_a: List[str], labels_b: List[str]) -> Counter:
    c: Counter = Counter()
    for a, b in zip(labels_a, labels_b):
        if a == b or a == MISSING or b == MISSING:
            continue
        key = tuple(sorted((a, b)))
        c[key] += 1
    return c


def build_from_raw_primary(a_path: str, b_path: str, id_field: str):
    A = load_map_primary(a_path, id_field)
    B = load_map_primary(b_path, id_field)
    shared = sorted(set(A) & set(B))
    la = [A[i] for i in shared]
    lb = [B[i] for i in shared]
    kappa = cohen_kappa(la, lb)
    pairs = confusion_pairs(la, lb)
    return kappa, len(shared), pairs


def derive_guidance(pairs: Counter, total_overlap: int, top_confusions: List[Dict]) -> List[str]:
    guidance: List[str] = []
    if not total_overlap:
        return guidance
    total_offdiag = sum(pairs.values()) or 1
    for entry in top_confusions:
        if entry["proportion_of_overlap"] >= 0.05 or entry["count"] / total_offdiag >= 0.15:
            guidance.append(
                f"Clarify boundary with contrasting examples for label pair {entry['pair']}"
            )
    label_presence = Counter()
    for (a, b), cnt in pairs.items():
        label_presence[a] += 1
        label_presence[b] += 1
    for lab, occ in label_presence.most_common():
        if occ >= max(2, int(0.4 * len(label_presence))):
            guidance.append(
                f"Refine definition scope for label '{lab}' (appears in {occ} confusion pairs)"
            )
    if top_confusions:
        trio = ", ".join(t["pair"] for t in top_confusions[:3])
        guidance.append(f"Prioritize adjudication session on pairs: {trio}")
    seen = set()
    uniq: List[str] = []
    for g in guidance:
        if g not in seen:
            seen.add(g)
            uniq.append(g)
    return uniq


def multitag_disagreements(a_csv: str, b_csv: str):
    A = {r["id"]: r for r in load_rows(a_csv) if r.get("id")}
    B = {r["id"]: r for r in load_rows(b_csv) if r.get("id")}
    shared = sorted(set(A) & set(B))
    disagreements = []
    for i in shared:
        ra, rb = A[i], B[i]
        diff_tags = []
        for t in TAGS:
            av = (ra.get(t) or "").strip().lower()
            bv = (rb.get(t) or "").strip().lower()
            if av == "" and bv == "":
                continue
            if av != bv:
                diff_tags.append(t)
        if diff_tags:
            disagreements.append(
                {
                    "id": i,
                    "diff_tags": diff_tags,
                    "a": {t: A[i].get(t, "") for t in TAGS},
                    "b": {t: B[i].get(t, "") for t in TAGS},
                }
            )
    return {"n_disagreements": len(disagreements), "items": disagreements}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", help="Annotator A CSV")
    ap.add_argument("--b", help="Annotator B CSV")
    ap.add_argument("--agreement-json", help="Existing agreement JSON (optional)")
    ap.add_argument("--out", help="Output JSON path (alias of --out-json)")
    ap.add_argument("--out-json", help="Output JSON path")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument(
        "--mode",
        choices=["comment", "pilot", "pilot-multitag"],
        default="pilot",
    )
    args = ap.parse_args()

    out_path = args.out_json or args.out
    if not out_path:
        raise SystemExit("Provide --out or --out-json")

    if args.mode == "pilot-multitag":
        if not (args.a and args.b):
            raise SystemExit("pilot-multitag mode requires --a and --b")
        result = multitag_disagreements(args.a, args.b)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Disagreement report -> {out_path} (mode=pilot-multitag, n={result['n_disagreements']})")
        return

    # Primary-tag confusion analysis
    if args.agreement_json:
        with open(args.agreement_json, "r", encoding="utf-8") as f:
            agree_data = json.load(f)
        confusion = agree_data.get("confusion", {})
        pairs_counter: Counter = Counter()
        for a, row in confusion.items():
            for b, cnt in row.items():
                if a == b or a == MISSING or b == MISSING:
                    continue
                key = tuple(sorted((a, b)))
                pairs_counter[key] += cnt
        kappa = agree_data.get("kappa")
        n_shared = agree_data.get("n_shared", 0)
    else:
        if not (args.a and args.b):
            raise SystemExit("Provide either --agreement-json or both --a and --b")
        id_field = "comment_id" if args.mode == "comment" else "id"
        kappa, n_shared, pairs_counter = build_from_raw_primary(args.a, args.b, id_field)

    total_overlap = n_shared
    ranked = []
    for (a, b), cnt in pairs_counter.most_common():
        ranked.append(
            {
                "pair": f"{a} vs {b}",
                "count": cnt,
                "proportion_of_overlap": (cnt / total_overlap) if total_overlap else 0.0,
            }
        )
    top_confusions = ranked[: args.top]
    guidance = derive_guidance(pairs_counter, total_overlap, top_confusions)

    out = {
        "kappa": kappa,
        "n_overlap": total_overlap,
        "top_confusions": top_confusions,
        "confusion_pairs_ranked": ranked,
        "guidance": guidance,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    kappa_str = f"{kappa:.3f}" if kappa is not None else "NA"
    print(f"Disagreement report -> {out_path} (mode={args.mode}, kappa={kappa_str})")


if __name__ == "__main__":
    main()
