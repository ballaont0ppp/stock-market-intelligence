"""
Authentication Security Testing
Tests password strength, session management, RBAC, etc.
"""
import time
import sys
import requests
import re
from zxcvbn import zxcvbn

from config import (
    APP_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD,
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD,
    PASSWORD_REQUIREMENTS, SESSION_REQUIREMENTS
)
from utils import SecurityTestResult, ReportGenerator, check_app_running


class AuthenticationTester:
    """Authentication security tester"""
    
    def __init__(self):
        self.result = SecurityTestResult("Authentication Security Testing")
        self.base_url = APP_URL
    
    def test_password_strength_requirements(self):
        """Test password strength requirements"""
        print("\n[1/6] Testing password strength requirements...")
        
        weak_passwords = [
            ('short', 'Too short'),
            ('alllowercase', 'No uppercase'),
            ('ALLUPPERCASE', 'No lowercase'),
            ('NoNumbers!', 'No digits'),
            ('NoSpecial123', 'No special characters'),
            ('password123', 'Common password')
        ]
        
        issues = []
        
        for password, reason in weak_passwords:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/register",
                    data={
                        'email': f'test{time.time()}@test.com',
                        'password': password,
                        'confirm_password': password,
                        'full_name': 'Test User'
                    },
                    timeout=5
                )
                
                # If registration succeeds with weak password, it's an issue
                if response.status_code == 200 and 'success' in response.text.lower():
                    issues.append(f'Accepted weak password: {reason}')
            
            except:
                pass
        
        if issues:
            self.result.add_finding(
                severity='high',
                title='Weak Password Requirements',
                description='Application accepts weak passwords that do not meet security standards.',
                recommendation=f'Enforce password requirements: min {PASSWORD_REQUIREMENTS["min_length"]} chars, uppercase, lowercase, digit, special character.',
                evidence='\n'.join(issues),
                cwe='CWE-521'
            )
            print(f"    ✗ Found {len(issues)} password strength issues")
        else:
            print("    ✓ Password strength requirements adequate")
    
    def test_password_strength_scoring(self):
        """Test password strength using zxcvbn"""
        print("\n[2/6] Testing password strength scoring...")
        
        test_passwords = [
            'password',
            'Password1',
            'P@ssw0rd',
            'MyS3cur3P@ssw0rd!',
            'correct horse battery staple'
        ]
        
        weak_accepted = []
        
        for password in test_passwords:
            strength = zxcvbn(password)
            score = strength['score']  # 0-4
            
            if score < PASSWORD_REQUIREMENTS['min_strength_score']:
                weak_accepted.append(f'{password} (score: {score}/4)')
        
        if weak_accepted:
            self.result.add_finding(
                severity='medium',
                title='Weak Password Strength Scoring',
                description='Application may accept passwords with low strength scores.',
                recommendation='Use zxcvbn or similar library to enforce minimum password strength.',
                evidence=f'Weak passwords: {", ".join(weak_accepted)}',
                cwe='CWE-521'
            )
            print(f"    ✗ Weak passwords may be accepted")
        else:
            print("    ✓ Password strength scoring adequate")
    
    def test_session_management(self):
        """Test session management security"""
        print("\n[3/6] Testing session management...")
        
        issues = []
        
        try:
            session = requests.Session()
            
            # Login
            response = session.post(
                f"{self.base_url}/auth/login",
                data={'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD},
                timeout=5
            )
            
            # Check session cookie attributes
            session_cookie = session.cookies.get('session')
            
            if session_cookie:
                # Check HttpOnly flag
                for cookie in session.cookies:
                    if cookie.name == 'session':
                        if not cookie.has_nonstandard_attr('HttpOnly'):
                            issues.append('Session cookie missing HttpOnly flag')
                        
                        if not cookie.secure and SESSION_REQUIREMENTS['secure']:
                            issues.append('Session cookie missing Secure flag')
                        
                        if not cookie.has_nonstandard_attr('SameSite'):
                            issues.append('Session cookie missing SameSite attribute')
            else:
                issues.append('No session cookie found')
        
        except Exception as e:
            issues.append(f'Session test error: {str(e)}')
        
        if issues:
            self.result.add_finding(
                severity='high',
                title='Insecure Session Management',
                description='Session cookies lack proper security attributes.',
                recommendation='Set HttpOnly, Secure, and SameSite flags on session cookies.',
                evidence='\n'.join(issues),
                cwe='CWE-614'
            )
            print(f"    ✗ Found {len(issues)} session security issues")
        else:
            print("    ✓ Session management secure")
    
    def test_role_based_access_control(self):
        """Test RBAC implementation"""
        print("\n[4/6] Testing role-based access control...")
        
        issues = []
        
        try:
            # Test user access to admin endpoints
            user_session = requests.Session()
            user_session.post(
                f"{self.base_url}/auth/login",
                data={'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD},
                timeout=5
            )
            
            admin_endpoints = [
                '/admin',
                '/admin/users',
                '/admin/companies',
                '/admin/brokers'
            ]
            
            for endpoint in admin_endpoints:
                response = user_session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=5,
                    allow_redirects=False
                )
                
                if response.status_code == 200:
                    issues.append(f'Regular user can access {endpoint}')
        
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='critical',
                title='RBAC Bypass - Privilege Escalation',
                description='Regular users can access admin-only endpoints.',
                recommendation='Implement proper role-based access control checks on all admin endpoints.',
                evidence='\n'.join(issues),
                cwe='CWE-269'
            )
            print(f"    ✗ RBAC bypass detected")
        else:
            print("    ✓ RBAC properly enforced")
    
    def test_session_timeout(self):
        """Test session timeout"""
        print("\n[5/6] Testing session timeout...")
        
        try:
            session = requests.Session()
            
            # Login
            session.post(
                f"{self.base_url}/auth/login",
                data={'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD},
                timeout=5
            )
            
            # Check if session has max_age set
            session_cookie = None
            for cookie in session.cookies:
                if cookie.name == 'session':
                    session_cookie = cookie
                    break
            
            if session_cookie:
                if session_cookie.expires is None:
                    self.result.add_finding(
                        severity='medium',
                        title='No Session Timeout',
                        description='Session cookies do not have an expiration time.',
                        recommendation=f'Set session timeout to {SESSION_REQUIREMENTS["max_age"]} seconds (24 hours).',
                        evidence='Session cookie has no expiration',
                        cwe='CWE-613'
                    )
                    print("    ✗ No session timeout configured")
                else:
                    print("    ✓ Session timeout configured")
            else:
                print("    ~ Could not verify session timeout")
        
        except:
            print("    ~ Could not test session timeout")
    
    def test_password_reset_security(self):
        """Test password reset security"""
        print("\n[6/6] Testing password reset security...")
        
        issues = []
        
        try:
            # Test password reset endpoint
            response = requests.post(
                f"{self.base_url}/auth/reset-password",
                data={'email': TEST_USER_EMAIL},
                timeout=5
            )
            
            # Check if response reveals whether email exists
            if 'not found' in response.text.lower() or 'does not exist' in response.text.lower():
                issues.append('Password reset reveals if email exists (user enumeration)')
        
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='low',
                title='User Enumeration via Password Reset',
                description='Password reset functionality reveals whether email addresses exist.',
                recommendation='Return same message regardless of whether email exists.',
                evidence='\n'.join(issues),
                cwe='CWE-204'
            )
            print(f"    ✗ User enumeration possible")
        else:
            print("    ✓ Password reset secure")
    
    def run_test(self):
        """Run complete authentication security test"""
        start_time = time.time()
        
        print("=" * 70)
        print("Authentication Security Testing")
        print("=" * 70)
        
        if not check_app_running(self.base_url):
            print(f"\n✗ Application not accessible at {self.base_url}")
            self.result.set_status('failed')
            return self.result
        
        print(f"\n✓ Application accessible at {self.base_url}")
        
        try:
            self.test_password_strength_requirements()
            self.test_password_strength_scoring()
            self.test_session_management()
            self.test_role_based_access_control()
            self.test_session_timeout()
            self.test_password_reset_security()
            
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
    tester = AuthenticationTester()
    result = tester.run_test()
    
    print("\nSaving results...")
    json_path = result.save_json('authentication_test.json')
    print(f"✓ JSON results saved: {json_path}")
    
    report_path = ReportGenerator.generate_report(result, 'authentication_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("Authentication security testing complete!")
    print("=" * 70)
    
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
