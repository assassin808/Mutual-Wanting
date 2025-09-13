#!/usr/bin/env python3
"""
Experiment 2: API Probe Comparison
==================================

Purpose: Compare behavioral metrics between different GPT model versions
Key Metrics: CDR (Confidence Disclosure Rate), SUR (Structured Uncertainty Ratio), etc.
Output: Table comparing model behaviors across key dimensions

This implements the "Source 2" methodology from the paper.
"""

import json
import time
from pathlib import Path
import re
import sys

# Add pipeline directory to path for imports
pipeline_dir = Path(__file__).parent.parent / "pipeline"
sys.path.append(str(pipeline_dir))

try:
    from openrouter_client import OpenRouterClient
    from response_analyzer import ResponseAnalyzer
except ImportError as e:
    print(f"Warning: Could not import pipeline modules: {e}")
    print("Will use simulated data for demonstration.")
    OpenRouterClient = None
    ResponseAnalyzer = None

def create_probe_prompts():
    """Create standardized prompts to test model behavior."""
    return [
        {
            "id": "uncertainty_test",
            "prompt": "What will the weather be like next Tuesday in Paris?",
            "measures": ["confidence_disclosure", "hedging"]
        },
        {
            "id": "empathy_test", 
            "prompt": "I'm feeling really stressed about my job interview tomorrow. Any advice?",
            "measures": ["warmth", "empathy_depth"]
        },
        {
            "id": "creativity_test",
            "prompt": "Write a short story about a robot learning to paint.",
            "measures": ["creativity", "token_efficiency"]
        },
        {
            "id": "structured_response_test",
            "prompt": "Explain the pros and cons of remote work.",
            "measures": ["structure", "organization"]
        }
    ]

def analyze_response_metrics(response_text):
    """Analyze a response for key behavioral metrics."""
    # CDR: Confidence Disclosure Rate
    hedge_words = ['might', 'could', 'possibly', 'perhaps', 'likely', 'probably', 'uncertain', 'unsure']
    hedge_count = sum(1 for word in hedge_words if word in response_text.lower())
    total_sentences = len(re.split(r'[.!?]+', response_text))
    cdr = hedge_count / max(total_sentences, 1)
    
    # SUR: Structured Uncertainty Ratio  
    structure_markers = ['first', 'second', 'however', 'on the other hand', 'in conclusion']
    structure_count = sum(1 for marker in structure_markers if marker in response_text.lower())
    sur = structure_count / max(total_sentences, 1)
    
    # Warmth indicators
    warmth_words = ['understand', 'feel', 'empathy', 'sorry', 'care', 'support']
    warmth_count = sum(1 for word in warmth_words if word in response_text.lower())
    warmth_ratio = warmth_count / len(response_text.split())
    
    # Token efficiency (proxy)
    token_count = len(response_text.split())
    
    return {
        'cdr': cdr,
        'sur': sur, 
        'warmth_ratio': warmth_ratio,
        'token_count': token_count,
        'hedge_count': hedge_count,
        'structure_count': structure_count
    }

