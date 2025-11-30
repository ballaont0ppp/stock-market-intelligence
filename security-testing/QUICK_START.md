# Security Testing Quick Start Guide

Get started with security testing in 5 minutes.

## Prerequisites

1. **Python 3.8+** installed
2. **Application running** at http://localhost:5000
3. **Test user account** created

## Quick Setup

### 1. Install Dependencies

```bash
cd security-testing
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file (or copy from `.env.example`):

```bash
APP_URL=http://localhost:5000
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=TestPassword123!
```

### 3. Verify Setup

```bash
python verify_setup.py
```

This will check:
- Python dependencies installed
- Application accessible
- Test credentials valid
- Required tools available

## Running Tests

### Run All Tests (Recommended)

```bash
python run_all_security_tests.py
```

This executes all 8 security test suites and generates a consolidated report.

**Duration:** ~5-10 minutes

### Run Individual Tests

```bash
# Static code analysis
python run_bandit_scan.py

# Dependency vulnerabilities
python run_dependency_check.py

# Penetration testing
python test_penetration.py

# Authentication security
python test_authentication.py

# Input validation
python test_input_validation.py

# Data protection
python test_data_protection.py

# API security
python test_api_security.py

# Compliance
python test_compliance.py
```

## Viewing Results

### HTML Reports

Open in browser:
```
reports/consolidated_security_report.html
```

Individual reports:
- `reports/bandit_report.html`
- `reports/dependency_report.html`
- `reports/penetration_report.html`
- `reports/authentication_report.html`
- `reports/input_validation_report.html`
- `reports/data_protection_report.html`
- `reports/api_security_report.html`
- `reports/compliance_report.html`

### JSON Results

Machine-readable results in `results/` directory.

## Understanding Results

### Severity Levels

- **Critical** 🔴 - Immediate action required
- **High** 🟠 - Fix before production
- **Medium** 🟡 - Address soon
- **Low** 🟢 - Consider fixing
- **Info** 🔵 - Informational only

### Common Findings

#### SQL Injection
- **Fix:** Use parameterized queries (SQLAlchemy ORM)
- **Priority:** Critical

#### XSS
- **Fix:** Enable Jinja2 auto-escaping
- **Priority:** High

#### CSRF
- **Fix:** Enable Flask-WTF CSRF protection
- **Priority:** High

#### Weak Passwords
- **Fix:** Enforce password requirements
- **Priority:** High

## Troubleshooting

### Application Not Accessible

```bash
# Start the application
python run.py
```

### Test User Not Found

```bash
# Create test user via registration page
# Or use existing user credentials
```

### Missing Dependencies

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### OWASP ZAP Not Running

```bash
# Start ZAP in daemon mode
zap.sh -daemon -port 8080 -config api.key=changeme
```

## Next Steps

1. **Review findings** in consolidated report
2. **Prioritize fixes** by severity
3. **Implement fixes** for critical/high issues
4. **Retest** after fixes
5. **Integrate** into CI/CD pipeline

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run Security Tests
  run: |
    cd security-testing
    pip install -r requirements.txt
    python run_all_security_tests.py
```

## Support

For issues:
1. Check `README.md` for detailed documentation
2. Review test logs in `results/` directory
3. Verify application is running and accessible

## Best Practices

- ✅ Run tests regularly (weekly minimum)
- ✅ Fix critical issues immediately
- ✅ Retest after fixes
- ✅ Keep dependencies updated
- ✅ Document exceptions
- ✅ Train team on findings
