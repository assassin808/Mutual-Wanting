# Key Findings & First-Author Summary (WIP Outline Stage)

## 1. Core Research Question
How do user "wants" (expressed/latent desiderata in public discourse) and system "wants" (implicit optimization / deployment preferences reflected in behavioral responses) diverge or realign across a salient GPT model version transition, and can a minimal two-lever method (Reddit discourse + controlled API probe suite) surface stable tension axes (warmth vs cost efficiency, stability vs iterative optimization, epistemic honesty vs authority signaling, emotional resonance vs dependence risk)?

### Why It Is Interesting
- Bridges unilateral “alignment” framing with a *bidirectional* desiderata negotiation (mutual wanting) rarely formalized.
- Provides an inexpensive, reproducible alternative to heavy lab studies for early detection of persona/drift tensions.
- Offers design-relevant composite metrics (CDR, SUR, WCTI, DRP, TCG) grounded in existing HCI and trust calibration literature yet integrated under a single relational alignment lens.

## 2. Novelty & Contributions
| Dimension | Novelty | Status |
|-----------|---------|--------|
| Conceptual Framing | Mutual Wanting Alignment Framework (symmetrized user + system desiderata axes) | Defined in manuscript |
| Minimal Method | Only two levers (organic Reddit + structured API prompt probes) for multi-axis drift/tension mapping | Pipeline implemented (API probing pending reliability gate) |
| Metrics Integration | Unified set linking uncertainty style, relational pacing, empathy tiering, and dependence risk | Operational definitions specified |
| Robustness Guardrails | Reliability gating (κ>0.65), frequency floors, enrichment bias quantification, separation-aware regression | Implemented in scripts / manuscript robustness section |
| Drift Lexicon Procedure | Log-odds with symmetric per-side frequency floor + restricted complaint lexicon | Script completed; awaiting authentic pre window |
| Sampling Design | Dual-path (keyword-enriched + random baseline) enabling precision/recall/enrichment risk estimation | Implemented; evaluation script ready |

## 3. Experiments / Analyses (Planned or In-Progress)
| Layer | Experiment / Analysis | Purpose | Current State | Gate to Proceed |
|-------|-----------------------|---------|---------------|-----------------|
| Reddit Collection | Filtered fetch + keyword enrichment + baseline sampling | Build analyzable complaint corpus with controllable bias | Functional; artificial pre/post due to placeholder date | Historical backfill for authentic pre |
| Dual Annotation | Split A/B with overlap; compute κ | Ensure label reliability before modeling | Split created (A=72,B=72, overlap=25) | κ > 0.65 overall |
| Enrichment Evaluation | Precision, relative risk, recall estimate (Wilson CIs) | Quantify sampling distortion risk | Tool ready (not yet run on real labels) | Need ≥100 labeled (mixed) |
| Feature Extraction | Hedging, warmth markers, pronouns, imperatives | Supply predictors for complaint presence & drift exploration | Implemented | Stable labeled dataset |
| Logistic Modeling | Complaint vs none (and per-tag where support) | Identify stylistic correlates; effect directions | Skeleton + fallback implemented | MIN_CLASS ≥8 & κ gate |
| Lexical Drift | Log-odds diff (freq floor ≥10) restricted/unrestricted | Detect stable persona vocabulary shifts | Script + floor ready | Authentic pre/post tokens; support per side |
| API Probe Suite | Structured prompts across versions (uncertainty, pacing, intimacy boundary) | Compare behavioral metrics (CDR, SUR, ETD, SST, TCG) between model versions | Not yet executed | Authentic drift signals + metrics calibration from Reddit phase |

## 4. Current Findings (Provisional / Non-Interpretive)
- Keyword enrichment yields sparse but high-precision complaint subset (needs recall quantification vs baseline once labeled). 
- Early differential tokens in synthetic pre/post dominated by release speculation (agi, advanced, voice) → topical contamination risk; justifies restricted complaint lexicon.
- High-score complaint posts underrepresented; indicates need for targeted retrieval or adjusted sampling weights.
- Latency & memory complaints co-occur with generic dissatisfaction terms → multi-factor bundles, not isolated persona warmth decreases.

