"""
Dividend Forms
Forms for dividend management
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import date


class DividendForm(FlaskForm):
    """Form for creating/editing dividends"""
    
    company_symbol = StringField(
        'Company Symbol',
        validators=[DataRequired()],
        render_kw={'placeholder': 'e.g., AAPL'}
    )
    
    dividend_per_share = DecimalField(
        'Dividend Per Share ($)',
        validators=[
            DataRequired(),
            NumberRange(min=0.0001, message='Dividend must be greater than 0')
        ],
        places=4,
        render_kw={'placeholder': '0.0000', 'step': '0.0001'}
    )
    
    ex_dividend_date = DateField(
        'Ex-Dividend Date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    
    record_date = DateField(
        'Record Date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    
    payment_date = DateField(
        'Payment Date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    
    announcement_date = DateField(
        'Announcement Date (Optional)',
        format='%Y-%m-%d'
    )
    
    dividend_type = SelectField(
        'Dividend Type',
        choices=[('REGULAR', 'Regular'), ('SPECIAL', 'Special')],
        default='REGULAR'
    )
    
    submit = SubmitField('Save Dividend')
    
    def validate_record_date(self, field):
        """Validate that record_date is after ex_dividend_date"""
        if self.ex_dividend_date.data and field.data:
            if field.data <= self.ex_dividend_date.data:
                raise ValidationError('Record date must be after ex-dividend date')
    
    def validate_payment_date(self, field):
        """Validate that payment_date is after record_date"""
        if self.record_date.data and field.data:
            if field.data <= self.record_date.data:
                raise ValidationError('Payment date must be after record date')
