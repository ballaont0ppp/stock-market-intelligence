# Code Documentation Guide

## Overview

This document provides comprehensive documentation for the Stock Portfolio Management Platform codebase. It covers architecture, key components, and usage patterns.

## Architecture Overview

The application follows a layered architecture:

```
Presentation Layer (Templates + Static Assets)
    ↓
Application Layer (Flask Routes/Blueprints)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (SQLAlchemy Models)
    ↓
Database Layer (MySQL)
```

## Core Components

### 1. Authentication System (`app/services/auth_service.py`)

**Purpose**: Handle user registration, login, session management, and authorization.

**Key Classes**:
- `AuthService`: Core authentication logic

**Key Methods**:
- `register_user(email, password, full_name)`: Create new user account with hashed password
- `authenticate_user(email, password)`: Verify credentials and return user object
- `hash_password(password)`: Generate bcrypt hash (work factor 12)
- `verify_password(password, hash)`: Verify password against stored hash

**Security Features**:
- Bcrypt password hashing
- Session management via Flask-Login
- Rate limiting on login attempts (5 per 15 minutes)
- CSRF protection on all forms

**Usage Example**:
```python
from app.services.auth_service import AuthService

auth_service = AuthService()
user = auth_service.register_user('user@example.com', 'SecurePass123!', 'John Doe')
authenticated = auth_service.authenticate_user('user@example.com', 'SecurePass123!')
```

### 2. Portfolio Service (`app/services/portfolio_service.py`)

**Purpose**: Manage user holdings, calculate valuations, track performance.

**Key Methods**:
- `get_wallet_balance(user_id)`: Retrieve current wallet balance
- `deposit_funds(user_id, amount, description)`: Add funds to wallet
- `withdraw_funds(user_id, amount, description)`: Remove funds from wallet
- `get_holdings(user_id)`: Fetch all user stock holdings
- `get_portfolio_value(user_id)`: Calculate total portfolio value at current prices
- `calculate_unrealized_gains(user_id)`: Calculate gains/losses for each holding
- `get_portfolio_summary(user_id)`: Aggregate portfolio metrics

**Database Locking**:
Uses row-level locking (`SELECT FOR UPDATE`) to prevent race conditions during concurrent transactions.

**Usage Example**:
```python
from app.services.portfolio_service import PortfolioService

portfolio_service = PortfolioService()
balance = portfolio_service.get_wallet_balance(user_id=1)
portfolio_service.deposit_funds(user_id=1, amount=10000.00, description='Initial deposit')
holdings = portfolio_service.get_holdings(user_id=1)
```

### 3. Transaction Engine (`app/services/transaction_engine.py`)

**Purpose**: Process buy/sell orders, manage order lifecycle, ensure data consistency.

**Key Methods**:
- `create_buy_order(user_id, symbol, quantity)`: Create and execute buy order
- `create_sell_order(user_id, symbol, quantity)`: Create and execute sell order
- `validate_buy_order(order)`: Check wallet balance and order validity
- `validate_sell_order(order)`: Check holdings quantity and order validity
- `execute_buy_order(order)`: Atomic transaction for buy execution
- `execute_sell_order(order)`: Atomic transaction for sell execution
- `calculate_commission(amount)`: Calculate 0.1% commission fee

**Order Processing Flow**:
1. Create Order record (status=PENDING)
2. Fetch current market price
3. Calculate total cost/proceeds and commission
4. Acquire database locks
5. Validate order (balance/holdings check)
6. Execute atomic transaction (update wallet, holdings, create transactions)
7. Update Order status (COMPLETED/FAILED)

**Usage Example**:
```python
from app.services.transaction_engine import TransactionEngine

engine = TransactionEngine()
order = engine.create_buy_order(user_id=1, symbol='AAPL', quantity=10)
# Returns Order object with status COMPLETED or FAILED
```

### 4. Stock Repository (`app/services/stock_repository.py`)

**Purpose**: Manage company data, price history, background price updates.

**Key Methods**:
- `get_company_by_symbol(symbol)`: Fetch company by stock symbol
- `create_company(symbol, data)`: Add new company to database
- `get_current_price(symbol)`: Get latest price (cached or live)
- `fetch_live_price(symbol)`: Fetch real-time price from yfinance
- `get_price_history(symbol, start_date, end_date)`: Retrieve historical prices
- `update_price_history(symbol, data)`: Store price data in database
- `search_companies(query, filters)`: Search companies with pagination

