# Stock Portfolio Management Platform

A comprehensive stock portfolio management platform with ML-based price predictions, sentiment analysis, and virtual trading capabilities.

## Project Structure

```
stock-portfolio-platform/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # SQLAlchemy models
│   ├── services/                # Business logic layer
│   ├── routes/                  # Flask blueprints
│   ├── forms/                   # WTForms
│   ├── utils/                   # Utility functions
│   └── jobs/                    # Background jobs
├── ml_models/                   # ML prediction models
├── templates/                   # Jinja2 templates
├── static/                      # Static assets (CSS, JS, images)
├── scripts/                     # Database scripts
├── tests/                       # Test suite
├── data/                        # Static data files
├── logs/                        # Application logs
├── migrations/                  # Database migrations
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and API keys.

### 4. Set Up MySQL Database

```bash
# Create database
mysql -u root -p
CREATE DATABASE stock_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON stock_portfolio.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Initialize Database

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration (after models are created)
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Seed initial data
flask seed-data
```

### 6. Run Application

```bash
# Development mode
python run.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development/production/testing)
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: MySQL connection string
- `DATA_MODE`: LIVE (yfinance) or STATIC (CSV files)
- `TWITTER_API_KEY`: Twitter API credentials (optional)
- `SENTIMENT_ENABLED`: Enable/disable sentiment analysis
- `JOBS_ENABLED`: Enable/disable background jobs

### Data Modes

**LIVE Mode** (default):
- Fetches real-time stock data from yfinance
- Requires internet connection
- Suitable for production

**STATIC Mode**:
- Uses local CSV files from `data/stocks/`
- No internet required
- Suitable for testing and demos
- Set `DATA_MODE=STATIC` and `SIMULATION_DATE=YYYY-MM-DD`

## Development

### Running Tests

```bash
pytest
pytest --cov=app  # With coverage
```

### Database Migrations

```bash
# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Flask Shell

```bash
flask shell
# Access db, models, and app context
```

## Features

- **User Authentication**: Secure registration, login, and session management
- **Virtual Wallet**: Simulated cash account with $100,000 starting balance
- **Stock Trading**: Buy and sell stocks with 0.1% commission
- **Portfolio Management**: Track holdings, valuations, and performance
- **ML Predictions**: LSTM, ARIMA, and Linear Regression models
- **Sentiment Analysis**: Twitter sentiment analysis with caching
- **Dividend Tracking**: Automatic dividend payments
- **Admin Dashboard**: User, company, and broker management
- **Reports**: Transaction history, billing, and performance analytics
- **Background Jobs**: Automated price updates and dividend processing

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy 3.0.5, MySQL 8.0+
- **ML**: TensorFlow 2.13.0, scikit-learn 1.3.0, statsmodels 0.14.0
- **Frontend**: Bootstrap 5, Chart.js, jQuery
- **APIs**: yfinance 0.2.18, tweepy 4.14.0
- **Jobs**: APScheduler 3.10.4

## Security

- Bcrypt password hashing (work factor 12)
- CSRF protection on all forms
- SQL injection prevention via ORM
- Secure session cookies
- Rate limiting on login attempts
- Input validation and sanitization

## License

See LICENSE file for details.

## Support

For issues and questions, please refer to the project documentation or contact the development team.
