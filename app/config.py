"""
Application Configuration
Defines configuration classes for different environments
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration with common settings"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database - Using SQLite (no password needed!)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "..", "portfolio.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Session Security
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # 24 hour session timeout
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    SESSION_COOKIE_SECURE = False  # Will be True in production with HTTPS
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Data Mode
    DATA_MODE = os.environ.get('DATA_MODE', 'LIVE')  # LIVE or STATIC
    SIMULATION_DATE = os.environ.get('SIMULATION_DATE')  # YYYY-MM-DD for STATIC mode
    STATIC_DATA_DIR = os.path.join(basedir, '..', 'data', 'stocks')
    
    # External APIs
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')
    
    # Sentiment Analysis
    SENTIMENT_ENABLED = os.environ.get('SENTIMENT_ENABLED', 'True').lower() == 'true'
    SENTIMENT_CACHE_DURATION = int(os.environ.get('SENTIMENT_CACHE_DURATION', 3600))
    SENTIMENT_TWEET_COUNT = int(os.environ.get('SENTIMENT_TWEET_COUNT', 100))
    SENTIMENT_SOURCES = ['TWITTER']
    
    # Trading
    COMMISSION_RATE = 0.001  # 0.1%
    MAX_ORDER_QUANTITY = 1000000
    MAX_DEPOSIT_AMOUNT = 1000000.00
    
    # Background Jobs
    SCHEDULER_API_ENABLED = True
    JOBS_ENABLED = os.environ.get('JOBS_ENABLED', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(basedir, '..', 'logs', 'app.log')
    
    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values - MUST be set in environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Stricter security for production
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    @classmethod
    def validate(cls):
        """Validate required environment variables"""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable must be set in production")
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    WTF_CSRF_ENABLED = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'  # Less verbose in production
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,  # Larger pool for production
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10
    }


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JOBS_ENABLED = False
    # SQLite doesn't support pool_size, so override with empty options
    SQLALCHEMY_ENGINE_OPTIONS = {}


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
