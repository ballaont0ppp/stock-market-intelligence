"""
Recommendation System Module
Generates investment recommendations based on predictions and sentiment analysis
"""

import pandas as pd
import numpy as np

class RecommendationSystem:
    """Class to generate investment recommendations based on multiple factors"""
    
    def __init__(self):
        """Initialize the RecommendationSystem"""
        pass
    
    def generate_recommendation(self, symbol, today_stock, forecast_set, global_polarity, model_errors):
        """
        Generate investment recommendation based on all factors
        
        Args:
            symbol (str): Stock symbol
            today_stock (pandas.DataFrame): Today's stock data
            forecast_set (numpy.array): Forecasted prices
            global_polarity (float): Sentiment analysis polarity
            model_errors (dict): Dictionary of model RMSE errors
            
        Returns:
            dict: Recommendation with details
        """
        try:
            # Calculate mean of forecasted prices
            mean_forecast = np.mean(forecast_set) if len(forecast_set) > 0 else today_stock.iloc[-1]['Close']
            
            # Get today's closing price
            today_close = today_stock.iloc[-1]['Close']
            
            # Determine price trend prediction
            price_trend = "RISE" if today_close < mean_forecast else "FALL"
            
            # Determine sentiment trend
            sentiment_trend = "POSITIVE" if global_polarity > 0 else "NEGATIVE" if global_polarity < 0 else "NEUTRAL"
            
            # Calculate model confidence based on RMSE errors (lower error = higher confidence)
            total_error = sum(model_errors.values())
            if total_error > 0:
                # Normalize errors to get confidence weights (inverse relationship)
                arima_confidence = 1 - (model_errors['arima'] / total_error) if model_errors['arima'] > 0 else 0.33
                lstm_confidence = 1 - (model_errors['lstm'] / total_error) if model_errors['lstm'] > 0 else 0.33
                lr_confidence = 1 - (model_errors['lr'] / total_error) if model_errors['lr'] > 0 else 0.33
                
                # Normalize confidence scores to sum to 1
                total_confidence = arima_confidence + lstm_confidence + lr_confidence
                if total_confidence > 0:
                    arima_confidence /= total_confidence
                    lstm_confidence /= total_confidence
                    lr_confidence /= total_confidence
            else:
                # If no errors, equal confidence
                arima_confidence = lstm_confidence = lr_confidence = 0.33
            
            # Generate recommendation based on price trend and sentiment
            if price_trend == "RISE" and sentiment_trend == "POSITIVE":
                recommendation = "STRONG BUY"
                reason = f"Predicted price increase with positive market sentiment for {symbol}"
            elif price_trend == "RISE" and sentiment_trend == "NEGATIVE":
                recommendation = "BUY"
                reason = f"Predicted price increase despite negative sentiment for {symbol} - potential contrarian opportunity"
            elif price_trend == "FALL" and sentiment_trend == "POSITIVE":
                recommendation = "HOLD"
                reason = f"Predicted price decrease despite positive sentiment for {symbol} - conflicting signals"
            elif price_trend == "FALL" and sentiment_trend == "NEGATIVE":
                recommendation = "SELL"
                reason = f"Predicted price decrease with negative market sentiment for {symbol}"
            else:
                recommendation = "HOLD"
                reason = f"Unclear signals for {symbol} - recommend holding position"
            
            # Calculate overall confidence score (0-100)
            confidence_score = self._calculate_confidence_score(
                price_trend, sentiment_trend, model_errors, 
                arima_confidence, lstm_confidence, lr_confidence
            )
            
            # Create detailed recommendation
            recommendation_details = {
                "symbol": symbol,
                "recommendation": recommendation,
                "reason": reason,
                "confidence_score": round(confidence_score, 2),
                "price_trend": price_trend,
                "sentiment_trend": sentiment_trend,
                "today_close": round(today_close, 2),
                "forecast_mean": round(mean_forecast, 2),
                "sentiment_score": round(global_polarity, 4),
                "model_confidence": {
                    "arima": round(arima_confidence * 100, 2),
                    "lstm": round(lstm_confidence * 100, 2),
                    "linear_regression": round(lr_confidence * 100, 2)
                },
                "model_errors": model_errors
            }
            
            return recommendation_details
            
        except Exception as e:
            print(f"Error generating recommendation: {str(e)}")
            return {
                "symbol": symbol,
                "recommendation": "HOLD",
                "reason": "Error in recommendation generation",
                "confidence_score": 0,
                "error": str(e)
            }
    
    def _calculate_confidence_score(self, price_trend, sentiment_trend, model_errors, 
                                  arima_confidence, lstm_confidence, lr_confidence):
        """
        Calculate overall confidence score for the recommendation
        
        Args:
            price_trend (str): Predicted price trend
            sentiment_trend (str): Sentiment trend
            model_errors (dict): Model RMSE errors
            arima_confidence (float): ARIMA model confidence
            lstm_confidence (float): LSTM model confidence
            lr_confidence (float): Linear Regression model confidence
            
        Returns:
            float: Confidence score (0-100)
        """
        try:
            # Base confidence from model performance (30% weight)
            model_confidence = (arima_confidence + lstm_confidence + lr_confidence) / 3 * 30
            
            # Confidence from low model errors (30% weight)
            # Lower errors mean higher confidence
            avg_error = sum(model_errors.values()) / len(model_errors)
            error_confidence = max(0, (1 - avg_error) * 30) if avg_error > 0 else 15
            
            # Confidence from alignment of signals (40% weight)
            signal_alignment = 0
            if price_trend == "RISE" and sentiment_trend == "POSITIVE":
                signal_alignment = 40  # Maximum alignment
            elif price_trend == "FALL" and sentiment_trend == "NEGATIVE":
                signal_alignment = 40  # Maximum alignment
            elif (price_trend == "RISE" and sentiment_trend == "NEGATIVE") or \
                 (price_trend == "FALL" and sentiment_trend == "POSITIVE"):
                signal_alignment = 10  # Conflicting signals
            else:
                signal_alignment = 20  # Neutral or unclear signals
            
            confidence_score = model_confidence + error_confidence + signal_alignment
            return min(100, confidence_score)  # Cap at 100
            
        except Exception as e:
            print(f"Error calculating confidence score: {str(e)}")
            return 50  # Default confidence
    
    def get_risk_assessment(self, symbol, today_stock, forecast_set, model_errors):
        """
        Assess risk level for the stock
        
        Args:
            symbol (str): Stock symbol
            today_stock (pandas.DataFrame): Today's stock data
            forecast_set (numpy.array): Forecasted prices
            model_errors (dict): Model RMSE errors
            
        Returns:
            dict: Risk assessment details
        """
        try:
            # Calculate volatility from forecast
            if len(forecast_set) > 0:
                forecast_std = np.std(forecast_set)
                forecast_range = np.max(forecast_set) - np.min(forecast_set)
            else:
                forecast_std = 0
                forecast_range = 0
            
            # Calculate average model error
            avg_error = sum(model_errors.values()) / len(model_errors) if model_errors else 0
            
            # Determine risk level
            if avg_error > 5 or forecast_range > 10:
                risk_level = "HIGH"
                risk_description = "High volatility and/or high prediction errors"
            elif avg_error > 2 or forecast_range > 5:
                risk_level = "MODERATE"
                risk_description = "Moderate volatility and/or moderate prediction errors"
            else:
                risk_level = "LOW"
                risk_description = "Low volatility and low prediction errors"
            
            return {
                "symbol": symbol,
                "risk_level": risk_level,
                "risk_description": risk_description,
                "volatility": round(forecast_std, 2),
                "forecast_range": round(forecast_range, 2),
                "avg_prediction_error": round(avg_error, 2)
            }
            
        except Exception as e:
            print(f"Error in risk assessment: {str(e)}")
            return {
                "symbol": symbol,
                "risk_level": "UNKNOWN",
                "risk_description": "Error in risk assessment",
                "error": str(e)
            }

# Example usage
if __name__ == "__main__":
    # This would typically be used in conjunction with other modules
    recommender = RecommendationSystem()
    print("Recommendation System initialized successfully")