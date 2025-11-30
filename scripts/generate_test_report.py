#!/usr/bin/env python3
"""
Automated Test Reporting System.
Generates comprehensive test reports with metrics, trends, and dashboards.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class TestReporter:
    """Generates comprehensive test reports."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / 'test_reports'
        self.reports_dir.mkdir(exist_ok=True)
        
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'overall_metrics': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0,
                'duration': 0
            },
            'coverage': {},
            'failures': []
        }
    
    def run_tests_with_json_output(self):
        """Run pytest with JSON output."""
        print("Running tests with JSON output...")
        
        result = subprocess.run(
            ['pytest', 'tests/', '--json-report', '--json-report-file=test_report.json',
             '--tb=short', '-v'],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    def parse_pytest_output(self):
        """Parse pytest JSON output."""
        json_report_file = self.project_root / 'test_report.json'
        
        if not json_report_file.exists():
            # Fallback: run pytest with junit XML output
            print("JSON report not found, using XML output...")
            subprocess.run(
                ['pytest', 'tests/', '--junitxml=test_results.xml', '-v'],
                cwd=self.project_root
            )
            return self.parse_junit_xml()
        
        try:
            with open(json_report_file, 'r') as f:
                data = json.load(f)
            
            # Extract metrics
            summary = data.get('summary', {})
            self.metrics['overall_metrics'] = {
                'total_tests': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'errors': summary.get('error', 0),
                'duration': data.get('duration', 0)
            }
            
            # Extract test details
            tests = data.get('tests', [])
            for test in tests:
                if test.get('outcome') == 'failed':
                    self.metrics['failures'].append({
                        'test_name': test.get('nodeid', ''),
                        'error': test.get('call', {}).get('longrepr', 'Unknown error')
                    })
            
            return True
        except Exception as e:
            print(f"Error parsing test output: {e}")
            return False
    
    def parse_junit_xml(self):
        """Parse JUnit XML output as fallback."""
        import xml.etree.ElementTree as ET
        
        xml_file = self.project_root / 'test_results.xml'
        if not xml_file.exists():
            return False
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Parse testsuite
            for testsuite in root.findall('testsuite'):
                total = int(testsuite.get('tests', 0))
                failures = int(testsuite.get('failures', 0))
                errors = int(testsuite.get('errors', 0))
                skipped = int(testsuite.get('skipped', 0))
                time = float(testsuite.get('time', 0))
                
                self.metrics['overall_metrics'] = {
                    'total_tests': total,
                    'passed': total - failures - errors - skipped,
                    'failed': failures,
                    'skipped': skipped,
                    'errors': errors,
                    'duration': time
                }
                
                # Extract failures
                for testcase in testsuite.findall('.//testcase'):
                    failure = testcase.find('failure')
                    if failure is not None:
                        self.metrics['failures'].append({
                            'test_name': f"{testcase.get('classname')}.{testcase.get('name')}",
                            'error': failure.text or 'Unknown error'
                        })
            
            return True
        except Exception as e:
            print(f"Error parsing JUnit XML: {e}")
            return False
    
    def load_coverage_data(self):
        """Load coverage data."""
        coverage_history_file = self.project_root / 'coverage_history.json'
        
        if coverage_history_file.exists():
            try:
                with open(coverage_history_file, 'r') as f:
                    history = json.load(f)
                    if history:
                        self.metrics['coverage'] = history[-1]
            except Exception as e:
                print(f"Error loading coverage data: {e}")
    
    def calculate_test_metrics(self):
        """Calculate additional test metrics."""
        metrics = self.metrics['overall_metrics']
        
        if metrics['total_tests'] > 0:
            metrics['pass_rate'] = (metrics['passed'] / metrics['total_tests']) * 100
            metrics['fail_rate'] = (metrics['failed'] / metrics['total_tests']) * 100
            metrics['skip_rate'] = (metrics['skipped'] / metrics['total_tests']) * 100
        else:
            metrics['pass_rate'] = 0
            metrics['fail_rate'] = 0
            metrics['skip_rate'] = 0
        
        # Calculate average test duration
        if metrics['total_tests'] > 0:
            metrics['avg_duration'] = metrics['duration'] / metrics['total_tests']
        else:
            metrics['avg_duration'] = 0
    
    def generate_html_report(self):
        """Generate HTML test report."""
        metrics = self.metrics['overall_metrics']
        coverage = self.metrics.get('coverage', {})
        
        # Determine overall status
        overall_status = "PASSED" if metrics['failed'] == 0 and metrics['errors'] == 0 else "FAILED"
        status_color = "#10b981" if overall_status == "PASSED" else "#ef4444"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - Stock Portfolio Platform</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .status {{
            font-size: 1.5em;
            font-weight: bold;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            display: inline-block;
            margin-top: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-value.passed {{ color: #10b981; }}
        .metric-value.failed {{ color: #ef4444; }}
        .metric-value.skipped {{ color: #f59e0b; }}
        .metric-value.total {{ color: #667eea; }}
        .metric-subtitle {{
            color: #999;
            font-size: 0.9em;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-segment {{
            height: 100%;
            float: left;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .progress-passed {{ background: #10b981; }}
        .progress-failed {{ background: #ef4444; }}
        .progress-skipped {{ background: #f59e0b; }}
        .failure-list {{
            list-style: none;
        }}
        .failure-item {{
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        .failure-item h4 {{
            color: #ef4444;
            margin-bottom: 10px;
        }}
        .failure-item pre {{
            background: #fff;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.85em;
        }}
        .coverage-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .coverage-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e5e7eb;
        }}
        .coverage-card h4 {{
            color: #666;
            margin-bottom: 10px;
        }}
        .coverage-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f9fafb;
            font-weight: 600;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Execution Report</h1>
            <p>Stock Portfolio Management Platform</p>
            <p>Generated: {self.metrics['timestamp']}</p>
            <div class="status" style="background-color: {status_color};">
                {overall_status}
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Tests</h3>
                <div class="metric-value total">{metrics['total_tests']}</div>
                <div class="metric-subtitle">Executed</div>
            </div>
            
            <div class="metric-card">
                <h3>Passed</h3>
                <div class="metric-value passed">{metrics['passed']}</div>
                <div class="metric-subtitle">{metrics.get('pass_rate', 0):.1f}%</div>
            </div>
            
            <div class="metric-card">
                <h3>Failed</h3>
                <div class="metric-value failed">{metrics['failed']}</div>
                <div class="metric-subtitle">{metrics.get('fail_rate', 0):.1f}%</div>
            </div>
            
            <div class="metric-card">
                <h3>Skipped</h3>
                <div class="metric-value skipped">{metrics['skipped']}</div>
                <div class="metric-subtitle">{metrics.get('skip_rate', 0):.1f}%</div>
            </div>
            
            <div class="metric-card">
                <h3>Duration</h3>
                <div class="metric-value total">{metrics['duration']:.1f}s</div>
                <div class="metric-subtitle">{metrics.get('avg_duration', 0):.3f}s avg</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Test Results Distribution</h2>
            <div class="progress-bar">
                <div class="progress-segment progress-passed" style="width: {metrics.get('pass_rate', 0)}%;">
                    {metrics['passed']} Passed
                </div>
                <div class="progress-segment progress-failed" style="width: {metrics.get('fail_rate', 0)}%;">
                    {metrics['failed']} Failed
                </div>
                <div class="progress-segment progress-skipped" style="width: {metrics.get('skip_rate', 0)}%;">
                    {metrics['skipped']} Skipped
                </div>
            </div>
        </div>
        
        {self._generate_coverage_section(coverage)}
        
        {self._generate_failures_section()}
        
        <div class="footer">
            <p>For detailed coverage reports, see <a href="../htmlcov/index.html">HTML Coverage Report</a></p>
            <p>For detailed test logs, see <a href="../test_results.xml">JUnit XML Report</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        output_file = self.reports_dir / 'test_report.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"HTML test report saved to {output_file}")
        return output_file
    
    def _generate_coverage_section(self, coverage):
        """Generate coverage section HTML."""
        if not coverage:
            return ""
        
        line_cov = coverage.get('line_coverage', 0)
        branch_cov = coverage.get('branch_coverage', 0)
        
        return f"""
        <div class="section">
            <h2>Code Coverage</h2>
            <div class="coverage-grid">
                <div class="coverage-card">
                    <h4>Line Coverage</h4>
                    <div class="coverage-value">{line_cov:.2f}%</div>
                </div>
                <div class="coverage-card">
                    <h4>Branch Coverage</h4>
                    <div class="coverage-value">{branch_cov:.2f}%</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_failures_section(self):
        """Generate failures section HTML."""
        failures = self.metrics.get('failures', [])
        
        if not failures:
            return """
        <div class="section">
            <h2>Test Failures</h2>
            <p style="color: #10b981; font-size: 1.2em;">✓ No test failures!</p>
        </div>
            """
        
        failures_html = ""
        for failure in failures[:10]:  # Show first 10 failures
            test_name = failure.get('test_name', 'Unknown')
            error = failure.get('error', 'Unknown error')
            # Escape HTML
            error = error.replace('<', '&lt;').replace('>', '&gt;')
            
            failures_html += f"""
            <div class="failure-item">
                <h4>{test_name}</h4>
                <pre>{error[:500]}...</pre>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>Test Failures ({len(failures)})</h2>
            <ul class="failure-list">
                {failures_html}
            </ul>
            {f'<p><em>Showing first 10 of {len(failures)} failures</em></p>' if len(failures) > 10 else ''}
        </div>
        """
    
    def save_json_report(self):
        """Save metrics as JSON."""
        output_file = self.reports_dir / 'test_metrics.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"JSON metrics saved to {output_file}")
    
    def print_summary(self):
        """Print test summary to console."""
        metrics = self.metrics['overall_metrics']
        
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        print(f"Total Tests:  {metrics['total_tests']}")
        print(f"Passed:       {metrics['passed']} ({metrics.get('pass_rate', 0):.1f}%)")
        print(f"Failed:       {metrics['failed']} ({metrics.get('fail_rate', 0):.1f}%)")
        print(f"Skipped:      {metrics['skipped']} ({metrics.get('skip_rate', 0):.1f}%)")
        print(f"Errors:       {metrics['errors']}")
        print(f"Duration:     {metrics['duration']:.2f}s")
        
        if self.metrics.get('coverage'):
            coverage = self.metrics['coverage']
            print(f"\nLine Coverage:   {coverage.get('line_coverage', 0):.2f}%")
            print(f"Branch Coverage: {coverage.get('branch_coverage', 0):.2f}%")
        
        print("\n" + "="*80 + "\n")
    
    def run(self):
        """Run test reporting."""
        # Parse test results
        if not self.parse_pytest_output():
            print("Warning: Could not parse test output")
        
        # Load coverage data
        self.load_coverage_data()
        
        # Calculate metrics
        self.calculate_test_metrics()
        
        # Generate reports
        self.generate_html_report()
        self.save_json_report()
        
        # Print summary
        self.print_summary()
        
        return self.metrics['overall_metrics']['failed'] == 0


def main():
    """Main entry point."""
    reporter = TestReporter()
    success = reporter.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
