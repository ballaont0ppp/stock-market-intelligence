# Technology Stack

## Core Framework
- **Flask 3.1.0** - Web framework
- **Python 3.8+** - Programming language
- **SQLite/MySQL** - Database (SQLite for dev, MySQL for production)

## Key Libraries

**Backend**
- Flask-SQLAlchemy 3.1.1 - ORM
- Flask-Login 0.6.3 - Authentication
- Flask-Bcrypt 1.0.1 - Password hashing
- Flask-WTF 1.2.1 - Form handling with CSRF protection
- Flask-Migrate 4.0.7 - Database migrations
- APScheduler 3.10.4 - Background job scheduling

**Data & ML**
- pandas 2.2.3 - Data manipulation
- numpy 1.26.4 - Numerical computing
- scikit-learn 1.5.2 - Machine learning
- statsmodels 0.14.5 - Statistical models (ARIMA)
- yfinance 0.2.40 - Stock data fetching
- matplotlib 3.9.2 - Visualization

**Testing**
- pytest 8.3.3 - Test framework
- pytest-flask 1.3.0 - Flask testing utilities
- pytest-cov 5.0.0 - Coverage reporting

**Frontend**
- Bootstrap - CSS framework
- jQuery - JavaScript library
- Jinja2 - Template engine

## Common Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Seed test data
python scripts/seed_data.py
```

### Running the Application
```bash
# Development server
python run.py
# or
flask run

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m routes        # Route tests only

# Run specific test file
pytest tests/test_models/test_user.py
```

### Database Management
```bash
# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Test database connection
python scripts/test_db_connection.py
```

### Code Quality
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/
pylint app/
```

### Deployment
```bash
# Backup database
bash scripts/backup_database.sh  # Linux/Mac
scripts\backup_database.bat      # Windows

# Deploy
bash scripts/deploy.sh           # Linux/Mac
scripts\deploy.bat               # Windows
```

## Configuration

Environment variables in `.env`:
- `FLASK_ENV` - development/production
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `DATA_MODE` - LIVE or STATIC (for testing)
- `JOBS_ENABLED` - Enable/disable background jobs
- `SENTIMENT_ENABLED` - Enable/disable sentiment analysis

## Build System

Uses standard Python packaging with `pyproject.toml` for tool configuration (black, isort, pylint, pytest).
