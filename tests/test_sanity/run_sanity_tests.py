"""
Sanity Test Runner

Quick validation runner for sanity tests after deployment.
Target execution time: < 15 minutes
"""
import pytest
import sys
from datetime import datetime


def run_sanity_tests():
    """Run sanity test suite"""
    print("="*60)
    print("RUNNING SANITY TESTS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target completion: < 15 minutes")
    print()
    
    args = [
        'tests/test_sanity/',
        '-v',
        '-m', 'sanity',
        '--tb=short',
        '--maxfail=10'  # Stop after 10 failures
    ]
    
    start_time = datetime.now()
    exit_code = pytest.main(args)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    minutes = duration / 60
    
    print()
    print("="*60)
    print(f"Sanity tests completed in {minutes:.2f} minutes ({duration:.2f} seconds)")
    
    if minutes > 15:
        print("⚠️  Warning: Sanity tests exceeded 15 minute target")
    
    if exit_code == 0:
        print("✓ All sanity tests PASSED")
        print("Changed modules are functioning correctly")
    else:
        print("✗ Some sanity tests FAILED")
        print("Recent changes may have introduced issues")
    
    print("="*60)
    
    return exit_code


if __name__ == '__main__':
    exit_code = run_sanity_tests()
    sys.exit(exit_code)
