# Synthetic Annotation Examples (Training)

These are fabricated examples to calibrate labeling decisions—do not treat as real Reddit quotes.

| Body (Paraphrased) | Primary Tag | Secondary Flags |
|--------------------|-------------|-----------------|
| "It used to chat like a friendly partner; now every reply is sterile." | WARMTH_LOSS | NOSTALGIA; ANTHRO_LANG |
| "Stories feel formulaic compared to before—structure repeats." | CREATIVITY_DROP | NOSTALGIA |
| "Keeps asserting facts confidently but two were wrong when I checked." | HELPFULNESS_REGRESSION | UNDER-HEDGING (ignore, captured in main) |
| "Now it constantly says it *might* be mistaken even on basics." | HEDGING_SHIFT |  |
| "Refuses to help with harmless code examples I asked last month." | SAFETY_REFUSAL_SHIFT | NOSTALGIA |
| "Loses context after a couple exchanges—forgetting prior constraints." | MEMORY_CONTINUITY |  |
| "Answers are just one short sentence now—need to prod for details." | VERBOSITY_CHANGE |  |
| "Everything is slower; spinning indicator for seconds each turn." | LATENCY_SPEED |  |
| "I keep hitting rate limits before finishing my outline." | ACCESS_LIMITS |  |
| "Colder, yes, but accuracy is actually better overall." | HELPFULNESS_REGRESSION | POSITIVE_COUNTER; WARMTH_LOSS (secondary tone) |
| "Honestly 5 is just smarter—math finally works." | UPGRADE_BENEFIT |  |
