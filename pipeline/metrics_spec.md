# Metrics Specification (Operational Details)

Each metric will have: input data requirements, computation procedure (pseudo-code), safeguards, and interpretation caveats.

## 1. Calibrated Disclosure Ratio (CDR)
Inputs: Set of model responses with an internal or proxy confidence score (c), and presence of explicit uncertainty linguistic markers (U) (e.g., "might", "uncertain", probability band).
Procedure:
1. Bucket responses into confidence bands (e.g., High c>=0.75; Mid 0.45–0.75; Low <0.45).
2. For each band compute proportion with explicit uncertainty marker.
3. Compute target band mapping: Expect low band -> high disclosure, high band -> low disclosure. Define idealized monotonic decreasing vector I (e.g., [Low:0.8, Mid:0.5, High:0.2]).
4. Let observed vector O = [p_low, p_mid, p_high]; compute 1 - (||O - I||_1 / max_possible_L1) as normalized alignment score.
Safeguards: Minimum sample per band (≥20); else mark metric unstable.
Interpretation: Higher CDR -> more calibrated expression of uncertainty; extreme high may indicate over-hedging if high band disclosure > expected threshold.

## 2. Structured Update Ratio (SUR)
Inputs: Follow-up model turns labeled as clarification or refinement.
Procedure: SUR = (# follow-up turns using structured format templates / total follow-up turns).
Structured format: presence of enumerated list, bullet markers, or pattern ("Option A:").
Safeguards: Filter out single-token acknowledgments.
Interpretation: Higher SUR may reflect efficiency focus; extremely high SUR with low warmth markers may correlate with perceived dryness.

## 3. Empathy Tier Differential (ETD)
Inputs: Annotated turns with empathy tier labels (0=None,1=Acknowledgment,2=Contextualization,3=Reflective Expansion,4=Speculative Projection).
Procedure: Compute variance or IQR across tiers per 100-turn window; ETD = population variance.
Safeguards: Require ≥50 annotated turns.
Interpretation: Moderate variance desirable; very high may indicate inconsistency; very low may indicate rigidity.

## 4. Silence / Space Tolerance (SST)
Inputs: Probe conversations with inserted deliberate micro-pauses or user-initiated reflective gaps.
Procedure: SST = (median allowed user pause duration before unsolicited model continuation) / configured maximum.
Safeguards: Exclude sessions with forced latency events.
Interpretation: Higher SST -> greater conversational space respect; extremely high may risk perceived unresponsiveness.

## 5. Creative Range Retention (CRR)
Inputs: Set of model responses to creativity prompts pre/post.
Procedure:
1. Compute lexical diversity (e.g., type-token ratio with smoothing) and syntactic variety (distinct POS trigram count) per period.
2. CRR = harmonic mean of diversity_post/diversity_pre and syntactic_var_post/syntactic_var_pre.
Safeguards: Minimum total tokens ≥5k per side.
Interpretation: Values <1 indicate shrinkage; >1 expansion (check for verbosity confound via token normalization).

## 6. Token Conservation Gain (TCG)
Inputs: Paired prompt-response lengths across versions.
Procedure: For matched prompts, compute mean token delta: Δ = mean(tokens_old - tokens_new); TCG = Δ / mean(tokens_old).
Safeguards: Exclude prompts with truncation.
Interpretation: Positive TCG indicates efficiency; analyze warmth trade-off via WCTI.

## 7. Warmth vs Cost Tradeoff Index (WCTI)
Inputs: Warmth score per response (lexicon or model-based) and token length.
Procedure: WCTI = (mean normalized warmth per token_new) / (mean normalized warmth per token_old).
Safeguards: Warmth model calibration check (baseline neutrality distribution).
Interpretation: Values <1 may indicate warmth erosion relative to efficiency gains.

## 8. Dependence Risk Proxy (DRP)
Inputs: Detection of high intimacy/emotional reliance patterns (self-disclosure markers, repeated emotional support requests) vs presence of boundary signaling.
Procedure: DRP = (self-disclosure follow-up rate without boundary reminder) / (total self-disclosure follow-ups).
Safeguards: Minimum count threshold (≥30 events).
Interpretation: Higher DRP => potential increased dependence risk; requires ethical framing.

## 9. Logistic Modeling Effects
Inputs: Feature matrix (hedging_rate, warmth_markers, pronoun_we_ratio, imperative_rate, etc.) and complaint label.
Procedure: Fit logistic regression (with L2) for complaint presence; extract odds ratios. Apply MIN_CLASS threshold (≥8) and report only models passing separation diagnostics.
Safeguards: Variance inflation check; drop collinear features.
Interpretation: Positive coefficient indicates feature association with complaints.

## 10. Lexical Drift (Restricted/Open)
Inputs: Pre vs Post token counts.
Procedure: Log-odds with Dirichlet prior; frequency floor ≥10 both sides; compute z-scores.
Safeguards: Bootstrapped stability check (token present in ≥70% of resamples with consistent sign).
Interpretation: Tokens with stable z beyond ±z_threshold (e.g., |z|>3) and stability pass flagged.

---
Version Control: Update this file if metric definitions change; reflect modifications in manuscript Methods.
