# Project Status (Rolling)

Date: 2025-09-08

## High-Level
Pilot infrastructure complete; beginning annotation (Annotator A/B not started). Historical dump acquisition remains the principal blocker for authentic pre/post transitions.

## Recently Completed
- Pilot split (60 items; 20 overlap) generated.
- Agreement & disagreement scripts adapted to pilot schema.
- Gating criteria + risk register registered in `pipeline/metrics_spec.md`.
- Labeling guidelines v0.1.1 issued (pilot size correction + gating reference).

## Active Focus (Next 48h)
1. Execute Annotator A pass (`pilot_batch_A.csv`).
2. Execute Annotator B pass (`pilot_batch_B.csv`).
3. Run agreement + disagreement; refine guidelines → v0.2.

## Risks / Mitigations
| Risk | Status | Mitigation |
|------|--------|------------|
| Historical dumps delay | Blocking core analyses | Parallelize pilot & feature engineering stubs |
| Reliability below κ 0.70 | Pending pilot | Confusion review & boundary examples |
| Lexicon enrichment precision low | Pending labels | Expand baseline sampling & refine keyword set |

## Metrics Gates Snapshot
| Gate | Current | Threshold | Pass? |
|------|---------|-----------|-------|
| Pilot κ overall | N/A | ≥0.70 | Pending |
| Token freq floor readiness | N/A | ≥10 each side | Pending (needs data) |
| Bootstrap stability spec | Specified | ≥0.8 sign consistency | N/A |

## Checklist Reference
Authoritative detailed tasks in `paper_checklists/EXPERIMENT_TO_PAPER_CHECKLIST.md`.

## Next Update Trigger
Post-pilot agreement run or in 48h, whichever first.
