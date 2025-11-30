"""
Security Testing Configuration
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / 'reports'
RESULTS_DIR = BASE_DIR / 'results'

# Create directories if they don't exist
REPORTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Application under test
APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
APP_HOST = os.getenv('APP_HOST', 'localhost')
APP_PORT = int(os.getenv('APP_PORT', '5000'))

# Test credentials
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'testuser@example.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'TestPassword123!')
TEST_ADMIN_EMAIL = os.getenv('TEST_ADMIN_EMAIL', 'admin@example.com')
TEST_ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'AdminPassword123!')

# OWASP ZAP Configuration
ZAP_API_KEY = os.getenv('ZAP_API_KEY', 'changeme')
ZAP_PROXY_HOST = os.getenv('ZAP_PROXY_HOST', 'localhost')
ZAP_PROXY_PORT = int(os.getenv('ZAP_PROXY_PORT', '8080'))
ZAP_TIMEOUT = 300  # seconds

# Bandit Configuration
BANDIT_CONFIG = {
    'exclude_dirs': [
        'venv',
        'stock_market_venv',
        'node_modules',
        '__pycache__',
        'migrations',
        '.git'
    ],
    'severity_level': 'low',
    'confidence_level': 'low'
}

# Safety Configuration
SAFETY_CONFIG = {
    'ignore_ids': [],  # CVE IDs to ignore
    'full_report': True
}

# Snyk Configuration
SNYK_TOKEN = os.getenv('SNYK_TOKEN', '')
SNYK_ORG = os.getenv('SNYK_ORG', '')

# Security Test Scenarios
SECURITY_TESTS = {
    'sql_injection': True,
    'xss': True,
    'csrf': True,
    'authentication': True,
    'authorization': True,
    'session_management': True,
    'input_validation': True,
    'data_protection': True,
    'api_security': True,
    'ssl_tls': True,
    'security_headers': True
}

# SQL Injection Test Payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "admin' --",
    "admin' #",
    "' UNION SELECT NULL--",
    "1' AND '1'='1",
    "1' AND '1'='2"
]

# XSS Test Payloads
XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
    "<body onload=alert('XSS')>",
    "'\"><script>alert(String.fromCharCode(88,83,83))</script>"
]

# Password Strength Requirements
PASSWORD_REQUIREMENTS = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
    'min_strength_score': 3  # zxcvbn score (0-4)
}

# Session Security Requirements
SESSION_REQUIREMENTS = {
    'httponly': True,
    'secure': True,  # Should be True in production
    'samesite': 'Lax',
    'max_age': 86400  # 24 hours
}

# Security Headers Requirements
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

# API Rate Limiting
RATE_LIMIT_TESTS = {
    'login_endpoint': {
        'max_attempts': 5,
        'time_window': 900  # 15 minutes
    },
    'api_endpoints': {
        'max_requests': 100,
        'time_window': 60  # 1 minute
    }
}

# Compliance Requirements
COMPLIANCE_CHECKS = {
    'gdpr': True,
    'pci_dss': False,  # Enable if handling payment cards
    'soc2': True
}

# Report Configuration
REPORT_CONFIG = {
    'format': 'html',
    'include_screenshots': True,
    'severity_colors': {
        'critical': '#d32f2f',
        'high': '#f57c00',
        'medium': '#fbc02d',
        'low': '#388e3c',
        'info': '#1976d2'
    }
}
