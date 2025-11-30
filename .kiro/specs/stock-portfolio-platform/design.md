# Design Document: Stock Portfolio Management Platform

## Overview

This design document outlines the architecture and implementation strategy for transforming the existing stock market prediction application into a comprehensive portfolio management platform. The system will integrate user authentication, database persistence (MySQL), virtual portfolio management, transaction processing, dividend tracking, broker administration, and enhanced sentiment analysis.

### Current State

The existing application provides:
- Flask-based web interface
- ML prediction models (LSTM, ARIMA, Linear Regression)
- Basic sentiment analysis (stubbed due to Twitter API limitations)
- Live data fetching via yfinance
- Visualization of predictions and trends

### Target State

The enhanced platform will add:
- User authentication and authorization system
- MySQL database with comprehensive schema
- Virtual wallet and portfolio management
- Simulated stock trading (buy/sell orders)
- Transaction history and reporting
- Dividend tracking and distribution
- Admin/broker dashboard with CRUD operations
- System monitoring and analytics
- Enhanced sentiment analysis with caching
- Static dataset mode for testing
- Responsive UI with improved navigation

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  (Flask Templates + Bootstrap 5 + JavaScript)               │
│  - User Pages: Dashboard, Portfolio, Orders, Reports        │
│  - Admin Pages: User Mgmt, Company Mgmt, Broker Mgmt       │
│  - Public Pages: Home, Login, Register                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                    (Flask Application)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │  Portfolio   │  │  Transaction │     │
│  │   Service    │  │   Service    │  │   Engine     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Prediction  │  │  Sentiment   │  │   Admin      │     │
│  │   Service    │  │   Engine     │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Access Layer                       │
│                   (SQLAlchemy ORM Models)                   │
│  User, Company, Wallet, Holdings, Order, Transaction,       │
│  Dividend, Broker, Notification, SentimentCache             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Persistence Layer                        │
│                      (MySQL Database)                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│  - yfinance API (stock data)                                │
│  - Twitter API v2 (sentiment analysis)                      │
│  - Background Jobs (APScheduler)                            │
└─────────────────────────────────────────────────────────────┘
```


### Technology Stack

**Backend:**
- Flask 2.3.3 (Web framework)
- SQLAlchemy 3.0.5 (ORM)
- Flask-Migrate (Database migrations)
- Flask-Login (Session management)
- Flask-WTF (Forms and CSRF protection)
- Flask-Bcrypt (Password hashing)
- APScheduler (Background jobs)

**Database:**
- MySQL 8.0+ (Primary database)
- InnoDB storage engine (ACID compliance)

**ML/Data Processing:**
- TensorFlow 2.13.0 + Keras 2.13.1 (LSTM model)
- statsmodels 0.14.0 (ARIMA model)
- scikit-learn 1.3.0 (Linear Regression, preprocessing)
- pandas 2.0.3, numpy 1.24.3 (Data manipulation)

**External APIs:**
- yfinance 0.2.18 (Stock data)
- tweepy 4.14.0 (Twitter API v2)
- textblob 0.17.1 (Sentiment analysis)

**Frontend:**
- Bootstrap 5 (Responsive UI framework)
- Chart.js (Interactive charts)
- jQuery (DOM manipulation)
- Jinja2 templates (Server-side rendering)

**Visualization:**
- matplotlib 3.7.2 (Static charts)
- seaborn 0.12.2 (Statistical visualizations)

### Directory Structure

```
stock-portfolio-platform/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── wallet.py
│   │   ├── holding.py
│   │   ├── order.py
│   │   ├── transaction.py
│   │   ├── dividend.py
│   │   ├── broker.py
│   │   ├── notification.py
│   │   └── sentiment_cache.py
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── portfolio_service.py
│   │   ├── transaction_engine.py
│   │   ├── prediction_service.py
│   │   ├── sentiment_engine.py
│   │   ├── admin_service.py
│   │   └── stock_repository.py
│   ├── routes/                  # Flask blueprints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── portfolio.py
│   │   ├── orders.py
│   │   ├── reports.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── forms/                   # WTForms
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── order_forms.py
│   │   └── admin_forms.py
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── jobs/                    # Background jobs
│       ├── __init__.py
│       ├── price_updater.py
│       └── dividend_processor.py
├── ml_models/                   # Existing ML code (refactored)
│   ├── __init__.py
│   ├── arima_model.py
│   ├── lstm_model.py
│   ├── linear_regression_model.py
│   └── stock_data_processor.py
├── templates/                   # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── portfolio/
│   ├── orders/
│   ├── reports/
│   └── admin/
├── static/                      # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── plots/
├── migrations/                  # Alembic migrations
├── data/                        # Static datasets (optional)
│   └── stocks/
├── tests/                       # Unit and integration tests
├── run.py                       # Application entry point
├── requirements.txt
└── .env                         # Environment variables
```


## Components and Interfaces

### 1. Authentication System

**Purpose:** Handle user registration, login, session management, and authorization.

**Components:**
- `AuthService`: Core authentication logic
- `User` model: User data persistence
- `auth` blueprint: Routes for login/register/logout
- `@login_required` decorator: Protect routes
- `@admin_required` decorator: Admin-only access

**Key Methods:**

```python
class AuthService:
    def register_user(email, password, full_name) -> User
    def authenticate_user(email, password) -> User | None
    def hash_password(password) -> str
    def verify_password(password, hash) -> bool
    def create_session(user) -> None
    def destroy_session() -> None
    def get_current_user() -> User | None
    def update_profile(user_id, data) -> User
    def change_password(user_id, old_pass, new_pass) -> bool
```

**Security Features:**
- Bcrypt password hashing (work factor 12)
- CSRF protection on all forms
- Session cookies: HttpOnly, Secure (production), SameSite=Lax
- Rate limiting on login (5 attempts per 15 minutes)
- Parameterized queries (SQL injection prevention)

**Database Schema:**

```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    risk_tolerance ENUM('conservative', 'moderate', 'aggressive') DEFAULT 'moderate',
    investment_goals TEXT,
    preferred_sectors JSON,
    notification_preferences JSON,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    account_status ENUM('active', 'suspended') DEFAULT 'active',
    INDEX idx_email (email)
) ENGINE=InnoDB;
```

### 2. Portfolio Management System

**Purpose:** Manage user holdings, calculate valuations, track performance.

**Components:**
- `PortfolioService`: Portfolio business logic
- `Wallet`, `Holdings` models: Data persistence
- `portfolio` blueprint: Portfolio routes

**Key Methods:**

```python
class PortfolioService:
    def get_wallet_balance(user_id) -> Decimal
    def deposit_funds(user_id, amount, description) -> Transaction
    def withdraw_funds(user_id, amount, description) -> Transaction
    def get_holdings(user_id) -> List[Holdings]
    def get_portfolio_value(user_id) -> Decimal
    def calculate_unrealized_gains(user_id) -> Dict
    def get_portfolio_summary(user_id) -> Dict
    def get_performance_metrics(user_id) -> Dict
    def get_sector_allocation(user_id) -> Dict
