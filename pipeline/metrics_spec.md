# Metrics Specification (Initial Scaffold)

Gating Criteria (registered):
- Inter-annotator reliability: Cohen's kappa ≥ 0.70 for major tags (warmth, creativity, helpfulness, hedging) prior to scale-up.
- Lexical drift tokens considered only if frequency ≥ 10 in both pre and post.
- Bootstrap sign consistency threshold: ≥ 0.80 for stable token direction claims.
- Regression outcomes included only if each class count ≥ 8 (MIN_CLASS).

Primary Metrics:
1. Complaint Incidence Shift: Interaction OR from logistic regression tag ~ pre_post * transition + controls.
2. Lexical Drift: Log-odds with informative Dirichlet prior (Monroe et al.) per token.
3. Enrichment Precision: Wilson 95% CI for complaint rate among enriched strata.
4. Relative Risk (enriched vs baseline) for complaint prevalence.
5. Probe Metrics (placeholders): CDR, SUR, ETD, SST, CPR, DRP (to be operationalized once probe suite defined).

Risk Register (living, initial entries):
| Risk | Description | Mitigation | Trigger | Status |
|------|-------------|------------|---------|--------|
| Incomplete historical coverage | Missing days in windows | Coverage report + gap flagging | >1 missing day per phase | Open |
| Low reliability | κ < 0.70 on major tag | Confusion audit + guideline refinement | Pilot κ computation | Open |
| Enrichment bias | Lexicon over-focuses on certain failure modes | Evaluate relative risk + expand lexicon | Precision lower bound <0.30 | Open |
| Sparse high-score strata | Few hi score posts reduce balance | Dynamic reallocation documented | n<5 hi per phase | Open |
| Privacy leak | Raw usernames accidentally stored | Hash & exclude handles | Username present in normalized row | Open |

Next Revision Triggers:
- After pilot disagreement analysis (guideline v0.2).
- After first enrichment precision computation (≥150 labeled items).

Version History:
- v0.1 (scaffold) 2025-09-08
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

Naming Collision Note: Earlier internal drafts used CRR to denote "Concision Re‑prompt Rate". That legacy concept is now renamed to CPR (Concision Prompt Rate) wherever it still appears. All occurrences of CRR henceforth refer exclusively to Creative Range Retention.

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
## 11. Gating Criteria (Registered)
* Annotation reliability: Overall Cohen's kappa ≥ 0.70 for major tags (WARMTH_LOSS, CREATIVITY_DROP, HELPFULNESS_REGRESSION, HEDGING_SHIFT) prior to scaling beyond pilot.
* Drift reporting: Only tokens with (freq_pre ≥10 AND freq_post ≥10) AND stability_sign_consistency ≥ 0.8 AND |z| ≥ 3.
* Regression models: Outcome classes require MIN_CLASS ≥ 8 positives & ≥ 8 negatives; otherwise model skipped and logged.
* Probe metrics: Each metric requires ≥50 valid conversations (or events) per model version; else annotate as underpowered.
* Enrichment evaluation: Precision lower bound (Wilson 95% CI) must exceed 0.30; otherwise lexicon expansion required before complaint prevalence claims.
* Lexical–theme coupling: Report only tokens where conditional tag OR 95% CI excludes 1.0.
* Placebo validation: Observed interaction effect must exceed 95th percentile of placebo distribution to claim drift effect.

## 12. Risk Register (Operational)
| Risk | Category | Trigger | Mitigation | Residual |
|------|----------|---------|------------|----------|
| Incomplete historical days | Data completeness | Missing >1 contiguous day per window | Truncate window; note in coverage table | Slight reduction in power |
| Low reliability on subtle tags | Annotation quality | κ <0.55 after pilot | Confusion workshop; add boundary examples | Potential schedule slip |
| Lexicon enrichment bias | Sampling bias | Precision <0.40 | Expand paraphrase set; increase baseline sample proportion | Moderate over-representation risk |
| Model separation in logistic | Statistical | Perfect prediction warning | L2 penalty; collapse rare tags | Reduced interpretability for rare tags |
| Overfitting drift to topical tokens | Construct validity | Top drift tokens unrelated to persona | Restrict to complaint-linked OR tokens | Some drift signal loss |
| Probe API version deprecation | External dependency | 410/404 responses | Snapshot prompt logs; fallback alt model version | Missing direct comparability |
| Parasocial risk inflation | Ethics | DRP >0.4 threshold | Strengthen boundary prompts; flag in Discussion | Residual dependency risk |
| Cost overrun for probes | Budget | API spend > planned | Early small-scale calibration; adjust prompt count | Lower metric confidence |

Version Control: Update this file if metric definitions change; reflect modifications in manuscript Methods.
