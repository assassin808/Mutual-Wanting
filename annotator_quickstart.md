# Annotator Quickstart (Pilot A/B)

1) Prioritize the 20 overlap IDs first. File: `pipeline/data/pilot_batch_overlap_ids.txt`.
2) Annotate consistently: only one primary_tag per item; binary columns for major tags (warmth/creativity/helpfulness/hedging/complaint) are yes/no.
3) If unsure, mark as unclear in notes and move on; do not guess.
4) Keep comments short; avoid copying user text into notes to minimize sensitive data exposure.
5) After finishing ≥12 overlap items, ping the pipeline to run early κ.

Run (maintainer): `make pilot-reports` to refresh agreement, disagreements, early κ, per-tag κ, and figure/table slices.
