# System Figure (Draw.io) – Outline

Purpose: Capture the end-to-end pipeline at a glance for Agents4Science 2025. This outline is mirrored from the Mermaid schematic but structured for draw.io.

Recommended layout (left→right):

1) Acquisition
   - Blocks: Historical Dumps (4→4o, 4o→5), Live Supplement (pilot only)
   - Notes: SHA256 integrity, time windows (transitions.yaml)

2) Hygiene / Normalization
   - Blocks: Dedup (exact + MinHash), Sensitive Filter, Normalize + Author Hash
   - Notes: canonical text fallback; conservative near-dup cap 5%

3) Sampling
   - Blocks: Baseline Random; Enriched Keywords; Score Buckets
   - Notes: manifests with rationale

4) Annotation
   - Blocks: Pilot A/B (20 overlap), Early κ, Guidelines v0.2 loop
   - Notes: κ≥0.70 gating for major tags

5) Features & Clustering
   - Blocks: warmth, hedging, pronouns, imperative; optional K=5 clustering (silhouette)

6) Analyses
   - Columns:
     a) Drift (log-odds + bootstrap; complaint-linked)
     b) Regression (pre×transition interactions; placebo)
     c) Probes (uncertainty, warmth, intimacy, pacing, creativity)

7) Coupling + Robustness
   - Blocks: lexical–theme coupling; enrichment precision; coverage; placebos

8) Outputs
   - Tables: agreement, enrichment, regressions, drift, probes, robustness
   - Figures: confusion heatmap, forest plots, drift lollipops, radar, coupling scatter

Styling notes:
- Use swimlanes for phases; color-code: Acquisition (gray), Hygiene (orange), Sampling (blue), Annotation (purple), Features (teal), Analyses (green), Outputs (gold).
- Add small privacy badge next to “author hash” block.
- Add “no synthetic data” badge near Analyses.

Export targets (Makefile: drawio-export): svg, png, html, and raw xml clone.
