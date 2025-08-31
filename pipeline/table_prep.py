#!/usr/bin/env python3
"""Prepare manuscript-ready JSON -> simple TSV tables.

Given various JSON artifacts (agreement.json, enrichment_eval.json, regression_results.json, drift_bootstrap.json)
this script emits TSV summaries under a target directory suitable for \input{} or copy/paste.

Usage:
  python pipeline/table_prep.py --agreement pipeline/outputs/agreement.json \
     --enrichment pipeline/outputs/enrichment_eval.json \
     --regress pipeline/outputs/regression_results.json \
     --drift-lex pipeline/outputs/drift_log_odds.json \
     --drift-boot pipeline/outputs/drift_bootstrap.json \
     --out-dir pipeline/outputs/tables
"""
from __future__ import annotations
import argparse, json, os, csv
from pathlib import Path


def load(path: str):
    if not path:
        return None
    if not os.path.isfile(path):
        return None
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)


def write_tsv(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8',newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    print(f'Table -> {path}')


def table_agreement(data, outdir: Path):
    if not data:
        return
    rows=[]
    rows.append(['kappa', f"{data.get('kappa',0):.3f}"])
    rows.append(['n_overlap', data.get('n_shared') or data.get('n_overlap')])
    write_tsv(outdir/'agreement.tsv',['metric','value'],rows)


def table_enrichment(data, outdir: Path):
    if not data:
        return
    p = data['precision_enriched']
    b = data['prevalence_baseline']
    rows=[
        ['n_enriched', data['n_enriched']],
        ['complaints_enriched', data['complaints_enriched']],
        ['precision_enriched', f"{p['point']:.3f} [{p['wilson_low']:.3f},{p['wilson_high']:.3f}]"],
        ['n_baseline', data['n_baseline']],
        ['prevalence_baseline', f"{b['point']:.3f} [{b['wilson_low']:.3f},{b['wilson_high']:.3f}]"],
        ['relative_risk_enrichment', f"{data.get('relative_risk_enrichment'):.2f}" if data.get('relative_risk_enrichment') else 'NA'],
        ['recall_estimate', f"{data['recall_estimate_under_random_prevalence']:.3f}"]
    ]
    write_tsv(outdir/'enrichment.tsv',['metric','value'],rows)


def table_regress(data, outdir: Path):
    if not data:
        return
    # Summarize only interaction coefficients (transition:pre_post) where available
    header=['outcome','estimator','positive','negative','interaction_coef','interaction_p']
    rows=[]
    for outcome, res in data.items():
        if 'skipped' in res:
            rows.append([outcome,'skipped',res.get('positive'),res.get('negative'),'',''])
            continue
        est = res.get('estimator')
        pos = res.get('positive') or res.get('params',{}).get('positive')
        neg = res.get('negative')
        params = res.get('params',{})
        pvals = res.get('pvalues',{})
        # find any param containing ':', heuristic for interaction
        inter_key = None
        for k in params.keys():
            if ':' in k:
                inter_key = k
                break
        rows.append([
            outcome,
            est,
            pos,
            neg,
            f"{params.get(inter_key):.3f}" if inter_key and isinstance(params.get(inter_key),(int,float)) else '',
            f"{pvals.get(inter_key):.3g}" if inter_key and inter_key in pvals else ''
        ])
    write_tsv(outdir/'regression_interactions.tsv',header,rows)


def table_drift(drift_lex, drift_boot, outdir: Path):
    if not drift_lex:
        return
    # Filter tokens by stability if bootstrap provided
    stable_tokens=set()
    if drift_boot:
        for tok, d in drift_boot.get('tokens',{}).items():
            if d.get('sign_consistency',0) >= 0.8:
                stable_tokens.add(tok)
    rows=[['token','pre_freq','post_freq','z','direction','stable']]
    def row(entry, direction):
        return [
            entry['token'], entry['pre_freq'], entry['post_freq'], f"{entry['z']:.2f}", direction,
            'yes' if entry['token'] in stable_tokens else 'no'
        ]
    for entry in drift_lex.get('top_pre_tokens',[])[:15]:
        rows.append(row(entry,'pre>post'))
    for entry in drift_lex.get('top_post_tokens',[])[:15]:
        rows.append(row(entry,'post>pre'))
    write_tsv(outdir/'drift_tokens.tsv', rows[0], rows[1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agreement')
    ap.add_argument('--enrichment')
    ap.add_argument('--regress')
    ap.add_argument('--drift-lex')
    ap.add_argument('--drift-boot')
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    agreement = load(args.agreement)
    enrichment = load(args.enrichment)
    regress = load(args.regress)
    drift_lex = load(args.drift_lex)
    drift_boot = load(args.drift_boot)

    table_agreement(agreement, outdir)
    table_enrichment(enrichment, outdir)
    table_regress(regress, outdir)
    table_drift(drift_lex, drift_boot, outdir)

if __name__ == '__main__':
    main()
