"""
Example script demonstrating basic usage of Shameless Sentiment Analyser.

This script shows how to:
1. Collect tweets using snscrape
2. Preprocess the text data
3. Analyze sentiment using ML models
4. Save and visualize results
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta

from sentiment_analyser.config import get_settings
from sentiment_analyser.models import SentimentAnalyzer, TextPreprocessor
from sentiment_analyser.scraper import DataStorage, TwitterCollector


def main():
    """Main execution function."""
    
    print("🎭 Shameless Sentiment Analyser - Example Usage\n")
    print("=" * 60)
    
    # Configuration
    QUERY = "artificial intelligence"
    MAX_TWEETS = 50
    SINCE_DATE = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    print(f"\n📋 Configuration:")
    print(f"  Query: {QUERY}")
    print(f"  Max tweets: {MAX_TWEETS}")
    print(f"  Since: {SINCE_DATE}\n")
    
    # Step 1: Initialize components
    print("🔧 Initializing components...")
    settings = get_settings()
    collector = TwitterCollector(rate_limit=1.0)
    preprocessor = TextPreprocessor(
        lowercase=True,
        remove_urls=True,
        remove_mentions=False,
        remove_hashtags=False
    )
    # Use Kaggle model with version from settings
    analyzer = SentimentAnalyzer(
        use_kaggle_model=True,
        kaggle_model_version=settings.MODEL_VERSION,
        device=settings.MODEL_DEVICE,
        preprocess=False
    )
    storage = DataStorage(settings.RAW_DATA_DIR)
    
    print(f"✅ Components initialized (Model: {settings.MODEL_VERSION}, Device: {settings.MODEL_DEVICE})\n")
    
    # Step 2: Collect tweets
    print(f"🐦 Collecting tweets for '{QUERY}'...")
    tweets = []
    
    try:
        for i, tweet in enumerate(collector.search(
            query=QUERY,
            limit=MAX_TWEETS,
            since=SINCE_DATE
        ), 1):
            tweets.append(tweet.to_dict())
            
            if i % 10 == 0:
                print(f"  Collected {i} tweets...")
        
        print(f"✅ Collected {len(tweets)} tweets\n")
        
    except Exception as e:
        print(f"❌ Error collecting tweets: {e}")
        return
    
    if not tweets:
        print("❌ No tweets collected. Exiting.")
        return
    
    # Step 3: Preprocess texts
    print("🧹 Preprocessing texts...")
    texts = [tweet['content'] for tweet in tweets]
    clean_texts = preprocessor.clean_batch(texts)
    print(f"✅ Preprocessed {len(clean_texts)} texts\n")
    
    # Step 4: Analyze sentiment
    print("🤖 Analyzing sentiment...")
    try:
        results = analyzer.analyze_batch(clean_texts, batch_size=16)
        print(f"✅ Analyzed {len(results)} texts\n")
    except Exception as e:
        print(f"❌ Error during sentiment analysis: {e}")
        return
    
    # Step 5: Add results to tweets
    for tweet, result in zip(tweets, results):
        tweet['sentiment'] = result['sentiment']
        tweet['sentiment_score'] = result['score']
        tweet['sentiment_label'] = result['label']
    
    # Step 6: Display results
    print("=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    # Count sentiments
    from collections import Counter
    sentiments = [tweet['sentiment'] for tweet in tweets]
    sentiment_counts = Counter(sentiments)
    
    print(f"\nSentiment Distribution:")
    for sentiment, count in sentiment_counts.most_common():
        percentage = (count / len(tweets)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {sentiment.capitalize():10} {bar} {count:3} ({percentage:5.1f}%)")
    
    # Average confidence
    avg_confidence = sum(tweet['sentiment_score'] for tweet in tweets) / len(tweets)
    print(f"\nAverage Confidence: {avg_confidence:.2%}\n")
    
    # Top positive tweets
    print("\n🌟 Top 3 Most Positive Tweets:")
    print("-" * 60)
    positive_tweets = sorted(
        [t for t in tweets if t['sentiment'] == 'positive'],
        key=lambda x: x['sentiment_score'],
        reverse=True
    )[:3]
    
    for i, tweet in enumerate(positive_tweets, 1):
        print(f"\n{i}. Score: {tweet['sentiment_score']:.2%}")
        print(f"   {tweet['content'][:100]}...")
        print(f"   By: @{tweet['username']} | ❤️ {tweet['likes']} | 🔄 {tweet['retweets']}")
    
    # Top negative tweets
    print("\n\n⚠️  Top 3 Most Negative Tweets:")
    print("-" * 60)
    negative_tweets = sorted(
        [t for t in tweets if t['sentiment'] == 'negative'],
        key=lambda x: x['sentiment_score'],
        reverse=True
    )[:3]
    
    for i, tweet in enumerate(negative_tweets, 1):
        print(f"\n{i}. Score: {tweet['sentiment_score']:.2%}")
        print(f"   {tweet['content'][:100]}...")
        print(f"   By: @{tweet['username']} | ❤️ {tweet['likes']} | 🔄 {tweet['retweets']}")
    
    # Step 7: Save results
    print("\n" + "=" * 60)
    print("💾 Saving results...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sentiment_analysis_{timestamp}"
    
    try:
        # Save as JSON
        json_path = storage.save_json(tweets, f"{filename}.json")
        print(f"✅ JSON saved: {json_path}")
        
        # Save as CSV
        csv_path = storage.save_csv(tweets, f"{filename}.csv")
        print(f"✅ CSV saved: {csv_path}")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Analysis complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Open the Jupyter notebook for detailed analysis")
    print("  2. Visualize results with charts and graphs")
    print("  3. Try different queries and parameters")
    print("  4. Export results for reports\n")


if __name__ == "__main__":
    main()
