probes:
	$(PY) experiments/validation/probe_runner.py --prompts pipeline/probes/prompts.yaml --out $(OUT_DIR)/probes_manifest.json || true
	$(PY) pipeline/probe_stats.py --manifest $(OUT_DIR)/probes_manifest.json --out-json $(OUT_DIR)/probes_results.json --out-tsv $(OUT_DIR)/tables/probes_summary.tsv || true


regression:
	$(PY) pipeline/build_model_dataset.py --features-csv $(OUT_DIR)/feature_rows_live.csv --labels-csv pipeline/data/labels_consensus.csv --out-csv $(OUT_DIR)/model_dataset.csv || true
	$(PY) pipeline/run_regression.py --dataset-csv $(OUT_DIR)/model_dataset.csv --targets complaint helpfulness warmth hedging creativity --out-json $(OUT_DIR)/regression_results.json || true

# One-shot reproduce current state (no external data): figures, tables, probe scaffold, regression scaffold
reproduce-all: fast-iterate pilot-reports tables figs probes regression
# Quick pipeline task shortcuts

PY?=python3

DATA_DIR=pipeline/data
OUT_DIR=pipeline/outputs
DRAWIO?=npx --yes @drawio/cli
# Canonical source-of-truth for the system diagram lives in exports as Draw.io XML
DRAWIO_SRC=figures/drawio/exports/system.xml
DRAWIO_OUT_DIR=figures/drawio/exports

.PHONY: plan hygiene sample pilot-agreement features tables clean

plan:
	$(PY) pipeline/plan_archives.py --transitions pipeline/transitions.yaml --out pipeline/archive_plan.json

hygiene:
	$(PY) pipeline/dedupe_text.py --in $(DATA_DIR)/recent_corpus_merged.jsonl --out $(DATA_DIR)/recent_corpus_merged_dedup.jsonl --report $(DATA_DIR)/recent_corpus_dedupe_report.json --near --near-threshold 0.9 || true
	$(PY) pipeline/sensitive_filter.py --jsonl $(DATA_DIR)/recent_corpus_merged_dedup.jsonl --out $(DATA_DIR)/recent_corpus_sensitive_report.json || true

sample:
	$(PY) pipeline/sampler.py --files $(DATA_DIR)/recent_corpus_merged_dedup.jsonl --per-stratum 30 --out-dir $(OUT_DIR)/sampling_test || true

pilot-agreement:
	$(PY) pipeline/agreement.py --a $(DATA_DIR)/pilot_batch_A.csv --b $(DATA_DIR)/pilot_batch_B.csv --out $(OUT_DIR)/pilot_agreement.json || true
	$(PY) pipeline/disagreement_report.py --a $(DATA_DIR)/pilot_batch_A.csv --b $(DATA_DIR)/pilot_batch_B.csv --out $(OUT_DIR)/pilot_disagreements.json || true

features:
	$(PY) pipeline/features_and_analysis.py --raw $(DATA_DIR)/recent_corpus_merged_dedup.jsonl --out $(OUT_DIR)/feature_summary_live.json --emit-csv $(OUT_DIR)/feature_rows_live.csv || true

tables:
	$(PY) pipeline/table_prep.py --agreement $(OUT_DIR)/pilot_agreement.json --enrichment $(OUT_DIR)/enrichment_eval.json --regress $(OUT_DIR)/regression_results.json --drift-lex $(OUT_DIR)/drift_log_odds.json --drift-boot $(OUT_DIR)/drift_bootstrap.json --coverage $(OUT_DIR)/coverage_pilot.json --out-dir $(OUT_DIR)/tables || true
	$(PY) pipeline/table1_sampling_coverage.py --coverage $(OUT_DIR)/coverage_pilot.json --sampling-manifest $(OUT_DIR)/sampling_manifest.json --out-tsv $(OUT_DIR)/tables/table1_sampling_coverage.tsv || true

table1:
	$(PY) pipeline/table1_sampling_coverage.py --coverage $(OUT_DIR)/coverage_pilot.json --sampling-manifest $(OUT_DIR)/sampling_manifest.json --out-tsv $(OUT_DIR)/tables/table1_sampling_coverage.tsv || true

