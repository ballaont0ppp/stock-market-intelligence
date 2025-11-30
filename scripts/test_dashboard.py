#!/usr/bin/env python3
"""
Test Dashboard Generator.
Creates a comprehensive dashboard showing all test metrics and trends.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


class TestDashboard:
    """Generates comprehensive test dashboard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dashboard_dir = self.project_root / 'test_dashboard'
        self.dashboard_dir.mkdir(exist_ok=True)
    
    def load_test_metrics(self):
        """Load test execution metrics."""
        metrics_file = self.project_root / 'test_reports' / 'test_metrics.json'
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_coverage_history(self):
        """Load coverage history."""
        history_file = self.project_root / 'coverage_history.json'
        
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    
    def calculate_quality_score(self, metrics, coverage):
        """Calculate overall quality score (0-100)."""
        if not metrics or not coverage:
            return 0
        
        # Weights
        weights = {
            'pass_rate': 0.4,
            'coverage': 0.3,
            'no_failures': 0.2,
            'speed': 0.1
        }
        
        # Pass rate score
        pass_rate = metrics.get('overall_metrics', {}).get('pass_rate', 0)
        pass_score = pass_rate * weights['pass_rate']
        
        # Coverage score
        line_cov = coverage.get('line_coverage', 0)
        cov_score = line_cov * weights['coverage']
        
        # No failures score
        failed = metrics.get('overall_metrics', {}).get('failed', 0)
        no_fail_score = (100 if failed == 0 else 0) * weights['no_failures']
        
        # Speed score (tests should complete in reasonable time)
        duration = metrics.get('overall_metrics', {}).get('duration', 0)
        total_tests = metrics.get('overall_metrics', {}).get('total_tests', 1)
        avg_duration = duration / total_tests if total_tests > 0 else 0
        speed_score = (100 if avg_duration < 1 else 50) * weights['speed']
        
        return round(pass_score + cov_score + no_fail_score + speed_score, 1)
    
    def generate_dashboard_html(self):
        """Generate dashboard HTML."""
        metrics = self.load_test_metrics()
        coverage_history = self.load_coverage_history()
        
        latest_coverage = coverage_history[-1] if coverage_history else {}
        quality_score = self.calculate_quality_score(metrics, latest_coverage)
        
        # Determine quality grade
        if quality_score >= 90:
            grade = "A"
            grade_color = "#10b981"
        elif quality_score >= 80:
            grade = "B"
            grade_color = "#3b82f6"
        elif quality_score >= 70:
            grade = "C"
            grade_color = "#f59e0b"
        elif quality_score >= 60:
            grade = "D"
            grade_color = "#ef4444"
        else:
            grade = "F"
            grade_color = "#991b1b"
        
        overall_metrics = metrics.get('overall_metrics', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Dashboard - Stock Portfolio Platform</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .quality-score {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .quality-score h2 {{
            color: #666;
            margin-bottom: 20px;
        }}
        .score-circle {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: {grade_color};
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        .score-value {{
            font-size: 4em;
            font-weight: bold;
        }}
        .score-grade {{
            font-size: 2em;
            margin-top: -10px;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            color: #666;
            margin-bottom: 20px;
            font-size: 1.1em;
            text-transform: uppercase;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .stat:last-child {{
            border-bottom: none;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.95em;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .stat-value.good {{ color: #10b981; }}
        .stat-value.bad {{ color: #ef4444; }}
        .stat-value.neutral {{ color: #667eea; }}
        .chart-card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .chart-card h3 {{
            color: #666;
            margin-bottom: 20px;
        }}
        .chart-card img {{
            width: 100%;
            height: auto;
            border-radius: 10px;
        }}
        .links {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }}
        .link-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            text-decoration: none;
            color: #667eea;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .link-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Test Quality Dashboard</h1>
            <p>Stock Portfolio Management Platform</p>
            <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="quality-score">
            <h2>Overall Quality Score</h2>
            <div class="score-circle">
                <div class="score-value">{quality_score}</div>
                <div class="score-grade">Grade {grade}</div>
            </div>
            <p style="color: #666; font-size: 1.1em;">
                Based on test pass rate, code coverage, failures, and performance
            </p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>Test Execution</h3>
                <div class="stat">
                    <span class="stat-label">Total Tests</span>
                    <span class="stat-value neutral">{overall_metrics.get('total_tests', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Passed</span>
                    <span class="stat-value good">{overall_metrics.get('passed', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Failed</span>
                    <span class="stat-value bad">{overall_metrics.get('failed', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Skipped</span>
                    <span class="stat-value neutral">{overall_metrics.get('skipped', 0)}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Code Coverage</h3>
                <div class="stat">
                    <span class="stat-label">Line Coverage</span>
                    <span class="stat-value {'good' if latest_coverage.get('line_coverage', 0) >= 85 else 'bad'}">
                        {latest_coverage.get('line_coverage', 0):.1f}%
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Branch Coverage</span>
                    <span class="stat-value {'good' if latest_coverage.get('branch_coverage', 0) >= 85 else 'bad'}">
                        {latest_coverage.get('branch_coverage', 0):.1f}%
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Threshold</span>
                    <span class="stat-value neutral">85%</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Performance</h3>
                <div class="stat">
                    <span class="stat-label">Total Duration</span>
                    <span class="stat-value neutral">{overall_metrics.get('duration', 0):.1f}s</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg per Test</span>
                    <span class="stat-value neutral">{overall_metrics.get('avg_duration', 0):.3f}s</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Pass Rate</span>
                    <span class="stat-value {'good' if overall_metrics.get('pass_rate', 0) >= 95 else 'bad'}">
                        {overall_metrics.get('pass_rate', 0):.1f}%
                    </span>
                </div>
            </div>
        </div>
        
        <div class="chart-card">
            <h3>Coverage Trend</h3>
            <img src="../coverage_charts/coverage_trend.png" alt="Coverage Trend" onerror="this.style.display='none'">
        </div>
        
        <div class="chart-card">
            <h3>Package Coverage</h3>
            <img src="../coverage_charts/package_coverage.png" alt="Package Coverage" onerror="this.style.display='none'">
        </div>
        
        <div class="links">
            <a href="../test_reports/test_report.html" class="link-card">
                📋 Detailed Test Report
            </a>
            <a href="../htmlcov/index.html" class="link-card">
                📊 Coverage Report
            </a>
            <a href="../coverage_charts/index.html" class="link-card">
                📈 Coverage Visualizations
            </a>
            <a href="../test_results.xml" class="link-card">
                📄 JUnit XML Report
            </a>
        </div>
        
        <div class="footer">
            <p>Automated Test Dashboard • Generated by Test Automation System</p>
        </div>
    </div>
</body>
</html>
"""
        
        output_file = self.dashboard_dir / 'index.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"Test dashboard saved to {output_file}")
        print(f"Quality Score: {quality_score}/100 (Grade {grade})")
        
        return output_file
    
    def run(self):
        """Generate dashboard."""
        return self.generate_dashboard_html()


def main():
    """Main entry point."""
    dashboard = TestDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()
