#!/bin/bash
# Database Setup Script
# Initializes database, creates migrations, and seeds data

echo "=========================================="
echo "Stock Portfolio Platform - Database Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠ Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠ Please edit .env with your database credentials before continuing"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Test database connection
echo "Step 1: Testing database connection..."
python scripts/test_db_connection.py
if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Database connection failed"
    echo "Please run: python scripts/init_db.py"
    exit 1
fi

echo ""
echo "Step 2: Initializing Flask-Migrate..."
if [ ! -d "migrations" ]; then
    flask db init
    echo "✓ Flask-Migrate initialized"
else
    echo "✓ Flask-Migrate already initialized"
fi

echo ""
echo "Step 3: Creating initial migration..."
flask db migrate -m "Initial migration - all tables"
if [ $? -ne 0 ]; then
    echo "✗ Migration creation failed"
    exit 1
fi
echo "✓ Migration created"

echo ""
echo "Step 4: Applying migration..."
flask db upgrade
if [ $? -ne 0 ]; then
    echo "✗ Migration failed"
    exit 1
fi
echo "✓ Migration applied"

echo ""
echo "Step 5: Seeding initial data..."
flask seed-data
if [ $? -ne 0 ]; then
    echo "✗ Seeding failed"
    exit 1
fi
echo "✓ Data seeded"

echo ""
echo "=========================================="
echo "✓ Database setup completed successfully!"
echo "=========================================="
echo ""
echo "You can now run the application:"
echo "  python run.py"
echo ""
