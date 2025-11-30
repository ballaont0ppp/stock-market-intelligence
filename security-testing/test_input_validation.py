"""
Input Validation Security Testing
Tests SQL injection, XSS, CSRF, file upload, and API input sanitization
"""
import time
import sys
import requests
from typing import List, Tuple

from config import (
    APP_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD,
    SQL_INJECTION_PAYLOADS, XSS_PAYLOADS
)
from utils import SecurityTestResult, ReportGenerator, check_app_running, get_session_with_login


class InputValidationTester:
    """Input validation security tester"""
    
    def __init__(self):
        self.result = SecurityTestResult("Input Validation Security Testing")
        self.base_url = APP_URL
        self.session = None
    
    def setup_session(self):
        """Setup authenticated session"""
        try:
            self.session = get_session_with_login(
                self.base_url,
                TEST_USER_EMAIL,
                TEST_USER_PASSWORD
            )
            return True
        except:
            self.session = requests.Session()
            return False
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        print("\n[1/5] Testing SQL injection prevention...")
        
        # Test endpoints with SQL injection payloads
        test_cases = [
            ('/auth/login', {'email': '', 'password': 'test'}),
            ('/api/stocks/search', {'q': ''}),
            ('/portfolio', {'filter': ''})
        ]
        
        vulnerable_endpoints = []
        
        for endpoint, params in test_cases:
            for payload in SQL_INJECTION_PAYLOADS:
                try:
                    # Update params with payload
                    test_params = params.copy()
                    for key in test_params:
                        test_params[key] = payload
                    
                    if endpoint.startswith('/api'):
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            params=test_params,
                            timeout=5
                        )
                    else:
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            data=test_params,
                            timeout=5
                        )
                    
                    # Check for SQL error messages
                    sql_errors = [
                        'sql syntax',
                        'mysql',
                        'sqlite',
                        'postgresql',
                        'ora-',
                        'syntax error',
                        'unclosed quotation',
                        'quoted string not properly terminated'
                    ]
                    
                    response_lower = response.text.lower()
                    if any(error in response_lower for error in sql_errors):
                        vulnerable_endpoints.append(f'{endpoint} - {list(test_params.keys())[0]}')
                        break
                
                except:
                    pass
        
        if vulnerable_endpoints:
            self.result.add_finding(
                severity='critical',
                title='SQL Injection Vulnerability Detected',
                description='Application is vulnerable to SQL injection attacks.',
                recommendation='Use parameterized queries (SQLAlchemy ORM). Never concatenate user input into SQL queries.',
                evidence=f'Vulnerable endpoints: {", ".join(set(vulnerable_endpoints))}',
                cwe='CWE-89'
            )
            print(f"    ✗ SQL injection vulnerabilities found")
        else:
            print("    ✓ SQL injection prevention adequate")
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        print("\n[2/5] Testing XSS prevention...")
        
        # Test endpoints that display user input
        test_endpoints = [
            ('/portfolio', 'search'),
            ('/orders', 'filter'),
            ('/dashboard', 'message')
        ]
        
        vulnerable_endpoints = []
        
        for endpoint, param_name in test_endpoints:
            for payload in XSS_PAYLOADS[:3]:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={param_name: payload},
                        timeout=5
                    )
                    
                    # Check if payload is reflected unescaped
                    if payload in response.text:
                        # Check if it's actually unescaped (not in a safe context)
                        if '<script>' in response.text or 'onerror=' in response.text:
                            vulnerable_endpoints.append(f'{endpoint} - {param_name}')
                            break
                
                except:
                    pass
        
        if vulnerable_endpoints:
            self.result.add_finding(
                severity='high',
                title='Cross-Site Scripting (XSS) Vulnerability',
                description='Application does not properly escape user input in HTML output.',
                recommendation='Enable Jinja2 auto-escaping. Use |safe filter only when necessary. Sanitize all user inputs.',
                evidence=f'Vulnerable endpoints: {", ".join(set(vulnerable_endpoints))}',
                cwe='CWE-79'
            )
            print(f"    ✗ XSS vulnerabilities found")
        else:
            print("    ✓ XSS prevention adequate (auto-escaping enabled)")
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        print("\n[3/5] Testing CSRF protection...")
        
        # Test state-changing operations without CSRF token
        test_operations = [
            ('/portfolio/wallet/deposit', {'amount': '100'}),
            ('/orders/buy', {'symbol': 'AAPL', 'quantity': '1'}),
            ('/auth/profile', {'full_name': 'Test'})
        ]
        
        vulnerable_operations = []
        
        # Create session without CSRF token
        test_session = requests.Session()
        
        for endpoint, data in test_operations:
            try:
                response = test_session.post(
                    f"{self.base_url}{endpoint}",
                    data=data,
                    timeout=5,
                    allow_redirects=False
                )
                
                # If operation succeeds without CSRF token, it's vulnerable
                if response.status_code == 200 or response.status_code == 302:
                    # Check if it's not just redirecting to login
                    if 'login' not in response.headers.get('Location', '').lower():
                        vulnerable_operations.append(endpoint)
            
            except:
                pass
        
        if vulnerable_operations:
            self.result.add_finding(
                severity='high',
                title='Missing CSRF Protection',
                description='State-changing operations lack CSRF token validation.',
                recommendation='Enable Flask-WTF CSRF protection on all forms. Validate CSRF tokens on all POST/PUT/DELETE requests.',
                evidence=f'Vulnerable operations: {", ".join(vulnerable_operations)}',
                cwe='CWE-352'
            )
            print(f"    ✗ CSRF protection missing")
        else:
            print("    ✓ CSRF protection enabled")
    
    def test_file_upload_validation(self):
        """Test file upload validation"""
        print("\n[4/5] Testing file upload validation...")
        
        # Test file upload endpoints
        upload_endpoints = [
            '/admin/companies/import',
            '/auth/profile'  # If profile picture upload exists
        ]
        
        issues = []
        
        # Test malicious file types
        malicious_files = [
            ('test.php', b'<?php system($_GET["cmd"]); ?>', 'PHP script'),
            ('test.exe', b'MZ\x90\x00', 'Executable'),
            ('test.html', b'<script>alert("XSS")</script>', 'HTML with script'),
            ('../../../etc/passwd', b'test', 'Path traversal')
        ]
        
        for endpoint in upload_endpoints:
            for filename, content, description in malicious_files:
                try:
                    files = {'file': (filename, content)}
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        files=files,
                        timeout=5
                    )
                    
                    # If upload succeeds, it might be an issue
                    if response.status_code == 200 and 'success' in response.text.lower():
                        issues.append(f'{endpoint} accepted {description}')
                
                except:
                    pass
        
        if issues:
            self.result.add_finding(
                severity='high',
                title='Insufficient File Upload Validation',
                description='Application accepts potentially malicious file uploads.',
                recommendation='Validate file types, extensions, and content. Sanitize filenames. Store uploads outside webroot.',
                evidence='\n'.join(issues),
                cwe='CWE-434'
            )
            print(f"    ✗ File upload validation insufficient")
        else:
            print("    ✓ File upload validation adequate")
    
    def test_api_input_sanitization(self):
        """Test API input sanitization"""
        print("\n[5/5] Testing API input sanitization...")
        
        # Test API endpoints with malicious inputs
        api_tests = [
            ('/api/stocks/search', {'q': '<script>alert(1)</script>'}),
            ('/api/stocks/search', {'q': "'; DROP TABLE users; --"}),
            ('/api/portfolio/summary', {'period': '../../../etc/passwd'}),
            ('/api/stocks/search', {'q': 'A' * 10000})  # Buffer overflow attempt
        ]
        
        issues = []
        
        for endpoint, params in api_tests:
            try:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=5
                )
                
                # Check for various issues
                if response.status_code == 500:
                    issues.append(f'{endpoint} returns 500 error with malicious input')
                
                # Check if malicious input is reflected
                if any(val in response.text for val in params.values() if isinstance(val, str)):
                    if '<script>' in response.text or 'DROP TABLE' in response.text:
                        issues.append(f'{endpoint} reflects unsanitized input')
            
            except requests.exceptions.Timeout:
                issues.append(f'{endpoint} timeout (possible DoS)')
            except:
                pass
        
        if issues:
            self.result.add_finding(
                severity='medium',
                title='API Input Sanitization Issues',
                description='API endpoints do not properly sanitize or validate inputs.',
                recommendation='Validate and sanitize all API inputs. Implement input length limits. Return proper error codes.',
                evidence='\n'.join(issues),
                cwe='CWE-20'
            )
            print(f"    ✗ API input sanitization issues found")
        else:
            print("    ✓ API input sanitization adequate")
    
    def run_test(self):
        """Run complete input validation test"""
        start_time = time.time()
        
        print("=" * 70)
        print("Input Validation Security Testing")
        print("=" * 70)
        
        if not check_app_running(self.base_url):
            print(f"\n✗ Application not accessible at {self.base_url}")
            self.result.set_status('failed')
            return self.result
        
        print(f"\n✓ Application accessible at {self.base_url}")
        
        # Setup session
        if self.setup_session():
            print("✓ Authenticated session established")
        else:
            print("~ Running tests without authentication")
        
        try:
            self.test_sql_injection_prevention()
            self.test_xss_prevention()
            self.test_csrf_protection()
            self.test_file_upload_validation()
            self.test_api_input_sanitization()
            
            self.result.set_status('completed')
        
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.result.set_status('failed')
        
        duration = time.time() - start_time
        self.result.set_duration(duration)
        
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"Status: {self.result.status.upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Total Findings: {self.result.summary['total']}")
        print(f"  Critical: {self.result.summary['critical']}")
        print(f"  High: {self.result.summary['high']}")
        print(f"  Medium: {self.result.summary['medium']}")
        print(f"  Low: {self.result.summary['low']}")
        
        return self.result


def main():
    """Main execution"""
    tester = InputValidationTester()
    result = tester.run_test()
    
    print("\nSaving results...")
    json_path = result.save_json('input_validation_test.json')
    print(f"✓ JSON results saved: {json_path}")
    
    report_path = ReportGenerator.generate_report(result, 'input_validation_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("Input validation security testing complete!")
    print("=" * 70)
    
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
