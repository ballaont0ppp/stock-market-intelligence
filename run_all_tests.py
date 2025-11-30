#!/usr/bin/env python3
"""
Comprehensive test runner for the Stock Portfolio Platform.
Executes all test suites and generates detailed reports.
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Orchestrates test execution and reporting."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'overall_status': 'PASSED',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0
        }
        self.project_root = Path(__file__).parent
    
    def run_command(self, command, description):
        """Run a shell command and capture output."""
        print(f"\n{'='*80}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(command)}")
        print(f"{'='*80}\n")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print(f"ERROR: {description} timed out after 10 minutes")
            return False, "", "Timeout"
        except Exception as e:
            print(f"ERROR: Failed to run {description}: {str(e)}")
            return False, "", str(e)
    
    def run_unit_tests(self):
        """Run unit tests."""
        success, stdout, stderr = self.run_command(
            ['pytest', 'tests/test_models/', 'tests/test_services/', 
             '-v', '--tb=short', '--cov=app', '--cov-report=term'],
            "Unit Tests"
        )
        
        self.results['test_suites']['unit_tests'] = {
            'status': 'PASSED' if success else 'FAILED',
            'output': stdout
        }
        
        if not success:
            self.results['overall_status'] = 'FAILED'
        
        return success
    
    def run_integration_tests(self):
        """Run integration tests."""
        success, stdout, stderr = self.run_command(
            ['pytest', 'tests/test_integration/', 'tests/test_routes/', 
             '-v', '--tb=short'],
            "Integration Tests"
        )
        
        self.results['test_suites']['integration_tests'] = {
            'status': 'PASSED' if success else 'FAILED',
            'output': stdout
        }
        
        if not success:
            self.results['overall_status'] = 'FAILED'
        
        return success
    
    def run_smoke_tests(self):
        """Run smoke tests."""
        smoke_test_path = self.project_root / 'tests' / 'test_smoke' / 'run_smoke_tests.py'
        
        if not smoke_test_path.exists():
            print(f"Smoke tests not found at {smoke_test_path}")
            return True
        
        success, stdout, stderr = self.run_command(
            ['python', str(smoke_test_path)],
            "Smoke Tests"
        )
        
        self.results['test_suites']['smoke_tests'] = {
            'status': 'PASSED' if success else 'FAILED',
            'output': stdout
        }
        
        if not success:
            self.results['overall_status'] = 'FAILED'
        
        return success
    
    def run_regression_tests(self):
        """Run regression tests."""
        regression_test_path = self.project_root / 'run_all_regression_tests.py'
        
        if not regression_test_path.exists():
            print(f"Regression tests not found at {regression_test_path}")
            return True
        
        success, stdout, stderr = self.run_command(
            ['python', str(regression_test_path)],
            "Regression Tests"
        )
        
        self.results['test_suites']['regression_tests'] = {
            'status': 'PASSED' if success else 'FAILED',
            'output': stdout
        }
        
        if not success:
            self.results['overall_status'] = 'FAILED'
        
        return success
    
    def run_security_tests(self):
        """Run security tests."""
        security_test_path = self.project_root / 'security-testing' / 'run_all_security_tests.py'
        
        if not security_test_path.exists():
            print(f"Security tests not found at {security_test_path}")
            return True
        
        success, stdout, stderr = self.run_command(
            ['python', str(security_test_path)],
            "Security Tests"
        )
        
        self.results['test_suites']['security_tests'] = {
            'status': 'PASSED' if success else 'FAILED',
            'output': stdout
        }
        
        if not success:
            self.results['overall_status'] = 'FAILED'
        
        return success
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print(f"\n{'='*80}")
        print("Generating Coverage Report")
        print(f"{'='*80}\n")
        
        success, stdout, stderr = self.run_command(
            ['pytest', '--cov=app', '--cov-report=html', '--cov-report=xml', 
             '--cov-report=term-missing', 'tests/'],
            "Coverage Report Generation"
        )
        
        if success:
            print("\nCoverage reports generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - XML: coverage.xml")
        
        return success
    
    def save_results(self):
        """Save test results to JSON file."""
        results_file = self.project_root / 'test_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nTest results saved to: {results_file}")
    
    def print_summary(self):
        """Print test execution summary."""
        print(f"\n{'='*80}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"Timestamp: {self.results['timestamp']}\n")
        
        print("Test Suite Results:")
        for suite_name, suite_data in self.results['test_suites'].items():
            status_symbol = "✓" if suite_data['status'] == 'PASSED' else "✗"
            print(f"  {status_symbol} {suite_name.replace('_', ' ').title()}: {suite_data['status']}")
        
        print(f"\n{'='*80}\n")
    
    def run_all(self):
        """Run all test suites."""
        print("Starting comprehensive test execution...")
        print(f"Project root: {self.project_root}\n")
        
        # Run test suites
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_smoke_tests()
        self.run_regression_tests()
        self.run_security_tests()
        
        # Generate coverage report
        self.generate_coverage_report()
        
        # Save and display results
        self.save_results()
        self.print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if self.results['overall_status'] == 'PASSED' else 1)


if __name__ == '__main__':
    runner = TestRunner()
    runner.run_all()
