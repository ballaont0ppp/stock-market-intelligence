@echo off
REM Database Setup Script for Windows
REM Initializes database, creates migrations, and seeds data

echo ==========================================
echo Stock Portfolio Platform - Database Setup
echo ==========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Created .env file
    echo Please edit .env with your database credentials before continuing
    echo.
    pause
)

REM Test database connection
echo Step 1: Testing database connection...
python scripts\test_db_connection.py
if errorlevel 1 (
    echo.
    echo Database connection failed
    echo Please run: python scripts\init_db.py
    exit /b 1
)

echo.
echo Step 2: Initializing Flask-Migrate...
if not exist migrations (
    flask db init
    echo Flask-Migrate initialized
) else (
    echo Flask-Migrate already initialized
)

echo.
echo Step 3: Creating initial migration...
flask db migrate -m "Initial migration - all tables"
if errorlevel 1 (
    echo Migration creation failed
    exit /b 1
)
echo Migration created

echo.
echo Step 4: Applying migration...
flask db upgrade
if errorlevel 1 (
    echo Migration failed
    exit /b 1
)
echo Migration applied

echo.
echo Step 5: Seeding initial data...
flask seed-data
if errorlevel 1 (
    echo Seeding failed
    exit /b 1
)
echo Data seeded

echo.
echo ==========================================
echo Database setup completed successfully!
echo ==========================================
echo.
echo You can now run the application:
echo   python run.py
echo.
pause
