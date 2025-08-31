# Annotation Refinement & Reliability Protocol

Version: 0.1 (2025-08-31)

## 1. Overlap Sampling Strategy
- Overlap size per batch: max(25, ceil(0.15 * batch_size)).
- Selection: stratified by current provisional primary_tag distribution (if unknown, random uniform) + ensure at least 3 examples per frequent tag (WARMTH_LOSS, HELPFULNESS_REGRESSION, CREATIVITY_DROP).

## 2. Reliability Metrics
Primary: Cohen's κ over full primary tag set.
Secondary: Per-class F1 (treating other tags as negative) for top 5 prevalent complaint tags.
Stability Trigger: If κ < 0.65 OR any major tag F1 < 0.60, trigger refinement cycle.

## 3. Refinement Cycle Steps
1. Disagreement Audit: Extract all items with annotator tag mismatch OR ties post `merge_annotations.py`.
2. Categorize disagreements by confusion pairs (e.g., WARMTH_LOSS vs VERBOSITY_CHANGE).
3. For top 3 confusion pairs by frequency, produce side-by-side examples and craft discriminative rule additions (one-line heuristic per pair).
4. Update `labeling_guidelines.md` with a new Ambiguity Case subsection listing rule additions.
5. Re-label 10% sample of affected categories (minimum 10 items) using updated rules.
6. Recompute κ; accept cycle if κ improvement ≥ 0.05 OR κ ≥ threshold.

## 4. Drift Monitoring
Every 200 new annotations:
- Randomly sample 20 previously labeled items; second annotator re-labels blind.
- Compute test-retest agreement; if decline > 0.07 absolute, perform micro training refresher.

## 5. Consensus Derivation Policy
- Majority strict; ties labeled `__TIE__` until adjudicated.
- Adjudication: Third pass by either senior annotator OR apply deterministic precedence rule if pattern obvious (document decision in change log).

## 6. Documentation Artifacts
- `pipeline/data/agreement_<date>.json` (raw agreement output).
- `pipeline/data/disagreements_<date>.csv` (rows with mismatch and both tags).
- `annotation_refinement_protocol.md` (this file; append change log).

## 7. Automation Hooks (Planned)
Add a lightweight script to:
- Ingest two annotated CSVs and emit top confusion pairs.
- Generate markdown snippet for guideline insertion.

## 8. Change Log
- v0.1: Initial reliability + refinement cycle definition.
