"""
Main Flask Application Module
Implements the web interface for the stock market prediction application
"""

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os
import logging
import warnings
import traceback
from datetime import datetime
warnings.filterwarnings("ignore")

# Import our custom modules
from stock_data_processor import StockDataProcessor
from arima_model import ARIMAModel
from lstm_model import LSTMModel
from linear_regression_model import LinearRegressionModel
from sentiment_analyzer import SentimentAnalyzer
from data_validation import print_dataframe_info

# Global configuration
DEBUG_MODE = True  # Set to False in production
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Initialize our models with debug mode
stock_processor = StockDataProcessor(debug=DEBUG_MODE)
arima_model = ARIMAModel(debug=DEBUG_MODE)
lstm_model = LSTMModel(debug=DEBUG_MODE)
lr_model = LinearRegressionModel(debug=DEBUG_MODE)
sentiment_analyzer = SentimentAnalyzer(debug=DEBUG_MODE, use_api=False)  # Disable API by default

logger.info("Stock Market Prediction Web App initialized")
logger.info(f"Debug mode: {DEBUG_MODE}")
logger.info(f"LSTM available: {lstm_model.is_available()}")
logger.info(f"Sentiment API status: {sentiment_analyzer.get_api_status()}")

# To control caching so as to save and retrieve plot figs on client side
@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    """Render the main index page"""
    if DEBUG_MODE:
        logger.debug("Rendering index page")
    
    # Get available stock symbols for dropdown
    available_symbols = stock_processor.get_available_symbols()
    
    return render_template('index.html', 
                         debug_mode=DEBUG_MODE,
                         available_symbols=available_symbols)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Handle stock prediction requests with comprehensive error handling
    """
    try:
        if request.method == 'GET':
            return redirect(url_for('index'))
        
        # Get stock symbol from form
        symbol = request.form.get('symbol', '').strip().upper()
        logger.info(f"Prediction request for symbol: {symbol}")
        
        if not symbol:
            return render_template('index.html', 
                                 error="Please enter a stock symbol",
                                 debug_mode=DEBUG_MODE)
        
        if DEBUG_MODE:
            logger.info(f"=== STARTING PREDICTION FOR {symbol} ===")
        
        # Step 1: Get historical data with validation
        logger.info("Step 1: Getting historical data...")
        df = stock_processor.get_historical_data(symbol)
        
        if df is None or df.empty:
            error_msg = f"Stock symbol '{symbol}' not found or no data available. Please try a different symbol."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE)
        
        if DEBUG_MODE:
            print_dataframe_info(df, f"{symbol} Raw Data")
            logger.info(f"Retrieved {len(df)} data points for {symbol}")
        
        # Step 2: Preprocess data with validation
        logger.info("Step 2: Preprocessing data...")
        df_processed = stock_processor.preprocess_data(df, symbol)
        
        if df_processed is None or df_processed.empty:
            error_msg = f"Failed to preprocess data for {symbol}. The data may be corrupted or in an unexpected format."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE)
        
        if DEBUG_MODE:
            print_dataframe_info(df_processed, f"{symbol} Processed Data")
        
        # Step 3: Get today's data
        logger.info("Step 3: Extracting today's data...")
        today_stock = stock_processor.get_today_data(df_processed)
        
        if today_stock is None or today_stock.empty:
            error_msg = f"Could not extract current stock data for {symbol}."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE)
        
        if DEBUG_MODE:
            logger.info(f"Today's stock data shape: {today_stock.shape}")
            logger.info(f"Today's stock columns: {today_stock.columns.tolist()}")
        
        # Initialize model results with safe defaults
        model_results = {
            'arima': {'pred': None, 'error': None, 'success': False, 'available': True},
            'lstm': {'pred': None, 'error': None, 'success': False, 'available': lstm_model.is_available()},
            'linear_regression': {'pred': None, 'error': None, 'success': False, 'available': True}
        }
        
        # Step 4: Make predictions with all models (handle failures gracefully)
        logger.info("Step 4: Making predictions...")
        
        # ARIMA Model
        if model_results['arima']['available']:
            try:
                logger.info("  - Making ARIMA prediction...")
                arima_pred, error_arima, arima_success = arima_model.predict(df_processed, symbol)
                model_results['arima'] = {
                    'pred': arima_pred if arima_success else None,
                    'error': error_arima if arima_success else None,
                    'success': arima_success,
                    'available': True
                }
                logger.info(f"  - ARIMA result: success={arima_success}, pred={arima_pred}, error={error_arima}")
            except Exception as e:
                logger.error(f"  - ARIMA failed: {str(e)}")
                model_results['arima']['available'] = False
        
        # LSTM Model
        if model_results['lstm']['available']:
            try:
                logger.info("  - Making LSTM prediction...")
                lstm_pred, error_lstm, lstm_success = lstm_model.predict(df_processed)
                model_results['lstm'] = {
                    'pred': lstm_pred if lstm_success else None,
                    'error': error_lstm if lstm_success else None,
                    'success': lstm_success,
                    'available': True
                }
                logger.info(f"  - LSTM result: success={lstm_success}, pred={lstm_pred}, error={error_lstm}")
            except Exception as e:
                logger.error(f"  - LSTM failed: {str(e)}")
                model_results['lstm']['available'] = False
        
        # Linear Regression Model
        if model_results['linear_regression']['available']:
            try:
                logger.info("  - Making Linear Regression prediction...")
                df_lr, lr_pred, forecast_set, mean, error_lr, lr_success = lr_model.predict(df_processed)
                model_results['linear_regression'] = {
                    'pred': lr_pred if lr_success else None,
                    'error': error_lr if lr_success else None,
                    'success': lr_success,
                    'available': True,
                    'mean': mean if lr_success else None,
                    'forecast_set': forecast_set if lr_success else np.array([])
                }
                logger.info(f"  - Linear Regression result: success={lr_success}, pred={lr_pred}, error={error_lr}")
            except Exception as e:
                logger.error(f"  - Linear Regression failed: {str(e)}")
                model_results['linear_regression']['available'] = False
        
        # Check if at least one model succeeded
        successful_models = [k for k, v in model_results.items() if v['success']]
        if not successful_models:
            error_msg = "All prediction models failed. This might be due to insufficient data or technical issues."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE)
        
        logger.info(f"Successful models: {successful_models}")
        
        # Step 5: Perform sentiment analysis
        logger.info("Step 5: Performing sentiment analysis...")
        try:
            polarity, tw_list, tw_pol, pos, neg, neutral, sentiment_success, error_msg = sentiment_analyzer.retrieving_tweets_polarity(symbol)
            logger.info(f"  - Sentiment result: success={sentiment_success}, polarity={polarity}, tweets={len(tw_list)}")
        except Exception as e:
            logger.error(f"  - Sentiment analysis failed: {str(e)}")
            # Use safe defaults
            polarity, tw_list, tw_pol, pos, neg, neutral = 0, [], "Analysis unavailable", 0, 0, 0
        
        # Step 6: Generate recommendation
        logger.info("Step 6: Generating recommendation...")
        idea, decision = recommending(df_processed, polarity, today_stock, 
                                    model_results['linear_regression']['mean'])
        
        logger.info(f"Recommendation: {idea} ({decision})")
        
        # Prepare data for template (handle missing values gracefully)
        template_data = {
            'symbol': symbol,
            'quote': symbol,
            'tw_list': tw_list,
            'tw_pol': tw_pol,
            'idea': idea,
            'decision': decision,
            'debug_mode': DEBUG_MODE,
            'model_results': model_results,
            'successful_models': successful_models
        }
        
        # Add model predictions with safe rounding
        for model_name, result in model_results.items():
            if result['success'] and result['pred'] is not None and np.isfinite(result['pred']):
                template_data[f'{model_name}_pred'] = round(result['pred'], 2)
                template_data[f'error_{model_name}'] = round(result['error'], 2) if result['error'] is not None else 0
            else:
                template_data[f'{model_name}_pred'] = "N/A"
                template_data[f'error_{model_name}'] = "N/A"
        
        # Add stock data with safe extraction
        stock_columns = ['Open', 'Close', 'Adj Close', 'High', 'Low', 'Volume']
        for col in stock_columns:
            try:
                if col in today_stock.columns and not today_stock[col].empty:
                    value = today_stock[col].iloc[0] if len(today_stock) > 0 else 'N/A'
                    if pd.isna(value) or not np.isfinite(value):
                        template_data[f'{col.lower()}_s'] = 'N/A'
                    else:
                        template_data[f'{col.lower()}_s'] = str(round(value, 2))
                else:
                    template_data[f'{col.lower()}_s'] = 'N/A'
            except Exception as e:
                logger.warning(f"Error extracting {col}: {e}")
                template_data[f'{col.lower()}_s'] = 'N/A'
        
        # Add forecast set if available
        if model_results['linear_regression']['success'] and model_results['linear_regression']['mean'] is not None:
            template_data['forecast_set'] = model_results['linear_regression']['forecast_set']
            template_data['mean'] = round(model_results['linear_regression']['mean'], 2)
        else:
            template_data['forecast_set'] = np.array([])
            template_data['mean'] = 0
        
        if DEBUG_MODE:
            logger.info("=== PREDICTION COMPLETED SUCCESSFULLY ===")
        
        # Render results page with all data
        return render_template('results.html', **template_data)
                              
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Critical error in prediction: {error_msg}", exc_info=True)
        
        if DEBUG_MODE:
            # In debug mode, provide more detailed error information
            detailed_error = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return render_template('index.html', 
                                 error=detailed_error,
                                 debug_mode=DEBUG_MODE,
                                 show_traceback=True)
        else:
            # In production, show user-friendly error
            return render_template('index.html', 
                                 error="An error occurred while processing your request. Please try again later.",
                                 debug_mode=False)

def recommending(df, global_polarity, today_stock, mean):
    """
    Generate recommendation based on predictions and sentiment analysis
    
    Args:
        df (pandas.DataFrame): Processed stock data
        global_polarity (float): Sentiment polarity score
        today_stock (pandas.DataFrame): Today's stock data
        mean (float): Mean of forecasted prices (from Linear Regression)
        
    Returns:
        tuple: (idea, decision) - Recommendation idea and decision
    """
    try:
        if today_stock is None or today_stock.empty:
            logger.warning("Cannot generate recommendation: today's stock data not available")
            return "HOLD", "INSUFFICIENT DATA"
        
        # Get current close price
        current_close = today_stock.iloc[-1]['Close'] if 'Close' in today_stock.columns else 0
        
        if mean is None or mean == 0:
            logger.warning("Cannot generate recommendation: forecast mean not available")
            # Fallback recommendation based on sentiment only
            if global_polarity > 0.1:
                return "RISE", "BUY"
            elif global_polarity < -0.1:
                return "FALL", "SELL"
            else:
                return "HOLD", "NEUTRAL"
        
        # Main recommendation logic
        if current_close < mean:
            if global_polarity > 0:
                idea = "RISE"
                decision = "BUY"
            elif global_polarity <= 0:
                idea = "FALL"
                decision = "SELL"
            else:
                idea = "FALL"
                decision = "SELL"
        else:
            idea = "FALL"
            decision = "SELL"
        
        logger.debug(f"Recommendation logic: current={current_close}, forecast={mean}, sentiment={global_polarity}")
        logger.debug(f"Final recommendation: {idea} ({decision})")
            
        return idea, decision
        
    except Exception as e:
        logger.error(f"Error in recommendation generation: {str(e)}")
        return "HOLD", "INSUFFICIENT DATA"

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test basic functionality
        connection_test = stock_processor.test_connection()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'debug_mode': DEBUG_MODE,
            'models': {
                'stock_processor': 'ok',
                'arima': 'ok',
                'lstm': 'available' if lstm_model.is_available() else 'unavailable',
                'linear_regression': 'ok',
                'sentiment': 'ok'
            },
            'external_apis': {
                'yfinance': connection_test['connection_ok']
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if DEBUG_MODE:
        logger.warning(f"404 error: {request.url}")
    return render_template('index.html', 
                         error="Page not found. Please use the navigation to find what you're looking for.",
                         debug_mode=DEBUG_MODE), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}", exc_info=True)
    return render_template('index.html', 
                         error="An internal server error occurred. Please try again later.",
                         debug_mode=DEBUG_MODE), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        logger.info("Created static directory")
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("STOCK MARKET PREDICTION WEB APP STARTING")
    logger.info("=" * 60)
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info(f"LSTM Available: {lstm_model.is_available()}")
    logger.info(f"Sentiment API: {sentiment_analyzer.get_api_status()}")
    logger.info("=" * 60)
    
    # Run the Flask app
    if DEBUG_MODE:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=False, host='0.0.0.0', port=5000)