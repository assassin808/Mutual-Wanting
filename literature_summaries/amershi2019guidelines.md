# Amershi et al. (2019) — Guidelines for Human-AI Interaction

Citation Key: amershi2019guidelines

## 1. Core Contribution
Introduces 18 empirically-derived guidelines for designing interactive AI systems across the lifecycle (initial onboarding, interaction, error handling, feedback, evolution).

## 2. Study Design & Methods
- Mixed-method: literature synthesis + heuristic extraction + iterative validation.
- Evaluated across multiple deployed AI products at Microsoft via internal expert review and designer uptake.

## 3. Key Findings
- Lifecycle framing (before, during, after interaction) improves guideline memorability.
- Designers under-address adaptation feedback and failure recovery.
- Early disclosure and graceful degradation essential for sustained trust.

## 4. Limitations / Threats to Validity
- Corporate context (Microsoft) may bias generalizability.
- Lack of quantitative user outcome measures tied to each guideline.
- Possible survivorship bias in which guidelines persisted.

## 5. Relevance to Mutual Wanting Framework
- Provides scaffolding for how systems signal evolving “wants” (e.g., capability changes, adaptation boundaries).
- Supports our proposed Router Transparency & Prompt Provenance interventions via guidelines on explanation timing and iterative refinement.

## 6. How It Informs Metrics / Design
- Justifies inclusion of Trust Calibration Gap and Confidence Disclosure Rate: aligns with guidelines on setting correct expectations.
- Inspires an operational checklist for our Reddit coding of expectation violations.

## 7. Integration Plan in Paper
Cited in Introduction (context-setting) and Methodology (design principles for intervention prototypes / prompt legibility surfaces).

## 8. Open Questions for This Work
- Which subset of 18 guidelines most predictive of reduced backlash in model version transitions?
- Can guidelines be ranked by frequency of violation in community discourse?
