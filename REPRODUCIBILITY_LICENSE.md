# Reproducibility License Statement (Agents4Science 2025)

Scope: This statement governs what we will release to enable reproducibility while protecting user privacy and platform terms.

1) Code and Config
- License: MIT (permissive). You may use, modify, and redistribute.
- Includes: pipeline scripts, prompts (text), configs, figure tooling, and analysis notebooks.

2) Data
- We will not redistribute raw Reddit content. Instead we will release:
  - Aggregated statistics and derived features (counts, token frequencies, anonymized lexicons).
  - Normalized schema definitions and validators.
  - Sampling manifests with hashed identifiers (salted) and timestamps truncated to day-level.
- Any quoted examples will be paraphrased (≥5-word changes while preserving meaning) and checked for searchability suppression.

3) Artifacts
- Probe prompts and parameter settings (temperatures, seeds, versions) will be published.
- Figures and tables will be regenerated from released code and derived artifacts.

4) Ethical Guardrails
- No attempts to re-identify users; no redistribution of raw handles or verbatim niche content.
- All scripts default to privacy-preserving settings (e.g., salted author hashing required by CLI).

5) How to Cite and Use
- Cite the paper and link to this repository. For any derivative datasets, clearly note the absence of raw user content and comply with the platform’s terms of service.

(Initial version: 2025-09-10)
