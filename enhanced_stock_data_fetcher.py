#!/usr/bin/env python3
"""
Enhanced Stock Data Fetcher
Advanced stock data fetching with robust yfinance integration, caching, rate limiting, and fallbacks
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
import warnings
import pickle
import hashlib
import json
import os
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

warnings.filterwarnings("ignore")


class RateLimiter:
    """Thread-safe rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = self.time_window - (now - oldest_call)
                if wait_time > 0:
                    logging.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
            
            self.calls.append(now)


class DataCache:
    """Persistent data cache with expiration and compression"""
    
    def __init__(self, cache_dir: str = "data_cache", default_ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self) -> None:
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, symbol: str, period: str, interval: str) -> str:
        """Generate cache key for data"""
        key_data = f"{symbol}_{period}_{interval}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def get(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """
        Get cached data if available and not expired
        
        Args:
            symbol: Stock symbol
            period: Data period
            interval: Data interval
            
        Returns:
            Cached DataFrame or None if not available/expired
        """
        cache_key = self._get_cache_key(symbol, period, interval)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if data has expired
            if time.time() - cached_data['timestamp'] > cached_data['ttl']:
                os.remove(cache_path)
                return None
            
            logging.debug(f"Cache hit for {symbol}_{period}_{interval}")
            return cached_data['data']
            
        except Exception as e:
            logging.warning(f"Error reading cache for {symbol}: {e}")
            # Remove corrupted cache file
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, symbol: str, period: str, interval: str, data: pd.DataFrame, ttl: Optional[int] = None) -> None:
        """
        Cache data with metadata
        
        Args:
            symbol: Stock symbol
            period: Data period
            interval: Data interval
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        cache_key = self._get_cache_key(symbol, period, interval)
        cache_path = self._get_cache_path(cache_path)
        
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl,
            'symbol': symbol,
            'period': period,
            'interval': interval
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            logging.debug(f"Cached data for {symbol}_{period}_{interval}")
        except Exception as e:
            logging.warning(f"Error caching data for {symbol}: {e}")
    
    def clear_expired(self) -> None:
        """Clear expired cache entries"""
        current_time = time.time()
        cleared_count = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                cache_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    if current_time - cached_data['timestamp'] > cached_data['ttl']:
                        os.remove(cache_path)
                        cleared_count += 1
                        
                except Exception:
                    # Remove corrupted cache files
                    os.remove(cache_path)
                    cleared_count += 1
        
        if cleared_count > 0:
            logging.info(f"Cleared {cleared_count} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = 0
        total_size = 0
        expired_files = 0
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                cache_path = os.path.join(self.cache_dir, filename)
                total_files += 1
                total_size += os.path.getsize(cache_path)
                
                try:
                    with open(cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    if current_time - cached_data['timestamp'] > cached_data['ttl']:
                        expired_files += 1
                except Exception:
                    expired_files += 1
        
        return {
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'expired_files': expired_files,
            'valid_files': total_files - expired_files
        }


def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator for retrying operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
            
            raise last_exception
        return wrapper
    return decorator


class EnhancedStockDataFetcher:
    """
    Advanced stock data fetcher with robust error handling, caching, and fallback mechanisms
    """
    
    def __init__(self, 
                 cache_enabled: bool = True,
                 rate_limit_calls: int = 60,
                 rate_limit_window: int = 60,
                 max_retries: int = 3,
                 timeout: int = 30,
                 cache_ttl: int = 3600):
        """
        Initialize the enhanced stock data fetcher
        
        Args:
            cache_enabled: Enable data caching
            rate_limit_calls: Maximum API calls per window
            rate_limit_window: Rate limit window in seconds
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_enabled = cache_enabled
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_window)
        
        # Initialize cache
        self.cache = DataCache(default_ttl=cache_ttl) if cache_enabled else None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Data source configurations
        self.data_sources = {
            'primary': 'yfinance',
            'fallbacks': ['alpha_vantage', 'iex_cloud', 'polygon']
        }
        
        # Setup HTTP session with retries
        self.session = self._setup_session()
        
        # Track API usage
        self.api_usage_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'cache_hits': 0
        }
    
    def _setup_session(self) -> requests.Session:
        """Setup HTTP session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _validate_symbol(self, symbol: str) -> bool:
        """
        Enhanced symbol validation
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol appears valid
        """
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Clean symbol
        clean_symbol = symbol.upper().strip()
        
        # Check for valid characters (alphanumeric, dots, hyphens, carets)
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-^')
        if not all(c in valid_chars for c in clean_symbol):
            return False
        
        # Length check
        if len(clean_symbol) < 1 or len(clean_symbol) > 10:
            return False
        
        # Check for reserved/suspicious patterns
        suspicious_patterns = ['123', 'TEST', 'FAKE', 'INVALID']
        if any(pattern in clean_symbol for pattern in suspicious_patterns):
            return False
        
        return True
    
    @retry_with_backoff(max_retries=3, backoff_factor=2.0)
    def _fetch_yfinance_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch data from yfinance with retry logic
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)
            
        Returns:
            DataFrame with stock data or None if failed
        """
        self.rate_limiter.wait_if_needed()
        self.api_usage_stats['total_calls'] += 1
        
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch data
            data = ticker.history(period=period, interval=interval, timeout=self.timeout)
            
            if data is None or data.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Data quality checks
            if len(data) == 0:
                raise ValueError("Empty data returned")
            
            # Check for too many missing values
            null_ratio = data[required_columns].isnull().sum().sum() / (len(data) * len(required_columns))
            if null_ratio > 0.1:  # More than 10% missing data
                raise ValueError(f"Too much missing data: {null_ratio:.2%}")
            
            self.api_usage_stats['successful_calls'] += 1
            self.logger.info(f"Successfully fetched {len(data)} records for {symbol} from yfinance")
            
            return data
            
        except Exception as e:
            self.api_usage_stats['failed_calls'] += 1
            self.logger.error(f"yfinance fetch failed for {symbol}: {e}")
            raise
    
    def _fetch_alpha_vantage_data(self, symbol: str, api_key: str) -> Optional[pd.DataFrame]:
        """
        Fetch data from Alpha Vantage as fallback
        
        Args:
            symbol: Stock symbol
            api_key: Alpha Vantage API key
            
        Returns:
            DataFrame or None if failed
        """
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': 'compact'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data:
                raise ValueError(data['Error Message'])
            
            if 'Time Series (Daily)' not in data:
                raise ValueError("No time series data in response")
            
            # Convert to DataFrame
            time_series = data['Time Series (Daily)']
            df_data = []
            
            for date, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(date),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            self.logger.info(f"Successfully fetched {len(df)} records for {symbol} from Alpha Vantage")
            return df
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage fetch failed for {symbol}: {e}")
            return None
    
    def _fetch_multiple_symbols_batch(self, symbols: List[str], period: str = "1y", 
                                    interval: str = "1d", max_workers: int = 5) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch data for multiple symbols concurrently
        
        Args:
            symbols: List of stock symbols
            period: Data period
            interval: Data interval
            max_workers: Maximum number of concurrent workers
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.get_historical_data, symbol, period, interval): symbol 
                for symbol in symbols
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    self.logger.error(f"Failed to fetch data for {symbol}: {e}")
                    results[symbol] = None
        
        return results
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d", 
                          use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Get historical stock data with comprehensive error handling and caching
        
        Args:
            symbol: Stock symbol
            period: Data period
            interval: Data interval
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with stock data or None if all sources fail
        """
        # Validate symbol
        if not self._validate_symbol(symbol):
            self.logger.error(f"Invalid symbol: {symbol}")
            return None
        
        # Check cache first
        if use_cache and self.cache:
            cached_data = self.cache.get(symbol, period, interval)
            if cached_data is not None:
                self.api_usage_stats['cache_hits'] += 1
                self.logger.info(f"Returning cached data for {symbol}")
                return cached_data
        
        # Try primary source (yfinance)
        try:
            data = self._fetch_yfinance_data(symbol, period, interval)
            
            if data is not None and use_cache and self.cache:
                self.cache.set(symbol, period, interval, data)
            
            return data
            
        except Exception as e:
            self.logger.warning(f"Primary data source failed for {symbol}: {e}")
            
            # Try fallback sources
            return self._try_fallback_sources(symbol, period, interval)
    
    def _try_fallback_sources(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """
        Try fallback data sources
        
        Args:
            symbol: Stock symbol
            period: Data period
            interval: Data interval
            
        Returns:
            DataFrame or None if all fallbacks fail
        """
        # Example: Try Alpha Vantage if API key is available
        alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if alpha_vantage_key:
            self.logger.info(f"Trying Alpha Vantage fallback for {symbol}")
            data = self._fetch_alpha_vantage_data(symbol, alpha_vantage_key)
            if data is not None:
                return data
        
        # Add more fallback sources as needed
        self.logger.error(f"All data sources failed for {symbol}")
        return None
    
    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time stock data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with real-time data or None if failed
        """
        if not self._validate_symbol(symbol):
            return None
        
        try:
            self.rate_limiter.wait_if_needed()
            ticker = yf.Ticker(symbol)
            
            # Get real-time data
            info = ticker.info
            fast_info = ticker.fast_info
            
            real_time_data = {
                'symbol': symbol,
                'current_price': fast_info.get('last_price'),
                'previous_close': info.get('previousClose'),
                'open': info.get('open'),
                'day_high': fast_info.get('day_high'),
                'day_low': fast_info.get('day_low'),
                'volume': fast_info.get('last_volume'),
                'market_cap': info.get('marketCap'),
                'timestamp': datetime.now().isoformat()
            }
            
            return real_time_data
            
        except Exception as e:
            self.logger.error(f"Failed to get real-time data for {symbol}: {e}")
            return None
    
    def get_multiple_symbols_data(self, symbols: List[str], period: str = "1y", 
                                interval: str = "1d", use_cache: bool = True) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Get historical data for multiple symbols efficiently
        
        Args:
            symbols: List of stock symbols
            period: Data period
            interval: Data interval
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        valid_symbols = [symbol for symbol in symbols if self._validate_symbol(symbol)]
        if not valid_symbols:
            self.logger.error("No valid symbols provided")
            return {}
        
        return self._fetch_multiple_symbols_batch(valid_symbols, period, interval)
    
    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """
        Clear cache entries
        
        Args:
            symbol: Specific symbol to clear, None to clear all
        """
        if not self.cache:
            return
        
        if symbol:
            # Clear specific symbol cache
            for period in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]:
                for interval in ["1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"]:
                    cache_key = self.cache._get_cache_key(symbol, period, interval)
                    cache_path = self.cache._get_cache_path(cache_key)
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
            self.logger.info(f"Cleared cache for {symbol}")
        else:
            # Clear all cache
            for filename in os.listdir(self.cache.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache.cache_dir, filename))
            self.logger.info("Cleared all cache")
    
    def get_api_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        cache_stats = self.cache.get_cache_stats() if self.cache else {}
        
        return {
            **self.api_usage_stats,
            'cache_statistics': cache_stats,
            'success_rate': (
                self.api_usage_stats['successful_calls'] / 
                max(self.api_usage_stats['total_calls'], 1)
            )
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test data source connections
        
        Returns:
            Dictionary with test results
        """
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'yfinance': {'status': 'unknown', 'error': None},
            'cache': {'status': 'unknown', 'error': None},
            'overall': 'unknown'
        }
        
        # Test yfinance
        try:
            test_data = self._fetch_yfinance_data('AAPL', period="5d")
            if test_data is not None and len(test_data) > 0:
                test_results['yfinance']['status'] = 'ok'
            else:
                test_results['yfinance']['status'] = 'no_data'
        except Exception as e:
            test_results['yfinance']['status'] = 'error'
            test_results['yfinance']['error'] = str(e)
        
        # Test cache
        if self.cache:
            try:
                cache_stats = self.cache.get_cache_stats()
                test_results['cache']['status'] = 'ok'
                test_results['cache']['stats'] = cache_stats
            except Exception as e:
                test_results['cache']['status'] = 'error'
                test_results['cache']['error'] = str(e)
        
        # Overall status
        if test_results['yfinance']['status'] == 'ok':
            test_results['overall'] = 'ok'
        elif test_results['yfinance']['status'] == 'error':
            test_results['overall'] = 'degraded'
        else:
            test_results['overall'] = 'failed'
        
        return test_results


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize enhanced fetcher
    fetcher = EnhancedStockDataFetcher(
        cache_enabled=True,
        rate_limit_calls=30,
        rate_limit_window=60,
        max_retries=3,
        timeout=30
    )
    
    # Test connection
    print("Testing data source connections...")
    connection_test = fetcher.test_connection()
    print(f"Connection test results: {json.dumps(connection_test, indent=2)}")
    
    # Test single symbol
    print("\nTesting single symbol fetch...")
    symbol = "AAPL"
    data = fetcher.get_historical_data(symbol, period="1mo")
    
    if data is not None:
        print(f"Successfully fetched {len(data)} records for {symbol}")
        print(f"Data range: {data.index.min()} to {data.index.max()}")
        print(f"Columns: {list(data.columns)}")
    else:
        print(f"Failed to fetch data for {symbol}")
    
    # Test multiple symbols
    print("\nTesting multiple symbols fetch...")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    multi_data = fetcher.get_multiple_symbols_data(symbols, period="5d")
    
    for sym, data in multi_data.items():
        if data is not None:
            print(f"{sym}: {len(data)} records")
        else:
            print(f"{sym}: Failed to fetch")
    
    # Get API usage stats
    print("\nAPI Usage Statistics:")
    stats = fetcher.get_api_usage_stats()
    print(json.dumps(stats, indent=2))
    
    print("\nTest completed successfully!")