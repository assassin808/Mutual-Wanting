#!/usr/bin/env python3
"""
Run only the API probe data collection part.
"""

import sys
import os
from pathlib import Path

# Add the pipeline directory to the path
sys.path.append(str(Path(__file__).parent / "pipeline"))

def collect_api_probe_data():
    """Run API probe data collection only."""
    print("🔍 Starting API Probe Data Collection...")
    
    try:
        from pipeline.openrouter_client import OpenRouterClient
        from pipeline.response_analyzer import ResponseAnalyzer
        import json
        
        # Initialize clients
        client = OpenRouterClient()
        analyzer = ResponseAnalyzer()
        
        # Test API access first
        print("Testing API access...")
        print(f"✅ API client initialized. Available models: {list(client.models.keys())}")
        
        # Run the probe suite
        print("Running behavioral probe suite...")
        results = client.run_probe_suite()
        
        # Save raw results
        output_dir = Path("pipeline/data")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        raw_file = output_dir / "api_probe_results_raw.json"
        with open(raw_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Raw probe results saved: {raw_file}")
        
        # Analyze results
        print("Analyzing probe results...")
        analysis = analyzer.analyze_probe_results(results)
        
        # Save analysis
        analysis_file = output_dir / "probe_analysis_complete.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✅ Probe analysis saved: {analysis_file}")
        
        print(f"\n🎉 API Probe Collection Complete!")
        print(f"   Raw results: {len(results)} probe responses")
        print(f"   Analysis: {len(analysis)} analyzed metrics")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ API probe collection failed: {e}")
        return False

if __name__ == "__main__":
    success = collect_api_probe_data()
    if success:
        print("\n✅ API data collection completed successfully!")
    else:
        print("\n❌ API data collection failed. Check error messages above.")
        sys.exit(1)