# Figure-ready CSV slices
figs:
	$(PY) pipeline/fig_prep.py --agreement $(OUT_DIR)/pilot_agreement.json --coverage $(OUT_DIR)/coverage_pilot.json --out-dir $(OUT_DIR)/figs || true

# Draw.io exports deprecated: system Fig1 is provided as a static PDF under figures/drawio/Fig1.pdf
drawio-export:
	@echo "drawio-export is deprecated; Fig1 is provided at figures/drawio/Fig1.pdf"

# Render Fig2 (confusion heatmap PNG) from generated CSV
fig2:
	$(PY) experiments/visualization/render_fig2_confusion.py pipeline/outputs/figs/confusion_heatmap.csv pipeline/outputs/figs/fig2_confusion_heatmap.png --out-pdf pipeline/outputs/figs/fig2_confusion_heatmap.pdf --normalize || true

# Fig3: forest plot from regression interactions TSV
fig3:
	$(PY) experiments/visualization/render_fig3_forest.py pipeline/outputs/tables/regression_interactions.tsv pipeline/outputs/figs/fig3_regression_forest.png --out-pdf pipeline/outputs/figs/fig3_regression_forest.pdf || true

# Fig5: probe metric contrasts from probes_summary.tsv
fig5:
	$(PY) experiments/visualization/render_fig5_probes.py pipeline/outputs/tables/probes_summary.tsv pipeline/outputs/figs/fig5_probe_contrasts.png --out-pdf pipeline/outputs/figs/fig5_probe_contrasts.pdf || true

# Convenience: all figures (CSV slices + fig2)
figs-all: figs fig2 fig3 fig5

# Lint Python with ruff; write JSON report (does not fail pipeline)
lint:
	@mkdir -p $(OUT_DIR)
	ruff check pipeline experiments --output-format=json > $(OUT_DIR)/lint_report.json || true
	@echo "Lint report -> $(OUT_DIR)/lint_report.json"

# Validate JSON artifacts in outputs; and JSONL schema for pilot normalized
validate-artifacts:
	$(PY) experiments/validation/validate_artifacts.py --dir $(OUT_DIR) --out $(OUT_DIR)/artifact_validation.json || true
	$(PY) experiments/validation/jsonl_schema_check.py --jsonl pipeline/data/recent_corpus_normalized_pilot.jsonl --required id subreddit author_hash created_utc score body parent_id link_id transition pre_post || true

# Quality bundle
quality: lint validate-artifacts term-check

# Terminology consistency (CPR vs CRR for concision)
term-check:
	$(PY) experiments/validation/terminology_check.py --root . --out $(OUT_DIR)/terminology_report.json || true

# Build LaTeX paper (best-effort; will not fail pipeline)
paper:
	( cd Agents4Science_Template && pdflatex -interaction=nonstopmode agents4science_2025.tex || true )
	( cd Agents4Science_Template && bibtex agents4science_2025 || true )
	( cd Agents4Science_Template && pdflatex -interaction=nonstopmode agents4science_2025.tex || true )
	( cd Agents4Science_Template && pdflatex -interaction=nonstopmode agents4science_2025.tex || true )

