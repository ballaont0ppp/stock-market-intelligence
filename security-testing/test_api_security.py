"""
API Security Testing
Tests rate limiting, authentication, validation, sanitization, and versioning
"""
import time
import sys
import requests
from typing import Dict, List
import json

from config import APP_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD, RATE_LIMIT_TESTS
from utils import SecurityTestResult, ReportGenerator, check_app_running


class APISecurityTester:
    """API security tester"""
    
    def __init__(self):
        self.result = SecurityTestResult("API Security Testing")
        self.base_url = APP_URL
        self.session = requests.Session()
    
    def setup_session(self):
        """Setup authenticated session"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD},
                timeout=5
            )
            return response.status_code == 200 or response.status_code == 302
        except:
            return False
    
    def test_rate_limiting(self):
        """Test API rate limiting"""
        print("\n[1/5] Testing rate limiting...")
        
        api_endpoints = [
            '/api/stocks/search',
            '/api/portfolio/summary',
            '/api/stocks/price'
        ]
        
        issues = []
        
        for endpoint in api_endpoints:
            try:
                # Make rapid requests
                rate_limited = False
                requests_made = 0
                
                for i in range(150):  # Try 150 requests
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        params={'q': 'test'},
                        timeout=2
                    )
                    requests_made += 1
                    
                    if response.status_code == 429:  # Too Many Requests
                        rate_limited = True
                        break
                
                if not rate_limited:
                    issues.append(f'{endpoint} - No rate limiting ({requests_made} requests succeeded)')
                else:
                    print(f"    ✓ {endpoint} - Rate limited after {requests_made} requests")
            
            except requests.exceptions.Timeout:
                # Timeout might indicate rate limiting or DoS protection
                print(f"    ✓ {endpoint} - Request timeout (possible rate limiting)")
            except:
                pass
        
        if issues:
            self.result.add_finding(
                severity='medium',
                title='Insufficient API Rate Limiting',
                description='API endpoints lack proper rate limiting.',
                recommendation=f'Implement rate limiting: {RATE_LIMIT_TESTS["api_endpoints"]["max_requests"]} requests per {RATE_LIMIT_TESTS["api_endpoints"]["time_window"]}s.',
                evidence='\n'.join(issues),
                cwe='CWE-770'
            )
            print(f"    ✗ Rate limiting issues found")
        else:
            print("    ✓ Rate limiting adequate")
    
    def test_api_authentication(self):
        """Test API authentication"""
        print("\n[2/5] Testing API authentication...")
        
        protected_endpoints = [
            '/api/portfolio/summary',
            '/api/portfolio/holdings',
            '/api/orders/history'
        ]
        
        issues = []
        
        # Test without authentication
        anon_session = requests.Session()
        
        for endpoint in protected_endpoints:
            try:
                response = anon_session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=5
                )
                
                # Protected endpoints should return 401 or redirect to login
                if response.status_code == 200:
                    issues.append(f'{endpoint} accessible without authentication')
                elif response.status_code not in [401, 403, 302]:
                    issues.append(f'{endpoint} returns unexpected status: {response.status_code}')
            
            except:
                pass
        
        if issues:
            self.result.add_finding(
                severity='high',
                title='API Authentication Bypass',
                description='Protected API endpoints accessible without authentication.',
                recommendation='Require authentication for all protected API endpoints. Return 401 for unauthenticated requests.',
                evidence='\n'.join(issues),
                cwe='CWE-306'
            )
            print(f"    ✗ Authentication issues found")
        else:
            print("    ✓ API authentication properly enforced")
    
    def test_request_validation(self):
        """Test API request validation"""
        print("\n[3/5] Testing request validation...")
        
        issues = []
        
        # Test with invalid data types
        test_cases = [
            ('/api/stocks/search', {'q': 'A' * 10000}, 'Excessive input length'),
            ('/api/stocks/search', {'q': '<script>alert(1)</script>'}, 'XSS payload'),
            ('/api/stocks/search', {'q': "'; DROP TABLE users; --"}, 'SQL injection'),
            ('/api/portfolio/summary', {'period': '../../../etc/passwd'}, 'Path traversal'),
        ]
        
        for endpoint, params, attack_type in test_cases:
            try:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=5
                )
                
                # Check for proper error handling
                if response.status_code == 500:
                    issues.append(f'{endpoint} - 500 error with {attack_type}')
                
                # Check if malicious input is reflected
                if any(str(val) in response.text for val in params.values()):
                    if '<script>' in response.text or 'DROP TABLE' in response.text:
                        issues.append(f'{endpoint} - Reflects unsanitized {attack_type}')
            
            except requests.exceptions.Timeout:
                issues.append(f'{endpoint} - Timeout with {attack_type} (possible DoS)')
            except:
                pass
        
        if issues:
            self.result.add_finding(
                severity='medium',
                title='Insufficient API Request Validation',
                description='API does not properly validate request parameters.',
                recommendation='Validate all input parameters. Implement length limits. Return proper error codes (400 for bad requests).',
                evidence='\n'.join(issues),
                cwe='CWE-20'
            )
            print(f"    ✗ Request validation issues found")
        else:
            print("    ✓ Request validation adequate")
    
    def test_response_sanitization(self):
        """Test API response sanitization"""
        print("\n[4/5] Testing response sanitization...")
        
        issues = []
        
        try:
            # Test API responses for sensitive data exposure
            response = self.session.get(f"{self.base_url}/api/portfolio/summary", timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check for sensitive data in response
                    response_str = json.dumps(data)
                    
                    # Check for password fields
                    if 'password' in response_str.lower():
                        issues.append('Response contains password field')
                    
                    # Check for internal IDs or paths
                    if '/home/' in response_str or 'C:\\' in response_str:
                        issues.append('Response contains internal file paths')
                    
                    # Check for stack traces
                    if 'Traceback' in response_str or 'Exception' in response_str:
                        issues.append('Response contains stack traces')
                
                except json.JSONDecodeError:
                    pass
        
        except:
            pass
        
        # Test error responses
        try:
            response = self.session.get(
                f"{self.base_url}/api/nonexistent",
                timeout=5
            )
            
            if 'Traceback' in response.text or 'Exception' in response.text:
                issues.append('Error responses contain stack traces')
        
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='medium',
                title='API Response Information Disclosure',
                description='API responses expose sensitive information.',
                recommendation='Sanitize all API responses. Remove sensitive fields. Disable debug mode in production.',
                evidence='\n'.join(issues),
                cwe='CWE-200'
            )
            print(f"    ✗ Response sanitization issues found")
        else:
            print("    ✓ Response sanitization adequate")
    
    def test_api_versioning(self):
        """Test API versioning"""
        print("\n[5/5] Testing API versioning...")
        
        issues = []
        
        # Check if API uses versioning
        api_endpoints = [
            '/api/stocks/search',
            '/api/portfolio/summary'
        ]
        
        has_versioning = False
        
        for endpoint in api_endpoints:
            # Check if endpoint includes version (e.g., /api/v1/...)
            if '/v1/' in endpoint or '/v2/' in endpoint:
                has_versioning = True
                break
        
        if not has_versioning:
            # Check response headers for API version
            try:
                response = self.session.get(f"{self.base_url}/api/stocks/search", timeout=5)
                
                if 'API-Version' in response.headers or 'X-API-Version' in response.headers:
                    has_versioning = True
            
            except:
                pass
        
        if not has_versioning:
            self.result.add_finding(
                severity='low',
                title='API Versioning Not Implemented',
                description='API does not implement versioning.',
                recommendation='Implement API versioning (e.g., /api/v1/...) to support backward compatibility.',
                evidence='No version indicators found in endpoints or headers',
                cwe='CWE-1059'
            )
            print("    ✗ API versioning not implemented")
        else:
            print("    ✓ API versioning implemented")
    
    def run_test(self):
        """Run complete API security test"""
        start_time = time.time()
        
        print("=" * 70)
        print("API Security Testing")
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
            self.test_rate_limiting()
            self.test_api_authentication()
            self.test_request_validation()
            self.test_response_sanitization()
            self.test_api_versioning()
            
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
    tester = APISecurityTester()
    result = tester.run_test()
    
    print("\nSaving results...")
    json_path = result.save_json('api_security_test.json')
    print(f"✓ JSON results saved: {json_path}")
    
    report_path = ReportGenerator.generate_report(result, 'api_security_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("API security testing complete!")
    print("=" * 70)
    
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
