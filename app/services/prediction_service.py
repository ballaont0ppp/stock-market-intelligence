"""
Prediction Service
Orchestrates ML models for stock price predictions
"""
import logging
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from ml_models.arima_model import ARIMAModel
from ml_models.lstm_model import LSTMModel
from ml_models.linear_regression_model import LinearRegressionModel
from ml_models.stock_data_processor import StockDataProcessor
from app.services.stock_repository import StockRepository
from app.services.sentiment_engine import SentimentEngine
from app.utils.exceptions import ValidationError, ExternalAPIError
from app.config import Config

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for orchestrating stock price predictions using multiple ML models"""
    
    def __init__(self):
        """Initialize the prediction service with ML models"""
        self.stock_repo = StockRepository()
        self.data_processor = StockDataProcessor(debug=False)
        
        # Initialize ML models
        self.arima_model = ARIMAModel(debug=False)
        self.lstm_model = LSTMModel(debug=False)
        self.lr_model = LinearRegressionModel(debug=False)
        
        # Initialize sentiment engine
        self.sentiment_engine = SentimentEngine()
        
        logger.info("PredictionService initialized")
    
    def get_historical_data(self, symbol: str, period_years: int = 2) -> Optional[pd.DataFrame]:
        """
        Get historical stock data using StockRepository
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period_years: Number of years of historical data (default: 2)
            
        Returns:
            DataFrame with historical stock data or None if failed
        """
        try:
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=period_years * 365)
            
            # Get price history from database
            price_history = self.stock_repo.get_price_history(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            if not price_history:
                logger.warning(f"No price history found in database for {symbol}, fetching from yfinance")
                # Fallback to yfinance
                return self.data_processor.get_historical_data(symbol, period_years)
            
            # Convert to DataFrame
            data = []
            for record in price_history:
                data.append({
                    'Date': record.date,
                    'Open': float(record.open),
                    'High': float(record.high),
                    'Low': float(record.low),
                    'Close': float(record.close),
                    'Volume': int(record.volume) if record.volume else 0
                })
            
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            
            logger.info(f"Retrieved {len(df)} historical records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            # Fallback to yfinance
            return self.data_processor.get_historical_data(symbol, period_years)
    
    def preprocess_data(self, df: pd.DataFrame, symbol: str) -> Optional[pd.DataFrame]:
        """
        Preprocess data using StockDataProcessor
        
        Args:
            df: Raw stock data DataFrame
            symbol: Stock symbol
            
        Returns:
            Preprocessed DataFrame or None if failed
        """
        try:
            return self.data_processor.preprocess_data(df, symbol)
        except Exception as e:
            logger.error(f"Error preprocessing data for {symbol}: {e}")
            return None
    
    def predict_stock_price(
        self, 
        symbol: str, 
        models: Optional[List[str]] = None,
        include_sentiment: bool = True
    ) -> Dict:
        """
        Predict stock price using specified ML models
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            models: List of model names to use ['arima', 'lstm', 'lr']. 
                   If None, uses all available models.
            
        Returns:
            Dictionary with predictions from each model and metadata
        """
        try:
            # Default to all models if not specified
            if models is None:
                models = ['arima', 'lstm', 'lr']
            
            # Validate symbol
            symbol = symbol.upper().strip()
            if not symbol:
                raise ValidationError("Stock symbol is required")
            
            logger.info(f"Starting prediction for {symbol} with models: {models}")
            
            # Get historical data
            df = self.get_historical_data(symbol, period_years=2)
            if df is None or df.empty:
                raise ExternalAPIError(f"Could not retrieve historical data for {symbol}")
            
            # Preprocess data
            df_processed = self.preprocess_data(df, symbol)
            if df_processed is None or df_processed.empty:
                raise ValidationError(f"Data preprocessing failed for {symbol}")
            
            # Initialize results
            results = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'data_points': len(df_processed),
                'predictions': {},
                'errors': {},
                'success': False
            }
            
            # Run ARIMA model
            if 'arima' in models:
                try:
                    logger.info(f"Running ARIMA model for {symbol}")
                    arima_raw = self.arima_model.predict(df_processed, symbol)
                    # Expected tuple: (prediction, error, success)
                    if isinstance(arima_raw, tuple) and len(arima_raw) >= 3:
                        arima_pred, arima_err, arima_ok = arima_raw[0], arima_raw[1], arima_raw[2]
                        if arima_ok and arima_pred is not None:
                            results['predictions']['arima'] = {
                                'prediction': float(arima_pred),
                                'error': float(arima_err) if arima_err is not None else None
                            }
                            logger.info(f"ARIMA prediction successful: {arima_pred}")
                        else:
                            results['errors']['arima'] = "ARIMA model returned no prediction"
                    else:
                        results['errors']['arima'] = "Unexpected ARIMA return shape"
                except Exception as e:
                    logger.error(f"ARIMA model error for {symbol}: {e}")
                    results['errors']['arima'] = str(e)
            
            # Run LSTM model
            if 'lstm' in models:
                try:
                    logger.info(f"Running LSTM model for {symbol}")
                    lstm_raw = self.lstm_model.predict(df_processed, symbol)
                    # Expected tuple: (prediction, error, success)
                    if isinstance(lstm_raw, tuple) and len(lstm_raw) >= 3:
                        lstm_pred, lstm_err, lstm_ok = lstm_raw[0], lstm_raw[1], lstm_raw[2]
                        if lstm_ok and lstm_pred is not None:
                            results['predictions']['lstm'] = {
                                'prediction': float(lstm_pred),
                                'error': float(lstm_err) if lstm_err is not None else None
                            }
                            logger.info(f"LSTM prediction successful: {lstm_pred}")
                        else:
                            results['errors']['lstm'] = "LSTM model returned no prediction"
                    else:
                        results['errors']['lstm'] = "Unexpected LSTM return shape"
                except Exception as e:
                    logger.error(f"LSTM model error for {symbol}: {e}")
                    results['errors']['lstm'] = str(e)
            
            # Run Linear Regression model
            if 'lr' in models:
                try:
                    logger.info(f"Running Linear Regression model for {symbol}")
                    lr_raw = self.lr_model.predict(df_processed, symbol)
                    # Expected tuple: (df, prediction, forecast_set, mean, error, success)
                    if isinstance(lr_raw, tuple) and len(lr_raw) >= 6:
                        _, lr_pred, forecast_set, lr_mean, lr_err, lr_ok = lr_raw[0], lr_raw[1], lr_raw[2], lr_raw[3], lr_raw[4], lr_raw[5]
                        if lr_ok and lr_pred is not None:
                            # Flatten forecast_set to a simple list of floats if available
                            try:
                                forecast_list = [float(x) for x in (forecast_set.flatten().tolist() if hasattr(forecast_set, 'flatten') else list(forecast_set))]
                            except Exception:
                                forecast_list = []
                            results['predictions']['lr'] = {
                                'prediction': float(lr_pred),
                                'error': float(lr_err) if lr_err is not None else None,
                                'mean': float(lr_mean) if lr_mean is not None else None,
                                'forecast': forecast_list
                            }
                            logger.info(f"LR prediction successful: {lr_pred}")
                        else:
                            results['errors']['lr'] = "Linear Regression model returned no prediction"
                    else:
                        results['errors']['lr'] = "Unexpected LR return shape"
                except Exception as e:
                    logger.error(f"Linear Regression model error for {symbol}: {e}")
                    results['errors']['lr'] = str(e)
            
            # Mark as successful if at least one model succeeded
            results['success'] = len(results['predictions']) > 0
            
            if not results['success']:
                logger.error(f"All models failed for {symbol}")
                raise ValidationError(f"All prediction models failed for {symbol}")
            
            # Add sentiment analysis if enabled
            if include_sentiment and self.sentiment_engine.is_enabled():
                try:
                    logger.info(f"Fetching sentiment analysis for {symbol}")
                    sentiment_data = self.sentiment_engine.get_sentiment_with_cache(
                        symbol=symbol,
                        tweet_count=100,
                        cache_duration_hours=1
                    )
                    results['sentiment'] = sentiment_data
                    logger.info(f"Sentiment analysis added: {sentiment_data.get('sentiment')}")
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed for {symbol}: {e}")
                    results['sentiment'] = {
                        'error': str(e),
                        'enabled': False
                    }
            else:
                results['sentiment'] = {
                    'enabled': False,
                    'message': 'Sentiment analysis is not configured'
                }
            
            logger.info(f"Prediction completed for {symbol}: {len(results['predictions'])} models succeeded")
            return results
            
        except ValidationError:
            raise
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in predict_stock_price for {symbol}: {e}")
            raise ExternalAPIError(f"Prediction failed for {symbol}: {str(e)}")
    
    def generate_forecast(
        self, 
        symbol: str, 
        days: int = 30,
        models: Optional[List[str]] = None,
        include_sentiment: bool = True
    ) -> Dict:
        """
        Generate multi-day price forecast
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days: Number of days to forecast (default: 30)
            models: List of model names to use. If None, uses all models.
            
        Returns:
            Dictionary with forecast data from each model
        """
        try:
            # Default to all models if not specified
            if models is None:
                models = ['arima', 'lstm', 'lr']
            
            # Validate inputs
            symbol = symbol.upper().strip()
            if not symbol:
                raise ValidationError("Stock symbol is required")
            
            if days < 1 or days > 365:
                raise ValidationError("Forecast days must be between 1 and 365")
            
            logger.info(f"Generating {days}-day forecast for {symbol} with models: {models}")
            
            # Get historical data
            df = self.get_historical_data(symbol, period_years=2)
            if df is None or df.empty:
                raise ExternalAPIError(f"Could not retrieve historical data for {symbol}")
            
            # Preprocess data
            df_processed = self.preprocess_data(df, symbol)
            if df_processed is None or df_processed.empty:
                raise ValidationError(f"Data preprocessing failed for {symbol}")
            
            # Initialize results
            results = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'forecast_days': days,
                'forecasts': {},
                'errors': {},
                'success': False
            }
            
            # Generate ARIMA forecast
            if 'arima' in models:
                try:
                    logger.info(f"Generating ARIMA forecast for {symbol}")
                    arima_forecast = self.arima_model.forecast(df_processed, symbol, days)
                    if arima_forecast:
                        results['forecasts']['arima'] = arima_forecast
                        logger.info(f"ARIMA forecast successful for {days} days")
                    else:
                        results['errors']['arima'] = "ARIMA model returned no forecast"
                except Exception as e:
                    logger.error(f"ARIMA forecast error for {symbol}: {e}")
                    results['errors']['arima'] = str(e)
            
            # Generate LSTM forecast
            if 'lstm' in models:
                try:
                    logger.info(f"Generating LSTM forecast for {symbol}")
                    lstm_forecast = self.lstm_model.forecast(df_processed, symbol, days)
                    if lstm_forecast:
                        results['forecasts']['lstm'] = lstm_forecast
                        logger.info(f"LSTM forecast successful for {days} days")
                    else:
                        results['errors']['lstm'] = "LSTM model returned no forecast"
                except Exception as e:
                    logger.error(f"LSTM forecast error for {symbol}: {e}")
                    results['errors']['lstm'] = str(e)
            
            # Generate Linear Regression forecast
            if 'lr' in models:
                try:
                    logger.info(f"Generating LR forecast for {symbol}")
                    lr_forecast = self.lr_model.forecast(df_processed, symbol, days)
                    if lr_forecast:
                        results['forecasts']['lr'] = lr_forecast
                        logger.info(f"LR forecast successful for {days} days")
                    else:
                        results['errors']['lr'] = "Linear Regression model returned no forecast"
                except Exception as e:
                    logger.error(f"LR forecast error for {symbol}: {e}")
                    results['errors']['lr'] = str(e)
            
            # Mark as successful if at least one model succeeded
            results['success'] = len(results['forecasts']) > 0
            
            if not results['success']:
                logger.error(f"All forecast models failed for {symbol}")
                raise ValidationError(f"All forecast models failed for {symbol}")
            
            # Add sentiment analysis if enabled
            if include_sentiment and self.sentiment_engine.is_enabled():
                try:
                    logger.info(f"Fetching sentiment analysis for {symbol}")
                    sentiment_data = self.sentiment_engine.get_sentiment_with_cache(
                        symbol=symbol,
                        tweet_count=100,
                        cache_duration_hours=1
                    )
                    results['sentiment'] = sentiment_data
                    logger.info(f"Sentiment analysis added: {sentiment_data.get('sentiment')}")
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed for {symbol}: {e}")
                    results['sentiment'] = {
                        'error': str(e),
                        'enabled': False
                    }
            else:
                results['sentiment'] = {
                    'enabled': False,
                    'message': 'Sentiment analysis is not configured'
                }
            
            logger.info(f"Forecast completed for {symbol}: {len(results['forecasts'])} models succeeded")
            return results
            
        except ValidationError:
            raise
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_forecast for {symbol}: {e}")
            raise ExternalAPIError(f"Forecast generation failed for {symbol}: {str(e)}")