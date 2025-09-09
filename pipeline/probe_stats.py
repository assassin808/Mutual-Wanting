#!/usr/bin/env python3
"""Compute basic probe metrics from a filled probes manifest (no API calls).

Expected manifest fields:
  responses: list of {model, prompt_id, text, metrics: {cdr:0/1, sur:0/1, ...}}
Outputs summary TSV and JSON.
"""
import argparse, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default='pipeline/outputs/probes_manifest.json')
    ap.add_argument('--out-json', default='pipeline/outputs/probes_results.json')
    ap.add_argument('--out-tsv', default='pipeline/outputs/tables/probes_summary.tsv')
    args = ap.parse_args()

    if not os.path.exists(args.manifest):
        print('Manifest not found; skipping probe stats.')
        return
    with open(args.manifest, 'r', encoding='utf-8') as f:
        man = json.load(f)
    rows = man.get('responses', [])
    # Aggregate simple mean per metric by model
    by_model = {}
    for r in rows:
        m = r.get('model')
        met = r.get('metrics', {})
        by_model.setdefault(m, {})
        for k, v in met.items():
            acc = by_model[m].setdefault(k, {'sum':0.0,'n':0})
            try:
                acc['sum'] += float(v)
                acc['n'] += 1
            except Exception:
                pass
    summary = {}
    for m, md in by_model.items():
        summary[m] = {k: (v['sum']/v['n'] if v['n'] else None) for k, v in md.items()}

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary}, f, indent=2)
    os.makedirs(os.path.dirname(args.out_tsv), exist_ok=True)
    with open(args.out_tsv, 'w', encoding='utf-8') as f:
        f.write('model\tmetric\tmean\n')
        for m, md in summary.items():
            for k, v in md.items():
                f.write(f"{m}\t{k}\t{v if v is not None else ''}\n")
    print(f"Probe stats -> {args.out_json}; {args.out_tsv}")


if __name__ == '__main__':
    main()
