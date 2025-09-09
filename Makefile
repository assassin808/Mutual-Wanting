# Quick pipeline task shortcuts

PY?=python3

DATA_DIR=pipeline/data
OUT_DIR=pipeline/outputs

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
