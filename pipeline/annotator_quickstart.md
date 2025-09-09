# Pilot Annotation Quickstart

Purpose: Minimize friction for Annotator A/B to reach early overlap labeling for κ.

Files:
- pilot_batch_A.csv (Annotator A)
- pilot_batch_B.csv (Annotator B)
- pilot_batch_overlap_ids.txt (20 overlapping ids)

Tooling:
1. Interactive CLI (optional): `python pipeline/annotation_tool.py --csv pipeline/data/pilot_batch_A.csv --out pipeline/data/pilot_batch_A.csv`
2. Progress check: `make progress-a`
3. Early partial κ once B has started: `make early-kappa`

Tag Entry Rules:
- Enter 'y' or 'n' ONLY; leave blank if uncertain (will be skipped for that tag pair).
- Tags are independent; multiple 'y' allowed.
- Prefer precision over recall for borderline warmth vs helpfulness (pending v0.2 refinement).

Overlap Strategy:
- Prioritize the 20 overlap IDs first (filter by those IDs) so early κ threshold (≥5–8 labeled pairs per tag) is met quickly.

Quality Notes:
- If a comment seems multi-topic, treat each evaluative dimension separately.
- Use blank for sarcasm unless clearly negative about model performance (complaint = y).

Escalation (log separately): create a row in `annotation_refinement_protocol.md` with ID and ambiguity description.
