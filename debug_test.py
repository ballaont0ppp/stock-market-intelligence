#!/usr/bin/env python3
"""
Debug Script for Stock Market Prediction Web App
Tests all components to identify potential issues
"""

import sys
import os
import logging
import traceback
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the debug script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    modules = [
        'pandas',
        'numpy', 
        'yfinance',
        'sklearn',
        'matplotlib',
        'statsmodels',
        'flask'
    ]
    
    optional_modules = [
        'tensorflow',
        'keras',
        'tweepy',
        'textblob',
        'preprocessor'
    ]
    
    results = {}
    
    # Test required modules
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
            results[module] = True
        except ImportError as e:
            print(f"[FAIL] {module}: {e}")
            results[module] = False
    
    # Test optional modules
    print("\nOptional Modules:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
            results[module] = True
        except ImportError as e:
            print(f"[SKIP] {module}: Not available")
            results[module] = False
    
    return results

def test_custom_modules():
    """Test if custom modules can be imported"""
    print("\n" + "=" * 60)
    print("TESTING CUSTOM MODULES")
    print("=" * 60)
    
    custom_modules = [
        'data_validation',
        'stock_data_processor',
        'arima_model',
        'lstm_model', 
        'linear_regression_model',
        'sentiment_analyzer'
    ]
    
    results = {}
    
    for module in custom_modules:
        try:
            mod = __import__(module)
            print(f"[OK] {module}")
            results[module] = mod
        except Exception as e:
            print(f"[FAIL] {module}: {e}")
            results[module] = None
    
    return results

def test_stock_data_processor(processor):
    """Test StockDataProcessor functionality"""
    print("\n" + "=" * 60)
    print("TESTING STOCK DATA PROCESSOR")
    print("=" * 60)
    
    try:
        # Test connection
        print("Testing yfinance connection...")
        connection_test = processor.test_connection()
        print(f"Connection test result: {connection_test}")
        
        if not connection_test['connection_ok']:
            print(f"[FAIL] Connection failed: {connection_test['error']}")
            return False
        
        # Test with a reliable symbol
        test_symbol = "AAPL"
        print(f"\nTesting data retrieval for {test_symbol}...")
        
        data = processor.get_historical_data(test_symbol)
        if data is None or data.empty:
            print("[FAIL] Failed to retrieve data")
            return False
        
        print(f"[OK] Retrieved {len(data)} data points")
        print(f"[OK] Data shape: {data.shape}")
        print(f"[OK] Columns: {data.columns.tolist()}")
        
        # Test preprocessing
        print(f"\nTesting preprocessing for {test_symbol}...")
        processed_data = processor.preprocess_data(data, test_symbol)
        if processed_data is None or processed_data.empty:
            print("[FAIL] Failed to preprocess data")
            return False
        
        print(f"[OK] Preprocessed data shape: {processed_data.shape}")
        print(f"[OK] Preprocessed columns: {processed_data.columns.tolist()}")
        
        # Test today's data extraction
        print(f"\nTesting today's data extraction for {test_symbol}...")
        today_data = processor.get_today_data(processed_data)
        if today_data is None or today_data.empty:
            print("[FAIL] Failed to extract today's data")
            return False
        
        print(f"[OK] Today's data shape: {today_data.shape}")
        print(f"[OK] Close price: {today_data.iloc[0]['Close']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Stock data processor test failed: {e}")
        traceback.print_exc()
        return False

def test_linear_regression_model(model, test_data):
    """Test LinearRegressionModel functionality"""
    print("\n" + "=" * 60)
    print("TESTING LINEAR REGRESSION MODEL")
    print("=" * 60)
    
    try:
        print("Testing Linear Regression prediction...")
        df, pred, forecast_set, mean, error, success = model.predict(test_data)
        
        if not success:
            print("[FAIL] Linear Regression prediction failed")
            return False
        
        print(f"[OK] Prediction successful: {pred:.4f}")
        print(f"[OK] RMSE Error: {error:.4f}")
        print(f"[OK] Mean forecast: {mean:.4f}")
        print(f"[OK] Forecast set shape: {forecast_set.shape}")
        
        # Test validation
        validation = model.validate_prediction(pred, forecast_set, error)
        print(f"[OK] Validation result: {validation['prediction_valid']}")
        if validation['warnings']:
            print(f"  Warnings: {validation['warnings']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Linear Regression model test failed: {e}")
        traceback.print_exc()
        return False

def test_lstm_model(model, test_data):
    """Test LSTMModel functionality"""
    print("\n" + "=" * 60)
    print("TESTING LSTM MODEL")
    print("=" * 60)
    
    try:
        # Check if model is available
        if not model.is_available():
            print("[SKIP] LSTM model not available (TensorFlow not installed)")
            return None  # None means not available, not failed
        
        print("Testing LSTM prediction...")
        pred, error, success = model.predict(test_data)
        
        if not success:
            print("[FAIL] LSTM prediction failed")
            return False
        
        print(f"[OK] Prediction successful: {pred:.4f}")
        print(f"[OK] RMSE Error: {error:.4f}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] LSTM model test failed: {e}")
        traceback.print_exc()
        return False

def test_arima_model(model, test_data):
    """Test ARIMAModel functionality"""
    print("\n" + "=" * 60)
    print("TESTING ARIMA MODEL")
    print("=" * 60)
    
    try:
        print("Testing ARIMA prediction...")
        pred, error, success = model.predict(test_data, "TEST")
        
        if not success:
            print("[FAIL] ARIMA prediction failed")
            return False
        
        print(f"[OK] Prediction successful: {pred:.4f}")
        print(f"[OK] RMSE Error: {error:.4f}")
        print(f"[OK] Model order: {model.order}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] ARIMA model test failed: {e}")
        traceback.print_exc()
        return False

def test_sentiment_analyzer(analyzer):
    """Test SentimentAnalyzer functionality"""
    print("\n" + "=" * 60)
    print("TESTING SENTIMENT ANALYZER")
    print("=" * 60)
    
    try:
        # Check API status
        api_status = analyzer.get_api_status()
        print(f"API Status: {api_status}")
        
        # Test with a sample symbol
        test_symbol = "AAPL"
        print(f"\nTesting sentiment analysis for {test_symbol}...")
        
        polarity, tweets, overall_sentiment, pos, neg, neutral, success, error = analyzer.retrieving_tweets_polarity(test_symbol)
        
        if not success:
            print(f"[FAIL] Sentiment analysis failed: {error}")
            return False
        
        print(f"[OK] Analysis successful")
        print(f"[OK] Global Polarity: {polarity:.4f}")
        print(f"[OK] Overall Sentiment: {overall_sentiment}")
        print(f"[OK] Positive: {pos}, Negative: {neg}, Neutral: {neutral}")
        print(f"[OK] Tweets analyzed: {len(tweets)}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Sentiment analyzer test failed: {e}")
        traceback.print_exc()
        return False

def create_test_data():
    """Create synthetic test data for models"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    print("\n" + "=" * 60)
    print("CREATING TEST DATA")
    print("=" * 60)
    
    try:
        # Create 100 days of synthetic stock data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Generate realistic-looking stock prices
        np.random.seed(42)
        trend = np.linspace(100, 120, 100)
        noise = np.random.randn(100) * 2
        close_prices = trend + noise
        
        test_df = pd.DataFrame({
            'Open': close_prices * 0.99,
            'High': close_prices * 1.02,
            'Low': close_prices * 0.98,
            'Close': close_prices,
            'Adj Close': close_prices,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        print(f"[OK] Created test data with {len(test_df)} rows")
        print(f"[OK] Date range: {dates[0]} to {dates[-1]}")
        print(f"[OK] Price range: ${close_prices.min():.2f} - ${close_prices.max():.2f}")
        
        return test_df
        
    except Exception as e:
        print(f"[FAIL] Failed to create test data: {e}")
        return None

def main():
    """Main testing function"""
    print("STOCK MARKET PREDICTION WEB APP - DEBUG SCRIPT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print("=" * 60)
    
    logger = setup_logging()
    
    # Test 1: Import all modules
    import_results = test_imports()
    
    # Check for critical missing modules
    critical_missing = [mod for mod, available in import_results.items() 
                       if not available and mod in ['pandas', 'numpy', 'yfinance', 'sklearn', 'matplotlib', 'statsmodels', 'flask']]
    
    if critical_missing:
        print(f"\nCRITICAL: Missing required modules: {critical_missing}")
        print("Please install missing modules and run again.")
        return
    
    # Test 2: Import custom modules
    custom_results = test_custom_modules()
    
    if not all(custom_results.values()):
        print("\nCRITICAL: Some custom modules failed to import")
        return
    
    # Test 3: Test individual components
    processor = None
    lr_model = None
    lstm_model = None
    arima_model = None
    sentiment_analyzer = None
    
    try:
        # Initialize components
        from stock_data_processor import StockDataProcessor
        from linear_regression_model import LinearRegressionModel
        from lstm_model import LSTMModel
        from arima_model import ARIMAModel
        from sentiment_analyzer import SentimentAnalyzer
        
        processor = StockDataProcessor(debug=True)
        lr_model = LinearRegressionModel(debug=True)
        lstm_model = LSTMModel(debug=True)
        arima_model = ARIMAModel(debug=True)
        sentiment_analyzer = SentimentAnalyzer(debug=True, use_api=False)
        
        print("\n[OK] All components initialized successfully")
        
    except Exception as e:
        print(f"\n[FAIL] Failed to initialize components: {e}")
        return
    
    # Test 4: Stock Data Processor
    data_success = test_stock_data_processor(processor)
    
    # Test 5: Create test data for models
    test_data = create_test_data()
    if test_data is None:
        print("\n[SKIP] Could not create test data, skipping model tests")
        return
    
    # Test 6: Linear Regression Model
    lr_success = test_linear_regression_model(lr_model, test_data)
    
    # Test 7: LSTM Model (might not be available)
    lstm_success = test_lstm_model(lstm_model, test_data)
    
    # Test 8: ARIMA Model
    arima_success = test_arima_model(arima_model, test_data)
    
    # Test 9: Sentiment Analyzer
    sentiment_success = test_sentiment_analyzer(sentiment_analyzer)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    results = {
        'Stock Data Processor': data_success,
        'Linear Regression Model': lr_success,
        'LSTM Model': lstm_success,
        'ARIMA Model': arima_success,
        'Sentiment Analyzer': sentiment_success
    }
    
    for component, success in results.items():
        if success is None:
            status = "NOT AVAILABLE"
        elif success:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"{component}: {status}")
    
    # Overall status
    failed_components = [comp for comp, success in results.items() if success is False]
    
    if not failed_components:
        print("\nALL TESTS PASSED! The application should work correctly.")
    else:
        print(f"\nFAILED COMPONENTS: {failed_components}")
        print("Please check the error messages above and fix the issues.")
    
    print(f"\nDebug script completed at {datetime.now()}")

if __name__ == "__main__":
    main()