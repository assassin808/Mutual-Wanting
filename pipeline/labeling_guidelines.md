# Labeling Guidelines (Pilot v0.1)

Purpose: Provide consistent definitions for pilot annotation of Reddit user complaints regarding model persona / quality drift.

Tags (binary: y / n / blank=unsure):
1. warmth: User explicitly or implicitly evaluates emotional tone (cold, empathetic, caring, sterile, robotic).
2. creativity: User references originality, variety, novelty, or avoidance of repetition / generic phrasing.
3. helpfulness: User comments on usefulness, practicality, accuracy (NOT mere politeness unless linked to usefulness).
4. hedging: Mentions of model uncertainty style (maybe, might, could, seems) framed as excessive, new, reduced, or problematic.
5. complaint: The post constitutes a complaint about any model change effect (if absent, other tags typically remain blank unless the user speculates on qualities anyway).

General Rules:
- Tag only once per item (no intensity scale).
- Prefer blank over forced guess if ambiguous.
- Multiple tags can co-occur (e.g., complaint + warmth + creativity).
- A neutral observation ("model says maybe more now") without dissatisfaction does NOT count as complaint unless negative framing.

Edge Cases:
- Sarcasm: If clearly negative about model quality -> complaint.
- Comparative: "Old model was more creative" => creativity=y, complaint=y.
- System prompts / jailbreak talk without quality claim: leave tags blank unless a quality claim appears.

Escalation List (capture for v0.2 refinement):
- Distinguishing warmth vs helpfulness when user references "caring details" that may also increase usefulness.
- Ambiguous hedging when user quotes only one instance.

Reliability Target: κ ≥ 0.70 major tags prior to scale annotation.

Change Log:
- v0.2 (planned) Coming refinement: clearer warmth vs helpfulness boundary; explicit examples of hedging vs factual uncertainty; add sarcasm decision matrix; add partial complaint framing cases ("miss the old model" vs direct dissatisfaction).
- v0.1 (pilot scaffold) 2025-09-08

---
## v0.2 Draft (DO NOT USE YET)

Planned Adjustments (pending pilot disagreement analysis):
1. Warmth vs Helpfulness Disambiguation
	- If user critiques lack of emotional tone AND output practicality, allow both tags; add examples where only one applies.
2. Hedging Definition Tightening
	- Require either (a) explicit user reference to increase/decrease in hedging OR (b) negative evaluation of hedging style; quoting a single "maybe" without evaluative context becomes blank.
3. Complaint Boundary Table
	| Scenario | Tag complaint? | Notes |
	|----------|----------------|-------|
	| "GPT-5 feels different" (no valence) | No | Lacks dissatisfaction signal |
	| "GPT-5 is drier / less creative" | Yes | Negative comparative quality |
	| "I miss GPT-4" | Yes | Implicit negative evaluation of current model |
	| "Used GPT-4o for poetry" (nostalgic, neutral) | No | Historical usage only |
4. Sarcasm Handling
	- Treat clearly derisive tone about model performance as complaint even if superficially positive phrasing ("Amazing how it forgets instantly").
5. Multi-Aspect Comments
	- Permit up to all five tags if independently satisfied; emphasize independence no exclusivity.
6. Annotation Etiquette
	- Prefer leaving ambiguous singular hedge quotes blank vs over-tagging.
7. Reliability Aid Examples
	- Add 5 positive examples + 5 borderline + 5 negative for each major tag.

This draft section will be merged + versioned after κ computation and disagreement audit.

# Reddit Model Transition Complaint Labeling Guidelines

Version: 0.1.1 (2025-09-08)  
(Minor corrective update: pilot size fix; added gating criteria reference.)
Primary goal: Consistent labeling of user comments discussing model version changes (GPT-3.5→4, 4→4o, 4o→5) to quantify shifts in complaint theme prevalence.

## 1. General Instructions
- Unit of labeling: individual comment (not thread). If a comment quotes another comment, ignore the quoted text when assigning tags.
- Assign exactly ONE primary tag (choose the dominant complaint theme). If no listed theme fits, assign `NONE` (rare — review later). 
- Assign any number of secondary flags that apply.
- If sentiment is purely positive about an upgrade, primary tag = `UPGRADE_BENEFIT`.
- If the comment mixes multiple complaints with roughly equal salience, pick the first in the priority order list below.

Priority order (tie-breaker): Warmth > Helpfulness > Creativity > Safety/Refusal > Hedging Shift > Memory > Verbosity > Latency > Access > Other.

