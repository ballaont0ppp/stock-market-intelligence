"""
Report Forms
WTForms for generating reports
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime


class TransactionReportForm(FlaskForm):
    """Form for generating transaction reports"""
    start_date = DateField(
        'Start Date',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'type': 'date'}
    )
    
    end_date = DateField(
        'End Date',
        validators=[Optional()],
        default=datetime.utcnow,
        render_kw={'class': 'form-control', 'type': 'date'}
    )
    
    submit = SubmitField('Generate Report', render_kw={'class': 'btn btn-primary'})


class BillingReportForm(FlaskForm):
    """Form for generating billing reports"""
    month = SelectField(
        'Month',
        choices=[
            ('1', 'January'), ('2', 'February'), ('3', 'March'),
            ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    year = IntegerField(
        'Year',
        validators=[
            DataRequired(),
            NumberRange(min=2020, max=2100, message='Year must be between 2020 and 2100')
        ],
        default=datetime.utcnow().year,
        render_kw={'class': 'form-control', 'min': '2020', 'max': '2100'}
    )
    
    submit = SubmitField('Generate Report', render_kw={'class': 'btn btn-primary'})


class PerformanceReportForm(FlaskForm):
    """Form for generating performance reports"""
    period = SelectField(
        'Time Period',
        choices=[
            ('1w', '1 Week'),
            ('1m', '1 Month'),
            ('3m', '3 Months'),
            ('6m', '6 Months'),
            ('1y', '1 Year'),
            ('all', 'All Time')
        ],
        validators=[DataRequired()],
        default='1m',
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField('Generate Report', render_kw={'class': 'btn btn-primary'})
