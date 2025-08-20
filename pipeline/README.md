# Minimal Pipeline Overview

Goal: Lightweight extraction, sampling, labeling, and analysis of Reddit complaints across GPT model transitions.

## Pipeline Steps
1. Fetch: Collect comments for defined pre/post windows per transition.
2. Sample: Stratify by engagement (score buckets) and pre/post.
3. Label: Human annotation using `labeling_guidelines.md`.
4. Features: Compute user style features (length, hedge density, pronoun types, imperative ratio, warmth markers).
5. Analysis: Proportion shifts, logistic models with interaction (transition * pre_post + user_cluster).

## Directory Layout
```
pipeline/
  labeling_guidelines.md
  README.md
  fetch_reddit.py          # placeholder
  sample_for_labeling.py   # placeholder
  features_and_analysis.py # placeholder
  util_text.py             # placeholder helper functions
  data/                    # raw and processed JSONL/CSV (gitignored recommended)
```

## Transitions & Windows (Tentative)
| Transition | Pre Window | Post Window |
|------------|-----------:|------------:|
| 3.5→4 | -14d to -1d | +0d to +28d |
| 4→4o  | -14d to -1d | +0d to +28d |
| 4o→5  | -14d to -1d | +0d to +28d |

Adjust if volume too large; we can subsample chronologically.

## Target Counts
~300 labeled comments pre + 300 post per transition → ~1,800. If time constrained, reduce to 200/200 (1,200 total).

## User Style Feature Sketch
- token_len, avg_sentence_len
- hedge_rate (list: maybe,could,perhaps,might,seems,appears,possibly)
- warmth_markers (thank, please, appreciate, love, enjoy)
- imperative_ratio (imperative verbs / verbs total heuristic)
- pronoun_personal_ratio (I,we,you occurrences / tokens)

## Statistical Models
Logistic regression for each complaint primary tag (one-vs-rest):
```
logit(tag ~ transition + pre_post + transition:pre_post + user_style_cluster + score_bucket)
```
Cluster: k-means (k=5) over standardized features.

## Outputs
- proportions_shift.csv
- regression_results.json
- cooccurrence_network.gml
- style_cluster_centroids.csv

## Dependencies
Install optional analysis libraries (skip if only preparing raw labels):

```
pip install -r pipeline/requirements.txt
```

## Quick Mock Run (Synthetic)
```
python pipeline/fetch_reddit.py --out pipeline/data/mock_raw.jsonl --limit 120
python pipeline/sample_for_labeling.py --raw pipeline/data/mock_raw.jsonl --out pipeline/data/sample_labels.csv --n 60
python pipeline/features_and_analysis.py --labeled pipeline/data/sample_labels.csv --out pipeline/data/summary.json
```
(You will need to manually fill primary_tag values in the CSV to see meaningful analysis.)

## Annotation Aids
See `pipeline/labeling_guidelines.md` and `pipeline/annotation_examples.md` for calibration.

## Next Actions
- Implement fetch script with simple Reddit API or pushshift fallback (if accessible).
- Create sampling script, produce pilot batch.
- Update guidelines after pilot reliability.

## Environment Variables (Reddit API)
Set locally (do NOT commit secrets):
```
export REDDIT_CLIENT_ID="<your_client_id>"
export REDDIT_CLIENT_SECRET="<your_client_secret>"
export REDDIT_USER_AGENT="PersonaDriftStudy/0.1 by Yang"
# Optional (script auth if needed)
export REDDIT_USERNAME="<reddit_username>"
export REDDIT_PASSWORD="<reddit_password>"
```
Fetching will gracefully fall back to synthetic data if these are missing.

## Subreddit Configuration
Create a simple text file `pipeline/subreddits.txt` listing one subreddit per line (e.g., `ChatGPT`, `OpenAI`, `ArtificialInteligence`). The fetch script will read it if present.

## Release Dates Configuration
Adjust `RELEASES` dict in `fetch_reddit.py` once exact GPT-5 public date is confirmed.
