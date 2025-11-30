"""
Custom Decorators
Provides decorators for route protection and access control
"""
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def login_required(f):
    """
    Decorator to require user authentication
    Redirects to login page if user is not authenticated
    
    Note: Flask-Login already provides @login_required, but this is a custom implementation
    that can be extended with additional logic if needed.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges
    Returns 403 Forbidden if user is not an admin
    
    Usage:
        @bp.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def active_account_required(f):
    """
    Decorator to require active account status
    Returns 403 Forbidden if account is suspended
    
    Usage:
        @bp.route('/orders/buy')
        @active_account_required
        def buy_order():
            return render_template('orders/buy.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        
        if current_user.account_status != 'active':
            flash('Your account has been suspended. Please contact support.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

