#!/usr/bin/env python3
"""
Code Cleanup and Quality Check Script

This script performs automated code cleanup and quality checks:
- Removes unused imports
- Formats code with black
- Sorts imports with isort
- Runs linting with flake8
- Checks for security issues with bandit
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and report results"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            print(f"✗ {description} found issues (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"✗ Error running {description}: {str(e)}")
        return False


def main():
    """Main cleanup workflow"""
    print("Starting Code Cleanup and Quality Checks...")
    print(f"Working directory: {Path.cwd()}")
    
    results = {}
    
    # 1. Remove unused imports with autoflake
    results['autoflake'] = run_command(
        'autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive app/ tests/',
        "Removing unused imports and variables"
    )
    
    # 2. Sort imports with isort
    results['isort'] = run_command(
        'isort app/ tests/ scripts/',
        "Sorting imports with isort"
    )
    
    # 3. Format code with black
    results['black'] = run_command(
        'black app/ tests/ scripts/',
        "Formatting code with black"
    )
    
    # 4. Run flake8 linting
    results['flake8'] = run_command(
        'flake8 app/ tests/',
        "Running flake8 linting"
    )
    
    # 5. Run pylint
    results['pylint'] = run_command(
        'pylint app/ --rcfile=pyproject.toml',
        "Running pylint analysis"
    )
    
    # 6. Run bandit security checks
    results['bandit'] = run_command(
        'bandit -r app/ -f txt',
        "Running bandit security checks"
    )
    
    # 7. Check for common security issues
    results['safety'] = run_command(
        'safety check --json',
        "Checking dependencies for security vulnerabilities"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("CLEANUP SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, status in results.items():
        status_icon = "✓" if status else "✗"
        print(f"{status_icon} {check}: {'PASSED' if status else 'FAILED'}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All code quality checks passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
