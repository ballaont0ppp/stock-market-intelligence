"""
Sentiment Analyzer Module
Implements sentiment analysis of tweets for stock market prediction
"""

import pandas as pd
import re
import logging
import warnings
warnings.filterwarnings("ignore")

try:
    import tweepy
    TWITTER_API_AVAILABLE = True
except ImportError:
    TWITTER_API_AVAILABLE = False
    logging.warning("Twitter API (tweepy) not available - sentiment analysis will use demo mode")

try:
    import preprocessor as p
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    class _DummyPreprocessor:
        @staticmethod
        def clean(text):
            return text
    p = _DummyPreprocessor()
    PREPROCESSOR_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available - sentiment analysis will be limited")

import matplotlib.pyplot as plt
from constants import consumer_key, consumer_secret, access_token, access_token_secret, num_of_tweets

# Import our validation utilities
from data_validation import print_dataframe_info

class SentimentAnalyzer:
    """Class to implement sentiment analysis of tweets"""
    
    def __init__(self, debug=False, use_api=True):
        """Initialize the SentimentAnalyzer
        
        Args:
            debug (bool): Enable debug logging
            use_api (bool): Whether to attempt Twitter API access
        """
        self.debug = debug
        self.use_api = use_api
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Twitter API configuration
        self.api_available = False
        self.api_error = None
        
        # Check if we can initialize the API
        if self.use_api:
            self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Twitter API connection with error handling"""
        try:
            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                self.api_error = "Twitter API credentials not properly configured"
                self.logger.warning(self.api_error)
                return
            
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            
            # Test the connection
            user = tweepy.API(auth, wait_on_rate_limit=True)
            user.verify_credentials()
            
            self.api_available = True
            self.logger.info("Twitter API initialized successfully")
            
        except Exception as e:
            self.api_error = str(e)
            self.api_available = False
            self.logger.warning(f"Twitter API initialization failed: {self.api_error}")
            self.logger.info("Sentiment analysis will run in demo mode")
    
    def _map_symbol_to_company(self, symbol):
        """Map stock ticker to company name for search
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            str: Company name for search
        """
        # Simple mapping for common stocks
        symbol_to_company = {
            'AAPL': 'Apple',
            'GOOGL': 'Google',
            'GOOG': 'Google',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'META': 'Meta',
            'FB': 'Facebook',
            'NVDA': 'NVIDIA',
            'NFLX': 'Netflix',
            'JPM': 'JPMorgan',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa',
            'PG': 'Procter & Gamble',
            'UNH': 'UnitedHealth',
            'HD': 'Home Depot',
            'MA': 'Mastercard',
            'BAC': 'Bank of America',
            'DIS': 'Disney',
            'VZ': 'Verizon',
            'ADBE': 'Adobe',
            'CRM': 'Salesforce',
            'INTC': 'Intel',
            'CSCO': 'Cisco',
            'CMCSA': 'Comcast',
            'PEP': 'PepsiCo',
            'T': 'AT&T',
            'XOM': 'ExxonMobil'
        }
        
        return symbol_to_company.get(symbol.upper(), symbol)
    
    def _clean_tweet(self, tweet_text):
        """Clean tweet text for sentiment analysis
        
        Args:
            tweet_text (str): Raw tweet text
            
        Returns:
            str: Cleaned tweet text
        """
        try:
            # Clean using tweet preprocessor
            cleaned = p.clean(tweet_text)
            
            # Replace & by &
            cleaned = re.sub('&', '&', cleaned)
            
            # Remove colons
            cleaned = re.sub(':', '', cleaned)
            
            # Remove Emojis and Hindi Characters
            cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
            
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            
            return cleaned
        except Exception as e:
            self.logger.warning(f"Error cleaning tweet: {e}")
            return tweet_text  # Return original if cleaning fails
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of a text using TextBlob
        
        Args:
            text (str): Text to analyze
            
        Returns:
            float: Polarity score (-1 to 1)
        """
        try:
            if not TEXTBLOB_AVAILABLE:
                # Fallback: simple keyword-based sentiment
                positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'win', 'profit', 'gain', 'bull', 'rise', 'up', 'positive']
                negative_words = ['bad', 'terrible', 'awful', 'hate', 'lose', 'loss', 'bear', 'fall', 'down', 'negative', 'crash', 'drop']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    return 0.5
                elif neg_count > pos_count:
                    return -0.5
                else:
                    return 0.0
            
            blob = TextBlob(text)
            return blob.sentiment.polarity
            
        except Exception as e:
            self.logger.warning(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def retrieving_tweets_polarity(self, symbol):
        """
        Retrieve and analyze sentiment of tweets for a given stock symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            tuple: (global_polarity, tw_list, tw_pol, pos, neg, neutral, success, error_msg)
        """
        try:
            if not self.api_available:
                # Return demo mode results
                self.logger.info(f"Running sentiment analysis in demo mode for {symbol}")
                return self._demo_sentiment_analysis(symbol)
            
            # Map symbol to company name
            company_name = self._map_symbol_to_company(symbol)
            
            # Retrieve tweets
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            user = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Search for tweets
            tweets = tweepy.Cursor(
                user.search_tweets, 
                q=company_name, 
                tweet_mode='extended', 
                lang='en', 
                exclude_replies=True
            ).items(num_of_tweets)
            
            tweet_list = []
            global_polarity = 0
            tw_list = []
            pos = 0
            neg = 0
            
            tweet_count = 0
            for tweet in tweets:
                try:
                    count = 20  # Number of tweets to display
                    if count <= 0:
                        break
                    
                    # Get full text
                    tw2 = tweet.full_text
                    tw = tweet.full_text
                    
                    # Clean the tweet
                    tw = self._clean_tweet(tw)
                    
                    # Analyze sentiment
                    polarity = self._analyze_sentiment(tw)
                    
                    # Classify as positive, negative, or neutral
                    if polarity > 0:
                        pos += 1
                    elif polarity < 0:
                        neg += 1
                    
                    global_polarity += polarity
                    tw_list.append(tw2)
                    tweet_list.append({'text': tw, 'polarity': polarity})
                    
                    tweet_count += 1
                    count -= 1
                    
                except Exception as e:
                    self.logger.warning(f"Error processing tweet: {e}")
                    continue
            
            if len(tweet_list) > 0:
                global_polarity = global_polarity / len(tweet_list)
            else:
                global_polarity = 0
            
            neutral = num_of_tweets - pos - neg
            if neutral < 0:
                neg += neutral
                neutral = num_of_tweets
            
            # Create sentiment pie chart
            try:
                self._create_sentiment_plot(pos, neg, neutral, symbol)
            except Exception as e:
                self.logger.warning(f"Could not create sentiment plot: {e}")
            
            # Determine overall sentiment
            if global_polarity > 0:
                tw_pol = "Overall Positive"
            elif global_polarity < 0:
                tw_pol = "Overall Negative"
            else:
                tw_pol = "Neutral"
            
            self.logger.info(f"Sentiment analysis completed for {symbol}: {tweet_count} tweets processed")
            self.logger.info(f"Positive: {pos}, Negative: {neg}, Neutral: {neutral}")
            
            return global_polarity, tw_list, tw_pol, pos, neg, neutral, True, None
            
        except Exception as e:
            error_msg = f"Error in sentiment analysis for {symbol}: {str(e)}"
            self.logger.error(error_msg)
            
            # Fallback to demo mode
            self.logger.info("Falling back to demo mode sentiment analysis")
            return self._demo_sentiment_analysis(symbol)
    
    def _demo_sentiment_analysis(self, symbol):
        """Provide demo sentiment analysis when API is not available
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            tuple: Demo sentiment results
        """
        try:
            # Generate demo tweets based on symbol
            company_name = self._map_symbol_to_company(symbol)
            
            demo_tweets = [
                f"{company_name} stock looking strong today!",
                f"Great quarter for {company_name}!",
                f"{company_name} continues to innovate",
                f"Watching {company_name} for potential breakout",
                f"{company_name} earnings coming up - excited!",
                f"Good fundamentals for {company_name}",
                f"{company_name} shows promise",
                f"Positive outlook for {company_name}",
                f"{company_name} building momentum",
                f"${symbol} forming a nice pattern"
            ]
            
            # Analyze demo tweets
            polarities = [self._analyze_sentiment(tweet) for tweet in demo_tweets]
            global_polarity = sum(polarities) / len(polarities) if polarities else 0
            
            # Classify sentiments
            pos = sum(1 for p in polarities if p > 0)
            neg = sum(1 for p in polarities if p < 0)
            neutral = len(polarities) - pos - neg
            
            # Determine overall sentiment
            if global_polarity > 0.1:
                tw_pol = "Overall Positive (Demo Mode)"
            elif global_polarity < -0.1:
                tw_pol = "Overall Negative (Demo Mode)"
            else:
                tw_pol = "Neutral (Demo Mode)"
            
            self.logger.info(f"Demo sentiment analysis for {symbol}: {global_polarity:.3f}")
            
            return global_polarity, demo_tweets, tw_pol, pos, neg, neutral, True, "Demo Mode"
            
        except Exception as e:
            self.logger.error(f"Demo sentiment analysis failed: {e}")
            return 0.0, [], "Analysis Error", 0, 0, 0, False, str(e)
    
    def _create_sentiment_plot(self, pos, neg, neutral, symbol):
        """Create sentiment analysis pie chart
        
        Args:
            pos (int): Positive tweet count
            neg (int): Negative tweet count
            neutral (int): Neutral tweet count
            symbol (str): Stock symbol
        """
        try:
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [pos, neg, neutral]
            explode = (0, 0, 0)
            colors = ['#28a745', '#dc3545', '#6c757d']
            
            fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=65)
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title(f'{symbol} - Sentiment Analysis')
            ax.axis('equal')
            plt.tight_layout()
            plt.savefig('static/SA.png', dpi=65, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Sentiment analysis plot saved to static/SA.png")
            
        except Exception as e:
            self.logger.warning(f"Could not create sentiment plot: {e}")
            plt.close()
    
    def get_api_status(self):
        """Get Twitter API status information
        
        Returns:
            dict: API status information
        """
        return {
            'api_available': self.api_available,
            'api_error': self.api_error,
            'textblob_available': TEXTBLOB_AVAILABLE,
            'credentials_configured': all([consumer_key, consumer_secret, access_token, access_token_secret]),
            'mode': 'Live API' if self.api_available else 'Demo Mode'
        }
    
    def get_model_info(self):
        """Get information about the sentiment analyzer
        
        Returns:
            dict: Model information
        """
        return {
            'model_type': 'Sentiment Analysis',
            'api_status': self.get_api_status(),
            'max_tweets': num_of_tweets,
            'display_tweets': 20,
            'sentiment_range': '(-1 to 1)',
            'preprocessing': 'Tweet cleaning and text normalization',
            'fallback': 'Keyword-based sentiment when TextBlob unavailable'
        }

# Example usage and testing
if __name__ == "__main__":
    print("Testing Sentiment Analyzer...")
    
    # Test API status
    analyzer = SentimentAnalyzer(debug=True)
    api_status = analyzer.get_api_status()
    print(f"API Status: {api_status}")
    
    # Test with a sample symbol
    test_symbol = "AAPL"
    print(f"\nTesting sentiment analysis for {test_symbol}...")
    
    try:
        polarity, tweets, overall_sentiment, pos, neg, neutral, success, error = analyzer.retrieving_tweets_polarity(test_symbol)
        
        print(f"\n=== SENTIMENT ANALYSIS RESULTS ===")
        print(f"Success: {success}")
        if success:
            print(f"Global Polarity: {polarity:.4f}")
            print(f"Overall Sentiment: {overall_sentiment}")
            print(f"Positive: {pos}, Negative: {neg}, Neutral: {neutral}")
            print(f"Tweets analyzed: {len(tweets)}")
            if len(tweets) > 0:
                print(f"Sample tweets: {tweets[:3]}")  # Show first 3 tweets
        else:
            print(f"Analysis failed: {error}")
            
    except Exception as e:
        print(f"Test failed: {e}")
    
    # Test model info
    print(f"\nModel Info: {analyzer.get_model_info()}")