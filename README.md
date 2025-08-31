# Mutual Wanting (GPT Version Transition Study)

Primary status & plan: `PROJECT_OVERVIEW.md`
Archived ideation / historical brainstorms: `ARCHIVE_IDEATION.md`
Progress log (chronological): `PROGRESS_LOG.md`
Manuscript source: `agents4science_2025.tex`

## Quick Start
1. Set up a local `.env` (do NOT commit):
```
OPENROUTER_API_KEY=YOUR_KEY_HERE
```
2. Run data fetch & sampling via scripts in `pipeline/`.
3. Follow remaining work checklist in `PROJECT_OVERVIEW.md` (Sections 6 & 7).

## Security Note
If any API key was ever exposed in plaintext (e.g., pasted into chats or committed), rotate it immediately in the provider dashboard. Never embed keys directly in code or markdown tracked by git.

## Contribution Flow
- Update active plans only in `PROJECT_OVERVIEW.md`.
- Keep `PROGRESS_LOG.md` for dated, append-only entries.
- Avoid re-expanding pointer files (`prompt.md`, `topic.md`, etc.).

## Remaining Work Snapshot (Abbrev)
Data & Labeling: Backfill pre window → Dual labeling → κ check → Full labeling → Enrichment eval.
Modeling: Features → Logistic models (thresholded) → Drift analyses.
Probe Suite: Spec → Runner → Metrics → Cross-signal synthesis.
Manuscript: Methods finalization → Results tables/figures → Discussion axes → Ethics & reproducibility → Polish & submission.

(Full checklist lives in the overview.)
