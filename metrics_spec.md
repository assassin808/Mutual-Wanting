# Metrics Specification and Gating Criteria (Agents4Science 2025)

Version: 2025-09-09
Owner: First Author

## Gating Criteria
- Annotation reliability: Cohen's kappa (overall) ≥ 0.70 before modeling.
- Per-outcome class size: ≥ 8 per binary contrast; otherwise skip.
- Drift tokens: frequency floor ≥ 10 per side; bootstrap sign consistency ≥ 0.8.
- Enrichment eval: precision reported with Wilson CI; if precision < 0.40, adjust lexicon and resample.

## Risk Register
- Sampling bias from enriched keywords → Mitigate with dual-track baseline; report RR and recall estimate.
- Quasi-separation in logistic models → L2-penalized fallback; skip if class support insufficient.
- Placeholder temporal windows → Block comparative claims until authentic pre/post loaded.

## Metrics Definitions (brief)
- CDR: fraction of responses with explicit uncertainty.
- SUR: fraction of uncertainty-bearing responses that follow (band + missing variable + invitation).
- ETD: distribution across empathy ladder tiers.
- SST: turns to escalation after minimal response.
- CPR: concision prompt rate (re-prompt for concision/elaboration).
- TCG: |acceptance proxy − confidence midpoint|.
- WCTI: warmth markers per token − normalized verbosity budget.
- DRP: escalation without boundary signaling.
