#!/usr/bin/env python3
"""Probe runner scaffold: records prompts and intended models with seeds; no API calls.

Outputs a manifest to be manually populated with responses to avoid external calls here.
"""
import argparse, json, os, time, hashlib, random
import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompts', default='pipeline/probes/prompts.yaml')
    ap.add_argument('--out', default='pipeline/outputs/probes_manifest.json')
    ap.add_argument('--seed', type=int, default=13)
    args = ap.parse_args()

    with open(args.prompts, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    random.seed(args.seed)
    run_id = hashlib.sha1(f"{time.time()}-{args.seed}".encode()).hexdigest()[:10]
    out = {
        'run_id': run_id,
        'version': cfg.get('version'),
        'seed': args.seed,
        'models': cfg.get('models', []),
        'prompts': cfg.get('prompts', []),
        'responses': [],  # to be filled offline
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print(f"Probe manifest -> {args.out}")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Probe Suite Runner
Executes structured prompt suite across specified model versions and computes preliminary behavioral metrics.

Usage:
  python pipeline/probe_runner.py --models gpt-4o gpt-5 --prompts pipeline/data/prompts.json --out-json pipeline/data/probe_runs.jsonl --metrics-out pipeline/data/probe_metrics.json

Prompts JSON format (list of objects):
[
  {"id":"U1","category":"uncertainty","text":"What is ...?"},
  {"id":"W1","category":"warmth","text":"I've been ..."}
]

Environment:
  OPENROUTER_API_KEY must be set (in .env loaded by shell) for live calls.

Note: This script avoids storing API keys or sensitive data. Responses are minimally processed for metric extraction (warmth lexicon density, uncertainty markers, structure heuristics). Full NLP model scoring can be added later.
"""
from __future__ import annotations
import os, argparse, json, time, random, re
from typing import List, Dict, Any
import requests

UNCERTAINTY_MARKERS = {"might","maybe","uncertain","likely","unlikely","approximately","roughly"}
WARMTH_LEXICON = {"appreciate","glad","encourage","cheering","happy","understand","support","together","let's","care"}
STRUCTURE_REGEX = re.compile(r"^(\d+\.|- )", re.MULTILINE)
MINIMAL_ACK_PATTERN = re.compile(r"^ready when you are\.?$", re.IGNORECASE)

RATE_LIMIT_SLEEP = 1.2  # seconds between calls (tunable)

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_prompts(path: str) -> List[Dict[str,Any]]:
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)


def call_model(model: str, prompt: str, temperature: float, seed: int) -> Dict[str,Any]:
    key = os.getenv('OPENROUTER_API_KEY')
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    body = {
        'model': model,
        'messages': [
            {'role':'user','content': prompt}
        ],
        'temperature': temperature,
        'top_p': 1.0,
        'seed': seed
    }
    resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Adapt extraction depending on provider response shape
    choice = data.get('choices',[{}])[0]
    message = choice.get('message',{})
    content = message.get('content','')
    usage = data.get('usage',{})
    return {
        'raw': data,
        'text': content,
        'tokens_prompt': usage.get('prompt_tokens'),
        'tokens_completion': usage.get('completion_tokens'),
        'tokens_total': usage.get('total_tokens')
    }


def extract_metrics(run: Dict[str,Any]) -> Dict[str,Any]:
    text = run['response_text']
    tokens = text.split()
    lower_tokens = [t.lower().strip('.,!?') for t in tokens]
    warmth_hits = sum(1 for t in lower_tokens if t in WARMTH_LEXICON)
    uncertainty_hits = sum(1 for t in lower_tokens if t in UNCERTAINTY_MARKERS)
    structured = bool(STRUCTURE_REGEX.search(text))
    minimal_ack = bool(MINIMAL_ACK_PATTERN.match(text.strip()))
    return {
        'warmth_density': warmth_hits / max(len(tokens),1),
        'uncertainty_marker_density': uncertainty_hits / max(len(tokens),1),
        'structured_format': structured,
        'minimal_ack_compliance': minimal_ack
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--models', nargs='+', required=True)
    ap.add_argument('--prompts', required=True)
    ap.add_argument('--out-json', required=True, help='Raw runs JSONL')
    ap.add_argument('--metrics-out', required=True, help='Aggregated metrics JSON')
    ap.add_argument('--seeds', type=int, default=1, help='Seeds per prompt/model')
    ap.add_argument('--temperature', type=float, default=0.7)
    ap.add_argument('--dry-run', action='store_true', help='Skip API calls; emit placeholder outputs')
    args = ap.parse_args()

    prompts = load_prompts(args.prompts)
    all_runs = []

    for model in args.models:
        for p in prompts:
            for i in range(args.seeds):
                seed = 1000 + i
                if args.dry_run:
                    response = {
                        'raw': {},
                        'text': "Ready when you are" if p['category']=='pacing' else "This might be due to temperature variance and ventilation.",
                        'tokens_prompt': None,
                        'tokens_completion': None,
                        'tokens_total': None
                    }
                else:
                    response = call_model(model, p['text'], args.temperature, seed)
                    time.sleep(RATE_LIMIT_SLEEP)
                run_record = {
                    'prompt_id': p['id'],
                    'category': p['category'],
                    'model': model,
                    'seed': seed,
                    'temperature': args.temperature,
                    'response_text': response['text'],
                    'tokens_prompt': response['tokens_prompt'],
                    'tokens_completion': response['tokens_completion'],
                    'tokens_total': response['tokens_total'],
                    'timestamp': time.time()
                }
                all_runs.append(run_record)

    # Write raw
    with open(args.out_json,'w',encoding='utf-8') as f:
        for r in all_runs:
            f.write(json.dumps(r)+"\n")

    # Aggregate metrics
    metrics = {}
    for r in all_runs:
        key = (r['model'], r['category'])
        m = extract_metrics(r)
        metrics.setdefault(key, { 'warmth_density': [], 'uncertainty_marker_density': [], 'structured_format': 0, 'structured_n':0, 'minimal_ack_compliance':0, 'ack_n':0})
        agg = metrics[key]
        agg['warmth_density'].append(m['warmth_density'])
        agg['uncertainty_marker_density'].append(m['uncertainty_marker_density'])
        agg['structured_format'] += int(m['structured_format'])
        agg['structured_n'] += 1
        agg['minimal_ack_compliance'] += int(m['minimal_ack_compliance'])
        agg['ack_n'] += 1

    summary = []
    for (model, category), agg in metrics.items():
        summary.append({
            'model': model,
            'category': category,
            'warmth_density_mean': sum(agg['warmth_density'])/len(agg['warmth_density']),
            'uncertainty_density_mean': sum(agg['uncertainty_marker_density'])/len(agg['uncertainty_marker_density']),
            'structured_rate': agg['structured_format']/max(agg['structured_n'],1),
            'minimal_ack_rate': agg['minimal_ack_compliance']/max(agg['ack_n'],1)
        })

    with open(args.metrics_out,'w',encoding='utf-8') as f:
        json.dump({'summary': summary, 'runs': len(all_runs)}, f, indent=2)
    print(f"Probe runs written: {len(all_runs)}; metrics -> {args.metrics_out}")

if __name__ == '__main__':
    main()
