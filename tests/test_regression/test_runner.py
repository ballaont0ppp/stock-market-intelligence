"""
Regression Test Runner

Provides utilities for running regression tests with different configurations
and generating reports for CI/CD integration.
"""
import pytest
import sys
import json
from datetime import datetime
from pathlib import Path


class RegressionTestRunner:
    """Runner for regression test suites"""
    
    def __init__(self, output_dir='test_results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'suites': {}
        }
    
    def run_critical_path_tests(self):
        """Run critical path regression tests"""
        print("Running Critical Path Regression Tests...")
        
        args = [
            'tests/test_regression/test_critical_paths.py',
            '-v',
            '-m', 'critical',
            '--tb=short',
            '--json-report',
            f'--json-report-file={self.output_dir}/critical_paths.json'
        ]
        
        exit_code = pytest.main(args)
        self.results['suites']['critical_paths'] = {
            'exit_code': exit_code,
            'passed': exit_code == 0
        }
        
        return exit_code
    
    def run_high_risk_tests(self):
        """Run high-risk area regression tests"""
        print("Running High-Risk Area Regression Tests...")
        
        args = [
            'tests/test_regression/test_high_risk_areas.py',
            '-v',
            '-m', 'high_risk',
            '--tb=short',
            '--json-report',
            f'--json-report-file={self.output_dir}/high_risk.json'
        ]
        
        exit_code = pytest.main(args)
        self.results['suites']['high_risk'] = {
            'exit_code': exit_code,
            'passed': exit_code == 0
        }
        
        return exit_code
    
    def run_all_regression_tests(self):
        """Run all regression tests"""
        print("Running All Regression Tests...")
        
        args = [
            'tests/test_regression/',
            '-v',
            '-m', 'regression',
            '--tb=short',
            '--json-report',
            f'--json-report-file={self.output_dir}/all_regression.json'
        ]
        
        exit_code = pytest.main(args)
        self.results['suites']['all_regression'] = {
            'exit_code': exit_code,
            'passed': exit_code == 0
        }
        
        return exit_code
    
    def generate_report(self):
        """Generate regression test report"""
        report_file = self.output_dir / f'regression_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nRegression Test Report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("REGRESSION TEST SUMMARY")
        print("="*60)
        
        all_passed = all(suite['passed'] for suite in self.results['suites'].values())
        
        for suite_name, suite_results in self.results['suites'].items():
            status = "✓ PASSED" if suite_results['passed'] else "✗ FAILED"
            print(f"{suite_name}: {status}")
        
        print("="*60)
        
        if all_passed:
            print("✓ All regression tests PASSED")
            return 0
        else:
            print("✗ Some regression tests FAILED")
            return 1


def run_regression_suite(suite='all'):
    """
    Run regression test suite
    
    Args:
        suite: 'all', 'critical', or 'high_risk'
    """
    runner = RegressionTestRunner()
    
    if suite == 'critical':
        exit_code = runner.run_critical_path_tests()
    elif suite == 'high_risk':
        exit_code = runner.run_high_risk_tests()
    else:
        exit_code = runner.run_all_regression_tests()
    
    runner.generate_report()
    return exit_code


if __name__ == '__main__':
    suite_type = sys.argv[1] if len(sys.argv) > 1 else 'all'
    exit_code = run_regression_suite(suite_type)
    sys.exit(exit_code)
