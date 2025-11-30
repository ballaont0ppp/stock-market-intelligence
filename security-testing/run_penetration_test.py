"""
Penetration Testing Suite
Black-box, white-box, and gray-box testing
"""
import time
import sys
from typing import Dict, List
from urllib.parse import urljoin
import requests

from config import (
    APP_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD,
    SQL_INJECTION_PAYLOADS, XSS_PAYLOADS
)
from utils import ReportGenerator, SecurityTestResult, check_app_running


class PenetrationTester:
    """Automated penetration testing"""
    
    def __init__(self):
        self.result = SecurityTestResult("Penetration Testing")
        self.base_url = APP_URL
        self.session = requests.Session()
    
    def test_black_box_testing(self):
        """Black-box testing - no prior knowledge"""
        print("\n[1/3] Black-box Testing (External Attacker Perspective)")
        print("-" * 70)
        
        # Test 1: Directory enumeration
        self.test_directory_enumeration()
        
        # Test 2: Information disclosure
        self.test_information_disclosure()
        
        # Test 3: Brute force protection
        self.test_brute_force_protection()
        
        # Test 4: Session fixation
        self.test_session_fixation()
    
    def test_white_box_testing(self):
        """White-box testing - full system knowledge"""
        print("\n[2/3] White-box Testing (Full System Knowledge)")
        print("-" * 70)
        
        # Test 1: SQL injection
        self.test_sql_injection()
        
        # Test 2: XSS vulnerabilities
        self.test_xss_vulnerabilities()
        
        # Test 3: CSRF protection
        self.test_csrf_protection()
        
        # Test 4: Authentication bypass
        self.test_authentication_bypass()
    
    def test_gray_box_testing(self):
        """Gray-box testing - Limited knowledge"""
        print("\n[3/3] Gray-box Testing (Limited Knowledge)")
        print("-" * 70)
        
        # Test 1: API security
        self.test_api_security()
        
        # Test 2: File upload vulnerabilities
        self.test_file_upload()
        
        # Test 3: Business logic flaws
        self.test_business_logic()
    
    def test_directory_enumeration(self):
        """Test for directory enumeration vulnerabilities"""
        print("  Testing directory enumeration...")
        
        common_paths = [
            '/.git',
            '/.env',
            '/admin',
            '/backup',
            '/config',
            '/database',
            '/phpinfo.php',
            '/server-status',
            '/.htaccess'
        ]
        
        exposed_paths = []
        
        for path in common_paths:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    exposed_paths.append(path)
            except:
                pass
        
        if exposed_paths:
            print(f"    ✗ Found {len(exposed_paths)} exposed paths")
            self.result.add_finding(
                severity='high',
                title='Directory Enumeration - Sensitive Paths Exposed',
                description=f'The following sensitive paths are accessible: {", ".join(exposed_paths)}',
                recommendation='Remove access to sensitive directories and files. Use proper access controls.',
                evidence=f'Exposed paths: {exposed_paths}',
                cwe='CWE-548'
            )
        else:
            print("    ✓ No sensitive paths exposed")
    
    def test_information_disclosure(self):
        """Test for information disclosure"""
        print("  Testing information disclosure...")
        
        issues = []
        
        # Check for verbose error messages
        try:
            response = self.session.get(f"{self.base_url}/nonexistent", timeout=5)
            
            if 'Traceback' in response.text or 'Exception' in response.text:
                issues.append('Verbose error messages expose stack traces')
        except:
            pass
        
        # Check for server version disclosure
        try:
            response = self.session.get(self.base_url, timeout=5)
            
            if 'Server' in response.headers:
                server = response.headers['Server']
                if any(version in server for version in ['/', '.']):
                    issues.append(f'Server version disclosed: {server}')
            
            # Check for X-Powered-By header
            if 'X-Powered-By' in response.headers:
                issues.append(f'Technology stack disclosed: {response.headers["X-Powered-By"]}')
        except:
            pass
        
        if issues:
            print(f"    ✗ Found {len(issues)} information disclosure issues")
            self.result.add_finding(
                severity='medium',
                title='Information Disclosure',
                description='Application discloses sensitive information that could aid attackers.',
                recommendation='Disable verbose error messages in production. Remove version headers.',
                evidence='\n'.join(issues),
                cwe='CWE-200'
            )
        else:
            print("    ✓ No information disclosure detected")
    
    def test_brute_force_protection(self):
        """Test for brute force protection"""
        print("  Testing brute force protection...")
        
        login_url = f"{self.base_url}/auth/login"
        
        # Attempt multiple failed logins
        failed_attempts = 0
        for i in range(10):
            try:
                data = {
                    'email': 'test@test.com',
                    'password': f'wrong{i}'
                }
                response = self.session.post(login_url, data=data, timeout=5)
                
                if response.status_code != 429:  # Not rate limited
                    failed_attempts += 1
            except:
                break
        
        if failed_attempts >= 8:
            print(f"    ✗ Insufficient brute force protection ({failed_attempts} attempts)")
            self.result.add_finding(
                severity='high',
                title='Insufficient Brute Force Protection',
                description=f'Successfully made {failed_attempts} login attempts without rate limiting.',
                recommendation='Implement rate limiting on authentication endpoints. Add CAPTCHA after failed attempts.',
                evidence=f'Made {failed_attempts} attempts without being blocked',
                cwe='CWE-307'
            )
        else:
            print("    ✓ Brute force protection appears adequate")
    
    def test_session_fixation(self):
        """Test for session fixation vulnerabilities"""
        print("  Testing session fixation...")
        
        try:
            # Get initial session
            response1 = self.session.get(f"{self.base_url}/auth/login", timeout=5)
            cookie1 = self.session.cookies.get('session')
            
            # Login
            data = {
                'email': TEST_USER_EMAIL,
                'password': TEST_USER_PASSWORD
            }
            self.session.post(f"{self.base_url}/auth/login", data=data, timeout=5)
            
            # Check if session changed
            cookie2 = self.session.cookies.get('session')
            
            if cookie1 and cookie2 and cookie1 == cookie2:
                print("    ✗ Session fixation vulnerability detected")
                self.result.add_finding(
                    severity='high',
                    title='Session Fixation Vulnerability',
                    description='Session ID is not regenerated after authentication.',
                    recommendation='Regenerate session ID upon successful login.',
                    evidence='Session ID remained the same before and after login',
                    cwe='CWE-384'
                )
            else:
                print("    ✓ Session properly regenerated on login")
        except:
            print("    ~ Could not test session fixation")
    
    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        print("  Testing SQL injection...")
        
        vulnerable_endpoints = []
        
        # Test login endpoint
        for payload in SQL_INJECTION_PAYLOADS[:3]:
            try:
                data = {
                    'email': payload,
                    'password': 'test'
                }
                response = self.session.post(f"{self.base_url}/auth/login", data=data, timeout=5)
                
                # Check for SQL error messages
                if any(err in response.text.lower() for err in ['sql', 'mysql', 'syntax', 'query']):
                    vulnerable_endpoints.append(f'/auth/login (email parameter)')
                    break
            except:
                pass
        
        if vulnerable_endpoints:
            print(f"    ✗ Found SQL injection vulnerability")
            self.result.add_finding(
                severity='critical',
                title='SQL Injection Vulnerability',
                description='Application is vulnerable to SQL injection attacks.',
                recommendation='Use parameterized queries. Validate and sanitize all inputs.',
                evidence=f'Vulnerable endpoints: {", ".join(vulnerable_endpoints)}',
                cwe='CWE-89'
            )
        else:
            print("    ✓ No SQL injection vulnerabilities detected")
    
    def test_xss_vulnerabilities(self):
        """Test for XSS vulnerabilities"""
        print("  Testing XSS vulnerabilities...")
        
        test_endpoints = [
            '/portfolio',
            '/orders',
            '/dashboard'
        ]
        
        vulnerable_endpoints = []
        
        for endpoint in test_endpoints:
            for payload in XSS_PAYLOADS[:2]:
                try:
                    params = {'search': payload}
                    response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=5)
                    
                    # Check if payload is reflected unescaped
                    if payload in response.text:
                        vulnerable_endpoints.append(endpoint)
                        break
                except:
                    pass
        
        if vulnerable_endpoints:
            print(f"    ✗ Found XSS vulnerability")
            self.result.add_finding(
                severity='high',
                title='Cross-Site Scripting (XSS) Vulnerability',
                description='Application does not properly sanitize user input.',
                recommendation='Enable auto-escaping in templates. Sanitize all user inputs.',
                evidence=f'Vulnerable endpoints: {", ".join(vulnerable_endpoints)}',
                cwe='CWE-79'
            )
        else:
            print("    ✓ No XSS vulnerabilities detected")
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        print("  Testing CSRF protection...")
        
        try:
            # Attempt POST without CSRF token
            data = {
                'amount': '100'
            }
            response = self.session.post(f"{self.base_url}/portfolio/wallet/deposit", data=data, timeout=5)
            
            if response.status_code == 200:
                print("    ✗ CSRF protection missing")
                self.result.add_finding(
                    severity='high',
                    title='Missing CSRF Protection',
                    description='State-changing operations lack CSRF protection.',
                    recommendation='Implement CSRF tokens on all forms. Use Flask-WTF CSRF protection.',
                    evidence='POST request succeeded without CSRF token',
                    cwe='CWE-352'
                )
            else:
                print("    ✓ CSRF protection appears active")
        except:
            print("    ~ Could not test CSRF protection")
    
    def test_authentication_bypass(self):
        """Test for authentication bypass"""
        print("  Testing authentication bypass...")
        
        protected_endpoints = [
            '/portfolio',
            '/orders',
            '/admin'
        ]
        
        bypassed = []
        
        # Test without authentication
        anon_session = requests.Session()
        for endpoint in protected_endpoints:
            try:
                response = anon_session.get(f"{self.base_url}{endpoint}", timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    bypassed.append(endpoint)
            except:
                pass
        
        if bypassed:
            print(f"    ✗ Authentication bypass found")
            self.result.add_finding(
                severity='critical',
                title='Authentication Bypass',
                description='Protected endpoints accessible without authentication.',
                recommendation='Ensure all protected routes require authentication.',
                evidence=f'Accessible without auth: {", ".join(bypassed)}',
                cwe='CWE-287'
            )
        else:
            print("    ✓ Authentication properly enforced")
    
    def test_api_security(self):
        """Test API security"""
        print("  Testing API security...")
        
        api_endpoints = [
            '/api/stocks/search',
            '/api/portfolio/summary'
        ]
        
        issues = []
        
        # Test rate limiting
        for endpoint in api_endpoints:
            try:
                for i in range(150):
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=1)
                    if response.status_code == 429:
                        break
                else:
                    issues.append(f'{endpoint} lacks rate limiting')
            except:
                pass
        
        # Test without authentication
        try:
            for endpoint in api_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    issues.append(f'{endpoint} accessible without auth')
        except:
            pass
        
        if issues:
            print(f"    ✗ Found {len(issues)} API security issues")
            self.result.add_finding(
                severity='medium',
                title='API Security Issues',
                description='API endpoints have security weaknesses.',
                recommendation='Implement authentication and rate limiting on all API endpoints.',
                evidence='\n'.join(issues),
                cwe='CWE-306'
            )
        else:
            print("    ✓ API security appears adequate")
    
    def test_file_upload(self):
        """Test file upload vulnerabilities"""
        print("  Testing file upload security...")
        
        # This is a placeholder - actual implementation would test file upload endpoints
        # Note: File upload testing requires manual verification
        print("    ~ File upload testing requires manual verification")
    
    def test_business_logic(self):
        """Test business logic flaws"""
        print("  Testing business logic...")
        
        try:
            # Test negative amounts
            data = {
                'amount': '-1000'
            }
            response = self.session.post(f"{self.base_url}/portfolio/wallet/deposit", data=data, timeout=5)
            
            if 'success' in response.text.lower():
                print("    ✗ Business logic flaw detected")
                self.result.add_finding(
                    severity='critical',
                    title='Business Logic Flaw - Negative Amounts',
                    description='Application accepts negative amounts on accounts.',
                    recommendation='Implement proper input validation for all numeric fields.',
                    evidence='Negative amount deposit accepted',
                    cwe='CWE-840'
                )
            else:
                print("    ✓ Business logic validation appears adequate")
        except:
            print("    ~ Could not test business logic")
    
    def run_test(self):
        """Main execution"""
        print("\n" + "=" * 70)
        print("Penetration Testing Suite")
        print("=" * 70)
        
        # Check if app is running
        if not check_app_running(self.base_url):
            print(f"\n✗ Application not accessible at {self.base_url}")
            print("Please ensure the application is running before testing")
            self.result.set_status('failed')
            return self.result
        
        print(f"\n✓ Application accessible at {self.base_url}")
        
        try:
            # Run test suites
            self.test_black_box_testing()
            self.test_white_box_testing()
            self.test_gray_box_testing()
            
            self.result.set_status('completed')
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.result.set_status('failed')
        
        # Print summary
        start_time = time.time()
        duration = time.time() - start_time
        self.result.set_duration(duration)
        
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"  Status: {self.result.status.upper()}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Total Findings: {self.result.summary['total']}")
        print(f"  Critical: {self.result.summary['critical']}")
        print(f"  High: {self.result.summary['high']}")
        print(f"  Medium: {self.result.summary['medium']}")
        print(f"  Low: {self.result.summary['low']}")
        
        # Save results
        print("\nSaving results...")
        json_path = self.result.save_json('penetration_test')
        print(f"✓ JSON results saved: {json_path}")
        
        # Generate report
        report_path = ReportGenerator.generate_report(self.result, 'penetration_report.html')
        print(f"✓ HTML report saved: {report_path}")
        
        print("\n" + "=" * 70)
        print("Penetration testing complete!")
        print("=" * 70)
        
        # Exit with error code if critical/high findings
        if self.result.summary['critical'] > 0 or self.result.summary['high'] > 0:
            sys.exit(1)
        
        sys.exit(0)


if __name__ == '__main__':
    tester = PenetrationTester()
    tester.run_test()
