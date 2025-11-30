# Quick Start Guide - Recovery Testing

Get started with recovery and resilience testing in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL 8.0+ running
- [ ] Stock Portfolio application running
- [ ] 10GB free disk space

## Quick Setup (5 minutes)

### Step 1: Install Dependencies (1 minute)
```bash
cd recovery-testing
pip install -r requirements.txt
```

### Step 2: Configure Environment (2 minutes)
```bash
# Copy example configuration
cp .env.example .env

# Edit configuration (use your favorite editor)
nano .env
```

Update these critical settings:
```ini
DB_PASSWORD=your_actual_password
TEST_BASE_URL=http://localhost:5000
```

### Step 3: Verify Setup (1 minute)
```bash
python verify_setup.py
```

Expected output:
```
✓ Python version 3.10.x
✓ Configuration file 'config.py' found
✓ Package 'pytest' installed
✓ MySQL tool 'mysql' available
✓ Database connection successful
✓ Application responding at http://localhost:5000
```

### Step 4: Run Tests (1 minute)
```bash
python run_all_tests.py
```

## What Gets Tested?

### 🗄️ Database Recovery (30 seconds)
- Connection recovery
- Backup/restore
- Transaction rollback

### 🖥️ Application Recovery (30 seconds)
- Crash recovery
- Memory handling
- Exception recovery

### 🌐 Network Recovery (30 seconds)
- Timeout handling
- Retry mechanisms
- Circuit breakers

### 💾 Data Loss Prevention (30 seconds)
- Backup procedures
- Point-in-time recovery
- Disaster recovery

## Understanding Results

### ✓ All Tests Passed
```
✓ All recovery tests passed!
Total: 4/4 test suites passed
```
**Action**: No action needed. System is resilient.

### ⚠ Some Tests Failed
```
✗ Some recovery tests failed
Total: 3/4 test suites passed
```
**Action**: Review `results/recovery_tests.log` for details.

## Common First-Time Issues

### Issue 1: Database Connection Failed
**Symptom:**
```
✗ Database connection error: Access denied
```

**Quick Fix:**
```bash
# Update password in .env
DB_PASSWORD=correct_password

# Test connection
mysql -h localhost -u root -p
```

### Issue 2: Application Not Running
**Symptom:**
```
✗ Application not responding
```

**Quick Fix:**
```bash
# Start application in another terminal
cd ..
python run.py
```

### Issue 3: MySQL Tools Missing
**Symptom:**
```
✗ MySQL tool 'mysqldump' NOT found
```

**Quick Fix:**
```bash
# Ubuntu/Debian
sudo apt-get install mysql-client

# macOS
brew install mysql-client

# Windows
# Download MySQL Installer from mysql.com
```

## Next Steps

### Run Individual Tests
```bash
# Test only database recovery
pytest test_database_recovery.py -v

# Test only application recovery
pytest test_application_recovery.py -v

# Test only network recovery
pytest test_network_recovery.py -v

# Test only data loss prevention
pytest test_data_loss_prevention.py -v
```

### Generate HTML Report
```bash
pytest --html=results/report.html --self-contained-html
```

### Schedule Regular Tests
Add to crontab for daily testing:
```bash
# Run recovery tests daily at 2 AM
0 2 * * * cd /path/to/recovery-testing && python run_all_tests.py
```

## Key Metrics to Monitor

| Metric | Target | Critical |
|--------|--------|----------|
| RTO (Recovery Time) | < 1 hour | < 15 min |
| RPO (Data Loss) | < 15 min | < 5 min |
| Test Pass Rate | > 95% | > 90% |
| Recovery Success | 100% | 100% |

## Getting Help

### Check Logs
```bash
# View latest test log
tail -f results/recovery_tests.log

# View application log
tail -f ../app.log

# View MySQL error log
sudo tail -f /var/log/mysql/error.log
```

### Debug Mode
```bash
# Run with verbose output
pytest -v -s --log-cli-level=DEBUG test_database_recovery.py
```

### Verify Configuration
```bash
# Check all settings
python -c "from config import *; print(f'DB: {DB_HOST}:{DB_PORT}/{DB_NAME}')"
```

## Best Practices

### ✓ Do's
- Run tests in a test environment
- Review logs after each run
- Keep backups of test results
- Schedule regular automated tests
- Monitor RTO/RPO metrics

### ✗ Don'ts
- Never run on production database
- Don't ignore warnings
- Don't skip setup verification
- Don't run without backups
- Don't modify tests without understanding

## Quick Reference

### Essential Commands
```bash
# Verify setup
python verify_setup.py

# Run all tests
python run_all_tests.py

# Run specific test
pytest test_database_recovery.py::test_backup_and_restore -v

# Generate report
pytest --html=results/report.html

# View results
cat results/recovery_test_results_*.json | jq .
```

### Important Files
```
recovery-testing/
├── config.py              # Configuration
├── .env                   # Environment variables
├── run_all_tests.py       # Main test runner
├── verify_setup.py        # Setup verification
├── results/               # Test results
│   ├── *.log             # Test logs
│   └── *.json            # Result data
└── backups/              # Database backups
```

### Configuration Quick Reference
```python
# Key settings in config.py
TEST_BASE_URL = 'http://localhost:5000'
DB_HOST = 'localhost'
DB_NAME = 'stock_portfolio_test'
RTO_TARGET_SECONDS = 3600  # 1 hour
RPO_TARGET_SECONDS = 900   # 15 minutes
```

## Success Criteria

Your recovery testing is successful when:

1. ✓ All 4 test suites pass
2. ✓ RTO < 1 hour for all scenarios
3. ✓ RPO < 15 minutes for all scenarios
4. ✓ No data integrity issues
5. ✓ All backups complete successfully
6. ✓ Application recovers automatically
7. ✓ Network failures handled gracefully
8. ✓ Transactions roll back correctly

## Troubleshooting Flowchart

```
Test Failed?
    ├─ Database Error?
    │   ├─ Check MySQL running
    │   ├─ Verify credentials
    │   └─ Test connection
    │
    ├─ Application Error?
    │   ├─ Check app running
    │   ├─ Review app logs
    │   └─ Verify port 5000
    │
    ├─ Network Error?
    │   ├─ Check connectivity
    │   ├─ Verify firewall
    │   └─ Test API endpoints
    │
    └─ Permission Error?
        ├─ Check file permissions
        ├─ Verify backup directory
        └─ Check disk space
```

## Ready to Go!

You're now ready to run comprehensive recovery tests. Start with:

```bash
python run_all_tests.py
```

For detailed documentation, see [README.md](README.md).

Good luck! 🚀
