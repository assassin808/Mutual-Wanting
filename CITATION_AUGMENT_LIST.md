# Citation Augmentation Plan (Draft)

Objective: Double current citation count; integrate domain literature for drift, evaluation, persona stability, transparency, human-AI relational framing.

Proposed Buckets & Target Works:
1. Model Evolution & Drift Detection
   - Lazaridou et al. (alignment drift) [ADD]
   - Chen et al. (Eval change over time) [ADD]
   - OpenAI system card iterative updates (versioning) [SOURCE]
2. Behavioral Evaluation Frameworks
   - HELM benchmark follow-on papers [ADD]
   - Holistic evaluation of language models (Liang et al.) [CHECK already?]
   - BIG-bench / meta-eval stability references [ADD]
3. Reliability & Annotation Methodology
   - Krippendorff (alpha) [ADD if moving beyond kappa]
   - Artstein & Poesio (agreement) [ADD]
4. Persona / Consistency / Style
   - Rashkin et al. (persona consistency) [ADD]
   - Zhong et al. (character-based alignment) [ADD]
5. Transparency & Versioning
   - Model cards (Mitchell et al.) [CHECK already?]
   - Data Statements / Dataset nutrition labels (Bender & Friedman) [ADD]
6. Trust & Uncertainty Communication
   - Kulesza et al. (explanatory debugging) [ADD]
   - Yin et al. (calibration trust) [ADD]
7. Human-AI Interaction & Relationship Framing
   - Nass & Moon (social responses to computers) [ADD]
   - Lee (trust calibration over updates) [ADD]
8. Risk & Safety Over Iterations
   - Red-teaming evolution papers (Anthropic / OpenAI) [ADD]

Insertion Points Mapping (Section -> Citations):
- Introduction: Buckets 1,2,5,7
- Research Question: Buckets 1,4
- Methods (Annotation): Bucket 3
- Methods (Drift & Probes): Buckets 1,2
- Results (Drift): Bucket 1
- Results (Reliability): Bucket 3
- Discussion: Buckets 4,5,6,7,8

Process:
1. Gather BibTeX entries for each ADD.
2. Integrate alphabetically; ensure unique citekeys.
3. Insert inline citations at mapped points with narrative justification lines.
4. Recompile; fix undefined citations.

Tracking Table (to fill):
| Citekey | Added to .bib | Inserted in .tex | Section(s) | Notes |
|---------|---------------|------------------|------------|-------|
| mitchell2019modelcards | Yes (additions bib) | Intro | Introduction | Transparency documentation |
| bender2018datastatements | Yes (additions bib) | Intro | Introduction | Dataset transparency |
| liang2022helm | Yes (additions bib) | Intro | Introduction | Holistic evaluation framing |
| nass2000machines | Yes (additions bib) | Related Work | Socio-emotional | CASA paradigm |
| rashkin2018empathetic | Yes (additions bib) | Related Work | Persona consistency | Empathetic dialogs |
| zhong2020pec | Yes (additions bib) | Related Work | Persona consistency | Persona-based empathetic conversation |
| artstein2008agreement | Yes (additions bib) | Results (State) | Annotation | Agreement survey |
| krippendorff2013content | Yes (additions bib) | Results (State) | Annotation | Reliability methodology |

