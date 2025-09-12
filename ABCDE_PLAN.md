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
1. Generate window reconstruction stub script (`scripts/reconstruct_window.py`).
2. Create coverage wrapper script (`scripts/compute_coverage_wrapper.py`).
3. Add sampling spec stub.
4. Add citation augment list.

## Provenance
Created: $(date placeholder)
