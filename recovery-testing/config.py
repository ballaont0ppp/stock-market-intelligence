"""
Configuration for Recovery and Resilience Testing
"""
import os
from datetime import datetime

# Test Configuration
TEST_BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:5000')
TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '30'))

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'stock_portfolio_test')

# Backup Configuration
BACKUP_DIR = os.getenv('BACKUP_DIR', './recovery-testing/backups')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '7'))

# Recovery Objectives
RTO_TARGET_SECONDS = 3600  # Recovery Time Objective: 1 hour
RPO_TARGET_SECONDS = 900   # Recovery Point Objective: 15 minutes

# Network Failure Simulation
NETWORK_FAILURE_DURATION = int(os.getenv('NETWORK_FAILURE_DURATION', '10'))
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '5'))

# Application Configuration
APP_RESTART_TIMEOUT = int(os.getenv('APP_RESTART_TIMEOUT', '60'))
MEMORY_LIMIT_MB = int(os.getenv('MEMORY_LIMIT_MB', '512'))

# Test Data
TEST_USER_EMAIL = 'recovery_test@example.com'
TEST_USER_PASSWORD = 'RecoveryTest123!'
TEST_ADMIN_EMAIL = 'admin_recovery@example.com'
TEST_ADMIN_PASSWORD = 'AdminRecovery123!'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './recovery-testing/results/recovery_tests.log')

# Results Directory
RESULTS_DIR = './recovery-testing/results'
SCREENSHOTS_DIR = './recovery-testing/screenshots'

# Test Execution
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60
CIRCUIT_BREAKER_EXPECTED_EXCEPTION = Exception

# Monitoring
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '5'))
HEALTH_CHECK_TIMEOUT = int(os.getenv('HEALTH_CHECK_TIMEOUT', '3'))

# Test Scenarios
SCENARIOS = {
    'database_crash': {
        'enabled': True,
        'description': 'Simulate database server crash and recovery',
        'severity': 'critical'
    },
    'connection_loss': {
        'enabled': True,
        'description': 'Simulate database connection loss',
        'severity': 'high'
    },
    'data_corruption': {
        'enabled': True,
        'description': 'Simulate data corruption and recovery',
        'severity': 'critical'
    },
    'backup_restore': {
        'enabled': True,
        'description': 'Verify backup and restore procedures',
        'severity': 'critical'
    },
    'server_crash': {
        'enabled': True,
        'description': 'Simulate application server crash',
        'severity': 'high'
    },
    'memory_exhaustion': {
        'enabled': True,
        'description': 'Simulate memory exhaustion',
        'severity': 'high'
    },
    'unhandled_exception': {
        'enabled': True,
        'description': 'Test unhandled exception recovery',
        'severity': 'medium'
    },
    'network_failure': {
        'enabled': True,
        'description': 'Simulate network connectivity loss',
        'severity': 'high'
    },
    'api_unavailability': {
        'enabled': True,
        'description': 'Simulate external API unavailability',
        'severity': 'medium'
    },
    'timeout_handling': {
        'enabled': True,
        'description': 'Test timeout handling mechanisms',
        'severity': 'medium'
    }
}

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_test_report_filename():
    """Generate test report filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'recovery_test_report_{timestamp}.html'
