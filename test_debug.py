#!/usr/bin/env python3
"""
Quick test script to debug Reddit data collection issues.
"""

import os
from pipeline.reddit_collector import RedditCollector
from datetime import datetime

def test_api_access():
    """Test basic Reddit API access."""
    print("🔍 Testing Reddit API access...")
    
    # Check environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            return False
    
    try:
        collector = RedditCollector()
        print("✅ RedditCollector initialized successfully")
        
        # Test basic subreddit access
        subreddit = collector.reddit.subreddit('ChatGPT')
        print(f"✅ Accessed r/ChatGPT - {subreddit.display_name}")
        
        # Get a few posts
        posts = list(subreddit.hot(limit=5))
        print(f"✅ Retrieved {len(posts)} hot posts")
        
        return True
        
    except Exception as e:
        print(f"❌ API access failed: {e}")
        return False

def test_filtering():
    """Test comment filtering logic."""
    print("\n🔍 Testing comment filtering...")
    
    collector = RedditCollector()
    
    test_cases = [
        ("ChatGPT has become so robotic and cold lately I miss the old version", True),
        ("GPT-5 personality changed completely from the previous model version", True),
        ("The AI assistant seems more creative now than it was before", True),
        ("Claude is more empathetic than before when I ask questions", True),
        ("Hello world", False),
        ("Great weather today", False),
        ("I love pizza", False),
        ("OpenAI released updates", False),  # No persona mention
        ("ChatGPT is great but lost its warmth and personality completely", True),
    ]
    
    for text, expected in test_cases:
        result = collector.is_relevant_comment(text, debug=True)
        status = "✅" if result == expected else "❌"
        print(f"{status} Expected: {expected}, Got: {result}")
        print()

def test_data_collection():
    """Test actual data collection from a single subreddit."""
    print("\n🔍 Testing data collection...")
    
    collector = RedditCollector()
    
    # Collect from one subreddit
    comments = collector.collect_subreddit_data(
        'ChatGPT',
        time_filter='week',
        limit=20
    )
    
    print(f"\nCollected {len(comments)} comments")
    
    if comments:
        print("Sample comment:")
        comment = comments[0]
        for key, value in comment.items():
            if key == 'body':
                print(f"  {key}: {str(value)[:100]}...")
            else:
                print(f"  {key}: {value}")

if __name__ == "__main__":
    print("🧪 Reddit Data Collection Debug Test")
    print("=" * 50)
    
    # Test 1: API Access
    if not test_api_access():
        print("\n❌ API access failed. Please check your credentials.")
        exit(1)
    
    # Test 2: Filtering Logic
    test_filtering()
    
    # Test 3: Data Collection
    test_data_collection()
    
    print("\n✅ Debug tests complete!")
