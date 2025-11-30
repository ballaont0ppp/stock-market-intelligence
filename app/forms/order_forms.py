"""
Order Forms
WTForms for buy/sell orders
Mobile-optimized with proper input types for mobile keyboards
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError


class BuyOrderForm(FlaskForm):
    """Form for buying stocks"""
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
    
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(message='Quantity is required'),
            NumberRange(min=1, max=1000000, message='Quantity must be between 1 and 1,000,000')
        ],
        render_kw={
            'placeholder': 'Number of shares',
            'class': 'form-control',
            'min': '1',
            'inputmode': 'numeric',
            'type': 'number'
        }
    )
    
    submit = SubmitField('Buy', render_kw={'class': 'btn btn-success'})
    
    def validate_symbol(self, field):
        """Validate stock symbol format"""
        symbol = field.data.strip().upper()
        if not symbol.isalpha():
            raise ValidationError('Stock symbol must contain only letters')
        field.data = symbol


class SellOrderForm(FlaskForm):
    """Form for selling stocks"""
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
    
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(message='Quantity is required'),
            NumberRange(min=1, max=1000000, message='Quantity must be between 1 and 1,000,000')
        ],
        render_kw={
            'placeholder': 'Number of shares',
            'class': 'form-control',
            'min': '1',
            'inputmode': 'numeric',
            'type': 'number'
        }
    )
    
    submit = SubmitField('Sell', render_kw={'class': 'btn btn-danger'})
    
    def validate_symbol(self, field):
        """Validate stock symbol format"""
        symbol = field.data.strip().upper()
        if not symbol.isalpha():
            raise ValidationError('Stock symbol must contain only letters')
        field.data = symbol


class OrderFilterForm(FlaskForm):
    """Form for filtering order history"""
    order_type = SelectField(
        'Order Type',
        choices=[('', 'All'), ('BUY', 'Buy'), ('SELL', 'Sell')],
        render_kw={'class': 'form-select', 'aria-label': 'Filter by order type'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('', 'All'),
            ('COMPLETED', 'Completed'),
            ('PENDING', 'Pending'),
            ('FAILED', 'Failed'),
            ('CANCELLED', 'Cancelled')
        ],
        render_kw={'class': 'form-select', 'aria-label': 'Filter by status'}
    )
    
    symbol = StringField(
        'Symbol',
        validators=[Length(max=10)],
        render_kw={
            'placeholder': 'Filter by symbol',
            'class': 'form-control',
            'inputmode': 'text',
            'pattern': '[A-Z]{0,10}'
        }
    )
    
    submit = SubmitField('Filter', render_kw={'class': 'btn btn-primary'})
