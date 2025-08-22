# Project Progress Log

Date: 2025-08-21

## New Actions This Session
- Added automatic `.env` loader to `fetch_reddit.py` (loads credentials if not exported).
- Integrated environment variable documentation previously; now operational without manual export if `.env` present.
- Ready for first live fetch run (use `--live`).

## Current Pipeline Integrity
Components present: fetch (with live + synthetic), sampling (stratified), labeling guidelines + examples, feature extraction, regression scaffold.

## Immediate Next Targets
1. Execute live fetch (limit 300–500) across configured subreddits.
2. Generate first stratified sample CSV for pilot labeling (n=200) and compute feature summary.
3. After labeling pilot: run regression scaffold (install dependencies) and record preliminary proportions.

## Risks / Notes
- Release date for GPT-5 still placeholder; adjust before final analyses.
- Need subreddit list file `pipeline/subreddits.txt` for domain coverage.

## Pending Decisions
- Final label count (1,800 vs 1,200) based on annotation throughput.
- Whether to include any additional social platforms (currently none planned to stay minimal).

## Added Subreddit List
Created `pipeline/subreddits.txt` with tiered groups:
- Core: ChatGPT, OpenAI, GPT3, GPT4
- Prompt/usage: PromptEngineering, AIprompting
- General AI: ArtificialIntelligence, singularity
- Practitioner: LanguageTechnology, MachineLearning, LocalLLaMA
- Safety: AISafety
- Additional hubs: AIPromptHub, AIChat

Rationale: capture high-salience complaint sources (core + prompt) plus contrast/control domains (practitioner, safety) and open-weight community (LocalLLaMA) for differential framing of persona drift vs capability.

## Next Action
Run first live fetch (limit 500) and inspect class balance across transitions; adjust keyword filter later if general subs yield excessive noise.

-- End of entry --

## Session Update (Subsequent)
- Enhanced `fetch_reddit.py` with subreddit-level exception handling and early abort safety.
- Fixed serialization (subreddit object) by coercing to display name.
- Successful live fetch (120 rows) despite 403 on some subs (e.g., GPT4) -> stored at `pipeline/data/live_raw.jsonl`.
- Created first stratified sample (`pipeline/data/label_batch1.csv`, n=60) for pilot labeling.
- Extended `features_and_analysis.py` with `--raw` mode; produced preliminary summary (`feature_summary.json`).

### Immediate Next Steps
1. Increase fetch volume (iterate higher limits; consider time-bounded queries) to obtain pre/post diversity (currently only future-post window due to placeholder release date interpreting current timestamps as post-transition).
2. Commence manual labeling on `label_batch1.csv`; save annotated copy and compute inter-annotator agreement if multiple raters.
3. Add bot / moderation filter heuristic (e.g., remove bodies matching auto-mod patterns) before next sampling.
4. Insert preliminary descriptive stats into manuscript (`agents4science_2025.tex`).
5. Replace GPT-5 placeholder release date with actual (or shift placeholder forward to avoid all data marked post).

### Notes
- Need historical retrieval method (Pushshift successor / monthly dumps) for genuine pre windows; current API only yields recent posts.
- Consider adding a keyword filter (e.g., complaints terms list) to enrich target density for labeling efficiency.

### Session Continuation Addendum
- Implemented keyword/length/bot filtering in fetch script; created `pipeline/keywords.txt`.
- Filtered fetch run: 400 raw -> 23 retained complaint-relevant rows (high precision, low recall) all tagged post (placeholder release date issue persists).
- Added JSON summary output for distribution auditing.
- Next: adjust release dates or backfill historical to achieve pre samples; consider relaxing min length or expanding limit for better retention.
- Added minimal CLI `annotation_tool.py` for in-terminal labeling; smoke test generated `_annotated` CSV.
- Generated provisional pre/post descriptive stats combining filtered passes (32 pre, 23 post). Early lexeme frequencies: 'worse' dominant; latency & memory co-occur; high-score complaints sparse.
- Expanded keyword lexicon (warmth + creativity paraphrases). New enriched fetch: 800 raw -> 63 retained (retention 7.9%, improved coverage). Still pre-only due to synthetic anchor.
- Mixed sample batch2 generated (target 140, actual 119 due to available enriched size): enriched=63, baseline=56.
- Generated per-row feature CSV (expanded enriched set) via updated features script for upcoming modeling.
- Added historical backfill scaffold script (GPT-4 -> 4o) awaiting external archive exports.

