"""
Dashboard Routes
Main dashboard and prediction interface
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import logging
from decimal import Decimal
from typing import Optional

from app.forms.prediction_forms import PredictionForm, ForecastForm
from app.services.prediction_service import PredictionService
from app.services.portfolio_service import PortfolioService
from app.utils.visualization import get_visualizer
from app.utils.exceptions import ValidationError, ExternalAPIError
from app.utils.error_handlers import handle_errors

logger = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard page
    Shows portfolio summary and quick predict form
    """
    try:
        portfolio_service = PortfolioService()
        
        # Get portfolio summary
        wallet_balance = portfolio_service.get_wallet_balance(current_user.user_id)
        holdings = portfolio_service.get_holdings(current_user.user_id)
        portfolio_value = portfolio_service.get_portfolio_value(current_user.user_id)
        
        # Calculate total worth
        total_worth = wallet_balance + portfolio_value
        
        # Get top 3 holdings by value
        top_holdings = sorted(holdings, key=lambda h: h.quantity * h.average_purchase_price, reverse=True)[:3] if holdings else []
        
        # Get recent transactions (last 5)
        from app.services.transaction_engine import TransactionEngine
        transaction_engine = TransactionEngine()
        recent_transactions, _ = transaction_engine.get_transaction_history(
            user_id=current_user.user_id,
            filters=None,
            page=1,
            per_page=5
        )
        
        # Calculate portfolio change (simplified - comparing current value to invested)
        portfolio_change = 0
        total_return = 0
        if holdings:
            total_invested = sum(h.total_invested for h in holdings)
            if total_invested > 0:
                portfolio_change = ((portfolio_value - total_invested) / total_invested) * 100
                total_return = portfolio_change
        
        # Create quick predict form
        predict_form = PredictionForm()
        
        return render_template(
            'dashboard/index.html',
            wallet_balance=wallet_balance,
            portfolio_value=portfolio_value,
            total_worth=total_worth,
            holdings_count=len(holdings),
            top_holdings=top_holdings,
            recent_transactions=recent_transactions,
            portfolio_change=portfolio_change,
            total_return=total_return,
            predict_form=predict_form
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard for user {current_user.user_id}: {e}")
        flash('Error loading dashboard data', 'error')
        return render_template('dashboard/index.html', predict_form=PredictionForm())


@bp.route('/predict', methods=['GET', 'POST'])
@login_required
@handle_errors()
def predict():
    """
    Stock price prediction page
    Accept stock symbol from form and display predictions from all models
    """
    form = PredictionForm()
    
    if request.method == 'GET':
        # Pre-fill symbol if provided in query string
        symbol = request.args.get('symbol', '').upper()
        if symbol:
            form.symbol.data = symbol
        
        return render_template('dashboard/predict.html', form=form)
    
    if form.validate_on_submit():
        try:
            symbol = form.symbol.data.upper().strip()
            models = form.models.data if form.models.data else ['arima', 'lstm', 'lr']
            
            logger.info(f"User {current_user.user_id} requesting prediction for {symbol} with models: {models}")
            
            # Get predictions
            prediction_service = PredictionService()
            results = prediction_service.predict_stock_price(symbol, models)
            
            if not results['success']:
                flash(f'Prediction failed for {symbol}. Please try again.', 'error')
                return render_template('dashboard/predict.html', form=form)
            
            # Generate visualizations
            visualizer = get_visualizer()
            plot_paths = {}
            
            # Generate individual model plots
            for model_name, model_result in results['predictions'].items():
                if 'actual' in model_result and 'predicted' in model_result:
                    if model_name == 'arima':
                        plot_path = visualizer.plot_arima_predictions(
                            model_result['actual'],
                            model_result['predicted'],
                            symbol
                        )
                    elif model_name == 'lstm':
                        plot_path = visualizer.plot_lstm_predictions(
                            model_result['actual'],
                            model_result['predicted'],
                            symbol
                        )
                    elif model_name == 'lr':
                        plot_path = visualizer.plot_linear_regression_predictions(
                            model_result['actual'],
                            model_result['predicted'],
                            symbol
                        )
                    
                    if plot_path:
                        # Convert to web path
                        plot_paths[model_name] = plot_path.replace('\\', '/')
            
            # Generate comparison plot if multiple models
            if len(results['predictions']) > 1:
                actual = None
                arima_pred = None
                lstm_pred = None
                lr_pred = None
                
                for model_name, model_result in results['predictions'].items():
                    if 'actual' in model_result:
                        actual = model_result['actual']
                    if model_name == 'arima' and 'predicted' in model_result:
                        arima_pred = model_result['predicted']
                    elif model_name == 'lstm' and 'predicted' in model_result:
                        lstm_pred = model_result['predicted']
                    elif model_name == 'lr' and 'predicted' in model_result:
                        lr_pred = model_result['predicted']
                
                if actual:
                    comparison_path = visualizer.plot_comparison(
                        actual, arima_pred, lstm_pred, lr_pred, symbol
                    )
                    if comparison_path:
                        plot_paths['comparison'] = comparison_path.replace('\\', '/')
            
            # Generate sentiment visualization if available
            if 'sentiment' in results and results['sentiment'].get('enabled', True):
                sentiment_data = results['sentiment']
                if 'positive' in sentiment_data:
                    sentiment_path = visualizer.plot_sentiment_analysis(
                        sentiment_data['positive'],
                        sentiment_data['negative'],
                        sentiment_data['neutral'],
                        symbol
                    )
                    if sentiment_path:
                        plot_paths['sentiment'] = sentiment_path.replace('\\', '/')
            
            # Determine recommendation based on predictions and sentiment
            recommendation = _generate_recommendation(results['predictions'], results.get('sentiment'))
            
            flash(f'Prediction completed successfully for {symbol}', 'success')
            
            return render_template(
                'dashboard/predict_results.html',
                symbol=symbol,
                results=results,
                plot_paths=plot_paths,
                recommendation=recommendation
            )
            
        except ValidationError as e:
            flash(str(e), 'error')
            return render_template('dashboard/predict.html', form=form)
        
        except ExternalAPIError as e:
            flash(f'Unable to fetch data: {str(e)}', 'error')
            return render_template('dashboard/predict.html', form=form)
        
        except Exception as e:
            logger.error(f"Unexpected error in prediction for user {current_user.user_id}: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('dashboard/predict.html', form=form)
    
    # Form validation failed
    return render_template('dashboard/predict.html', form=form)


@bp.route('/forecast', methods=['GET', 'POST'])
@login_required
@handle_errors()
def forecast():
    """
    Multi-day stock price forecast page
    """
    form = ForecastForm()
    
    if request.method == 'GET':
        # Pre-fill symbol if provided in query string
        symbol = request.args.get('symbol', '').upper()
        if symbol:
            form.symbol.data = symbol
        
        return render_template('dashboard/forecast.html', form=form)
    
    if form.validate_on_submit():
        try:
            symbol = form.symbol.data.upper().strip()
            days = form.days.data
            models = form.models.data if form.models.data else ['arima', 'lstm', 'lr']
            
            logger.info(f"User {current_user.user_id} requesting {days}-day forecast for {symbol}")
            
            # Generate forecast
            prediction_service = PredictionService()
            results = prediction_service.generate_forecast(symbol, days, models)
            
            if not results['success']:
                flash(f'Forecast generation failed for {symbol}. Please try again.', 'error')
                return render_template('dashboard/forecast.html', form=form)
            
            # Generate visualizations
            visualizer = get_visualizer()
            plot_paths = {}
            
            # Generate forecast plots for each model
            for model_name, forecast_result in results['forecasts'].items():
                if 'forecast' in forecast_result:
                    plot_path = visualizer.plot_forecast(
                        forecast_result['forecast'],
                        symbol,
                        days
                    )
                    if plot_path:
                        plot_paths[model_name] = plot_path.replace('\\', '/')
            
            # Determine recommendation
            recommendation = _generate_forecast_recommendation(results['forecasts'], days)
            
            flash(f'{days}-day forecast completed successfully for {symbol}', 'success')
            
            return render_template(
                'dashboard/forecast_results.html',
                symbol=symbol,
                days=days,
                results=results,
                plot_paths=plot_paths,
                recommendation=recommendation
            )
            
        except ValidationError as e:
            flash(str(e), 'error')
            return render_template('dashboard/forecast.html', form=form)
        
        except ExternalAPIError as e:
            flash(f'Unable to fetch data: {str(e)}', 'error')
            return render_template('dashboard/forecast.html', form=form)
        
        except Exception as e:
            logger.error(f"Unexpected error in forecast for user {current_user.user_id}: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('dashboard/forecast.html', form=form)
    
    # Form validation failed
    return render_template('dashboard/forecast.html', form=form)


def _generate_recommendation(predictions: dict, sentiment: Optional[dict] = None) -> dict:
    """
    Generate buy/sell/hold recommendation based on model predictions
    
    Args:
        predictions: Dictionary of model predictions
        
    Returns:
        Dictionary with recommendation and reasoning
    """
    try:
        buy_signals = 0
        sell_signals = 0
        total_models = len(predictions)
        
        for model_name, result in predictions.items():
            if 'prediction' in result:
                predicted = result['prediction']
                if 'actual' in result and len(result['actual']) > 0:
                    current = result['actual'][-1]
                    
                    # Calculate percentage change
                    change_pct = ((predicted - current) / current) * 100
                    
                    if change_pct > 2:  # More than 2% increase
                        buy_signals += 1
                    elif change_pct < -2:  # More than 2% decrease
                        sell_signals += 1
        
        # Determine overall recommendation
        if buy_signals > sell_signals and buy_signals >= total_models * 0.5:
            action = 'BUY'
            confidence = (buy_signals / total_models) * 100
            reason = f'{buy_signals} out of {total_models} models predict price increase'
        elif sell_signals > buy_signals and sell_signals >= total_models * 0.5:
            action = 'SELL'
            confidence = (sell_signals / total_models) * 100
            reason = f'{sell_signals} out of {total_models} models predict price decrease'
        else:
            action = 'HOLD'
            confidence = 50
            reason = 'Models show mixed signals or minimal price movement'
        
        # Adjust recommendation based on sentiment if available
        if sentiment and sentiment.get('enabled', True) and 'sentiment' in sentiment:
            sentiment_type = sentiment['sentiment']
            if sentiment_type == 'POSITIVE' and action == 'BUY':
                confidence = min(confidence + 10, 100)
                reason += '. Positive market sentiment supports this recommendation'
            elif sentiment_type == 'NEGATIVE' and action == 'SELL':
                confidence = min(confidence + 10, 100)
                reason += '. Negative market sentiment supports this recommendation'
            elif sentiment_type == 'POSITIVE' and action == 'SELL':
                confidence = max(confidence - 10, 0)
                reason += '. However, market sentiment is positive'
            elif sentiment_type == 'NEGATIVE' and action == 'BUY':
                confidence = max(confidence - 10, 0)
                reason += '. However, market sentiment is negative'
        
        return {
            'action': action,
            'confidence': round(confidence, 1),
            'reason': reason
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        return {
            'action': 'HOLD',
            'confidence': 0,
            'reason': 'Unable to generate recommendation'
        }


def _generate_forecast_recommendation(forecasts: dict, days: int) -> dict:
    """
    Generate recommendation based on multi-day forecasts
    
    Args:
        forecasts: Dictionary of model forecasts
        days: Number of forecast days
        
    Returns:
        Dictionary with recommendation and reasoning
    """
    try:
        upward_trends = 0
        downward_trends = 0
        total_models = len(forecasts)
        
        for model_name, result in forecasts.items():
            if 'forecast' in result and len(result['forecast']) > 0:
                forecast_data = result['forecast']
                
                # Compare first and last forecast values
                start_price = forecast_data[0]
                end_price = forecast_data[-1]
                
                change_pct = ((end_price - start_price) / start_price) * 100
                
                if change_pct > 3:  # More than 3% increase over period
                    upward_trends += 1
                elif change_pct < -3:  # More than 3% decrease over period
                    downward_trends += 1
        
        # Determine overall recommendation
        if upward_trends > downward_trends and upward_trends >= total_models * 0.5:
            action = 'BUY'
            confidence = (upward_trends / total_models) * 100
            reason = f'{upward_trends} out of {total_models} models predict upward trend over {days} days'
        elif downward_trends > upward_trends and downward_trends >= total_models * 0.5:
            action = 'SELL'
            confidence = (downward_trends / total_models) * 100
            reason = f'{downward_trends} out of {total_models} models predict downward trend over {days} days'
        else:
            action = 'HOLD'
            confidence = 50
            reason = f'Models show mixed trends over {days} days'
        
        return {
            'action': action,
            'confidence': round(confidence, 1),
            'reason': reason
        }
        
    except Exception as e:
        logger.error(f"Error generating forecast recommendation: {e}")
        return {
            'action': 'HOLD',
            'confidence': 0,
            'reason': 'Unable to generate recommendation'
        }
