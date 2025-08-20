# Reddit Model Transition Complaint Labeling Guidelines

Version: 0.1 (2025-08-20)
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
- Pilot batch: 80 comments, dual-labeled.
- Calculate Cohen’s κ for WARMTH_LOSS, HELPFULNESS_REGRESSION, CREATIVITY_DROP, HEDGING_SHIFT (target ≥0.70). Refine unclear definitions.
- Drift check: every 200 labels, re-label 20 previously labeled comments to monitor consistency.

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
