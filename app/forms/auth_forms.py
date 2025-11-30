"""
Authentication Forms
WTForms for user authentication and profile management
Mobile-optimized with proper input types for mobile keyboards
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
    ], render_kw={
        'type': 'email',
        'class': 'form-control',
        'placeholder': 'your@email.com',
        'autocomplete': 'email',
        'inputmode': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'At least 8 characters',
        'autocomplete': 'new-password'
    })
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Confirm your password',
        'autocomplete': 'new-password'
    })
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=255, message='Full name must be between 2 and 255 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Your full name',
        'autocomplete': 'name'
    })
    
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
    ], render_kw={
        'type': 'email',
        'class': 'form-control',
        'placeholder': 'your@email.com',
        'autocomplete': 'email',
        'inputmode': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Your password',
        'autocomplete': 'current-password'
    })
    
    remember_me = BooleanField('Remember Me', render_kw={
        'class': 'form-check-input'
    })


class ProfileForm(FlaskForm):
    """User profile update form"""
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=255, message='Full name must be between 2 and 255 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Your full name',
        'autocomplete': 'name'
    })
    
    risk_tolerance = SelectField('Risk Tolerance', 
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive')
        ],
        validators=[DataRequired(message='Please select your risk tolerance')],
        render_kw={
            'class': 'form-select'
        }
    )
    
    investment_goals = TextAreaField('Investment Goals', validators=[
        Optional(),
        Length(max=1000, message='Investment goals must be less than 1000 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Describe your investment goals',
        'rows': '4'
    })
    
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
        validators=[Optional()],
        render_kw={
            'class': 'form-select'
        }
    )
    
    # Notification preferences
    notify_dividends = BooleanField('Notify me about dividend payments', render_kw={
        'class': 'form-check-input'
    })
    notify_price_changes = BooleanField('Notify me about significant price movements (>5%)', render_kw={
        'class': 'form-check-input'
    })
    notify_weekly_summary = BooleanField('Send weekly portfolio summary', render_kw={
        'class': 'form-check-input'
    })


class NotificationPreferencesForm(FlaskForm):
    """Notification preferences form"""
    
    email_notifications = BooleanField('Email Notifications')
    dividend_alerts = BooleanField('Dividend Alerts')
    price_alerts = BooleanField('Price Alerts')


class PasswordChangeForm(FlaskForm):
    """Password change form"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Your current password',
        'autocomplete': 'current-password'
    })
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'At least 8 characters',
        'autocomplete': 'new-password'
    })
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Confirm your new password',
        'autocomplete': 'new-password'
    })
    
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