```

**Database Schema:**

```sql
CREATE TABLE wallets (
    wallet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    balance DECIMAL(15,2) DEFAULT 100000.00 CHECK (balance >= 0),
    currency VARCHAR(3) DEFAULT 'USD',
    total_deposited DECIMAL(15,2) DEFAULT 100000.00,
    total_withdrawn DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    average_purchase_price DECIMAL(10,2) NOT NULL,
    total_invested DECIMAL(15,2) NOT NULL,
    first_purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_company (user_id, company_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE RESTRICT,
    INDEX idx_user (user_id),
    INDEX idx_company (company_id)
) ENGINE=InnoDB;
```


### 3. Transaction Engine

**Purpose:** Process buy/sell orders, manage order lifecycle, ensure data consistency.

**Components:**
- `TransactionEngine`: Order processing logic
- `Order`, `Transaction` models: Data persistence
- `orders` blueprint: Order routes

**Key Methods:**

```python
class TransactionEngine:
    def create_buy_order(user_id, symbol, quantity) -> Order
    def create_sell_order(user_id, symbol, quantity) -> Order
    def validate_buy_order(order) -> Tuple[bool, str]
    def validate_sell_order(order) -> Tuple[bool, str]
    def execute_buy_order(order) -> bool
    def execute_sell_order(order) -> bool
    def calculate_commission(amount) -> Decimal  # 0.1% commission
    def get_order_history(user_id, filters) -> List[Order]
    def get_transaction_history(user_id, filters) -> List[Transaction]
    def cancel_order(order_id) -> bool
```

**Order Processing Flow:**

```
1. User submits order (symbol, quantity, type)
2. Create Order record (status=PENDING)
3. Fetch current market price (PriceHistory or yfinance)
4. Calculate total cost/proceeds and commission
5. Acquire database locks (SELECT FOR UPDATE)
6. Validate order:
   - BUY: Check wallet balance >= total_cost
   - SELL: Check holdings quantity >= sell_quantity
7. If validation fails:
   - Update Order status=FAILED with reason
   - Rollback transaction
   - Return error message
8. If validation passes:
   - Update wallet balance
   - Update/Create holdings record
   - Create transaction records (main + commission)
   - Update Order status=COMPLETED
   - Commit transaction
9. Return success message with details
```

**Database Schema:**

```sql
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    order_type ENUM('BUY', 'SELL') NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_per_share DECIMAL(10,2) NOT NULL,
    commission_fee DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    order_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP NULL,
    failure_reason TEXT,
    realized_gain_loss DECIMAL(15,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE RESTRICT,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_status (order_status)
) ENGINE=InnoDB;

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_type ENUM('BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAWAL', 'FEE') NOT NULL,
    order_id INT NULL,
    company_id INT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_type (transaction_type)
) ENGINE=InnoDB;
```

### 4. Stock Repository

**Purpose:** Manage company data, price history, background price updates.

**Components:**
- `StockRepository`: Stock data management
- `Company`, `PriceHistory` models: Data persistence
- Background jobs: Price refresh scheduler

**Key Methods:**

```python
class StockRepository:
    def get_company_by_symbol(symbol) -> Company | None
    def create_company(symbol, data) -> Company
    def update_company(company_id, data) -> Company
    def get_current_price(symbol) -> Decimal
    def get_price_history(symbol, start_date, end_date) -> List[PriceHistory]
    def fetch_live_price(symbol) -> Decimal  # yfinance
    def fetch_historical_data(symbol, period) -> pd.DataFrame
    def update_price_history(symbol, data) -> None
    def search_companies(query, filters) -> List[Company]
    def get_trending_stocks(limit) -> List[Company]
```

**Data Mode Support:**

```python
# config.py
DATA_MODE = 'LIVE'  # or 'STATIC'
SIMULATION_DATE = None  # Used when DATA_MODE='STATIC'

# In StockRepository
def get_current_price(self, symbol):
    if config.DATA_MODE == 'STATIC':
        return self._get_static_price(symbol, config.SIMULATION_DATE)
    else:
        return self._get_live_price(symbol)
```

**Database Schema:**

```sql
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    website VARCHAR(255),
    ceo VARCHAR(255),
    employees INT,
    founded_year INT,
    headquarters VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_symbol (symbol),
    INDEX idx_sector (sector)
) ENGINE=InnoDB;

