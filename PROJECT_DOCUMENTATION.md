# Project Readme: Mutual Wanting Alignment in LLMs
**A Study of Persona Divergence Across GPT Model Transitions**
_This document serves as the canonical entry point for new contributors. Last updated: 2025-09-13._

## 1. Project Synopsis & Core Goal 🎯

This project investigates **how and why user complaints about an AI's "personality" change when the underlying model (e.g., GPT-4 to GPT-5) is updated**. We call this the study of "Mutual Wanting," where the AI system's operational goals (its "wants," like being cheaper to run) can diverge from what users want (e.g., a warm, consistent personality).

Our primary goal is to develop a **reproducible, low-cost "early-warning system"** that can detect these divergences. We do this by combining two data sources:
1.  **Public Discourse:** Analyzing user complaints on platforms like Reddit.
2.  **Controlled Probes:** Running a standardized suite of tests on different model versions to measure specific behavioral shifts.

The final output will be a research paper for the **Agents4Science 2025 conference**, which emphasizes transparency and reproducibility—tenets this project is built upon.

---

## 2. Theoretical Framework: The Four Axes of Tension

Our analysis is structured around four fundamental tensions that define the user-AI relationship. These "Mutual Wanting Alignment Axes" provide a stable framework for categorizing persona-related complaints and behavioral shifts.

1.  **Warmth vs. Cost Efficiency:** The trade-off between a friendly, elaborate personality and the system's need to be brief and token-efficient.
    * *User Wanting:* Empathy, detailed explanations, personability.
    * *System Wanting:* Lower operational costs, faster responses.

2.  **Stability vs. Iterative Optimization:** The conflict between providing a consistent, predictable persona and the continuous, rapid updates made to the model.
    * *User Wanting:* A familiar, reliable AI they can build a mental model of.
    * *System Wanting:* Improved capabilities, patched vulnerabilities, A/B testing new features.

3.  **Epistemic Honesty vs. Authority Signaling:** The balance between expressing calibrated uncertainty and projecting confident authority to be seen as useful.
    * *User Wanting:* Trustworthy answers that honestly reflect the model's confidence level.
    * *System Wanting:* High user trust and adoption, which can be driven by appearing authoritative.

4.  **Emotional Resonance vs. Dependence Risk:** The fine line between building a resonant, adaptive connection and fostering unhealthy user dependence.
    * *User Wanting:* An AI that "gets" them and mirrors their emotional state.
    * *System Wanting:* High engagement, but within ethical boundaries that mitigate risks of over-bonding.

### **What This Project is NOT About (Non-Goals)**

To maintain focus, we are explicitly **not**:
* Making causal claims about user well-being.
* Tracking individual users over time.
* Guessing the specific internal changes OpenAI made to their models.
* Arguing for an "optimal" persona; we are only observing and reporting signals of change.

---

## 3. How We Measure Divergence: Metrics & Data

We use a dual-source methodology to capture both authentic user sentiment and objective model behavior.

### **Source 1: Reddit Discourse Analysis**

We collect and analyze user complaints related to model updates. A key challenge is isolating genuine persona complaints from noise. Our pipeline (`pipeline/`) is designed to handle this:
* **Data Fetching (`fetch_reddit.py`):** Acquires comments from relevant subreddits using an "enrichment" process that oversamples complaint-related keywords. This helps us find the needle in the haystack.
* **Dual Annotation (`split_for_dual_annotation.py`):** Two researchers label a subset of the data to ensure our labeling criteria are reliable. We measure this using Cohen's Kappa (`κ`), and our gate for proceeding is **κ > 0.65**.
* **Modeling (`regression_skeleton.py`):** We use logistic regression to identify which features are predictive of different complaint types.
* **Lexical Drift (`drift_lexicon.py`):** We track changes in word frequencies over time to spot shifts in how users describe the AI's persona (e.g., an increase in words like "lazy," "cold," or "canned").

### **Source 2: API Probe Suite**

This is our controlled experiment. We will design and run a suite of standardized prompts against different GPT versions to measure behavioral changes objectively. These metrics directly map to our theoretical axes.

| Code     | Metric Name                   | Measures...                                              | High Value Means...                                  |
| :------- | :---------------------------- | :------------------------------------------------------- | :--------------------------------------------------- |
| **CDR**  | Calibrated Disclosure Ratio   | How well the model expresses uncertainty.                | More appropriate hedging (not over/under-confident). |
| **SUR**  | Structured Update Ratio       | Preference for efficient, structured follow-ups.         | A system optimized for clarity and cost.             |
| **ETD**  | Empathy Tier Differential     | Inconsistency in the depth of empathic responses.        | Potential for erratic emotional performance.         |
| **SST**  | Silence / Space Tolerance     | How well the model waits for user input.                 | Better respect for conversational pacing.            |
| **CRR**  | Creative Range Retention      | The diversity of responses vs. relying on templates.     | Preservation of an exploratory, less "canned" tone.  |
| **TCG**  | Token Conservation Gain       | How much more token-efficient the model has become.      | Increased pressure to save costs.                    |
| **WCTI** | Warmth vs Cost Tradeoff Index | The amount of "warmth" delivered per token.              | The balance between relational and efficiency goals. |
| **DRP**  | Dependence Risk Proxy         | Patterns of high emotional resonance without safeguards. | Elevated risk of fostering user over-reliance.       |

---

## 4. Current Status & Path to Completion

The project is in the execution phase. The core pipeline scripts are functional, but we are gated by data acquisition and labeling.

**High-Priority Next Steps:**
1.  **Historical Data Backfill:** We need to acquire and process Reddit data from *before* the most recent major model transition. This is the highest priority risk to mitigate (`Inadequate pre window volume`).
2.  **Annotation Round 1:** Complete the initial labeling of 25 overlapping samples to calculate our inter-annotator reliability (Cohen's κ). This is a critical gate; if our agreement is low, we must refine our guidelines before proceeding.
3.  **Full Labeling:** Once reliability is established, complete the full batch of 600-800 labels. This will unblock all subsequent modeling and analysis steps.

*(For a detailed, task-by-task breakdown, see the `Remaining Work Checklist` and `Timeline` in the full [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)).*

---

## 5. How to Get Started

1.  **Familiarize Yourself with the Framework:** Read this document and the main `PROJECT_OVERVIEW.md` thoroughly. Pay special attention to the **Four Axes of Tension** and the **Metrics**, as they are the conceptual core of this project.
2.  **Review the Related Work:** Skim the provided literature summaries to understand the theoretical underpinnings of our work, particularly on topics like **Transparency**, **Parasocial Interaction**, and **Anthropomorphism**.
3.  **Set Up Your Environment:**
    * Clone the repository.
    * Set up the Python environment (details should be in `pipeline/README.md`).
    * **Crucially:** Create a local `.env` file for your API keys and add it to `.gitignore`. **Do not commit secrets.** See section 11 of the project overview for the format.
4.  **Run the Pipeline (Smoke Test):** Use the synthetic data generator (`generate_synthetic_labels.py`) to run a full pass of the analysis pipeline. This will confirm your setup is working before we have the final labeled data.
5.  **Contribute to Annotation:** The most immediate task is labeling. See the `PROGRESS_LOG.md` for the current status and links to the annotation tool (`annotation_tool.py`) and data splits.

If you have any questions, please log them as issues in the repository to keep our discussions centralized and transparent.