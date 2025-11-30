"""
Database Initialization Script
Creates the MySQL database and user if they don't exist
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


def create_database():
    """
    Create the database and user for the application
    """
    # Parse DATABASE_URL to get connection details
    db_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/stock_portfolio')
    
    # Extract connection details
    # Format: mysql+pymysql://username:password@host:port/database
    parts = db_url.replace('mysql+pymysql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')
    
    username = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    database = host_db[1] if len(host_db) > 1 else 'stock_portfolio'
    
    print(f"Connecting to MySQL at {host}:{port}...")
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user='root',  # Use root to create database
            password=input("Enter MySQL root password: "),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database
            print(f"Creating database '{database}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Create user if not root
            if username != 'root':
                print(f"Creating user '{username}'...")
                cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO '{username}'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
            
            print("✓ Database setup completed successfully!")
            
        connection.close()
        
        # Test connection with application credentials
        print(f"\nTesting connection as '{username}'...")
        test_connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with test_connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ Connected successfully! MySQL version: {version['VERSION()']}")
        
        test_connection.close()
        
        return True
        
    except pymysql.Error as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Stock Portfolio Platform - Database Initialization")
    print("=" * 60)
    print()
    
    success = create_database()
    
    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Run: flask db init")
        print("2. Run: flask db migrate -m 'Initial migration'")
        print("3. Run: flask db upgrade")
        print("4. Run: flask seed-data")
        print("=" * 60)
    else:
        print("\n✗ Database initialization failed. Please check your settings.")
