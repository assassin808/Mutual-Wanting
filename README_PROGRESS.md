# Rapid Progress Addendum (Ephemeral)

This short-lived file records the latest incremental utilities added for multitask acceleration (will be merged into main README later).

## Newly Added Scripts
| Script | Purpose | Notes |
|--------|---------|-------|
| `pipeline/annotation_progress.py` | Quick pilot annotation completion + tag distribution status | Safe to run anytime; overlap support |
| `pipeline/cluster_user_styles.py` | Optional k-means style clustering on feature vectors | Skips automatically if insufficient rows |

## New Make Targets
| Target | Runs | Dependency |
|--------|------|------------|
| `cluster` | Clusters user style features | `features` (feature_rows_live.csv) |
| `progress-a` | Pilot A batch progress report | pilot_batch_A.csv |

## Next Immediate Actions (Internal)
- Run `make hygiene sample` then `make features cluster` once new raw corpus chunk ready.
- Begin Annotator A labeling; monitor with `make progress-a`.
- Threshold for early κ dry-run: ≥12 overlap items labeled by both annotators.

_(This file may be removed or merged after stabilization.)_
