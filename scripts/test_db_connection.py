"""
Database Connection Test
Tests the database connection and displays configuration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text


def test_connection():
    """
    Test database connection and display information
    """
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    try:
        app = create_app('development')
        
        with app.app_context():
            # Display configuration
            print(f"\nDatabase URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"Pool Size: {app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_size']}")
            print(f"Pool Recycle: {app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_recycle']}s")
            
            # Test connection
            print("\nTesting connection...")
            result = db.session.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            
            print(f"✓ Connection successful!")
            print(f"✓ MySQL Version: {version}")
            
            # Test database name
            result = db.session.execute(text("SELECT DATABASE()"))
            database = result.fetchone()[0]
            print(f"✓ Connected to database: {database}")
            
            # Test table listing
            result = db.session.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            
            if tables:
                print(f"\n✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("\n⚠ No tables found. Run migrations to create tables.")
            
            print("\n" + "=" * 60)
            print("✓ All tests passed!")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\n" + "=" * 60)
        print("Troubleshooting:")
        print("1. Check DATABASE_URL in .env file")
        print("2. Ensure MySQL server is running")
        print("3. Verify database and user exist")
        print("4. Check credentials are correct")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
