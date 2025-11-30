"""
Simple SQLite Database Initialization Script
No MySQL or passwords needed!
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Company, Broker, Wallet

def init_database():
    """Initialize SQLite database with tables"""
    print("=" * 60)
    print("Stock Portfolio Platform - Database Initialization")
    print("Using SQLite (no password needed!)")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (fresh start)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully!")
        
        # Create default admin user
        print("\nCreating default admin user...")
        admin = User(
            email='admin@example.com',
            full_name='Administrator',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create default wallet for admin
        wallet = Wallet(user_id=1, balance=100000.00)
        db.session.add(wallet)
        
        db.session.commit()
        
        print("✓ Admin user created!")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("  ⚠️  Change this password after first login!")
        
        print("\n" + "=" * 60)
        print("✓ Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python run.py")
        print("2. Open browser: http://localhost:5000")
        print("3. Login with admin@example.com / admin123")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
