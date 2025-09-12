# Scale Annotation Sampling Specification (Draft)

Goal: Obtain ≥600 annotated instances (target 800 to allow filtering) spanning pre/post windows and style/theme diversity.

Stratification Axes:
1. Temporal: equal allocation across (pre, post) for primary transition (gpt4_to_4o) once windows exist.
2. Subreddit topical clusters: derive from TF-IDF + k-means (k=12) on window corpora; sample proportional to log(size) to avoid dominance.
3. Length buckets (tokens in body): short (<=40), medium (41–120), long (>120).
4. Presence of question mark / interrogative (proxy for help-seeking) vs none.
5. Sentiment polarity rough bucket (VADER or rule-based) negative / neutral / positive (optional if tool available quickly).

Allocation Formula:
Base quota per (temporal * subreddit_cluster) cell = ceil( Target / (2 * K) ). Then refine within cell to meet length and question strata with minimum 5 per sub-stratum where feasible.

Pilot Reuse:
- Incorporate existing 60 pilot annotated rows; re-weigh quotas to subtract their occupied cells.

Edge Case Handling:
- If a cell has fewer raw candidates than quota, redistribute deficit proportionally to remaining cells with >110% of base.

Output Artifacts:
- sampling_frame.csv (all candidate rows with stratum labels, exclusion flags)
- selection_final.csv (chosen for annotation wave)
- sampling_report.md (summary counts, coverage heatmap)

Quality Controls:
- Random seed recorded in `sampling_metadata.json`.
- Interleaved 10% overlap for double annotation reliability per wave (compute Cohen's kappa per major tag and macro-average, target >=0.75).

Open Questions (Need Data):
- Availability of author ids to enforce per-author max (cap 2) to reduce clustering.
- Precise time boundaries of pre/post windows (will be set after window reconstruction script runs).

Next Steps:
1. Implement window reconstruction.
2. Build candidate pool dataset.
3. Execute stratified sampling code.
