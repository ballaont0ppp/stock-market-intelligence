"""
Script to check the status of all ML models
"""

import sys
import os

# Add the parent directory to the path to import the models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Add the ml_models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_models'))

from ml_models.lstm_model import LSTMModel
from ml_models.arima_model import ARIMAModel
from ml_models.linear_regression_model import LinearRegressionModel

def check_model_status():
    """Check the status of all models"""
    print("Checking ML Model Status")
    print("="*40)
    
    # Check LSTM Model
    print("LSTM Model:")
    lstm_model = LSTMModel()
    lstm_available = lstm_model.is_available()
    print(f"  Available: {lstm_available}")
    if not lstm_available:
        status = lstm_model.get_tensorflow_status()
        print(f"  Error: {status['error']}")
        print(f"  Recommendation: {status['recommendation']}")
    else:
        info = lstm_model.get_model_info()
        print(f"  Model Type: {info['model_type']}")
        print(f"  Layers: {info['layers']}")
    print()
    
    # Check ARIMA Model
    print("ARIMA Model:")
    arima_model = ARIMAModel()
    info = arima_model.get_model_info()
    print(f"  Available: True")
    print(f"  Model Type: {info['model_type']}")
    print(f"  Order: {info['order']}")
    print(f"  Min Data Points: {info['min_data_points']}")
    print()
    
    # Check Linear Regression Model
    print("Linear Regression Model:")
    lr_model = LinearRegressionModel()
    info = lr_model.get_model_info()
    print(f"  Available: True")
    print(f"  Model Type: {info['model_type']}")
    print(f"  Features: {info['features']}")
    print(f"  Min Data Points: {info['min_data_points']}")
    print()
    
    print("Summary:")
    print(f"  LSTM: {'Available' if lstm_available else 'Not Available (requires TensorFlow)'}")
    print("  ARIMA: Available")
    print("  Linear Regression: Available")

if __name__ == "__main__":
    check_model_status()