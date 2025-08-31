#!/usr/bin/env python3
"""End-to-end orchestration helper for Mutual Wanting Alignment study.

This script stitches existing modular steps with explicit checkpoints, producing
artifacts ready to drop into manuscript tables. It is intentionally linear and
transparent (no hidden state) so each phase can be inspected / resumed.

Phases (toggle with --phase or run all by default):
  1. backfill      : Validate + combine historical pre/post archives (uses historical_backfill_stub.py)
  2. sample        : Create labeling batch CSV(s) (sample_for_labeling.py / mixed_sample.py as needed)
  3. split         : Split batch for dual annotation (--batch-path)
  4. agreement     : Compute agreement & disagreement report (agreement.py + disagreement_report.py)
  5. merge         : Merge annotated CSVs into consensus (merge_annotations.py)
  6. enrichment    : Evaluate enrichment sampling bias (enrichment_eval.py)
  7. features      : Extract per-row features (features_and_analysis.py)
  8. drift         : Lexical drift + bootstrap stability (drift_lexicon.py + drift_bootstrap.py)
  9. regress       : Run logistic regressions (regression_skeleton.py)
 10. probes        : Run probe suite (probe_runner.py)

Each phase checks for expected inputs and skips if outputs already present unless --force.

Example minimal usage (after obtaining archives & completing labeling):
  python pipeline/orchestrate_pipeline.py --phase drift --pre-json pipeline/data/historical_pre.jsonl \
      --post-json pipeline/data/historical_post.jsonl --out-dir pipeline/outputs

Outputs are placed under an out directory (default pipeline/outputs/<date>/...).
"""
from __future__ import annotations
import argparse, subprocess, sys, os, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DEFAULT_OUT = ROOT / 'outputs'

PHASES = [
    'backfill','coverage','sample','split','agreement','merge','enrichment','features','drift','regress','probes','probe_stats'
]


