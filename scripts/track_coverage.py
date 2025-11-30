#!/usr/bin/env python3
"""
Test Coverage Tracking and Reporting Script.
Tracks coverage trends over time and enforces coverage thresholds.
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET


class CoverageTracker:
    """Tracks and reports test coverage metrics."""
    
    def __init__(self, threshold=85.0):
        self.threshold = threshold
        self.project_root = Path(__file__).parent.parent
        self.coverage_history_file = self.project_root / 'coverage_history.json'
        self.coverage_xml = self.project_root / 'coverage.xml'
        
    def run_coverage(self):
        """Run tests with coverage."""
        print("Running tests with coverage...")
        
        result = subprocess.run(
            ['pytest', '--cov=app', '--cov-report=xml', '--cov-report=html', 
             '--cov-report=term-missing', 'tests/'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    
    def parse_coverage_xml(self):
        """Parse coverage.xml to extract metrics."""
        if not self.coverage_xml.exists():
            print(f"Coverage XML not found at {self.coverage_xml}")
            return None
        
        try:
            tree = ET.parse(self.coverage_xml)
            root = tree.getroot()
            
            # Get overall coverage
            coverage_elem = root.find('.')
            line_rate = float(coverage_elem.get('line-rate', 0)) * 100
            branch_rate = float(coverage_elem.get('branch-rate', 0)) * 100
            
            # Get package-level coverage
            packages = {}
            for package in root.findall('.//package'):
                package_name = package.get('name')
                pkg_line_rate = float(package.get('line-rate', 0)) * 100
                pkg_branch_rate = float(package.get('branch-rate', 0)) * 100
                
                packages[package_name] = {
                    'line_coverage': round(pkg_line_rate, 2),
                    'branch_coverage': round(pkg_branch_rate, 2)
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'line_coverage': round(line_rate, 2),
                'branch_coverage': round(branch_rate, 2),
                'packages': packages
            }
        except Exception as e:
            print(f"Error parsing coverage XML: {e}")
            return None
    
    def load_coverage_history(self):
        """Load historical coverage data."""
        if not self.coverage_history_file.exists():
            return []
        
        try:
            with open(self.coverage_history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading coverage history: {e}")
            return []
    
    def save_coverage_history(self, history):
        """Save coverage history to file."""
        try:
            with open(self.coverage_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            print(f"Coverage history saved to {self.coverage_history_file}")
        except Exception as e:
            print(f"Error saving coverage history: {e}")
    
    def update_coverage_history(self, current_coverage):
        """Update coverage history with current metrics."""
        history = self.load_coverage_history()
        history.append(current_coverage)
        
        # Keep only last 100 entries
        if len(history) > 100:
            history = history[-100:]
        
        self.save_coverage_history(history)
        return history
    
    def calculate_trend(self, history):
        """Calculate coverage trend."""
        if len(history) < 2:
            return "N/A"
        
        recent = history[-5:] if len(history) >= 5 else history
        first_coverage = recent[0]['line_coverage']
        last_coverage = recent[-1]['line_coverage']
        
        diff = last_coverage - first_coverage
        
        if diff > 1:
            return f"↑ Improving (+{diff:.2f}%)"
        elif diff < -1:
            return f"↓ Declining ({diff:.2f}%)"
        else:
            return "→ Stable"
    
    def print_coverage_report(self, current_coverage, history):
        """Print detailed coverage report."""
        print("\n" + "="*80)
        print("TEST COVERAGE REPORT")
        print("="*80 + "\n")
        
        print(f"Timestamp: {current_coverage['timestamp']}")
        print(f"Coverage Threshold: {self.threshold}%\n")
        
        # Overall coverage
        line_cov = current_coverage['line_coverage']
        branch_cov = current_coverage['branch_coverage']
        
        line_status = "✓ PASS" if line_cov >= self.threshold else "✗ FAIL"
        branch_status = "✓ PASS" if branch_cov >= self.threshold else "✗ FAIL"
        
        print("Overall Coverage:")
        print(f"  Line Coverage:   {line_cov:6.2f}% {line_status}")
        print(f"  Branch Coverage: {branch_cov:6.2f}% {branch_status}")
        
        # Trend
        trend = self.calculate_trend(history)
        print(f"\nCoverage Trend: {trend}")
        
        # Package-level coverage
        print("\nPackage Coverage:")
        for package_name, metrics in sorted(current_coverage['packages'].items()):
            pkg_line_cov = metrics['line_coverage']
            pkg_status = "✓" if pkg_line_cov >= self.threshold else "✗"
            print(f"  {pkg_status} {package_name:40s} {pkg_line_cov:6.2f}%")
        
        # Historical data
        if len(history) > 1:
            print("\nRecent Coverage History:")
            for entry in history[-5:]:
                timestamp = entry['timestamp'][:19]  # Remove microseconds
                line_cov = entry['line_coverage']
                print(f"  {timestamp}: {line_cov:6.2f}%")
        
        print("\n" + "="*80 + "\n")
        
        # Coverage reports location
        print("Detailed Reports:")
        print(f"  HTML Report: {self.project_root}/htmlcov/index.html")
        print(f"  XML Report:  {self.project_root}/coverage.xml")
        print(f"  History:     {self.coverage_history_file}")
        print()
    
    def check_threshold(self, current_coverage):
        """Check if coverage meets threshold."""
        line_cov = current_coverage['line_coverage']
        branch_cov = current_coverage['branch_coverage']
        
        if line_cov < self.threshold:
            print(f"ERROR: Line coverage ({line_cov:.2f}%) is below threshold ({self.threshold}%)")
            return False
        
        if branch_cov < self.threshold:
            print(f"WARNING: Branch coverage ({branch_cov:.2f}%) is below threshold ({self.threshold}%)")
            # Don't fail on branch coverage, just warn
        
        return True
    
    def generate_badge(self, coverage):
        """Generate coverage badge data."""
        line_cov = coverage['line_coverage']
        
        if line_cov >= 90:
            color = "brightgreen"
        elif line_cov >= 80:
            color = "green"
        elif line_cov >= 70:
            color = "yellowgreen"
        elif line_cov >= 60:
            color = "yellow"
        else:
            color = "red"
        
        badge_data = {
            "schemaVersion": 1,
            "label": "coverage",
            "message": f"{line_cov:.1f}%",
            "color": color
        }
        
        badge_file = self.project_root / 'coverage_badge.json'
        with open(badge_file, 'w') as f:
            json.dump(badge_data, f, indent=2)
        
        print(f"Coverage badge data saved to {badge_file}")
    
    def run(self):
        """Run coverage tracking."""
        # Run tests with coverage
        if not self.run_coverage():
            print("ERROR: Tests failed")
            return False
        
        # Parse coverage results
        current_coverage = self.parse_coverage_xml()
        if not current_coverage:
            print("ERROR: Failed to parse coverage data")
            return False
        
        # Update history
        history = self.update_coverage_history(current_coverage)
        
        # Print report
        self.print_coverage_report(current_coverage, history)
        
        # Generate badge
        self.generate_badge(current_coverage)
        
        # Check threshold
        return self.check_threshold(current_coverage)


def main():
    """Main entry point."""
    # Get threshold from environment or use default
    threshold = float(os.environ.get('COVERAGE_THRESHOLD', '85.0'))
    
    tracker = CoverageTracker(threshold=threshold)
    success = tracker.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
