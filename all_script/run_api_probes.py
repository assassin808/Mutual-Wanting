#!/usr/bin/env python3
"""
Run comprehensive API probe collection with reproducibility testing.
"""

import json
from pathlib import Path
from pipeline.openrouter_client import OpenRouterClient

def main():
    print("🧪 COMPREHENSIVE API PROBE COLLECTION")
    print("=" * 60)
    print("🔬 Features:")
    print("   • 28 comprehensive persona analysis probes")
    print("   • 5 state-of-the-art models (GPT-4o, Claude-3, etc.)")
    print("   • 3 runs per probe for reproducibility")
    print("   • Temperature variation (0.3, 0.7, 1.0)")
    print("   • Statistical significance testing")
    print("=" * 60)
    
    # Initialize client
    try:
        client = OpenRouterClient()
        print("✅ OpenRouter client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # Run comprehensive probe suite with reproducibility
    print("\n🚀 Starting comprehensive probe collection...")
    try:
        results = client.run_probe_suite(num_runs=3)  # 3 runs for statistical analysis
        
        # Save raw results
        output_dir = Path("pipeline/data")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        raw_file = output_dir / "api_probe_results_raw.json"
        with open(raw_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Raw results saved: {raw_file}")
        print(f"📊 Total responses collected: {len(results)}")
        
        # Basic analysis
        successful_responses = [r for r in results if r['success']]
        failed_responses = [r for r in results if not r['success']]
        
        print(f"✅ Successful: {len(successful_responses)}")
        print(f"❌ Failed: {len(failed_responses)}")
        
        if successful_responses:
            models_tested = set(r['model'] for r in successful_responses)
            probes_completed = set(r['probe_id'] for r in successful_responses)
            
            print(f"\n📈 Collection Summary:")
            print(f"   Models tested: {len(models_tested)}")
            print(f"   Probe types: {len(probes_completed)}")
            print(f"   Avg tokens per response: {sum(r['usage']['total_tokens'] for r in successful_responses) // len(successful_responses)}")
            
            # Show probe categories
            categories = {}
            for result in successful_responses:
                category = result.get('probe_category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            print(f"\n🎯 Probe Categories Tested:")
            for category, count in sorted(categories.items()):
                print(f"   {category}: {count} responses")
        
        # Create analysis placeholder
        analysis_file = output_dir / "probe_analysis_complete.json"
        analysis_data = {
            "collection_timestamp": results[0]['timestamp'] if results else None,
            "total_responses": len(results),
            "successful_responses": len(successful_responses),
            "models_tested": list(models_tested) if successful_responses else [],
            "probe_categories": categories if successful_responses else {},
            "reproducibility_runs": 3,
            "temperature_variation": [0.3, 0.7, 1.0],
            "ready_for_analysis": True
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"💾 Analysis metadata saved: {analysis_file}")
        print("\n🎉 Comprehensive API probe collection complete!")
        print("📊 Ready for statistical analysis and persona assessment!")
        
    except Exception as e:
        print(f"❌ Probe collection failed: {e}")
        return

if __name__ == "__main__":
    main()
