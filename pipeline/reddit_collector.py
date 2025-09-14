#!/usr/bin/env python3
"""
Reddit Data Collection Pipeline
===============================

Collects real user comments about AI persona changes using Reddit API.
Focuses on GPT-4 retirement and ChatGPT updates for lexical drift analysis.
"""

import praw
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

class RedditCollector:
    def __init__(self):
        """Initialize Reddit API client."""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Target subreddits for AI discussion (comprehensive list for 2025)
        self.target_subreddits = [
            # Primary OpenAI/GPT subreddits
            'ChatGPT',           # 9.9M+ members - main ChatGPT community
            'OpenAI',            # 2.3M+ members - OpenAI discussion
            'ChatGPTPro',        # 390K+ members - professional usage
            'GPT3',              # 589K+ members - GPT model discussions
            'GPTStore',          # GPT app store discussions
            
            # General AI subreddits (high engagement)
            'artificial',        # 1.1M+ members - general AI discussion  
            'ArtificialInteligence',  # 1.4M+ members - trending AI updates
            'MachineLearning',   # 2.8M+ members - technical ML discussion
            'singularity',       # 1.5M+ members - AGI and future AI
            'agi',               # 62K+ members - artificial general intelligence
            
            # Model-specific communities
            'ClaudeAI',          # Anthropic's Claude
            'GoogleGeminiAI',    # Google's Gemini
            'GeminiAI',          # Alternative Gemini community
            'LocalLLaMA',        # Open source LLMs
            'MistralAI',         # Mistral model discussions
            
            # AI prompt and programming
            'AIPromptProgramming', # 69K+ members - prompt engineering
            'PromptEngineering',   # Prompt optimization
            'ChatGPTCoding',       # AI for programming
            
            # AI applications and tools
            'AutoGPT',           # Autonomous AI agents
            'AI_Agents',         # AI agent development
            'aiwars',            # AI model comparisons and debates
            'AIethics',          # AI ethics discussions
            'generativeAI',      # Generative AI tools and discussion
            
            # Tech communities with AI focus
            'technology',        # 14M+ members - general tech with AI news
            'futurology',        # 19M+ members - future tech predictions
            'programming'        # 5M+ members - includes AI programming
        ]
        
        # Keywords that indicate persona/personality complaints
        self.persona_keywords = [
            'personality', 'persona', 'character', 'behavior', 'tone',
            'warm', 'cold', 'friendly', 'robotic', 'mechanical', 'bland',
            'creative', 'boring', 'lazy', 'helpful', 'unhelpful',
            'changed', 'different', 'worse', 'better', 'lobotomized',
            'canned', 'generic', 'empathy', 'empathetic', 'caring',
            'rude', 'polite', 'formal', 'informal', 'stiff'
        ]
    
    def is_relevant_comment(self, comment_text, debug=False):
        """Check if comment discusses AI persona/personality changes."""
        if not comment_text or len(comment_text.strip()) == 0:
            if debug: print(f"    [DEBUG] Empty comment")
            return False
            
        text_lower = comment_text.lower()
        
        # Must mention AI/GPT/ChatGPT
        ai_mentions = any(term in text_lower for term in [
            'chatgpt', 'gpt', 'openai', 'ai', 'assistant', 'bot', 'claude', 'gemini', 'bard'
        ])
        
        # Must contain persona-related keywords
        persona_mentions = any(keyword in text_lower for keyword in self.persona_keywords)
        
        # Should be substantial (not just "yes" or "lol")
        substantial = len(comment_text.split()) >= 5  # Reduced from 10 to 5
        
        if debug:
            print(f"    [DEBUG] Comment: '{comment_text[:100]}...'")
            print(f"    [DEBUG] AI mentions: {ai_mentions}, Persona mentions: {persona_mentions}, Substantial: {substantial}")
            print(f"    [DEBUG] Word count: {len(comment_text.split())}")
            if ai_mentions:
                found_ai_terms = [term for term in ['chatgpt', 'gpt', 'openai', 'ai', 'assistant', 'bot', 'claude', 'gemini', 'bard'] if term in text_lower]
                print(f"    [DEBUG] Found AI terms: {found_ai_terms}")
            if persona_mentions:
                found_persona_terms = [keyword for keyword in self.persona_keywords if keyword in text_lower]
                print(f"    [DEBUG] Found persona terms: {found_persona_terms}")
        
        return ai_mentions and persona_mentions and substantial
    
    def collect_subreddit_data(self, subreddit_name, time_filter='month', limit=1000):
        """Collect relevant posts and comments from a subreddit."""
        print(f"Collecting from r/{subreddit_name}...")
        
        subreddit = self.reddit.subreddit(subreddit_name)
        collected_comments = []
        
        # Search for posts about GPT updates, model changes, etc. (updated for 2025)
        search_queries = [
            # Use broader terms that actually return results
            'ChatGPT', 'GPT', 'AI', 'update', 'change', 'personality', 
            'behavior', 'model', 'worse', 'better', 'different'
        ]
        
        posts_found = 0
        comments_checked = 0
        relevant_found = 0
        
        for query in search_queries:
            try:
                print(f"  Searching: '{query}'")
                posts = subreddit.search(query, time_filter=time_filter, limit=limit//len(search_queries))
                
                query_posts = 0
                for post in posts:
                    posts_found += 1
                    query_posts += 1
                    
                    # Collect post body if relevant
                    if hasattr(post, 'selftext') and post.selftext and self.is_relevant_comment(post.selftext, debug=False):
                        collected_comments.append({
                            'id': post.id,
                            'type': 'post',
                            'author': str(post.author) if post.author else '[deleted]',
                            'body': post.selftext,
                            'score': post.score,
                            'created_utc': post.created_utc,
                            'subreddit': subreddit_name,
                            'title': post.title,
                            'url': post.url
                        })
                        relevant_found += 1
                    
                    # Collect relevant comments
                    try:
                        post.comments.replace_more(limit=0)  # Don't expand "more comments"
                        for comment in post.comments[:50]:  # Limit per post
                            comments_checked += 1
                            if hasattr(comment, 'body') and self.is_relevant_comment(comment.body, debug=False):
                                collected_comments.append({
                                    'id': comment.id,
                                    'type': 'comment',
                                    'author': str(comment.author) if comment.author else '[deleted]',
                                    'body': comment.body,
                                    'score': comment.score,
                                    'created_utc': comment.created_utc,
                                    'subreddit': subreddit_name,
                                    'parent_post_title': post.title,
                                    'parent_post_id': post.id
                                })
                                relevant_found += 1
                    except Exception as e:
                        print(f"    Error processing comments for post {post.id}: {e}")
                        continue
                
                print(f"    Query '{query}': {query_posts} posts found")
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error searching '{query}': {e}")
                continue
        
        # Also collect from recent hot posts (they often contain relevant discussions)
        print("  Collecting from hot posts...")
        try:
            hot_posts = list(subreddit.hot(limit=25))
            print(f"    Found {len(hot_posts)} hot posts")
            
            for post in hot_posts:
                posts_found += 1
                
                # Check post content
                post_text = f"{post.title} {post.selftext if hasattr(post, 'selftext') else ''}"
                if self.is_relevant_comment(post_text):
                    collected_comments.append({
                        'id': post.id,
                        'type': 'post',
                        'author': str(post.author) if post.author else '[deleted]',
                        'body': post_text,
                        'score': post.score,
                        'created_utc': post.created_utc,
                        'subreddit': subreddit_name,
                        'title': post.title,
                        'url': post.url
                    })
                    relevant_found += 1
                
                # Collect comments from hot posts
                try:
                    post.comments.replace_more(limit=2)
                    for comment in post.comments.list()[:20]:  # Limit comments per hot post
                        comments_checked += 1
                        if hasattr(comment, 'body') and comment.body and comment.body != '[deleted]':
                            if self.is_relevant_comment(comment.body):
                                collected_comments.append({
                                    'id': comment.id,
                                    'type': 'comment',
                                    'author': str(comment.author) if comment.author else '[deleted]',
                                    'body': comment.body,
                                    'score': comment.score,
                                    'created_utc': comment.created_utc,
                                    'subreddit': subreddit_name,
                                    'parent_post_title': post.title,
                                    'parent_post_id': post.id
                                })
                                relevant_found += 1
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"    Error collecting hot posts: {e}")
        
        print(f"  [DEBUG] Total posts found: {posts_found}")
        print(f"  [DEBUG] Total comments checked: {comments_checked}")
        print(f"  [DEBUG] Relevant items found: {relevant_found}")
        print(f"  Collected {len(collected_comments)} relevant items from r/{subreddit_name}")
        return collected_comments
    
    def determine_time_period(self, timestamp):
        """Classify comment as pre/post GPT-5 release (December 2024)."""
        # GPT-5 was released around December 2024
        cutoff_date = datetime(2024, 12, 1).timestamp()
        
        if timestamp < cutoff_date:
            return 'pre'  # Pre-GPT-5 era
        else:
            return 'post'  # Post-GPT-5 era
    
    def collect_all_data(self, time_filter='year', limit_per_subreddit=500):
        """Collect data from all target subreddits."""
        all_comments = []
        
        print("Starting Reddit data collection...")
        print(f"Target subreddits: {', '.join(self.target_subreddits)}")
        
        for subreddit_name in self.target_subreddits:
            try:
                comments = self.collect_subreddit_data(
                    subreddit_name, 
                    time_filter=time_filter, 
                    limit=limit_per_subreddit
                )
                all_comments.extend(comments)
                
                # Be nice to Reddit's API
                time.sleep(2)
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
                continue
        
        print(f"\nTotal collected: {len(all_comments)} items")
        return all_comments
    
    def save_data(self, comments, output_dir):
        """Save collected data, split by time period."""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"\n[DEBUG] Starting to save {len(comments)} total comments...")
        
        # Split by time period
        pre_comments = []
        post_comments = []
        
        for comment in comments:
            period = self.determine_time_period(comment['created_utc'])
            comment_date = datetime.fromtimestamp(comment['created_utc'])
            print(f"[DEBUG] Comment from {comment_date.strftime('%Y-%m-%d')} classified as '{period}'")
            
            if period == 'pre':
                pre_comments.append(comment)
            else:
                post_comments.append(comment)
        
        print(f"[DEBUG] Split results: {len(pre_comments)} pre, {len(post_comments)} post")
        
        # Save as JSONL files (updated for GPT-5 era)
        pre_file = output_dir / "gpt5_release_chatgpt_pre.jsonl"
        post_file = output_dir / "gpt5_release_chatgpt_post.jsonl"
        
        print(f"[DEBUG] Saving to files:")
        print(f"[DEBUG]   Pre-file: {pre_file}")
        print(f"[DEBUG]   Post-file: {post_file}")
        
        with open(pre_file, 'w') as f:
            for comment in pre_comments:
                f.write(json.dumps(comment) + '\n')
        
        with open(post_file, 'w') as f:
            for comment in post_comments:
                f.write(json.dumps(comment) + '\n')
        
        # Also save as CSV for easier analysis
        if comments:  # Only save CSV if we have data
            df = pd.DataFrame(comments)
            csv_file = output_dir / "reddit_comments_all.csv"
            df.to_csv(csv_file, index=False)
            print(f"[DEBUG] CSV saved: {csv_file}")
        else:
            print(f"[DEBUG] No comments to save to CSV")
        
        print(f"\nData saved:")
        print(f"  Pre-transition: {len(pre_comments)} items → {pre_file}")
        print(f"  Post-transition: {len(post_comments)} items → {post_file}")
        print(f"  All data: {len(comments)} items → reddit_comments_all.csv")
        
        return {
            'pre_count': len(pre_comments),
            'post_count': len(post_comments),
            'total_count': len(comments),
            'pre_file': str(pre_file),
            'post_file': str(post_file)
        }

