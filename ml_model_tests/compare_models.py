"""
Script to compare all models side-by-side
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the parent directory to the path to import the models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Add the ml_models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))

from ml_models.lstm_model import LSTMModel
from ml_models.arima_model import ARIMAModel
from ml_models.linear_regression_model import LinearRegressionModel

def create_sample_data():
    """Create sample stock data for testing"""
    # Create a date range
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    
    # Create sample stock data with some realistic patterns
    np.random.seed(42)  # For reproducible results
    base_price = 100
    trend = 0.05  # 5% upward trend
    prices = []
    
    for i in range(100):
        # Add trend, some noise, and occasional larger movements
        price_change = trend + np.random.normal(0, 0.02) + 0.1 * np.sin(i/10)
        if i > 0:
            new_price = prices[-1] * (1 + price_change)
        else:
            new_price = base_price * (1 + price_change)
        prices.append(new_price)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Open': [price * (1 + np.random.normal(0, 0.01)) for price in prices],
        'High': [price * (1 + abs(np.random.normal(0, 0.02))) for price in prices],
        'Low': [price * (1 - abs(np.random.normal(0, 0.02))) for price in prices],
        'Close': prices,
        'Volume': [np.random.randint(1000000, 5000000) for _ in range(100)]
    })
    
    return df

def compare_models():
    """Compare all models side-by-side"""
    print("Comparing all models...")
    print("="*50)
    
    # Create sample data
    df = create_sample_data()
    print(f"Sample data created with {len(df)} rows")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Price range: ${df['Close'].min():.2f} to ${df['Close'].max():.2f}")
    print("="*50)
    
    # Initialize models
    lstm_model = LSTMModel()
    arima_model = ARIMAModel()
    lr_model = LinearRegressionModel()
    
    # Test LSTM
    print("Testing LSTM Model...")
    lstm_pred, lstm_error, lstm_success = None, None, False
    try:
        if lstm_model.is_available():
            lstm_pred, lstm_error, lstm_success = lstm_model.predict(df)
            if lstm_success:
                print(f"LSTM Prediction: ${lstm_pred:.2f}")
                print(f"LSTM RMSE Error: {lstm_error:.2f}")
            else:
                print("LSTM Model failed to generate prediction")
        else:
            print("LSTM Model not available (requires TensorFlow)")
    except Exception as e:
        print(f"LSTM Model failed with error: {str(e)}")
    print("-"*30)
    
    # Test ARIMA
    print("Testing ARIMA Model...")
    arima_pred, arima_error, arima_success = None, None, False
    try:
        arima_pred, arima_error, arima_success = arima_model.predict(df, "TEST")
        if arima_success:
            print(f"ARIMA Prediction: ${arima_pred:.2f}")
            print(f"ARIMA RMSE Error: {arima_error:.2f}")
        else:
            print("ARIMA Model failed to generate prediction")
    except Exception as e:
        print(f"ARIMA Model failed with error: {str(e)}")
    print("-"*30)
    
    # Test Linear Regression
    print("Testing Linear Regression Model...")
    lr_pred, lr_error, lr_success = None, None, False
    try:
        df_result, lr_pred, forecast_set, mean, lr_error, lr_success = lr_model.predict(df)
        if lr_success:
            print(f"Linear Regression Prediction: ${lr_pred:.2f}")
            print(f"Linear Regression RMSE Error: {lr_error:.2f}")
            print(f"Mean Forecast: ${mean:.2f}")
        else:
            print("Linear Regression Model failed to generate prediction")
    except Exception as e:
        print(f"Linear Regression Model failed with error: {str(e)}")
    print("-"*30)
    
    # Summary
    print("\nSUMMARY")
    print("="*50)
    print(f"{'Model':<20} {'Prediction':<15} {'RMSE Error':<15} {'Status':<10}")
    print("-"*60)
    if lstm_model.is_available() and lstm_success and lstm_pred is not None:
        print(f"{'LSTM':<20} ${lstm_pred:<14.2f} {lstm_error:<15.2f} {'PASSED':<10}")
    else:
        print(f"{'LSTM':<20} {'N/A':<15} {'N/A':<15} {'SKIPPED':<10}")
        
    if arima_success and arima_pred is not None:
        print(f"{'ARIMA':<20} ${arima_pred:<14.2f} {arima_error:<15.2f} {'PASSED':<10}")
    else:
        print(f"{'ARIMA':<20} {'N/A':<15} {'N/A':<15} {'FAILED':<10}")
        
    if lr_success and lr_pred is not None:
        print(f"{'Linear Regression':<20} ${lr_pred:<14.2f} {lr_error:<15.2f} {'PASSED':<10}")
    else:
        print(f"{'Linear Regression':<20} {'N/A':<15} {'N/A':<15} {'FAILED':<10}")
    
    print("="*60)
    print("Comparison completed!")

if __name__ == "__main__":
    compare_models()