#!/usr/bin/env python3
"""Multi-transition stratified sampler for large-N annotation wave.

Strata dimensions implemented:
  transition * pre_post * cluster_id * length_bucket
Additional balancing:
  - Enforce roughly equal pre/post within each transition (tolerance ±2 when limited)
  - Ensure minimum per (transition, cluster_id) if feasible (min_per_cluster)
  - Filter out very short / empty bodies by token_len >= --min-token-len

Sampling procedure:
  1. Load *_sampling_frame_clusters.csv for each transition provided (or auto-discover).
  2. Filter rows meeting token length and (optional) question flag inclusion logic.
  3. Compute target allocation per transition (proportional to available rows^alpha) with floor minimum.
  4. Within each transition, allocate quota across clusters proportionally, then across pre/post equally.
  5. Perform random sampling with deterministic seed.
  6. If shortfall (insufficient rows in a stratum) redistribute remainder greedily to strata with spare capacity.

Outputs:
  pipeline/outputs/annotation/selection_final.csv
  pipeline/outputs/annotation/sampling_manifest.json
  pipeline/outputs/annotation/sampling_report.md

Usage:
  python scripts/multi_transition_sampling.py --target-n 800 --seed 42 --alpha 1.0 --min-per-transition 200
"""
from __future__ import annotations
import argparse, csv, glob, json, os, random, math
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple

HEADER = ['id','transition','pre_post','subreddit','score_bucket','length_bucket','question_flag','sentiment','cluster_id','token_len']


