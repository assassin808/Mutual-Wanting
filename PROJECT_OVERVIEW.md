# Project Overview: Mutual Wanting Across GPT Model Transitions

_Last updated: 2025-08-26_

## 1. Core Research Question (Finalized 2025-09-08)
To what extent, and along which stable tension axes (Warmth–Cost Efficiency, Stability–Iteration, Epistemic Honesty–Authority, Emotional Resonance–Dependence), do user‑perceived persona complaints shift across GPT model version transitions, and can a minimal dual‑source method (Reddit discourse + controlled probe suite) yield reproducible early‑warning signals of divergence between user wanting and system operational wanting?

## 2. Mutual Wanting Alignment Framework (Axes)
- Warmth vs Cost Efficiency: personable, empathic elaboration vs brevity/token frugality.
- Stability vs Iterative Optimization: persona continuity vs rapid tuning/router shifts.
- Epistemic Honesty vs Authority Signaling: calibrated uncertainty vs confident assurance.
- Emotional Resonance vs Dependence Risk: adaptive mirroring vs over‑bonding vulnerability.

### Non-Goals (Explicit)
- No causal inference about downstream user behavioral or wellbeing outcomes.
- No longitudinal per-user trajectory reconstruction (privacy-preserving aggregate only).
- No attribution to specific internal training interventions or safety policy edits (black-box stance).
- No normative claims about optimal persona; strictly observational early-warning signals.

## 3. Metrics (Operational Set)
| Code | Name (Short) | Concept | High Value Indicates |
|------|--------------|---------|----------------------|
| CDR | Calibrated Disclosure Ratio | Uncertainty style balance | Appropriate uncertainty vs over/under hedging |
| SUR | Structured Update Ratio | Compact structured follow‑ups | System preference for efficient clarification |
| ETD | Empathy Tier Differential | Depth variance in empathic turns | Potential inconsistency / over-indexing |
| SST | Silence / Space Tolerance | Allowance for user pacing | Respect for conversational space |
| CRR | Creative Range Retention | Variety vs template shrink | Preservation of exploratory tone |
| TCG | Token Conservation Gain | Efficiency tuning magnitude | Cost‑saving pressure |
| WCTI | Warmth vs Cost Tradeoff Index | Warmth per token | Efficiency–relational balance |
| DRP | Dependence Risk Proxy | High-resonance patterns w/o safeguards | Elevated reliance risk |

## 4. Current Artifact Inventory
- Data / Pipeline: `pipeline/` scripts (fetch, enrichment sampling, dual annotation split, feature extraction, regression skeleton, drift lexicon, enrichment eval, synthetic label generator, historical backfill scaffold).
- Manuscript: `agents4science_2025.tex` (cleaned sections, metrics table, checklists partial).
- Logs & Status: `PROGRESS_LOG.md` (chronological), this `PROJECT_OVERVIEW.md` (canonical forward plan).
- Archives / Ideation: `ARCHIVE_IDEATION.md` (consolidated), legacy: `prompt.md`, `topic.md`, `research_topics.md`, `PROJECT_STATUS.md`, `KEY_FINDINGS.md` (now pointers).

## 5. Experiment / Analysis Plan & Gates
| Layer | Purpose | Status | Gate to Advance |
|-------|---------|--------|-----------------|
| Historical Backfill | Authentic pre window acquisition | Scaffold only | Acquire archived pre period data |
| Current Fetch + Enrichment | Complaint corpus with bias control | Functional (post-heavy) | Pre data integrated |
| Dual Annotation Round 1 | Reliability estimation | Split prepared | κ > 0.65 (overlap n=25) |
| Enrichment Evaluation | Bias quantification (precision/recall/RR) | Script ready | ≥100 labeled examples |
| Feature Extraction | Predictor matrix for modeling | Implemented | Stable labeled set (post-merge) |
| Logistic Modeling | Effect directions (complaint + tags) | Skeleton + fallback | MIN_CLASS ≥ 8 & reliability gate |
| Lexical Drift (Restricted + Open) | Persona / topical shift signals | Script; needs authentic pre | Frequency floor ≥10 both sides |
| Probe Suite Execution | Cross-version behavioral metrics | Spec pending | Drift + metrics calibration complete |
| Integrative Analysis | Map Reddit ↔ Probe signals | Pending | All above datasets finalized |

## 6. Remaining Work Checklist (Execution)
### Data & Labeling
- [ ] Implement historical backfill script run (authentic pre interval selection + config)  
- [ ] Fetch + store pre window JSONL (target ≥1k raw)  
- [ ] Regenerate enriched + baseline samples with real pre/post flags  
- [ ] Prepare `label_batch2_A.csv` & `label_batch2_B.csv` (real, not synthetic)  
- [ ] Complete overlap labeling first (n=25)  
- [ ] Compute Cohen's κ (target >0.65; stretch >0.70)  
- [ ] Refine label guidelines if κ below threshold & re-label disputed items  
- [ ] Finish full batch labeling (target n_total ≈ 600–800 initial)  
- [ ] Run enrichment evaluation (precision, recall estimate, relative risk + Wilson CIs)  
- [ ] Adjust enrichment keywords / sampling if recall <0.60 or RR > desired risk band  

