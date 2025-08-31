#!/usr/bin/env python3
"""Statistical comparison utilities for probe metrics.

Given a probes_results.json (output of probe_runner) having structure:
  { model: { prompt_id: { 'text': ..., 'metrics': { cdr:0/1, sur:0/1, ... } }, ... }, ... }

This script aggregates per-model proportion metrics and performs pairwise
Wald z-tests for proportions across models for specified binary metrics.

Outputs JSON with per-model aggregates and pairwise comparisons.

Usage:
  python pipeline/probe_stats.py --probes-json pipeline/outputs/probes_results.json \
      --metrics cdr sur --out pipeline/outputs/probe_stats.json
"""
from __future__ import annotations
import json, argparse, math, itertools
from typing import Dict, Any, List


def load(path: str) -> Dict[str,Any]:
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)


def aggregate(data: Dict[str,Any], metrics: List[str]):
    per_model={}
    for model, prompts in data.items():
        agg={}
        counts={m:0 for m in metrics}
        n_prompts=0
        for pid, meta in prompts.items():
            m=meta.get('metrics',{})
            n_prompts+=1
            for k in metrics:
                v=m.get(k)
                if v in (0,1):
                    counts[k]+=v
        for k in metrics:
            denom=n_prompts or 1
            p=counts[k]/denom
            agg[k]={'n': n_prompts, 'count': counts[k], 'prop': p}
        per_model[model]=agg
    return per_model


def z_test(p1, n1, p2, n2):
    # Wald z
    if n1==0 or n2==0:
        return None
    p_pool=(p1*n1 + p2*n2)/(n1+n2)
    se=math.sqrt(p_pool*(1-p_pool)*(1/n1 + 1/n2))
    if se==0:
        return None
    z=(p1-p2)/se
    # two-sided p approximated via normal
    try:
        import math as _m
        from math import erf, sqrt
        # tail prob
        from math import exp
    except:  # noqa
        pass
    # Use survival function approximation
    p_val=2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
    return z, p_val


def pairwise_tests(per_model: Dict[str,Any], metrics: List[str]):
    comps=[]
    models=list(per_model.keys())
    for a,b in itertools.combinations(models,2):
        for m in metrics:
            pa=per_model[a][m]['prop']
            na=per_model[a][m]['n']
            pb=per_model[b][m]['prop']
            nb=per_model[b][m]['n']
            z_p=z_test(pa,na,pb,nb)
            comps.append({
                'metric': m,
                'model_a': a,
                'model_b': b,
                'prop_a': pa,
                'prop_b': pb,
                'z': None if z_p is None else z_p[0],
                'p': None if z_p is None else z_p[1]
            })
    return comps


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--probes-json', required=True)
    ap.add_argument('--metrics', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()

    data=load(args.probes_json)
    per_model=aggregate(data, args.metrics)
    comps=pairwise_tests(per_model, args.metrics)
    out={'per_model': per_model, 'pairwise': comps}
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(out,f,indent=2)
    print(f"Probe stats -> {args.out}")

if __name__=='__main__':
    main()
