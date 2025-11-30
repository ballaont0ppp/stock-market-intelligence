# Recovery and Resilience Testing Suite

Comprehensive testing framework for verifying the Stock Portfolio Management Platform's ability to recover from various failure scenarios.

## Overview

This testing suite validates the platform's resilience and recovery capabilities across four critical areas:

1. **Database Failure Recovery** - Database crashes, connection loss, data corruption
2. **Application Failure Recovery** - Server crashes, memory exhaustion, exception handling
3. **Network Failure Recovery** - Connectivity loss, API unavailability, timeout handling
4. **Data Loss Prevention** - Backup procedures, point-in-time recovery, disaster recovery

## Test Coverage

### Database Recovery Tests
- ✓ Database connection recovery after connection loss
- ✓ Backup and restore procedures
- ✓ Transaction rollback on failure
- ✓ Connection pool recovery after exhaustion
- ✓ Data corruption detection and recovery
- ✓ Recovery Time Objective (RTO) compliance
- ✓ Recovery Point Objective (RPO) compliance

### Application Recovery Tests
- ✓ Server crash recovery
- ✓ Graceful shutdown procedures
- ✓ Memory exhaustion handling
- ✓ Unhandled exception recovery
- ✓ Database connection recovery after restart
- ✓ Concurrent request handling after recovery
- ✓ Auto-restart mechanism verification

### Network Recovery Tests
- ✓ Network timeout handling
- ✓ Retry mechanism verification
- ✓ Circuit breaker pattern implementation
- ✓ Connection refused handling
- ✓ API unavailability handling
- ✓ Connection pooling
- ✓ External API failure recovery
- ✓ Network latency handling
- ✓ Concurrent network request handling

### Data Loss Prevention Tests
- ✓ Full backup procedures
- ✓ Incremental backup procedures
- ✓ Point-in-time recovery
- ✓ Transaction atomicity (ACID compliance)
- ✓ Data integrity checks
- ✓ Disaster recovery plan execution
- ✓ Backup retention policy
- ✓ RPO compliance verification
- ✓ Concurrent backup operations

## Prerequisites

### System Requirements
- Python 3.8 or higher
- MySQL 8.0 or higher
- MySQL command-line tools (mysql, mysqldump)
- 2GB RAM minimum
- 10GB disk space for backups

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- pytest >= 7.4.0
- requests >= 2.31.0
- psutil >= 5.9.5
- mysql-connector-python >= 8.1.0
- python-dotenv >= 1.0.0

### Application Requirements
- Stock Portfolio Management Platform must be running
- Database must be accessible
- Test user accounts must exist

## Setup

### 1. Install Dependencies
```bash
cd recovery-testing
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment file and update with your settings:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```ini
# Application
TEST_BASE_URL=http://localhost:5000

# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=stock_portfolio_test

