"""
Database Seed Script
Populates initial data for development and testing
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Company, Wallet
import pandas as pd


def seed_companies():
    """Import companies from Yahoo-Finance-Ticker-Symbols.csv"""
    print("Seeding companies...")
    
    try:
        # Check if file exists
        csv_file = 'Yahoo-Finance-Ticker-Symbols.csv'
        if not os.path.exists(csv_file):
            print(f"⚠ Warning: {csv_file} not found. Skipping company import.")
            print("  You can add companies later through the admin panel.")
            return
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Import top 100 companies (or all if less than 100)
        count = min(100, len(df))
        imported = 0
        
        for _, row in df.head(count).iterrows():
            # Check if company already exists
            symbol = str(row.get('Ticker', '')).strip().upper()
            if not symbol:
                continue
                
            existing = Company.query.filter_by(symbol=symbol).first()
            if existing:
                continue
            
            company = Company(
                symbol=symbol,
                company_name=str(row.get('Name', symbol)),
                sector=str(row.get('Sector', 'Unknown')) if pd.notna(row.get('Sector')) else None,
                industry=str(row.get('Industry', 'Unknown')) if pd.notna(row.get('Industry')) else None,
                is_active=True
            )
            db.session.add(company)
            imported += 1
        
        db.session.commit()
        print(f"✓ Imported {imported} companies")
        
    except Exception as e:
        print(f"✗ Error seeding companies: {e}")
        db.session.rollback()


def seed_admin_user():
    """Create default admin user"""
    print("Creating admin user...")
    
    try:
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@stockportfolio.com').first()
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            email='admin@stockportfolio.com',
            full_name='System Administrator',
            is_admin=True,
            risk_tolerance='moderate',
            account_status='active',
            created_at=datetime.utcnow()
        )
        admin.set_password('admin123')  # ⚠️ Change in production!
        
        db.session.add(admin)
        db.session.flush()  # Get user_id
        
        # Create wallet for admin
        wallet = Wallet(
            user_id=admin.user_id,
            balance=100000.00,
            total_deposited=100000.00,
            total_withdrawn=0.00
        )
        db.session.add(wallet)
        
        db.session.commit()
        print("✓ Created admin user: admin@stockportfolio.com / admin123")
        print("  ⚠️  IMPORTANT: Change the admin password immediately!")
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.session.rollback()


def seed_test_users():
    """Create test users for development"""
    print("Creating test users...")
    
    try:
        created = 0
        
        for i in range(1, 6):
            email = f'user{i}@example.com'
            
            # Check if user already exists
            existing = User.query.filter_by(email=email).first()
            if existing:
                continue
            
            # Create test user
            user = User(
                email=email,
                full_name=f'Test User {i}',
                risk_tolerance='moderate',
                account_status='active',
                created_at=datetime.utcnow()
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.flush()  # Get user_id
            
            # Create wallet for user
            wallet = Wallet(
                user_id=user.user_id,
                balance=100000.00,
                total_deposited=100000.00,
                total_withdrawn=0.00
            )
            db.session.add(wallet)
            created += 1
        
        db.session.commit()
        print(f"✓ Created {created} test users (user1@example.com - user5@example.com)")
        print("  Password for all test users: password123")
        
    except Exception as e:
        print(f"✗ Error creating test users: {e}")
        db.session.rollback()


def seed_all():
    """Seed all initial data"""
    print("=" * 60)
    print("Database Seeding")
    print("=" * 60)
    print()
    
    app = create_app('development')
    
    with app.app_context():
        seed_companies()
        print()
        seed_admin_user()
        print()
        seed_test_users()
        print()
        print("=" * 60)
        print("✓ Database seeding completed!")
        print("=" * 60)


if __name__ == '__main__':
    seed_all()
