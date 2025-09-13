#!/usr/bin/env python3
"""Recompute lightweight lexical features for current selection (Wave 1) to prepare for drift/regression scaffolds.

Inputs:
  --selection pipeline/outputs/annotation/selection_final.csv (id, transition, pre_post, ...)
  --enriched pipeline/data/label_batch1_enriched.csv (contains body)
Outputs:
  JSON summary + per-row feature CSV aligned with selection order.

Usage:
  python scripts/recompute_features_selection.py \
     --selection pipeline/outputs/annotation/selection_final.csv \
     --enriched pipeline/data/label_batch1_enriched.csv \
     --out-json pipeline/outputs/annotation/selection_features_summary.json \
     --out-csv pipeline/outputs/annotation/selection_features.csv

Feature Set mirrors minimal definitions in pipeline/features_and_analysis.py for consistency.
"""
from __future__ import annotations
import csv, argparse, json, os, re, statistics
from typing import Dict, List, Any, Optional

WORD_RE = re.compile(r"[A-Za-z']+")
HEDGES = {"maybe","might","could","possibly","perhaps","seems","appears"}
WARMTH = {"thanks","thank","please","appreciate","love","enjoy"}
IMP_EXCL = {"i","you","we","it"}
PRONOUNS = {"i","we","me","us","our","ours","you","your","yours"}


def tokenize(text: str):
    return WORD_RE.findall(text.lower())


def extract(text: str) -> Dict[str,Any]:
    toks=tokenize(text or '')
    if not toks:
        return {"token_len":0,"hedge_rate":0,"warmth_rate":0,"imperative_ratio":0,"pronoun_ratio":0}
    n=len(toks)
    hedge=sum(t in HEDGES for t in toks)
    warmth=sum(t in WARMTH for t in toks)
    imperative=1 if toks and toks[0] not in IMP_EXCL and toks[0] not in HEDGES else 0
    pron=sum(t in PRONOUNS for t in toks)
    return {
        "token_len": n,
        "hedge_rate": hedge/n,
        "warmth_rate": warmth/n,
        "imperative_ratio": imperative,
        "pronoun_ratio": pron/n
    }


def read_csv(path: str) -> List[Dict[str,str]]:
    with open(path,'r',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_row_id(row: Dict[str,str], preferred: Optional[str]=None) -> Optional[str]:
    # Try preferred first, then common variants
    candidates = []
    if preferred:
        candidates.append(preferred)
    candidates.extend(['id','comment_id','commentid','row_id'])
    for k in candidates:
        if k in row and row[k]:
            return row[k]
    return None


def aggregate(rows: List[Dict[str,Any]]) -> Dict[str,Any]:
    agg={}
    for k in ["token_len","hedge_rate","warmth_rate","imperative_ratio","pronoun_ratio"]:
        vals=[float(r[k]) for r in rows if k in r]
        if vals:
            agg[k]={"mean": sum(vals)/len(vals), "median": statistics.median(vals)}
    return agg


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--selection', required=True)
    ap.add_argument('--enriched', required=True)
    ap.add_argument('--out-json', required=True)
    ap.add_argument('--out-csv', required=True)
    ap.add_argument('--selection-id-col', default='id', help='ID column name in selection CSV (default: id)')
    ap.add_argument('--enriched-id-col', default=None, help='ID column name in enriched CSV (auto-detect if omitted)')
    args=ap.parse_args()

    selection=read_csv(args.selection)
    enriched=read_csv(args.enriched)
    by_id={}
    for r in enriched:
        rid=get_row_id(r, args.enriched_id_col)
        if rid is not None:
            by_id[rid]=r

    feat_rows=[]
    missing=0
    for r in selection:
        rid=get_row_id(r, args.selection_id_col)
        er=by_id.get(rid, {})
        body=er.get('body','')
        f=extract(body)
        out=dict(r)
        out.update(f)
        feat_rows.append(out)
        if not body:
            missing+=1

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    # Write per-row
    fieldnames=sorted({k for row in feat_rows for k in row.keys()})
    with open(args.out_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in feat_rows:
            w.writerow(row)

    summary=aggregate(feat_rows)
    meta={"count":len(feat_rows),"missing_body":missing,"summary":summary}
    with open(args.out_json,'w',encoding='utf-8') as f:
        json.dump(meta,f,indent=2)
    print(f"Features recomputed -> rows={len(feat_rows)} missing_body={missing} json={args.out_json} csv={args.out_csv}")

if __name__=='__main__':
    main()
