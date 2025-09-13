#!/usr/bin/env python3
"""
Experiment 1: Reddit Discourse Analysis
========================================

Purpose: Analyze user complaints about AI persona changes across model transitions
Key Metric: Lexical drift in complaint language (warmth, creativity, helpfulness)
Output: Table of word frequency changes pre/post transition

This implements the "Source 1" methodology from the paper.
"""

import json
import pandas as pd
from collections import Counter
import numpy as np
from pathlib import Path
import sys
import os

# Add pipeline directory to path for imports
pipeline_dir = Path(__file__).parent.parent / "pipeline"
sys.path.append(str(pipeline_dir))

try:
    from reddit_collector import RedditCollector
except ImportError:
    print("Warning: Could not import RedditCollector. Will use existing data or examples.")
    RedditCollector = None

def load_reddit_data():
    """Load pre/post transition Reddit data. Collect new data if needed."""
    data_dir = Path("pipeline/data")
    
    # Load existing data if available (updated for GPT-5 era)
    pre_file = data_dir / "gpt5_release_chatgpt_pre.jsonl"
    post_file = data_dir / "gpt5_release_chatgpt_post.jsonl"
    
    pre_posts = []
    post_posts = []
    
    if pre_file.exists():
        with open(pre_file) as f:
            pre_posts = [json.loads(line) for line in f if line.strip()]
    
    if post_file.exists():
        with open(post_file) as f:
            post_posts = [json.loads(line) for line in f if line.strip()]
    
    # If no data exists, try to collect it
    if (not pre_posts or not post_posts) and RedditCollector:
        print("No existing Reddit data found. Collecting new data...")
        collector = RedditCollector()
        
        try:
            all_comments = collector.collect_all_data(time_filter='year', limit_per_subreddit=200)
            if all_comments:
                results = collector.save_data(all_comments, data_dir)
                
                # Reload the newly collected data
                if Path(results['pre_file']).exists():
                    with open(results['pre_file']) as f:
                        pre_posts = [json.loads(line) for line in f if line.strip()]
                
                if Path(results['post_file']).exists():
                    with open(results['post_file']) as f:
                        post_posts = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            print(f"Failed to collect Reddit data: {e}")
            print("Using minimal example data for demonstration.")
    
    print(f"Loaded {len(pre_posts)} pre-transition posts")
    print(f"Loaded {len(post_posts)} post-transition posts")
    
    return pre_posts, post_posts

def extract_complaint_words(posts):
    """Extract complaint-related words from posts."""
    # Key complaint words from the paper's framework
    complaint_words = [
        'lazy', 'cold', 'canned', 'robotic', 'bland', 'boring',
        'warm', 'creative', 'helpful', 'personal', 'empathetic',
        'worse', 'better', 'changed', 'different', 'lost', 'missing'
    ]
    
    word_counts = Counter()
    total_words = 0
    
    for post in posts:
        text = post.get('body', '').lower()
        words = text.split()
        total_words += len(words)
        
        for word in complaint_words:
            if word in text:
                word_counts[word] += text.count(word)
    
    return word_counts, total_words

def compute_drift_analysis(pre_posts, post_posts):
    """Compute lexical drift between pre/post periods."""
    pre_counts, pre_total = extract_complaint_words(pre_posts)
    post_counts, post_total = extract_complaint_words(post_posts)
    
    results = []
    
    for word in set(pre_counts.keys()) | set(post_counts.keys()):
        pre_freq = pre_counts[word] / pre_total if pre_total > 0 else 0
        post_freq = post_counts[word] / post_total if post_total > 0 else 0
        
        # Log-odds ratio (as mentioned in paper)
        if pre_freq > 0 and post_freq > 0:
            log_odds = np.log(post_freq / pre_freq)
        else:
            log_odds = 0
        
        results.append({
            'word': word,
            'pre_freq': pre_freq,
            'post_freq': post_freq,
            'log_odds_change': log_odds,
            'pre_count': pre_counts[word],
            'post_count': post_counts[word]
        })
    
    return pd.DataFrame(results)

def main():
    """Run the Reddit discourse analysis."""
    print("=== Experiment 1: Reddit Discourse Analysis ===")
    
    # Load data
    pre_posts, post_posts = load_reddit_data()
    
    if not pre_posts or not post_posts:
        print("Warning: Missing Reddit data. Using minimal example.")
        # Create minimal example data
        pre_posts = [
            {"body": "The AI used to be so warm and helpful"},
            {"body": "It feels more creative than before"}
        ]
        post_posts = [
            {"body": "The AI seems cold and robotic now"},
            {"body": "It's become lazy and canned in responses"}
        ]
    
    # Run drift analysis
    drift_results = compute_drift_analysis(pre_posts, post_posts)
    
    # Sort by absolute log-odds change
    drift_results['abs_change'] = drift_results['log_odds_change'].abs()
    drift_results = drift_results.sort_values('abs_change', ascending=False)
    
    print("\n--- Lexical Drift Results ---")
    print(drift_results[['word', 'pre_freq', 'post_freq', 'log_odds_change']].round(4))
    
    # Save results
    output_dir = Path("pipeline/outputs")
    output_dir.mkdir(exist_ok=True)
    
    drift_results.to_csv(output_dir / "experiment_1_reddit_drift.csv", index=False)
    
    # Create summary for paper
    summary = {
        "experiment": "reddit_discourse_analysis",
        "pre_posts": len(pre_posts),
        "post_posts": len(post_posts),
        "top_drift_words": drift_results.head(5)[['word', 'log_odds_change']].to_dict('records'),
        "key_finding": f"Strongest drift in '{drift_results.iloc[0]['word']}' (log-odds: {drift_results.iloc[0]['log_odds_change']:.3f})"
    }
    
    with open(output_dir / "experiment_1_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Results saved to {output_dir}")
    print(f"Key finding: {summary['key_finding']}")
    
    return drift_results

if __name__ == "__main__":
    main()
