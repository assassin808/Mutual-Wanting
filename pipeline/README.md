# Pipeline Overview (Operational)

Goal: Lightweight, reproducible extraction, sampling, labeling, probing, and analysis of Reddit complaints and model behavior across GPT version transitions.

## Core Phases
1. Fetch / Backfill: Collect or externally export Reddit comments for canonical pre/post windows.
2. Sample: Stratify by engagement (score buckets) and pre/post.
3. Split: Dual-annotation split with controlled overlap for reliability.
4. Label: Human annotation using `labeling_guidelines.md` + refinement cycles.
5. Agreement & Disagreement Report: Compute kappa + surface confusion pairs.
6. Merge & Consensus: Majority + tie flagging.
7. Enrichment Evaluation: Quantify sampling precision/recall & relative risk.
8. Features: User style / linguistic features.
9. Drift: Lexical log-odds + bootstrap stability filtering.
10. Regression: Complaint incidence modeling with interaction.
11. Probes: Behavioral prompt suite across API model versions.
12. Table Prep: Convert JSON artifacts into manuscript-ready TSV tables.

## Directory Layout
```
pipeline/
  labeling_guidelines.md
  README.md
  fetch_reddit.py          # placeholder
  sample_for_labeling.py   # placeholder
  features_and_analysis.py # placeholder
  util_text.py             # placeholder helper functions
  data/                    # raw and processed JSONL/CSV (gitignored recommended)
```

## Transitions & Windows (Tentative)
| Transition | Pre Window | Post Window |
|------------|-----------:|------------:|
| 3.5→4 | -14d to -1d | +0d to +28d |
| 4→4o  | -14d to -1d | +0d to +28d |
| 4o→5  | -14d to -1d | +0d to +28d |

Adjust if volume too large; we can subsample chronologically.

## Target Counts
~300 labeled comments pre + 300 post per transition → ~1,800. If time constrained, reduce to 200/200 (1,200 total).

## User Style Feature Sketch
- token_len, avg_sentence_len
- hedge_rate (list: maybe,could,perhaps,might,seems,appears,possibly)
- warmth_markers (thank, please, appreciate, love, enjoy)
- imperative_ratio (imperative verbs / verbs total heuristic)
- pronoun_personal_ratio (I,we,you occurrences / tokens)

## Statistical Models
Logistic regression for each complaint primary tag (one-vs-rest):
```
logit(tag ~ transition + pre_post + transition:pre_post + user_style_cluster + score_bucket)
```
Cluster: k-means (k=5) over standardized features.

## Key Scripts Added
| Script | Purpose |
|--------|---------|
| `historical_backfill_stub.py` | Normalize externally exported Reddit archives and tag pre/post. |
| `multi_backfill_stub.py` | Normalize multiple transitions from YAML + archive map. |
| `multi_fetch_windows.py` | Batch fetch all transition pre/post windows + manifest. |
| `transitions.yaml` | Canonical transition window configuration. |
| `archive_coverage.py` | Validate coverage of raw pre/post archives (day counts, sparsity). |
| `fetch_window_reddit.py` | Build focused raw window archives (Pushshift fallback). |
| `split_for_dual_annotation.py` | Create annotator A/B CSVs with overlap subset. |
| `agreement.py` | Compute Cohen's kappa + confusion matrix. |
| `disagreement_report.py` | Rank confusion pairs & emit remediation guidance. |
| `merge_annotations.py` | Build consensus labels & disagreement summary. |
| `enrichment_eval.py` | Evaluate keyword enrichment precision, recall proxy, relative risk. |
| `features_and_analysis.py` | Per-row feature extraction + aggregate summary. |
| `drift_lexicon.py` | Log-odds lexical drift (frequency floor guarded). |
| `drift_bootstrap.py` | Drift token stability via bootstrap sign consistency. |
| `regression_skeleton.py` | Logistic modeling with separation safeguards. |
| `probe_runner.py` | Execute probe prompt suite vs API models (behavioral metrics). |
| `probe_stats.py` | Pairwise proportion tests over probe metrics. |
| `orchestrate_pipeline.py` | One-stop phase orchestrator with resumable outputs. |
| `table_prep.py` | Collate JSON artifacts into TSV tables for manuscript. |
| `regression_placebo.py` | Null distribution (shuffled pre_post) for interaction effect sanity. |
| `drift_trend.py` | Cross-transition drift trend stability. |
| `regression_placebo.py` | Null distribution for interaction effect sanity. |

## Primary JSON/TSV Artifacts
| Artifact | Source Phase | Notes |
|----------|--------------|-------|
| `agreement.json` | agreement | Contains kappa & confusion matrix. |
| `disagreement_report.json` | disagreement_report | Heuristic remediation guidance. |
| `labels_consensus.csv` | merge | Consensus primary tags (ties flagged). |
| `enrichment_eval.json` | enrichment | Precision, prevalence, relative risk, recall estimate. |
| `features_rows.csv` | features | Per-row merged labels + features for modeling. |
| `drift_log_odds.json` | drift | Top tokens each side (freq floor applied). |
| `drift_bootstrap.json` | drift | Token stability metrics (mean z, std, sign consistency). |
| `regression_results.json` | regress | Model coefficients (interaction focus). |
| `probes_results.json` | probes | Behavioral metrics per model/prompt. |
| `tables/*.tsv` | table_prep | Manuscript-ready condensed tables. |

## Dependencies
Install optional analysis libraries (skip if only preparing raw labels):

```
pip install -r pipeline/requirements.txt
```

