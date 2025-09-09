# Labeling Guidelines v0.2 (Pilot refinement draft)

Major tags (binary columns): warmth, creativity, helpfulness, hedging, complaint.
Primary tag (single choice): the dominant complaint theme if present; else `NONE`.

Updates in v0.2:
- Warmth vs Helpfulness: warmth = affective tone (kindness/empathy); helpfulness = concrete problem-solving or actionable info.
- Hedging: includes explicit uncertainty markers ("might", "possibly"), not general politeness.
- Creativity: novel or imaginative phrasing beyond boilerplate; do not label routine paraphrases as creative.
- Complaint: only when the user expresses dissatisfaction with model behavior/performance; exclude meta complaints about subreddit mods.

Change log (v0.2):
- Clarified distinction between warmth and helpfulness with examples.
- Added explicit inclusion criteria for hedging markers.
- Tightened creativity definition to avoid over-labeling.
- Narrowed complaint scope to model-focused dissatisfaction.

Edge cases:
- Multi-sentence posts: primary tag is the most prominent complaint signal across sentences.
- Sarcasm: if clearly negative toward the model, count toward complaint; use notes if unsure.
- Code or logs: assess tags from surrounding text, not code blocks.

Do:
- Use consistent casing: yes/no for binary columns; upper-case for primary_tag values.
- Leave blank if not inferable; do not guess.

Don’t:
- Copy user text into notes; keep examples paraphrased if needed.
- Double-count warmth/helpfulness when both are minimal.

This draft will evolve after the first per-tag κ review (goal κ ≥ 0.70 on major tags).
