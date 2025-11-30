#!/bin/bash
# Deployment script for Stock Portfolio Management Platform
# Usage: ./scripts/deploy.sh [environment]

set -e  # Exit on error

ENVIRONMENT=${1:-production}

echo "========================================="
echo "Stock Portfolio Platform Deployment"
echo "Environment: $ENVIRONMENT"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check environment variables
echo "Checking environment variables..."
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -z "$SECRET_KEY" ]; then
        echo "ERROR: SECRET_KEY environment variable not set"
        exit 1
    fi
    if [ -z "$DATABASE_URL" ]; then
        echo "ERROR: DATABASE_URL environment variable not set"
        exit 1
    fi
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo "Creating logs directory..."
    mkdir -p logs
fi

# Run tests (optional, comment out for faster deployment)
# echo "Running tests..."
# pytest tests/ -v

echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  Development: flask run"
echo "  Production: gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'"
echo ""
