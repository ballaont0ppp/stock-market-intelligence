"""
Script to run all model tests
"""

import sys
import os
import subprocess

def run_test(test_file):
    """Run a single test file"""
    print("="*45)
    print(f"Running {test_file}")
    print("="*45)
    
    # Get the full path to the test file
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    # Run the test file
    try:
        result = subprocess.run([sys.executable, test_path], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Print stdout
        if result.stdout:
            print(result.stdout)
        
        # Print stderr
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {str(e)}")
        return False

def run_all_tests():
    """Run all model tests"""
    print("Running all model tests...")
    print()
    
    # List of test files to run
    test_files = [
        "test_lstm_model.py",
        "test_arima_model.py",
        "test_linear_regression_model.py"
    ]
    
    # Run each test
    results = []
    for test_file in test_files:
        success = run_test(test_file)
        results.append((test_file, success))
        print()
    
    # Print summary
    print("="*45)
    print("TEST SUMMARY")
    print("="*45)
    all_passed = True
    for test_file, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_file}: {status}")
        if not success:
            all_passed = False
    
    print("="*45)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)