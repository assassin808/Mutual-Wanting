# Mutual Wanting in Human-AI Interaction

**Empirical Evidence from Large-Scale Analysis of GPT Model Transitions**

A research project investigating bidirectional expectations between users and AI systems during major model transitions, with practical applications for building more trustworthy and relationally-aware AI systems.

## 🎯 Quick Start

### Repository Usage

1. **Setup Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Run Complete Analysis Pipeline**
   ```bash
   python experiments/run_all_experiments.py
   ```

3. **Generate Paper Results**
   ```bash
   # Results will be in pipeline/outputs/
   # - experiment_1_reddit_drift.csv
   # - experiment_2_probe_results.json
   # - experiment_3_reliability.json
   # - paper_tables.tex (ready for LaTeX inclusion)
   ```

4. **Compile Paper**
   ```bash
   cd paper/
   pdflatex mutual_wanting_paper_v1.tex
   bibtex mutual_wanting_paper_v1
   pdflatex mutual_wanting_paper_v1.tex
   pdflatex mutual_wanting_paper_v1.tex
   ```

### Directory Structure

```
├── README.md                   # This file - usage guidance and research archive
├── experiments/               # 3 focused experiments for paper validation
│   ├── experiment_1_reddit_analysis.py    # Reddit discourse analysis
│   ├── experiment_2_probe_comparison.py   # API probe behavioral comparison
│   ├── experiment_3_reliability_analysis.py # Inter-annotator reliability
│   └── run_all_experiments.py             # Execute all experiments
├── pipeline/                  # Data processing and analysis pipeline
│   ├── fetch_reddit.py       # Reddit data collection
│   ├── features_and_analysis.py # Feature extraction and analysis
│   ├── response_analyzer.py  # API response analysis
│   └── outputs/              # Generated results and tables
├── paper/                    # Final manuscript and submission materials
│   ├── mutual_wanting_paper_v1.tex # Main paper (ready for submission)
│   ├── mutual_wanting_paper_v1.pdf # Compiled PDF
│   └── references.bib        # Bibliography
├── analysis_output/          # Visualizations and analysis results
└── literature_summaries/     # Related work summaries
```

## 📊 Key Findings

Our analysis of 22,411 Reddit comments and 729 controlled API responses reveals:

- **48.65%** of users employ anthropomorphic language when discussing AI systems
- **11.9:1** trust-to-betrayal language ratio, indicating generally positive but fragile relationships
- **11 distinct user types** based on mutual wanting patterns
- **Measurable expectation violations** clustered around model update periods
- **Significant persona changes** across GPT model transitions (35% warmth reduction, 64% efficiency gain)

## 🔬 Research Methodology

### Dual-Source Approach

1. **Reddit Discourse Analysis**: Large-scale analysis of authentic user responses to model transitions
2. **Controlled API Probing**: Standardized tests across multiple model versions to measure behavioral changes

### Key Innovations

- **47-dimensional feature extraction** targeting bidirectional desires
- **Dual-algorithm topic modeling** (LDA + NMF) for robust theme identification
- **Custom lexicons** for anthropomorphism, trust dynamics, and expectation violations
- **Mutual Wanting Alignment Framework (M-WAF)** for systematic analysis

## 📚 Research Archive

### Project Evolution

This research emerged from observations of user reactions to GPT model transitions, particularly the intense relational responses that resembled interpersonal relationship dynamics rather than typical software feedback. The project evolved through several phases:

1. **Initial Observation Phase** (2024): Noticed patterns in user complaints about AI "personality changes"
2. **Theoretical Development** (Early 2025): Developed "mutual wanting" framework to explain bidirectional expectations
3. **Empirical Validation** (Mid 2025): Large-scale data collection and analysis
4. **Paper Completion** (September 2025): Final manuscript for Agents4Science 2025 conference

### Core Theoretical Framework

**Mutual Wanting**: The bidirectional expectation dynamics where users have desires for AI systems (reliability, warmth, intelligence, creativity, honesty, helpfulness, responsiveness) while AI systems, through their design optimization, implicitly "want" certain user behaviors (clarity, structure, efficiency, feedback, boundaries, patience).

### Experimental Design Philosophy

- **Minimal-Resource Approach**: No proprietary data or expensive compute required
- **Reproducible Methods**: All code and processing transparent
- **Focused Experiments**: Each test validates exactly one core claim
- **Sufficient Evidence**: Meets methodological requirements for publication

### Validation Results

- **Inter-annotator reliability**: Cohen's Kappa = 0.762 (Substantial agreement)
- **Statistical significance**: Multiple findings with p < 0.05
- **Effect sizes**: Substantial changes detected across multiple dimensions
- **Methodology gate**: Exceeds κ > 0.65 threshold for publication

### Related Work Integration

The research builds on foundational work in:
- **Anthropomorphism in AI** (Epley & Waytz, 2010)
- **Parasocial relationships** (Horton & Wohl, 1956)
- **Trust in automation** (Lee & See, 2004)
- **AI transparency** (Amershi et al., 2019)
- **Human-AI alignment** (Kirk et al., 2025)

### Conference Context

**Agents4Science 2025**: A conference emphasizing AI as primary author and reviewer, with transparency as a core value. Our project exemplifies reproducible, low-cost alignment observability, directly addressing the conference's focus on computational human-AI interaction.

## 🔧 Technical Implementation

### Requirements

- Python 3.8+
- Standard NLP libraries (spaCy, NLTK, scikit-learn)
- Statistical packages (pandas, numpy, scipy)
- Visualization tools (matplotlib, seaborn)

### API Keys Needed

Create `.env` file with:
```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
OPENAI_API_KEY=your_openai_api_key
```

### Data Sources

- **Reddit**: r/ChatGPT, r/artificial, r/MachineLearning, r/singularity
- **API Probing**: 9 OpenAI models across 81 standardized scenarios
- **Time Period**: November 2024 - January 2025 (GPT-5 release period)

## 📈 Results and Impact

### Academic Contributions

1. **First large-scale empirical validation** of bidirectional desire dynamics in human-AI interaction
2. **Novel clustering discovery** of 11 distinct user types based on mutual wanting patterns
3. **Methodological innovation** in combining discourse analysis with controlled behavioral probing
4. **Practical framework** for expectation violation detection and trust monitoring

### Practical Applications

- **Early warning systems** for user dissatisfaction during model transitions
- **Personalized interaction strategies** based on user type identification
- **Trust calibration monitoring** for AI system deployment
- **Anthropomorphism-aware design** principles for conversational AI

## 📝 Citation

```bibtex
@article{mutual_wanting_2025,
  title={Mutual Wanting in Human--AI Interaction: Empirical Evidence from Large-Scale Analysis of GPT Model Transitions},
  author={Anonymous Authors},
  journal={Agents4Science 2025},
  year={2025},
  note={Under Review}
}
```

## 📄 License

This research is released under CC BY 4.0 license for maximum reproducibility and impact.

## 🤝 Contributing

This research emphasizes transparency and reproducibility. The complete methodology, code, and results are available for verification and extension by the research community.

---

**Status**: Paper submitted to Agents4Science 2025 (September 2025)  
**Contact**: Available through conference submission system during review period
