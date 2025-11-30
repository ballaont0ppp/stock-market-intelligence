@echo off
REM Deployment script for Stock Portfolio Management Platform (Windows)
REM Usage: scripts\deploy.bat [environment]

setlocal

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

echo =========================================
echo Stock Portfolio Platform Deployment
echo Environment: %ENVIRONMENT%
echo =========================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check environment variables
echo Checking environment variables...
if "%ENVIRONMENT%"=="production" (
    if "%SECRET_KEY%"=="" (
        echo ERROR: SECRET_KEY environment variable not set
        exit /b 1
    )
    if "%DATABASE_URL%"=="" (
        echo ERROR: DATABASE_URL environment variable not set
        exit /b 1
    )
)

REM Run database migrations
echo Running database migrations...
flask db upgrade

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

echo =========================================
echo Deployment completed successfully!
echo =========================================
echo.
echo To start the application:
echo   Development: flask run
echo   Production: waitress-serve --port=8000 app:create_app
echo.

endlocal
