"""
Verify Performance Testing Setup

Checks that all dependencies and configurations are correct
"""

import sys
import os


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'locust',
        'psutil',
        'prometheus_client',
        'matplotlib',
        'pandas'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r performance-testing/requirements.txt")
        return False
    
    print("✓ All dependencies installed\n")
    return True


def check_files():
    """Check if required files exist"""
    print("Checking files...")
    
    required_files = [
        'performance-testing/locustfile.py',
        'performance-testing/config.py',
        'performance-testing/monitoring.py',
        'performance-testing/test_data_generator.py',
        'performance-testing/run_tests.py',
        'performance-testing/README.md'
    ]
    
    missing = []
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} - NOT FOUND")
            missing.append(filepath)
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✓ All required files present\n")
    return True


def check_directories():
    """Check if required directories exist"""
    print("Checking directories...")
    
    required_dirs = [
        'performance-testing',
        'performance-testing/reports'
    ]
    
    for dirpath in required_dirs:
        if os.path.exists(dirpath):
            print(f"  ✓ {dirpath}")
        else:
            print(f"  ℹ {dirpath} - Creating...")
            os.makedirs(dirpath, exist_ok=True)
    
    print("✓ All directories ready\n")
    return True


def check_test_data():
    """Check if test data has been generated"""
    print("Checking test data...")
    
    test_data_dir = 'performance-testing/test_data'
    test_files = [
        'test_users.csv',
        'test_companies.csv',
        'test_price_history.csv',
        'test_transactions.csv'
    ]
    
    if not os.path.exists(test_data_dir):
        print(f"  ℹ Test data not generated yet")
        print("  Run: python performance-testing/test_data_generator.py\n")
        return False
    
    missing = []
    for filename in test_files:
        filepath = os.path.join(test_data_dir, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  ✓ {filename} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {filename} - NOT FOUND")
            missing.append(filename)
    
    if missing:
        print(f"\n⚠ Missing test data files: {', '.join(missing)}")
        print("Run: python performance-testing/test_data_generator.py\n")
        return False
    
    print("✓ Test data ready\n")
    return True


def check_config():
    """Check if configuration is valid"""
    print("Checking configuration...")
    
    try:
        from config import BENCHMARKS, LOAD_TEST_SCENARIOS
        
        print(f"  ✓ {len(BENCHMARKS)} benchmarks defined")
        print(f"  ✓ {len(LOAD_TEST_SCENARIOS)} test scenarios defined")
        
        # List scenarios
        print("\n  Available scenarios:")
        for name, scenario in LOAD_TEST_SCENARIOS.items():
            print(f"    - {name}: {scenario.users} users, {scenario.duration}")
        
        print("\n✓ Configuration valid\n")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}\n")
        return False


def check_application():
    """Check if application is accessible"""
    print("Checking application...")
    
    try:
        import requests
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("  ✓ Application is running at http://localhost:5000")
            print("✓ Application accessible\n")
            return True
        else:
            print(f"  ⚠ Application returned status {response.status_code}")
            print("✓ Application accessible but may have issues\n")
            return True
    except requests.exceptions.ConnectionError:
        print("  ⚠ Application not running at http://localhost:5000")
        print("  Start with: python run.py\n")
        return False
    except Exception as e:
        print(f"  ⚠ Could not check application: {e}\n")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("PERFORMANCE TESTING SETUP VERIFICATION")
    print("="*60 + "\n")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Files", check_files),
        ("Directories", check_directories),
        ("Configuration", check_config),
        ("Test Data", check_test_data),
        ("Application", check_application)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ SETUP COMPLETE - Ready to run performance tests!")
        print("\nNext steps:")
        print("  1. python performance-testing/run_tests.py --quick")
        print("  2. python performance-testing/run_tests.py --scenario normal")
        print("  3. python performance-testing/run_tests.py --all")
    else:
        print("⚠ SETUP INCOMPLETE - Please address the issues above")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r performance-testing/requirements.txt")
        print("  - Generate test data: python performance-testing/test_data_generator.py")
        print("  - Start application: python run.py")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
