"""
Verify Compatibility Testing Setup
Checks if all requirements are met before running tests
"""
import sys
import os
import platform
import subprocess
import requests
from config import APP_URL


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    required_packages = [
        'selenium',
        'webdriver_manager',
        'pytest',
        'requests',
        'PIL'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} installed")
        except ImportError:
            print(f"  ✗ {package} not installed")
            all_installed = False
    
    return all_installed


def check_browsers():
    """Check if browsers are available"""
    print("\nChecking browsers...")
    browsers_found = []
    
    # Check Chrome
    try:
        if platform.system() == 'Windows':
            chrome_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ]
            if any(os.path.exists(path) for path in chrome_paths):
                print("  ✓ Chrome found")
                browsers_found.append('chrome')
        else:
            result = subprocess.run(['which', 'google-chrome'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✓ Chrome found")
                browsers_found.append('chrome')
    except:
        pass
    
    # Check Firefox
    try:
        if platform.system() == 'Windows':
            firefox_paths = [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ]
            if any(os.path.exists(path) for path in firefox_paths):
                print("  ✓ Firefox found")
                browsers_found.append('firefox')
        else:
            result = subprocess.run(['which', 'firefox'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✓ Firefox found")
                browsers_found.append('firefox')
    except:
        pass
    
    # Check Edge
    try:
        if platform.system() == 'Windows':
            edge_paths = [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
            ]
            if any(os.path.exists(path) for path in edge_paths):
                print("  ✓ Edge found")
                browsers_found.append('edge')
    except:
        pass
    
    if not browsers_found:
        print("  ✗ No browsers found")
        return False
    
    return True


def check_application():
    """Check if application is accessible"""
    print(f"\nChecking application at {APP_URL}...")
    try:
        response = requests.get(APP_URL, timeout=10)
        if response.status_code == 200:
            print(f"  ✓ Application accessible (Status: {response.status_code})")
            return True
        else:
            print(f"  ⚠ Application returned status {response.status_code}")
            return True  # Still accessible, just not 200
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Cannot connect to application")
        print(f"     Make sure the application is running at {APP_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ✗ Connection timeout")
        return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    directories = ['results', 'results/screenshots', 'results/reports']
    
    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/ exists")
        else:
            print(f"  ⚠ {directory}/ does not exist (will be created)")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"     Created {directory}/")
            except Exception as e:
                print(f"     ✗ Failed to create: {str(e)}")
                all_exist = False
    
    return all_exist


def check_webdriver():
    """Check if webdriver-manager can download drivers"""
    print("\nChecking WebDriver setup...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("  ✓ WebDriver manager available")
        print("  ℹ Drivers will be downloaded automatically on first run")
        return True
    except ImportError:
        print("  ✗ WebDriver manager not available")
        return False


def print_system_info():
    """Print system information"""
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Executable: {sys.executable}")
    print("="*60)


def main():
    """Main verification"""
    print("\n" + "#"*60)
    print("# COMPATIBILITY TESTING SETUP VERIFICATION")
    print("#"*60)
    
    print_system_info()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Browsers", check_browsers),
        ("Application", check_application),
        ("Directories", check_directories),
        ("WebDriver", check_webdriver)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to run compatibility tests.")
        print("\nNext steps:")
        print("  1. Run all tests: python run_all_tests.py")
        print("  2. Or run individual tests:")
        print("     - python test_browser_compatibility.py")
        print("     - python test_os_compatibility.py")
        print("     - python test_device_compatibility.py")
        print("     - python test_network_compatibility.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Install Chrome: https://www.google.com/chrome/")
        print("  - Start application: python run.py")
        return 1


if __name__ == '__main__':
    exit(main())