**Data Modes**:
- **LIVE**: Fetch real-time data from yfinance API
- **STATIC**: Use pre-downloaded CSV files for testing

**Configuration**:
```python
# config.py
DATA_MODE = 'LIVE'  # or 'STATIC'
SIMULATION_DATE = None  # Used when DATA_MODE='STATIC'
```

### 5. Prediction Service (`app/services/prediction_service.py`)

**Purpose**: Integrate ML models, provide unified prediction interface.

**Supported Models**:
- ARIMA: Time series forecasting
- LSTM: Deep learning neural network
- Linear Regression: Statistical regression

**Key Methods**:
- `predict_stock_price(symbol, models)`: Run predictions using specified models
- `get_historical_data(symbol, period)`: Fetch historical data for training
- `generate_forecast(symbol, days)`: Multi-day price forecast
- `calculate_model_accuracy(predictions, actual)`: Evaluate model performance

**Response Format**:
```python
{
    'symbol': 'AAPL',
    'current_price': 175.43,
    'predictions': {
        'ARIMA': {'price': 178.20, 'error': 2.45},
        'LSTM': {'price': 176.80, 'error': 1.89},
        'LR': {'price': 177.50, 'error': 2.12}
    },
    'forecast': [176.5, 177.2, 178.0, ...],
    'sentiment': {...},
    'visualizations': {...}
}
```

### 6. Sentiment Engine (`app/services/sentiment_engine.py`)

**Purpose**: Analyze market sentiment from Twitter, cache results.

**Key Methods**:
- `analyze_sentiment(symbol)`: Get sentiment analysis for stock
- `get_cached_sentiment(symbol)`: Check cache for existing analysis
- `fetch_tweets(symbol, count)`: Search Twitter for relevant tweets
- `clean_tweet(text)`: Remove URLs, mentions, emojis
- `calculate_polarity(tweets)`: Analyze sentiment using TextBlob

**Caching Strategy**:
- Cache duration: 1 hour (configurable)
- Reduces API calls and improves performance
- Falls back to expired cache if API fails

**Configuration**:
```python
# .env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# config.py
SENTIMENT_ENABLED = True
SENTIMENT_CACHE_DURATION = 3600  # seconds
SENTIMENT_TWEET_COUNT = 100
```

### 7. Admin Service (`app/services/admin_service.py`)

**Purpose**: Administrative functions for user, company, broker, and system management.

**User Management**:
- `get_all_users(filters, pagination)`: List all users with filtering
- `get_user_details(user_id)`: Complete user profile and activity
- `update_user(user_id, data)`: Modify user information
- `suspend_user(user_id, reason)`: Suspend user account
- `activate_user(user_id)`: Reactivate suspended account
- `adjust_wallet_balance(user_id, amount, reason)`: Manual balance adjustment

**Company Management**:
- `get_all_companies(filters, pagination)`: List all companies
- `create_company(data)`: Add new company with yfinance data
- `update_company(company_id, data)`: Modify company details
- `deactivate_company(company_id)`: Soft delete company
- `bulk_import_companies(csv_file)`: Import companies from CSV

**System Monitoring**:
- `get_system_metrics()`: Dashboard overview metrics
- `get_transaction_monitoring(filters)`: Real-time transaction feed
- `get_api_usage_stats()`: API call statistics
- `get_audit_log(filters)`: Admin action history

### 8. Background Jobs (`app/jobs/`)

**Price Updater** (`price_updater.py`):
- Daily price update: 4:30 PM EST on weekdays
- Intraday refresh: Every 15 minutes during market hours
- Fetches prices for all actively traded stocks
- Stores in PriceHistory table

**Dividend Processor** (`dividend_processor.py`):
- Runs daily at 4:00 PM EST
- Checks for dividends with payment_date = today
- Calculates and distributes payments to users
- Creates transaction records and notifications

**Scheduler** (`scheduler.py`):
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(update_daily_prices, trigger='cron', 
                  day_of_week='mon-fri', hour=16, minute=30)
scheduler.start()
```

## Database Models

### User Model (`app/models/user.py`)

```python
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    risk_tolerance = db.Column(db.Enum('conservative', 'moderate', 'aggressive'))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False)
    holdings = db.relationship('Holdings', backref='user')
    orders = db.relationship('Order', backref='user')
```

### Wallet Model (`app/models/wallet.py`)

```python
class Wallet(db.Model):
    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    balance = db.Column(db.Numeric(15, 2), default=100000.00)
    total_deposited = db.Column(db.Numeric(15, 2), default=100000.00)
    total_withdrawn = db.Column(db.Numeric(15, 2), default=0.00)
    
    __table_args__ = (
        db.CheckConstraint('balance >= 0', name='check_positive_balance'),
    )
