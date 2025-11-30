"""
Test file for models with real stock data
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

def load_real_data(file_path):
    """Load real stock data from CSV file"""
    try:
        # Load the CSV file without header
        df = pd.read_csv(file_path, header=None)
        print(f"Loaded {len(df)} rows from {file_path}")
        
        # Display basic info
        print(f"Raw data shape: {df.shape}")
        print(f"First few rows:")
        print(df.iloc[:5, :])
        
        # Extract the data starting from row 3 (index 3)
        data_rows = df.iloc[3:, :]
        
        # Create proper column names
        columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
        data_rows.columns = columns
        
        # Convert Date column to datetime
        data_rows['Date'] = pd.to_datetime(data_rows['Date'])
        
        # Convert numeric columns
        numeric_columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        for col in numeric_columns:
            data_rows[col] = pd.to_numeric(data_rows[col], errors='coerce')
        
        # Drop rows with NaN values
        data_rows = data_rows.dropna()
        
        # Reset index
        data_rows = data_rows.reset_index(drop=True)
        
        print(f"Processed data shape: {data_rows.shape}")
        print(f"Date range: {data_rows['Date'].min()} to {data_rows['Date'].max()}")
        print(f"Close price range: ${data_rows['Close'].min():.2f} to ${data_rows['Close'].max():.2f}")
        
        return data_rows
    except Exception as e:
        print(f"Error loading data from {file_path}: {str(e)}")
        return None

def test_models_with_real_data():
    """Test all models with real stock data"""
    print("Testing models with real stock data...")
    print("="*50)
    
    # Try to load Apple stock data
    data_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'AAPL.csv'
    )
    
    df = load_real_data(data_file)
    if df is None or len(df) == 0:
        print("Failed to load real data, exiting...")
        return False
    
    print("="*50)
    
    # Initialize models
    lstm_model = LSTMModel()
    arima_model = ARIMAModel()
    lr_model = LinearRegressionModel()
    
    # Test LSTM
    print("Testing LSTM Model with real data...")
    lstm_pred, lstm_error, lstm_success = None, None, False
    try:
        lstm_pred, lstm_error, lstm_success = lstm_model.predict(df)
        if lstm_success:
            print(f"LSTM Prediction: ${lstm_pred:.2f}")
            print(f"LSTM RMSE Error: {lstm_error:.2f}")
        else:
            print("LSTM Model not available (requires TensorFlow)")
    except Exception as e:
        print(f"LSTM Model failed with error: {str(e)}")
    print("-"*30)
    
    # Test ARIMA
    print("Testing ARIMA Model with real data...")
    arima_pred, arima_error, arima_success = None, None, False
    try:
        arima_pred, arima_error, arima_success = arima_model.predict(df, "AAPL")
        if arima_success:
            print(f"ARIMA Prediction: ${arima_pred:.2f}")
            print(f"ARIMA RMSE Error: {arima_error:.2f}")
        else:
            print("ARIMA Model failed to generate prediction")
    except Exception as e:
        print(f"ARIMA Model failed with error: {str(e)}")
    print("-"*30)
    
    # Test Linear Regression
    print("Testing Linear Regression Model with real data...")
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
    print("\nSUMMARY WITH REAL DATA")
    print("="*50)
    print(f"{'Model':<20} {'Prediction':<15} {'RMSE Error':<15} {'Status':<10}")
    print("-"*60)
    if lstm_success and lstm_pred is not None:
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
    print("Real data testing completed!")
    
    # At least one model should work
    return lstm_success or arima_success or lr_success

if __name__ == "__main__":
    success = test_models_with_real_data()
    if success:
        print("\nAt least one model worked with real data!")
    else:
        print("\nAll models failed with real data!")
    sys.exit(0 if success else 1)