# Sampling Specification (v1)

Goal: Balanced representation of user complaints vs baseline across model transition windows without manufacturing synthetic content.

Strata Dimensions:
1. Transition (each entry in `archive_plan.json`)
2. Phase: pre, post
3. Score Bucket (lo, mid, hi)
4. Enrichment Type: enriched (keyword hit) vs baseline (random)

Score Buckets (tunable):
- lo: score < 10
- mid: 10 ≤ score < 50
- hi: score ≥ 50

Enrichment Lexicon (initial seed – expand post-pilot):
- complaint, broken, worse, degraded, slow, error, hallucinat, unsafe, rude, unhelpful, jailbroken

Target Allocation (per (transition × phase × bucket)):
- 50% enriched, 50% baseline (fallback: if enriched < target, reallocate to baseline; record shortfall).

Manifest Fields:
- id, transition, phase, score, score_bucket, enriched (bool), keyword_hits (array), source_file

Gating / QC:
- Minimum enriched precision (lower Wilson bound) ≥ 0.30 before scaling enrichment proportion beyond 50%.
- If precision < 0.30 after 150 total labels: expand lexicon (add 5–10 high-signal stems) and re-sample remaining slots.

Versioning:
- Update this file with a new section documenting any lexicon change (append not overwrite).

Change Log:
- v1 (initial scaffold).
# Sampling Specification (Score Buckets & Strategy)

Version: 2025-09-08

## 1. Objectives
Provide a reproducible method to sample Reddit comments across model transition windows that balances:
* Transition phase (pre vs post)
* Score strata (lo / mid / hi) to mitigate karma-driven topical skew
* Enrichment (keyword-focused) vs baseline random draws

## 2. Score Bucket Definition (Finalized)
Primary (default) static thresholds:
* lo: score < 10
* mid: 10 ≤ score < 50
* hi: score ≥ 50

Rationale: Empirical Reddit score distributions (heavy-tailed) typically show strong topical & temporal drift above ~50; mid band ensures representation of moderately visible discourse. Thresholds align with existing provisional logic in scripts.

Fallback Dynamic Mode (if any bucket < 5% of total after initial fetch):
1. Compute empirical quantiles q33, q66 over scores within (transition × pre_post).
2. Define lo < q33, mid q33–q66, hi ≥ q66 (enforce distinctness; if ties collapse adjacent).
3. Record dynamic thresholds in sampling manifest with `dynamic_score_thresholds=true`.

## 3. Sampling Process
1. Merge raw pre + post window JSONL (after normalization & tagging transition metadata).
2. Assign score_bucket via static thresholds; if imbalance criterion triggered, switch to dynamic mode.
3. Stratify by (transition, pre_post, score_bucket).
4. Target per cell count proportional to available population with minimum 1 per non-empty cell.
5. Overlay enrichment: For each cell, reserve up to 50% of its allocation for enrichment-hits; fill remainder from baseline random. If enrichment < allocation, backfill with baseline to maintain cell size.

## 4. Enrichment Tagging
* Load keyword lexicon (complaint_focus_lexicon.txt) lowercased.
* A row is enrichment-eligible if any keyword appears as a whole word (case-insensitive) in body.
* Store flag `enriched=1|0` in sampling manifest rows.

## 5. Manifest Fields
`id, transition, pre_post, score, score_bucket, enriched, source_file, sample_batch_id`

Plus top-level JSON sidecar (e.g., `sampling_manifest_meta.json`):
```
{
  "generated_utc": 1736371200,
  "static_thresholds": {"lo_lt": 10, "mid_lt": 50},
  "dynamic_score_thresholds": false,
  "target_n": 600,
  "actual_n": 598,
  "strata_counts": {"gpt4_to_4o|pre|lo": 42, ...},
  "enrichment_fraction": 0.47
}
```

## 6. Reproducibility
* Set RNG seed (default 42) before stratified sampling.
* Log discarded rows (if any cap) with reason.

## 7. Quality Checks
* Ensure no (transition, pre_post) pair has hi bucket share > 60% (else consider downsampling hi or merging hi+mid for modeling sensitivity test).
* Report per-bucket median length & complaint keyword density to detect lexicon-induced topic bias.

## 8. Integration Points
* `sample_for_labeling.py` updated to accept `--score-thresholds` and produce manifest JSON.
* Downstream regression includes score_bucket as covariate; modeling script reads the manifest JSON for documentation.

## 9. Future Extensions
* Optional weighting by subreddit size (inverse probability) if single subreddit dominates strata > 70%.
* Adaptive oversampling of under-represented complaint tags after initial labeled batch (active balancing).

## 10. Change Log
* v1: Initial formalization & dynamic threshold fallback.
