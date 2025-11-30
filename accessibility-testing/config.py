"""
Configuration for Accessibility Testing
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / 'results'
SCREENSHOTS_DIR = BASE_DIR / 'screenshots'
REPORTS_DIR = BASE_DIR / 'reports'

# Create directories if they don't exist
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Application Configuration
APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'testuser@example.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'TestPassword123!')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'AdminPassword123!')

# WCAG Compliance Configuration
WCAG_LEVEL = os.getenv('WCAG_LEVEL', 'AA')  # A, AA, or AAA
WCAG_VERSION = os.getenv('WCAG_VERSION', '2.1')  # 2.0, 2.1, or 2.2
CONTRAST_RATIO_NORMAL = float(os.getenv('CONTRAST_RATIO_NORMAL', '4.5'))  # 4.5:1 for AA
CONTRAST_RATIO_LARGE = float(os.getenv('CONTRAST_RATIO_LARGE', '3.0'))  # 3:1 for AA large text
MIN_TOUCH_TARGET_SIZE = int(os.getenv('MIN_TOUCH_TARGET_SIZE', '44'))  # 44x44px minimum

# Browser Configuration
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
BROWSER = os.getenv('BROWSER', 'chrome')  # chrome, firefox, edge
WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1920'))
WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '1080'))

# Screenshot Configuration
SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'screenshots')

# Report Configuration
REPORT_DIR = os.getenv('REPORT_DIR', 'results')
REPORT_FORMAT = os.getenv('REPORT_FORMAT', 'html,json').split(',')

# Test Pages to Audit
TEST_PAGES = [
    {'name': 'Home', 'path': '/', 'requires_auth': False},
    {'name': 'Login', 'path': '/auth/login', 'requires_auth': False},
    {'name': 'Register', 'path': '/auth/register', 'requires_auth': False},
    {'name': 'Dashboard', 'path': '/dashboard', 'requires_auth': True},
    {'name': 'Portfolio', 'path': '/portfolio', 'requires_auth': True},
    {'name': 'Wallet', 'path': '/portfolio/wallet', 'requires_auth': True},
    {'name': 'Orders', 'path': '/orders', 'requires_auth': True},
    {'name': 'Buy Order', 'path': '/orders/buy', 'requires_auth': True},
    {'name': 'Sell Order', 'path': '/orders/sell', 'requires_auth': True},
    {'name': 'Reports', 'path': '/reports', 'requires_auth': True},
    {'name': 'Notifications', 'path': '/notifications', 'requires_auth': True},
    {'name': 'Profile', 'path': '/auth/profile', 'requires_auth': True},
]

# Accessibility Rules to Test
ACCESSIBILITY_RULES = {
    'visual': [
        'color-contrast',
        'image-alt',
        'label',
        'link-name',
        'button-name',
    ],
    'keyboard': [
        'focus-order-semantics',
        'tabindex',
        'accesskeys',
        'skip-link',
    ],
    'structure': [
        'heading-order',
        'landmark-one-main',
        'page-has-heading-one',
        'region',
    ],
    'forms': [
        'label',
        'form-field-multiple-labels',
        'input-button-name',
        'select-name',
    ],
    'aria': [
        'aria-allowed-attr',
        'aria-required-attr',
        'aria-valid-attr-value',
        'aria-roles',
    ]
}

# Keyboard Navigation Test Sequences
KEYBOARD_SEQUENCES = {
    'tab_navigation': ['TAB'] * 20,
    'shift_tab_navigation': ['SHIFT+TAB'] * 20,
    'enter_activation': ['ENTER'],
    'space_activation': ['SPACE'],
    'escape_close': ['ESCAPE'],
    'arrow_navigation': ['ARROW_DOWN', 'ARROW_UP', 'ARROW_LEFT', 'ARROW_RIGHT'],
}

# Screen Reader Test Configuration
SCREEN_READER_CONFIG = {
    'nvda': {
        'enabled': True,
        'executable': 'C:\\Program Files (x86)\\NVDA\\nvda.exe',
    },
    'jaws': {
        'enabled': False,
        'executable': 'C:\\Program Files\\Freedom Scientific\\JAWS\\2023\\jfw.exe',
    }
}

# Color Contrast Test Pairs (foreground, background)
COLOR_TEST_PAIRS = [
    ('#333333', '#ffffff'),  # Dark text on white
    ('#ffffff', '#007bff'),  # White text on primary blue
    ('#ffffff', '#28a745'),  # White text on success green
    ('#ffffff', '#dc3545'),  # White text on danger red
    ('#ffffff', '#ffc107'),  # White text on warning yellow
]

# Text Resize Test Levels
TEXT_RESIZE_LEVELS = [100, 125, 150, 175, 200]  # Percentage

# Timeout Configuration
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 10
IMPLICIT_WAIT = 5

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