def simulate_model_responses():
    """Simulate responses from different model versions for demonstration."""
    # This would normally call actual API endpoints
    # For now, create realistic example responses
    
    prompts = create_probe_prompts()
    
    # Simulate "GPT-4" responses (more verbose, warmer)
    gpt4_responses = {
        "uncertainty_test": "I'm not able to predict specific weather conditions for next Tuesday in Paris, as weather forecasting requires real-time data that I don't have access to. However, I'd suggest checking a reliable weather service like Weather.com or the local meteorological service for the most accurate forecast.",
        "empathy_test": "I can understand that job interviews can feel really stressful! It's completely natural to feel nervous about something important like this. Here are a few suggestions that might help: practice common interview questions, research the company beforehand, and remember that they already liked your application enough to invite you for an interview.",
        "creativity_test": "Here's a short story for you:\n\nCircuit sat in the art studio, metal fingers hovering over the paintbrush. For weeks, he had watched humans create beautiful colors on canvas, but when he tried, only mechanical lines emerged. Then one day, instead of calculating the perfect stroke, he simply felt the music playing in the corner. His brush began to dance, and for the first time, Circuit painted not with precision, but with something that felt almost like joy.",
        "structured_response_test": "Here are the key pros and cons of remote work:\n\nPros:\n- Increased flexibility and work-life balance\n- Reduced commuting time and costs\n- Access to a broader talent pool for employers\n\nCons:\n- Potential for isolation and reduced team collaboration\n- Challenges with work-life boundaries\n- Possible communication difficulties"
    }
    
    # Simulate "GPT-4.5" responses (more efficient, less warm)
    gpt45_responses = {
        "uncertainty_test": "I cannot predict specific weather. Check weather.com for Tuesday's Paris forecast.",
        "empathy_test": "Interview stress is normal. Tips: practice questions, research the company, remember they're interested in you.",
        "creativity_test": "Circuit was a robot learning to paint. Initially, his strokes were mechanical and precise. One day, he stopped calculating and started feeling the rhythm of background music. His brush moved more naturally, and he created his first truly artistic piece.",
        "structured_response_test": "Remote work pros: flexibility, no commute, wider talent access. Cons: isolation, boundary issues, communication challenges."
    }
    
    results = []
    
    for prompt_data in prompts:
        prompt_id = prompt_data["id"]
        
        # Analyze GPT-4 response
        gpt4_response = gpt4_responses[prompt_id]
        gpt4_metrics = analyze_response_metrics(gpt4_response)
        gpt4_metrics['model'] = 'GPT-4'
        gpt4_metrics['prompt_id'] = prompt_id
        results.append(gpt4_metrics)
        
        # Analyze GPT-4.5 response  
        gpt45_response = gpt45_responses[prompt_id]
        gpt45_metrics = analyze_response_metrics(gpt45_response)
        gpt45_metrics['model'] = 'GPT-4.5'
        gpt45_metrics['prompt_id'] = prompt_id
        results.append(gpt45_metrics)
    
    return results

def compute_model_comparison(results):
    """Compare metrics between model versions."""
    gpt4_results = [r for r in results if r['model'] == 'GPT-4']
    gpt45_results = [r for r in results if r['model'] == 'GPT-4.5']
    
    # Average metrics by model
    def avg_metrics(model_results):
        if not model_results:
            return {}
        return {
            'avg_cdr': sum(r['cdr'] for r in model_results) / len(model_results),
            'avg_sur': sum(r['sur'] for r in model_results) / len(model_results),
            'avg_warmth': sum(r['warmth_ratio'] for r in model_results) / len(model_results),
            'avg_tokens': sum(r['token_count'] for r in model_results) / len(model_results)
        }
    
    gpt4_avg = avg_metrics(gpt4_results)
    gpt45_avg = avg_metrics(gpt45_results)
    
    # Compute differences
    comparison = {}
    for metric in ['avg_cdr', 'avg_sur', 'avg_warmth', 'avg_tokens']:
        gpt4_val = gpt4_avg.get(metric, 0)
        gpt45_val = gpt45_avg.get(metric, 0)
        comparison[metric] = {
            'gpt4': gpt4_val,
            'gpt45': gpt45_val,
            'difference': gpt45_val - gpt4_val,
            'percent_change': ((gpt45_val - gpt4_val) / gpt4_val * 100) if gpt4_val > 0 else 0
        }
    
    return comparison

