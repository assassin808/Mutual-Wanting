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
