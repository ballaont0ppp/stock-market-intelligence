"""
Compliance Testing
Tests GDPR, PCI-DSS, and SOC 2 compliance requirements
"""
import time
import sys
import requests
from typing import Dict, List

from config import APP_URL, COMPLIANCE_CHECKS, SECURITY_HEADERS
from utils import SecurityTestResult, ReportGenerator, check_app_running


class ComplianceTester:
    """Compliance tester"""
    
    def __init__(self):
        self.result = SecurityTestResult("Compliance Testing")
        self.base_url = APP_URL
        self.session = requests.Session()
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance"""
        print("\n[1/3] Testing GDPR compliance...")
        
        if not COMPLIANCE_CHECKS['gdpr']:
            print("    ~ GDPR compliance testing disabled")
            return
        
        issues = []
        
        # Check for privacy policy
        try:
            response = self.session.get(f"{self.base_url}/privacy", timeout=5)
            if response.status_code != 200:
                issues.append('No privacy policy page found')
        except:
            issues.append('Privacy policy page not accessible')
        
        # Check for cookie consent
        try:
            response = self.session.get(self.base_url, timeout=5)
            if 'cookie' not in response.text.lower() and 'consent' not in response.text.lower():
                issues.append('No cookie consent mechanism found')
        except:
            pass
        
        # Check for data export capability
        try:
            response = self.session.get(f"{self.base_url}/auth/profile", timeout=5)
            if 'export' not in response.text.lower() and 'download' not in response.text.lower():
                issues.append('No data export functionality found (GDPR Right to Data Portability)')
        except:
            pass
        
        # Check for account deletion
        try:
            response = self.session.get(f"{self.base_url}/auth/profile", timeout=5)
            if 'delete account' not in response.text.lower() and 'close account' not in response.text.lower():
                issues.append('No account deletion functionality found (GDPR Right to Erasure)')
        except:
            pass
        
        # Check for data processing consent
        try:
            response = self.session.get(f"{self.base_url}/auth/register", timeout=5)
            if 'terms' not in response.text.lower() and 'privacy' not in response.text.lower():
                issues.append('No consent checkbox for data processing during registration')
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='high',
                title='GDPR Compliance Issues',
                description='Application does not meet GDPR requirements.',
                recommendation='Implement: Privacy policy, cookie consent, data export, account deletion, and explicit consent mechanisms.',
                evidence='\n'.join(issues),
                cwe='N/A'
            )
            print(f"    ✗ Found {len(issues)} GDPR compliance issues")
        else:
            print("    ✓ GDPR compliance requirements met")
    
    def test_pci_dss_compliance(self):
        """Test PCI-DSS compliance"""
        print("\n[2/3] Testing PCI-DSS compliance...")
        
        if not COMPLIANCE_CHECKS['pci_dss']:
            print("    ~ PCI-DSS compliance testing disabled (not handling payment cards)")
            return
        
        issues = []
        
        # Check for HTTPS
        if self.base_url.startswith('http://'):
            issues.append('Not using HTTPS (PCI-DSS Requirement 4)')
        
        # Check for secure payment processing
        try:
            response = self.session.get(f"{self.base_url}/payment", timeout=5)
            if response.status_code == 200:
                # Check if credit card fields are present
                if 'card' in response.text.lower() or 'credit' in response.text.lower():
                    # Should use tokenization or third-party processor
                    if 'stripe' not in response.text.lower() and 'paypal' not in response.text.lower():
                        issues.append('Direct credit card handling detected (should use payment processor)')
        except:
            pass
        
        # Check for security headers
        try:
            response = self.session.get(self.base_url, timeout=5)
            
            if 'X-Frame-Options' not in response.headers:
                issues.append('Missing X-Frame-Options header (PCI-DSS Requirement 6.5.10)')
            
            if 'Content-Security-Policy' not in response.headers:
                issues.append('Missing Content-Security-Policy header')
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='critical',
                title='PCI-DSS Compliance Issues',
                description='Application does not meet PCI-DSS requirements for payment card handling.',
                recommendation='Use HTTPS, implement security headers, use payment processor (Stripe/PayPal), never store card data.',
                evidence='\n'.join(issues),
                cwe='N/A'
            )
            print(f"    ✗ Found {len(issues)} PCI-DSS compliance issues")
        else:
            print("    ✓ PCI-DSS compliance requirements met")
    
    def test_soc2_compliance(self):
        """Test SOC 2 compliance preparation"""
        print("\n[3/3] Testing SOC 2 compliance preparation...")
        
        if not COMPLIANCE_CHECKS['soc2']:
            print("    ~ SOC 2 compliance testing disabled")
            return
        
        issues = []
        
        # Security - Check security headers
        try:
            response = self.session.get(self.base_url, timeout=5)
            
            for header, expected_value in SECURITY_HEADERS.items():
                if header not in response.headers:
                    issues.append(f'Missing security header: {header}')
                elif expected_value and expected_value not in response.headers[header]:
                    issues.append(f'Incorrect {header}: {response.headers[header]}')
        except:
            pass
        
        # Availability - Check for health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                issues.append('No health check endpoint found (SOC 2 Availability)')
        except:
            issues.append('Health check endpoint not accessible')
        
        # Confidentiality - Check for HTTPS
        if self.base_url.startswith('http://'):
            issues.append('Not using HTTPS (SOC 2 Confidentiality)')
        
        # Processing Integrity - Check for audit logging
        try:
            # This would require checking if audit logs are implemented
            # For now, we'll check if there's an admin audit log page
            response = self.session.get(f"{self.base_url}/admin/audit-logs", timeout=5)
            if response.status_code == 404:
                issues.append('No audit logging system found (SOC 2 Processing Integrity)')
        except:
            pass
        
        # Privacy - Check for privacy policy
        try:
            response = self.session.get(f"{self.base_url}/privacy", timeout=5)
            if response.status_code != 200:
                issues.append('No privacy policy found (SOC 2 Privacy)')
        except:
            pass
        
        if issues:
            self.result.add_finding(
                severity='medium',
                title='SOC 2 Compliance Preparation Issues',
                description='Application does not meet all SOC 2 Trust Service Criteria.',
                recommendation='Implement: Security headers, health checks, HTTPS, audit logging, and privacy policy.',
                evidence='\n'.join(issues),
                cwe='N/A'
            )
            print(f"    ✗ Found {len(issues)} SOC 2 preparation issues")
        else:
            print("    ✓ SOC 2 compliance preparation adequate")
    
    def generate_compliance_documentation(self):
        """Generate compliance documentation"""
        print("\nGenerating compliance documentation...")
        
        doc = {
            'gdpr': {
                'status': 'Tested',
                'requirements': [
                    'Privacy Policy',
                    'Cookie Consent',
                    'Data Export (Right to Data Portability)',
                    'Account Deletion (Right to Erasure)',
                    'Data Processing Consent'
                ]
            },
            'pci_dss': {
                'status': 'Not Applicable' if not COMPLIANCE_CHECKS['pci_dss'] else 'Tested',
                'requirements': [
                    'HTTPS Encryption',
                    'Security Headers',
                    'Payment Processor Integration',
                    'No Card Data Storage'
                ]
            },
            'soc2': {
                'status': 'Tested',
                'trust_criteria': [
                    'Security (Security Headers)',
                    'Availability (Health Checks)',
                    'Confidentiality (HTTPS)',
                    'Processing Integrity (Audit Logs)',
                    'Privacy (Privacy Policy)'
                ]
            }
        }
        
        self.result.add_finding(
            severity='info',
            title='Compliance Testing Summary',
            description='Compliance testing completed for GDPR, PCI-DSS, and SOC 2.',
            recommendation='Review findings and implement missing compliance requirements.',
            evidence=f'GDPR: {doc["gdpr"]["status"]}\nPCI-DSS: {doc["pci_dss"]["status"]}\nSOC 2: {doc["soc2"]["status"]}',
            cwe='N/A'
        )
        
        print("    ✓ Compliance documentation generated")
    
    def run_test(self):
        """Run complete compliance test"""
        start_time = time.time()
        
        print("=" * 70)
        print("Compliance Testing")
        print("=" * 70)
        
        if not check_app_running(self.base_url):
            print(f"\n✗ Application not accessible at {self.base_url}")
            self.result.set_status('failed')
            return self.result
        
        print(f"\n✓ Application accessible at {self.base_url}")
        
        try:
            self.test_gdpr_compliance()
            self.test_pci_dss_compliance()
            self.test_soc2_compliance()
            self.generate_compliance_documentation()
            
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
        print(f"  Info: {self.result.summary['info']}")
        
        return self.result


def main():
    """Main execution"""
    tester = ComplianceTester()
    result = tester.run_test()
    
    print("\nSaving results...")
    json_path = result.save_json('compliance_test.json')
    print(f"✓ JSON results saved: {json_path}")
    
    report_path = ReportGenerator.generate_report(result, 'compliance_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("Compliance testing complete!")
    print("=" * 70)
    
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
