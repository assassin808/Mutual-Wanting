# First Author Active TODO (Rolling)

Legend: [ ] pending, [~] in progress, [x] done.

## Data & Labeling
- [ ] Acquire authentic GPT-4 -> GPT-4o pre/post Reddit archives (export tool) -> place under `pipeline/data/historical_{pre,post}.jsonl`.
- [ ] Run `historical_backfill_stub.py` to produce combined normalized JSONL.
- [ ] Sampling: generate enriched + baseline random batch (target 600 items) with stratified score buckets.
- [ ] Dual split: `split_for_dual_annotation.py` (overlap >= 15%).
- [ ] Round 1 overlap labeling (A/B) + run agreement & disagreement report.
- [ ] Guideline refinement (update ambiguous tag definitions) referencing disagreement guidance.
- [ ] Round 2 labeling until kappa > 0.65.
- [ ] Merge consensus + enrichment evaluation.

## Lexical & Feature Analysis
- [ ] Run drift_lexicon + drift_bootstrap on authentic pre/post.
- [ ] Filter tokens: freq floor >=10 & sign_consistency >=0.8 for reporting list.
- [ ] Expand warmth markers set if recall < 0.9 on manual check sample (random 50 complaints).
- [ ] Recompute features_rows.csv; verify distributions (e.g., hedge_rate median).

## Modeling
- [ ] Regression: any_complaint + category models (skip insufficient counts).
- [ ] Inspect interaction coefficients; flag substantive |coef| > 0.5 for narrative.
- [ ] Sensitivity: vary MIN_CLASS (8 vs 10) and confirm stability of significant interactions.

## Probes
- [ ] Finalize model list (historical & current accessible variants).
- [ ] Rotate API key & set env var (no commit).
- [ ] Run probe_runner with max_prompts cap (dry run) -> verify metric extraction.
- [ ] Full probe run; compute per-model metrics (CDR, SUR, ETD, SST proxy, CPR, DRP).
- [ ] Statistical comparison: pairwise proportion tests for CDR/SUR across versions.

## Tables & Manuscript Integration
- [ ] Run table_prep for agreement, enrichment, drift, regression.
- [ ] Add placeholders/results tables into LaTeX (macro or \input). 
- [ ] Insert probe metrics table & drift stability appendix table.
- [ ] Draft Results section subsections (Reliability, Enrichment Bias, Drift, Behavioral Probes, Modeling Effects).
- [ ] Write Discussion framing (mutual wanting axes with empirical values).

## Ethics & Reproducibility
- [ ] Codify paraphrasing rule for quoted Reddit snippets (>= 5 word change + preserve meaning).
- [ ] Add README subsection listing gating criteria and data exclusion policies.
- [ ] Prepare artifact release checklist (scripts, prompts, lexicons, anonymization note).

## Validation & Risk Checks
- [ ] Kappa stability across batches (plot if >2 batches) to detect annotator drift.
- [ ] Drift token stability vs boot iterations (boot counts 100, 200, 400) to ensure convergence.
- [ ] Regression robustness: re-run with shuffled pre_post labels to confirm null distribution (placebo test).
- [ ] Probe reproducibility: re-run subset on different day/time; measure variance.

## Stretch (If Time)
- [ ] Topic modeling (BERTopic) for higher-level theme grouping.
- [ ] User cluster feature analysis (k-means) and cluster-specific complaint incidence.
- [ ] Exploratory embedding similarity drift for warmth adjectives.

(Updated: 2025-08-31 UTC)
