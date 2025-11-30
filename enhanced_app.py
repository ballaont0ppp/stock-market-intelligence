"""
Enhanced Flask Application Module for Stock Market Prediction
Integrates all enhanced components with the web interface
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import os
import logging
import warnings
import traceback
from datetime import datetime
import json
from typing import Dict, Any, Optional
warnings.filterwarnings("ignore")

# Import enhanced components
try:
    from enhanced_stock_data_fetcher import EnhancedStockDataFetcher
    from enhanced_data_validator import EnhancedDataValidator
    from sophisticated_lstm_model import SophisticatedLSTMModel, ModelConfig
    from configuration_manager import ConfigurationManager, create_default_config_files
    ENHANCED_COMPONENTS_AVAILABLE = True
    print("✓ Enhanced components loaded successfully")
except ImportError as e:
    print(f"⚠ Enhanced components not available: {e}")
    print("Falling back to original components")
    ENHANCED_COMPONENTS_AVAILABLE = False

# Import original modules for fallback
from stock_data_processor import StockDataProcessor
from arima_model import ARIMAModel
from lstm_model import LSTMModel
from linear_regression_model import LinearRegressionModel
from sentiment_analyzer import SentimentAnalyzer
from data_validation import print_dataframe_info

# Enhanced Application Configuration
class EnhancedAppConfig:
    """Configuration for enhanced application"""
    def __init__(self):
        # Initialize configuration manager
        self.config_manager = None
        self.config = None
        
        # Initialize enhanced components
        self.enhanced_fetcher = None
        self.enhanced_validator = None
        self.enhanced_lstm = None
        
        # Fallback components
        self.fallback_processor = None
        self.fallback_lstm = None
        
        # Feature flags
        self.use_enhanced_components = ENHANCED_COMPONENTS_AVAILABLE
        self.use_enhanced_fetcher = True
        self.use_enhanced_validator = True
        self.use_enhanced_lstm = True
        
        # Performance settings
        self.enable_caching = True
        self.enable_validation = True
        self.debug_mode = True

# Global configuration
DEBUG_MODE = True  # Set to False in production
ENABLE_ENHANCED_FEATURES = True

# Initialize enhanced app configuration
app_config = EnhancedAppConfig()

# Create Flask app
app = Flask(__name__)

# Setup logging
def setup_logging():
    """Setup enhanced logging configuration"""
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def initialize_components():
    """Initialize all components (enhanced and fallback)"""
    global app_config
    
    try:
        if app_config.use_enhanced_components:
            logger.info("Initializing enhanced components...")
            
            # Initialize configuration manager
            try:
                app_config.config_manager = ConfigurationManager(environment="development" if DEBUG_MODE else "production")
                app_config.config = app_config.config_manager.get_config()
                logger.info("✓ Configuration manager initialized")
            except Exception as e:
                logger.warning(f"Configuration manager initialization failed: {e}")
                app_config.use_enhanced_components = False
            
            # Initialize enhanced data fetcher
            if app_config.use_enhanced_fetcher:
                try:
                    fetcher_config = app_config.config.data_fetcher.__dict__ if app_config.config else {}
                    app_config.enhanced_fetcher = EnhancedStockDataFetcher(**fetcher_config)
                    logger.info("✓ Enhanced data fetcher initialized")
                except Exception as e:
                    logger.warning(f"Enhanced fetcher initialization failed: {e}")
                    app_config.enhanced_fetcher = None
            
            # Initialize enhanced data validator
            if app_config.use_enhanced_validator:
                try:
                    app_config.enhanced_validator = EnhancedDataValidator(debug=DEBUG_MODE)
                    logger.info("✓ Enhanced data validator initialized")
                except Exception as e:
                    logger.warning(f"Enhanced validator initialization failed: {e}")
                    app_config.enhanced_validator = None
            
            # Initialize enhanced LSTM model
            if app_config.use_enhanced_lstm:
                try:
                    if app_config.config:
                        lstm_config = ModelConfig(
                            sequence_length=app_config.config.lstm_model.sequence_length,
                            epochs=min(app_config.config.lstm_model.epochs, 10),  # Limit epochs for web app
                            batch_size=app_config.config.lstm_model.batch_size,
                            lstm_units=app_config.config.lstm_model.lstm_units[:2],  # Limit complexity for web app
                            dense_units=app_config.config.lstm_model.dense_units,
                            model_type='LSTM',
                            use_batch_norm=app_config.config.lstm_model.use_batch_norm,
                            feature_columns=app_config.config.lstm_model.feature_columns
                        )
                    else:
                        lstm_config = ModelConfig()
                    
                    app_config.enhanced_lstm = SophisticatedLSTMModel(lstm_config, debug=DEBUG_MODE)
                    
                    if app_config.enhanced_lstm.is_available():
                        logger.info("✓ Enhanced LSTM model initialized")
                    else:
                        logger.warning("Enhanced LSTM model not available (TensorFlow not installed)")
                        app_config.enhanced_lstm = None
                        
                except Exception as e:
                    logger.warning(f"Enhanced LSTM initialization failed: {e}")
                    app_config.enhanced_lstm = None
        
        # Initialize fallback components
        logger.info("Initializing fallback components...")
        app_config.fallback_processor = StockDataProcessor(debug=DEBUG_MODE)
        app_config.fallback_lstm = LSTMModel(debug=DEBUG_MODE)
        
        # Initialize other models
        arima_model = ARIMAModel(debug=DEBUG_MODE)
        lr_model = LinearRegressionModel(debug=DEBUG_MODE)
        sentiment_analyzer = SentimentAnalyzer(debug=DEBUG_MODE, use_api=False)
        
        logger.info("✓ Fallback components initialized")
        
        # Log component status
        status = {
            'enhanced_features_enabled': app_config.use_enhanced_components,
            'enhanced_fetcher': app_config.enhanced_fetcher is not None,
            'enhanced_validator': app_config.enhanced_validator is not None,
            'enhanced_lstm': app_config.enhanced_lstm is not None and app_config.enhanced_lstm.is_available(),
            'fallback_fetcher': app_config.fallback_processor is not None,
            'fallback_lstm': app_config.fallback_lstm is not None and app_config.fallback_lstm.is_available(),
            'arima_available': True,
            'lr_available': True
        }
        
        logger.info(f"Component status: {json.dumps(status, indent=2)}")
        
        return status
        
    except Exception as e:
        logger.error(f"Component initialization failed: {e}")
        return {'error': str(e)}

# Initialize components
component_status = initialize_components()

# Initialize other models (using original modules for now)
arima_model = ARIMAModel(debug=DEBUG_MODE)
lr_model = LinearRegressionModel(debug=DEBUG_MODE)
sentiment_analyzer = SentimentAnalyzer(debug=DEBUG_MODE, use_api=False)

logger.info("Enhanced Stock Market Prediction Web App initialized")
logger.info(f"Debug mode: {DEBUG_MODE}")
logger.info(f"Enhanced features: {app_config.use_enhanced_components}")

# To control caching so as to save and retrieve plot figs on client side
@app.after_request
def add_header(response):
    """Add cache control headers"""
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
    if app_config.fallback_processor:
        available_symbols = app_config.fallback_processor.get_available_symbols()
    else:
        available_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    # Get system status
    status = get_system_status()
    
    return render_template('index.html', 
                         debug_mode=DEBUG_MODE,
                         available_symbols=available_symbols,
                         enhanced_features=app_config.use_enhanced_components,
                         system_status=status)

def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    status = {
        'enhanced_components': app_config.use_enhanced_components,
        'data_fetcher': {
            'type': 'enhanced' if app_config.enhanced_fetcher else 'fallback',
            'available': app_config.enhanced_fetcher is not None or app_config.fallback_processor is not None
        },
        'lstm_model': {
            'type': 'enhanced' if app_config.enhanced_lstm else 'fallback',
            'available': (app_config.enhanced_lstm and app_config.enhanced_lstm.is_available()) or 
                        (app_config.fallback_lstm and app_config.fallback_lstm.is_available())
        },
        'data_validator': {
            'type': 'enhanced' if app_config.enhanced_validator else 'basic',
            'available': app_config.enhanced_validator is not None
        }
    }
    
    # Add performance metrics if available
    if app_config.enhanced_fetcher:
        try:
            api_stats = app_config.enhanced_fetcher.get_api_usage_stats()
            status['performance'] = {
                'cache_hits': api_stats.get('cache_hits', 0),
                'total_calls': api_stats.get('total_calls', 0),
                'success_rate': api_stats.get('success_rate', 0)
            }
        except:
            pass
    
    return status

@app.route('/system-status')
def system_status():
    """API endpoint for system status"""
    return jsonify(get_system_status())

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Handle stock prediction requests with enhanced error handling and component integration
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
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components)
        
        if DEBUG_MODE:
            logger.info(f"=== STARTING ENHANCED PREDICTION FOR {symbol} ===")
        
        # Step 1: Get historical data using enhanced or fallback fetcher
        logger.info("Step 1: Getting historical data...")
        df = get_historical_data(symbol)
        
        if df is None or df.empty:
            error_msg = f"Stock symbol '{symbol}' not found or no data available. Please try a different symbol."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components)
        
        if DEBUG_MODE:
            print_dataframe_info(df, f"{symbol} Raw Data")
            logger.info(f"Retrieved {len(df)} data points for {symbol}")
        
        # Step 2: Enhanced data validation
        logger.info("Step 2: Validating and preprocessing data...")
        df_processed = validate_and_preprocess_data(df, symbol)
        
        if df_processed is None or df_processed.empty:
            error_msg = f"Failed to validate/process data for {symbol}. The data may be corrupted or in an unexpected format."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components)
        
        if DEBUG_MODE:
            print_dataframe_info(df_processed, f"{symbol} Processed Data")
        
        # Step 3: Get today's data
        logger.info("Step 3: Extracting today's data...")
        today_stock = get_today_data(df_processed)
        
        if today_stock is None or today_stock.empty:
            error_msg = f"Could not extract current stock data for {symbol}."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components)
        
        # Step 4: Make predictions with enhanced and fallback models
        logger.info("Step 4: Making predictions with all available models...")
        model_results = make_predictions(df_processed, symbol)
        
        # Check if at least one model succeeded
        successful_models = [k for k, v in model_results.items() if v['success']]
        if not successful_models:
            error_msg = "All prediction models failed. This might be due to insufficient data or technical issues."
            logger.error(error_msg)
            return render_template('index.html', 
                                 error=error_msg,
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components)
        
        logger.info(f"Successful models: {successful_models}")
        
        # Step 5: Enhanced sentiment analysis
        logger.info("Step 5: Performing sentiment analysis...")
        sentiment_results = perform_sentiment_analysis(symbol)
        polarity = sentiment_results['polarity']
        tw_list = sentiment_results['tw_list']
        tw_pol = sentiment_results['tw_pol']
        
        # Step 6: Generate recommendation using enhanced logic
        logger.info("Step 6: Generating recommendation...")
        idea, decision = generate_enhanced_recommendation(
            df_processed, polarity, today_stock, model_results
        )
        
        logger.info(f"Recommendation: {idea} ({decision})")
        
        # Prepare template data with enhanced information
        template_data = prepare_template_data(
            symbol, today_stock, model_results, idea, decision, 
            tw_list, tw_pol, sentiment_results
        )
        
        if DEBUG_MODE:
            logger.info("=== ENHANCED PREDICTION COMPLETED SUCCESSFULLY ===")
        
        # Render results page
        return render_template('results.html', **template_data)
                              
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Critical error in prediction: {error_msg}", exc_info=True)
        
        if DEBUG_MODE:
            detailed_error = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return render_template('index.html', 
                                 error=detailed_error,
                                 debug_mode=DEBUG_MODE,
                                 enhanced_features=app_config.use_enhanced_components,
                                 show_traceback=True)
        else:
            return render_template('index.html', 
                                 error="An error occurred while processing your request. Please try again later.",
                                 debug_mode=False,
                                 enhanced_features=app_config.use_enhanced_components)

def get_historical_data(symbol: str) -> Optional[pd.DataFrame]:
    """Get historical data using enhanced or fallback fetcher"""
    try:
        # Try enhanced fetcher first
        if app_config.enhanced_fetcher and app_config.use_enhanced_fetcher:
            logger.info("Using enhanced data fetcher...")
            data = app_config.enhanced_fetcher.get_historical_data(
                symbol, period="1y", interval="1d", use_cache=True
            )
            if data is not None and not data.empty:
                logger.info("✓ Enhanced fetcher succeeded")
                return data
        
        # Fallback to original processor
        if app_config.fallback_processor:
            logger.info("Using fallback data fetcher...")
            data = app_config.fallback_processor.get_historical_data(symbol)
            if data is not None and not data.empty:
                logger.info("✓ Fallback fetcher succeeded")
                return data
        
        logger.error("No data fetcher available or all failed")
        return None
        
    except Exception as e:
        logger.error(f"Error in get_historical_data: {e}")
        return None

def validate_and_preprocess_data(df: pd.DataFrame, symbol: str) -> Optional[pd.DataFrame]:
    """Validate and preprocess data using enhanced validator"""
    try:
        # Use enhanced validator if available
        if app_config.enhanced_validator and app_config.use_enhanced_validator:
            logger.info("Using enhanced data validator...")
            
            # Comprehensive validation
            is_valid, issues, analysis = app_config.enhanced_validator.validate_dataframe(
                df, symbol, strict=False
            )
            
            logger.info(f"Validation result: {'VALID' if is_valid else 'INVALID'}")
            logger.info(f"Data quality score: {analysis['data_quality']['overall_score']:.2f}")
            
            # Handle issues if found
            if not is_valid:
                logger.info("Attempting to clean data...")
                
                # Handle missing values
                df = app_config.enhanced_validator.handle_missing_values(
                    df, strategy='forward_fill'
                )
                
                # Handle outliers
                df = app_config.enhanced_validator.handle_outliers(
                    df, method='iqr', action='remove'
                )
                
                logger.info(f"Data cleaned, shape: {df.shape}")
            
            # Generate validation report
            if DEBUG_MODE:
                report = app_config.enhanced_validator.generate_validation_report(
                    df, symbol, f"validation_report_{symbol}.json"
                )
                logger.info(f"Validation report generated for {symbol}")
        
        # Add symbol column (required for compatibility)
        if 'Code' not in df.columns:
            code_list = [symbol] * len(df)
            df_code = pd.DataFrame(code_list, columns=['Code'])
            df = pd.concat([df_code, df], axis=1)
        
        logger.info("Data validation and preprocessing completed")
        return df
        
    except Exception as e:
        logger.error(f"Error in validate_and_preprocess_data: {e}")
        # Fallback to basic processing
        if app_config.fallback_processor:
            try:
                return app_config.fallback_processor.preprocess_data(df, symbol)
            except:
                pass
        return df

def get_today_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Extract today's data using enhanced or fallback method"""
    try:
        if app_config.fallback_processor:
            return app_config.fallback_processor.get_today_data(df)
        else:
            # Simple fallback
            return df.iloc[-1:] if not df.empty else None
    except Exception as e:
        logger.error(f"Error in get_today_data: {e}")
        return None

