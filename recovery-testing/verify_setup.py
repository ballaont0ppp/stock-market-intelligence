"""
Verify Recovery Testing Setup

This script verifies that all prerequisites are met for running recovery tests.
"""
import sys
import os
import subprocess
import mysql.connector
from mysql.connector import Error
import requests

def print_status(message, status):
    """Print status message"""
    symbol = "✓" if status else "✗"
    print(f"{symbol} {message}")
    return status

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 8)
    status = version >= required
    print_status(
        f"Python version {version.major}.{version.minor}.{version.micro} (required: {required[0]}.{required[1]}+)",
        status
    )
    return status

def check_dependencies():
    """Check required Python packages"""
    required_packages = [
        'pytest',
        'requests',
        'psutil',
        'mysql.connector'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print_status(f"Package '{package}' installed", True)
        except ImportError:
            print_status(f"Package '{package}' NOT installed", False)
            all_installed = False
    
    return all_installed

def check_mysql_tools():
    """Check MySQL command-line tools"""
    tools = ['mysql', 'mysqldump']
    all_available = True
    
    for tool in tools:
        try:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print_status(f"MySQL tool '{tool}' available: {version}", True)
            else:
                print_status(f"MySQL tool '{tool}' NOT available", False)
                all_available = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_status(f"MySQL tool '{tool}' NOT found", False)
            all_available = False
    
    return all_available

def check_database_connection():
    """Check database connection"""
    try:
        from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
        
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            print_status(f"Database connection successful (MySQL {version})", True)
            return True
        else:
            print_status("Database connection failed", False)
            return False
    except Error as e:
        print_status(f"Database connection error: {e}", False)
        return False
    except ImportError:
        print_status("Config file not found or invalid", False)
        return False

def check_application_running():
    """Check if application is running"""
    try:
        from config import TEST_BASE_URL
        
        response = requests.get(TEST_BASE_URL, timeout=5)
        status = response.status_code in [200, 302, 401]
        print_status(
            f"Application responding at {TEST_BASE_URL} (status: {response.status_code})",
            status
        )
        return status
    except requests.exceptions.RequestException as e:
        print_status(f"Application not responding: {e}", False)
        return False
    except ImportError:
        print_status("Config file not found or invalid", False)
        return False

def check_directories():
    """Check required directories"""
    directories = ['results', 'backups', 'screenshots']
    all_exist = True
    
    for directory in directories:
        if os.path.exists(directory):
            print_status(f"Directory '{directory}' exists", True)
        else:
            print_status(f"Directory '{directory}' does not exist (will be created)", True)
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print_status(f"Failed to create directory '{directory}': {e}", False)
                all_exist = False
    
    return all_exist

def check_config_file():
    """Check configuration file"""
    if os.path.exists('config.py'):
        print_status("Configuration file 'config.py' found", True)
        return True
    else:
        print_status("Configuration file 'config.py' NOT found", False)
        print("  Please create config.py or copy from .env.example")
        return False

def check_env_file():
    """Check environment file"""
    if os.path.exists('.env'):
        print_status("Environment file '.env' found", True)
        return True
    else:
        print_status("Environment file '.env' NOT found (optional)", True)
        print("  You can create .env from .env.example for custom configuration")
        return True

def main():
    """Main verification function"""
    print("=" * 80)
    print("  RECOVERY TESTING SETUP VERIFICATION")
    print("=" * 80)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Configuration File", check_config_file),
        ("Environment File", check_env_file),
        ("Python Dependencies", check_dependencies),
        ("MySQL Tools", check_mysql_tools),
        ("Database Connection", check_database_connection),
        ("Application Status", check_application_running),
        ("Required Directories", check_directories)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        print("-" * 80)
        result = check_func()
        results.append((name, result))
        print()
    
    # Summary
    print("=" * 80)
    print("  VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("✓ All checks passed! You can run the recovery tests.")
        print()
        print("To run all tests:")
        print("  python run_all_tests.py")
        print()
        print("To run individual test suites:")
        print("  pytest test_database_recovery.py -v")
        print("  pytest test_application_recovery.py -v")
        print("  pytest test_network_recovery.py -v")
        print("  pytest test_data_loss_prevention.py -v")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues before running tests.")
        print()
        print("Common fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Install MySQL tools: apt-get install mysql-client (Linux)")
        print("  • Create config.py from .env.example")
        print("  • Start the application: python run.py")
        print("  • Check database credentials in config.py")
        return 1

if __name__ == '__main__':
    sys.exit(main())
