"""
Sentiment Engine Service
Handles Twitter API integration and sentiment analysis for stock symbols
"""
import logging
import re
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Optional dependencies
TEXTBLOB_AVAILABLE = False
TWEEPY_AVAILABLE = False
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except Exception as _e:
    logging.getLogger(__name__).warning(f"TextBlob not available: {_e}")
try:
    import tweepy  # type: ignore
    TWEEPY_AVAILABLE = True
except Exception as _e:
    logging.getLogger(__name__).warning(f"tweepy not available: {_e}")

from app import db
from app.models.sentiment_cache import SentimentCache
from app.utils.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


class SentimentEngine:
    """Service for fetching tweets and analyzing sentiment"""
    
    def __init__(self):
        """Initialize the sentiment engine with Twitter API credentials"""
        self.api = None
        self.client = None
        self.enabled = False
        
        # Load Twitter API credentials from environment
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter API if credentials and dependencies are available
        if self._validate_credentials() and TWEEPY_AVAILABLE and TEXTBLOB_AVAILABLE:
            self._initialize_api()
        else:
            logger.warning("Sentiment analysis disabled (missing credentials or optional dependencies)")
    
    def _validate_credentials(self) -> bool:
        """
        Validate that required Twitter API credentials are present
        
        Returns:
            True if credentials are valid, False otherwise
        """
        # Check for v2 bearer token (preferred)
        if self.bearer_token:
            return True
        
        # Check for v1.1 credentials
        if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            return True
        
        return False
    
    def _initialize_api(self):
        """Initialize Twitter API client"""
        try:
            # Try to use Twitter API v2 with bearer token
            if self.bearer_token and TWEEPY_AVAILABLE:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                self.enabled = True
                logger.info("Twitter API v2 initialized successfully")
            
            # Fallback to v1.1 API
            elif all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]) and TWEEPY_AVAILABLE:
                auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                self.enabled = True
                logger.info("Twitter API v1.1 initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """
        Check if sentiment analysis is enabled
        
        Returns:
            True if Twitter API is configured and working
        """
        return self.enabled
    
    def fetch_tweets(self, symbol: str, count: int = 100) -> List[str]:
        """
        Fetch tweets mentioning the stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            count: Number of tweets to fetch (default: 100, max: 100)
            
        Returns:
            List of tweet texts
            
        Raises:
            ExternalAPIError: If Twitter API call fails
        """
        if not self.enabled:
            raise ExternalAPIError("Twitter API is not configured")
        
        try:
            tweets = []
            
            # Build search query
            query = f"${symbol} OR #{symbol} -is:retweet lang:en"
            
            # Use Twitter API v2 if available
            if self.client:
                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(count, 100),
                    tweet_fields=['created_at', 'public_metrics']
                )
                
                if response.data:
                    tweets = [tweet.text for tweet in response.data]
                    logger.info(f"Fetched {len(tweets)} tweets for {symbol} using API v2")
            
            # Fallback to API v1.1
            elif self.api:
                cursor = tweepy.Cursor(
                    self.api.search_tweets,
                    q=query,
                    lang='en',
                    result_type='recent',
                    tweet_mode='extended'
                )
                
                for tweet in cursor.items(min(count, 100)):
                    tweets.append(tweet.full_text)
                
                logger.info(f"Fetched {len(tweets)} tweets for {symbol} using API v1.1")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Twitter API error fetching tweets for {symbol}: {e}")
            raise ExternalAPIError(f"Failed to fetch tweets: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error fetching tweets for {symbol}: {e}")
            raise ExternalAPIError(f"Failed to fetch tweets: {str(e)}")
    
    def clean_tweet(self, text: str) -> str:
        """
        Clean tweet text by removing URLs, mentions, hashtags, and special characters
        
        Args:
            text: Raw tweet text
            
        Returns:
            Cleaned tweet text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags (keep the text, remove #)
        text = re.sub(r'#', '', text)
        
        # Remove special characters and emojis
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def calculate_polarity(self, tweets: List[str]) -> Tuple[int, int, int, float]:
        """
        Calculate sentiment polarity for a list of tweets
        
        Args:
            tweets: List of tweet texts
            
        Returns:
            Tuple of (positive_count, negative_count, neutral_count, average_polarity)
        """
        positive = 0
        negative = 0
        neutral = 0
        total_polarity = 0.0
        
        for tweet in tweets:
            # Clean the tweet
            cleaned = self.clean_tweet(tweet)
            
            if not cleaned:
                continue
            
            # Analyze sentiment using TextBlob
            try:
                analysis = TextBlob(cleaned)
                polarity = analysis.sentiment.polarity
                total_polarity += polarity
                
                # Classify sentiment
                if polarity > 0.1:
                    positive += 1
                elif polarity < -0.1:
                    negative += 1
                else:
                    neutral += 1
                    
            except Exception as e:
                logger.warning(f"Error analyzing tweet sentiment: {e}")
                neutral += 1
        
        # Calculate average polarity
        total_tweets = positive + negative + neutral
        avg_polarity = total_polarity / total_tweets if total_tweets > 0 else 0.0
        
        logger.info(f"Sentiment analysis: {positive} positive, {negative} negative, {neutral} neutral")
        
        return positive, negative, neutral, avg_polarity
    
    def analyze_sentiment(self, symbol: str, tweet_count: int = 100) -> Dict:
        """
        Fetch tweets and analyze sentiment for a stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            tweet_count: Number of tweets to analyze (default: 100)
            
        Returns:
            Dictionary with sentiment analysis results
            
        Raises:
            ExternalAPIError: If Twitter API call fails
        """
        if not self.enabled:
            raise ExternalAPIError("Sentiment analysis is not enabled. Twitter API credentials not configured.")
        
        try:
            symbol = symbol.upper().strip()
            logger.info(f"Starting sentiment analysis for {symbol}")
            
            # Fetch tweets
            tweets = self.fetch_tweets(symbol, tweet_count)
            
            if not tweets:
                logger.warning(f"No tweets found for {symbol}")
                return {
                    'symbol': symbol,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total_tweets': 0,
                    'average_polarity': 0.0,
                    'sentiment': 'NEUTRAL',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Calculate sentiment
            positive, negative, neutral, avg_polarity = self.calculate_polarity(tweets)
            
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
                'total_tweets': len(tweets),
                'average_polarity': round(avg_polarity, 4),
                'sentiment': overall_sentiment,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Sentiment analysis completed for {symbol}: {overall_sentiment}")
            return result
            
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {symbol}: {e}")
            raise ExternalAPIError(f"Sentiment analysis failed: {str(e)}")
    
    def get_cached_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Get cached sentiment data for a symbol if available and valid
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Cached sentiment data or None if not available/expired
        """
        try:
            symbol = symbol.upper().strip()
            
            # Query cache
            cache_entry = SentimentCache.query.filter_by(symbol=symbol).first()
            
            if cache_entry and self.is_cache_valid(cache_entry):
                logger.info(f"Using cached sentiment data for {symbol}")
                return {
                    'symbol': cache_entry.symbol,
                    'positive': cache_entry.positive_count,
                    'negative': cache_entry.negative_count,
                    'neutral': cache_entry.neutral_count,
                    'total_tweets': cache_entry.total_tweets,
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
        """
        Store sentiment analysis results in cache
        
        Args:
            symbol: Stock symbol
            sentiment_data: Sentiment analysis results
        """
        try:
            symbol = symbol.upper().strip()
            
            # Check if cache entry exists
            cache_entry = SentimentCache.query.filter_by(symbol=symbol).first()
            
            if cache_entry:
                # Update existing entry
                cache_entry.positive_count = sentiment_data['positive']
                cache_entry.negative_count = sentiment_data['negative']
                cache_entry.neutral_count = sentiment_data['neutral']
                cache_entry.total_tweets = sentiment_data['total_tweets']
                cache_entry.average_polarity = sentiment_data['average_polarity']
                cache_entry.overall_sentiment = sentiment_data['sentiment']
                cache_entry.analyzed_at = datetime.utcnow()
            else:
                # Create new entry
                cache_entry = SentimentCache(
                    symbol=symbol,
                    positive_count=sentiment_data['positive'],
                    negative_count=sentiment_data['negative'],
                    neutral_count=sentiment_data['neutral'],
                    total_tweets=sentiment_data['total_tweets'],
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
        """
        Check if a cache entry is still valid
        
        Args:
            cache_entry: SentimentCache database entry
            duration_hours: Cache validity duration in hours (default: 1)
            
        Returns:
            True if cache is still valid, False otherwise
        """
        if not cache_entry or not cache_entry.analyzed_at:
            return False
        
        expiry_time = cache_entry.analyzed_at + timedelta(hours=duration_hours)
        is_valid = datetime.utcnow() < expiry_time
        
        if not is_valid:
            logger.info(f"Cache expired for {cache_entry.symbol}")
        
        return is_valid
    
    def get_sentiment_with_cache(
        self, 
        symbol: str, 
        tweet_count: int = 100,
        cache_duration_hours: int = 1
    ) -> Dict:
        """
        Get sentiment analysis with caching support
        
        Args:
            symbol: Stock symbol
            tweet_count: Number of tweets to analyze if cache miss
            cache_duration_hours: Cache validity duration in hours
            
        Returns:
            Sentiment analysis results (from cache or fresh analysis)
        """
        # Check cache first
        cached_data = self.get_cached_sentiment(symbol)
        
        if cached_data:
            # Verify cache is still valid with custom duration
            cache_entry = SentimentCache.query.filter_by(symbol=symbol.upper()).first()
            if cache_entry and self.is_cache_valid(cache_entry, cache_duration_hours):
                return cached_data
        
        # Cache miss or expired - perform fresh analysis
        if not self.enabled:
            raise ExternalAPIError("Sentiment analysis is not enabled")
        
        sentiment_data = self.analyze_sentiment(symbol, tweet_count)
        
        # Store in cache
        self.store_sentiment_cache(symbol, sentiment_data)
        
        return sentiment_data