### Modeling & Analysis
- [ ] Merge adjudicated labels (consensus file)  
- [ ] Feature extraction on consensus set  
- [ ] Validate class counts (≥ MIN_CLASS per modeled label)  
- [ ] Run logistic models (complaint presence + key attributes) with separation fallback  
- [ ] Inspect coefficient stability (CIs or bootstraps if feasible)  
- [ ] Generate effect direction table for manuscript  
- [ ] Execute lexical drift (restricted complaint lexicon) with frequency floor  
- [ ] Execute full drift (open vocabulary) and filter by statistical + frequency criteria  
- [ ] Subsample robustness check (e.g., 80% resamples) for drift tokens  
- [ ] Synthesize tension axis mapping (which metrics align with which axes)  

### API Probe Suite
- [ ] Finalize probe spec (uncertainty, pacing, intimacy boundary, warm vs concise)  
- [ ] Implement probe runner (multi-version calls with deterministic seed / temp)  
- [ ] Add rate limiting & retry wrapper; log raw JSONL  
- [ ] Compute behavioral metrics (CDR, SUR, etc.) per version  
- [ ] Statistical comparison (paired / bootstrap) across versions  
- [ ] Cross-correlate Reddit-derived signals with probe deltas  

### Validation & Robustness
- [ ] Reliability re-check after any guideline revision  
- [ ] Enrichment bias context paragraph (precision/recall narrative)  
- [ ] Sensitivity: remove high-activity subreddits, re-run key stats  
- [ ] Temporal stability: split post window halves and compare drift consistency  
- [ ] Cost / token efficiency analysis to support Warmth–Cost claims  

## 7. Manuscript Writing Checklist
### Methods & Data
- [ ] Finalize Data Collection (authentic dates, subreddit list rationale)  
- [ ] Labeling Protocol & Reliability (κ result + adjudication)  
- [ ] Sampling & Enrichment Bias subsection (with metrics)  
- [ ] Feature & Metric Operationalization (appendix pseudocode)  
- [ ] Probe Suite Description (prompts, parameters)  

### Results
- [ ] Descriptive Corpus Stats (counts, enrichment precision/recall)  
- [ ] Reliability Table  
- [ ] Logistic Model Effects Table  
- [ ] Drift Token Table (restricted + selected open)  
- [ ] Behavior Metrics Comparison (probe suite)  
- [ ] Integrated Axes Synthesis Figure  

### Discussion & Framing
- [ ] Interpretation per Axis (caution against overreach)  
- [ ] Design Implications (lightweight observability tools)  
- [ ] Limitations (sampling, platform scope, temporal coverage)  
- [ ] Future Work (multi-platform, proactive adaptation loops)  

### Ethics & Reproducibility
- [ ] Privacy / User Data Handling  
- [ ] Synthetic vs Authentic Segregation Note  
- [ ] Risk of Over-Personification / Dependence Safeguards  
- [ ] Reproducibility Artifacts List (scripts, prompt suite, config)  

### Production / Submission
- [ ] Clean unused citations  
- [ ] Final reference metadata (pending entries resolved)  
- [ ] Figures (pipeline diagram, axes, metrics plots, drift tokens)  
- [ ] Tables compiled & LaTeX validated  
- [ ] Readability + coherence editing pass  
- [ ] Conference formatting & page limits check  

## 8. Risk Register (Live)
| Risk | Likelihood | Impact | Status | Mitigation |
|------|------------|--------|--------|------------|
| Inadequate pre window volume | Medium | High | Open | Early backfill + broaden sub list if needed |
| Low κ on first pass | Medium | High | Open | Guideline refinement + targeted examples |
| Enrichment recall too low (<0.5) | Medium | Medium | Open | Expand keyword lexicon iteratively |
| Drift dominated by topical news tokens | High | Medium | Open | Restricted lexicon + frequency floor |
| Model routing confounds in probe suite | Medium | Medium | Open | Force explicit version spec; multi-run averaging |
| Over-interpretation of small effect sizes | Medium | Medium | Open | CI / bootstrap emphasis; effect size thresholds |

## 9. Timeline (Indicative)
Week 1: Backfill + Label Round 1 + κ.  
Week 2: Complete labeling + enrichment eval + modeling.  
Week 3: Drift + probe suite runs + initial results drafting.  
Week 4: Robustness checks + full manuscript results & discussion.  
Week 5: Polishing, figures, submission prep.  

## 10. Usage & Scripts Quick Reference
| Script | Purpose |
|--------|---------|
| `fetch_reddit.py` | Acquire raw Reddit comments (enriched + baseline) |
| `split_for_dual_annotation.py` | Create A/B annotation splits with overlap |
| `annotation_tool.py` | CLI labeling helper |
| `generate_synthetic_labels.py` | Synthetic labels for pipeline smoke test |
| `features_and_analysis.py` | Feature extraction & summary stats |
| `regression_skeleton.py` | Logistic modeling with separation fallback |
| `drift_lexicon.py` | Lexical drift (restricted/open) with frequency floors |
| `enrichment_eval.py` | Precision / recall / RR for enrichment bias |
| `historical_backfill_stub.py` | Placeholder for authentic pre-window acquisition |

## 11. Security / API Key Handling
Do NOT commit raw API keys. Store secrets in a local `.env` with entries like:  
```
OPENROUTER_API_KEY=YOUR_KEY_HERE
```
Add `.env` to `.gitignore` (if not already). Rotate the key if it has been exposed in any public context.

## 12. Legacy File Pointers
- `KEY_FINDINGS.md` -> superseded by sections 1–9 here.
- `PROJECT_STATUS.md` -> merged (framework, metrics, bibliography tracking now implicit).
- Ideation (`prompt.md`, `topic.md`, `research_topics.md`) -> consolidated into `ARCHIVE_IDEATION.md`.

---
Canonical status + plan lives here going forward.