## 5. Risks & Mitigations
| Risk | Impact | Mitigation Implemented | Remaining Action |
|------|--------|------------------------|------------------|
| Artificial pre/post labeling (placeholder date) | Invalid drift inference | Historical backfill scaffold prepared | Acquire authentic archives |
| Low frequency lexical noise | Spurious drift claims | Frequency floor (≥10/side) + restricted lexicon | Wait for authentic counts |
| Annotation inconsistency | Unreliable modeling | Dual overlap + κ gating | Perform dual labeling |
| Sampling bias from enrichment | Distorted incidence estimates | Enrichment evaluation script | Run after initial labeling |
| Logistic separation on sparse classes | Inflated coefficients | L2 fallback + MIN_CLASS threshold | Execute after labels |
| Overinterpreting synthetic validation | False narratives | Explicit manuscript segregation | Maintain discipline in drafts |

## 6. Folder / File Organization Assessment
| Path | Keep? | Rationale |
|------|-------|-----------|
| `pipeline/` | Yes | Core scripts & data flow |
| `Agents4Science_Template/` | Yes | Manuscript source (cleaned) |
| `literature_summaries/` | Yes | Traceability for citations |
| `PROGRESS_LOG.md` | Yes | Chronological decisions (retain) |
| `PROJECT_STATUS.md` | Consider merging | Overlap with this KEY_FINDINGS; could consolidate |
| `keynote.md` | Optional | Presentation planning (keep if active) |
| `prompt.md` / `topic.md` / `research_topics.md` / `requirement.md` | Prune / merge | Fragmented early ideation; consolidate salient points into one archival ideation file |
| `.venv/` | Ignore (not tracked) | Local environment |

### Proposed Cleanup Actions
1. Merge `PROJECT_STATUS.md` salient deltas into `KEY_FINDINGS.md`; then archive or delete.
2. Consolidate `prompt.md`, `topic.md`, `research_topics.md`, `requirement.md` into a single `ARCHIVE_IDEATION.md` (retain timestamps, drop redundancy).
3. Keep `keynote.md` if active; otherwise archive alongside ideation.

## 7. Immediate Next Steps (Priority Ordered)
1. Human Labeling Round 1: Annotator A proceeds on `label_batch2_A.csv`; B on `label_batch2_B.csv`; focus on overlap first.
2. Reliability Computation: Run `agreement.py` on overlap; refine ambiguous label definitions if κ<0.65.
3. Consensus Merge: `merge_annotations.py` → produce consensus dataset for enrichment evaluation.
4. Enrichment Evaluation: Run `enrichment_eval.py` to report precision, prevalence, relative risk, recall estimate.
5. Historical Backfill: Ingest authentic GPT-4→4o window; re-tag phase; regenerate mixed sample for second labeling wave.
6. Drift Candidate Generation: Run `drift_lexicon.py` (restricted + unrestricted) post-authentic backfill.
7. API Probe Design Finalization: Freeze prompt suite using lexicon + complaint archetypes; begin controlled runs.

## 8. Mentor Questions / Concerns for Guidance
- Source for robust historical Reddit archives (Pushshift alternatives) you recommend for reproducible GPT-4 era slices?
- Threshold calibration: Is MIN_CLASS=8 sufficient, or should we raise to 10 before per-tag modeling for early draft rigor?
- Any additional ethical disclosure elements you want emphasized (e.g., handling potential mental health queries)?
- Preference on consolidation timing: proceed with folder cleanup now or wait until after first reliability pass?
- For API probing: should we prioritize uncertainty style differentials or warmth-cost trade-off scenarios first for narrative impact?

## 9. Open Design Decisions
| Decision | Options | Tentative Lean |
|----------|---------|----------------|
| Additional Platforms | Add (HN / X) vs stay Reddit-only | Stay Reddit-only (maintain minimal method purity) |
| Warmth Lexicon Expansion Scope | Moderate (synonyms only) vs broad (embedding neighbors) | Moderate first, then embedding-based recall check |
| Drift Visualization | Top z-scored tokens vs axis-mapped clusters | Start with top tokens + interpretive grouping |

---
_First-author note: All findings currently non-inferential; manuscript explicitly labels outline status until authentic temporal contrast + reliability gate achieved._
