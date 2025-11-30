"""
Portfolio Forms
Forms for wallet management
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
        places=2
    )
    description = TextAreaField(
        'Description',
        validators=[Optional()],
        default='Deposit'
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
        places=2
    )
    description = TextAreaField(
        'Description',
        validators=[Optional()],
        default='Withdrawal'
    )
    submit = SubmitField('Withdraw Funds')
