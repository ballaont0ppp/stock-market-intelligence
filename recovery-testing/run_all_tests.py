"""
Run All Recovery and Resilience Tests

This script runs all recovery testing suites and generates a comprehensive report.
"""
import subprocess
import sys
import os
import time
from datetime import datetime
import json

# Test suites
TEST_SUITES = [
    {
        'name': 'Database Recovery',
        'file': 'test_database_recovery.py',
        'description': 'Database failure recovery, connection loss, backup/restore'
    },
    {
        'name': 'Application Recovery',
        'file': 'test_application_recovery.py',
        'description': 'Server crash, memory exhaustion, exception handling'
    },
    {
        'name': 'Network Recovery',
        'file': 'test_network_recovery.py',
        'description': 'Network failures, API unavailability, retry mechanisms'
    },
    {
        'name': 'Data Loss Prevention',
        'file': 'test_data_loss_prevention.py',
        'description': 'Backup procedures, point-in-time recovery, disaster recovery'
    }
]


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_test_suite(suite):
    """Run a single test suite"""
    print(f"\n{'=' * 80}")
    print(f"Running: {suite['name']}")
    print(f"Description: {suite['description']}")
    print(f"{'=' * 80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', suite['file'], '-v', '--tb=short'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per suite
        )
        
        elapsed_time = time.time() - start_time
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            'name': suite['name'],
            'file': suite['file'],
            'passed': result.returncode == 0,
            'return_code': result.returncode,
            'elapsed_time': elapsed_time,
            'output': result.stdout
        }
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"\n⚠ Test suite timed out after {elapsed_time:.2f} seconds\n")
        return {
            'name': suite['name'],
            'file': suite['file'],
            'passed': False,
            'return_code': -1,
            'elapsed_time': elapsed_time,
            'output': 'Test suite timed out'
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n✗ Error running test suite: {e}\n")
        return {
            'name': suite['name'],
            'file': suite['file'],
            'passed': False,
            'return_code': -1,
            'elapsed_time': elapsed_time,
            'output': str(e)
        }


def generate_summary_report(results):
    """Generate summary report"""
    print_header("RECOVERY TESTING SUMMARY")
    
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r['passed'])
    failed_suites = total_suites - passed_suites
    total_time = sum(r['elapsed_time'] for r in results)
    
    print(f"Total Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {failed_suites}")
    print(f"Total Time: {total_time:.2f} seconds")
    print()
    
    # Detailed results
    print("Detailed Results:")
    print("-" * 80)
    for result in results:
        status = "✓ PASSED" if result['passed'] else "✗ FAILED"
        print(f"{status} - {result['name']}")
        print(f"  File: {result['file']}")
        print(f"  Time: {result['elapsed_time']:.2f}s")
        print(f"  Return Code: {result['return_code']}")
        print()
    
    # Save results to JSON
    os.makedirs('results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'results/recovery_test_results_{timestamp}.json'
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': {
                'total_suites': total_suites,
                'passed': passed_suites,
                'failed': failed_suites,
                'total_time': total_time
            },
            'results': results
        }, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()
    
    return passed_suites == total_suites


def main():
    """Main execution function"""
    print_header("RECOVERY AND RESILIENCE TESTING SUITE")
    
    print("This test suite will verify:")
    print("  • Database failure recovery")
    print("  • Application crash recovery")
    print("  • Network failure handling")
    print("  • Data loss prevention")
    print()
    
    # Check if running in correct directory
    if not os.path.exists('config.py'):
        print("✗ Error: config.py not found. Please run from recovery-testing directory.")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('results', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('screenshots', exist_ok=True)
    
    print("Starting tests...\n")
    start_time = time.time()
    
    # Run all test suites
    results = []
    for suite in TEST_SUITES:
        result = run_test_suite(suite)
        results.append(result)
        
        # Brief pause between suites
        time.sleep(2)
    
    total_time = time.time() - start_time
    
    # Generate summary
    all_passed = generate_summary_report(results)
    
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    if all_passed:
        print("\n✓ All recovery tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some recovery tests failed. Please review the results.")
        sys.exit(1)


if __name__ == '__main__':
    main()
