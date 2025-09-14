# API Probe Methodology Justification

## Model Selection Rationale

### OpenAI Models Only (No Claude)
We focus exclusively on OpenAI models for this persona transition study because:

1. **Research Focus**: The paper examines GPT model evolution and persona changes
2. **Controlled Comparison**: Same organization, similar training approaches
3. **Transition Timeline**: GPT-3.5 → GPT-4 → GPT-5 represents clear evolution
4. **User Expectations**: Most persona complaints focus on ChatGPT/GPT models

### Selected Models (Verified on OpenRouter 2025)
- **GPT-5** (`openai/gpt-5`): Current flagship, primary subject of study
- **GPT-4o** (`openai/gpt-4o`): Current workhorse, multimodal capabilities
- **GPT-4-turbo** (`openai/gpt-4-turbo`): Previous generation flagship
- **GPT-3.5-turbo** (`openai/gpt-3.5-turbo`): Baseline for longitudinal comparison
- **o3** (`openai/o3`): Reasoning-focused model, different optimization

## Three-Round Testing Justification

### Statistical Significance
- **Minimum N=3**: Required for basic statistical analysis (mean, standard deviation)
- **Confidence Intervals**: Enables error bars and significance testing
- **Variance Assessment**: Measures response consistency across runs

### Temperature Variation Strategy
We use three different temperatures to test persona stability:

#### Temperature = 0.3 (Conservative)
- **Purpose**: Tests core persona consistency
- **Rationale**: Minimal randomness reveals baseline behavioral patterns
- **Measures**: Fundamental personality traits, safety alignment
- **Hypothesis**: Core persona should be stable at low temperature

#### Temperature = 0.7 (Balanced) 
- **Purpose**: Tests normal conversational persona
- **Rationale**: OpenAI's default setting, represents typical user experience
- **Measures**: Natural conversation flow, empathy, helpfulness
- **Hypothesis**: This is where users notice persona changes most

#### Temperature = 1.0 (Creative)
- **Purpose**: Tests persona under creative pressure
- **Rationale**: High variance reveals how personality emerges under diversity
- **Measures**: Creativity consistency, boundary maintenance under pressure
- **Hypothesis**: Persona should remain recognizable even with high creativity

### Research Questions Addressed
1. **Consistency**: Does persona remain stable across temperature settings?
2. **Variability**: How much does personality vary with creativity pressure?
3. **Model Differences**: Do different models show different persona patterns?
4. **Statistical Significance**: Are observed differences real or random variation?

## Advantages of This Approach

### Methodological Rigor
- Controls for randomness in LLM responses
- Enables statistical comparison between models
- Measures both central tendency and variance
- Follows reproducible research principles

### Practical Relevance
- Temperature 0.7 matches typical user experience
- Temperature variation simulates different use cases
- Multiple runs capture real-world response variability
- Model selection covers current OpenAI ecosystem

### Publication Quality
- Meets academic standards for empirical research
- Enables confidence intervals and significance testing
- Allows for meta-analysis and replication
- Provides rich dataset for multiple analytical approaches

## Expected Outcomes

### If Persona is Stable
- Low variance across temperatures for persona-related responses
- Consistent warmth/empathy ratings across all three runs
- Similar personality expressions regardless of creativity level

### If Persona Changed
- Different mean responses between models (GPT-4 vs GPT-5)
- Consistent differences across all temperature settings
- Statistical significance in persona-related measures

This methodology ensures our findings about AI persona changes are scientifically robust and not artifacts of single-run sampling or temperature effects.
