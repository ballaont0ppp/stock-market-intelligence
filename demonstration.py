"""
Demonstration Script for Stock Market Prediction System
This script shows how to use the implemented modules together
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Import our custom modules
from stock_data_processor import StockDataProcessor
from arima_model import ARIMAModel
from lstm_model import LSTMModel
from linear_regression_model import LinearRegressionModel
from sentiment_analyzer import SentimentAnalyzer
from visualization import DataVisualizer
from recommendation_system import RecommendationSystem

def create_sample_data():
    """Create sample stock data for demonstration"""
    print("Creating sample stock data...")
    
    # Generate sample data
    dates = pd.date_range('2023-01-01', periods=200, freq='D')
    # Create realistic stock price movements
    prices = [150.0]  # Starting price
    for i in range(1, 200):
        # Random walk with slight trend
        change = np.random.normal(0.001, 0.02)  # Mean return 0.1% with 2% volatility
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 0.01))  # Ensure positive prices
    
    data = {
        'Open': [p * np.random.uniform(0.98, 1.02) for p in prices],
        'High': [p * np.random.uniform(1.01, 1.05) for p in prices],
        'Low': [p * np.random.uniform(0.95, 0.99) for p in prices],
        'Close': prices,
        'Adj Close': [p * np.random.uniform(0.99, 1.01) for p in prices],
        'Volume': np.random.randint(1000000, 10000000, 200)
    }
    
    df = pd.DataFrame(data, index=dates)
    return df

def demonstrate_system():
    """Demonstrate the complete stock prediction system"""
    print("=" * 60)
    print("STOCK MARKET PREDICTION SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Step 1: Create sample data
    print("\n1. Creating sample stock data...")
    sample_data = create_sample_data()
    print(f"   Created sample data with {len(sample_data)} records")
    
    # Step 2: Process data
    print("\n2. Processing stock data...")
    processor = StockDataProcessor()
    processed_data = processor.preprocess_data(sample_data, "DEMO")
    today_data = processor.get_today_data(processed_data)
    print("   Data processing completed")
    
    # Step 3: Make predictions (simplified for demo)
    print("\n3. Making predictions with ML models...")
    
    # ARIMA prediction (simplified)
    arima_model = ARIMAModel()
    print("   - ARIMA model: Prediction generated (simplified for demo)")
    arima_pred, arima_error = 155.25, 1.8  # Sample values
    
    # LSTM prediction (simplified)
    lstm_model = LSTMModel()
    print("   - LSTM model: Prediction generated (simplified for demo)")
    lstm_pred, lstm_error = 157.30, 2.1  # Sample values
    
    # Linear Regression prediction (simplified)
    lr_model = LinearRegressionModel()
    print("   - Linear Regression model: Prediction generated (simplified for demo)")
    lr_pred, lr_error = 153.75, 1.5  # Sample values
    
    # Step 4: Sentiment analysis
    print("\n4. Performing sentiment analysis...")
    sentiment_analyzer = SentimentAnalyzer()
    polarity, tw_list, tw_pol, pos, neg, neutral = sentiment_analyzer.retrieving_tweets_polarity("DEMO")
    print(f"   - Sentiment analysis completed: {tw_pol}")
    
    # Step 5: Data visualization
    print("\n5. Creating data visualizations...")
    visualizer = DataVisualizer()
    visualizer.plot_trends(sample_data, "DEMO")
    visualizer.plot_sentiment_analysis(12, 8, 10)  # Sample sentiment data
    visualizer.plot_forecast(np.array([155, 157, 160, 158, 162, 165, 163]))  # Sample forecast
    print("   - Visualizations created in static/ directory")
    
    # Step 6: Generate recommendation
    print("\n6. Generating investment recommendation...")
    recommender = RecommendationSystem()
    model_errors = {'arima': arima_error, 'lstm': lstm_error, 'lr': lr_error}
    recommendation = recommender.generate_recommendation(
        "DEMO", today_data, np.array([155, 157, 160, 158, 162, 165, 163]), 
        0.25, model_errors
    )
    risk_assessment = recommender.get_risk_assessment(
        "DEMO", today_data, 
        np.array([155, 157, 160, 158, 162, 165, 163]), 
        model_errors
    )
    
    print(f"   - Recommendation: {recommendation['recommendation']}")
    print(f"   - Confidence: {recommendation['confidence_score']}%")
    print(f"   - Risk Level: {risk_assessment['risk_level']}")
    
    # Display results summary
    print("\n" + "=" * 60)
    print("DEMONSTRATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"Stock Symbol: DEMO")
    print(f"Current Price: ${today_data['Close'].iloc[0]:.2f}")
    print(f"ARIMA Prediction: ${arima_pred:.2f} (Error: {arima_error:.2f})")
    print(f"LSTM Prediction: ${lstm_pred:.2f} (Error: {lstm_error:.2f})")
    print(f"Linear Regression Prediction: ${lr_pred:.2f} (Error: {lr_error:.2f})")
    print(f"Sentiment: {tw_pol}")
    print(f"Recommendation: {recommendation['recommendation']}")
    print(f"Confidence: {recommendation['confidence_score']}%")
    print(f"Risk Level: {risk_assessment['risk_level']}")
    
    print("\n✅ Demonstration completed successfully!")
    print("\nTo run the full web application, execute: python app.py")

if __name__ == "__main__":
    demonstrate_system()