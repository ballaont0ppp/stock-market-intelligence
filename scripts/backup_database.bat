@echo off
REM Database backup script for Stock Portfolio Management Platform (Windows)
REM Usage: scripts\backup_database.bat

setlocal enabledelayedexpansion

REM Configuration
set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=stock_portfolio_backup_%TIMESTAMP%.sql

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" (
    echo Creating backup directory...
    mkdir "%BACKUP_DIR%"
)

REM Load environment variables from .env file
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        set %%a=%%b
    )
)

REM Check DATABASE_URL
if "%DATABASE_URL%"=="" (
    echo ERROR: DATABASE_URL environment variable not set
    exit /b 1
)

echo =========================================
echo Database Backup
echo =========================================
echo Backup file: %BACKUP_DIR%\%BACKUP_FILE%
echo.

REM Note: This script requires mysqldump to be in PATH
REM Parse DATABASE_URL and extract credentials
REM For Windows, you may need to manually set these variables:
REM set DB_USER=root
REM set DB_PASS=password
REM set DB_HOST=localhost
REM set DB_NAME=stock_portfolio

echo Creating backup...
echo NOTE: Please ensure mysqldump is installed and in your PATH
echo If not, install MySQL client tools or use MySQL Workbench for backups
echo.

REM Uncomment and modify the following line with your database credentials:
REM mysqldump -h %DB_HOST% -u %DB_USER% -p%DB_PASS% %DB_NAME% > "%BACKUP_DIR%\%BACKUP_FILE%"

echo =========================================
echo Backup script completed
echo =========================================
echo.
echo For Windows users, consider using:
echo 1. MySQL Workbench (Data Export feature)
echo 2. phpMyAdmin (Export feature)
echo 3. Manual mysqldump command with your credentials
echo.

endlocal
