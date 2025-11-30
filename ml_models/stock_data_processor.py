"""
Stock Data Processor Module
Handles retrieval and processing of stock market data from various sources
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
import warnings
warnings.filterwarnings("ignore")

# Import our validation utilities
from ml_models.data_validation import validate_stock_data, clean_stock_data, print_dataframe_info

class StockDataProcessor:
    """Class to handle stock data retrieval and processing"""
    
    def __init__(self, debug=False):
        """Initialize the StockDataProcessor
        
        Args:
            debug (bool): Enable debug logging
        """
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        
        # Store supported symbols cache
        self.supported_symbols = set()
        
    def is_valid_symbol(self, symbol):
        """Check if a stock symbol is valid
        
        Args:
            symbol (str): Stock symbol to validate
            
        Returns:
            bool: True if symbol appears to be valid
        """
        # Basic validation - alphanumeric and common characters
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Remove common prefixes/suffixes and validate
        clean_symbol = symbol.upper().replace('.', '').replace('-', '')
        
        # Basic length check (most stock symbols are 1-5 characters)
        if len(clean_symbol) < 1 or len(clean_symbol) > 10:
            return False
            
        # Check for valid characters
        if not clean_symbol.isalnum():
            return False
            
        return True
    
    def get_historical_data(self, symbol, period_years=2):
        """
        Retrieve historical stock data for a given symbol with robust error handling
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
            period_years (int): Number of years of historical data to retrieve (default: 2)
            
        Returns:
            pandas.DataFrame: Historical stock data with Date, Open, High, Low, Close, Adj Close, Volume
            or None if retrieval fails
        """
        try:
            # Validate symbol first
            if not self.is_valid_symbol(symbol):
                self.logger.error(f"Invalid stock symbol: {symbol}")
                return None
                
            # Calculate start and end dates
            end = datetime.now()
            start = datetime(end.year - period_years, end.month, end.day)
            
            if self.debug:
                self.logger.info(f"Fetching {period_years} years of data for {symbol} from {start.date()} to {end.date()}")
            
            # Download data using yfinance with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use yfinance download with progress disabled for cleaner output
                    data = yf.download(
                        symbol, 
                        start=start, 
                        end=end, 
                        progress=False,
                        timeout=30
                    )
                    
                    if data.empty:
                        if attempt == max_retries - 1:
                            self.logger.error(f"No data returned for symbol {symbol} after {max_retries} attempts")
                            return None
                        else:
                            self.logger.warning(f"No data for {symbol}, attempt {attempt + 1}/{max_retries}")
                            continue
                    
                    # yfinance returns a DataFrame directly, no need to convert
                    df = data.copy()
                    
                    # Handle MultiIndex columns (yfinance sometimes returns these for single symbols)
                    if isinstance(df.columns, pd.MultiIndex):
                        # Flatten the MultiIndex by taking the first level
                        df.columns = df.columns.get_level_values(0)
                    
                    # Ensure index is datetime
                    if not isinstance(df.index, pd.DatetimeIndex):
                        df.index = pd.to_datetime(df.index)
                    
                    # Validate the retrieved data
                    is_valid, validation_errors = validate_stock_data(df, symbol, strict=False)
                    if not is_valid:
                        self.logger.error(f"Data validation failed for {symbol}: {validation_errors}")
                        return None
                    
                    # Clean the data
                    df_clean = clean_stock_data(df)
                    
                    if df_clean.empty:
                        self.logger.error(f"Data cleaning resulted in empty DataFrame for {symbol}")
                        return None
                    
                    # Save to CSV file with error handling
                    csv_filename = f"{symbol}.csv"
                    try:
                        df_clean.to_csv(csv_filename)
                        self.logger.info(f"Historical data for {symbol} saved to {csv_filename} ({len(df_clean)} records)")
                    except Exception as e:
                        self.logger.warning(f"Could not save CSV for {symbol}: {e}")
                        # Don't fail the entire operation for CSV save issues
                    
                    if self.debug:
                        print_dataframe_info(df_clean, symbol)
                    
                    return df_clean
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"Failed to retrieve data for {symbol} after {max_retries} attempts: {str(e)}")
                        return None
                    else:
                        self.logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Unexpected error in get_historical_data for {symbol}: {str(e)}")
            return None
    
    def preprocess_data(self, df, symbol):
        """
        Preprocess the stock data for machine learning models with validation
        
        Args:
            df (pandas.DataFrame): Raw stock data
            symbol (str): Stock symbol
            
        Returns:
            pandas.DataFrame: Processed stock data or None if processing fails
        """
        try:
            if df is None or df.empty:
                self.logger.error(f"Cannot preprocess empty/None DataFrame for {symbol}")
                return None
            
            # Validate input data
            is_valid, validation_errors = validate_stock_data(df, symbol, strict=False)
            if not is_valid:
                self.logger.error(f"Input data validation failed for {symbol}: {validation_errors}")
                return None
            
            # Remove any rows with missing data
            original_length = len(df)
            df_clean = df.dropna()
            
            if len(df_clean) < original_length:
                removed_count = original_length - len(df_clean)
                self.logger.warning(f"Removed {removed_count} rows with missing data for {symbol}")
            
            if len(df_clean) == 0:
                self.logger.error(f"All data removed after cleaning for {symbol}")
                return None
            
            # Add a column for the stock symbol
            code_list = [symbol] * len(df_clean)
            df_code = pd.DataFrame(code_list, columns=['Code'])
            
            # Combine the code column with the stock data
            df_processed = pd.concat([df_code, df_clean], axis=1)
            
            self.logger.info(f"Data preprocessing completed for {symbol}: {len(df_processed)} records")
            
            if self.debug:
                print_dataframe_info(df_processed, f"{symbol}_processed")
            
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data for {symbol}: {str(e)}")
            return None
    
    def get_today_data(self, df):
        """
        Extract today's stock data from the DataFrame with robust error handling
        
        Args:
            df (pandas.DataFrame): Processed stock data
            
        Returns:
            pandas.DataFrame: Today's stock data or None if extraction fails
        """
        try:
            if df is None or df.empty:
                self.logger.error("Cannot extract today's data from empty/None DataFrame")
                return None
            
            if len(df) == 0:
                self.logger.error("Cannot extract today's data from empty DataFrame")
                return None
            
            # Get the last row (most recent data)
            today_stock = df.iloc[-1:]
            
            if self.debug:
                self.logger.debug(f"Today's stock data:\n{today_stock}")
            
            return today_stock
            
        except Exception as e:
            self.logger.error(f"Error extracting today's data: {str(e)}")
            return None
    
    def get_available_symbols(self):
        """
        Get list of commonly used stock symbols for testing
        
        Returns:
            list: List of popular stock symbols
        """
        return [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'DIS',
            'VZ', 'ADBE', 'CRM', 'INTC', 'CSCO', 'CMCSA', 'PEP', 'T', 'XOM'
        ]
    
    def test_connection(self):
        """
        Test the yfinance connection and data retrieval
        
        Returns:
            dict: Test results
        """
        test_results = {
            'connection_ok': False,
            'test_symbol': None,
            'data_points': 0,
            'error': None
        }
        
        try:
            # Test with a reliable symbol
            test_symbol = 'AAPL'
            test_data = yf.download(test_symbol, period="5d", progress=False)
            
            if not test_data.empty:
                test_results['connection_ok'] = True
                test_results['test_symbol'] = test_symbol
                test_results['data_points'] = len(test_data)
                self.logger.info(f"Connection test successful: {len(test_data)} data points for {test_symbol}")
            else:
                test_results['error'] = "No data returned for test symbol"
                
        except Exception as e:
            test_results['error'] = str(e)
            self.logger.error(f"Connection test failed: {e}")
        
        return test_results