CREATE TABLE price_history (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    adjusted_close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_date (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    INDEX idx_company_date (company_id, date)
) ENGINE=InnoDB;
```


### 5. Prediction Service

**Purpose:** Integrate existing ML models, provide unified prediction interface.

**Components:**
- `PredictionService`: Orchestrates ML models
- Existing models: `ARIMAModel`, `LSTMModel`, `LinearRegressionModel`
- `StockDataProcessor`: Data preprocessing

**Key Methods:**

```python
class PredictionService:
    def __init__(self):
        self.arima_model = ARIMAModel()
        self.lstm_model = LSTMModel()
        self.lr_model = LinearRegressionModel()
        self.data_processor = StockDataProcessor()
    
    def predict_stock_price(symbol, models=['ARIMA', 'LSTM', 'LR']) -> Dict
    def get_historical_data(symbol, period='2y') -> pd.DataFrame
    def preprocess_data(df, symbol) -> pd.DataFrame
    def generate_forecast(symbol, days=7) -> Dict
    def calculate_model_accuracy(predictions, actual) -> Dict
```

**Prediction Response Format:**

```python
{
    'symbol': 'AAPL',
    'current_price': 175.43,
    'predictions': {
        'ARIMA': {'price': 178.20, 'error': 2.45},
        'LSTM': {'price': 176.80, 'error': 1.89},
        'LR': {'price': 177.50, 'error': 2.12}
    },
    'forecast': [176.5, 177.2, 178.0, 179.1, 180.3, 181.2, 182.0],
    'sentiment': {
        'polarity': 0.15,
        'label': 'Overall Positive',
        'distribution': {'positive': 45, 'negative': 20, 'neutral': 35}
    },
    'recommendation': {
        'action': 'BUY',
        'confidence': 'MODERATE',
        'reasoning': 'Positive sentiment and upward price trend'
    },
    'visualizations': {
        'arima_plot': '/static/plots/ARIMA_AAPL.png',
        'lstm_plot': '/static/plots/LSTM_AAPL.png',
        'lr_plot': '/static/plots/LR_AAPL.png',
        'trends_plot': '/static/plots/Trends_AAPL.png',
        'sentiment_plot': '/static/plots/SA_AAPL.png'
    }
}
```

**Integration with Existing Code:**

The existing ML models (`arima_model.py`, `lstm_model.py`, `linear_regression_model.py`) will be:
1. Moved to `ml_models/` directory
2. Refactored to use consistent interfaces
3. Wrapped by `PredictionService` for unified access
4. Enhanced with better error handling and logging

### 6. Sentiment Engine

**Purpose:** Analyze market sentiment from Twitter, cache results, provide sentiment scores.

**Components:**
- `SentimentEngine`: Sentiment analysis logic
- `SentimentCache` model: Cache sentiment results
- Twitter API v2 integration via tweepy

**Key Methods:**

```python
class SentimentEngine:
    def __init__(self):
        self.twitter_client = self._init_twitter_client()
        self.cache_duration = 3600  # 1 hour
    
    def analyze_sentiment(symbol) -> Dict
    def get_cached_sentiment(symbol) -> Dict | None
    def fetch_tweets(symbol, count=100) -> List[str]
    def clean_tweet(text) -> str
    def calculate_polarity(tweets) -> Dict
    def store_sentiment_cache(symbol, data) -> None
    def is_cache_valid(cache_entry) -> bool
```

**Sentiment Analysis Flow:**

```
1. Check SentimentCache for valid cached data
2. If cache hit and not expired:
   - Return cached sentiment data
3. If cache miss or expired:
   - Fetch company name from Companies table
   - Search Twitter for tweets (symbol OR company_name)
   - Clean tweets (remove URLs, mentions, emojis)
   - Calculate polarity using TextBlob
   - Classify tweets (positive/negative/neutral)
   - Generate visualization (pie chart)
   - Store in SentimentCache with expiry
   - Return sentiment data
4. Handle API errors gracefully:
   - Auth failure: Log error, return neutral sentiment
   - Rate limit: Use expired cache if available
   - Network error: Retry with exponential backoff
```

**Database Schema:**

```sql
CREATE TABLE sentiment_cache (
    cache_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    source ENUM('TWITTER', 'NEWS', 'REDDIT') DEFAULT 'TWITTER',
    polarity_score DECIMAL(3,2) NOT NULL,
    positive_count INT NOT NULL,
    negative_count INT NOT NULL,
    neutral_count INT NOT NULL,
    sample_texts JSON,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    INDEX idx_company_source_expiry (company_id, source, expires_at)
) ENGINE=InnoDB;
```

**Configuration:**

```python
# config.py
SENTIMENT_ENABLED = True
SENTIMENT_CACHE_DURATION = 3600  # seconds
SENTIMENT_TWEET_COUNT = 100
SENTIMENT_SOURCES = ['TWITTER']

# .env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```


### 7. Dividend Manager

**Purpose:** Track dividend announcements, calculate payments, distribute to users.

**Components:**
- `DividendManager`: Dividend processing logic
- `Dividend`, `DividendPayment` models: Data persistence
- Background job: Daily dividend processor

**Key Methods:**

```python
class DividendManager:
    def create_dividend(company_id, data) -> Dividend
    def update_dividend(dividend_id, data) -> Dividend
    def delete_dividend(dividend_id) -> bool
    def get_upcoming_dividends() -> List[Dividend]
    def process_dividend_payments(dividend_id) -> List[DividendPayment]
    def calculate_user_dividend(user_id, dividend) -> Decimal
    def distribute_dividend(dividend_id) -> Dict
```

**Dividend Processing Flow:**

```
1. Daily job runs at 4:00 PM EST
2. Query dividends WHERE payment_date = TODAY
3. For each dividend:
   a. Get all users with holdings for that company
   b. For each user:
      - Calculate: amount = dividend_per_share * quantity_owned
      - Add amount to user's wallet balance
      - Create Transaction record (type=DIVIDEND)
      - Create DividendPayment record
      - Create Notification for user
   c. Log summary: total users paid, total amount distributed
4. Handle errors: Log failures, continue processing remaining dividends
```

**Database Schema:**

```sql
CREATE TABLE dividends (
    dividend_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    dividend_per_share DECIMAL(10,4) NOT NULL CHECK (dividend_per_share > 0),
    payment_date DATE NOT NULL,
    record_date DATE NOT NULL,
    ex_dividend_date DATE NOT NULL,
    announcement_date DATE,
    dividend_type ENUM('REGULAR', 'SPECIAL') DEFAULT 'REGULAR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    INDEX idx_company_payment (company_id, payment_date),
    CHECK (payment_date > record_date AND record_date > ex_dividend_date)
) ENGINE=InnoDB;

CREATE TABLE dividend_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    dividend_id INT NOT NULL,
    user_id INT NOT NULL,
    holding_id INT NOT NULL,
    shares_owned INT NOT NULL,
    amount_paid DECIMAL(15,2) NOT NULL,
    transaction_id INT NOT NULL,
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dividend_id) REFERENCES dividends(dividend_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (holding_id) REFERENCES holdings(holding_id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_dividend (dividend_id)
) ENGINE=InnoDB;
```

### 8. Admin Service

**Purpose:** Provide administrative functions for user, company, broker, and system management.

**Components:**
- `AdminService`: Admin business logic
- `Broker`, `Notification` models: Data persistence
- `admin` blueprint: Admin routes
- `@admin_required` decorator: Access control

**Key Methods:**

```python
class AdminService:
    # User Management
    def get_all_users(filters, pagination) -> List[User]
    def get_user_details(user_id) -> Dict
    def update_user(user_id, data) -> User
    def suspend_user(user_id, reason) -> bool
    def activate_user(user_id) -> bool
    def delete_user(user_id) -> bool
    def adjust_wallet_balance(user_id, amount, reason) -> Transaction
    
    # Company Management
    def get_all_companies(filters, pagination) -> List[Company]
    def create_company(data) -> Company
    def update_company(company_id, data) -> Company
    def deactivate_company(company_id) -> bool
    def bulk_import_companies(csv_file) -> Dict
    
    # Broker Management
    def get_all_brokers(filters) -> List[Broker]
    def create_broker(user_id, data) -> Broker
    def update_broker(broker_id, data) -> Broker
    def deactivate_broker(broker_id) -> bool
    def assign_user_to_broker(user_id, broker_id) -> bool
    
    # System Monitoring
    def get_system_metrics() -> Dict
    def get_transaction_monitoring(filters) -> List[Transaction]
    def get_audit_log(filters) -> List[AuditLog]
    def get_api_usage_stats() -> Dict
```

**System Metrics Response:**

```python
{
    'users': {
        'total': 1250,
        'active': 980,
        'new_today': 15,
        'suspended': 5
    },
    'transactions': {
        'today': 342,
        'volume_today': 1250000.00,
        'total_volume': 45000000.00
    },
    'portfolio': {
        'total_value': 125000000.00,
        'total_holdings': 5420
    },
    'system_health': {
        'database': 'green',
        'api': 'green',
        'ml_models': 'yellow',
        'overall': 'green'
    },
    'top_stocks': [
        {'symbol': 'AAPL', 'trades': 145},
        {'symbol': 'GOOGL', 'trades': 98},
        ...
    ]
}
```

**Database Schema:**

```sql
CREATE TABLE brokers (
    broker_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    broker_name VARCHAR(255) NOT NULL,
    license_number VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    assigned_users_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type ENUM('TRANSACTION', 'DIVIDEND', 'PRICE_ALERT', 'SYSTEM') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_unread (user_id, is_read, created_at)
) ENGINE=InnoDB;
```


### 9. Background Jobs

**Purpose:** Automate periodic tasks like price updates and dividend processing.

**Components:**
- APScheduler: Job scheduling framework
- `PriceUpdater`: Daily and intraday price refresh
- `DividendProcessor`: Daily dividend distribution
- `JobLog` model: Track job execution history

**Job Definitions:**

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# Daily price update - runs at 4:30 PM EST on weekdays
scheduler.add_job(
    func=update_daily_prices,
    trigger=CronTrigger(day_of_week='mon-fri', hour=16, minute=30, timezone='US/Eastern'),
    id='daily_price_update',
    name='Daily Price Update',
    replace_existing=True
)

# Intraday price refresh - runs every 15 minutes during market hours
scheduler.add_job(
    func=update_intraday_prices,
    trigger=CronTrigger(day_of_week='mon-fri', hour='9-16', minute='*/15', timezone='US/Eastern'),
    id='intraday_price_refresh',
    name='Intraday Price Refresh',
    replace_existing=True
)

# Dividend processing - runs at 4:00 PM EST daily
scheduler.add_job(
    func=process_dividends,
    trigger=CronTrigger(hour=16, minute=0, timezone='US/Eastern'),
    id='dividend_processor',
    name='Dividend Processor',
    replace_existing=True
)

scheduler.start()
```

**Job Implementation:**

```python
def update_daily_prices():
    """Fetch and store end-of-day prices for all actively traded stocks"""
    job_log = JobLog.create(job_name='daily_price_update')
    try:
        # Get unique company_ids from holdings
        active_companies = db.session.query(Holdings.company_id).distinct().all()
        
        success_count = 0
        failed_count = 0
        failed_symbols = []
        
        for company_id in active_companies:
            try:
                company = Company.query.get(company_id)
                # Fetch latest data from yfinance
                data = yf.download(company.symbol, period='1d', progress=False)
                
                if not data.empty:
                    # Store in price_history
                    price_record = PriceHistory(
                        company_id=company_id,
                        date=data.index[0].date(),
                        open=data['Open'].iloc[0],
                        high=data['High'].iloc[0],
                        low=data['Low'].iloc[0],
                        close=data['Close'].iloc[0],
                        adjusted_close=data['Adj Close'].iloc[0],
                        volume=data['Volume'].iloc[0]
                    )
                    db.session.merge(price_record)
                    company.last_updated = datetime.now()
                    success_count += 1
                else:
                    failed_count += 1
                    failed_symbols.append(company.symbol)
                    
            except Exception as e:
                logger.error(f"Failed to update {company.symbol}: {str(e)}")
                failed_count += 1
                failed_symbols.append(company.symbol)
        
        db.session.commit()
        
        job_log.complete(
            status='SUCCESS' if failed_count == 0 else 'PARTIAL',
            stocks_processed=success_count,
            stocks_failed=failed_count,
            error_message=f"Failed symbols: {', '.join(failed_symbols)}" if failed_symbols else None
        )
        
        # Notify admins if there were failures
        if failed_count > 0:
            notify_admins(
                title='Price Update Completed with Errors',
                message=f'Processed: {success_count}, Failed: {failed_count}'
            )
            
    except Exception as e:
        logger.error(f"Daily price update job failed: {str(e)}")
        job_log.complete(status='FAILED', error_message=str(e))
```

**Database Schema:**

```sql
CREATE TABLE job_logs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL') DEFAULT 'RUNNING',
    stocks_processed INT DEFAULT 0,
    stocks_failed INT DEFAULT 0,
    error_message TEXT,
    INDEX idx_job_name_started (job_name, started_at)
) ENGINE=InnoDB;
```


## Data Models

### Complete Entity Relationship Overview

```
users (1) ──────< (M) wallets
users (1) ──────< (M) holdings ───────> (1) companies
users (1) ──────< (M) orders ─────────> (1) companies
users (1) ──────< (M) transactions
users (1) ──────< (M) notifications
users (1) ──────< (1) brokers
companies (1) ───< (M) price_history
companies (1) ───< (M) dividends
companies (1) ───< (M) sentiment_cache
dividends (1) ───< (M) dividend_payments ───> (1) users
orders (1) ──────< (M) transactions
holdings (1) ────< (M) dividend_payments
```

### SQLAlchemy Model Definitions

**User Model:**

```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    risk_tolerance = db.Column(db.Enum('conservative', 'moderate', 'aggressive'), default='moderate')
    investment_goals = db.Column(db.Text)
    preferred_sectors = db.Column(db.JSON)
    notification_preferences = db.Column(db.JSON)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    account_status = db.Column(db.Enum('active', 'suspended'), default='active')
    
    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade='all, delete-orphan')
    holdings = db.relationship('Holdings', backref='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan')
    broker = db.relationship('Broker', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='bcrypt')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
