# Experiments Directory

This directory contains the organized experimental code for the AI Researcher project, restructured for clarity and maintainability.

## Directory Structure

### `/core/` - Core Experimental Components
Essential scripts that form the foundation of the experimental pipeline:

- **`reliability_scaffold.py`** - Inter-annotator agreement analysis using Cohen's kappa and Krippendorff's alpha
- **`recompute_features_selection.py`** - Feature extraction and recomputation with robust ID mapping
- **`multi_transition_sampling.py`** - Sampling framework for annotation batch preparation

### `/analysis/` - Data Analysis Scripts
Scripts for statistical analysis and pattern detection:

- **`drift_lexicon.py`** - Temporal drift analysis with log-odds computation
- **`agreement.py`** - Agreement metric computation and validation
- **`features_and_analysis.py`** - Feature engineering and statistical analysis

### `/visualization/` - Figure Generation
Scripts for creating publication-ready visualizations:

- **`render_fig2_confusion.py`** - Confusion matrix heatmap generation
- **`render_fig3_forest.py`** - Forest plot visualization
- **`render_fig5_probes.py`** - Probe analysis visualization

### `/validation/` - Quality Assurance
Scripts for validation and reproducibility testing:

- **`validate_artifacts.py`** - Artifact integrity checking
- **`probe_runner.py`** - Probe suite execution and validation
- **`seed_repro_test.py`** - Reproducibility testing with fixed seeds

## Usage

All scripts should be executed from the project root directory. The build system (`Makefile`) provides automated execution targets that coordinate these scripts appropriately.

Example:
```bash
# From project root
make wave1-all    # Executes full pipeline including core scripts
make reliability-wave1  # Runs reliability analysis
make paper        # Builds manuscript with figures
```

## Maintenance

This reorganized structure replaces the previous scattered layout in `scripts/` and `pipeline/` directories. All essential functionality has been preserved and logically organized for better maintainability.
