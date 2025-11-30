# Setup Instructions

Follow these steps to set up the Stock Portfolio Management Platform.

## Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stock-portfolio-platform
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and update the following:

```env
# Change this to a secure random string
SECRET_KEY=your-secret-key-here

# Update with your MySQL credentials
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stock_portfolio

# Optional: Twitter API credentials for sentiment analysis
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

### 5. Set Up MySQL Database

#### Option A: Using the initialization script

```bash
python scripts/init_db.py
```

This will:
- Create the database
- Create the user (if not root)
- Grant necessary privileges
- Test the connection

#### Option B: Manual setup

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE stock_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON stock_portfolio.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### 6. Initialize Database Schema

#### Option A: Using the setup script (Recommended)

**On Windows:**
```bash
scripts\setup_database.bat
```

**On macOS/Linux:**
```bash
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

#### Option B: Manual steps

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Seed initial data
flask seed-data
```

### 7. Verify Setup

Test the database connection:

```bash
python scripts/test_db_connection.py
```

You should see:
```
✓ Connection successful!
✓ MySQL Version: 8.0.x
✓ Connected to database: stock_portfolio
```

### 8. Run the Application

```bash
python run.py
```

The application will be available at: `http://localhost:5000`

## Default Credentials

After seeding, you can log in with:

**Admin Account:**
- Email: `admin@stockportfolio.com`
- Password: `admin123` (⚠️ Change this immediately!)

**Test Users:**
- Email: `user1@example.com` through `user5@example.com`
- Password: `password123`

## Troubleshooting

### Database Connection Issues

**Error: "Access denied for user"**
- Check your DATABASE_URL in `.env`
- Verify MySQL user exists and has correct password
- Ensure user has privileges on the database

**Error: "Unknown database"**
- Run `python scripts/init_db.py` to create the database
- Or manually create it using MySQL commands

**Error: "Can't connect to MySQL server"**
- Ensure MySQL server is running
- Check host and port in DATABASE_URL
- Verify firewall settings

### Migration Issues

**Error: "Target database is not up to date"**
```bash
flask db upgrade
```

**Error: "Multiple heads"**
```bash
flask db merge heads -m "Merge migrations"
flask db upgrade
```

**Start fresh (⚠️ Destroys all data):**
```bash
flask db downgrade base
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Import Errors

**Error: "No module named 'app'"**
- Ensure you're in the project root directory
- Activate the virtual environment
- Install dependencies: `pip install -r requirements.txt`

**Error: "No module named 'pymysql'"**
```bash
pip install pymysql
```

### Port Already in Use

If port 5000 is already in use:

```bash
# Run on different port
flask run --port 5001
```

Or edit `run.py` and change the port number.

## Development Workflow

### Making Model Changes

1. Edit model in `app/models/`
2. Create migration: `flask db migrate -m "Description"`
3. Review migration file in `migrations/versions/`
4. Apply migration: `flask db upgrade`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models.py
```

### Accessing Flask Shell

```bash
flask shell
```

This gives you access to:
- `db` - Database instance
- All models (User, Company, etc.)
- Application context

Example:
```python
>>> users = User.query.all()
>>> print(users)
```

## Additional Configuration

### Static Dataset Mode

For testing without internet:

1. Set in `.env`:
```env
DATA_MODE=STATIC
SIMULATION_DATE=2024-01-15
```

2. Place CSV files in `data/stocks/`:
```
data/stocks/AAPL.csv
data/stocks/GOOGL.csv
data/stocks/MSFT.csv
```

### Disable Background Jobs

In `.env`:
```env
JOBS_ENABLED=False
```

### Disable Sentiment Analysis

In `.env`:
```env
SENTIMENT_ENABLED=False
```

## Production Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## Getting Help

- Check `README_NEW_STRUCTURE.md` for project structure
- See `MIGRATION_GUIDE.md` for database migration help
- Review logs in `logs/app.log`
- Check Flask debug output in terminal

## Next Steps

After setup:

1. Change default admin password
2. Configure Twitter API credentials (optional)
3. Import company data
4. Start trading!

For more information, see the full documentation in the `docs/` directory.
