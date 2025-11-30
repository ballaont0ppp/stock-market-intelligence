# Security Testing Suite

Comprehensive security testing framework for the Stock Portfolio Management Platform.

## Overview

This security testing suite provides automated security testing capabilities including:
- Vulnerability scanning (OWASP ZAP)
- Static code analysis (Bandit)
- Dependency vulnerability checking (Safety, Snyk)
- Authentication security testing
- Input validation testing
- Data protection testing
- API security testing
- Compliance validation

## Prerequisites

### Required Tools

1. **Python 3.8+**
2. **OWASP ZAP** (for vulnerability scanning)
   - Download from: https://www.zaproxy.org/download/
   - Or install via package manager:
     ```bash
     # Windows (Chocolatey)
     choco install zap
     
     # macOS
     brew install --cask owasp-zap
     
     # Linux
     sudo snap install zaproxy --classic
     ```

3. **Bandit** (installed via pip)
4. **Safety** (installed via pip)
5. **Snyk** (optional, requires account)
   - Sign up at: https://snyk.io/
   - Install CLI: `npm install -g snyk`

### Environment Setup

1. Install Python dependencies:
   ```bash
   cd security-testing
   pip install -r requirements.txt
   ```

2. Configure environment variables (create `.env` file):
   ```bash
   APP_URL=http://localhost:5000
   APP_HOST=localhost
   APP_PORT=5000
   
   TEST_USER_EMAIL=testuser@example.com
   TEST_USER_PASSWORD=TestPassword123!
   TEST_ADMIN_EMAIL=admin@example.com
   TEST_ADMIN_PASSWORD=AdminPassword123!
   
   ZAP_API_KEY=changeme
   ZAP_PROXY_HOST=localhost
   ZAP_PROXY_PORT=8080
   
   SNYK_TOKEN=your_snyk_token_here
   SNYK_ORG=your_org_name
   ```

3. Start OWASP ZAP in daemon mode:
   ```bash
   # Windows
   "C:\Program Files\OWASP\Zed Attack Proxy\zap.bat" -daemon -port 8080 -config api.key=changeme
   
   # macOS/Linux
   zap.sh -daemon -port 8080 -config api.key=changeme
   ```

## Test Suites

### 1. Vulnerability Assessment
```bash
python run_vulnerability_scan.py
```
- Network-based scanning
- Host-based scanning
- Application-based scanning
- Generates vulnerability report

### 2. Static Code Analysis
```bash
python run_bandit_scan.py
```
- Scans Python code for security issues
- Identifies common vulnerabilities
- Generates detailed report

### 3. Dependency Vulnerability Check
```bash
python run_dependency_check.py
```
- Checks for known vulnerabilities in dependencies
- Uses Safety and Snyk
- Provides remediation recommendations

### 4. Authentication Security Testing
```bash
python test_authentication.py
```
- Password strength validation
- Session management testing
- Role-based access control
- Brute force protection

### 5. Input Validation Testing
```bash
python test_input_validation.py
```
- SQL injection testing
- XSS prevention testing
- CSRF protection testing
- File upload validation

### 6. Data Protection Testing
```bash
python test_data_protection.py
```
- Password hashing verification
- Session cookie security
- Data encryption testing
- PII data masking

### 7. API Security Testing
```bash
python test_api_security.py
```
- Rate limiting validation
- API authentication testing
- Request/response validation
- API versioning

### 8. Compliance Testing
```bash
python test_compliance.py
```
- GDPR compliance checks
- PCI-DSS validation (if applicable)
- SOC 2 preparation
- Compliance documentation

## Running All Tests

Execute all security tests:
```bash
python run_all_security_tests.py
```

This will:
1. Run all test suites
2. Generate individual reports
3. Create a consolidated security report
4. Provide remediation recommendations

## Reports

All reports are generated in the `reports/` directory:
- `vulnerability_report.html` - OWASP ZAP scan results
- `bandit_report.html` - Static code analysis
- `dependency_report.html` - Dependency vulnerabilities
- `authentication_report.html` - Auth security tests
- `input_validation_report.html` - Input validation tests
- `data_protection_report.html` - Data protection tests
- `api_security_report.html` - API security tests
- `compliance_report.html` - Compliance validation
- `consolidated_report.html` - All results combined

## Interpreting Results

### Severity Levels
- **Critical**: Immediate action required
- **High**: Should be fixed before production
- **Medium**: Should be addressed in near term
- **Low**: Consider fixing when convenient
- **Info**: Informational only

### Common Issues and Fixes

#### SQL Injection
- Use parameterized queries
- Validate and sanitize all inputs
- Use ORM (SQLAlchemy) properly

#### XSS
- Enable Jinja2 auto-escaping
- Sanitize user-generated content
- Set Content-Security-Policy headers

#### CSRF
- Enable CSRF protection on all forms
- Use Flask-WTF CSRF tokens
- Validate tokens on POST requests

#### Session Security
- Set HttpOnly, Secure, SameSite flags
- Implement session timeout
- Regenerate session ID on login

## Best Practices

1. **Run tests regularly** - Integrate into CI/CD pipeline
2. **Fix critical issues first** - Prioritize by severity
3. **Retest after fixes** - Verify vulnerabilities are resolved
4. **Keep dependencies updated** - Regularly update packages
5. **Document exceptions** - If ignoring findings, document why
6. **Train developers** - Share findings and best practices

## Troubleshooting

### OWASP ZAP Connection Issues
- Ensure ZAP is running in daemon mode
- Check API key matches configuration
- Verify proxy port is not in use

### Bandit False Positives
- Add `# nosec` comment to suppress specific warnings
- Update `.bandit` configuration file
- Document why issues are false positives

### Snyk Authentication Issues
- Run `snyk auth` to authenticate
- Verify SNYK_TOKEN is set correctly
- Check organization access permissions

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [Snyk Documentation](https://docs.snyk.io/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test logs in `results/` directory
3. Consult security testing documentation
4. Contact security team
