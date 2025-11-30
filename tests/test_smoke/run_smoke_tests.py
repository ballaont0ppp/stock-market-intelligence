"""
Smoke Test Runner

Quick runner for smoke tests - should complete in under 2 minutes.
"""
import pytest
import sys
from datetime import datetime


def run_smoke_tests():
    """Run smoke test suite"""
    print("="*60)
    print("RUNNING SMOKE TESTS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    args = [
        'tests/test_smoke/',
        '-v',
        '-m', 'smoke',
        '--tb=short',
        '--maxfail=5',  # Stop after 5 failures
        '-x'  # Stop on first failure for quick feedback
    ]
    
    start_time = datetime.now()
    exit_code = pytest.main(args)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    print()
    print("="*60)
    print(f"Smoke tests completed in {duration:.2f} seconds")
    
    if exit_code == 0:
        print("✓ All smoke tests PASSED")
        print("Application is ready for use")
    else:
        print("✗ Some smoke tests FAILED")
        print("Application may have critical issues")
    
    print("="*60)
    
    return exit_code


if __name__ == '__main__':
    exit_code = run_smoke_tests()
    sys.exit(exit_code)