### Synthetic Pipeline Validation (2025-08-22)
- Created `generate_synthetic_labels.py` to assign synthetic complaint tags (controlled randomization; optional post flips) for end-to-end smoke test.
- Produced `label_batch2_synth_annotated.csv` (n=119) mirroring mixed sample schema.
- Ran `features_and_analysis.py --labeled` on synthetic file; initial failure due to strict CSV DictWriter fieldnames (missing union of dynamic feature keys) resulting in ValueError; patched script to compute union across all rows prior to writer initialization.
- Generated per-row feature export (`feature_rows_synth.csv`) and summary (`feature_summary_synth.json`).
- Executed `regression_skeleton.py` on synthetic labels; several models produced extreme coefficients / singular matrix errors (e.g., warmth_regression, verbosity_change) consistent with quasi-separation in synthetic data. Captured outputs in `regression_synth.json`.
- Logged convergence warnings (overflow in exp / singular matrix) indicating need for: (a) penalized logistic fallback, (b) minimum positive class count threshold before modeling.
- Ran restricted drift lexicon analysis (`drift_lexicon.py --restrict-lexicon complaint_focus_lexicon.txt`) producing `drift_log_odds_restricted.json`; extremely low token counts (many <5 per side) underline current instability; will enforce token frequency floor (≥10 per side) before interpretive use.
- Confirmed acquisition→sample→label (synthetic)→features→regression→drift path operational end-to-end.

### Updated Immediate Next Actions
1. Manual Labeling: Begin real annotation on `label_batch2.csv` (retain synthetic variant only for tooling regression tests). Target: ≥120 labeled within 24h; designate 25 overlapping items for second rater to compute Cohen's κ (goal >0.65).
2. Reliability: After dual labels, run `agreement.py` then `merge_annotations.py` to produce consensus set for modeling.
3. Modeling Hardening: Implement automatic fallback to L2-penalized logistic (scikit-learn) when statsmodels GLM fails or class counts < threshold; skip models where minority class <8.
4. Drift Stability: Add frequency floor filter & caching of token counts; re-run restricted drift only after both sides have ≥150 total tokens and each candidate term ≥10 per side.
5. Historical Backfill: Populate `historical_backfill_stub.py` with actual GPT-4→4o archive files (expected JSONL). On ingestion, recompute sampling ensuring authentic pre/post rather than placeholder-based tagging.
6. Enrichment Evaluation: Add utility to estimate precision/recall of keyword filter using baseline-labeled subset; adjust lexicon accordingly (track F1).
7. Manuscript Update: Insert note distinguishing synthetic pipeline validation from empirical findings; add planned safeguards (penalized models, token frequency floors) to Methods.

### Risks / Mitigations (Update)
- Synthetic overfitting / separation -> add penalization + thresholds (Mitigation in progress).
- Sparse lexical counts -> enforce frequency floors + optionally merge synonyms.
- Annotation throughput uncertainty -> prioritize enriched subset; adjust baseline proportion dynamically.
- Delay in historical archive acquisition -> parallelize labeling of recent (post) data while sourcing pre archives; maintain explicit provenance labels.

-- End of 2025-08-22 update --

### Implementation Note (Modeling Hardening Executed 2025-08-22)
- Updated `regression_skeleton.py` with: class count threshold (MIN_CLASS=8), statsmodels primary fit, scikit-learn L2 logistic fallback when failures (separation / singular matrix) occur, explicit estimator annotation, and skip metadata when insufficient data. Purpose: prevent spurious large coefficients influencing narrative about persona drift (ensures only adequately supported complaint shift signals enter manuscript). Pending: integrate into manuscript Methods (Robustness subsection).
