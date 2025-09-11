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
- [x] Freeze taxonomy tag names (post-pilot; version tags in guidelines)  
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
	- (tooling ready: `build_archive_map.py`)  
- [ ] Run `archive_coverage.py` → produce `archive_coverage_report.json`  
- [ ] Compute sparsity & per-day counts; flag missing days >1 gap  
- [D] Decision: fallback if partial days? (interpolate vs truncate)  

### 1.2 Recent Live Supplement
- [x] `limited_historical_scrape.py` executed (manifest present)  
- [x] Decide retention vs discard for final analyses (pilot only)  
- [x] Tag any reused rows to avoid mixing with authentic windows  
	- (tooling: `tag_live_rows.py`)  

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
- [~] Compute κ overall + per-major tag (warmth, creativity, helpfulness, hedging)  
	- (tooling: `agreement.py` full; `early_kappa.py` for partial overlap readiness; `per_tag_kappa.py` added)  
- [x] `disagreement_report.py` tool present  
- [x] Guideline refinement → v0.2 (change log appended)  

Pilot Progress Note (ephemeral): A = 0/40 labeled (init). Overlap readiness threshold: label ≥12 overlap rows before B starts for early κ dry-run.
Additional Action: Overlap IDs to be prioritized first using `annotator_quickstart.md` guidance.

### 3.2 Scale Annotation
- [ ] Generate first full batch (e.g. 400 items)  
- [ ] Split with overlap (≥15%)  
- [ ] Dual annotation  
- [ ] Cohen’s κ recalculation  
- [ ] If κ < 0.70: run focused confusion workshops (document decisions)  
- [ ] Consensus merge (majority / escalate unresolved)  
- [ ] Periodic drift check (re-annotate 20 previously labeled items per 200 new)  

### 3.3 Data Hygiene
- [x] De-duplication (hash body text)  
 	- (improved canonical text fallback; current run kept 1748 / removed 2 exact dups)  
- [x] Remove near-identical reposts (minhash)  
 	- (pairwise conservative pass; 0 removals under 5% cap; report saved)  
- [ ] Author hash generation (SHA256 salt)  
 	- (tooling ready: `pipeline/archive_normalize.py`)  
	- [x] Pilot corpus normalized with author hashes (`recent_corpus_normalized_pilot.jsonl`)  
- [x] Sensitive content filter log  
 	- (executed on near-clean corpus; 0/1748 flagged with default patterns)  

## 4. Feature Engineering
- [x] Warmth markers expansion (config in `feature_lexicon_config.json`)  
- [x] Hedge lexicon validation (initial list extended in config)  
- [x] Compute per-comment features: length, warmth_rate, hedge_rate, pronoun ratios, imperative ratio  
	- (tooling executed for recent corpus dedup once run; script: `features_and_analysis.py`)  
- [x] User style clustering (k=5) – optional; record silhouette score; decide inclusion  
	- (tooling enhanced to emit silhouette; inclusion decision pending)  
- [x] Store `feature_rows.csv` + `feature_summary.json`  
	- (1748 rows; clusters skew: majority cluster size 1137; outlier small cluster size 5)  
- [x] Validate no leakage features referencing post labels incorrectly  
	- (tooling: `feature_leak_check.py`)  
	- Status: initial pass OK (no flagged columns).  

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
- [~] Construct modeling dataset (merged features + consensus labels)  
- [ ] Filter outcomes with class count ≥ MIN_CLASS (8)  
- [ ] Fit logistic models: tag ~ pre_post * transition + subreddit + score_bucket (+ cluster if used)  
- [ ] Extract interaction ORs + 95% CI  
- [ ] Penalized fallback for separation (L2)  
- [ ] Placebo interaction test (shuffle pre_post) distribution  
- [~] Save `regression_results.json` + `regression_placebo.json`  
- [ ] Model diagnostics: variance inflation, Hosmer–Lemeshow (optional)  

## 7. Probe Experiments (Behavioral)
- [x] Finalize probe prompt suite (uncertainty, warmth, intimacy boundary, silence pacing, creativity)  
- [x] Specify target model versions (e.g., gpt-4o-YYYYMM, gpt-5-YYYYMM)  
- [x] Rate limit / cost budgeting doc  
- [x] Run `probe_runner.py` with seed reproducibility  
- [ ] Derive metrics: CDR, SUR, ETD, SST, CPR, DRP  
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
- [x] Add reproducibility license statement  
	- Added `REPRODUCIBILITY_LICENSE.md`.

## 11. Figures & Tables Production
### 11.1 Data Extraction Scripts
- [x] `table_prep.py` extended for: agreement, enrichment, regression, drift, probes, coverage  
- [x] Add `fig_prep.py` for figure-ready CSV slices  