# Historical acquisition pipeline (expects JSONL dumps under $(DATA_DIR)/raw)
integrity-historical:
	$(PY) pipeline/archive_integrity.py --files $(DATA_DIR)/raw/*.jsonl --out $(OUT_DIR)/archive_integrity_report.json || true

archive-map:
	$(PY) pipeline/build_archive_map.py --integrity $(OUT_DIR)/archive_integrity_report.json --plan pipeline/archive_plan.json --out $(OUT_DIR)/archive_map.json || true

# Normalize one window file
# usage: make normalize-window TRANSITION=gpt4_to_4o PHASE=pre IN=$(DATA_DIR)/raw/gpt4_pre.jsonl OUT=$(DATA_DIR)/gpt4_to_4o_pre.jsonl AUTHOR_SALT=... 
normalize-window:
	@if [ -z "$(TRANSITION)" ] || [ -z "$(PHASE)" ] || [ -z "$(IN)" ] || [ -z "$(OUT)" ]; then \
		echo "Usage: make normalize-window TRANSITION=<id> PHASE=pre|post IN=<in.jsonl> OUT=<out.jsonl> AUTHOR_SALT=..."; \
		exit 1; \
	fi
	AUTHOR_SALT=$(AUTHOR_SALT) $(PY) pipeline/archive_normalize.py --transition-id $(TRANSITION) --phase $(PHASE) --in $(IN) --out $(OUT) --author-salt "$(AUTHOR_SALT)" || true

# Coverage for a normalized pre/post pair
# usage: make coverage-historical PRE=$(DATA_DIR)/gpt4_to_4o_pre.jsonl POST=$(DATA_DIR)/gpt4_to_4o_post.jsonl
coverage-historical:
	@if [ -z "$(PRE)" ] || [ -z "$(POST)" ]; then \
		echo "Usage: make coverage-historical PRE=<pre.jsonl> POST=<post.jsonl>"; \
		exit 1; \
	fi
	$(PY) pipeline/archive_coverage.py --pre $(PRE) --post $(POST) --out $(OUT_DIR)/archive_coverage_report.json || true

# Consensus merge of annotations (pilot A/B)
consensus:
	$(PY) pipeline/merge_annotations.py --inputs $(DATA_DIR)/pilot_batch_A.csv $(DATA_DIR)/pilot_batch_B.csv --out-csv $(DATA_DIR)/labels_consensus.csv --out-json $(OUT_DIR)/labels_consensus_summary.json || true

# Validate core artifacts quickly (pilot schema, leak check)
validate:
	$(PY) pipeline/jsonl_schema_check.py --jsonl pipeline/data/recent_corpus_normalized_pilot.jsonl --required id subreddit author_hash created_utc score body parent_id link_id transition pre_post || true
	$(PY) pipeline/feature_leak_check.py --features-csv $(OUT_DIR)/feature_rows_nearclean.csv --out $(OUT_DIR)/feature_leak_check_nearclean.json || true

# Pilot reports bundle: agreement, disagreements, early kappa, tables, figs
pilot-reports:
	$(PY) pipeline/agreement.py --a pipeline/data/pilot_batch_A.csv --b pipeline/data/pilot_batch_B.csv --out $(OUT_DIR)/pilot_agreement.json --mode pilot || true
	$(PY) pipeline/disagreement_report.py --a pipeline/data/pilot_batch_A.csv --b pipeline/data/pilot_batch_B.csv --out $(OUT_DIR)/pilot_disagreements.json || true
	$(PY) pipeline/early_kappa.py --a pipeline/data/pilot_batch_A.csv --b pipeline/data/pilot_batch_B.csv --overlap-ids pipeline/data/pilot_batch_overlap_ids.txt --out $(OUT_DIR)/early_kappa.json || true
	$(PY) pipeline/per_tag_kappa.py --a pipeline/data/pilot_batch_A.csv --b pipeline/data/pilot_batch_B.csv --out $(OUT_DIR)/per_tag_kappa.json || true
	$(MAKE) tables
	$(MAKE) figs

# New: optional user style clustering (depends on features target having run)
cluster:
	$(PY) pipeline/cluster_user_styles.py --features-csv $(OUT_DIR)/feature_rows_live.csv --out-json $(OUT_DIR)/style_clusters.json --out-csv $(OUT_DIR)/feature_rows_with_clusters.csv || true

# Annotation progress quick check (A batch example)
progress-a:
	$(PY) pipeline/annotation_progress.py --csv $(DATA_DIR)/pilot_batch_A.csv --out $(OUT_DIR)/pilot_A_progress.json --overlap-ids $(DATA_DIR)/pilot_batch_overlap_ids.txt || true

# Composite fast iteration: hygiene -> features -> cluster -> progress
fast-iterate: hygiene features cluster progress-a

# Early partial kappa on overlap IDs (binary per-tag columns)
early-kappa:
	$(PY) pipeline/early_kappa.py --a $(DATA_DIR)/pilot_batch_A.csv --b $(DATA_DIR)/pilot_batch_B.csv --overlap-ids $(DATA_DIR)/pilot_batch_overlap_ids.txt --out $(OUT_DIR)/early_kappa.json || true

# Enrichment evaluation (needs labeled enriched & baseline CSVs)
enrichment-eval:
	$(PY) pipeline/enrichment_eval.py --enriched-labeled $(DATA_DIR)/enriched_labeled.csv --baseline-labeled $(DATA_DIR)/baseline_labeled.csv --out $(OUT_DIR)/enrichment_eval.json || true

# Feature leakage guard
leak-check:
	$(PY) pipeline/feature_leak_check.py --features-csv $(OUT_DIR)/feature_rows_live2.csv --out $(OUT_DIR)/feature_leak_check.json || true

# Reproduce (current partial pipeline) – expands fast-iterate with leak & early kappa attempt
reproduce: fast-iterate leak-check early-kappa

# Near-duplicate only (adjust threshold via NEAR_T)
NEAR_T?=0.9
nearpass:
	$(PY) pipeline/text_minhash.py --jsonl $(DATA_DIR)/recent_corpus_merged_dedup2.jsonl --out $(OUT_DIR)/near_pairs.json --jaccard-min $(NEAR_T) || true


# Conservative near-duplicate clean then sensitive log
near-clean:
	$(PY) pipeline/text_minhash.py --jsonl $(DATA_DIR)/recent_corpus_tagged.jsonl --out $(OUT_DIR)/near_pairs.json --jaccard-min $(NEAR_T) || true
	$(PY) pipeline/apply_near_duplicate_filter.py --jsonl $(DATA_DIR)/recent_corpus_tagged.jsonl --pairs $(OUT_DIR)/near_pairs.json --out-jsonl $(DATA_DIR)/recent_corpus_merged_nearclean.jsonl --report $(DATA_DIR)/near_duplicate_filter_report.json --mode pairwise --removal-cap-frac 0.05 --secondary-jaccard-min $(NEAR_T) --min-tokens 10 || true
	$(PY) pipeline/sensitive_filter.py --jsonl $(DATA_DIR)/recent_corpus_merged_nearclean.jsonl --out $(DATA_DIR)/recent_corpus_sensitive_report.json || true


clean:
	rm -f $(OUT_DIR)/*.json $(OUT_DIR)/*.csv
	rm -rf $(OUT_DIR)/tables

# --- New convenience targets for Wave 1 scaffolds ---
.PHONY: reliability-wave1 selection-features drift-retirement

reliability-wave1:
	$(PY) experiments/core/reliability_scaffold.py \
	  --a pipeline/data/label_batch1_A_enriched.csv \
	  --b pipeline/data/label_batch1_B_enriched.csv \
	  --overlap pipeline/data/label_batch1_overlap_ids.txt \
	  --label-col primary_tag \
	  --out $(OUT_DIR)/annotation/reliability_wave1.json || true

selection-features:
	$(PY) experiments/core/recompute_features_selection.py \
	  --selection $(OUT_DIR)/annotation/selection_final.csv \
	  --enriched pipeline/data/label_batch1_enriched.csv \
	  --out-json $(OUT_DIR)/annotation/selection_features_summary.json \
	  --out-csv $(OUT_DIR)/annotation/selection_features.csv \
	  --selection-id-col id --enriched-id-col comment_id || true

drift-retirement:
	$(PY) experiments/analysis/drift_lexicon.py \
	  --pre pipeline/data/gpt4_retirement_chatgpt_pre.jsonl \
	  --post pipeline/data/gpt4_retirement_chatgpt_post.jsonl \
	  --out-json pipeline/data/drift_log_odds_restricted.json \
	  --freq-floor 10 --top 25 || true

# Generate figure-ready CSVs from reliability JSON and render Fig2 (once labels exist)
.PHONY: figdata-wave1 fig2-wave1 wave1-all
figdata-wave1:
	$(PY) pipeline/fig_prep.py --agreement $(OUT_DIR)/annotation/reliability_wave1.json --coverage $(OUT_DIR)/coverage_pilot.json --out-dir $(OUT_DIR)/figs || true

fig2-wave1: figdata-wave1
	$(PY) experiments/visualization/render_fig2_confusion.py $(OUT_DIR)/figs/confusion_heatmap.csv $(OUT_DIR)/figs/fig2_confusion_heatmap.png --out-pdf $(OUT_DIR)/figs/fig2_confusion_heatmap.pdf --normalize || true

# Convenience: run Wave 1 scaffolds end-to-end
wave1-all: selection-features reliability-wave1 figdata-wave1 drift-retirement
