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
