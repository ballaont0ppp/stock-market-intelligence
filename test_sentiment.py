"""
Quick test script for multi-source sentiment analysis
"""
import os
from app.services.multi_sentiment_engine import MultiSentimentEngine

print("=" * 60)
print("Multi-Source Sentiment Engine Test")
print("=" * 60)

# Initialize engine
engine = MultiSentimentEngine()

# Check which sources are enabled
print(f"\n✅ Sentiment Engine Status:")
print(f"   Overall Enabled: {engine.is_enabled()}")
print(f"   Twitter: {engine.twitter_enabled}")
print(f"   News API: {engine.news_enabled}")

# Check environment variables
print(f"\n🔑 Environment Variables:")
print(f"   NEWS_API_KEY: {'✅ Set' if os.getenv('NEWS_API_KEY') else '❌ Not set'}")
print(f"   SENTIMENT_ENABLED: {os.getenv('SENTIMENT_ENABLED')}")

if engine.is_enabled():
    print(f"\n🎉 Success! Sentiment analysis is ready!")
    print(f"   Active sources: ", end="")
    sources = []
    if engine.twitter_enabled:
        sources.append("Twitter")
    if engine.news_enabled:
        sources.append("News API")
    print(", ".join(sources))
    
    # Optional: Test with a real stock symbol
    test_symbol = input("\n📊 Enter a stock symbol to test (or press Enter to skip): ").strip().upper()
    if test_symbol:
        print(f"\n🔍 Analyzing sentiment for {test_symbol}...")
        try:
            result = engine.analyze_sentiment(test_symbol, count_per_source=10)
            print(f"\n✅ Results:")
            print(f"   Sentiment: {result['sentiment']}")
            print(f"   Positive: {result['positive']}")
            print(f"   Negative: {result['negative']}")
            print(f"   Neutral: {result['neutral']}")
            print(f"   Total Items: {result['total_items']}")
            print(f"   Average Polarity: {result['average_polarity']}")
            print(f"   Sources Used: {', '.join(result['sources'])}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
else:
    print(f"\n⚠️  No sentiment sources are enabled.")
    print(f"   Please add your API credentials to the .env file.")

print("\n" + "=" * 60)
