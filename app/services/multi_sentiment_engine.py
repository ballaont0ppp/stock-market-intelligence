"""
Multi-Source Sentiment Engine
Supports Twitter and News API for comprehensive sentiment analysis
"""
import logging
import re
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Optional dependencies
TEXTBLOB_AVAILABLE = False
TWEEPY_AVAILABLE = False
NEWSAPI_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except Exception as _e:
    logging.getLogger(__name__).warning(f"TextBlob not available: {_e}")

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except Exception as _e:
    logging.getLogger(__name__).warning(f"tweepy not available: {_e}")

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except Exception as _e:
    logging.getLogger(__name__).warning(f"newsapi-python not available: {_e}")

from app import db
from app.models.sentiment_cache import SentimentCache
from app.utils.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


class MultiSentimentEngine:
    """Service for fetching content from multiple sources and analyzing sentiment"""
    
    def __init__(self):
        """Initialize the multi-source sentiment engine"""
        self.twitter_enabled = False
        self.news_enabled = False
        
        # Initialize each source
        self._init_twitter()
        self._init_news_api()
        
        # Log available sources
        sources = []
        if self.twitter_enabled:
            sources.append("Twitter")
        if self.news_enabled:
            sources.append("News API")
        
        if sources:
            logger.info(f"Sentiment analysis enabled with sources: {', '.join(sources)}")
        else:
            logger.warning("No sentiment sources available - all APIs disabled")
    
    def _init_twitter(self):
        """Initialize Twitter API"""
        if not TWEEPY_AVAILABLE or not TEXTBLOB_AVAILABLE:
            return
        
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        try:
            if bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
                self.twitter_enabled = True
                logger.info("Twitter API v2 initialized")
            elif all([api_key, api_secret, access_token, access_token_secret]):
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_token_secret)
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
                self.twitter_enabled = True
                logger.info("Twitter API v1.1 initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter: {e}")
    
    def _init_news_api(self):
        """Initialize News API"""
        if not NEWSAPI_AVAILABLE or not TEXTBLOB_AVAILABLE:
            return
        
        api_key = os.getenv('NEWS_API_KEY')
        if api_key:
            try:
                self.news_client = NewsApiClient(api_key=api_key)
                self.news_enabled = True
                logger.info("News API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize News API: {e}")
    
    def is_enabled(self) -> bool:
        """Check if any sentiment source is enabled"""
        return self.twitter_enabled or self.news_enabled
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing URLs, mentions, hashtags, and special characters"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtags (keep text)
        text = re.sub(r'#', '', text)
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def fetch_twitter_content(self, symbol: str, count: int = 50) -> List[str]:
        """Fetch tweets about the stock"""
        if not self.twitter_enabled:
            return []
        
        try:
            tweets = []
            query = f"${symbol} OR #{symbol} -is:retweet lang:en"
            
            if hasattr(self, 'twitter_client'):
                response = self.twitter_client.search_recent_tweets(
                    query=query,
                    max_results=min(count, 100),
                    tweet_fields=['created_at']
                )
                if response.data:
                    tweets = [tweet.text for tweet in response.data]
            elif hasattr(self, 'twitter_api'):
                cursor = tweepy.Cursor(
                    self.twitter_api.search_tweets,
                    q=query,
                    lang='en',
                    result_type='recent',
                    tweet_mode='extended'
                )
                for tweet in cursor.items(min(count, 100)):
                    tweets.append(tweet.full_text)
            
            logger.info(f"Fetched {len(tweets)} tweets for {symbol}")
            return tweets
        except Exception as e:
            logger.error(f"Twitter fetch error for {symbol}: {e}")
            return []
    
    def fetch_news_content(self, symbol: str, count: int = 50) -> List[str]:
        """Fetch news articles about the stock"""
        if not self.news_enabled:
            return []
        
        try:
            articles = []
            # Search for company name and stock symbol
            query = f"{symbol} stock"
            
            response = self.news_client.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=min(count, 100)
            )
            
            if response['status'] == 'ok' and response['articles']:
                for article in response['articles']:
                    # Combine title and description for sentiment
                    text = f"{article.get('title', '')} {article.get('description', '')}"
                    if text.strip():
                        articles.append(text)
            
            logger.info(f"Fetched {len(articles)} news articles for {symbol}")
            return articles
        except Exception as e:
            logger.error(f"News API fetch error for {symbol}: {e}")
            return []
    

    def calculate_sentiment(self, texts: List[str]) -> Tuple[int, int, int, float]:
        """Calculate sentiment polarity for a list of texts"""
        positive = 0
        negative = 0
        neutral = 0
        total_polarity = 0.0
        
        for text in texts:
            cleaned = self.clean_text(text)
            if not cleaned:
                continue
            
            try:
                analysis = TextBlob(cleaned)
                polarity = analysis.sentiment.polarity
                total_polarity += polarity
                
                if polarity > 0.1:
                    positive += 1
                elif polarity < -0.1:
                    negative += 1
                else:
                    neutral += 1
            except Exception as e:
                logger.warning(f"Error analyzing sentiment: {e}")
                neutral += 1
        
        total_texts = positive + negative + neutral
        avg_polarity = total_polarity / total_texts if total_texts > 0 else 0.0
        
        return positive, negative, neutral, avg_polarity
    
    def analyze_sentiment(self, symbol: str, count_per_source: int = 50) -> Dict:
        """
        Analyze sentiment from all available sources
        
        Args:
            symbol: Stock symbol
            count_per_source: Number of items to fetch from each source
            
        Returns:
            Combined sentiment analysis results
        """
        if not self.is_enabled():
            raise ExternalAPIError("No sentiment sources are enabled")
        
        try:
            symbol = symbol.upper().strip()
            logger.info(f"Starting multi-source sentiment analysis for {symbol}")
            
            # Fetch content from all sources
            all_texts = []
            sources_used = []
            
            if self.twitter_enabled:
                tweets = self.fetch_twitter_content(symbol, count_per_source)
                all_texts.extend(tweets)
                if tweets:
                    sources_used.append('Twitter')
            
            if self.news_enabled:
                news = self.fetch_news_content(symbol, count_per_source)
                all_texts.extend(news)
                if news:
                    sources_used.append('News')
            
            if not all_texts:
                logger.warning(f"No content found for {symbol}")
                return {
                    'symbol': symbol,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total_items': 0,
                    'average_polarity': 0.0,
                    'sentiment': 'NEUTRAL',
                    'sources': sources_used,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Calculate combined sentiment
            positive, negative, neutral, avg_polarity = self.calculate_sentiment(all_texts)
            
            # Determine overall sentiment
            if positive > negative and positive > neutral:
                overall_sentiment = 'POSITIVE'
            elif negative > positive and negative > neutral:
                overall_sentiment = 'NEGATIVE'
            else:
                overall_sentiment = 'NEUTRAL'
            
            result = {
                'symbol': symbol,
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'total_items': len(all_texts),
                'average_polarity': round(avg_polarity, 4),
                'sentiment': overall_sentiment,
                'sources': sources_used,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Sentiment analysis completed for {symbol}: {overall_sentiment} from {sources_used}")
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {symbol}: {e}")
            raise ExternalAPIError(f"Sentiment analysis failed: {str(e)}")
    
    def get_cached_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get cached sentiment data if available and valid"""
        try:
            symbol = symbol.upper().strip()
            cache_entry = SentimentCache.query.filter_by(symbol=symbol).first()
            
            if cache_entry and self.is_cache_valid(cache_entry):
                logger.info(f"Using cached sentiment data for {symbol}")
                return {
                    'symbol': cache_entry.symbol,
                    'positive': cache_entry.positive_count,
                    'negative': cache_entry.negative_count,
                    'neutral': cache_entry.neutral_count,
                    'total_items': cache_entry.total_tweets,
                    'average_polarity': float(cache_entry.average_polarity),
                    'sentiment': cache_entry.overall_sentiment,
                    'timestamp': cache_entry.analyzed_at.isoformat(),
                    'cached': True
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached sentiment for {symbol}: {e}")
            return None
    
    def store_sentiment_cache(self, symbol: str, sentiment_data: Dict):
        """Store sentiment analysis results in cache"""
        try:
            symbol = symbol.upper().strip()
            cache_entry = SentimentCache.query.filter_by(symbol=symbol).first()
            
            if cache_entry:
                cache_entry.positive_count = sentiment_data['positive']
                cache_entry.negative_count = sentiment_data['negative']
                cache_entry.neutral_count = sentiment_data['neutral']
                cache_entry.total_tweets = sentiment_data['total_items']
                cache_entry.average_polarity = sentiment_data['average_polarity']
                cache_entry.overall_sentiment = sentiment_data['sentiment']
                cache_entry.analyzed_at = datetime.utcnow()
            else:
                cache_entry = SentimentCache(
                    symbol=symbol,
                    positive_count=sentiment_data['positive'],
                    negative_count=sentiment_data['negative'],
                    neutral_count=sentiment_data['neutral'],
                    total_tweets=sentiment_data['total_items'],
                    average_polarity=sentiment_data['average_polarity'],
                    overall_sentiment=sentiment_data['sentiment']
                )
                db.session.add(cache_entry)
            
            db.session.commit()
            logger.info(f"Sentiment data cached for {symbol}")
        except Exception as e:
            logger.error(f"Error storing sentiment cache for {symbol}: {e}")
            db.session.rollback()
    
    def is_cache_valid(self, cache_entry: SentimentCache, duration_hours: int = 1) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry or not cache_entry.analyzed_at:
            return False
        
        expiry_time = cache_entry.analyzed_at + timedelta(hours=duration_hours)
        return datetime.utcnow() < expiry_time
    
    def get_sentiment_with_cache(
        self,
        symbol: str,
        count_per_source: int = 50,
        cache_duration_hours: int = 1
    ) -> Dict:
        """Get sentiment analysis with caching support"""
        # Check cache first
        cached_data = self.get_cached_sentiment(symbol)
        if cached_data:
            cache_entry = SentimentCache.query.filter_by(symbol=symbol.upper()).first()
            if cache_entry and self.is_cache_valid(cache_entry, cache_duration_hours):
                return cached_data
        
        # Perform fresh analysis
        if not self.is_enabled():
            raise ExternalAPIError("No sentiment sources are enabled")
        
        sentiment_data = self.analyze_sentiment(symbol, count_per_source)
        self.store_sentiment_cache(symbol, sentiment_data)
        
        return sentiment_data
