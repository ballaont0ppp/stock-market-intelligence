"""
Run All Security Tests
Executes all security test suites and generates consolidated report
"""
import time
import sys
from pathlib import Path
from datetime import datetime

from config import REPORTS_DIR, RESULTS_DIR
from utils import SecurityTestResult, ReportGenerator

# Import all test modules
from run_bandit_scan import BanditScanner
from run_dependency_check import DependencyChecker
from test_penetration import PenetrationTester
from test_authentication import AuthenticationTester
from test_input_validation import InputValidationTester
from test_data_protection import DataProtectionTester
from test_api_security import APISecurityTester
from test_compliance import ComplianceTester


class SecurityTestSuite:
    """Complete security test suite runner"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """Run all security tests"""
        self.start_time = time.time()
        
        print("=" * 70)
        print("COMPREHENSIVE SECURITY TESTING SUITE")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Test 1: Static Code Analysis (Bandit)
        print("\n\n" + "=" * 70)
        print("TEST 1/8: Static Code Analysis (Bandit)")
        print("=" * 70)
        try:
            scanner = BanditScanner()
            result = scanner.run_scan()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Bandit scan failed: {e}")
        
        # Test 2: Dependency Vulnerability Check
        print("\n\n" + "=" * 70)
        print("TEST 2/8: Dependency Vulnerability Check")
        print("=" * 70)
        try:
            checker = DependencyChecker()
            result = checker.run_scan()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Dependency check failed: {e}")
        
        # Test 3: Penetration Testing
        print("\n\n" + "=" * 70)
        print("TEST 3/8: Penetration Testing")
        print("=" * 70)
        try:
            tester = PenetrationTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Penetration test failed: {e}")
        
        # Test 4: Authentication Security
        print("\n\n" + "=" * 70)
        print("TEST 4/8: Authentication Security Testing")
        print("=" * 70)
        try:
            tester = AuthenticationTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Authentication test failed: {e}")
        
        # Test 5: Input Validation
        print("\n\n" + "=" * 70)
        print("TEST 5/8: Input Validation Security Testing")
        print("=" * 70)
        try:
            tester = InputValidationTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Input validation test failed: {e}")
        
        # Test 6: Data Protection
        print("\n\n" + "=" * 70)
        print("TEST 6/8: Data Protection Security Testing")
        print("=" * 70)
        try:
            tester = DataProtectionTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Data protection test failed: {e}")
        
        # Test 7: API Security
        print("\n\n" + "=" * 70)
        print("TEST 7/8: API Security Testing")
        print("=" * 70)
        try:
            tester = APISecurityTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ API security test failed: {e}")
        
        # Test 8: Compliance
        print("\n\n" + "=" * 70)
        print("TEST 8/8: Compliance Testing")
        print("=" * 70)
        try:
            tester = ComplianceTester()
            result = tester.run_test()
            self.results.append(result)
        except Exception as e:
            print(f"✗ Compliance test failed: {e}")
        
        self.end_time = time.time()
    
    def generate_consolidated_report(self):
        """Generate consolidated security report"""
        print("\n\n" + "=" * 70)
        print("GENERATING CONSOLIDATED REPORT")
        print("=" * 70)
        
        # Aggregate all findings
        consolidated = SecurityTestResult("Comprehensive Security Testing")
        
        for result in self.results:
            for finding in result.findings:
                consolidated.add_finding(
                    severity=finding['severity'],
                    title=f"[{result.test_name}] {finding['title']}",
                    description=finding['description'],
                    recommendation=finding['recommendation'],
                    evidence=finding['evidence'],
                    cwe=finding['cwe']
                )
        
        # Set metadata
        duration = self.end_time - self.start_time
        consolidated.set_duration(duration)
        consolidated.set_status('completed')
        
        # Save consolidated results
        json_path = consolidated.save_json('consolidated_security_results.json')
        print(f"✓ Consolidated JSON saved: {json_path}")
        
        # Generate HTML report
        report_path = ReportGenerator.generate_report(
            consolidated,
            'consolidated_security_report.html'
        )
        print(f"✓ Consolidated HTML report saved: {report_path}")
        
        return consolidated
    
    def print_summary(self, consolidated: SecurityTestResult):
        """Print final summary"""
        print("\n\n" + "=" * 70)
        print("SECURITY TESTING SUMMARY")
        print("=" * 70)
        
        duration = self.end_time - self.start_time
        print(f"Total Duration: {duration:.2f}s ({duration/60:.1f} minutes)")
        print(f"Tests Executed: {len(self.results)}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-" * 70)
        print("FINDINGS BY SEVERITY")
        print("-" * 70)
        print(f"  Critical: {consolidated.summary['critical']}")
        print(f"  High:     {consolidated.summary['high']}")
        print(f"  Medium:   {consolidated.summary['medium']}")
        print(f"  Low:      {consolidated.summary['low']}")
        print(f"  Info:     {consolidated.summary['info']}")
        print(f"  TOTAL:    {consolidated.summary['total']}")
        
        print("\n" + "-" * 70)
        print("FINDINGS BY TEST")
        print("-" * 70)
        for result in self.results:
            print(f"  {result.test_name}: {result.summary['total']} findings")
        
        print("\n" + "-" * 70)
        print("REPORTS GENERATED")
        print("-" * 70)
        print(f"  Location: {REPORTS_DIR}")
        print(f"  Consolidated Report: consolidated_security_report.html")
        print(f"  Individual Reports: {len(self.results)} files")
        
        # Risk assessment
        print("\n" + "-" * 70)
        print("RISK ASSESSMENT")
        print("-" * 70)
        
        if consolidated.summary['critical'] > 0:
            print("  ⚠ CRITICAL RISK: Immediate action required!")
            print(f"    {consolidated.summary['critical']} critical vulnerabilities found")
        elif consolidated.summary['high'] > 0:
            print("  ⚠ HIGH RISK: Address before production deployment")
            print(f"    {consolidated.summary['high']} high-severity vulnerabilities found")
        elif consolidated.summary['medium'] > 0:
            print("  ⚠ MEDIUM RISK: Address in near term")
            print(f"    {consolidated.summary['medium']} medium-severity vulnerabilities found")
        elif consolidated.summary['low'] > 0:
            print("  ✓ LOW RISK: Consider addressing when convenient")
            print(f"    {consolidated.summary['low']} low-severity findings")
        else:
            print("  ✓ MINIMAL RISK: No significant vulnerabilities found")
        
        print("\n" + "=" * 70)
        print("Security testing complete!")
        print("=" * 70)
        print(f"\nView consolidated report: {REPORTS_DIR / 'consolidated_security_report.html'}")


def main():
    """Main execution"""
    suite = SecurityTestSuite()
    
    try:
        # Run all tests
        suite.run_all_tests()
        
        # Generate consolidated report
        consolidated = suite.generate_consolidated_report()
        
        # Print summary
        suite.print_summary(consolidated)
        
        # Exit with error code if critical/high findings
        if consolidated.summary['critical'] > 0 or consolidated.summary['high'] > 0:
            sys.exit(1)
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n✗ Security testing interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n\n✗ Security testing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