# Backup
BACKUP_DIR=./backups
```

### 3. Verify Setup
Run the setup verification script:
```bash
python verify_setup.py
```

This will check:
- Python version
- Required dependencies
- MySQL tools availability
- Database connectivity
- Application status
- Directory structure

## Running Tests

### Run All Tests
Execute the complete test suite:
```bash
python run_all_tests.py
```

This will:
- Run all four test suites sequentially
- Generate detailed logs
- Create a summary report
- Save results to JSON

### Run Individual Test Suites

**Database Recovery Tests:**
```bash
pytest test_database_recovery.py -v
```

**Application Recovery Tests:**
```bash
pytest test_application_recovery.py -v
```

**Network Recovery Tests:**
```bash
pytest test_network_recovery.py -v
```

**Data Loss Prevention Tests:**
```bash
pytest test_data_loss_prevention.py -v
```

### Run Specific Tests
```bash
pytest test_database_recovery.py::test_database_connection_recovery -v
pytest test_application_recovery.py::test_server_crash_recovery -v
pytest test_network_recovery.py::test_retry_mechanism -v
pytest test_data_loss_prevention.py::test_disaster_recovery_plan -v
```

### Generate HTML Report
```bash
pytest --html=results/report.html --self-contained-html
```

## Test Results

### Output Locations
- **Logs**: `results/recovery_tests.log`
- **JSON Results**: `results/recovery_test_results_YYYYMMDD_HHMMSS.json`
- **HTML Reports**: `results/report.html`
- **Backups**: `backups/`
- **Screenshots**: `screenshots/`

### Understanding Results

**Test Status Indicators:**
- ✓ PASSED - Test completed successfully
- ✗ FAILED - Test failed, review logs for details
- ⚠ WARNING - Test completed with warnings

**Key Metrics:**
- **RTO (Recovery Time Objective)**: Target < 1 hour
- **RPO (Recovery Point Objective)**: Target < 15 minutes
- **Success Rate**: Target > 90%
- **Recovery Time**: Measured for each scenario

## Recovery Objectives

### RTO (Recovery Time Objective)
Maximum acceptable time to restore service after failure:
- **Target**: 1 hour (3600 seconds)
- **Critical Services**: 15 minutes
- **Non-Critical Services**: 4 hours

### RPO (Recovery Point Objective)
Maximum acceptable data loss measured in time:
- **Target**: 15 minutes (900 seconds)
- **Critical Data**: 5 minutes
- **Non-Critical Data**: 1 hour

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
```
Error: Database connection failed
```
**Solution:**
- Verify database is running: `systemctl status mysql`
- Check credentials in `.env`
- Test connection: `mysql -h localhost -u root -p`

**2. Application Not Responding**
```
Error: Application not responding
```
**Solution:**
- Start the application: `python run.py`
- Check application logs: `tail -f app.log`
- Verify port 5000 is not in use: `netstat -an | grep 5000`

**3. MySQL Tools Not Found**
```
Error: MySQL tool 'mysqldump' NOT found
```
**Solution:**
- Install MySQL client tools:
  - Ubuntu/Debian: `sudo apt-get install mysql-client`
  - CentOS/RHEL: `sudo yum install mysql`
  - macOS: `brew install mysql-client`
  - Windows: Install MySQL Workbench or MySQL Shell

**4. Permission Denied for Backups**
```
Error: Permission denied: './backups'
```
**Solution:**
- Create backup directory: `mkdir -p backups`
- Set permissions: `chmod 755 backups`

**5. Tests Timeout**
```
Error: Test suite timed out
```
**Solution:**
- Increase timeout in config: `TEST_TIMEOUT=60`
- Check system resources: `top` or `htop`
- Reduce concurrent tests

### Debug Mode
Run tests with verbose output:
```bash
pytest -v -s --log-cli-level=DEBUG
```

## Best Practices

### Before Running Tests
1. **Backup Production Data** - Never run on production database
2. **Use Test Environment** - Dedicated test database and application instance
3. **Check Resources** - Ensure sufficient disk space and memory
4. **Review Configuration** - Verify all settings in `.env`

### During Testing
1. **Monitor Resources** - Watch CPU, memory, and disk usage
2. **Review Logs** - Check logs for warnings and errors
3. **Document Issues** - Note any unexpected behavior
4. **Isolate Failures** - Run failed tests individually for debugging

### After Testing
1. **Review Results** - Analyze test reports and metrics
2. **Clean Up** - Remove old backups and test data
3. **Update Documentation** - Document any issues or improvements
4. **Plan Improvements** - Address any failed tests or warnings

## Continuous Integration

### GitHub Actions Example
```yaml
name: Recovery Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  recovery-tests:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: stock_portfolio_test
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd recovery-testing
          pip install -r requirements.txt
      
      - name: Run recovery tests
        run: |
          cd recovery-testing
          python run_all_tests.py
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: recovery-test-results
          path: recovery-testing/results/
```

## Metrics and Reporting

### Key Performance Indicators (KPIs)
- **Test Pass Rate**: Target > 95%
- **Average Recovery Time**: Target < 30 seconds
- **RTO Compliance**: Target 100%
- **RPO Compliance**: Target 100%
- **Data Integrity**: Target 100%

### Report Contents
1. **Executive Summary** - High-level results and metrics
2. **Detailed Results** - Individual test outcomes
3. **Performance Metrics** - Recovery times and resource usage
4. **Compliance Status** - RTO/RPO compliance
5. **Recommendations** - Improvements and action items

## Support

### Documentation
- [Quick Start Guide](QUICK_START.md)
- [Configuration Guide](CONFIG.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

### Contact
For issues or questions:
- Create an issue in the project repository
- Contact the development team
- Review the main project documentation

## License

This testing suite is part of the Stock Portfolio Management Platform project.

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- Database recovery tests
- Application recovery tests
- Network recovery tests
- Data loss prevention tests
- Comprehensive documentation
- CI/CD integration examples
