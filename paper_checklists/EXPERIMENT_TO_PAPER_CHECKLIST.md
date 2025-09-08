# End-to-End Experiment → Paper Production Checklist (Agents4Science 2025)

Version: 2025-09-08
Owner: First Author (autonomous); update status inline as you progress.

---
## Legend
- [ ] Not started  
- [~] In progress  
- [x] Complete  
- [!] Blocked / Needs external resource  
- [D] Decision log item (record rationale)  

---
## 0. Framing & Scope Lock
- [x] Finalize core research question wording (persona drift framed as mutual wanting tension)  
- [ ] Freeze taxonomy tag names (post-pilot; version tags in guidelines)  
 - [x] Register gating criteria (kappa ≥ 0.70 major tags; freq floor 10 tokens side) in `metrics_spec.md`  
- [x] Document non-goals (no clinical claims, no causal user outcome inference)  
- [x] Add risk register section to `metrics_spec.md` (temporary host)  

## 1. Data Acquisition Layer
### 1.1 Historical Dumps
- [!] Source GPT-4→4o window dumps (list candidate mirrors with SHA256)  
- [!] Source 4o→5 (or 4.5→5) preliminary window (may need rolling capture)  
- [x] Generate archive plan windows (`plan_archives.py` -> `archive_plan.json`)  
- [ ] Validate integrity (line counts, compression checks)  
	- (tooling ready: `pipeline/archive_integrity.py`)  
- [ ] Normalize to unified JSONL schema (fields: id, subreddit, author_hash, created_utc, score, body, parent_id, link_id)  
	- (tooling ready: `pipeline/archive_normalize.py`)  
- [ ] Build `archive_map.json` with exact unix boundaries & transition labels  
- [ ] Run `archive_coverage.py` → produce `archive_coverage_report.json`  
- [ ] Compute sparsity & per-day counts; flag missing days >1 gap  
- [D] Decision: fallback if partial days? (interpolate vs truncate)  

### 1.2 Recent Live Supplement
- [x] `limited_historical_scrape.py` executed (manifest present)  
- [ ] Decide retention vs discard for final analyses (pilot only?)  
- [ ] Tag any reused rows to avoid mixing with authentic windows  

## 2. Sampling Strategy
- [x] Define score buckets (lo <10, mid 10–49, hi ≥50) across windows (see `pipeline/sampling_spec.md`)  
- [x] Implement balanced sampler (`pipeline/sampler.py`)  
- [x] Dual-track sampling: enriched (keyword) + baseline random (implemented)  
- [x] Store sampling manifest with inclusion rationale (keyword hits)  
- [ ] Run enrichment precision/relative risk once first 150 labels exist  
- [D] Decide target N per transition (e.g. 300 pre + 300 post)  

## 3. Annotation Phase
### 3.1 Pilot
- [x] Pilot batch generated (60 items balanced)  
- [x] A/B split with 20 overlap items  
- [ ] Annotator A completion  
- [ ] Annotator B completion  
- [x] Agreement tool (`pipeline/agreement.py`)  
- [ ] Compute κ overall + per-major tag (warmth, creativity, helpfulness, hedging)  
- [x] `disagreement_report.py` tool present  
- [ ] Guideline refinement → v0.2 (change log appended)  

### 3.2 Scale Annotation
- [ ] Generate first full batch (e.g. 400 items)  
- [ ] Split with overlap (≥15%)  
- [ ] Dual annotation  
- [ ] Cohen’s κ recalculation  
- [ ] If κ < 0.70: run focused confusion workshops (document decisions)  
- [ ] Consensus merge (majority / escalate unresolved)  
- [ ] Periodic drift check (re-annotate 20 previously labeled items per 200 new)  

### 3.3 Data Hygiene
- [ ] De-duplication (hash body text)  
	- (tooling ready: `pipeline/dedupe_text.py`)  
- [ ] Remove near-identical reposts (minhash)  
	- (tooling ready: `pipeline/text_minhash.py`)  
