# Project Progress Log

Date: 2025-08-21

## New Actions This Session
- Added automatic `.env` loader to `fetch_reddit.py` (loads credentials if not exported).
- Integrated environment variable documentation previously; now operational without manual export if `.env` present.
- Ready for first live fetch run (use `--live`).

## Current Pipeline Integrity
Components present: fetch (with live + synthetic), sampling (stratified), labeling guidelines + examples, feature extraction, regression scaffold.

## Immediate Next Targets
1. Execute live fetch (limit 300–500) across configured subreddits.
2. Generate first stratified sample CSV for pilot labeling (n=200) and compute feature summary.
3. After labeling pilot: run regression scaffold (install dependencies) and record preliminary proportions.

## Risks / Notes
- Release date for GPT-5 still placeholder; adjust before final analyses.
- Need subreddit list file `pipeline/subreddits.txt` for domain coverage.

## Pending Decisions
- Final label count (1,800 vs 1,200) based on annotation throughput.
- Whether to include any additional social platforms (currently none planned to stay minimal).

## Added Subreddit List
Created `pipeline/subreddits.txt` with tiered groups:
- Core: ChatGPT, OpenAI, GPT3, GPT4
- Prompt/usage: PromptEngineering, AIprompting
- General AI: ArtificialIntelligence, singularity
- Practitioner: LanguageTechnology, MachineLearning, LocalLLaMA
- Safety: AISafety
- Additional hubs: AIPromptHub, AIChat

Rationale: capture high-salience complaint sources (core + prompt) plus contrast/control domains (practitioner, safety) and open-weight community (LocalLLaMA) for differential framing of persona drift vs capability.

## Next Action
Run first live fetch (limit 500) and inspect class balance across transitions; adjust keyword filter later if general subs yield excessive noise.

-- End of entry --

## Session Update (Subsequent)
- Enhanced `fetch_reddit.py` with subreddit-level exception handling and early abort safety.
- Fixed serialization (subreddit object) by coercing to display name.
- Successful live fetch (120 rows) despite 403 on some subs (e.g., GPT4) -> stored at `pipeline/data/live_raw.jsonl`.
- Created first stratified sample (`pipeline/data/label_batch1.csv`, n=60) for pilot labeling.
- Extended `features_and_analysis.py` with `--raw` mode; produced preliminary summary (`feature_summary.json`).

### Immediate Next Steps
1. Increase fetch volume (iterate higher limits; consider time-bounded queries) to obtain pre/post diversity (currently only future-post window due to placeholder release date interpreting current timestamps as post-transition).
2. Commence manual labeling on `label_batch1.csv`; save annotated copy and compute inter-annotator agreement if multiple raters.
3. Add bot / moderation filter heuristic (e.g., remove bodies matching auto-mod patterns) before next sampling.
4. Insert preliminary descriptive stats into manuscript (`agents4science_2025.tex`).
5. Replace GPT-5 placeholder release date with actual (or shift placeholder forward to avoid all data marked post).

### Notes
- Need historical retrieval method (Pushshift successor / monthly dumps) for genuine pre windows; current API only yields recent posts.
- Consider adding a keyword filter (e.g., complaints terms list) to enrich target density for labeling efficiency.

### Session Continuation Addendum
- Implemented keyword/length/bot filtering in fetch script; created `pipeline/keywords.txt`.
- Filtered fetch run: 400 raw -> 23 retained complaint-relevant rows (high precision, low recall) all tagged post (placeholder release date issue persists).
- Added JSON summary output for distribution auditing.
- Next: adjust release dates or backfill historical to achieve pre samples; consider relaxing min length or expanding limit for better retention.
- Added minimal CLI `annotation_tool.py` for in-terminal labeling; smoke test generated `_annotated` CSV.
- Generated provisional pre/post descriptive stats combining filtered passes (32 pre, 23 post). Early lexeme frequencies: 'worse' dominant; latency & memory co-occur; high-score complaints sparse.
