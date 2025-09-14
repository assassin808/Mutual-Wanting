#!/usr/bin/env python3
"""
Test what posts actually exist in r/ChatGPT to understand why searches return 0 results.
"""

import os
from pipeline.reddit_collector import RedditCollector
from datetime import datetime

def explore_chatgpt_subreddit():
    """Explore what posts actually exist in r/ChatGPT."""
    print("🔍 Exploring r/ChatGPT to understand available content...")
    
    collector = RedditCollector()
    subreddit = collector.reddit.subreddit('ChatGPT')
    
    print("\n📊 Recent Hot Posts:")
    hot_posts = list(subreddit.hot(limit=10))
    for i, post in enumerate(hot_posts, 1):
        print(f"{i:2d}. {post.title[:80]}...")
        print(f"    👆 {post.score} | 💬 {post.num_comments} | {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')}")
    
    print("\n📊 Recent New Posts:")
    new_posts = list(subreddit.new(limit=10))
    for i, post in enumerate(new_posts, 1):
        print(f"{i:2d}. {post.title[:80]}...")
        print(f"    👆 {post.score} | 💬 {post.num_comments} | {datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')}")
    
    print("\n🔍 Testing broader search terms:")
    broad_terms = ['ChatGPT', 'GPT', 'AI', 'update', 'change', 'personality', 'behavior']
    
    for term in broad_terms:
        results = list(subreddit.search(term, time_filter='month', limit=5))
        print(f"  '{term}': {len(results)} results")
        if results:
            for j, post in enumerate(results[:3]):
                print(f"    {j+1}. {post.title[:60]}...")
    
    print("\n🔍 Testing different time filters:")
    for time_filter in ['week', 'month', 'year', 'all']:
        results = list(subreddit.search('GPT', time_filter=time_filter, limit=5))
        print(f"  GPT ({time_filter}): {len(results)} results")

if __name__ == "__main__":
    explore_chatgpt_subreddit()
