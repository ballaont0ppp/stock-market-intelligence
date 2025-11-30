"""
LSTM Model Module
Implements the LSTM (Long Short-Term Memory) neural network model for stock price prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import logging
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

# Import our validation utilities
from ml_models.data_validation import validate_stock_data, print_dataframe_info

# Try to import TensorFlow/Keras
TENSORFLOW_AVAILABLE = False
TENSORFLOW_ERROR = None
KerasModels = None
KerasLayers = None

try:
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, LSTM
    TENSORFLOW_AVAILABLE = True
    KerasModels = Sequential
    KerasLayers = {'Dense': Dense, 'Dropout': Dropout, 'LSTM': LSTM}
except ImportError as e:
    TENSORFLOW_ERROR = str(e)
    logging.warning(f"TensorFlow/Keras not available: {TENSORFLOW_ERROR}")
    logging.warning("LSTM model will return None values")

class LSTMModel:
    """Class to implement LSTM model for stock price prediction"""
    
    def __init__(self, debug=False):
        """Initialize the LSTMModel
        
        Args:
            debug (bool): Enable debug logging
        """
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("LSTM Model cannot be used without TensorFlow/Keras")
            self.logger.error(f"Import error: {TENSORFLOW_ERROR}")
    
    def _get_close_column_data(self, df):
        """Safely extract Close column data with column name handling
        
        Args:
            df (pandas.DataFrame): Stock data
            
        Returns:
            tuple: (close_data, close_col_idx)
        """
        try:
            # Find Close column by name first
            if 'Close' in df.columns:
                close_col_idx = df.columns.get_loc('Close')
                close_data = df.iloc[:, close_col_idx:close_col_idx+1].values
                self.logger.debug(f"Found 'Close' column at index {close_col_idx}")
                return close_data, close_col_idx
            else:
                # Fallback to 4th column (index 4) for Close price
                if df.shape[1] > 4:
                    close_data = df.iloc[:, 4:5].values
                    self.logger.warning(f"'Close' column not found, using 4th column (index 4)")
                    return close_data, 4
                else:
                    raise ValueError(f"DataFrame has only {df.shape[1]} columns, need at least 5 for Close price")
        except Exception as e:
            raise ValueError(f"Could not extract Close price data: {str(e)}")
    
    def predict(self, df, sequence_length=7, epochs=5):
        """
        Make stock price predictions using LSTM model
        
        Args:
            df (pandas.DataFrame): Processed stock data
            sequence_length (int): Number of time steps for LSTM (default: 7)
            epochs (int): Number of training epochs (default: 5)
            
        Returns:
            tuple: (lstm_pred, error_lstm, success) - Prediction, RMSE error, success flag
        """
        try:
            if not TENSORFLOW_AVAILABLE:
                raise ImportError("TensorFlow/Keras not available. Please install: pip install tensorflow")
            
            if df is None or df.empty:
                raise ValueError("Input DataFrame is None or empty")
            
            # Validate input data
            is_valid, validation_errors = validate_stock_data(df, "LSTM", strict=False)
            if not is_valid:
                raise ValueError(f"Input data validation failed: {validation_errors}")
            
            if self.debug:
                print_dataframe_info(df, "LSTM Input")
            
            # Ensure we have enough data points
            min_required = sequence_length + 20  # Need sequence_length + some buffer
            if len(df) < min_required:
                raise ValueError(f"Insufficient data: need at least {min_required} rows, got {len(df)}")
            
            # Split data into training set and test set
            train_size = int(0.8 * len(df))
            if train_size < min_required:
                train_size = max(min_required, len(df) // 2)
            
            dataset_train = df.iloc[0:train_size, :]
            dataset_test = df.iloc[train_size:, :]
            
            # Extract Close price data safely
            try:
                training_set, close_col_idx = self._get_close_column_data(df)
                self.logger.debug(f"Using Close column at index {close_col_idx}")
            except Exception as e:
                raise ValueError(f"Failed to extract Close price data: {str(e)}")
            
            # Ensure we have enough points to build sequences
            if training_set.shape[0] < sequence_length + 10:
                raise ValueError(f"Insufficient data for sequence creation: {training_set.shape[0]} rows, need {sequence_length + 10}")
            
            # Feature Scaling
            sc = MinMaxScaler(feature_range=(0, 1))
            training_set_scaled = sc.fit_transform(training_set)
            
            # Creating data structure with sequence_length timesteps and 1 output
            X_train = []
            y_train = []
            
            for i in range(sequence_length, len(training_set_scaled)):
                X_train.append(training_set_scaled[i-sequence_length:i, 0])
                y_train.append(training_set_scaled[i, 0])
                
            # Convert lists to numpy arrays
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            if X_train.shape[0] == 0:
                raise ValueError("No training sequences could be created")
            
            # For forecasting, prepare the last sequence
            X_forecast = np.array(X_train[-1, 1:])
            X_forecast = np.append(X_forecast, y_train[-1])
            
            # Reshaping: Adding 3rd dimension
            X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
            X_forecast = np.reshape(X_forecast, (1, X_forecast.shape[0], 1))
            
           
 # Building LSTM model
            regressor = Sequential()
            
            # Add first LSTM layer
            regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
            regressor.add(Dropout(0.1))
            
            # Add 2nd LSTM layer
            regressor.add(LSTM(units=50, return_sequences=True))
            regressor.add(Dropout(0.1))
            
            # Add 3rd LSTM layer
            regressor.add(LSTM(units=50, return_sequences=True))
            regressor.add(Dropout(0.1))
            
            # Add 4th LSTM layer
            regressor.add(LSTM(units=50))
            regressor.add(Dropout(0.1))
            
            # Add output layer
            regressor.add(Dense(units=1))
            
            # Compile
            regressor.compile(optimizer='adam', loss='mean_squared_error')
            
            # Training
            self.logger.info(f"Training LSTM model for {epochs} epochs...")
            regressor.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=0)
            self.logger.info("LSTM training completed")
            
            # Testing
            real_stock_price = dataset_test.iloc[:, close_col_idx:close_col_idx+1].values
            
            # To predict, we need stock prices of sequence_length days before the test set
            dataset_total = pd.concat((dataset_train['Close'], dataset_test['Close']), axis=0)
            testing_set = dataset_total[len(dataset_total) - len(dataset_test) - sequence_length:].values
            testing_set = testing_set.reshape(-1, 1)
            
            if testing_set.shape[0] < sequence_length + 5:
                raise ValueError(f"Not enough points to form test sequences: {testing_set.shape[0]}")
            
            # Feature scaling
            testing_set = sc.transform(testing_set)
            
            # Create data structure
            X_test = []
            for i in range(sequence_length, len(testing_set)):
                X_test.append(testing_set[i-sequence_length:i, 0])
                
            # Convert list to numpy arrays
            X_test = np.array(X_test)
            
            # Reshaping: Adding 3rd dimension
            X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
            
            # Testing Prediction
            predicted_stock_price = regressor.predict(X_test)
            
            # Getting original prices back from scaled values
            predicted_stock_price = sc.inverse_transform(predicted_stock_price)
            
            # Calculate error
            if len(real_stock_price) > 0 and len(predicted_stock_price) > 0:
                error_lstm = math.sqrt(mean_squared_error(real_stock_price, predicted_stock_price))
            else:
                error_lstm = 0.0
            
            # Forecasting Prediction
            forecasted_stock_price = regressor.predict(X_forecast)
            
            # Getting original prices back from scaled values
            forecasted_stock_price = sc.inverse_transform(forecasted_stock_price)
            
            lstm_pred = forecasted_stock_price[0, 0]
            
            self.logger.info(f"LSTM prediction: {lstm_pred:.4f}")
            self.logger.info(f"LSTM RMSE: {error_lstm:.4f}")
            
            # Validate prediction
            if not np.isfinite(lstm_pred) or lstm_pred <= 0:
                self.logger.warning(f"LSTM prediction may be invalid: {lstm_pred}")
            
            return lstm_pred, error_lstm, True
            
        except Exception as e:
            error_msg = f"Error in LSTM prediction: {str(e)}"
            self.logger.error(error_msg)
            
            if self.debug:
                self.logger.debug(f"Input DataFrame shape: {df.shape if df is not None else 'None'}")
                self.logger.debug(f"Input columns: {df.columns.tolist() if df is not None else 'None'}")
                self.logger.debug(f"TensorFlow available: {TENSORFLOW_AVAILABLE}")
                if not TENSORFLOW_AVAILABLE:
                    self.logger.debug(f"TensorFlow error: {TENSORFLOW_ERROR}")
            
            # Return None values with error flag
            return None, None, False
    
    def is_available(self):
        """Check if LSTM model is available (TensorFlow is installed)
        
        Returns:
            bool: True if model can be used
        """
        return TENSORFLOW_AVAILABLE
    
    def get_model_info(self):
        """Get information about the LSTM model
        
        Returns:
            dict: Model information
        """
        return {
            'model_type': 'LSTM Neural Network',
            'available': TENSORFLOW_AVAILABLE,
            'tensorflow_error': TENSORFLOW_ERROR,
            'layers': ['LSTM(50)', 'Dropout(0.1)', 'LSTM(50)', 'Dropout(0.1)', 
                      'LSTM(50)', 'Dropout(0.1)', 'LSTM(50)', 'Dropout(0.1)', 'Dense(1)'],
            'optimizer': 'adam',
            'loss': 'mean_squared_error',
            'sequence_length': 7,
            'default_epochs': 5,
            'min_data_points': 30
        }
    
    def get_tensorflow_status(self):
        """Get detailed TensorFlow installation status
        
        Returns:
            dict: TensorFlow status information
        """
        return {
            'available': TENSORFLOW_AVAILABLE,
            'error': TENSORFLOW_ERROR,
            'recommendation': (
                "Install TensorFlow: pip install tensorflow" if not TENSORFLOW_AVAILABLE 
                else "TensorFlow is properly installed"
            )
        }