```

**Company Model:**

```python
class Company(db.Model):
    __tablename__ = 'companies'
    
    company_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    sector = db.Column(db.String(100), index=True)
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.BigInteger)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    ceo = db.Column(db.String(255))
    employees = db.Column(db.Integer)
    founded_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='company', cascade='all, delete-orphan')
    holdings = db.relationship('Holdings', backref='company')
    orders = db.relationship('Order', backref='company')
    dividends = db.relationship('Dividend', backref='company', cascade='all, delete-orphan')
    sentiment_cache = db.relationship('SentimentCache', backref='company', cascade='all, delete-orphan')
```

**Wallet Model:**

```python
class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=100000.00, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    total_deposited = db.Column(db.Numeric(15, 2), default=100000.00)
    total_withdrawn = db.Column(db.Numeric(15, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint('balance >= 0', name='check_positive_balance'),
    )
```

**Holdings Model:**

```python
class Holdings(db.Model):
    __tablename__ = 'holdings'
    
    holding_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    average_purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_invested = db.Column(db.Numeric(15, 2), nullable=False)
    first_purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'company_id', name='unique_user_company'),
        db.CheckConstraint('quantity > 0', name='check_positive_quantity'),
    )
```

**Order Model:**

```python
class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    order_type = db.Column(db.Enum('BUY', 'SELL'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2), nullable=False)
    commission_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    order_status = db.Column(db.Enum('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED'), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    executed_at = db.Column(db.DateTime)
    failure_reason = db.Column(db.Text)
    realized_gain_loss = db.Column(db.Numeric(15, 2))
    
    # Relationships
    transactions = db.relationship('Transaction', backref='order')
    
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_positive_quantity'),
    )
