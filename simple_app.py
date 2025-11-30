"""
Simple version of the Stock Prediction App that can be run successfully
"""

from flask import Flask, render_template, request
import os

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    """Render the main index page"""
    return render_template('simple_index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle stock prediction requests"""
    symbol = request.form.get('nm', 'AAPL')  # Default to AAPL if no symbol provided
    
    # Sample data for demonstration
    sample_data = {
        'symbol': symbol,
        'open_s': '150.25',
        'high_s': '155.75',
        'low_s': '149.50',
        'close_s': '153.80',
        'adj_close': '153.80',
        'vol': '25478963',
        'arima_pred': '156.25',
        'lstm_pred': '157.30',
        'lr_pred': '154.90',
        'error_arima': '1.85',
        'error_lstm': '2.10',
        'error_lr': '1.65',
        'tw_pol': 'Overall Positive',
        'idea': 'RISE',
        'decision': 'BUY',
        'forecast_set': [[155.2], [156.8], [157.5], [158.1], [159.3], [160.2], [161.0]]
    }
    
    # For simplicity, we'll render the results template with sample data
    # In a real implementation, this would be the results.html template
    return render_template('simple_index.html', **sample_data, quote=symbol)

if __name__ == '__main__':
    print("Starting Stock Prediction App...")
    print("Open your browser and go to http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)