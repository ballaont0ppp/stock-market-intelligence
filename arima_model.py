"""
ARIMA Model Module
Implements the ARIMA (AutoRegressive Integrated Moving Average) model for stock price prediction
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import math
from datetime import datetime
import logging
import warnings
warnings.filterwarnings("ignore")

# Import our validation utilities
from data_validation import validate_stock_data, print_dataframe_info

class ARIMAModel:
    """Class to implement ARIMA model for stock price prediction"""
    
    def __init__(self, debug=False, order=(6, 1, 0)):
        """Initialize the ARIMAModel
        
        Args:
            debug (bool): Enable debug logging
            order (tuple): ARIMA order (p, d, q) parameters
        """
        self.debug = debug
        self.order = order
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def parser(self, x):
        """
        Parse date string to datetime object
        
        Args:
            x (str): Date string in format 'YYYY-MM-DD'
            
        Returns:
            datetime: Parsed datetime object
        """
        try:
            return datetime.strptime(x, '%Y-%m-%d')
        except ValueError:
            # Fallback for different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    return datetime.strptime(x, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Could not parse date: {x}")
    
    def _prepare_time_series(self, df):
        """
        Prepare time series data from DataFrame
        
        Args:
            df (pandas.DataFrame): Stock data
            
        Returns:
            pandas.DataFrame: Time series with Date index and Price column
        """
        try:
            data = df.copy()
            
            # Ensure we have Close column
            if 'Close' not in data.columns:
                raise ValueError("'Close' column not found in data")
            
            # Ensure index is datetime
            if not isinstance(data.index, pd.DatetimeIndex):
                if 'Date' in data.columns:
                    # Try to parse Date column
                    try:
                        data['Date'] = pd.to_datetime(data['Date'])
                        data = data.set_index('Date')
                    except Exception as e:
                        self.logger.warning(f"Could not parse Date column: {e}")
                        # Use current index and assume it's date-like
                        try:
                            data.index = pd.to_datetime(data.index)
                        except Exception as e2:
                            self.logger.warning(f"Could not parse index as dates: {e2}")
                            # Create a simple date range
                            from datetime import timedelta
                            start_date = datetime.now() - timedelta(days=len(data))
                            data.index = pd.date_range(start=start_date, periods=len(data))
                else:
                    # No date information, create a simple date range
                    from datetime import timedelta
                    start_date = datetime.now() - timedelta(days=len(data))
                    data.index = pd.date_range(start=start_date, periods=len(data))
            
            # Build time series with Close as Price
            quantity_date = pd.DataFrame(index=data.index)
            quantity_date['Price'] = data['Close'].astype(float)
            
            # Handle missing values
            if quantity_date['Price'].isnull().any():
                self.logger.warning("Found null values in price data, applying forward fill")
                quantity_date = quantity_date.fillna(method='ffill')
                # Drop any remaining NaN values
                quantity_date = quantity_date.dropna()
            
            if quantity_date.empty:
                raise ValueError("Time series is empty after cleaning")
            
            return quantity_date
            
        except Exception as e:
            raise ValueError(f"Failed to prepare time series: {str(e)}")
    
    def arima_model(self, train, test, order=None):
        """
        Train and test ARIMA model
        
        Args:
            train (list): Training data
            test (list): Test data
            order (tuple): ARIMA order parameters
            
        Returns:
            tuple: (predictions, model_info) - Predictions for test data and model information
        """
        if order is None:
            order = self.order
        
        history = [x for x in train]
        predictions = list()
        model_info = {
            'order': order,
            'iterations': 0,
            'errors': []
        }
        
        try:
            for t in range(len(test)):
                try:
                    model = ARIMA(history, order=order)
                    model_fit = model.fit()
                    output = model_fit.forecast()
                    yhat = output[0]
                    predictions.append(yhat)
                    
                    obs = test[t]
                    history.append(obs)
                    model_info['iterations'] += 1
                    
                except Exception as e:
                    self.logger.warning(f"ARIMA iteration {t} failed: {e}")
                    model_info['errors'].append(f"Iteration {t}: {str(e)}")
                    
                    # Use simple prediction as fallback
                    if len(history) > 0:
                        predictions.append(history[-1])  # Use last known value
                    else:
                        predictions.append(0)  # Ultimate fallback
            
            return predictions, model_info
            
        except Exception as e:
            self.logger.error(f"ARIMA modeling failed completely: {e}")
            model_info['errors'].append(f"Complete failure: {str(e)}")
            # Return simple predictions
            predictions = [train[-1] if train else 0] * len(test)
            return predictions, model_info
    
    def predict(self, df, symbol="Unknown"):
        """
        Make stock price predictions using ARIMA model
        
        Args:
            df (pandas.DataFrame): Processed stock data
            symbol (str): Stock symbol for logging
            
        Returns:
            tuple: (arima_pred, error_arima, success) - Prediction, RMSE error, success flag
        """
        try:
            if df is None or df.empty:
                raise ValueError("Input DataFrame is None or empty")
            
            # Validate input data
            is_valid, validation_errors = validate_stock_data(df, symbol, strict=False)
            if not is_valid:
                raise ValueError(f"Input data validation failed: {validation_errors}")
            
            if self.debug:
                print_dataframe_info(df, f"{symbol} ARIMA Input")
            
            # Ensure we have enough data points for ARIMA
            min_required = 50  # ARIMA typically needs more data
            if len(df) < min_required:
                raise ValueError(f"Insufficient data for ARIMA: need at least {min_required} rows, got {len(df)}")
            
            # Prepare time series
            quantity_date = self._prepare_time_series(df)
            
            if len(quantity_date) < 10:
                raise ValueError(f"Insufficient time series data: {len(quantity_date)} points")
            
            # Plot trends with error handling
            try:
                plt.figure(figsize=(7.2, 4.8), dpi=65)
                plt.plot(quantity_date.index, quantity_date['Price'], label='Historical Price')
                plt.title(f'{symbol} - Price Trends')
                plt.xlabel('Date')
                plt.ylabel('Price')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig('static/Trends.png', dpi=65, bbox_inches='tight')
                plt.close()
                self.logger.info("ARIMA trend plot saved to static/Trends.png")
            except Exception as e:
                self.logger.warning(f"Could not save ARIMA trend plot: {e}")
                plt.close()
            
            # Prepare data for training/testing
            quantity = quantity_date['Price'].values
            size = int(len(quantity) * 0.80) if len(quantity) > 1 else 1
            
            if size < 10:  # Minimum training size
                size = max(10, len(quantity) // 2)
            
            train, test = quantity[0:size], quantity[size:len(quantity)]
            
            if len(test) == 0:
                # Use last few points as test
                test = train[-5:] if len(train) >= 5 else [train[-1]]
                train = train[:-len(test)]
            
            self.logger.info(f"ARIMA training data: {len(train)} points, testing data: {len(test)} points")
            
            # Fit model and make predictions
            predictions, model_info = self.arima_model(train, test)
            
            # Plot results with error handling
            try:
                plt.figure(figsize=(7.2, 4.8), dpi=65)
                plt.plot(test, label='Actual Price', color='blue', marker='o')
                plt.plot(predictions, label='Predicted Price', color='red', linestyle='--', marker='s')
                plt.legend(loc=4)
                plt.title(f'{symbol} - ARIMA Model Performance')
                plt.xlabel('Time')
                plt.ylabel('Stock Price')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig('static/ARIMA.png', dpi=65, bbox_inches='tight')
                plt.close()
                self.logger.info("ARIMA prediction plot saved to static/ARIMA.png")
            except Exception as e:
                self.logger.warning(f"Could not save ARIMA prediction plot: {e}")
                plt.close()
            
            # Calculate prediction and error
            if len(predictions) > 0:
                # Use the last prediction as our forecast
                arima_pred = predictions[-1]
                
                # Calculate error if we have test data
                if len(test) == len(predictions):
                    error_arima = math.sqrt(mean_squared_error(test, predictions))
                else:
                    # Fallback error calculation
                    error_arima = abs(arima_pred - (test[-1] if len(test) > 0 else arima_pred))
            else:
                raise ValueError("No predictions generated")
            
            self.logger.info(f"ARIMA prediction for {symbol}: {arima_pred:.4f}")
            self.logger.info(f"ARIMA RMSE: {error_arima:.4f}")
            self.logger.info(f"Model info: {model_info}")
            
            # Validate prediction
            if not np.isfinite(arima_pred) or arima_pred <= 0:
                self.logger.warning(f"ARIMA prediction may be invalid: {arima_pred}")
            
            return arima_pred, error_arima, True
            
        except Exception as e:
            error_msg = f"Error in ARIMA prediction for {symbol}: {str(e)}"
            self.logger.error(error_msg)
            
            if self.debug:
                self.logger.debug(f"Input DataFrame shape: {df.shape if df is not None else 'None'}")
                self.logger.debug(f"Input columns: {df.columns.tolist() if df is not None else 'None'}")
                self.logger.debug(f"Symbol: {symbol}")
            
            # Return None values with error flag
            return None, None, False

if __name__ == "__main__":
    print("ARIMA Model ready for testing")