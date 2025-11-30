"""
Master Regression Test Runner

Orchestrates all regression test suites:
- Smoke tests (< 2 minutes)
- Sanity tests (< 15 minutes)
- Full regression tests (< 2 hours)

Usage:
    python run_all_regression_tests.py [suite]
    
    suite options:
        smoke    - Run smoke tests only
        sanity   - Run sanity tests only
        full     - Run full regression suite
        all      - Run all test suites (default)
"""
import sys
import argparse
from datetime import datetime
from pathlib import Path
import json


def run_smoke_tests():
    """Run smoke test suite"""
    print("\n" + "="*70)
    print("RUNNING SMOKE TESTS")
    print("="*70)
    print("Target: < 2 minutes")
    print()
    
    import pytest
    args = [
        'tests/test_smoke/',
        '-v',
        '-m', 'smoke',
        '--tb=short',
        '-x'  # Stop on first failure
    ]
    
    start = datetime.now()
    exit_code = pytest.main(args)
    duration = (datetime.now() - start).total_seconds()
    
    print(f"\nSmoke tests completed in {duration:.2f} seconds")
    return exit_code, duration


def run_sanity_tests():
    """Run sanity test suite"""
    print("\n" + "="*70)
    print("RUNNING SANITY TESTS")
    print("="*70)
    print("Target: < 15 minutes")
    print()
    
    import pytest
    args = [
        'tests/test_sanity/',
        '-v',
        '-m', 'sanity',
        '--tb=short'
    ]
    
    start = datetime.now()
    exit_code = pytest.main(args)
    duration = (datetime.now() - start).total_seconds()
    
    print(f"\nSanity tests completed in {duration / 60:.2f} minutes")
    return exit_code, duration


def run_full_regression():
    """Run full regression test suite"""
    print("\n" + "="*70)
    print("RUNNING FULL REGRESSION TESTS")
    print("="*70)
    print("Target: < 2 hours")
    print()
    
    import pytest
    args = [
        'tests/test_regression/',
        '-v',
        '-m', 'regression',
        '--tb=short',
        '--cov=app',
        '--cov-report=html',
        '--cov-report=term-missing'
    ]
    
    start = datetime.now()
    exit_code = pytest.main(args)
    duration = (datetime.now() - start).total_seconds()
    
    print(f"\nFull regression tests completed in {duration / 60:.2f} minutes")
    return exit_code, duration


def generate_report(results):
    """Generate comprehensive test report"""
    report_dir = Path('test_results')
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'regression_report_{timestamp}.json'
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total_suites': len(results),
            'passed_suites': sum(1 for r in results.values() if r['exit_code'] == 0),
            'failed_suites': sum(1 for r in results.values() if r['exit_code'] != 0),
            'total_duration': sum(r['duration'] for r in results.values())
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    return report_data


def print_summary(results):
    """Print test execution summary"""
    print("\n" + "="*70)
    print("REGRESSION TEST EXECUTION SUMMARY")
    print("="*70)
    
    total_duration = sum(r['duration'] for r in results.values())
    all_passed = all(r['exit_code'] == 0 for r in results.values())
    
    for suite_name, suite_result in results.items():
        status = "✓ PASSED" if suite_result['exit_code'] == 0 else "✗ FAILED"
        duration = suite_result['duration']
        
        if duration < 60:
            time_str = f"{duration:.2f}s"
        elif duration < 3600:
            time_str = f"{duration / 60:.2f}m"
        else:
            time_str = f"{duration / 3600:.2f}h"
        
        print(f"{suite_name:20s}: {status:10s} ({time_str})")
    
    print("-" * 70)
    
    if total_duration < 60:
        total_time_str = f"{total_duration:.2f} seconds"
    elif total_duration < 3600:
        total_time_str = f"{total_duration / 60:.2f} minutes"
    else:
        total_time_str = f"{total_duration / 3600:.2f} hours"
    
    print(f"Total execution time: {total_time_str}")
    
    print("="*70)
    
    if all_passed:
        print("✓ ALL REGRESSION TESTS PASSED")
        print("Application is stable and ready for release")
    else:
        print("✗ SOME REGRESSION TESTS FAILED")
        print("Review failures before proceeding with release")
    
    print("="*70)
    
    return 0 if all_passed else 1


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description='Run regression test suites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['smoke', 'sanity', 'full', 'all'],
        help='Test suite to run (default: all)'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("REGRESSION TEST SUITE RUNNER")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Running: {args.suite} test suite(s)")
    print("="*70)
    
    results = {}
    
    try:
        if args.suite in ['smoke', 'all']:
            exit_code, duration = run_smoke_tests()
            results['Smoke Tests'] = {'exit_code': exit_code, 'duration': duration}
            
            if exit_code != 0 and args.suite == 'all':
                print("\n⚠️  Smoke tests failed. Stopping execution.")
                print("Fix smoke test failures before running other suites.")
                return exit_code
        
        if args.suite in ['sanity', 'all']:
            exit_code, duration = run_sanity_tests()
            results['Sanity Tests'] = {'exit_code': exit_code, 'duration': duration}
            
            if exit_code != 0 and args.suite == 'all':
                print("\n⚠️  Sanity tests failed. Stopping execution.")
                print("Fix sanity test failures before running full regression.")
                return exit_code
        
        if args.suite in ['full', 'all']:
            exit_code, duration = run_full_regression()
            results['Full Regression'] = {'exit_code': exit_code, 'duration': duration}
        
        # Generate report
        if args.report or args.suite == 'all':
            generate_report(results)
        
        # Print summary
        final_exit_code = print_summary(results)
        
        return final_exit_code
        
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\nError during test execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
