"""
Configuration for Compatibility Testing Suite
"""
import os
from datetime import datetime

# Base Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SCREENSHOTS_DIR = os.path.join(RESULTS_DIR, 'screenshots')
REPORTS_DIR = os.path.join(RESULTS_DIR, 'reports')

# Create directories if they don't exist
for directory in [RESULTS_DIR, SCREENSHOTS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Application Under Test
APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
APP_NAME = 'Stock Portfolio Management Platform'

# Test User Credentials
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'testuser@example.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'TestPassword123!')
TEST_ADMIN_EMAIL = os.getenv('TEST_ADMIN_EMAIL', 'admin@example.com')
TEST_ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'AdminPassword123!')

# Browser Configuration
BROWSERS = {
    'chrome': {
        'versions': ['latest', 'latest-1'],
        'driver': 'chromedriver',
        'enabled': True
    },
    'firefox': {
        'versions': ['latest', 'latest-1'],
        'driver': 'geckodriver',
        'enabled': True
    },
    'edge': {
        'versions': ['latest', 'latest-1'],
        'driver': 'msedgedriver',
        'enabled': True
    },
    'safari': {
        'versions': ['latest', 'latest-1'],
        'driver': 'safaridriver',
        'enabled': False  # Safari only on macOS
    }
}

# Operating System Configuration
OPERATING_SYSTEMS = {
    'windows': {
        'versions': ['10', '11'],
        'enabled': True
    },
    'macos': {
        'versions': ['Monterey', 'Ventura'],
        'enabled': False  # Requires macOS
    },
    'linux': {
        'versions': ['Ubuntu 22.04', 'CentOS 8'],
        'enabled': True
    }
}

# Device Configuration
DEVICES = {
    'desktop': {
        'resolutions': [
            {'width': 1920, 'height': 1080, 'name': 'Full HD'},
            {'width': 1366, 'height': 768, 'name': 'HD'},
            {'width': 2560, 'height': 1440, 'name': '2K'},
        ],
        'enabled': True
    },
    'tablet': {
        'devices': [
            {'width': 768, 'height': 1024, 'name': 'iPad Portrait'},
            {'width': 1024, 'height': 768, 'name': 'iPad Landscape'},
            {'width': 800, 'height': 1280, 'name': 'Android Tablet'},
        ],
        'enabled': True
    },
    'mobile': {
        'devices': [
            {'width': 375, 'height': 667, 'name': 'iPhone SE'},
            {'width': 390, 'height': 844, 'name': 'iPhone 12/13'},
            {'width': 414, 'height': 896, 'name': 'iPhone 11 Pro Max'},
            {'width': 360, 'height': 640, 'name': 'Android Small'},
            {'width': 412, 'height': 915, 'name': 'Android Large'},
        ],
        'enabled': True
    }
}

# Network Configuration
NETWORK_CONDITIONS = {
    'fiber': {
        'download': 100000,  # kbps
        'upload': 100000,
        'latency': 5,  # ms
        'enabled': True
    },
    'cable': {
        'download': 50000,
        'upload': 10000,
        'latency': 20,
        'enabled': True
    },
    'dsl': {
        'download': 10000,
        'upload': 1000,
        'latency': 50,
        'enabled': True
    },
    '4g': {
        'download': 4000,
        'upload': 3000,
        'latency': 100,
        'enabled': True
    },
    '3g': {
        'download': 750,
        'upload': 250,
        'latency': 200,
        'enabled': True
    }
}

# Test Scenarios
TEST_SCENARIOS = [
    {
        'name': 'User Registration',
        'url': '/register',
        'actions': ['fill_form', 'submit'],
        'critical': True
    },
    {
        'name': 'User Login',
        'url': '/login',
        'actions': ['fill_form', 'submit'],
        'critical': True
    },
    {
        'name': 'Dashboard View',
        'url': '/dashboard',
        'actions': ['view', 'check_elements'],
        'critical': True
    },
    {
        'name': 'Portfolio View',
        'url': '/portfolio',
        'actions': ['view', 'check_table'],
        'critical': True
    },
    {
        'name': 'Stock Prediction',
        'url': '/dashboard',
        'actions': ['fill_form', 'submit', 'wait_results'],
        'critical': True
    },
    {
        'name': 'Buy Order',
        'url': '/orders/buy',
        'actions': ['fill_form', 'submit'],
        'critical': True
    },
    {
        'name': 'Sell Order',
        'url': '/orders/sell',
        'actions': ['fill_form', 'submit'],
        'critical': True
    },
    {
        'name': 'Transaction History',
        'url': '/orders',
        'actions': ['view', 'check_table', 'filter'],
        'critical': False
    },
    {
        'name': 'Reports Generation',
        'url': '/reports',
        'actions': ['select_type', 'generate'],
        'critical': False
    },
    {
        'name': 'Admin Dashboard',
        'url': '/admin',
        'actions': ['view', 'check_metrics'],
        'critical': False
    }
]

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'page_load_time': 3.0,  # seconds
    'time_to_interactive': 5.0,  # seconds
    'first_contentful_paint': 2.0,  # seconds
    'largest_contentful_paint': 2.5,  # seconds
}

# Compatibility Requirements
COMPATIBILITY_REQUIREMENTS = {
    'min_browser_support': {
        'chrome': 90,
        'firefox': 88,
        'edge': 90,
        'safari': 14
    },
    'responsive_breakpoints': [
        {'name': 'mobile', 'max_width': 767},
        {'name': 'tablet', 'min_width': 768, 'max_width': 1023},
        {'name': 'desktop', 'min_width': 1024}
    ],
    'touch_target_size': 44,  # pixels
    'min_contrast_ratio': 4.5
}

# Test Report Configuration
REPORT_CONFIG = {
    'format': 'html',
    'include_screenshots': True,
    'include_console_logs': True,
    'include_network_logs': False,
    'timestamp_format': '%Y-%m-%d_%H-%M-%S'
}

# Selenium Configuration
SELENIUM_CONFIG = {
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'script_timeout': 30,
    'headless': False,  # Set to True for CI/CD
    'window_size': (1920, 1080)
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(RESULTS_DIR, f'compatibility_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
}
