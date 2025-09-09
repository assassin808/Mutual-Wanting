# Fig1: Pipeline schematic (Mermaid)

```mermaid
flowchart LR
  A[Historical Dumps] -->|integrity, normalize| B[Unified JSONL]
  A2[Live Supplement (Pilot Only)] -->|tag provenance| B
  B --> C[Hygiene: dedupe + near-dup + sensitive log]
  C --> D[Sampling: enriched + baseline]
  D --> E[Pilot Annotation A/B (overlap)]
  E --> F[Agreement + Disagreement + Guidelines v0.x]
  F --> G[Scale Annotation + Consensus]
  G --> H[Features]
  H --> I[Drift (log-odds + bootstrap)]
  H --> J[Regression (interaction ORs)]
  H --> K[Probes (behavioral metrics)]
  I --> L[Lexical–Theme Coupling]
  J --> L
  K --> L
  L --> M[Tables & Figures]
  M --> N[Writing & QA]
  N --> O[Submission]
```
