# Mutual Wanting in Human-AI Interaction

**Empirical Evidence from Large-Scale Analysis of GPT Model Transitions**

A research project investigating bidirectional expectations between users and AI systems during major model transitions, with practical applications for building more trustworthy and relationally-aware AI systems.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone <repository-url>
cd AI-researcher

# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file in root directory:
```bash
# Reddit API (for discourse analysis)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=mutual_wanting_research_bot/1.0

# OpenRouter API (for model comparison)
OPEN_ROUTER_API_KEY=your_openrouter_api_key
```

### 3. Collect Real Data
```bash
# Full data collection pipeline
python collect_data.py

# Or collect individually:
python run_api_collection.py  # API probe data only
python pipeline/reddit_collector.py  # Reddit data only
```

### 4. Generate Paper Results
```bash
# Run all experiments (generates tables and figures)
python experiments/run_all_experiments.py

# Compile final paper
cd paper/
pdflatex mutual_wanting_paper_v1.tex
bibtex mutual_wanting_paper_v1
pdflatex mutual_wanting_paper_v1.tex
```

## 📁 Repository Structure

```
AI-researcher/
├── README.md                    # This file - quick start guide
├── RESEARCH_ARCHIVE.md          # Research background and evolution
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
│
├── collect_data.py             # Main data collection orchestrator
├── run_api_collection.py       # API-only collection script
├── run_api_probes.py           # Comprehensive API probing
├── explore_reddit.py           # Reddit exploration utility
│
├── pipeline/                   # Core data processing pipeline
│   ├── collect_data.py         # Data collection coordinator
│   ├── reddit_collector.py     # Reddit API integration
│   ├── openrouter_client.py    # OpenRouter API integration  
│   ├── response_analyzer.py    # Behavioral metrics extraction
│   └── data/                   # Collected datasets
│       ├── reddit_comments_all.csv
│       ├── api_probe_results_raw.json
│       └── probe_analysis_complete.json
│
├── experiments/                # Minimal experiments for validation
│   ├── experiment_1_reddit_analysis.py     # Reddit discourse analysis
│   ├── experiment_2_probe_comparison.py    # API probe comparison
│   ├── experiment_3_reliability_analysis.py # Inter-annotator reliability
│   └── run_all_experiments.py              # Execute all experiments
│
├── paper/                      # Final manuscript
│   ├── mutual_wanting_paper_v1.tex         # Main paper
│   ├── mutual_wanting_paper_v1.pdf         # Compiled PDF
│   ├── references.bib                      # Bibliography
│   └── agents4science_2025.sty             # Conference style
│
├── analysis_output/            # Generated visualizations and results
│   ├── visualizations/         # Figures and charts
│   └── system-fig/             # System overview diagrams
│
└── literature_summaries/       # Related work documentation
    ├── amershi2019guidelines.md
    ├── epley2007seeing.md
    └── [other literature summaries]
```

## 🎯 Core Workflow & Research Process

### Research Methodology Overview
Our systematic 5-phase approach demonstrates reproducible, low-cost alignment observability:

1. **🔍 Observation & Theory Development**: Identified relationship-like responses to AI model changes
2. **📊 Data Collection Strategy**: Designed dual-source methodology (Reddit + API probes)  
3. **⚡ Empirical Data Gathering**: Collected 22,411 comments + 729 controlled responses
4. **🔬 Multi-Dimensional Analysis**: 47-dimensional feature extraction and clustering
5. **✅ Validation & Documentation**: Statistical validation (κ=0.762) and reproducibility package

*See `experiments/README.md` for complete process documentation*

### Data Collection
1. **Reddit Analysis**: Collect user discourse from 29 AI-related subreddits
2. **API Probing**: Test 5 OpenAI models with standardized behavioral probes
3. **Validation**: Ensure data quality meets publication standards

### Analysis Pipeline
1. **Feature Extraction**: 47-dimensional analysis of mutual wanting patterns
2. **Clustering**: Identify distinct user types (11 clusters discovered)
3. **Statistical Testing**: Validate findings with appropriate significance tests

### Results Generation
- **48.65%** anthropomorphism rate in user discourse
- **11.9:1** trust-to-betrayal language ratio
- **11 distinct user types** based on mutual wanting patterns
- **Measurable expectation violations** during model transitions

## 📊 Key Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `collect_data.py` | Complete data collection | Before running any experiments |
| `run_api_collection.py` | API probes only | When Reddit data exists |
| `pipeline/reddit_collector.py` | Reddit data only | When API data exists |
| `experiments/run_all_experiments.py` | Generate all results | After data collection |
| `explore_reddit.py` | Debug Reddit issues | When Reddit collection fails |

## ⚙️ Configuration

### Data Collection Settings
- **Reddit subreddits**: 29 AI-related communities (9.9M to 62K members)
- **Time period**: Pre/Post GPT-5 release (Dec 2024)
- **API models**: GPT-5, GPT-4o, GPT-4-turbo, GPT-3.5-turbo, O3
- **Probe suite**: 6 standardized behavioral tests per model

### Quality Thresholds
- Minimum 20 comments per time period
- 80%+ API probe success rate
- Relevance filtering (AI mentions + persona keywords)
- Substantial content (5+ words per comment)

## 🔧 Troubleshooting

### Common Issues

**Reddit API returns 0 results:**
```bash
python explore_reddit.py  # Debug Reddit access
```

**API probe failures:**
```bash
# Check API key in .env
# Verify OpenRouter model availability
python run_api_collection.py  # Test API access
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
# For NLTK data:
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Data Validation
The pipeline automatically validates:
- Both pre/post Reddit files exist with sufficient data
- API probe files exist with high success rates
- All required behavioral metrics are computed
- Data quality meets publication standards

## 📈 Expected Outputs

After successful data collection and analysis:
- `pipeline/data/reddit_comments_all.csv` - Complete Reddit dataset
- `pipeline/data/api_probe_results_raw.json` - Raw API responses
- `pipeline/data/probe_analysis_complete.json` - Behavioral metrics
- `experiments/outputs/paper_tables.tex` - LaTeX tables for paper
- `paper/mutual_wanting_paper_v1.pdf` - Complete manuscript

## 🏆 Research Impact

This work provides the first large-scale empirical validation of bidirectional desire dynamics in human-AI interaction, with practical applications for:
- Early warning systems for user dissatisfaction
- Personalized interaction strategies based on user types
- Trust calibration monitoring for AI deployments
- Anthropomorphism-aware design principles

## � Contact

For technical issues or research questions, please open an issue in this repository.

**Status**: Paper submitted to Agents4Science 2025 (September 2025)