def run(cmd: list[str]):
    print('[run]', ' '.join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip():
        print(res.stderr.strip())


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def phase_backfill(args, outdir: Path):
    if not (args.pre_archive and args.post_archive):
        print('Skipping backfill (archives not provided).')
        return None
    combined = outdir / 'historical_combined.jsonl'
    if combined.exists() and not args.force:
        print('Backfill already exists.')
        return combined
    run([
        sys.executable, str(ROOT / 'historical_backfill_stub.py'),
        '--pre-archive', args.pre_archive,
        '--post-archive', args.post_archive,
        '--out', str(combined)
    ])
    return combined


def phase_coverage(args, outdir: Path):
    if not (args.pre_json and args.post_json):
        print('Skipping coverage (need --pre-json & --post-json).')
        return None
    report = outdir / 'archive_coverage.json'
    if report.exists() and not args.force:
        print('Archive coverage exists.')
        return report
    run([
        sys.executable, str(ROOT / 'archive_coverage.py'),
        '--pre', args.pre_json,
        '--post', args.post_json,
        '--out', str(report)
    ])
    return report


def phase_sample(args, outdir: Path):
    if not args.raw_json:
        print('Skipping sampling (raw JSON not provided).')
        return None
    batch = outdir / 'label_batch.csv'
    if batch.exists() and not args.force:
        print('Sample exists.')
        return batch
    run([
        sys.executable, str(ROOT / 'sample_for_labeling.py'),
        '--raw', args.raw_json,
        '--out', str(batch),
        '--n', str(args.sample_n)
    ])
    return batch


def phase_split(args, outdir: Path):
    if not args.batch_path:
        print('Skipping split (no --batch-path).')
        return None
    a = outdir / 'label_batch_A.csv'
    b = outdir / 'label_batch_B.csv'
    if a.exists() and b.exists() and not args.force:
        print('Split outputs exist.')
        return a, b
    run([
        sys.executable, str(ROOT / 'split_for_dual_annotation.py'),
        '--in', args.batch_path,
        '--out-prefix', str(outdir / 'label_batch'),
        '--overlap', str(args.overlap),
        '--seed', str(args.seed)
    ])
    return a, b


def phase_agreement(args, outdir: Path):
    if not (args.annot_a and args.annot_b):
        print('Skipping agreement (annotator files missing).')
        return None
    agree_json = outdir / 'agreement.json'
    if agree_json.exists() and not args.force:
        print('Agreement already computed.')
    else:
        run([
            sys.executable, str(ROOT / 'agreement.py'),
            '--a', args.annot_a,
            '--b', args.annot_b,
            '--out', str(agree_json)
        ])
    disagree_json = outdir / 'disagreement_report.json'
    if disagree_json.exists() and not args.force:
        print('Disagreement report exists.')
    else:
        run([
            sys.executable, str(ROOT / 'disagreement_report.py'),
            '--agreement-json', str(agree_json),
            '--out-json', str(disagree_json)
        ])
    return agree_json, disagree_json


def phase_merge(args, outdir: Path):
    if not args.consensus_inputs:
        print('Skipping merge (no --consensus-inputs).')
        return None
    out_csv = outdir / 'labels_consensus.csv'
    out_json = outdir / 'labels_consensus_summary.json'
    if out_csv.exists() and not args.force:
        print('Consensus already exists.')
        return out_csv
    run([
        sys.executable, str(ROOT / 'merge_annotations.py'),
        '--inputs', *args.consensus_inputs,
        '--out-csv', str(out_csv),
        '--out-json', str(out_json)
    ])
    return out_csv


def phase_enrichment(args, outdir: Path):
    if not (args.enriched_labeled and args.baseline_labeled):
        print('Skipping enrichment (need both --enriched-labeled & --baseline-labeled).')
        return None
    out_json = outdir / 'enrichment_eval.json'
    if out_json.exists() and not args.force:
        print('Enrichment eval exists.')
        return out_json
    run([
        sys.executable, str(ROOT / 'enrichment_eval.py'),
        '--enriched-labeled', args.enriched_labeled,
        '--baseline-labeled', args.baseline_labeled,
        '--out', str(out_json)
    ])
    return out_json


def phase_features(args, outdir: Path):
    if not args.consensus_csv:
        print('Skipping features (no --consensus-csv).')
        return None
    summary_json = outdir / 'features_summary.json'
    perrow_csv = outdir / 'features_rows.csv'
    if summary_json.exists() and not args.force:
        print('Features summary exists.')
        return perrow_csv
    run([
        sys.executable, str(ROOT / 'features_and_analysis.py'),
        '--labeled', args.consensus_csv,
        '--out', str(summary_json),
        '--emit-csv', str(perrow_csv)
    ])
    return perrow_csv


def phase_drift(args, outdir: Path):
    if not (args.pre_json and args.post_json):
        print('Skipping drift (need --pre-json & --post-json).')
        return None
    drift_json = outdir / 'drift_log_odds.json'
    if not drift_json.exists() or args.force:
        run([
            sys.executable, str(ROOT / 'drift_lexicon.py'),
            '--pre', args.pre_json,
            '--post', args.post_json,
            '--out-json', str(drift_json),
            '--freq-floor', str(args.drift_freq_floor)
        ])
    boot_json = outdir / 'drift_bootstrap.json'
    if not boot_json.exists() or args.force:
        run([
            sys.executable, str(ROOT / 'drift_bootstrap.py'),
            '--pre', args.pre_json,
            '--post', args.post_json,
            '--freq-floor', str(args.drift_freq_floor),
            '--boots', str(args.drift_boots),
            '--out', str(boot_json)
        ])
    return drift_json, boot_json


def phase_regress(args, outdir: Path):
    if not args.consensus_csv:
        print('Skipping regress (no consensus labels).')
        return None
    features_csv = outdir / 'features_rows.csv'
    if not features_csv.exists():
        print('Need features_rows.csv (run features phase first).')
        return None
    out_json = outdir / 'regression_results.json'
    if out_json.exists() and not args.force:
        print('Regression results exist.')
        return out_json
    run([
        sys.executable, str(ROOT / 'regression_skeleton.py'),
        '--labeled', str(features_csv),
        '--out', str(out_json)
    ])
    return out_json


def phase_probes(args, outdir: Path):
    if not args.prompts_json:
        print('Skipping probes (no --prompts-json).')
        return None
    out_json = outdir / 'probes_results.json'
    if out_json.exists() and not args.force:
        print('Probe results exist.')
        return out_json
    cmd = [
        sys.executable, str(ROOT / 'probe_runner.py'),
        '--prompts-json', args.prompts_json,
        '--out', str(out_json)
    ]
    if args.models:
        cmd += ['--models', *args.models]
    if args.max_prompts:
        cmd += ['--max-prompts', str(args.max_prompts)]
    run(cmd)
    return out_json


def phase_probe_stats(args, outdir: Path):
    if not args.probes_json:
        print('Skipping probe_stats (need --probes-json).')
        return None
    out_json = outdir / 'probe_stats.json'
    if out_json.exists() and not args.force:
        print('Probe stats exist.')
        return out_json
    metrics = args.probe_metrics or ['cdr','sur']
    run([
        sys.executable, str(ROOT / 'probe_stats.py'),
        '--probes-json', args.probes_json,
        '--metrics', *metrics,
        '--out', str(out_json)
    ])
    return out_json


PHASE_FUNC = {
    'backfill': phase_backfill,
    'coverage': phase_coverage,
    'sample': phase_sample,
    'split': phase_split,
    'agreement': phase_agreement,
    'merge': phase_merge,
    'enrichment': phase_enrichment,
    'features': phase_features,
    'drift': phase_drift,
    'regress': phase_regress,
    'probes': phase_probes,
    'probe_stats': phase_probe_stats
}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=PHASES, help='Run a single phase (else run all)')
    ap.add_argument('--out-root', default=str(DEFAULT_OUT))
    ap.add_argument('--force', action='store_true')
    # Backfill
    ap.add_argument('--pre-archive')
    ap.add_argument('--post-archive')
    # Sampling
    ap.add_argument('--raw-json', help='Raw combined window JSONL for sampling')
    ap.add_argument('--sample-n', type=int, default=300)
    # Split
    ap.add_argument('--batch-path', help='Existing batch CSV to split')
    ap.add_argument('--overlap', type=int, default=40)
    ap.add_argument('--seed', type=int, default=42)
    # Agreement
    ap.add_argument('--annot-a')
    ap.add_argument('--annot-b')
    # Merge
    ap.add_argument('--consensus-inputs', nargs='+')
    # Enrichment
    ap.add_argument('--enriched-labeled')
    ap.add_argument('--baseline-labeled')
    # Features / regress
    ap.add_argument('--consensus-csv')
    # Drift
    ap.add_argument('--pre-json')
    ap.add_argument('--post-json')
    ap.add_argument('--drift-freq-floor', type=int, default=10)
    ap.add_argument('--drift-boots', type=int, default=200)
    # Probes
    ap.add_argument('--prompts-json')
    ap.add_argument('--models', nargs='+')
    ap.add_argument('--max-prompts', type=int)
    ap.add_argument('--probes-json', help='Existing probes results JSON for stats phase')
    ap.add_argument('--probe-metrics', nargs='+', help='Binary probe metrics to compare (default cdr sur)')
    return ap.parse_args()


def main():
    args = parse_args()
    datestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M')
    outdir = Path(args.out_root) / datestamp if not args.phase else Path(args.out_root)
    ensure_dir(outdir)

    phases_to_run = [args.phase] if args.phase else PHASES

    results_index = {}
    for ph in phases_to_run:
        fn = PHASE_FUNC[ph]
        print(f"=== Phase: {ph} ===")
        try:
            res = fn(args, outdir)
            if res is not None:
                results_index[ph] = [str(r) for r in (res if isinstance(res, (list, tuple)) else [res])]
        except SystemExit:
            raise
        except Exception as e:
            print(f"[error] phase {ph} failed: {e}")
            break

    # Write index manifest
    manifest = outdir / 'manifest.json'
    with open(manifest, 'w', encoding='utf-8') as f:
        json.dump({'phases': phases_to_run, 'artifacts': results_index}, f, indent=2)
    print(f"Manifest -> {manifest}")

if __name__ == '__main__':
    main()
