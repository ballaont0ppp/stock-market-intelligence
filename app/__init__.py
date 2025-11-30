"""
Flask Application Factory
Creates and configures the Flask application instance
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='../static')
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register custom Jinja2 filters for XSS protection
    from app.utils.xss_protection import sanitize_url, sanitize_user_input
    app.jinja_env.filters['safe_url'] = sanitize_url
    app.jinja_env.filters['sanitize'] = sanitize_user_input
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.portfolio import bp as portfolio_bp
    from app.routes.orders import orders_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.api import bp as api_bp
    from app.routes.notifications import bp as notifications_bp
    from app.routes.pwa import bp as pwa_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(pwa_bp)
    
    # Register error handlers
    from app.utils import error_handlers
    error_handlers.register_error_handlers(app)
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers_to_response(response):
        """Add comprehensive security headers to all responses"""
        from app.utils.xss_protection import add_security_headers
        is_production = not app.debug and not app.testing
        response = add_security_headers(response, is_production=is_production)
        return response
    
    # Set up logging
    if not app.debug and not app.testing:
        from app.utils.logging_config import setup_logging
        setup_logging(app)
    
    # Start background jobs scheduler
    if app.config.get('JOBS_ENABLED', True):
        from app.jobs import scheduler
        scheduler.init_scheduler(app)
    
    # Register CLI commands
    from app import cli_commands
    cli_commands.register_commands(app)
    
    return app