def make_predictions(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Make predictions using enhanced and fallback models"""
    model_results = {
        'arima': {'pred': None, 'error': None, 'success': False, 'available': True, 'type': 'enhanced'},
        'lstm': {'pred': None, 'error': None, 'success': False, 'available': False, 'type': 'enhanced'},
        'linear_regression': {'pred': None, 'error': None, 'success': False, 'available': True, 'type': 'enhanced'}
    }
    
    # ARIMA Model
    try:
        logger.info("  - Making ARIMA prediction...")
        arima_pred, error_arima, arima_success = arima_model.predict(df, symbol)
        model_results['arima'] = {
            'pred': arima_pred if arima_success else None,
            'error': error_arima if arima_success else None,
            'success': arima_success,
            'available': True,
            'type': 'enhanced'
        }
        logger.info(f"  - ARIMA result: success={arima_success}, pred={arima_pred}")
    except Exception as e:
        logger.error(f"  - ARIMA failed: {str(e)}")
        model_results['arima']['available'] = False
    
    # Enhanced LSTM Model
    if app_config.enhanced_lstm and app_config.enhanced_lstm.is_available():
        try:
            logger.info("  - Making Enhanced LSTM prediction...")
            
            # For web app, use a smaller, faster configuration
            temp_config = ModelConfig(
                sequence_length=min(app_config.enhanced_lstm.config.sequence_length, 30),
                epochs=min(app_config.enhanced_lstm.config.epochs, 5),
                batch_size=32,
                lstm_units=app_config.enhanced_lstm.config.lstm_units[:2],  # Use first 2 layers only
                dense_units=[16],
                model_type='LSTM'
            )
            
            # Create a temporary model for faster prediction
            temp_model = SophisticatedLSTMModel(temp_config, debug=False)
            
            # Split data for validation
            split_idx = int(0.8 * len(df))
            train_data = df.iloc[:split_idx]
            val_data = df.iloc[split_idx:]
            
            if len(train_data) >= temp_config.sequence_length + 10:
                # Train quickly
                temp_model.train(train_data, target_column='Close', validation_data=val_data)
                
                # Make predictions
                predictions = temp_model.predict(val_data, target_column='Close')
                
                if len(predictions) > 0:
                    final_pred = predictions[-1]
                    model_results['lstm'] = {
                        'pred': final_pred,
                        'error': None,
                        'success': True,
                        'available': True,
                        'type': 'enhanced'
                    }
                    logger.info(f"  - Enhanced LSTM result: pred={final_pred}")
                else:
                    logger.warning("  - Enhanced LSTM: no predictions generated")
            else:
                logger.warning("  - Enhanced LSTM: insufficient data for training")
                
        except Exception as e:
            logger.error(f"  - Enhanced LSTM failed: {str(e)}")
            model_results['lstm']['available'] = False
    
    # Fallback LSTM Model
    elif app_config.fallback_lstm and app_config.fallback_lstm.is_available():
        try:
            logger.info("  - Making Fallback LSTM prediction...")
            lstm_pred, error_lstm, lstm_success = app_config.fallback_lstm.predict(df)
            model_results['lstm'] = {
                'pred': lstm_pred if lstm_success else None,
                'error': error_lstm if lstm_success else None,
                'success': lstm_success,
                'available': True,
                'type': 'fallback'
            }
            logger.info(f"  - Fallback LSTM result: success={lstm_success}, pred={lstm_pred}")
        except Exception as e:
            logger.error(f"  - Fallback LSTM failed: {str(e)}")
            model_results['lstm']['available'] = False
    
    # Linear Regression Model
    try:
        logger.info("  - Making Linear Regression prediction...")
        df_lr, lr_pred, forecast_set, mean, error_lr, lr_success = lr_model.predict(df)
        model_results['linear_regression'] = {
            'pred': lr_pred if lr_success else None,
            'error': error_lr if lr_success else None,
            'success': lr_success,
            'available': True,
            'type': 'enhanced',
            'mean': mean if lr_success else None,
            'forecast_set': forecast_set if lr_success else np.array([])
        }
        logger.info(f"  - Linear Regression result: success={lr_success}, pred={lr_pred}")
    except Exception as e:
        logger.error(f"  - Linear Regression failed: {str(e)}")
        model_results['linear_regression']['available'] = False
    
    return model_results

def perform_sentiment_analysis(symbol: str) -> Dict[str, Any]:
    """Perform sentiment analysis with enhanced error handling"""
    try:
        polarity, tw_list, tw_pol, pos, neg, neutral, sentiment_success, error_msg = \
            sentiment_analyzer.retrieving_tweets_polarity(symbol)
        
        logger.info(f"  - Sentiment result: success={sentiment_success}, polarity={polarity}, tweets={len(tw_list)}")
        
        return {
            'polarity': polarity,
            'tw_list': tw_list,
            'tw_pol': tw_pol,
            'positive': pos,
            'negative': neg,
            'neutral': neutral,
            'success': sentiment_success,
            'error': error_msg
        }
    except Exception as e:
        logger.error(f"  - Sentiment analysis failed: {str(e)}")
        # Return safe defaults
        return {
            'polarity': 0,
            'tw_list': [],
            'tw_pol': "Analysis unavailable",
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'success': False,
            'error': str(e)
        }

def generate_enhanced_recommendation(df: pd.DataFrame, polarity: float, 
                                   today_stock: pd.DataFrame, 
                                   model_results: Dict[str, Any]) -> tuple:
    """Generate recommendation using enhanced logic"""
    try:
        if today_stock is None or today_stock.empty:
            logger.warning("Cannot generate recommendation: today's stock data not available")
            return "HOLD", "INSUFFICIENT DATA"
        
        # Get current close price
        current_close = today_stock.iloc[-1]['Close'] if 'Close' in today_stock.columns else 0
        
        # Collect all available predictions
        predictions = []
        for model_name, result in model_results.items():
            if result['success'] and result['pred'] is not None:
                predictions.append((model_name, result['pred'], result['type']))
        
        if not predictions:
            logger.warning("No successful predictions available")
            return "HOLD", "NO PREDICTIONS"
        
        # Calculate ensemble prediction (weighted average)
        total_weight = 0
        weighted_sum = 0
        
        # Assign weights based on model type and success
        for model_name, pred, model_type in predictions:
            if model_type == 'enhanced':
                weight = 2.0  # Enhanced models get higher weight
            else:
                weight = 1.0  # Fallback models get lower weight
                
            # Special handling for different models
            if model_name == 'lstm':
                weight *= 1.5  # LSTM gets bonus weight
            elif model_name == 'arima':
                weight *= 1.2  # ARIMA gets moderate weight
            
            total_weight += weight
            weighted_sum += pred * weight
        
        ensemble_prediction = weighted_sum / total_weight if total_weight > 0 else current_close
        
        # Enhanced recommendation logic
        price_change_pct = ((ensemble_prediction - current_close) / current_close) * 100
        
        # Decision thresholds
        strong_buy_threshold = 5.0   # >5% expected increase
        buy_threshold = 2.0          # >2% expected increase
        sell_threshold = -2.0        # <-2% expected decrease
        strong_sell_threshold = -5.0 # <-5% expected decrease
        
        # Generate recommendation based on ensemble prediction and sentiment
        if price_change_pct > strong_buy_threshold:
            if polarity > 0.1:
                idea, decision = "RISE", "STRONG BUY"
            elif polarity > 0:
                idea, decision = "RISE", "BUY"
            else:
                idea, decision = "RISE", "BUY"  # Still buy based on strong price prediction
        elif price_change_pct > buy_threshold:
            if polarity > 0.1:
                idea, decision = "RISE", "BUY"
            elif polarity < -0.1:
                idea, decision = "HOLD", "CAUTIOUS"
            else:
                idea, decision = "RISE", "BUY"
        elif price_change_pct < strong_sell_threshold:
            if polarity < -0.1:
                idea, decision = "FALL", "STRONG SELL"
            else:
                idea, decision = "FALL", "SELL"
        elif price_change_pct < sell_threshold:
            if polarity < -0.1:
                idea, decision = "FALL", "SELL"
            elif polarity > 0.1:
                idea, decision = "HOLD", "CAUTIOUS"
            else:
                idea, decision = "FALL", "SELL"
        else:
            # Price change is small - use sentiment to decide
            if polarity > 0.2:
                idea, decision = "RISE", "BUY"
            elif polarity < -0.2:
                idea, decision = "FALL", "SELL"
            else:
                idea, decision = "HOLD", "NEUTRAL"
        
        # Log recommendation details
        logger.debug(f"Ensemble prediction: {ensemble_prediction:.2f} (current: {current_close:.2f})")
        logger.debug(f"Expected change: {price_change_pct:.2f}%")
        logger.debug(f"Sentiment polarity: {polarity:.2f}")
        logger.debug(f"Final recommendation: {idea} ({decision})")
        
        return idea, decision
        
    except Exception as e:
        logger.error(f"Error in enhanced recommendation generation: {e}")
        # Fallback to simple logic
        return recommending(df, polarity, today_stock, 
                          model_results.get('linear_regression', {}).get('mean'))

def prepare_template_data(symbol: str, today_stock: pd.DataFrame, 
                         model_results: Dict[str, Any], idea: str, decision: str,
                         tw_list: list, tw_pol: str, sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare template data with enhanced information"""
    template_data = {
        'symbol': symbol,
        'quote': symbol,
        'tw_list': tw_list,
        'tw_pol': tw_pol,
        'idea': idea,
        'decision': decision,
        'debug_mode': DEBUG_MODE,
        'enhanced_features': app_config.use_enhanced_components,
        'model_results': model_results,
        'successful_models': [k for k, v in model_results.items() if v['success']],
        'sentiment_results': sentiment_results
    }
    
    # Add model predictions with safe rounding
    for model_name, result in model_results.items():
        if result['success'] and result['pred'] is not None and np.isfinite(result['pred']):
            template_data[f'{model_name}_pred'] = round(result['pred'], 2)
            template_data[f'error_{model_name}'] = round(result['error'], 2) if result['error'] is not None else 0
            template_data[f'{model_name}_type'] = result.get('type', 'unknown')
        else:
            template_data[f'{model_name}_pred'] = "N/A"
            template_data[f'error_{model_name}'] = "N/A"
            template_data[f'{model_name}_type'] = "unavailable"
    
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
    
    # Add forecast data if available
    if model_results['linear_regression']['success'] and model_results['linear_regression']['mean'] is not None:
        template_data['forecast_set'] = model_results['linear_regression']['forecast_set']
        template_data['mean'] = round(model_results['linear_regression']['mean'], 2)
    else:
        template_data['forecast_set'] = np.array([])
        template_data['mean'] = 0
    
    return template_data

# Keep the original recommending function for fallback
def recommending(df, global_polarity, today_stock, mean):
    """Original recommendation function for fallback"""
    try:
        if today_stock is None or today_stock.empty:
            logger.warning("Cannot generate recommendation: today's stock data not available")
            return "HOLD", "INSUFFICIENT DATA"
        
        current_close = today_stock.iloc[-1]['Close'] if 'Close' in today_stock.columns else 0
        
        if mean is None or mean == 0:
            if global_polarity > 0.1:
                return "RISE", "BUY"
            elif global_polarity < -0.1:
                return "FALL", "SELL"
            else:
                return "HOLD", "NEUTRAL"
        
        if current_close < mean:
            if global_polarity > 0:
                idea, decision = "RISE", "BUY"
            elif global_polarity <= 0:
                idea, decision = "FALL", "SELL"
            else:
                idea, decision = "FALL", "SELL"
        else:
            idea, decision = "FALL", "SELL"
        
        return idea, decision
        
    except Exception as e:
        logger.error(f"Error in original recommendation generation: {e}")
        return "HOLD", "INSUFFICIENT DATA"

@app.route('/health')
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test basic functionality
        connection_test = None
        if app_config.fallback_processor:
            connection_test = app_config.fallback_processor.test_connection()
        elif app_config.enhanced_fetcher:
            connection_test = app_config.enhanced_fetcher.test_connection()
        
        # Get enhanced system metrics
        enhanced_metrics = {}
        if app_config.enhanced_fetcher:
            try:
                enhanced_metrics = app_config.enhanced_fetcher.get_api_usage_stats()
            except:
                pass
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'debug_mode': DEBUG_MODE,
            'enhanced_features': app_config.use_enhanced_components,
            'components': {
                'enhanced_fetcher': app_config.enhanced_fetcher is not None,
                'enhanced_validator': app_config.enhanced_validator is not None,
                'enhanced_lstm': app_config.enhanced_lstm is not None and app_config.enhanced_lstm.is_available(),
                'fallback_fetcher': app_config.fallback_processor is not None,
                'fallback_lstm': app_config.fallback_lstm is not None and app_config.fallback_lstm.is_available(),
                'arima': 'ok',
                'linear_regression': 'ok',
                'sentiment': 'ok'
            },
            'external_apis': {
                'yfinance': connection_test['connection_ok'] if connection_test else False
            },
            'enhanced_metrics': enhanced_metrics,
            'system_status': get_system_status()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'enhanced_features': app_config.use_enhanced_components
        }, 500