- [ ] Author hash generation (SHA256 salt)  
	- (tooling ready: `pipeline/archive_normalize.py`)  
- [ ] Sensitive content filter log  
	- (tooling ready: `pipeline/sensitive_filter.py`)  

## 4. Feature Engineering
- [x] Warmth markers expansion (config in `feature_lexicon_config.json`)  
- [x] Hedge lexicon validation (initial list extended in config)  
- [ ] Compute per-comment features: length, warmth_rate, hedge_rate, pronoun ratios, imperative ratio  
- [ ] User style clustering (k=5) – optional; record silhouette score; decide inclusion  
- [ ] Store `feature_rows.csv` + `feature_summary.json`  
- [ ] Validate no leakage features referencing post labels incorrectly  

## 5. Drift Analysis
- [ ] Authentic pre/post corpus assembly (per transition)  
- [ ] Tokenization + frequency floor application (≥10 each side)  
- [ ] Log-odds with informative prior (save counts)  
- [ ] Bootstrap stability (sign consistency ≥0.8)  
- [ ] Produce `drift_log_odds.json` + `drift_bootstrap.json` per transition  
- [ ] Restrict to complaint-linked lexemes (map via tag-conditioned OR > threshold)  
- [ ] Multi-transition trend convergence test (direction consistency)  
- [ ] Placebo (shuffled pre_post) drift to estimate false positive rate  

## 6. Regression Modeling
- [ ] Construct modeling dataset (merged features + consensus labels)  
- [ ] Filter outcomes with class count ≥ MIN_CLASS (8)  
- [ ] Fit logistic models: tag ~ pre_post * transition + subreddit + score_bucket (+ cluster if used)  
- [ ] Extract interaction ORs + 95% CI  
- [ ] Penalized fallback for separation (L2)  
- [ ] Placebo interaction test (shuffle pre_post) distribution  
- [ ] Save `regression_results.json` + `regression_placebo.json`  
- [ ] Model diagnostics: variance inflation, Hosmer–Lemeshow (optional)  

## 7. Probe Experiments (Behavioral)
- [ ] Finalize probe prompt suite (uncertainty, warmth, intimacy boundary, silence pacing, creativity)  
- [ ] Specify target model versions (e.g., gpt-4o-YYYYMM, gpt-5-YYYYMM)  
- [ ] Rate limit / cost budgeting doc  
- [ ] Run `probe_runner.py` with seed reproducibility  
- [ ] Derive metrics: CDR, SUR, ETD, SST, CRR, DRP  
- [ ] Statistical comparisons (proportion tests / non-param) via `probe_stats.py`  
- [ ] Store `probes_results.json` + summary TSV  

## 8. Lexical–Theme Coupling
- [ ] Compute per-token conditional probability shift given complaint tag  
- [ ] Correlate token log-odds with regression interaction ORs  
- [ ] Identify top convergent tokens (report with anonymized paraphrases)  
- [ ] Stability check across transitions  

## 9. Robustness & Bias Sections
- [ ] Enrichment eval: precision, relative risk, recall estimate (Wilson CI)  
- [ ] Coverage stats table (days covered, missing spans)  
- [ ] Sensitivity: exclude high-score outliers; re-run models  
- [ ] Sensitivity: exclude single-subreddit dominance  
- [ ] Report placebo effect quantiles  
- [ ] Document all skip conditions (outcome insufficient class size)  

## 10. Ethics & Governance
- [ ] Privacy review (ensure no user handles)  
- [ ] Parasocial risk assessment (ETD distribution vs thresholds)  
- [ ] Boundary adherence audit (DRP acceptable range)  
- [ ] Data retention policy recorded  
- [ ] Add reproducibility license statement  

## 11. Figures & Tables Production
### 11.1 Data Extraction Scripts
- [ ] `table_prep.py` extended for: agreement, enrichment, regression, drift, probes, robustness  
- [ ] Add `fig_prep.py` for figure-ready CSV slices  

