"""
Error Handlers
Flask error handlers for common HTTP errors and error handling decorators
"""
import logging
from functools import wraps
from flask import render_template
from sqlalchemy.exc import SQLAlchemyError

from app.utils.exceptions import (
    ValidationError,
    BusinessLogicError,
    InsufficientFundsError,
    InsufficientSharesError,
    ExternalAPIError,
    StockNotFoundError
)

logger = logging.getLogger(__name__)


def handle_errors(error_category='general'):
    """
    Decorator for consistent error handling across services
    
    Args:
        error_category: Category of errors ('database', 'external_api', 'general')
    
    Returns:
        Decorated function with error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ValidationError, BusinessLogicError, InsufficientFundsError, 
                    InsufficientSharesError, StockNotFoundError) as e:
                # Re-raise business logic and validation errors
                logger.warning(f"{func.__name__} validation error: {str(e)}")
                raise
            except SQLAlchemyError as e:
                # Database errors
                from app import db
                db.session.rollback()
                logger.error(f"{func.__name__} database error: {str(e)}", exc_info=True)
                if error_category == 'database':
                    raise ValidationError("Database operation failed. Please try again.")
                raise
            except ExternalAPIError as e:
                # External API errors
                logger.error(f"{func.__name__} API error: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                # Unexpected errors
                logger.error(f"{func.__name__} unexpected error: {str(e)}", exc_info=True)
                raise ValidationError(f"An unexpected error occurred: {str(e)}")
        return wrapper
    return decorator


def register_error_handlers(app):
    """
    Register error handlers with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        from app import db
        db.session.rollback()
        app.logger.exception("Internal server error")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors (including CSRF failures)"""
        from flask import request, flash, redirect, url_for
        
        # Check if this is a CSRF error
        if 'csrf' in str(error).lower() or request.method == 'POST':
            app.logger.warning(f"CSRF validation failed for {request.path}")
            flash('Security validation failed. Please try again.', 'error')
            
            # Redirect to the referring page or home
            return redirect(request.referrer or url_for('dashboard.index'))
        
        return render_template('errors/400.html'), 400
