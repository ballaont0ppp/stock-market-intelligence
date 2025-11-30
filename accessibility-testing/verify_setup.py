"""
Verify that the accessibility testing environment is properly set up
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (3.8+ required)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        'selenium',
        'pytest',
        'axe_selenium_python',
        'webdriver_manager',
        'PIL',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (not installed)")
            all_installed = False
    
    return all_installed


def check_config_file():
    """Check if .env file exists"""
    print("\nChecking configuration...")
    
    env_file = Path(__file__).parent / '.env'
    env_example = Path(__file__).parent / '.env.example'
    
    if env_file.exists():
        print(f"✓ .env file exists")
        return True
    elif env_example.exists():
        print(f"⚠ .env file not found, but .env.example exists")
        print(f"  Copy .env.example to .env and configure your settings")
        return False
    else:
        print(f"✗ Neither .env nor .env.example found")
        return False


def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    base_dir = Path(__file__).parent
    required_dirs = ['results', 'screenshots', 'reports']
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"⚠ {dir_name}/ directory not found (will be created automatically)")
    
    return True


def check_browser_driver():
    """Check if browser driver can be initialized"""
    print("\nChecking browser driver...")
    
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("Attempting to initialize Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.quit()
        print("✓ Chrome driver initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize Chrome driver: {e}")
        print("  Make sure Chrome browser is installed")
        return False


def check_app_connectivity():
    """Check if the application is accessible"""
    print("\nChecking application connectivity...")
    
    try:
        import config
        import requests
        
        response = requests.get(config.APP_URL, timeout=10)
        if response.status_code == 200:
            print(f"✓ Application accessible at {config.APP_URL}")
            return True
        else:
            print(f"⚠ Application returned status code {response.status_code}")
            return False
    except ImportError:
        print("⚠ Cannot import config (create .env file first)")
        return False
    except Exception as e:
        print(f"✗ Cannot connect to application: {e}")
        print("  Make sure the application is running")
        return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("ACCESSIBILITY TESTING SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config_file),
        ("Directories", check_directories),
        ("Browser Driver", check_browser_driver),
        ("Application", check_app_connectivity)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during {name} check: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! You're ready to run accessibility tests.")
        print("\nRun tests with: python run_all_tests.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above before running tests.")
        print("\nInstall dependencies with: pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
