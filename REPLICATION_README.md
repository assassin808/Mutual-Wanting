# Replication Guide (Minimal)

This guide explains how to regenerate tables and figures without distributing raw Reddit content.

## 1. Environment
- Python 3.10+
- Recommended: create a virtual environment

## 2. Quick Reproduce (partial pipeline)
Run: `make reproduce-all`
Outputs land in `pipeline/outputs/`.

## 3. Figures
- System diagram: open `figures/drawio/exports/system.xml` in Draw.io Desktop and export SVG/PNG/HTML. Then run `make paper` to include.
- Fig2: Replace placeholder asset when provided, or render from `pipeline/outputs/figs/confusion_heatmap.csv` via `make fig2`.

## 4. Data Notes
- Use your own Reddit exports that match our schema. Validate with `pipeline/jsonl_schema_check.py`.
- Do not commit raw user text.

## 5. Probes
- Configure API keys as environment variables; run `make probes` (cost-bounded).

## 6. Troubleshooting
- See `pipeline/outputs/lint_report.json` and `pipeline/outputs/artifact_validation.json`.

Updated: 2025-09-10
