# Enrichment Precision Placeholder

Will be computed once >=150 labeled rows exist.

Steps (future automated script):
1. Load combined labeled CSV (A+B merged after alignment) with `complaint` tag.
2. Identify rows where `enrichment_flag == 1` vs baseline.
3. Compute:
   - Precision = complaint_positive_in_enriched / total_enriched
   - Relative Risk = (complaint_positive_in_enriched / total_enriched) / (complaint_positive_in_baseline / total_baseline)
   - Wilson 95% CI for precision.
4. Bootstrap (1k) difference in proportions for stability; require sign consistency >=0.8.
5. Output JSON: enrichment_eval.json with fields {precision, rr, ci_low, ci_high, bootstrap_sign_consistency, counts}.

Blocking requirement: labeled_count >= 150.
