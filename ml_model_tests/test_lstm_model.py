"""
Test file for LSTM model
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the parent directory to the path to import the model
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Add the ml_models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))

from ml_models.lstm_model import LSTMModel

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

def test_lstm_model():
    """Test the LSTM model with sample data"""
    print("Testing LSTM Model...")
    
    # Create sample data
    df = create_sample_data()
    print(f"Sample data created with {len(df)} rows")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Price range: ${df['Close'].min():.2f} to ${df['Close'].max():.2f}")
    
    # Initialize LSTM model
    lstm_model = LSTMModel()
    
    # Check if TensorFlow is available
    if not lstm_model.is_available():
        print("LSTM Model test SKIPPED - TensorFlow not available")
        print("To enable LSTM model, install TensorFlow: pip install tensorflow")
        return True  # Not a failure, just skipped
    
    # Test prediction
    try:
        prediction, error, success = lstm_model.predict(df)
        print(f"LSTM Prediction: {prediction}")
        print(f"LSTM RMSE Error: {error}")
        print(f"LSTM Success: {success}")
        
        # Check if we got valid results
        if success and prediction is not None and not np.isnan(prediction) and prediction > 0:
            print("LSTM Model test PASSED")
            return True
        else:
            print("LSTM Model test FAILED - No valid prediction generated")
            return False
    except Exception as e:
        print(f"LSTM Model test FAILED with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_lstm_model()
    if success:
        print("\nLSTM Model test completed successfully!")
    else:
        print("\nLSTM Model test failed!")
    sys.exit(0 if success else 1)