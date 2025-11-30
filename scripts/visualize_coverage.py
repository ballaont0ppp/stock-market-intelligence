#!/usr/bin/env python3
"""
Coverage Visualization Script.
Creates charts and graphs showing coverage trends over time.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")


class CoverageVisualizer:
    """Visualizes coverage trends."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.coverage_history_file = self.project_root / 'coverage_history.json'
        self.output_dir = self.project_root / 'coverage_charts'
        self.output_dir.mkdir(exist_ok=True)
    
    def load_coverage_history(self):
        """Load historical coverage data."""
        if not self.coverage_history_file.exists():
            print(f"No coverage history found at {self.coverage_history_file}")
            return []
        
        try:
            with open(self.coverage_history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading coverage history: {e}")
            return []
    
    def plot_coverage_trend(self, history):
        """Plot coverage trend over time."""
        if not HAS_MATPLOTLIB:
            return
        
        if len(history) < 2:
            print("Not enough data points to plot trend")
            return
        
        # Extract data
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in history]
        line_coverage = [entry['line_coverage'] for entry in history]
        branch_coverage = [entry['branch_coverage'] for entry in history]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(timestamps, line_coverage, marker='o', label='Line Coverage', linewidth=2)
        ax.plot(timestamps, branch_coverage, marker='s', label='Branch Coverage', linewidth=2)
        
        # Add threshold line
        ax.axhline(y=85, color='r', linestyle='--', label='Threshold (85%)', alpha=0.7)
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Coverage (%)', fontsize=12)
        ax.set_title('Test Coverage Trend Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45)
        
        # Set y-axis range
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        # Save plot
        output_file = self.output_dir / 'coverage_trend.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Coverage trend chart saved to {output_file}")
        
        plt.close()
    
    def plot_package_coverage(self, history):
        """Plot package-level coverage for latest run."""
        if not HAS_MATPLOTLIB:
            return
        
        if not history:
            print("No coverage data available")
            return
        
        latest = history[-1]
        packages = latest.get('packages', {})
        
        if not packages:
            print("No package data available")
            return
        
        # Extract data
        package_names = list(packages.keys())
        line_coverage = [packages[pkg]['line_coverage'] for pkg in package_names]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, max(6, len(package_names) * 0.4)))
        
        # Create horizontal bar chart
        y_pos = range(len(package_names))
        bars = ax.barh(y_pos, line_coverage)
        
        # Color bars based on coverage
        for i, (bar, cov) in enumerate(zip(bars, line_coverage)):
            if cov >= 90:
                bar.set_color('green')
            elif cov >= 80:
                bar.set_color('yellowgreen')
            elif cov >= 70:
                bar.set_color('yellow')
            else:
                bar.set_color('red')
        
        # Add threshold line
        ax.axvline(x=85, color='r', linestyle='--', label='Threshold (85%)', alpha=0.7)
        
        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels(package_names)
        ax.set_xlabel('Coverage (%)', fontsize=12)
        ax.set_title('Package-Level Coverage', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Set x-axis range
        ax.set_xlim(0, 100)
        
        # Add coverage values on bars
        for i, (bar, cov) in enumerate(zip(bars, line_coverage)):
            ax.text(cov + 1, i, f'{cov:.1f}%', va='center', fontsize=9)
        
        plt.tight_layout()
        
        # Save plot
        output_file = self.output_dir / 'package_coverage.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Package coverage chart saved to {output_file}")
        
        plt.close()
    
    def generate_html_report(self, history):
        """Generate HTML report with embedded charts."""
        if not history:
            print("No coverage data available")
            return
        
        latest = history[-1]
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Report - Stock Portfolio Platform</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-value.pass {{
            color: #10b981;
        }}
        .metric-value.fail {{
            color: #ef4444;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .chart-container h2 {{
            margin-top: 0;
            color: #333;
        }}
        .chart-container img {{
            width: 100%;
            height: auto;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Test Coverage Report</h1>
        <p>Stock Portfolio Management Platform</p>
        <p>Generated: {latest['timestamp']}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>Line Coverage</h3>
            <div class="metric-value {'pass' if latest['line_coverage'] >= 85 else 'fail'}">
                {latest['line_coverage']:.2f}%
            </div>
            <p>{'✓ Meets threshold' if latest['line_coverage'] >= 85 else '✗ Below threshold (85%)'}</p>
        </div>
        
        <div class="metric-card">
            <h3>Branch Coverage</h3>
            <div class="metric-value {'pass' if latest['branch_coverage'] >= 85 else 'fail'}">
                {latest['branch_coverage']:.2f}%
            </div>
            <p>{'✓ Meets threshold' if latest['branch_coverage'] >= 85 else '✗ Below threshold (85%)'}</p>
        </div>
        
        <div class="metric-card">
            <h3>Total Packages</h3>
            <div class="metric-value" style="color: #667eea;">
                {len(latest.get('packages', {}))}
            </div>
            <p>Tracked packages</p>
        </div>
    </div>
    
    <div class="chart-container">
        <h2>Coverage Trend Over Time</h2>
        <img src="coverage_trend.png" alt="Coverage Trend">
    </div>
    
    <div class="chart-container">
        <h2>Package-Level Coverage</h2>
        <img src="package_coverage.png" alt="Package Coverage">
    </div>
    
    <div class="footer">
        <p>For detailed line-by-line coverage, see <a href="../htmlcov/index.html">HTML Coverage Report</a></p>
    </div>
</body>
</html>
"""
        
        output_file = self.output_dir / 'index.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report saved to {output_file}")
    
    def run(self):
        """Run visualization."""
        history = self.load_coverage_history()
        
        if not history:
            print("No coverage history available. Run tests first.")
            return False
        
        print(f"Loaded {len(history)} coverage data points")
        
        # Generate visualizations
        self.plot_coverage_trend(history)
        self.plot_package_coverage(history)
        self.generate_html_report(history)
        
        print(f"\nVisualization complete! Open {self.output_dir}/index.html to view the report.")
        return True


def main():
    """Main entry point."""
    visualizer = CoverageVisualizer()
    success = visualizer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