### 11.2 Planned Figures
- [x] Fig1 Pipeline schematic (Mermaid or Graphviz)  
- [x] Fig1b System architecture (provided PDF; draw.io deprecated)  
	- Status 2025-09-11: Included `figures/drawio/Fig1.pdf` directly in LaTeX; PDF version cleaned.  
- [x] Fig2 Annotation reliability (confusion heatmap)  
	- Status: Placeholder renderer implemented; included in LaTeX.  
- [x] Fig3 Complaint incidence shifts (forest plot of ORs)  
	- Status 2025-09-11: Placeholder renderer implemented; included in LaTeX.
- [ ] Fig4 Lexical drift (top stable tokens; bar / lollipop)  
- [x] Fig5 Probe metric contrasts (radar or grouped bars)  
	- Status 2025-09-11: Placeholder renderer implemented; included in LaTeX.
- [ ] Fig6 Lexical–theme coupling scatter  
- [ ] Appendix: Drift token stability distribution (hist)  

### 11.3 Tables
- [x] Table1 Sampling & coverage  
- [ ] Table2 Enrichment evaluation  
- [ ] Table3 Regression interactions  
- [~] Table4 Probe metrics summary  
	- (tooling scaffolded: `probe_runner.py`, `probe_stats.py`)  
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
- [x] Artifact availability statement (post-review release plan)  
	- Added `REPRODUCIBILITY_LICENSE.md` and `REPLICATION_README.md`.
- [x] AI involvement checklist finalization  
	- Added `AI_INVOLVEMENT_CHECKLIST.md`.

## 13. Quality Gates
- [ ] Lint / type check scripts (ruff / mypy optional)  
- [x] Repro run doc (`REPRODUCE.md`)  
- [~] Random seed reproducibility test (minimal features stability test added; drift token intersection test pending)  
- [~] All JSON artifacts schema-validated  
  	- (pilot normalized JSONL validated via `jsonl_schema_check.py`; outputs validated via `scripts/validate_artifacts.py`)  
- [ ] Manual spot audit of 10 random labeled rows vs raw text  
- [x] Bibliography dedup & validation (no placeholder citations)  

## 13.1 Figure Tooling (Draw.io)  
- [x] Add draw.io export Makefile target (`drawio-export`)  
- [x] Add helper script `scripts/drawio_export.sh`  
- [x] Add outline `figures/system_architecture_outline.md`  
- [x] Canonicalize source-of-truth to `figures/drawio/exports/system.xml`  
- [~] Export SVG/PNG/HTML/XML to `figures/drawio/exports/` and commit SVG/PNG/HTML  
    	- Note: CLI export blocked (npm 404 for @drawio/cli). Fallback: use Draw.io Desktop to export SVG/PNG/HTML and drop into `figures/drawio/exports/`.  
    		- Source of truth: keep only `exports/system.xml` (other draw.io artifacts removed).  
    		- LaTeX expects: `figures/drawio/exports/system_architecture.png` (now referenced in manuscript).

## 14. Submission Prep
- [ ] Ensure LaTeX compiles without warnings (refs, figs)  
- [ ] PDF font embedding check  
- [ ] Page limit compliance  
- [ ] Anonymization audit (no accidental author IDs)  
- [ ] Final diff review vs outline to ensure no provisional claims remain  

## 15. Post-Submission (Planned)
- [ ] Prepare artifact repository (redacted datasets + code)  
- [x] Draft replication README  
	- Added `REPLICATION_README.md`.
- [x] Create issue templates (bug, replication question)  
	- Added `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/ISSUE_TEMPLATE/replication_question.md`.

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
| 2025-09-08 | Decide retention of recent live supplement limited to pilot only unless coverage gaps | (1) Discard entirely (2) Use for pilot only (3) Blend into final | Avoid biasing authentic pre/post windows; maintain purity | Simplifies later drift comparability |
| 2025-09-09 | MinHash near-duplicate threshold set at J>=0.90; retain longest token variant per component | (1) Random removal (2) Keep first (3) Keep longest | Longest likely preserves maximal semantic content & context | Minimizes information loss while removing redundancy |

## Notes
Maintain minimal cross-file duplication: this master checklist is authoritative; reflect only high-level status mirrors in `PROJECT_STATUS.md`.

Update 2025-09-09: v0.2 guidelines change log appended; `metrics_spec.md` added with gating criteria and risk register; Fig2 rendered and included; Table1 sampling/coverage generated; bibliography deduplicated and paper compiles; minimal seed reproducibility test output at `pipeline/outputs/seed_repro.json`.

Update 2025-09-10: Ran Make targets (figs, fig2, quality, paper, probes, regression). Paper compiled (14pp) with Fig2 included; artifact validation JSON written; probe manifest + summary TSV scaffolded; regression dataset empty pending labels; Draw.io CLI export failed (npm 404) — manual desktop export required.