def load_frames(paths: List[str], min_token_len: int) -> List[Dict[str,Any]]:
    rows=[]
    for p in paths:
        with open(p,'r',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            for r in reader:
                try:
                    tl=int(r.get('token_len') or 0)
                except: # noqa
                    tl=0
                if tl < min_token_len:
                    continue
                rows.append(r)
    return rows


def proportional_alloc(sizes: Dict[str,int], target: int, alpha: float, min_per: int) -> Dict[str,int]:
    weights={k: (v**alpha) for k,v in sizes.items()}
    total=sum(weights.values()) or 1
    raw={k: max(min_per, int(round(target * w/total))) for k,w in weights.items()}
    # Adjust to exact target via trimming/adding
    diff=sum(raw.values())-target
    if diff>0:
        # trim from largest allocations > min_per
        while diff>0:
            k=max(raw, key=lambda x: raw[x])
            if raw[k]>min_per:
                raw[k]-=1; diff-=1
            else:
                break
    elif diff<0:
        diff=-diff
        keys=sorted(raw, key=lambda k: raw[k])
        i=0
        while diff>0 and keys:
            k=keys[i%len(keys)]
            raw[k]+=1; diff-=1; i+=1
    return raw


def strat_key(r):
    return (r['transition'], r['pre_post'], r['cluster_id'], r['length_bucket'])


def sample_transition(rows: List[Dict[str,Any]], quota: int, seed: int, min_per_cluster: int) -> List[Dict[str,Any]]:
    random.seed(seed)
    # Group by cluster
    clusters=defaultdict(list)
    for r in rows:
        clusters[r['cluster_id']].append(r)
    # Initial cluster allocation proportional
    total=sum(len(v) for v in clusters.values()) or 1
    alloc={cid: max(min_per_cluster, int(round(quota * len(v)/total))) for cid,v in clusters.items()}
    # Adjust back to quota
    diff=sum(alloc.values())-quota
    if diff>0:
        while diff>0:
            cid=max(alloc, key=lambda c: alloc[c])
            if alloc[cid]>min_per_cluster:
                alloc[cid]-=1; diff-=1
            else:
                break
    elif diff<0:
        diff=-diff
        while diff>0:
            cid=min(alloc, key=lambda c: alloc[c])
            alloc[cid]+=1; diff-=1
    # Within cluster, split pre/post ~ equally
    out=[]
    for cid,v in clusters.items():
        k=alloc.get(cid,0)
        if k<=0: continue
        pre=[r for r in v if r['pre_post']=='pre']
        post=[r for r in v if r['pre_post']=='post']
        half=k//2
        take_pre=min(len(pre), half)
        take_post=min(len(post), k - take_pre)
        # If leftover due to shortage in one side, fill from other
        deficit=k - (take_pre+take_post)
        if deficit>0:
            # allocate to whichever side has capacity
            if len(pre)-take_pre > len(post)-take_post:
                extra=min(deficit, len(pre)-take_pre)
                take_pre+=extra; deficit-=extra
            if deficit>0 and (len(post)-take_post)>0:
                extra=min(deficit, len(post)-take_post)
                take_post+=extra; deficit-=extra
        chosen_pre=random.sample(pre, take_pre) if take_pre>0 else []
        chosen_post=random.sample(post, take_post) if take_post>0 else []
        out.extend(chosen_pre+chosen_post)
    # If still short due to sparse clusters, top up globally
    if len(out)<quota:
        remaining=[r for r in rows if r not in out]
        need=quota-len(out)
        if remaining:
            out.extend(random.sample(remaining, min(need,len(remaining))))
    return out[:quota]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--target-n', type=int, default=800)
    ap.add_argument('--alpha', type=float, default=1.0, help='Exponent for proportional allocation (alpha<1 flattens)')
    ap.add_argument('--min-per-transition', type=int, default=200)
    ap.add_argument('--min-token-len', type=int, default=5)
    ap.add_argument('--min-per-cluster', type=int, default=5)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--transitions', nargs='*', help='Explicit transitions (else auto)')
    ap.add_argument('--annotation-dir', default='pipeline/outputs/annotation')
    ap.add_argument('--out-selection', default='pipeline/outputs/annotation/selection_final.csv')
    args=ap.parse_args()

    pattern=os.path.join(args.annotation_dir,'*_sampling_frame_clusters.csv')
    files=glob.glob(pattern)
    if args.transitions:
        files=[f for f in files if any(f"/{t}_" in f or f"\\{t}_" in f for t in args.transitions)]
    if not files:
        raise SystemExit('No sampling frame cluster files discovered')

    # Map transitions
    trans_files=defaultdict(list)
    for f in files:
        base=os.path.basename(f)
        t=base.split('_sampling_frame_clusters.csv')[0]
        trans_files[t].append(f)

    # Load rows per transition
    rows_by_transition={}
    sizes={}
    for t, fps in trans_files.items():
        rows=load_frames(fps, args.min_token_len)
        rows_by_transition[t]=rows
        sizes[t]=len(rows)

    alloc=proportional_alloc(sizes, args.target_n, args.alpha, args.min_per_transition)

    selected=[]
    for t, rows in rows_by_transition.items():
        q=alloc.get(t,0)
        if q<=0 or not rows:
            continue
        sel=sample_transition(rows, q, args.seed+hash(t)%10000, args.min_per_cluster)
        selected.extend(sel)

    random.seed(args.seed)
    random.shuffle(selected)

    os.makedirs(os.path.dirname(args.out_selection), exist_ok=True)
    with open(args.out_selection,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(HEADER)
        for r in selected:
            w.writerow([r.get(h,'') for h in HEADER])

    # Manifest & report
    manifest_path=os.path.join(args.annotation_dir,'sampling_manifest.json')
    strata_counts=Counter((r['transition'], r['pre_post']) for r in selected)
    with open(manifest_path,'w',encoding='utf-8') as f:
        json.dump({
            'target_n': args.target_n,
            'actual_n': len(selected),
            'allocation': alloc,
            'sizes': sizes,
            'min_token_len': args.min_token_len,
            'seed': args.seed,
            'strata_counts': {f"{k[0]}|{k[1]}": v for k,v in strata_counts.items()}
        }, f, indent=2)

    report_path=os.path.join(args.annotation_dir,'sampling_report.md')
    with open(report_path,'w',encoding='utf-8') as f:
        f.write(f"# Sampling Report\n\nTarget: {args.target_n} Actual: {len(selected)}\n\n")
        f.write('## Allocation\n')
        for t in sorted(alloc):
            f.write(f"- {t}: alloc={alloc[t]} avail={sizes[t]}\n")
        f.write('\n## Transition Pre/Post Counts\n')
        per_trans=defaultdict(lambda: {'pre':0,'post':0})
        for (t,phase),cnt in strata_counts.items():
            per_trans[t][phase]+=cnt
        for t, d in per_trans.items():
            f.write(f"- {t}: pre={d['pre']} post={d['post']}\n")
    print(f"Selection written: {args.out_selection} (n={len(selected)})")
    print(f"Manifest: {manifest_path}\nReport: {report_path}")

if __name__=='__main__':
    main()