## Quick Mock Run (Synthetic)
```
python pipeline/fetch_reddit.py --out pipeline/data/mock_raw.jsonl --limit 120
python pipeline/sample_for_labeling.py --raw pipeline/data/mock_raw.jsonl --out pipeline/data/sample_labels.csv --n 60
python pipeline/features_and_analysis.py --labeled pipeline/data/sample_labels.csv --out pipeline/data/summary.json
```
(You will need to manually fill primary_tag values in the CSV to see meaningful analysis.)

## Annotation Aids
See `pipeline/labeling_guidelines.md` and `pipeline/annotation_examples.md` for calibration.

### Pilot-Specific Tools (Submissions Dataset)
For the pilot submission-focused batch (`pilot_batch.csv`):
* Use `pilot_split_for_dual_annotation.py` to create `_A` / `_B` splits plus overlap IDs (default overlap=20 for 60-item pilot).
* Annotators label with `annotation_tool_pilot.py`, which implements the updated tag set from `labeling_guidelines.md` (WARMTH_LOSS, CREATIVITY_DROP, etc.).
* Overlap IDs file feeds into reliability computation (extend `agreement.py` to handle the pilot field schema: map `id` -> primary_tag for both annotators, then compute Cohen's kappa).

Legacy comment-batch scripts (`split_for_dual_annotation.py`, `annotation_tool.py`) remain for window-based comment corpora (fields: comment_id/body/etc.).

## Orchestration Usage
Single phase (e.g., drift only):
```
python pipeline/orchestrate_pipeline.py --phase drift \
  --pre-json pipeline/data/historical_pre.jsonl \
  --post-json pipeline/data/historical_post.jsonl \
  --out-root pipeline/outputs
```
Full run (provide inputs progressively; phases skip missing prerequisites):
```
python pipeline/orchestrate_pipeline.py --out-root pipeline/outputs \
  --pre-archive exported_pre.jsonl --post-archive exported_post.jsonl \
  --raw-json pipeline/outputs/historical_combined.jsonl --sample-n 600 \
  --batch-path pipeline/outputs/label_batch.csv --overlap 60 \
  --annot-a pipeline/outputs/label_batch_A.csv --annot-b pipeline/outputs/label_batch_B.csv \
  --consensus-inputs pipeline/outputs/label_batch_A_annotated.csv pipeline/outputs/label_batch_B_annotated.csv \
  --consensus-csv pipeline/outputs/labels_consensus.csv \
  --pre-json pipeline/data/historical_pre.jsonl --post-json pipeline/data/historical_post.jsonl \
  --prompts-json pipeline/data/prompts.json
```
Then prepare tables:
```
python pipeline/table_prep.py --agreement pipeline/outputs/agreement.json \
  --enrichment pipeline/outputs/enrichment_eval.json \
  --regress pipeline/outputs/regression_results.json \
  --drift-lex pipeline/outputs/drift_log_odds.json \
  --drift-boot pipeline/outputs/drift_bootstrap.json \
  --out-dir pipeline/outputs/tables
```

## Reliability & Stability Gates
- Annotation phase proceeds until Cohen's kappa > 0.65 (refinement cycles guided by `disagreement_report.py`).
- Drift tokens reported only if frequency floor met (>=10 each side) AND sign_consistency >= 0.8 (bootstrap).
- Regression models skipped for outcomes failing MIN_CLASS threshold (>=8 positives & negatives).

## Next Immediate Actions (if resuming mid-project)
1. Run `multi_fetch_windows.py` to create per-transition pre/post archives + `archive_map.json` (or supply externally exported archives and build map manually).
2. Run orchestrator `--phase multi_backfill` with `--transitions` + `--archive-map` to generate `multi_transitions.jsonl`.
3. Run coverage phase (archive completeness) then sampling.
4. Split, dual annotation, agreement + disagreement refinement cycles until kappa > 0.65.
5. Merge, enrichment eval, features, drift + bootstrap, regressions.
6. Run probes, probe_stats, regression_placebo, drift_trend for robustness.
7. Table prep & manuscript Results population.

### Interim (No Archive Dumps Yet) Data Capture
When you **do not** yet have historical Pushshift (or equivalent) dumps, you can still harvest the maximum RECENT + TOP historical surface via the API using `limited_historical_scrape.py`:

```
python pipeline/limited_historical_scrape.py \
  --subreddits-file pipeline/subreddits.txt \
  --out-dir pipeline/data/live_scrape \
  --keywords "gpt,openai,persona" --max-per-view 1000
```

Outputs: one `<sub>_aggregate.jsonl` per subreddit plus per‑sub summaries and a `scrape_manifest.json`.

Limitations: This **cannot** reconstruct full historical pre windows; it only unions what each listing (new/top/controversial + keyword searches) still exposes (each capped at ~1000). Use solely for exploratory feature prototyping until real archives are ingested.

## Environment Variables (Reddit API)
Set locally (do NOT commit secrets):
```
export REDDIT_CLIENT_ID="<your_client_id>"
export REDDIT_CLIENT_SECRET="<your_client_secret>"
export REDDIT_USER_AGENT="PersonaDriftStudy/0.1 by Yang"
# Optional (script auth if needed)
export REDDIT_USERNAME="<reddit_username>"
export REDDIT_PASSWORD="<reddit_password>"
```
Synthetic fallback has been fully disabled; absence of credentials will now just limit live fetch attempts (historical relies on local archives only).

## Subreddit Configuration
Create a simple text file `pipeline/subreddits.txt` listing one subreddit per line (e.g., `ChatGPT`, `OpenAI`, `ArtificialInteligence`). The fetch script will read it if present.

## Release Dates Configuration
Adjust `RELEASES` dict in `fetch_reddit.py` once exact GPT-5 public date is confirmed.
