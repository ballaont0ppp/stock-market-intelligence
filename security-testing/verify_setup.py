"""
Verify Security Testing Setup
Checks all prerequisites and configuration
"""
import sys
import subprocess
from pathlib import Path

# Check Python version
print("=" * 70)
print("Security Testing Setup Verification")
print("=" * 70)

print("\n[1/6] Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"    ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"    ✗ Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor})")
    sys.exit(1)

# Check required packages
print("\n[2/6] Checking required packages...")
required_packages = [
    'requests',
    'jinja2',
    'zxcvbn',
    'bandit'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"    ✓ {package}")
    except ImportError:
        print(f"    ✗ {package} not installed")
        missing_packages.append(package)

if missing_packages:
    print(f"\n    Install missing packages:")
    print(f"    pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Check configuration
print("\n[3/6] Checking configuration...")
try:
    from config import APP_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD
    print(f"    ✓ Configuration loaded")
    print(f"      APP_URL: {APP_URL}")
    print(f"      TEST_USER_EMAIL: {TEST_USER_EMAIL}")
except ImportError as e:
    print(f"    ✗ Configuration error: {e}")
    sys.exit(1)

# Check application accessibility
print("\n[4/6] Checking application accessibility...")
try:
    import requests
    response = requests.get(APP_URL, timeout=5)
    if response.status_code < 500:
        print(f"    ✓ Application accessible at {APP_URL}")
    else:
        print(f"    ✗ Application returned error: {response.status_code}")
        sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"    ✗ Cannot connect to application: {e}")
    print(f"      Make sure application is running at {APP_URL}")
    sys.exit(1)

# Check directories
print("\n[5/6] Checking directories...")
from config import REPORTS_DIR, RESULTS_DIR

if REPORTS_DIR.exists():
    print(f"    ✓ Reports directory: {REPORTS_DIR}")
else:
    print(f"    ✗ Reports directory not found: {REPORTS_DIR}")

if RESULTS_DIR.exists():
    print(f"    ✓ Results directory: {RESULTS_DIR}")
else:
    print(f"    ✗ Results directory not found: {RESULTS_DIR}")

# Check optional tools
print("\n[6/6] Checking optional tools...")

# Check Bandit
try:
    result = subprocess.run(['bandit', '--version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        print(f"    ✓ Bandit installed")
    else:
        print(f"    ✗ Bandit not working properly")
except (FileNotFoundError, subprocess.TimeoutExpired):
    print(f"    ✗ Bandit not found (install: pip install bandit)")

# Check Safety
try:
    result = subprocess.run(['safety', '--version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        print(f"    ✓ Safety installed")
    else:
        print(f"    ~ Safety not working properly")
except (FileNotFoundError, subprocess.TimeoutExpired):
    print(f"    ~ Safety not found (install: pip install safety)")

# Check OWASP ZAP (optional)
print(f"    ~ OWASP ZAP (optional, for vulnerability scanning)")
print(f"      Download from: https://www.zaproxy.org/download/")

print("\n" + "=" * 70)
print("Setup Verification Complete!")
print("=" * 70)
print("\nYou can now run security tests:")
print("  python run_all_security_tests.py")
print("\nOr run individual tests:")
print("  python run_bandit_scan.py")
print("  python test_authentication.py")
print("  python test_input_validation.py")
print("  etc.")
print("\n" + "=" * 70)
