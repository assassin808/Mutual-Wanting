# Real Data Collection Pipeline

This pipeline collects **actual data** for publication-quality research using real APIs.

## 🎯 Data Sources

### Reddit Data Collection
- **Target:** 29 AI-related subreddits (9.9M+ to 62K+ members)
- **Focus:** GPT-5 release discussions, personality changes, user complaints
- **Time Period:** Pre/Post GPT-5 release (December 2024)
- **Search Terms:** 41 targeted queries including "GPT-5", "personality change", etc.

### API Probe Collection  
- **Models Tested:** GPT-5, GPT-4o, GPT-4-turbo, GPT-3.5-turbo, O3
- **Platform:** OpenRouter API for consistent access
- **Metrics:** CDR, SUR, warmth ratio, empathy score, creativity score
- **Probes:** 6 standardized behavioral tests per model

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API credentials in .env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret  
OPEN_ROUTER_API_KEY=your_openrouter_key
```

### Data Collection
```bash
# Collect all real data
python collect_data.py

# Or collect individually:
python pipeline/reddit_collector.py
python pipeline/openrouter_client.py
```

## 📊 Generated Files

### Reddit Data
- `gpt5_release_chatgpt_pre.jsonl` - Pre-GPT-5 user discussions
- `gpt5_release_chatgpt_post.jsonl` - Post-GPT-5 user discussions  
- `reddit_comments_all.csv` - Combined dataset for analysis

### API Probe Data
- `api_probe_results_raw.json` - Raw API responses
- `probe_analysis_complete.json` - Behavioral metrics analysis
- `api_probe_summary.json` - Model comparison summary

## 🎯 Target Subreddits (29 total)

### Primary OpenAI Communities
- r/ChatGPT (9.9M) - Main community
- r/OpenAI (2.3M) - Official discussions  
- r/ChatGPTPro (390K) - Professional usage
- r/GPT3 (589K) - Model discussions

### Major AI Communities  
- r/artificial (1.1M) - General AI
- r/ArtificialInteligence (1.4M) - Trending AI
- r/MachineLearning (2.8M) - Technical ML
- r/singularity (1.5M) - AGI discussions

### Model-Specific Communities
- r/ClaudeAI, r/GoogleGeminiAI, r/LocalLLaMA, r/MistralAI

### Specialized Communities
- r/AIPromptProgramming, r/PromptEngineering, r/ChatGPTCoding
- r/AutoGPT, r/AI_Agents, r/aiwars, r/AIethics

## 🔍 Search Strategy

### GPT-5 Focused Queries
- "GPT-5", "GPT5", "GPT-5 release", "GPT-5 personality"
- "GPT-5 vs GPT-4", "GPT-5 behavior", "GPT-5 announcement"

### Persona Change Detection
- "personality change", "behavior change", "AI personality"
- "AI cold", "AI warm", "AI robotic", "lost personality"
- "lobotomized", "dumbed down", "more human", "less human"

### Model Transition Discussions
- "GPT-4 retirement", "GPT-4o update", "model comparison"
- "ChatGPT changed", "ChatGPT different", "AI got worse"

## 📈 Data Quality Validation

The pipeline includes automatic validation:
- ✅ Minimum 20 comments per time period
- ✅ 80%+ API probe success rate  
- ✅ Relevance filtering (AI mentions + persona keywords)
- ✅ Substantial content (10+ words per comment)

## 🔧 Rate Limiting & Ethics

- **Reddit API:** 2-second delays between subreddits
- **OpenRouter API:** 2-second delays between probes
- **Content Filtering:** Only public discussions, no personal data
- **Anonymization:** User handles preserved but no tracking

## 📋 Output Validation

Before running experiments, the pipeline validates:
1. Both pre/post Reddit files exist with sufficient data
2. API probe files exist with high success rates  
3. All required behavioral metrics are computed
4. Data quality meets publication standards

**Ready for publication!** ✅