```

**Transaction Model:**

```python
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    transaction_type = db.Column(db.Enum('BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAWAL', 'FEE'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance_before = db.Column(db.Numeric(15, 2), nullable=False)
    balance_after = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```


## Error Handling

### Error Handling Strategy

**Principles:**
1. Fail gracefully - never crash the application
2. Log all errors with context (user_id, action, timestamp)
3. Display user-friendly messages
4. Rollback database transactions on errors
5. Retry transient failures (API calls, network issues)

**Error Categories:**

```python
class ErrorCategory:
    VALIDATION = 'validation'        # User input errors
    BUSINESS_LOGIC = 'business'      # Business rule violations
    DATABASE = 'database'            # DB connection, query errors
    EXTERNAL_API = 'external_api'    # yfinance, Twitter API errors
    SYSTEM = 'system'                # Unexpected system errors
```

**Error Handler Implementation:**

```python
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_errors(error_category):
    """Decorator for consistent error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"Validation error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': str(e), 'category': 'validation'}
            except BusinessLogicError as e:
                logger.warning(f"Business logic error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': str(e), 'category': 'business'}
            except SQLAlchemyError as e:
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                db.session.rollback()
                return {'success': False, 'error': 'Database error occurred', 'category': 'database'}
            except ExternalAPIError as e:
                logger.error(f"External API error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': 'External service unavailable', 'category': 'external_api'}
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': 'An unexpected error occurred', 'category': 'system'}
        return wrapper
    return decorator
```

**Custom Exceptions:**

```python
class ValidationError(Exception):
    """Raised when user input validation fails"""
    pass

class BusinessLogicError(Exception):
    """Raised when business rules are violated"""
    pass

class InsufficientFundsError(BusinessLogicError):
    """Raised when wallet balance is insufficient"""
    pass

class InsufficientSharesError(BusinessLogicError):
    """Raised when user doesn't own enough shares"""
    pass

class ExternalAPIError(Exception):
    """Raised when external API calls fail"""
    pass

class StockNotFoundError(ExternalAPIError):
    """Raised when stock symbol is not found"""
    pass
```

**Retry Logic for External APIs:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_stock_data_with_retry(symbol):
    """Fetch stock data with automatic retry on failure"""
    try:
        data = yf.download(symbol, period='1d', progress=False)
        if data.empty:
            raise StockNotFoundError(f"No data found for symbol: {symbol}")
        return data
    except Exception as e:
        logger.warning(f"Attempt failed for {symbol}: {str(e)}")
        raise ExternalAPIError(f"Failed to fetch data for {symbol}")
```

**Flask Error Handlers:**

```python
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.exception("Internal server error")
    return render_template('errors/500.html'), 500

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    flash(str(error), 'error')
    return redirect(request.referrer or url_for('index'))
```

## Testing Strategy

### Testing Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │  (10%)
                    │  Selenium   │
                    └─────────────┘
                  ┌───────────────────┐
                  │ Integration Tests │  (30%)
                  │  API, DB, Services│
                  └───────────────────┘
              ┌─────────────────────────────┐
              │      Unit Tests             │  (60%)
              │  Models, Utils, Validators  │
              └─────────────────────────────┘
```

### Unit Tests

**Test Coverage Goals:**
- Models: 90%+ coverage
- Services: 85%+ coverage
- Utils: 95%+ coverage
- Overall: 80%+ coverage

**Example Unit Tests:**

```python
import pytest
from app.models import User, Wallet
from app.services.portfolio_service import PortfolioService

class TestPortfolioService:
    
    @pytest.fixture
    def user(self, db):
        user = User(email='test@example.com', full_name='Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user
    
    @pytest.fixture
    def wallet(self, db, user):
        wallet = Wallet(user_id=user.user_id, balance=100000.00)
        db.session.add(wallet)
        db.session.commit()
        return wallet
    
    def test_get_wallet_balance(self, user, wallet):
        service = PortfolioService()
        balance = service.get_wallet_balance(user.user_id)
        assert balance == 100000.00
    
    def test_deposit_funds_success(self, user, wallet):
        service = PortfolioService()
        transaction = service.deposit_funds(user.user_id, 5000.00, "Test deposit")
        
        assert transaction.transaction_type == 'DEPOSIT'
        assert transaction.amount == 5000.00
        assert wallet.balance == 105000.00
    
    def test_withdraw_funds_insufficient_balance(self, user, wallet):
        service = PortfolioService()
        
        with pytest.raises(InsufficientFundsError):
            service.withdraw_funds(user.user_id, 150000.00, "Test withdrawal")
```

### Integration Tests

**Test Scenarios:**
- Complete order flow (buy/sell)
- Dividend distribution process
- Price update jobs
- Authentication flow
- Admin operations

**Example Integration Test:**

```python
class TestOrderFlow:
    
    def test_complete_buy_order_flow(self, client, auth_user, test_company):
        # Login
        client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})
        
        # Submit buy order
        response = client.post('/orders/buy', data={
            'symbol': 'AAPL',
            'quantity': 10
        })
        
        assert response.status_code == 200
        assert b'Order completed successfully' in response.data
        
        # Verify wallet balance decreased
        wallet = Wallet.query.filter_by(user_id=auth_user.user_id).first()
        assert wallet.balance < 100000.00
        
        # Verify holdings created
        holding = Holdings.query.filter_by(
            user_id=auth_user.user_id,
            company_id=test_company.company_id
        ).first()
        assert holding is not None
        assert holding.quantity == 10
        
        # Verify transactions created
        transactions = Transaction.query.filter_by(user_id=auth_user.user_id).all()
        assert len(transactions) == 2  # BUY + FEE
```

### Test Database

```python
# conftest.py
import pytest
from app import create_app, db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()
```


## UI/UX Design - Clean Minimalist Style

### Design System

**Color Palette:**
```css
/* Primary Colors */
--primary: #2563EB;        /* Blue - Primary actions */
--primary-light: #DBEAFE; /* Light blue - Hover states */
--primary-dark: #1E40AF;  /* Dark blue - Active states */

/* Neutral Colors */
--gray-50: #F9FAFB;       /* Background */
--gray-100: #F3F4F6;      /* Card backgrounds */
--gray-200: #E5E7EB;      /* Borders */
--gray-300: #D1D5DB;      /* Disabled */
--gray-600: #4B5563;      /* Secondary text */
--gray-900: #111827;      /* Primary text */

/* Semantic Colors */
--success: #10B981;       /* Green - Gains, success */
--success-light: #D1FAE5;
--error: #EF4444;         /* Red - Losses, errors */
--error-light: #FEE2E2;
--warning: #F59E0B;       /* Orange - Warnings */
--warning-light: #FEF3C7;
--info: #3B82F6;          /* Blue - Info */
--info-light: #DBEAFE;

/* White & Black */
--white: #FFFFFF;
--black: #000000;
```

**Typography:**
```css
/* Font Family */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**Spacing System:**
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

**Shadows & Borders:**
```css
/* Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Border Radius */
--radius-sm: 0.375rem;  /* 6px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-full: 9999px;  /* Fully rounded */

/* Border Width */
--border-1: 1px;
--border-2: 2px;
```

### Component Library

**Buttons:**
```css
/* Primary Button */
.btn-primary {
    background: var(--primary);
    color: var(--white);
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-md);
    font-weight: var(--font-medium);
    border: none;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
    background: var(--primary-dark);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
    background: var(--white);
    color: var(--gray-900);
    border: var(--border-1) solid var(--gray-200);
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-md);
    font-weight: var(--font-medium);
    transition: all 0.2s ease;
}

.btn-secondary:hover {
    background: var(--gray-50);
    border-color: var(--gray-300);
}

/* Ghost Button */
.btn-ghost {
    background: transparent;
    color: var(--gray-600);
    padding: var(--space-3) var(--space-6);
    border: none;
    font-weight: var(--font-medium);
    transition: all 0.2s ease;
}

.btn-ghost:hover {
    background: var(--gray-100);
    color: var(--gray-900);
}
```

**Cards:**
```css
.card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
    border: var(--border-1) solid var(--gray-200);
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: var(--shadow-md);
}

.card-header {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--gray-900);
    margin-bottom: var(--space-4);
}

.card-stat {
    background: var(--gray-50);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    border: var(--border-1) solid var(--gray-200);
}

.card-stat-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
    font-weight: var(--font-medium);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.card-stat-value {
    font-size: var(--text-3xl);
    font-weight: var(--font-bold);
    color: var(--gray-900);
    margin-top: var(--space-2);
}
```

**Forms:**
```css
.form-group {
    margin-bottom: var(--space-5);
}

.form-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--gray-700);
    margin-bottom: var(--space-2);
}

.form-input {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    border: var(--border-1) solid var(--gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    transition: all 0.2s ease;
    background: var(--white);
}

.form-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-light);
}

.form-input:disabled {
    background: var(--gray-100);
    color: var(--gray-500);
    cursor: not-allowed;
}
```

### Base Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Portfolio{% endblock %} | StockFlow</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@latest/font/lucide.min.css">
    
    <!-- Custom CSS -->
    <link href="{{ url_for('static', filename='css/design-system.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/components.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/pages.css') }}" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    <!-- Sidebar Navigation (Desktop) -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <i class="lucide-trending-up"></i>
                <span>StockFlow</span>
            </div>
        </div>
        
        <nav class="sidebar-nav">
            {% if current_user.is_authenticated %}
                <a href="{{ url_for('dashboard.index') }}" class="nav-item {% if request.endpoint == 'dashboard.index' %}active{% endif %}">
                    <i class="lucide-layout-dashboard"></i>
                    <span>Dashboard</span>
                </a>
                <a href="{{ url_for('portfolio.index') }}" class="nav-item {% if request.endpoint == 'portfolio.index' %}active{% endif %}">
                    <i class="lucide-briefcase"></i>
                    <span>Portfolio</span>
                </a>
                <a href="{{ url_for('orders.index') }}" class="nav-item {% if request.endpoint == 'orders.index' %}active{% endif %}">
                    <i class="lucide-shopping-cart"></i>
                    <span>Orders</span>
                </a>
                <a href="{{ url_for('reports.index') }}" class="nav-item {% if request.endpoint == 'reports.index' %}active{% endif %}">
                    <i class="lucide-file-text"></i>
                    <span>Reports</span>
                </a>
                
                {% if current_user.is_admin %}
                    <div class="nav-divider"></div>
                    <a href="{{ url_for('admin.index') }}" class="nav-item {% if 'admin' in request.endpoint %}active{% endif %}">
                        <i class="lucide-shield"></i>
                        <span>Admin</span>
                    </a>
                {% endif %}
            {% endif %}
        </nav>
        
        <div class="sidebar-footer">
            {% if current_user.is_authenticated %}
                <div class="user-menu">
                    <div class="user-avatar">{{ current_user.full_name[0] }}</div>
                    <div class="user-info">
                        <div class="user-name">{{ current_user.full_name }}</div>
                        <div class="user-email">{{ current_user.email }}</div>
                    </div>
                    <div class="user-actions">
                        <a href="{{ url_for('auth.profile') }}" class="icon-btn" title="Profile">
                            <i class="lucide-settings"></i>
                        </a>
                        <a href="{{ url_for('auth.logout') }}" class="icon-btn" title="Logout">
                            <i class="lucide-log-out"></i>
                        </a>
                    </div>
                </div>
            {% endif %}
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
        <!-- Top Bar -->
        <header class="top-bar">
            <div class="top-bar-left">
                <button class="mobile-menu-toggle">
                    <i class="lucide-menu"></i>
                </button>
                <h1 class="page-title">{% block page_title %}{% endblock %}</h1>
            </div>
            
            <div class="top-bar-right">
                <!-- Search -->
                <div class="search-box">
                    <i class="lucide-search"></i>
                    <input type="text" placeholder="Search stocks..." id="global-search">
                </div>
                
                <!-- Notifications -->
                <button class="icon-btn notification-btn">
                    <i class="lucide-bell"></i>
                    <span class="badge">3</span>
                </button>
            </div>
        </header>

        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">
                            <i class="lucide-{% if category == 'success' %}check-circle{% elif category == 'error' %}x-circle{% elif category == 'warning' %}alert-triangle{% else %}info{% endif %}"></i>
                            <span>{{ message }}</span>
                            <button class="alert-close"><i class="lucide-x"></i></button>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <!-- Page Content -->
        <div class="content-wrapper">
            {% block content %}{% endblock %}
        </div>
    </main>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```


## Configuration Management

### Configuration Structure

```python
# app/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/stock_portfolio'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Data Mode
    DATA_MODE = os.environ.get('DATA_MODE', 'LIVE')  # LIVE or STATIC
    SIMULATION_DATE = os.environ.get('SIMULATION_DATE')  # YYYY-MM-DD for STATIC mode
    STATIC_DATA_DIR = 'data/stocks/'
    
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
    LOG_FILE = 'logs/app.log'
    
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
    
    # Override with production values
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Stricter security
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JOBS_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### Environment Variables (.env)

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stock_portfolio

# Data Mode
DATA_MODE=LIVE
# SIMULATION_DATE=2024-01-15  # Uncomment for STATIC mode

# Twitter API (optional)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Sentiment Analysis
SENTIMENT_ENABLED=True
SENTIMENT_CACHE_DURATION=3600
SENTIMENT_TWEET_COUNT=100

# Background Jobs
JOBS_ENABLED=True

# Logging
LOG_LEVEL=INFO
```

## Deployment Considerations

### Database Setup

**Initial Setup:**

```bash
# Create database
mysql -u root -p
CREATE DATABASE stock_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON stock_portfolio.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;

# Run migrations
flask db upgrade

# Seed initial data
flask seed-data
```

**Backup Strategy:**
- Daily automated backups at 2:00 AM
- Retain backups for 30 days
- Store backups in separate location
- Test restore process monthly

### Performance Optimization

**Database Indexing:**
- All foreign keys indexed
- Composite indexes on frequently queried columns
- Regular ANALYZE TABLE to update statistics

**Caching Strategy:**
- Sentiment analysis results cached for 1 hour
- Price data cached for 15 minutes during market hours
- User session data in Redis (optional)

**Query Optimization:**
- Use eager loading for relationships (joinedload)
- Paginate large result sets
- Use database connection pooling
- Monitor slow queries (>1 second)

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS in production
- [ ] Set secure cookie flags
- [ ] Implement rate limiting on login
- [ ] Validate all user inputs
- [ ] Use parameterized queries
- [ ] Keep dependencies updated
- [ ] Enable CSRF protection
- [ ] Implement proper error handling
- [ ] Log security events
- [ ] Regular security audits

### Monitoring and Logging

**Logging Configuration:**

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        # File handler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Stock Portfolio Platform startup')
```

**Metrics to Monitor:**
- Request rate and response times
- Database query performance
- API call success/failure rates
- Background job execution status
- Error rates by endpoint
- User activity patterns
- System resource usage (CPU, memory, disk)


## Migration from Current System

### Migration Strategy

**Phase 1: Setup Foundation (Week 1)**
1. Set up new directory structure
2. Configure MySQL database
3. Create SQLAlchemy models
4. Set up Flask-Migrate for migrations
5. Implement configuration management

**Phase 2: Core Services (Week 2-3)**
1. Implement Authentication System
2. Create Portfolio Service
3. Build Transaction Engine
4. Develop Stock Repository
5. Set up database seed data

**Phase 3: ML Integration (Week 4)**
1. Refactor existing ML models
2. Create Prediction Service wrapper
3. Integrate with new architecture
4. Update visualization generation
5. Test prediction accuracy

**Phase 4: Advanced Features (Week 5-6)**
1. Implement Sentiment Engine with caching
2. Build Dividend Manager
3. Create Admin Service
4. Develop background jobs
5. Add notification system

**Phase 5: UI Development (Week 7-8)**
1. Create base templates
2. Build user pages (dashboard, portfolio, orders, reports)
3. Develop admin pages
4. Implement responsive design
5. Add client-side validation

**Phase 6: Testing & Deployment (Week 9-10)**
1. Write unit tests
2. Create integration tests
3. Perform security audit
4. Load testing
5. Production deployment

### Code Refactoring Plan

**Existing Files to Refactor:**

```
Current Structure:
├── app.py                      → routes/dashboard.py
├── main.py                     → (deprecated, merge into new structure)
├── arima_model.py              → ml_models/arima_model.py
├── lstm_model.py               → ml_models/lstm_model.py
├── linear_regression_model.py  → ml_models/linear_regression_model.py
├── stock_data_processor.py     → ml_models/stock_data_processor.py
├── sentiment_analyzer.py       → services/sentiment_engine.py
├── visualization.py            → utils/visualization.py
└── constants.py                → config.py (merge)
```

**Backward Compatibility:**

During migration, maintain backward compatibility by:
1. Keep existing endpoints functional
2. Gradually migrate routes to new blueprints
3. Use feature flags to toggle new features
4. Provide data migration scripts
5. Document breaking changes

### Data Migration

**Seed Data Script:**

```python
# scripts/seed_data.py
from app import create_app, db
from app.models import User, Company, Wallet
import pandas as pd

def seed_companies():
    """Import companies from Yahoo-Finance-Ticker-Symbols.csv"""
    df = pd.read_csv('Yahoo-Finance-Ticker-Symbols.csv')
    
    # Import top 100 companies
    for _, row in df.head(100).iterrows():
        company = Company(
            symbol=row['Ticker'],
            company_name=row['Name'],
            sector=row.get('Sector', 'Unknown'),
            industry=row.get('Industry', 'Unknown')
        )
        db.session.add(company)
    
    db.session.commit()
    print(f"Seeded {100} companies")

def seed_admin_user():
    """Create default admin user"""
    admin = User(
        email='admin@stockportfolio.com',
        full_name='System Administrator',
        is_admin=True
    )
    admin.set_password('admin123')  # Change in production!
    db.session.add(admin)
    
    # Create wallet for admin
    wallet = Wallet(user_id=admin.user_id)
    db.session.add(wallet)
    
    db.session.commit()
    print("Created admin user")

def seed_test_users():
    """Create test users for development"""
    for i in range(1, 6):
        user = User(
            email=f'user{i}@example.com',
            full_name=f'Test User {i}',
            risk_tolerance='moderate'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        wallet = Wallet(user_id=user.user_id)
        db.session.add(wallet)
    
    db.session.commit()
    print("Created 5 test users")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_companies()
        seed_admin_user()
        seed_test_users()
```

## API Documentation

### REST API Endpoints

**Authentication:**
```
POST   /api/auth/register       - Register new user
POST   /api/auth/login          - Login user
POST   /api/auth/logout         - Logout user
GET    /api/auth/profile        - Get current user profile
PUT    /api/auth/profile        - Update user profile
```

**Portfolio:**
```
GET    /api/portfolio           - Get user portfolio summary
GET    /api/portfolio/holdings  - Get all holdings
GET    /api/wallet              - Get wallet balance
POST   /api/wallet/deposit      - Deposit funds
POST   /api/wallet/withdraw     - Withdraw funds
```

**Orders:**
```
POST   /api/orders/buy          - Create buy order
POST   /api/orders/sell         - Create sell order
GET    /api/orders              - Get order history
GET    /api/orders/:id          - Get order details
DELETE /api/orders/:id          - Cancel order
```

**Stocks:**
```
GET    /api/stocks/search       - Search stocks
GET    /api/stocks/:symbol      - Get stock details
GET    /api/stocks/:symbol/price - Get current price
GET    /api/stocks/:symbol/history - Get price history
POST   /api/stocks/:symbol/predict - Get price predictions
```

**Admin:**
```
GET    /api/admin/users         - List all users
GET    /api/admin/users/:id     - Get user details
PUT    /api/admin/users/:id     - Update user
DELETE /api/admin/users/:id     - Delete user
GET    /api/admin/companies     - List companies
POST   /api/admin/companies     - Create company
PUT    /api/admin/companies/:id - Update company
GET    /api/admin/metrics       - Get system metrics
```

### Response Format

**Success Response:**
```json
{
    "success": true,
    "data": {
        // Response data
    },
    "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_FUNDS",
        "message": "Insufficient funds for this purchase",
        "details": {
            "required": 5000.00,
            "available": 3000.00
        }
    }
}
```

## Conclusion

This design document provides a comprehensive blueprint for transforming the existing stock market prediction application into a full-featured portfolio management platform. The architecture is modular, scalable, and maintainable, with clear separation of concerns between layers.

### Key Design Decisions

1. **Layered Architecture**: Separation of presentation, business logic, and data access layers
2. **Service-Oriented**: Business logic encapsulated in service classes
3. **ORM-Based**: SQLAlchemy for database abstraction and type safety
4. **Blueprint-Based Routing**: Modular route organization
5. **Decorator Pattern**: Consistent error handling and authorization
6. **Background Jobs**: APScheduler for automated tasks
7. **Caching Strategy**: Reduce external API calls and improve performance
8. **Responsive Design**: Bootstrap 5 for mobile-friendly UI

### Next Steps

1. Review and approve this design document
2. Create detailed implementation tasks
3. Set up development environment
4. Begin Phase 1 implementation
5. Conduct regular design reviews during implementation

### Design Principles Followed

- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **DRY**: Don't repeat yourself - reusable components
- **KISS**: Keep it simple - avoid over-engineering
- **Security First**: Built-in security from the ground up
- **Testability**: Design for easy unit and integration testing
- **Scalability**: Architecture supports future growth
- **Maintainability**: Clear code organization and documentation


### Dashboard Page Layout

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Welcome back, John! 👋                                     │
│  Here's what's happening with your portfolio today          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Wallet       │  │ Portfolio    │  │ Total Worth  │     │
│  │ $125,430.50  │  │ $874,569.50  │  │ $1,000,000   │     │
│  │ +2.3% today  │  │ +5.2% today  │  │ +4.8% today  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌────────────────────────┐  │
│  │ Quick Predict           │  │ Top Holdings           │  │
│  │ ┌─────────────────────┐ │  │ AAPL  $45,230  +3.2%  │  │
│  │ │ Enter symbol...     │ │  │ GOOGL $38,450  +2.1%  │  │
│  │ └─────────────────────┘ │  │ MSFT  $32,100  +1.8%  │  │
│  │ [Predict Price]         │  │ [View All →]           │  │
│  └─────────────────────────┘  └────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Recent Activity                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ● Bought 10 shares of AAPL at $175.43    2 hours ago│  │
│  │ ● Sold 5 shares of TSLA at $245.20       Yesterday  │  │
│  │ ● Dividend received from MSFT: $12.50    2 days ago │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Portfolio Page Layout

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Portfolio Overview                                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Total Value  │  │ Total Gain   │  │ Return       │     │
│  │ $874,569.50  │  │ +$74,569.50  │  │ +8.52%       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Performance Chart (Last 6 Months)                   │  │
│  │ [Line chart showing portfolio value over time]      │  │
│  └─────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Holdings                                [Sort ▼] [Filter] │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Symbol │ Shares │ Avg Price │ Current │ Value │ Gain│  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ AAPL   │   100  │  $152.30  │ $175.43 │$17.5K│+15%│  │
│  │ GOOGL  │    50  │  $128.50  │ $142.80 │ $7.1K│+11%│  │
│  │ MSFT   │    75  │  $310.20  │ $328.45 │$24.6K│ +6%│  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Orders Page Layout

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Place New Order                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Stock Symbol                                        │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │ AAPL                                    [Search]│ │  │
│  │ └─────────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │ Order Type:  ○ Buy  ○ Sell                         │  │
│  │                                                     │  │
│  │ Quantity                                            │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │ 10                                              │ │  │
│  │ └─────────────────────────────────────────────────┘ │  │
│  │                                                     │  │
│  │ Current Price: $175.43                              │  │
│  │ Total Cost: $1,754.30 + $1.75 commission           │  │
│  │                                                     │  │
│  │ [Place Order]                                       │  │
│  └─────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Order History                          [Filter] [Export]  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Date       │ Symbol │ Type │ Qty │ Price │ Status  │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ 2024-01-15 │ AAPL   │ BUY  │ 10  │$175.43│✓Complete│  │
│  │ 2024-01-14 │ TSLA   │ SELL │  5  │$245.20│✓Complete│  │
│  │ 2024-01-13 │ GOOGL  │ BUY  │ 15  │$142.80│✓Complete│  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Admin Dashboard Layout

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  System Overview                                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Users    │  │ Trans.   │  │ Volume   │  │ Health   │  │
│  │ 1,250    │  │ 342      │  │ $1.25M   │  │ ● Good   │  │
│  │ +15 new  │  │ today    │  │ today    │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│  [Users] [Companies] [Brokers] [Dividends] [Monitoring]    │
├─────────────────────────────────────────────────────────────┤
│  User Management                        [+ Add User] [⚙️]   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Email          │ Name      │ Joined    │ Status    │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ john@email.com │ John Doe  │ 2024-01-01│ ● Active  │  │
│  │ jane@email.com │ Jane Smith│ 2024-01-05│ ● Active  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

```css
/* Mobile First Approach */
/* Mobile: 0-767px (default) */
/* Tablet: 768px-1023px */
@media (min-width: 768px) {
    .sidebar { width: 240px; }
    .main-content { margin-left: 240px; }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
    .sidebar { width: 280px; }
    .main-content { margin-left: 280px; }
    .content-wrapper { max-width: 1400px; }
}

/* Large Desktop: 1440px+ */
@media (min-width: 1440px) {
    .content-wrapper { max-width: 1600px; }
}
```

### Animation & Transitions

```css
/* Smooth transitions for interactive elements */
.card, .btn, .nav-item, .form-input {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hover effects */
.card:hover {
    transform: translateY(-2px);
}

.btn:hover {
    transform: translateY(-1px);
}

/* Loading states */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.skeleton {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
    background-size: 200% 100%;
}

/* Page transitions */
.page-enter {
    opacity: 0;
    transform: translateY(10px);
}

.page-enter-active {
    opacity: 1;
    transform: translateY(0);
    transition: all 0.3s ease;
}
```

### Accessibility Features

```css
/* Focus states for keyboard navigation */
*:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --gray-600: #000000;
        --gray-900: #000000;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Screen reader only content */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
```



## Testing Strategy

#