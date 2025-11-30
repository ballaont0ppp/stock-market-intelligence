"""
Logging Configuration
Sets up application logging with rotating file handler
"""
import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """
    Configure application logging with RotatingFileHandler
    
    Configures:
    - DEBUG, INFO, WARNING, ERROR log levels
    - Rotating file handler (10MB per file, 10 backups)
    - Format: timestamp, level, message, location
    - Creates logs/ directory if needed
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created logs directory: {log_dir}")
    
    # File handler with rotation (10MB per file, keep 10 backups)
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    # Set log format with timestamp, level, message, and location
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Set log level from config (DEBUG, INFO, WARNING, ERROR)
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    file_handler.setLevel(log_level)
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # Also add console handler for development
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        app.logger.addHandler(console_handler)
    
    app.logger.info('Stock Portfolio Platform startup')
    app.logger.info(f'Log level set to: {app.config["LOG_LEVEL"]}')
    app.logger.info(f'Logging to file: {app.config["LOG_FILE"]}')