```

### Order Model (`app/models/order.py`)

```python
class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    order_type = db.Column(db.Enum('BUY', 'SELL'))
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2))
    commission_fee = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(15, 2))
    order_status = db.Column(db.Enum('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    failure_reason = db.Column(db.Text)
```

## Configuration

### Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost/portfolio_db

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Twitter API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Data Mode
DATA_MODE=LIVE  # or STATIC
```

### Application Configuration (`app/config.py`)

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_COOKIE_SECURE = True  # Production only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Data Mode
    DATA_MODE = os.environ.get('DATA_MODE', 'LIVE')
    
    # Sentiment Analysis
    SENTIMENT_ENABLED = True
    SENTIMENT_CACHE_DURATION = 3600
    SENTIMENT_TWEET_COUNT = 100
```

## Error Handling

### Custom Exceptions (`app/utils/exceptions.py`)

```python
class ValidationError(Exception):
    """Raised when user input validation fails"""
    pass

class InsufficientFundsError(Exception):
    """Raised when wallet balance is insufficient"""
    pass

class InsufficientSharesError(Exception):
    """Raised when user doesn't own enough shares"""
    pass

class StockNotFoundError(Exception):
    """Raised when stock symbol is not found"""
    pass
```

### Error Handler Decorator

```python
from functools import wraps

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(request.referrer or url_for('dashboard.index'))
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('An unexpected error occurred', 'error')
            return redirect(url_for('dashboard.index'))
    return decorated_function
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services/test_auth_service.py

# Run specific test
pytest tests/test_services/test_auth_service.py::test_register_user
```

### Test Structure

```
tests/
├── conftest.py              # Fixtures and configuration
├── test_models/             # Model tests
├── test_services/           # Service layer tests
├── test_routes/             # Route/endpoint tests
└── test_integration/        # Integration tests
```

### Writing Tests

```python
import pytest
from app.services.auth_service import AuthService

def test_register_user(app, db):
    """Test user registration creates user with hashed password"""
    auth_service = AuthService()
    user = auth_service.register_user(
        email='test@example.com',
        password='SecurePass123!',
        full_name='Test User'
    )
    
    assert user.email == 'test@example.com'
    assert user.password_hash != 'SecurePass123!'
    assert user.full_name == 'Test User'
```

## Deployment

### Production Checklist

1. Set `FLASK_ENV=production`
2. Use strong `SECRET_KEY`
3. Enable `SESSION_COOKIE_SECURE=True`
4. Configure production database
5. Set up HTTPS/SSL certificates
6. Configure firewall rules
7. Set up monitoring and logging
8. Configure backup procedures
9. Test disaster recovery plan

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## Performance Optimization

### Database Query Optimization

- Use eager loading for relationships: `db.session.query(User).options(joinedload(User.wallet))`
- Add indexes on frequently queried columns
- Use pagination for large result sets
- Implement query result caching

### Caching Strategy

- Sentiment analysis: 1 hour cache
- Stock prices: 15 minute cache during market hours
- User sessions: 24 hour expiry

### Background Job Optimization

- Use connection pooling
- Implement retry logic with exponential backoff
- Process items in batches
- Log execution metrics

## Security Best Practices

1. **Password Security**: Bcrypt hashing with work factor 12
2. **Session Security**: HttpOnly, Secure, SameSite cookies
3. **CSRF Protection**: Enabled on all forms
4. **SQL Injection**: Use parameterized queries via ORM
5. **XSS Prevention**: Jinja2 auto-escaping enabled
6. **Rate Limiting**: Implemented on authentication endpoints
7. **Input Validation**: Validate and sanitize all user inputs
8. **Security Headers**: X-Content-Type-Options, X-Frame-Options, etc.

## Troubleshooting

### Common Issues

**Database Connection Errors**:
- Check DATABASE_URL in .env
- Verify MySQL server is running
- Check firewall rules

**Twitter API Errors**:
- Verify API credentials in .env
- Check API rate limits
- Ensure Twitter Developer account is active

**Background Jobs Not Running**:
- Check scheduler is started in app/__init__.py
- Verify job execution logs
- Check system timezone configuration

## Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- APScheduler Documentation: https://apscheduler.readthedocs.io/
- yfinance Documentation: https://pypi.org/project/yfinance/
- Tweepy Documentation: https://docs.tweepy.org/