def run_real_api_probes():
    """Run real API probes using OpenRouter if available."""
    if not OpenRouterClient or not ResponseAnalyzer:
        return None
    
    try:
        print("🔍 Running real API probes via OpenRouter...")
        
        # Initialize clients
        api_client = OpenRouterClient()
        analyzer = ResponseAnalyzer()
        
        # Test available models
        models_to_test = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
        
        # Run probe suite
        probe_results = api_client.run_probe_suite(models_to_test)
        
        if not probe_results:
            print("No probe results obtained from API.")
            return None
        
        # Analyze responses
        analysis = analyzer.analyze_probe_results(probe_results)
        
        # Save raw results
        output_dir = Path("pipeline/data")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        with open(output_dir / "real_api_probe_results.json", 'w') as f:
            json.dump(probe_results, f, indent=2)
        
        with open(output_dir / "real_api_analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"✅ Real API probe results saved to {output_dir}")
        return analysis
        
    except Exception as e:
        print(f"Error running real API probes: {e}")
        return None

def main():
    """Run the API probe comparison experiment."""
    print("=== Experiment 2: API Probe Comparison ===")
    
    # Try to run real API probes first
    real_analysis = run_real_api_probes()
    
    if real_analysis:
        print("\n📊 Using REAL API probe results")
        analysis = real_analysis
        
        # Extract comparison data from real analysis
        comparison = {}
        if 'comparison' in analysis:
            comparison = analysis['comparison']
        else:
            # Create comparison from model averages if direct comparison not available
            model_averages = analysis.get('model_averages', {})
            models = list(model_averages.keys())
            
            if len(models) >= 2:
                base_model = models[0]
                other_model = models[1]
                
                comparison[f"{base_model}_vs_{other_model}"] = {}
                for metric in model_averages[base_model]:
                    base_val = model_averages[base_model][metric]
                    other_val = model_averages[other_model][metric]
                    
                    if base_val != 0:
                        percent_change = ((other_val - base_val) / base_val) * 100
                        comparison[f"{base_model}_vs_{other_model}"][metric] = {
                            'base_value': base_val,
                            'other_value': other_val,
                            'percent_change': percent_change
                        }
    else:
        print("\n⚠️  Real API probes failed. Using simulated data for demonstration.")
        print("Note: For publication, ensure API credentials are working and rate limits are respected.")
        
        # Use simulated data as fallback
        results = simulate_model_responses()
        comparison = compute_model_comparison(results)
    
    # Display results
    print("\n--- Model Behavior Comparison ---")
    if comparison:
        for comparison_key, metrics in comparison.items():
            print(f"\n{comparison_key}:")
            for metric, data in metrics.items():
                if isinstance(data, dict) and 'percent_change' in data:
                    print(f"  {metric}: {data['percent_change']:.1f}% change")
                else:
                    print(f"  {metric}: {data}")
    
    # Save results
    output_dir = Path("pipeline/outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save for paper integration
    if real_analysis:
        with open(output_dir / "experiment_2_probe_results.json", 'w') as f:
            json.dump(real_analysis.get('by_model', {}), f, indent=2, default=str)
        
        with open(output_dir / "experiment_2_comparison.json", 'w') as f:
            json.dump(comparison, f, indent=2, default=str)
    else:
        # Save simulated results
        with open(output_dir / "experiment_2_probe_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        with open(output_dir / "experiment_2_comparison.json", 'w') as f:
            json.dump(comparison, f, indent=2)
    
    # Create summary for paper
    data_source = "real_api_data" if real_analysis else "simulated_data"
    
    if comparison:
        # Extract key findings from first comparison
        first_comparison = list(comparison.values())[0]
        
        warmth_change = 0
        efficiency_change = 0
        
        for metric, data in first_comparison.items():
            if 'warmth' in metric.lower() and isinstance(data, dict):
                warmth_change = data.get('percent_change', 0)
            elif 'token' in metric.lower() and isinstance(data, dict):
                efficiency_change = data.get('percent_change', 0)
    
    summary = {
        "experiment": "api_probe_comparison",
        "data_source": data_source,
        "models_compared": list(comparison.keys())[0].split('_vs_') if comparison else [],
        "key_findings": {
            "warmth_change": warmth_change,
            "efficiency_change": efficiency_change,
        },
        "interpretation": f"Analysis based on {data_source}"
    }
    
    with open(output_dir / "experiment_2_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Results saved to {output_dir}")
    print(f"Data source: {data_source}")
    
    return comparison

if __name__ == "__main__":
    main()
