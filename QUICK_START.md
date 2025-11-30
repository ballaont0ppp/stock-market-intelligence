# Quick Start Guide

## What You Need

1. **Python 3.8+** - The programming language
2. **pip** - Python package manager (comes with Python)
3. **SQLite** - Database (comes with Python)

That's it! No WordPress, no XAMPP needed.

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and add your settings (optional for basic testing):
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///portfolio.db
```

### 3. Initialize the Database

```bash
python scripts/init_db.py
```

This creates your database and tables.

### 4. (Optional) Add Sample Data

```bash
python scripts/seed_data.py
```

This adds test companies, users, etc.

### 5. Run the Application

```bash
python run.py
```

Or:
```bash
flask run
```

### 6. Open Your Browser

Go to: `http://localhost:5000`

Default login:
- Username: `admin`
- Password: `admin123` (change this!)

## What Each Component Does

- **Flask** - Web framework (handles routes, templates)
- **SQLAlchemy** - Database ORM (talks to SQLite)
- **SQLite** - Database file (stores all your data)
- **Jinja2** - Template engine (renders HTML)
- **Bootstrap** - CSS framework (makes it look good)

## Common Issues

### "Module not found"
Run: `pip install -r requirements.txt`

### "Database not found"
Run: `python scripts/init_db.py`

### Port already in use
Change port: `flask run --port 5001`

## File Structure

```
├── app/                    # Main application
│   ├── models/            # Database models
│   ├── routes/            # URL routes
│   ├── services/          # Business logic
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── ml_models/             # Machine learning models
├── scripts/               # Setup scripts
├── tests/                 # Test files
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Next Steps

1. Change the default admin password
2. Add your own companies/stocks
3. Customize the branding
4. Deploy to a server (optional)
