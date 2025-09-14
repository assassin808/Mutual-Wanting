#!/usr/bin/env python3
"""
Data Collection Orchestrator
=============================

Coordinates the collection of both Reddit data and API probe data.
Run this before experiments to ensure we have real data for publication.
"""

import sys
from pathlib import Path
import json

# Add pipeline to path
pipeline_dir = Path(__file__).parent / "pipeline"
sys.path.append(str(pipeline_dir))

def collect_reddit_data():
    """Collect Reddit discourse data."""
    print("🔍 Starting Reddit Data Collection...")
    
    try:
        from pipeline.reddit_collector import RedditCollector
        
        collector = RedditCollector()
        
        # Collect data with reasonable limits for publication
        comments = collector.collect_all_data(
            time_filter='year',  # Last year of data
            limit_per_subreddit=300  # Enough for statistical significance
        )
        
        if not comments:
            print("❌ No Reddit comments collected. Check API credentials and search terms.")
            return False
        
        # Save data
        results = collector.save_data(comments, Path("pipeline/data"))
        
        print(f"✅ Reddit data collection complete:")
        print(f"   Pre-transition: {results['pre_count']} comments")
        print(f"   Post-transition: {results['post_count']} comments")
        print(f"   Total: {results['total_count']} comments")
        
        # Validate we have enough data
        if results['pre_count'] < 10 or results['post_count'] < 10:
            print("⚠️  Warning: Low comment counts may affect analysis quality.")
            print("   Consider adjusting search terms or time ranges.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import Reddit collector: {e}")
        print("   Install required packages: pip install praw python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Reddit collection failed: {e}")
        return False

def collect_api_probe_data():
    """Collect API probe response data."""
    print("\n🔍 Starting API Probe Data Collection...")
    
    try:
        from pipeline.openrouter_client import OpenRouterClient
        from pipeline.response_analyzer import ResponseAnalyzer
        
        # Initialize clients
        api_client = OpenRouterClient()
        analyzer = ResponseAnalyzer()
        
        # Test models for comparison (updated for 2025)
        models_to_test = [
            'gpt-5',           # Latest model
            'gpt-4o',          # Previous flagship
            'gpt-4-turbo',     # Turbo variant
            'gpt-3.5-turbo'    # Baseline for comparison
        ]
        
        print(f"Testing models: {', '.join(models_to_test)}")
        
        # Run probe suite
        probe_results = api_client.run_probe_suite(models_to_test)
        
        if not probe_results:
            print("❌ No probe results obtained.")
            return False
        
        # Analyze responses
        analysis = analyzer.analyze_probe_results(probe_results)
        
        # Save comprehensive results
        output_dir = Path("pipeline/data")
        
        # Save raw probe data
        summary = api_client.save_probe_results(probe_results, output_dir)
        
        # Save analysis
        with open(output_dir / "probe_analysis_complete.json", 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"✅ API probe collection complete:")
        successful_probes = sum(1 for r in probe_results if r['success'])
        print(f"   Successful probes: {successful_probes}/{len(probe_results)}")
        print(f"   Models tested: {len(models_to_test)}")
        
        # Show model comparison summary
        if 'model_averages' in analysis:
            print("\n📊 Model Comparison Preview:")
            for model, metrics in analysis['model_averages'].items():
                warmth = metrics.get('avg_warmth_ratio', 0)
                tokens = metrics.get('avg_word_count', 0)
                print(f"   {model}: warmth={warmth:.3f}, avg_words={tokens:.1f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import API clients: {e}")
        print("   Install required packages: pip install openai python-dotenv nltk textstat")
        return False
    except Exception as e:
        print(f"❌ API probe collection failed: {e}")
        print("   Check OpenRouter API key and network connection.")
        return False

def validate_data_quality():
    """Validate that collected data meets publication standards."""
    print("\n🔍 Validating Data Quality...")
    
    data_dir = Path("pipeline/data")
    issues = []
    
    # Check Reddit data (updated for GPT-5)
    reddit_files = [
        "gpt5_release_chatgpt_pre.jsonl",
        "gpt5_release_chatgpt_post.jsonl"
    ]
    
    for filename in reddit_files:
        filepath = data_dir / filename
        if not filepath.exists():
            issues.append(f"Missing Reddit data file: {filename}")
        else:
            # Count lines
            with open(filepath) as f:
                count = sum(1 for line in f if line.strip())
            
            if count < 20:
                issues.append(f"Low Reddit data count in {filename}: {count} items")
            else:
                print(f"✅ {filename}: {count} items")
    
    # Check API probe data
    probe_files = [
        "api_probe_results_raw.json",
        "probe_analysis_complete.json"
    ]
    
    for filename in probe_files:
        filepath = data_dir / filename
        if not filepath.exists():
            issues.append(f"Missing API probe file: {filename}")
        else:
            print(f"✅ {filename}: exists")
    
    # Check API probe success rate
    probe_raw_file = data_dir / "api_probe_results_raw.json"
    if probe_raw_file.exists():
        with open(probe_raw_file) as f:
            probe_data = json.load(f)
        
        successful = sum(1 for item in probe_data if item.get('success'))
        total = len(probe_data)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        if success_rate < 80:
            issues.append(f"Low API probe success rate: {success_rate:.1f}%")
        else:
            print(f"✅ API probe success rate: {success_rate:.1f}%")
    
    # Summary
    if issues:
        print(f"\n⚠️  Data Quality Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n🔧 Recommendations:")
        print("   - Re-run data collection with adjusted parameters")
        print("   - Check API credentials and rate limits")
        print("   - Consider expanding search terms or time ranges")
        return False
    else:
        print(f"\n✅ Data quality validation passed!")
        print("   All required data files present with sufficient data.")
        return True

def main():
    """Run complete data collection pipeline."""
    print("=" * 60)
    print("DATA COLLECTION FOR PUBLICATION")
    print("=" * 60)
    
    print("This script collects REAL data for the paper:")
    print("1. Reddit discourse analysis data")
    print("2. API probe comparison data")
    print("\nNote: This requires valid API credentials in .env file")
    
    # Collect Reddit data
    reddit_success = collect_reddit_data()
    
    # Collect API probe data
    api_success = collect_api_probe_data()
    
    # Validate overall data quality
    data_quality_ok = validate_data_quality()
    
    # Summary
    print("\n" + "=" * 60)
    print("DATA COLLECTION SUMMARY")
    print("=" * 60)
    
    print(f"Reddit Data Collection: {'✅ SUCCESS' if reddit_success else '❌ FAILED'}")
    print(f"API Probe Collection:   {'✅ SUCCESS' if api_success else '❌ FAILED'}")
    print(f"Data Quality Check:     {'✅ PASSED' if data_quality_ok else '❌ ISSUES'}")
    
    if reddit_success and api_success and data_quality_ok:
        print(f"\n🎉 DATA COLLECTION COMPLETE!")
        print(f"   Ready to run experiments with real data.")
        print(f"   Next step: python experiments/run_all_experiments.py")
        return True
    else:
        print(f"\n⚠️  DATA COLLECTION INCOMPLETE")
        print(f"   Some data collection failed. Check error messages above.")
        print(f"   Experiments will fall back to simulated data.")
        return False

if __name__ == "__main__":
    main()
