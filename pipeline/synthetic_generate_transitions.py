#!/usr/bin/env python3
"""Generate synthetic per-transition pre/post Reddit-like archives.

Purpose: Unblock pipeline execution when real Reddit data unavailable (e.g., no
network or missing credentials). Produces JSONL files matching expected schema
for `multi_backfill_stub.py`.

Design:
  - For each transition defined in transitions.yaml create pre & post archives
    with configurable counts per subreddit.
  - Inject controlled lexical drift: each transition gets a set of drift_up and
    drift_down tokens whose frequencies change between pre/post to exercise
    drift_lexicon + bootstrap + trend scripts.
  - Complaint signal: inject a "complaint" keyword cluster more in post for one
    transition and more in pre for another to produce interaction variance.

Usage:
  python pipeline/synthetic_generate_transitions.py \
      --transitions pipeline/transitions.yaml \
      --subreddits pipeline/subreddits.txt \
      --out-dir pipeline/data \
      --per-subreddit 60 --seed 42

Outputs:
  pipeline/data/<transition>_pre.jsonl
  pipeline/data/<transition>_post.jsonl

Safe to re-run (overwrites). Only use for internal testing; do not mix with real data.
"""
from __future__ import annotations
import argparse, json, random, yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transitions', required=True)
    ap.add_argument('--subreddits', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--per-subreddit', type=int, default=80, help='Rows per subreddit per phase')
    ap.add_argument('--seed', type=int, default=17)
    return ap.parse_args()


def load_yaml(path: str):
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_subreddits(path: str) -> List[str]:
    subs=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            subs.append(line)
    return subs


DRIFT_TOKEN_POOL = [
    'guardrail','refusal','policy','jailbreak','aligned','persona','creative','verbose','concise',
    'hedge','warm','stilted','direct','apology','safe','sandbox','bias','tone','structured'
]

COMPLAINT_TERMS = ['worse','declined','nerfed','broken','censored','sanitized','unhelpful','inconsistent']
NEUTRAL_FILL = ['the','and','i','it','this','that','for','with','when','you','we','model','response','prompt']


def synth_body(base_seed: int, drift_up: List[str], drift_down: List[str], phase: str, complaint_bias: float) -> str:
    rnd = random.Random(base_seed)
    tokens = []
    # neutral backbone
    for _ in range(rnd.randint(6,14)):
        tokens.append(rnd.choice(NEUTRAL_FILL))
    # drift tokens: more of drift_up in post, drift_down in pre
    for t in drift_up:
        if phase == 'post':
            tokens.extend([t]*rnd.randint(1,2))
        else:
            if rnd.random() < 0.3:
                tokens.append(t)
    for t in drift_down:
        if phase == 'pre':
            tokens.extend([t]*rnd.randint(1,2))
        else:
            if rnd.random() < 0.3:
                tokens.append(t)
    # complaints
    if rnd.random() < complaint_bias:
        tokens.append(rnd.choice(COMPLAINT_TERMS))
    return ' '.join(tokens)


def main():
    args = parse_args()
    random.seed(args.seed)
    transitions = load_yaml(args.transitions)
    subs = load_subreddits(args.subreddits)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Assign drift tokens per transition deterministically
    rnd_global = random.Random(args.seed)
    drift_assignments: Dict[str, Dict[str,List[str]]] = {}
    for t in transitions:
        tid = t['id']
        rnd_local = random.Random(args.seed + hash(tid) % 10000)
        shuffled = DRIFT_TOKEN_POOL[:]
        rnd_local.shuffle(shuffled)
        half = len(shuffled)//2
        drift_assignments[tid] = {
            'up': shuffled[:half//2],
            'down': shuffled[half//2:half]
        }

    # Complaint bias pattern: alternate which phase has higher complaint probability
    complaint_pattern = {}
    for i, t in enumerate(transitions):
        complaint_pattern[t['id']] = 'post' if i % 2 == 0 else 'pre'

    for t in transitions:
        tid = t['id']
        rel = datetime.strptime(str(t['release_date']), '%Y-%m-%d')
        pre_days = int(t.get('pre_days',14))
        post_days = int(t.get('post_days',14))
        pre_start = rel - timedelta(days=pre_days)
        post_start = rel
        drift_up = drift_assignments[tid]['up']
        drift_down = drift_assignments[tid]['down']
        complaint_phase = complaint_pattern[tid]
        for phase in ['pre','post']:
            path = out_dir / f"{tid}_{phase}.jsonl"
            rows: List[Dict[str,Any]] = []
            for sub in subs:
                for i in range(args.per_subreddit):
                    # time spread uniformly over window
                    if phase == 'pre':
                        day_offset = random.randint(0, max(pre_days-1,0))
                        base_dt = pre_start + timedelta(days=day_offset, hours=random.randint(0,23), minutes=random.randint(0,59))
                    else:
                        day_offset = random.randint(0, max(post_days-1,0))
                        base_dt = post_start + timedelta(days=day_offset, hours=random.randint(0,23), minutes=random.randint(0,59))
                    created = int(base_dt.timestamp())
                    complaint_bias = 0.55 if phase == complaint_phase else 0.15
                    body = synth_body(created ^ args.seed, drift_up, drift_down, phase, complaint_bias)
                    score = random.randint(0,60)
                    rows.append({
                        'id': f'{tid[:4]}_{phase}_{sub}_{i}_{created}',
                        'parent_id': None,
                        'link_id': f't3_{tid[:4]}_{i}',
                        'created_utc': created,
                        'score': score,
                        'body': body,
                        'subreddit': sub,
                        'author': f'user_{random.randint(0,500)}'
                    })
            with open(path,'w',encoding='utf-8') as f:
                for r in rows:
                    f.write(json.dumps(r)+'\n')
            print(f"Wrote {len(rows)} rows -> {path}")

    # Summary manifest
    manifest = {
        'drift_assignments': drift_assignments,
        'complaint_pattern': complaint_pattern,
        'per_subreddit': args.per_subreddit
    }
    with open(out_dir / 'synthetic_generation_summary.json','w',encoding='utf-8') as f:
        json.dump(manifest,f,indent=2)
    print(f"Synthetic summary -> {out_dir / 'synthetic_generation_summary.json'}")

if __name__ == '__main__':
    main()
