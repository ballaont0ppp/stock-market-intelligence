"""
Portfolio Forms
Forms for wallet management
Mobile-optimized with proper input types for mobile keyboards
"""
from flask_wtf import FlaskForm
from wtforms import DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional


class DepositForm(FlaskForm):
    """Form for depositing funds"""
    amount = DecimalField(
        'Amount',
        validators=[
            DataRequired(message='Amount is required'),
            NumberRange(min=0.01, message='Amount must be positive')
        ],
        places=2,
        render_kw={
            'class': 'form-control',
            'placeholder': '0.00',
            'inputmode': 'decimal',
            'type': 'number',
            'step': '0.01',
            'min': '0.01'
        }
    )
    description = TextAreaField(
        'Description',
        validators=[Optional()],
        default='Deposit',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Optional description',
            'rows': '3'
        }
    )
    submit = SubmitField('Deposit Funds')


class WithdrawForm(FlaskForm):
    """Form for withdrawing funds"""
    amount = DecimalField(
        'Amount',
        validators=[
            DataRequired(message='Amount is required'),
            NumberRange(min=0.01, message='Amount must be positive')
        ],
        places=2,
        render_kw={
            'class': 'form-control',
            'placeholder': '0.00',
            'inputmode': 'decimal',
            'type': 'number',
            'step': '0.01',
            'min': '0.01'
        }
    )
    description = TextAreaField(
        'Description',
        validators=[Optional()],
        default='Withdrawal',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Optional description',
            'rows': '3'
        }
    )
    submit = SubmitField('Withdraw Funds')