def main():
    """Run Reddit data collection."""
    collector = RedditCollector()
    
    # Test mode: collect a small sample first
    print("🔍 Running in TEST MODE - collecting sample data...")
    
    # Try just one subreddit first
    test_subreddit = 'ChatGPT'
    print(f"Testing collection from r/{test_subreddit}...")
    
    test_comments = collector.collect_subreddit_data(
        test_subreddit, 
        time_filter='month',  # Last month
        limit=50  # Small limit for testing
    )
    
    print(f"\n[DEBUG] Test collection results: {len(test_comments)} comments")
    
    if test_comments:
        print("\n[DEBUG] Sample comment data:")
        for i, comment in enumerate(test_comments[:3]):  # Show first 3 comments
            print(f"  Comment {i+1}:")
            print(f"    ID: {comment['id']}")
            print(f"    Type: {comment['type']}")
            print(f"    Subreddit: {comment['subreddit']}")
            print(f"    Body: {comment['body'][:100]}...")
            print(f"    Date: {datetime.fromtimestamp(comment['created_utc']).strftime('%Y-%m-%d %H:%M')}")
    
    # Save test data
    if test_comments:
        output_dir = Path("pipeline/data")
        results = collector.save_data(test_comments, output_dir)
        
        print(f"\n✅ Test data collection complete!")
        print(f"Results: {results}")
    else:
        print("\n❌ No comments collected in test mode.")
        print("This suggests either:")
        print("1. No posts found for the search queries")
        print("2. No comments pass the relevance filter")
        print("3. API/authentication issues")
        
        # Let's test the relevance filter with some examples
        print("\n🔍 Testing relevance filter...")
        test_texts = [
            "ChatGPT has become so robotic and cold lately, it lost its personality",
            "GPT-5 is amazing but feels different from GPT-4",
            "The AI seems more helpful but less creative",
            "Hello world",  # Should fail - no AI mention
            "ChatGPT is great",  # Should fail - no persona mention
            "I love the new AI updates, it's more empathetic and warm now"
        ]
        
        for text in test_texts:
            is_relevant = collector.is_relevant_comment(text, debug=True)
            print(f"    Relevant: {is_relevant}")
            print()
    
    return test_comments

if __name__ == "__main__":
    main()