### 11.2 Planned Figures
- [ ] Fig1 Pipeline schematic (Mermaid or Graphviz)  
- [ ] Fig2 Annotation reliability (confusion heatmap)  
- [ ] Fig3 Complaint incidence shifts (forest plot of ORs)  
- [ ] Fig4 Lexical drift (top stable tokens; bar / lollipop)  
- [ ] Fig5 Probe metric contrasts (radar or grouped bars)  
- [ ] Fig6 Lexical–theme coupling scatter  
- [ ] Appendix: Drift token stability distribution (hist)  

### 11.3 Tables
- [ ] Table1 Sampling & coverage  
- [ ] Table2 Enrichment evaluation  
- [ ] Table3 Regression interactions  
- [ ] Table4 Probe metrics summary  
- [ ] Table5 Robustness & placebo  
- [ ] Appendix tables: full drift lexicon (filtered), feature definitions  

## 12. Writing Phases
### 12.1 Methods Finalization
- [ ] Replace outline placeholders with real counts & effect sizes  
- [ ] Insert reliability + enrichment results  
- [ ] Insert regression + probe metrics  
- [ ] Cross-reference gating criteria in text  

### 12.2 Results Narrative
- [ ] Draft thematic grouping of shifts along four tension axes  
- [ ] Integrate lexical–theme + probe alignment examples  
- [ ] Include negative results (axes with no significant change)  

### 12.3 Discussion
- [ ] Interpret mutual wanting tensions; design implications  
- [ ] Limitations (sampling, Reddit bias, absence of user longitudinal identity)  
- [ ] Future work (controlled user study, multimodal signals, cross-lingual)  

### 12.4 Abstract & Title Revision
- [ ] Update abstract to include empirical highlights & key metrics  
- [ ] Confirm terminology consistency (warmth vs empathy; uncertainty vs confidence)  

### 12.5 Ancillary Sections
- [ ] Ethics & broader impact finalize  
- [ ] Artifact availability statement (post-review release plan)  
- [ ] AI involvement checklist finalization  

## 13. Quality Gates
- [ ] Lint / type check scripts (ruff / mypy optional)  
- [ ] Repro run script (`make reproduce` or doc)  
- [ ] Random seed reproducibility test (two-run drift token intersection ≥90%)  
- [ ] All JSON artifacts schema-validated  
- [ ] Manual spot audit of 10 random labeled rows vs raw text  
- [ ] Bibliography dedup & validation (no placeholder citations)  

## 14. Submission Prep
- [ ] Ensure LaTeX compiles without warnings (refs, figs)  
- [ ] PDF font embedding check  
- [ ] Page limit compliance  
- [ ] Anonymization audit (no accidental author IDs)  
- [ ] Final diff review vs outline to ensure no provisional claims remain  

## 15. Post-Submission (Planned)
- [ ] Prepare artifact repository (redacted datasets + code)  
- [ ] Draft replication README  
- [ ] Create issue templates (bug, replication question)  

---
## Dependency Graph (High-Level)
```
Historical Dumps → Sampling → Annotation → Consensus → Features → Drift / Regression (placebo) → Probes → Coupling → Tables/Figures → Writing → QA → Submission
```

## Critical Path (Earliest Start Time)
1. Acquire historical dumps (blocking).  
2. Pilot annotation (unblocked).  
3. Reliability & guideline refinement.  
4. Scale annotation & consensus.  
5. Drift + regression + probes in parallel (post-consensus).  
6. Writing once ≥60% analytic artifacts stable.  

## Fast-Fail Checks
- If κ < 0.55 after first pilot: halt scaling; run confusion workshop.  
- If enrichment precision < 0.40: expand lexicon & re-balance baseline sampling.  
- If placebo interaction effect 95th percentile > observed: treat drift claim as unsupported; gather more data.  

## Open Decisions Log (Fill as You Go)
| Date | Decision | Options Considered | Rationale | Impact |
|------|----------|--------------------|-----------|--------|
| YYYY-MM-DD |  |  |  |  |

## Notes
Maintain minimal cross-file duplication: this master checklist is authoritative; reflect only high-level status mirrors in `PROJECT_STATUS.md`.
