#!/usr/bin/env python3
"""
Response Analysis Module
========================

Analyzes API responses to extract behavioral metrics for model comparison.
Implements the metrics described in the paper's theoretical framework.
"""

import re
import json
import numpy as np
from collections import Counter
from pathlib import Path
import nltk
import textstat
from typing import Dict, List, Any

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class ResponseAnalyzer:
    def __init__(self):
        """Initialize response analyzer with keyword dictionaries."""
        self.stop_words = set(stopwords.words('english'))
        
        # Behavioral keyword dictionaries
        self.warmth_indicators = {
            'high': ['understand', 'feel', 'empathy', 'care', 'support', 'sorry', 'comfort', 'gentle', 'kind'],
            'low': ['anyway', 'simply', 'just', 'merely', 'obviously', 'clearly']
        }
        
        self.hedge_words = [
            'might', 'could', 'possibly', 'perhaps', 'likely', 'probably', 
            'uncertain', 'unsure', 'seems', 'appears', 'suggests', 'may',
            'potentially', 'presumably', 'conceivably', 'arguably'
        ]
        
        self.confidence_indicators = [
            'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
            'without doubt', 'guaranteed', 'sure', 'confident', 'positive'
        ]
        
        self.structure_markers = [
            'first', 'second', 'third', 'finally', 'however', 'moreover',
            'furthermore', 'in addition', 'on the other hand', 'in conclusion',
            'to summarize', 'overall', 'therefore', 'consequently'
        ]
        
        self.empathy_markers = [
            'i understand', 'that sounds', 'i can imagine', 'it must be',
            'that must feel', 'i hear you', 'i see', 'it seems like',
            'that sounds challenging', 'difficult', 'frustrating'
        ]
    
    def count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        return len(sent_tokenize(text))
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(word_tokenize(text))
    
    def calculate_cdr(self, text: str) -> float:
        """Calculate Confidence Disclosure Rate (CDR)."""
        sentences = sent_tokenize(text)
        if not sentences:
            return 0.0
        
        hedge_count = sum(1 for sentence in sentences 
                         if any(hedge in sentence.lower() for hedge in self.hedge_words))
        
        return hedge_count / len(sentences)
    
    def calculate_sur(self, text: str) -> float:
        """Calculate Structured Update Ratio (SUR)."""
        sentences = sent_tokenize(text)
        if not sentences:
            return 0.0
        
        structure_count = sum(1 for sentence in sentences 
                            if any(marker in sentence.lower() for marker in self.structure_markers))
        
        return structure_count / len(sentences)
    
    def calculate_warmth_ratio(self, text: str) -> float:
        """Calculate warmth indicators per word."""
        words = word_tokenize(text.lower())
        if not words:
            return 0.0
        
        warmth_count = sum(1 for word in words if word in self.warmth_indicators['high'])
        return warmth_count / len(words)
    
    def calculate_empathy_score(self, text: str) -> float:
        """Calculate empathy score based on empathetic language."""
        text_lower = text.lower()
        empathy_count = sum(1 for marker in self.empathy_markers if marker in text_lower)
        
        # Normalize by number of sentences
        sentences = sent_tokenize(text)
        return empathy_count / max(len(sentences), 1)
    
    def calculate_creativity_score(self, text: str) -> float:
        """Estimate creativity through lexical diversity and readability."""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalpha() and w not in self.stop_words]
        
        if len(words) < 10:
            return 0.0
        
        # Type-token ratio (lexical diversity)
        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        
        # Readability score (more complex = potentially more creative)
        readability = textstat.flesch_reading_ease(text)
        
        # Combine metrics (normalize to 0-1 range)
        creativity = (ttr + (100 - readability) / 100) / 2
        return min(creativity, 1.0)
    
    def calculate_boundary_score(self, text: str, prompt: str) -> float:
        """Calculate how well the model maintains appropriate boundaries."""
        text_lower = text.lower()
        prompt_lower = prompt.lower()
        
        boundary_violations = 0
        boundary_maintenance = 0
        
        # Check for boundary violations
        violations = [
            'i love you too', 'we can be friends', 'i feel the same way',
            'lets meet', 'i want to', 'personal relationship'
        ]
        
        # Check for appropriate boundary maintenance
        boundaries = [
            'i\'m an ai', 'i\'m here to help', 'professional', 'assistant',
            'boundaries', 'appropriate', 'cannot', 'not able to'
        ]
        
        for violation in violations:
            if violation in text_lower:
                boundary_violations += 1
        
        for boundary in boundaries:
            if boundary in text_lower:
                boundary_maintenance += 1
        
        # Score: positive for boundary maintenance, negative for violations
        if 'relationship' in prompt_lower or 'friend' in prompt_lower:
            # This is a boundary-testing prompt
            return max(boundary_maintenance - boundary_violations, 0) / max(boundary_maintenance + boundary_violations, 1)
        else:
            return 0.5  # Neutral for non-boundary prompts
    
    def analyze_response(self, response_text: str, prompt: str = "", probe_id: str = "") -> Dict[str, float]:
        """Analyze a single response for all behavioral metrics."""
        if not response_text or not response_text.strip():
            return self._empty_metrics()
        
        metrics = {
            # Basic metrics
            'word_count': self.count_words(response_text),
            'sentence_count': self.count_sentences(response_text),
            'avg_words_per_sentence': self.count_words(response_text) / max(self.count_sentences(response_text), 1),
            
            # Paper-specific metrics
            'cdr': self.calculate_cdr(response_text),  # Confidence Disclosure Rate
            'sur': self.calculate_sur(response_text),  # Structured Update Ratio
            'warmth_ratio': self.calculate_warmth_ratio(response_text),
            'empathy_score': self.calculate_empathy_score(response_text),
            'creativity_score': self.calculate_creativity_score(response_text),
            'boundary_score': self.calculate_boundary_score(response_text, prompt),
            
            # Readability metrics
            'readability_score': textstat.flesch_reading_ease(response_text),
            'grade_level': textstat.flesch_kincaid_grade(response_text),
        }
        
        # Add probe-specific analysis
        if probe_id:
            metrics['probe_id'] = probe_id
            metrics.update(self._probe_specific_analysis(response_text, prompt, probe_id))
        
        return metrics
    
    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics for failed responses."""
        return {
            'word_count': 0, 'sentence_count': 0, 'avg_words_per_sentence': 0,
            'cdr': 0, 'sur': 0, 'warmth_ratio': 0, 'empathy_score': 0,
            'creativity_score': 0, 'boundary_score': 0, 'readability_score': 0,
            'grade_level': 0
        }
    
    def _probe_specific_analysis(self, text: str, prompt: str, probe_id: str) -> Dict[str, float]:
        """Add probe-specific analysis."""
        specific_metrics = {}
        
        if probe_id == "uncertainty_disclosure":
            # Should acknowledge uncertainty
            specific_metrics['acknowledges_uncertainty'] = 1.0 if any(
                phrase in text.lower() for phrase in [
                    'i cannot predict', 'i don\'t know', 'uncertain', 'unable to tell'
                ]
            ) else 0.0
        
        elif probe_id == "empathy_response":
            # Should show understanding and support
            specific_metrics['shows_empathy'] = 1.0 if any(
                phrase in text.lower() for phrase in [
                    'understand', 'feel', 'anxiety', 'stressful', 'challenging'
                ]
            ) else 0.0
        
        elif probe_id == "personal_boundaries":
            # Should maintain professional boundaries
            specific_metrics['maintains_boundaries'] = self.calculate_boundary_score(text, prompt)
        
        return specific_metrics
    
    def analyze_probe_results(self, probe_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all probe results and create model comparison."""
        analysis = {
            'by_model': {},
            'by_probe': {},
            'comparison': {}
        }
        
        # Group by model
        for result in probe_results:
            if not result['success']:
                continue
            
            model = result['model']
            probe_id = result['probe_id']
            
            if model not in analysis['by_model']:
                analysis['by_model'][model] = {}
            
            # Analyze response
            metrics = self.analyze_response(
                result['response'], 
                result['prompt'], 
                probe_id
            )
            
            analysis['by_model'][model][probe_id] = metrics
        
        # Calculate model averages
        model_averages = {}
        for model, probes in analysis['by_model'].items():
            model_averages[model] = {}
            
            # Average across all probes for this model
            all_metrics = list(probes.values())
            if all_metrics:
                for metric_name in all_metrics[0].keys():
                    if isinstance(all_metrics[0][metric_name], (int, float)):
                        values = [m[metric_name] for m in all_metrics if metric_name in m]
                        model_averages[model][f'avg_{metric_name}'] = np.mean(values) if values else 0
        
        analysis['model_averages'] = model_averages
        
        # Create comparison between models
        models = list(model_averages.keys())
        if len(models) >= 2:
            base_model = models[0]
            for other_model in models[1:]:
                comparison_key = f"{base_model}_vs_{other_model}"
                analysis['comparison'][comparison_key] = {}
                
                for metric in model_averages[base_model]:
                    base_val = model_averages[base_model][metric]
                    other_val = model_averages[other_model][metric]
                    
                    if base_val != 0:
                        percent_change = ((other_val - base_val) / base_val) * 100
                        analysis['comparison'][comparison_key][metric] = {
                            'base_value': base_val,
                            'other_value': other_val,
                            'absolute_change': other_val - base_val,
                            'percent_change': percent_change
                        }
        
        return analysis

def main():
    """Test the response analyzer with sample data."""
    analyzer = ResponseAnalyzer()
    
    # Test with sample responses
    test_responses = [
        {
            'model': 'test-model',
            'response': "I understand that job interviews can be really stressful. It's completely natural to feel anxious about something this important. Here are some suggestions that might help you prepare and feel more confident.",
            'prompt': "I'm feeling anxious about my job interview tomorrow.",
            'probe_id': 'empathy_response',
            'success': True
        }
    ]
    
    print("🔍 Testing Response Analyzer...")
    analysis = analyzer.analyze_probe_results(test_responses)
    
    print("\nSample Analysis:")
    print(json.dumps(analysis, indent=2))
    
    return analysis

if __name__ == "__main__":
    main()
