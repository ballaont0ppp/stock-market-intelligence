"""
Linear Regression Model Module
Implements the Linear Regression model for stock price prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import logging
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

# Import our validation utilities
from data_validation import validate_stock_data, print_dataframe_info

class LinearRegressionModel:
    """Class to implement Linear Regression model for stock price prediction"""
    
    def __init__(self, debug=False):
        """Initialize the LinearRegressionModel
        
        Args:
            debug (bool): Enable debug logging
        """
        self.debug = debug
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def predict(self, df, forecast_days=7):
        """
        Make stock price predictions using Linear Regression model
        
        Args:
            df (pandas.DataFrame): Processed stock data
            forecast_days (int): Number of days to forecast ahead (default: 7)
            
        Returns:
            tuple: (df, lr_pred, forecast_set, mean, error_lr, success) - 
                   Processed data, prediction, forecast set, mean, RMSE error, success flag
        """
        try:
            if df is None or df.empty:
                raise ValueError("Input DataFrame is None or empty")
            
            # Validate input data
            is_valid, validation_errors = validate_stock_data(df, "LinearRegression", strict=False)
            if not is_valid:
                raise ValueError(f"Input data validation failed: {validation_errors}")
            
            if self.debug:
                print_dataframe_info(df, "LinearRegression Input")
            
            # Ensure we have enough data points
            if len(df) < forecast_days + 35:  # Need enough data for forecasting
                raise ValueError(f"Insufficient data: need at least {forecast_days + 35} rows, got {len(df)}")
            
            # Work with a copy to avoid modifying original data
            df_work = df.copy()
            
            # Ensure 'Close' column exists
            if 'Close' not in df_work.columns:
                raise ValueError("'Close' column not found in data")
            
            # Number of days to be forecasted in future
            forecast_out = int(forecast_days)
            
            # Price after n days
            df_work['Close after n days'] = df_work['Close'].shift(-forecast_out)
            
            # Check how many valid rows we have for training
            valid_rows = df_work.dropna(subset=['Close after n days'])
            if len(valid_rows) < forecast_out:
                raise ValueError(f"Insufficient valid training data: {len(valid_rows)} rows after removing NaN")
            
            # New df with only relevant data
            df_new = df_work[['Close', 'Close after n days']].copy()
            
            # Remove rows with NaN values
            df_new = df_new.dropna()
            
            if len(df_new) == 0:
                raise ValueError("No valid data remaining after cleaning")
            
            # Structure data for train, test & forecast
            # Labels of known data, discard last forecast_out rows
            y = np.array(df_new.iloc[:-forecast_out, -1])
            y = np.reshape(y, (-1, 1))
            
            # All cols of known data except labels, discard last forecast_out rows
            X = np.array(df_new.iloc[:-forecast_out, 0:-1])
            
            # Unknown, X to be forecasted
            X_to_be_forecasted = np.array(df_new.iloc[-forecast_out:, 0:-1])
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No training data available after processing")
            
            # Training, testing to plot graphs, check accuracy
            train_size = int(0.8 * len(df))
            if train_size < 10:  # Minimum training size
                train_size = max(10, len(df) // 2)
            
            X_train = X[0:train_size, :]
            X_test = X[train_size:, :]
            y_train = y[0:train_size, :]
            y_test = y[train_size:, :]
            
            if len(X_train) == 0 or len(y_train) == 0:
                raise ValueError("No training data available")
            
            # Feature Scaling===Normalization
            sc = StandardScaler()
            X_train_scaled = sc.fit_transform(X_train)
            X_test_scaled = sc.transform(X_test)
            X_to_be_forecasted_scaled = sc.transform(X_to_be_forecasted)
            
            # Training
            clf = LinearRegression()
            clf.fit(X_train_scaled, y_train)
            
            # Testing
            y_test_pred = clf.predict(X_test_scaled)
            y_test_pred = y_test_pred * (1.04)  # Apply adjustment factor
            
            # Plot results with error handling
            try:
                plt.figure(figsize=(7.2, 4.8), dpi=65)
                plt.plot(y_test, label='Actual Price', color='blue')
                plt.plot(y_test_pred, label='Predicted Price', color='red', linestyle='--')
                plt.legend(loc=4)
                plt.title('Linear Regression Model Performance')
                plt.xlabel('Time')
                plt.ylabel('Stock Price')
                plt.grid(True, alpha=0.3)
                plt.savefig('static/LR.png', dpi=65, bbox_inches='tight')
                plt.close()
                self.logger.info("Linear Regression plot saved to static/LR.png")
            except Exception as e:
                self.logger.warning(f"Could not save Linear Regression plot: {e}")
                plt.close()
            
            # Calculate error
            if len(y_test) > 0 and len(y_test_pred) > 0:
                error_lr = math.sqrt(mean_squared_error(y_test, y_test_pred))
            else:
                error_lr = 0.0
            
            # Forecasting
            if len(X_to_be_forecasted_scaled) > 0:
                forecast_set = clf.predict(X_to_be_forecasted_scaled)
                forecast_set = forecast_set * (1.04)  # Apply adjustment factor
                mean = forecast_set.mean()
                lr_pred = forecast_set[0, 0]
            else:
                raise ValueError("No data available for forecasting")
            
            self.logger.info(f"Linear Regression prediction: {lr_pred:.4f}")
            self.logger.info(f"Linear Regression RMSE: {error_lr:.4f}")
            self.logger.info(f"Forecast set shape: {forecast_set.shape}")
            self.logger.info(f"Mean forecast: {mean:.4f}")
            
            return df_work, lr_pred, forecast_set, mean, error_lr, True
            
        except Exception as e:
            error_msg = f"Error in Linear Regression prediction: {str(e)}"
            self.logger.error(error_msg)
            
            if self.debug:
                self.logger.debug(f"Input DataFrame shape: {df.shape if df is not None else 'None'}")
                self.logger.debug(f"Input columns: {df.columns.tolist() if df is not None else 'None'}")
                self.logger.debug(f"Input data types: {df.dtypes.to_dict() if df is not None else 'None'}")
                if df is not None:
                    self.logger.debug(f"Null values: {df.isnull().sum().to_dict()}")
            
            # Return safe defaults with error flag
            return df if df is not None else pd.DataFrame(), 0.0, np.array([]), 0.0, 0.0, False
    
    def validate_prediction(self, prediction, forecast_set, error, threshold_high=0.2):
        """
        Validate if a prediction is reasonable
        
        Args:
            prediction (float): Current prediction
            forecast_set (numpy.array): All forecasted values
            error (float): RMSE error
            threshold_high (float): Maximum acceptable error ratio
            
        Returns:
            dict: Validation results
        """
        try:
            validation_results = {
                'prediction_valid': True,
                'warnings': [],
                'errors': []
            }
            
            # Check if prediction is finite
            if not np.isfinite(prediction):
                validation_results['errors'].append("Prediction is not a finite number")
                validation_results['prediction_valid'] = False
            
            # Check if forecast set is valid
            if len(forecast_set) == 0:
                validation_results['errors'].append("Empty forecast set")
                validation_results['prediction_valid'] = False
            elif not np.isfinite(forecast_set).all():
                validation_results['errors'].append("Forecast set contains invalid values")
                validation_results['prediction_valid'] = False
            
            # Check prediction reasonableness
            if prediction <= 0:
                validation_results['errors'].append("Prediction is non-positive")
                validation_results['prediction_valid'] = False
            
            if prediction > 10000:
                validation_results['warnings'].append("Prediction seems unusually high")
            
            # Check error reasonableness
            if error > threshold_high * abs(prediction):
                validation_results['warnings'].append(f"High error rate: {error:.4f}")
            
            # Check forecast set consistency
            if len(forecast_set) > 0:
                if np.std(forecast_set) > 0.5 * np.mean(np.abs(forecast_set)):
                    validation_results['warnings'].append("High volatility in forecast set")
            
            return validation_results
            
        except Exception as e:
            return {
                'prediction_valid': False,
                'warnings': [f"Validation error: {str(e)}"],
                'errors': ["Could not validate prediction"]
            }

if __name__ == "__main__":
    print("Linear Regression Model ready for testing")