# ABCDE Rebuild Plan

This file captures the operational execution of steps ABCDE requested by mentor.

A. Assess & Acquire Authentic Historical Windows
- Current `archive_plan.json` defines 3 transitions (gpt4_to_4o, gpt4o_iterative_mar2025, gpt4_retirement_chatgpt).
- Existing `archive_map.json` only maps `gpt4_to_4o` but referenced files `gpt4_to_4o_pre.jsonl` and `gpt4_to_4o_post.jsonl` are NOT present in `pipeline/data/`.
- Live scrape shards present under `pipeline/data/live_scrape/` (per-subreddit aggregate dumps) but not partitioned into the pre/post windows.
- ACTION NEEDED: reconstruct pre/post windows from live scrape aggregates or ingest archived dumps.

B. Build Normalization & Coverage Derivation (without reusing existing scripts verbatim)
- Will create wrappers that:
  1. Concatenate subreddit aggregates restricted to window timestamps.
  2. Apply minimal schema filter (id, subreddit, created_utc, score, body, parent_id, link_id) with validation.
  3. Salt and hash author strings (placeholder: requires original author field—currently absent → BLOCKED until raw author present or design decision to skip author-level analyses).
  4. Emit coverage JSON (days covered, missing spans, total posts).

C. Consensus Annotation Scaling Preparation
- Pilot only; need scale sampling design spec (target ≥600). Will generate `SCALE_SAMPLING_SPEC.md` stub.

D. Analytical Pipeline Rebuild Targets
- Drift, regression, probes, lexical coupling all blocked pending A and C completion.

E. Expanded Citation & Narrative Integration
- Prepare `CITATION_AUGMENT_LIST.md` enumerating target papers and insertion points.

## Blockers
- Missing historical pre/post raw window files.
- Lack of author identifiers prevents full replication of hashing step (may proceed omitting until data obtained; mark limitation).

## Next Actions
1. (Done) Window reconstruction script `scripts/reconstruct_window.py` created.
2. (Done) Coverage wrapper `scripts/compute_coverage_wrapper.py` created.
3. (Done) Sampling spec stub `SCALE_SAMPLING_SPEC.md` added.
4. (Done) Citation augment list `CITATION_AUGMENT_LIST.md` added.
5. NEXT: Determine timestamp boundaries for first transition and run reconstruction.

## Provenance
Created: $(date placeholder)

## Progress Updates
2025-09-12:
- Reconstructed gpt4_to_4o pre/post windows (pre=63, post=197 rows).
- Normalized with salted author hashing placeholder.
- Coverage computed (no missing days; sparse counts due to low volumetric capture vs ideal Reddit firehose).
- Updated `table1_sampling_coverage.tsv` with real counts.
- Built initial sampling frame (260 combined rows after normalization; token lengths predominantly zero -> indicates `body` field empty for many posts; need to verify ingestion retained body/selftext vs missing field mapping). 
- Next: Diagnose empty body issue (char/token medians = 0) before sampling/annotation scaling; confirm if source fields use `selftext` vs `body` in ingestion path and patch normalization to preserve content.
 - Extended: Added two additional transitions (gpt4o_iterative_mar2025, gpt4_retirement_chatgpt) reconstructed, normalized, coverage audited; coverage table now aggregated for all three.
 - Implemented clustering across transitions; sampling frames: 260 / 506 / 709 rows (total 1,475 candidates).
 - Multi-transition stratified sampler produced selection_final.csv (n=795) near target 800.
 - Prepared dual annotation batch with 15% overlap (119 shared items) -> label_batch1_A/B.csv.
 - Added scripts: assign_topic_clusters.py, multi_transition_sampling.py, prepare_annotation_batches.py; patched compute_coverage_wrapper for append semantics; patched archive_normalize.py to ingest selftext.
 - Enriched Wave 1 annotation batches with body text (scripts/enrich_label_batch_bodies.py); all 795 bodies populated; limitation note about earlier empties resolved.
 - Added citation augmentation file (references_additions.bib) and integrated first wave of transparency, evaluation, persona, and reliability citations into manuscript.
2025-09-13:
 - Added reliability scaffold (Cohen's kappa + Krippendorff's alpha) over A/B overlap; emits confusion, labels, counts. Current n_pairs=0 pending annotation.
 - Recomputed features for Wave 1 selection using enriched bodies (n=795; missing_body=0); emitted per-row CSV and summary.
 - Seeded lexical drift (log-odds) on gpt4_retirement_chatgpt windows with frequency floor for stability; JSON artifact written.
 - Added Makefile targets: reliability-wave1, selection-features, drift-retirement, figdata-wave1, fig2-wave1 to streamline execution.