## 2. Primary Tags (Mutually Exclusive)
| Tag | Definition | Inclusion Examples | Exclusion / Edge Notes |
|-----|------------|--------------------|-------------------------|
| WARMTH_LOSS | Perceived reduction in friendliness, empathy, personality, tone richness | "It feels colder now", "lost its personality" | Creativity-specific complaints go to CREATIVITY_DROP unless explicitly emotional tone focus |
| CREATIVITY_DROP | Decline in imaginative / varied / novel outputs | "Stories are generic now" | If framed as emotional distance, use WARMTH_LOSS |
| HELPFULNESS_REGRESSION | Accuracy, correctness, factual depth, reasoning worse | "It gets facts wrong now" | If hedge style focus without correctness claim → HEDGING_SHIFT |
| HEDGING_SHIFT | Over-hedging (too cautious) OR under-hedging (too certain) without explicit correctness claim | "Now it keeps saying it *might* be wrong" | If paired with correctness failure → HELPFULNESS_REGRESSION |
| SAFETY_REFUSAL_SHIFT | New refusals, broader safety filters, or inconsistent safety gating | "It refuses harmless stuff now" | Pure factual decline ≠ this|
| MEMORY_CONTINUITY | Remembers less context, loses thread continuity, conversational forgetfulness | "It forgets what we said 2 mins ago" | If described as general unhelpfulness, classify HELPFULNESS_REGRESSION |
| VERBOSITY_CHANGE | Too short, too terse, or too verbose (length complaint) | "Replies are just one line now" | If brevity tied to loss of warmth, choose WARMTH_LOSS |
| LATENCY_SPEED | Slower or inconsistent response speed | "Getting really slow now" | Token or cost comments → ACCESS_LIMITS |
| ACCESS_LIMITS | Rate limits, paywall, availability, capacity messages | "Constantly hitting usage cap" | Performance speed complaints → LATENCY_SPEED |
| UPGRADE_BENEFIT | Explicit praise of improvement (creativity, reasoning, speed) | "5 is way better at math" | Mixed with complaint—label complaint tag |
| NONE | No clear mapping; meta discussion without experiential claim | "People are overreacting" | Use sparingly |

## 3. Secondary Flags (Multi-Label)
| Flag | Definition | Examples |
|------|------------|----------|
| ANTHRO_LANG | Human-like attribution of intent/personality/feelings | "It seems depressed" |
| PARASOCIAL | Emotional attachment / companionship framing | "I miss the old friend it was" |
| NOSTALGIA | Comparative backward-looking phrase | "It used to", "back when 4 would" |
| POSITIVE_COUNTER | Contains a counterbalancing positive note | "Colder, but more accurate" |
| META_SPECULATION | Speculates on internal changes (training, nerfing) | "They nerfed it to cut costs" |

## 4. Decision Flow (Simplified)
1. Is main focus praise? → UPGRADE_BENEFIT.
2. Is main focus emotional tone/personality? → WARMTH_LOSS.
3. Is main focus creativity/novelty? → CREATIVITY_DROP.
4. Is main focus correctness depth? → HELPFULNESS_REGRESSION.
5. Is main focus hedging style? → HEDGING_SHIFT.
6. Safety / refusal gating? → SAFETY_REFUSAL_SHIFT.
7. Context retention? → MEMORY_CONTINUITY.
8. Length / brevity / verbosity? → VERBOSITY_CHANGE.
9. Speed? → LATENCY_SPEED.
10. Access / limits? → ACCESS_LIMITS.
11. Else NONE.

## 5. Ambiguity Handling
- Comment: "It’s so short and boring now." If strong boredom tone (personality), choose WARMTH_LOSS; else VERBOSITY_CHANGE.
- Comment: "It hedges more and is less accurate." Choose HELPFULNESS_REGRESSION (accuracy trumps hedging).
- Comment: "Miss old creative flair; now basic facts still fine." Choose CREATIVITY_DROP.

## 6. Annotation Quality Control
Pilot batch: 60 comments (20 overlap dual-labeled; 20 unique A; 20 unique B).

Reliability: Compute Cohen’s κ overall and per-major tag (WARMTH_LOSS, HELPFULNESS_REGRESSION, CREATIVITY_DROP, HEDGING_SHIFT). Target κ ≥0.70 before scaling.

Drift check: Every additional 200 consensus labels, re-label 20 previously labeled comments (temporal consistency audit).

Gating Criteria Reference: See `pipeline/metrics_spec.md` Section 11 for formal gating thresholds (kappa, token frequency floors, bootstrap stability ≥0.8). Scaling proceeds only if pilot reliability gate passes.

## 7. Data Fields for Export
Each labeled row should include:
`comment_id, thread_id, parent_id, created_utc, model_transition_window, pre_post_window, body_text (sanitized), primary_tag, secondary_flags (semicolon-separated), annotator_id`

## 8. Privacy / Ethics Notes
- Do not store usernames.
- Hash any user identifiers if needed for per-user style clustering.
- Avoid quoting long verbatim examples in the paper; convert to paraphrase.

## 9. Link to Literature Support (Selected)
- Warmth / Anthropomorphism: Epley 2007; Horton & Wohl 1956; Peter et al. 2025.
- Hedging / Trust Calibration: Yin 2019; Lai & Tan 2019; Kay 2016.
- Safety / Refusal: Amershi 2019 (guidelines on failure handling); Kizilcec 2016 (transparency load).
- Continuity Gaps: (Gap — highlight as under-studied).

## 10. Change Log
- v0.1: Initial schema creation.
- v0.1.1: Corrected pilot size (60 not 80); added explicit reliability gate reference; clarified overlap structure.
