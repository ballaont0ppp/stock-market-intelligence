"""
Authentication Forms
WTForms for user authentication and profile management
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models.user import User


class RegistrationForm(FlaskForm):
    """User registration form"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=255, message='Email must be less than 255 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=255, message='Full name must be between 2 and 255 characters')
    ])
    
    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('Email already registered. Please use a different email or login.')
    
    def validate_password(self, field):
        """Validate password strength"""
        password = field.data
        
        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number')


class LoginForm(FlaskForm):
    """User login form"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')


class ProfileForm(FlaskForm):
    """User profile update form"""
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=255, message='Full name must be between 2 and 255 characters')
    ])
    
    risk_tolerance = SelectField('Risk Tolerance', 
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive')
        ],
        validators=[DataRequired(message='Please select your risk tolerance')]
    )
    
    investment_goals = TextAreaField('Investment Goals', validators=[
        Optional(),
        Length(max=1000, message='Investment goals must be less than 1000 characters')
    ])
    
    preferred_sectors = SelectMultipleField('Preferred Sectors',
        choices=[
            ('Technology', 'Technology'),
            ('Healthcare', 'Healthcare'),
            ('Finance', 'Finance'),
            ('Energy', 'Energy'),
            ('Consumer', 'Consumer'),
            ('Industrial', 'Industrial'),
            ('Real Estate', 'Real Estate'),
            ('Utilities', 'Utilities')
        ],
        validators=[Optional()]
    )
    
    # Notification preferences
    notify_dividends = BooleanField('Notify me about dividend payments')
    notify_price_changes = BooleanField('Notify me about significant price movements (>5%)')
    notify_weekly_summary = BooleanField('Send weekly portfolio summary')


class PasswordChangeForm(FlaskForm):
    """Password change form"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    def validate_new_password(self, field):
        """Validate new password strength"""
        password = field.data
        
        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number')

