#!/bin/bash
# Production startup script for Stock Portfolio Management Platform
# Usage: ./scripts/start_production.sh

set -e  # Exit on error

echo "========================================="
echo "Starting Stock Portfolio Platform"
echo "Environment: PRODUCTION"
echo "========================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run deploy.sh first."
    exit 1
fi

# Check required environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set"
    exit 1
fi

# Set Flask environment
export FLASK_ENV=production
export FLASK_APP=run.py

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Start the application with gunicorn
echo "Starting application with gunicorn..."
echo "Workers: 4"
echo "Bind: 0.0.0.0:8000"
echo ""

gunicorn -w 4 \
    -b 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    'run:app'
