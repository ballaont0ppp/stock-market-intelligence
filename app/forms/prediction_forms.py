"""
Prediction Forms
Forms for stock price prediction functionality
Mobile-optimized with proper input types for mobile keyboards
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PredictionForm(FlaskForm):
    """Form for requesting stock price predictions"""
    
    symbol = StringField(
        'Stock Symbol',
        validators=[
            DataRequired(message='Stock symbol is required'),
            Length(min=1, max=10, message='Symbol must be 1-10 characters')
        ],
        render_kw={
            'placeholder': 'e.g., AAPL',
            'class': 'form-control',
            'autocomplete': 'off',
            'inputmode': 'text',
            'pattern': '[A-Z]{1,10}'
        }
    )
    
    models = SelectMultipleField(
        'Models to Use',
        choices=[
            ('arima', 'ARIMA'),
            ('lstm', 'LSTM'),
            ('lr', 'Linear Regression')
        ],
        default=['arima', 'lstm', 'lr'],
        render_kw={'class': 'form-select', 'aria-label': 'Select prediction models'}
    )
    
    submit = SubmitField('Get Prediction', render_kw={'class': 'btn btn-primary'})


class ForecastForm(FlaskForm):
    """Form for requesting multi-day stock price forecasts"""
    
    symbol = StringField(
        'Stock Symbol',
        validators=[
            DataRequired(message='Stock symbol is required'),
            Length(min=1, max=10, message='Symbol must be 1-10 characters')
        ],
        render_kw={
            'placeholder': 'e.g., AAPL',
            'class': 'form-control',
            'autocomplete': 'off',
            'inputmode': 'text',
            'pattern': '[A-Z]{1,10}'
        }
    )
    
    days = IntegerField(
        'Forecast Days',
        validators=[
            DataRequired(message='Number of days is required'),
            NumberRange(min=1, max=365, message='Days must be between 1 and 365')
        ],
        default=30,
        render_kw={
            'placeholder': '30',
            'class': 'form-control',
            'min': '1',
            'max': '365',
            'inputmode': 'numeric',
            'type': 'number'
        }
    )
    
    models = SelectMultipleField(
        'Models to Use',
        choices=[
            ('arima', 'ARIMA'),
            ('lstm', 'LSTM'),
            ('lr', 'Linear Regression')
        ],
        default=['arima', 'lstm', 'lr'],
        render_kw={'class': 'form-select', 'aria-label': 'Select forecast models'}
    )
    
    submit = SubmitField('Generate Forecast', render_kw={'class': 'btn btn-primary'})
