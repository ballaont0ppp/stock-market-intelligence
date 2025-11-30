"""
Data Visualization Module
Handles creation of charts and graphs for stock market data visualization
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# Set style for better-looking plots
plt.style.use('ggplot')


class DataVisualizer:
    """Class to handle data visualization for stock market predictions"""
    
    def __init__(self, plots_dir: str = 'static/plots'):
        """
        Initialize the DataVisualizer
        
        Args:
            plots_dir: Directory to save plot images (default: 'static/plots')
        """
        self.plots_dir = plots_dir
        
        # Create plots directory if it doesn't exist
        if not os.path.exists(self.plots_dir):
            os.makedirs(self.plots_dir)
            logger.info(f"Created plots directory: {self.plots_dir}")
    
    def _generate_filename(self, base_name: str, symbol: str = None) -> str:
        """
        Generate a unique filename for a plot
        
        Args:
            base_name: Base name for the file (e.g., 'trends', 'arima')
            symbol: Optional stock symbol to include in filename
            
        Returns:
            Full path to the plot file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if symbol:
            filename = f"{symbol}_{base_name}_{timestamp}.png"
        else:
            filename = f"{base_name}_{timestamp}.png"
        
        return os.path.join(self.plots_dir, filename)
    
    def plot_trends(self, data: pd.DataFrame, symbol: str) -> Optional[str]:
        """
        Plot historical stock price trends
        
        Args:
            data: Stock price data with 'Close' column
            symbol: Stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(data.index, data['Close'], linewidth=2, color='#2E86AB')
            plt.title(f"Historical Price Trends for {symbol}", fontsize=16, fontweight='bold')
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Closing Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filepath = self._generate_filename('trends', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Trends plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting trends for {symbol}: {e}")
            plt.close()
            return None
    
    def plot_arima_predictions(
        self, 
        actual: List[float], 
        predicted: List[float],
        symbol: str = None
    ) -> Optional[str]:
        """
        Plot ARIMA model predictions vs actual prices
        
        Args:
            actual: Actual stock prices
            predicted: Predicted stock prices
            symbol: Optional stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            plt.figure(figsize=(12, 6))
            x = range(len(actual))
            
            plt.plot(x, actual, label='Actual Price', marker='o', 
                    linewidth=2, markersize=6, color='#2E86AB')
            plt.plot(x, predicted, label='Predicted Price', marker='s', 
                    linewidth=2, markersize=6, color='#A23B72')
            
            plt.legend(loc='best', fontsize=11)
            plt.title("ARIMA Model: Actual vs Predicted Prices", fontsize=16, fontweight='bold')
            plt.xlabel("Time Period", fontsize=12)
            plt.ylabel("Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filepath = self._generate_filename('arima', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"ARIMA predictions plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting ARIMA predictions: {e}")
            plt.close()
            return None
    
    def plot_lstm_predictions(
        self, 
        actual: List[float], 
        predicted: List[float],
        symbol: str = None
    ) -> Optional[str]:
        """
        Plot LSTM model predictions vs actual prices
        
        Args:
            actual: Actual stock prices
            predicted: Predicted stock prices
            symbol: Optional stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            plt.figure(figsize=(12, 6))
            x = range(len(actual))
            
            plt.plot(x, actual, label='Actual Price', marker='o', 
                    linewidth=2, markersize=6, color='#2E86AB')
            plt.plot(x, predicted, label='Predicted Price', marker='s', 
                    linewidth=2, markersize=6, color='#F18F01')
            
            plt.legend(loc='best', fontsize=11)
            plt.title("LSTM Model: Actual vs Predicted Prices", fontsize=16, fontweight='bold')
            plt.xlabel("Time Period", fontsize=12)
            plt.ylabel("Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filepath = self._generate_filename('lstm', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"LSTM predictions plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting LSTM predictions: {e}")
            plt.close()
            return None
    
    def plot_linear_regression_predictions(
        self, 
        actual: List[float], 
        predicted: List[float],
        symbol: str = None
    ) -> Optional[str]:
        """
        Plot Linear Regression model predictions vs actual prices
        
        Args:
            actual: Actual stock prices
            predicted: Predicted stock prices
            symbol: Optional stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            plt.figure(figsize=(12, 6))
            x = range(len(actual))
            
            plt.plot(x, actual, label='Actual Price', marker='o', 
                    linewidth=2, markersize=6, color='#2E86AB')
            plt.plot(x, predicted, label='Predicted Price', marker='s', 
                    linewidth=2, markersize=6, color='#06A77D')
            
            plt.legend(loc='best', fontsize=11)
            plt.title("Linear Regression Model: Actual vs Predicted Prices", 
                     fontsize=16, fontweight='bold')
            plt.xlabel("Time Period", fontsize=12)
            plt.ylabel("Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filepath = self._generate_filename('lr', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Linear Regression predictions plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting Linear Regression predictions: {e}")
            plt.close()
            return None
    
    def plot_sentiment_analysis(
        self, 
        pos: int, 
        neg: int, 
        neutral: int,
        symbol: str = None
    ) -> Optional[str]:
        """
        Plot sentiment analysis results as a pie chart
        
        Args:
            pos: Number of positive tweets
            neg: Number of negative tweets
            neutral: Number of neutral tweets
            symbol: Optional stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [pos, neg, neutral]
            colors = ['#28a745', '#dc3545', '#6c757d']
            explode = (0.1, 0, 0)  # explode the positive slice
            
            plt.figure(figsize=(10, 8))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=True, startangle=140,
                    textprops={'fontsize': 12})
            plt.axis('equal')
            
            title = f"Sentiment Analysis for {symbol}" if symbol else "Sentiment Analysis of Tweets"
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            filepath = self._generate_filename('sentiment', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Sentiment analysis plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting sentiment analysis: {e}")
            plt.close()
            return None
    
    def plot_forecast(
        self, 
        forecast_data: np.ndarray,
        symbol: str = None,
        days: int = None
    ) -> Optional[str]:
        """
        Plot multi-day forecast
        
        Args:
            forecast_data: Forecasted prices
            symbol: Optional stock symbol
            days: Number of days in forecast (defaults to length of forecast_data)
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            if days is None:
                days = len(forecast_data)
            
            x = range(1, len(forecast_data) + 1)
            
            plt.figure(figsize=(12, 6))
            plt.plot(x, forecast_data, marker='o', linewidth=2, 
                    markersize=8, color='#2E86AB')
            
            title = f"{days}-Day Stock Price Forecast"
            if symbol:
                title = f"{symbol} - {title}"
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel("Days", fontsize=12)
            plt.ylabel("Predicted Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(x)
            plt.tight_layout()
            
            filepath = self._generate_filename('forecast', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Forecast plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting forecast: {e}")
            plt.close()
            return None
    
    def plot_comparison(
        self,
        actual: List[float],
        arima_pred: Optional[List[float]] = None,
        lstm_pred: Optional[List[float]] = None,
        lr_pred: Optional[List[float]] = None,
        symbol: str = None
    ) -> Optional[str]:
        """
        Plot comparison of all model predictions vs actual prices
        
        Args:
            actual: Actual stock prices
            arima_pred: ARIMA predictions (optional)
            lstm_pred: LSTM predictions (optional)
            lr_pred: Linear Regression predictions (optional)
            symbol: Optional stock symbol
            
        Returns:
            Path to saved plot file or None if failed
        """
        try:
            plt.figure(figsize=(14, 7))
            x = range(len(actual))
            
            plt.plot(x, actual, label='Actual Price', marker='o', 
                    linewidth=2.5, markersize=7, color='#2E86AB')
            
            if arima_pred:
                plt.plot(x, arima_pred, label='ARIMA', marker='s', 
                        linewidth=2, markersize=5, color='#A23B72', alpha=0.8)
            
            if lstm_pred:
                plt.plot(x, lstm_pred, label='LSTM', marker='^', 
                        linewidth=2, markersize=5, color='#F18F01', alpha=0.8)
            
            if lr_pred:
                plt.plot(x, lr_pred, label='Linear Regression', marker='d', 
                        linewidth=2, markersize=5, color='#06A77D', alpha=0.8)
            
            plt.legend(loc='best', fontsize=11)
            
            title = "Model Comparison: Actual vs Predicted Prices"
            if symbol:
                title = f"{symbol} - {title}"
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel("Time Period", fontsize=12)
            plt.ylabel("Price ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filepath = self._generate_filename('comparison', symbol)
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Comparison plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error plotting comparison: {e}")
            plt.close()
            return None
    
    def cleanup_old_plots(self, days_old: int = 7):
        """
        Remove plot files older than specified days
        
        Args:
            days_old: Remove files older than this many days (default: 7)
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 86400)  # 86400 seconds in a day
            
            removed_count = 0
            for filename in os.listdir(self.plots_dir):
                filepath = os.path.join(self.plots_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old plot files")
                
        except Exception as e:
            logger.error(f"Error cleaning up old plots: {e}")


# Singleton instance
_visualizer_instance = None


def get_visualizer() -> DataVisualizer:
    """
    Get or create the singleton DataVisualizer instance
    
    Returns:
        DataVisualizer instance
    """
    global _visualizer_instance
    if _visualizer_instance is None:
        _visualizer_instance = DataVisualizer()
    return _visualizer_instance