@app.route('/config')
def get_config():
    """Get current configuration"""
    try:
        if app_config.config_manager:
            return jsonify(app_config.config_manager.get_config_summary())
        else:
            return jsonify({
                'error': 'Configuration manager not available',
                'enhanced_features': app_config.use_enhanced_components
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if DEBUG_MODE:
        logger.warning(f"404 error: {request.url}")
    return render_template('index.html', 
                         error="Page not found. Please use the navigation to find what you're looking for.",
                         debug_mode=DEBUG_MODE,
                         enhanced_features=app_config.use_enhanced_features), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}", exc_info=True)
    return render_template('index.html', 
                         error="An internal server error occurred. Please try again later.",
                         debug_mode=DEBUG_MODE,
                         enhanced_features=app_config.use_enhanced_features), 500

if __name__ == '__main__':
    # Create necessary directories
    directories = ['static', 'logs', 'data_cache', 'models', 'plots', 'reports']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created {directory} directory")
    
    # Create default configuration if enhanced components available
    if app_config.use_enhanced_components:
        try:
            create_default_config_files()
            logger.info("Default configuration files created")
        except Exception as e:
            logger.warning(f"Failed to create default config: {e}")
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("ENHANCED STOCK MARKET PREDICTION WEB APP STARTING")
    logger.info("=" * 60)
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info(f"Enhanced Features: {app_config.use_enhanced_components}")
    logger.info(f"Enhanced Fetcher: {app_config.enhanced_fetcher is not None}")
    logger.info(f"Enhanced Validator: {app_config.enhanced_validator is not None}")
    logger.info(f"Enhanced LSTM: {app_config.enhanced_lstm is not None and app_config.enhanced_lstm.is_available()}")
    logger.info(f"Fallback LSTM: {app_config.fallback_lstm is not None and app_config.fallback_lstm.is_available()}")
    logger.info(f"Sentiment API: {sentiment_analyzer.get_api_status()}")
    logger.info("=" * 60)
    
    # Run the Flask app
    if DEBUG_MODE:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        app.run(debug=False, host='0.0.0.0', port=5000)