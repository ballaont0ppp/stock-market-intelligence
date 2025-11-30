"""
Run All Compatibility Tests
Executes all compatibility test suites and generates a comprehensive report
"""
import os
import sys
import time
from datetime import datetime
from test_browser_compatibility import BrowserCompatibilityTester
from test_os_compatibility import OSCompatibilityTester
from test_device_compatibility import DeviceCompatibilityTester
from test_network_compatibility import NetworkCompatibilityTester
from config import *


class CompatibilityTestRunner:
    """Run all compatibility tests and generate comprehensive report"""
    
    def __init__(self):
        self.results = {
            'browser': [],
            'os': [],
            'device': [],
            'network': []
        }
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self):
        """Run all compatibility test suites"""
        print(f"\n{'#'*70}")
        print(f"# COMPREHENSIVE COMPATIBILITY TESTING SUITE")
        print(f"# Application: {APP_NAME}")
        print(f"# URL: {APP_URL}")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}\n")
        
        self.start_time = time.time()
        
        # Run Browser Compatibility Tests
        print("\n" + "="*70)
        print("RUNNING BROWSER COMPATIBILITY TESTS")
        print("="*70)
        try:
            browser_tester = BrowserCompatibilityTester()
            self.results['browser'] = browser_tester.run_all_tests()
            browser_tester.generate_report()
            print("✓ Browser compatibility tests completed")
        except Exception as e:
            print(f"✗ Browser compatibility tests failed: {str(e)}")
        
        # Run OS Compatibility Tests
        print("\n" + "="*70)
        print("RUNNING OS COMPATIBILITY TESTS")
        print("="*70)
        try:
            os_tester = OSCompatibilityTester()
            self.results['os'] = [os_tester.run_os_tests()]
            os_tester.generate_report()
            print("✓ OS compatibility tests completed")
        except Exception as e:
            print(f"✗ OS compatibility tests failed: {str(e)}")
        
        # Run Device Compatibility Tests
        print("\n" + "="*70)
        print("RUNNING DEVICE COMPATIBILITY TESTS")
        print("="*70)
        try:
            device_tester = DeviceCompatibilityTester()
            self.results['device'] = device_tester.run_all_tests()
            device_tester.generate_report()
            print("✓ Device compatibility tests completed")
        except Exception as e:
            print(f"✗ Device compatibility tests failed: {str(e)}")
        
        # Run Network Compatibility Tests
        print("\n" + "="*70)
        print("RUNNING NETWORK COMPATIBILITY TESTS")
        print("="*70)
        try:
            network_tester = NetworkCompatibilityTester()
            self.results['network'] = network_tester.run_all_tests()
            network_tester.generate_report()
            print("✓ Network compatibility tests completed")
        except Exception as e:
            print(f"✗ Network compatibility tests failed: {str(e)}")
        
        self.end_time = time.time()
        
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        report_file = os.path.join(REPORTS_DIR, f'compatibility_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        # Calculate statistics
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        browser_passed = sum(1 for r in self.results['browser'] if r.get('status') == 'PASSED')
        browser_total = len(self.results['browser'])
        
        os_passed = sum(1 for r in self.results['os'] if r.get('status') == 'PASSED')
        os_total = len(self.results['os'])
        
        device_passed = sum(1 for r in self.results['device'] if r.get('status') == 'PASSED')
        device_total = len(self.results['device'])
        
        network_passed = sum(1 for r in self.results['network'] if r.get('status') == 'PASSED')
        network_total = len(self.results['network'])
        
        total_passed = browser_passed + os_passed + device_passed + network_passed
        total_tests = browser_total + os_total + device_total + network_total
        
        overall_status = 'PASSED' if total_passed == total_tests else 'FAILED'
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Compatibility Testing Summary Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 4px solid #007bff; padding-bottom: 15px; margin-bottom: 30px; }}
        h2 {{ color: #555; margin-top: 40px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
        .summary h2 {{ color: white; border: none; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .stat-card h3 {{ margin: 0 0 10px 0; color: #555; font-size: 0.9em; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2.5em; font-weight: bold; color: #007bff; margin: 10px 0; }}
        .stat-card .label {{ color: #666; font-size: 0.9em; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .section {{ background: #fff; padding: 20px; margin: 20px 0; border: 1px solid #ddd; border-radius: 8px; }}
        .section-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .badge {{ padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; }}
        .badge-success {{ background: #28a745; color: white; }}
        .badge-danger {{ background: #dc3545; color: white; }}
        .badge-warning {{ background: #ffc107; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; color: #555; }}
        tr:hover {{ background: #f8f9fa; }}
        .progress-bar {{ width: 100%; height: 30px; background: #e9ecef; border-radius: 15px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745 0%, #20c997 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 0.3s; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: rgba(255,255,255,0.9); }}
        .metric-value {{ font-size: 1.3em; color: white; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Comprehensive Compatibility Testing Report</h1>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="metric">
                <span class="metric-label">Application:</span>
                <span class="metric-value">{APP_NAME}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Test Date:</span>
                <span class="metric-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Duration:</span>
                <span class="metric-value">{int(total_duration // 60)}m {int(total_duration % 60)}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Overall Status:</span>
                <span class="metric-value" style="font-size: 1.5em;">
                    {('✓ PASSED' if overall_status == 'PASSED' else '✗ FAILED')}
                </span>
            </div>
        </div>
        
        <h2>Test Results Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Browser Compatibility</h3>
                <div class="value {('passed' if browser_passed == browser_total else 'failed')}">
                    {browser_passed}/{browser_total}
                </div>
                <div class="label">Browsers Passed</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(browser_passed/browser_total*100 if browser_total > 0 else 0):.0f}%">
                        {(browser_passed/browser_total*100 if browser_total > 0 else 0):.0f}%
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>OS Compatibility</h3>
                <div class="value {('passed' if os_passed == os_total else 'failed')}">
                    {os_passed}/{os_total}
                </div>
                <div class="label">Operating Systems Passed</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(os_passed/os_total*100 if os_total > 0 else 0):.0f}%">
                        {(os_passed/os_total*100 if os_total > 0 else 0):.0f}%
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Device Compatibility</h3>
                <div class="value {('passed' if device_passed == device_total else 'failed')}">
                    {device_passed}/{device_total}
                </div>
                <div class="label">Devices Passed</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(device_passed/device_total*100 if device_total > 0 else 0):.0f}%">
                        {(device_passed/device_total*100 if device_total > 0 else 0):.0f}%
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Network Compatibility</h3>
                <div class="value {('passed' if network_passed == network_total else 'failed')}">
                    {network_passed}/{network_total}
                </div>
                <div class="label">Network Conditions Passed</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(network_passed/network_total*100 if network_total > 0 else 0):.0f}%">
                        {(network_passed/network_total*100 if network_total > 0 else 0):.0f}%
                    </div>
                </div>
            </div>
        </div>
        
        <h2>Detailed Results</h2>
        
        <div class="section">
            <div class="section-header">
                <h3>🌐 Browser Compatibility</h3>
                <span class="badge {('badge-success' if browser_passed == browser_total else 'badge-danger')}">
                    {browser_passed}/{browser_total} Passed
                </span>
            </div>
            <table>
                <tr>
                    <th>Browser</th>
                    <th>Status</th>
                    <th>Tests Passed</th>
                    <th>Failed Tests</th>
                </tr>
"""
        
        for result in self.results['browser']:
            status = result.get('status', 'UNKNOWN')
            badge_class = 'badge-success' if status == 'PASSED' else 'badge-danger'
            html_content += f"""
                <tr>
                    <td>{result['browser'].upper()}</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                    <td>{result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)}</td>
                    <td>{result.get('failed_tests', 0)}</td>
                </tr>
"""
        
        html_content += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h3>💻 Operating System Compatibility</h3>
                <span class="badge {('badge-success' if os_passed == os_total else 'badge-danger')}">
                    {os_passed}/{os_total} Passed
                </span>
            </div>
            <table>
                <tr>
                    <th>Operating System</th>
                    <th>Status</th>
                    <th>Tests Passed</th>
                    <th>Failed Tests</th>
                </tr>
"""
        
        for result in self.results['os']:
            status = result.get('status', 'UNKNOWN')
            badge_class = 'badge-success' if status == 'PASSED' else 'badge-danger'
            os_info = result.get('os_info', {})
            html_content += f"""
                <tr>
                    <td>{os_info.get('system', 'Unknown')} {os_info.get('release', '')}</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                    <td>{result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)}</td>
                    <td>{result.get('failed_tests', 0)}</td>
                </tr>
"""
        
        html_content += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h3>📱 Device Compatibility</h3>
                <span class="badge {('badge-success' if device_passed == device_total else 'badge-danger')}">
                    {device_passed}/{device_total} Passed
                </span>
            </div>
            <table>
                <tr>
                    <th>Device</th>
                    <th>Resolution</th>
                    <th>Status</th>
                    <th>Tests Passed</th>
                </tr>
"""
        
        for result in self.results['device']:
            status = result.get('status', 'UNKNOWN')
            badge_class = 'badge-success' if status == 'PASSED' else 'badge-danger'
            html_content += f"""
                <tr>
                    <td>{result['device']}</td>
                    <td>{result['width']}x{result['height']}</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                    <td>{result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)}</td>
                </tr>
"""
        
        html_content += f"""
            </table>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h3>🌐 Network Compatibility</h3>
                <span class="badge {('badge-success' if network_passed == network_total else 'badge-danger')}">
                    {network_passed}/{network_total} Passed
                </span>
            </div>
            <table>
                <tr>
                    <th>Network Condition</th>
                    <th>Speed</th>
                    <th>Status</th>
                    <th>Tests Passed</th>
                </tr>
"""
        
        for result in self.results['network']:
            status = result.get('status', 'UNKNOWN')
            badge_class = 'badge-success' if status == 'PASSED' else 'badge-danger'
            config = result.get('config', {})
            html_content += f"""
                <tr>
                    <td>{result['network'].upper()}</td>
                    <td>↓{config.get('download', 0)} kbps / ↑{config.get('upload', 0)} kbps</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                    <td>{result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)}</td>
                </tr>
"""
        
        html_content += f"""
            </table>
        </div>
        
        <div class="footer">
            <p><strong>Stock Portfolio Management Platform</strong></p>
            <p>Compatibility Testing Suite v1.0</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n{'='*70}")
        print(f"Summary report generated: {report_file}")
        print(f"{'='*70}")
        
        return report_file
    
    def print_summary(self):
        """Print test summary to console"""
        print(f"\n{'='*70}")
        print("COMPATIBILITY TESTING SUMMARY")
        print(f"{'='*70}")
        
        print(f"\nBrowser Compatibility:")
        for result in self.results['browser']:
            status = result.get('status', 'UNKNOWN')
            symbol = '✓' if status == 'PASSED' else '✗'
            print(f"  {symbol} {result['browser'].upper()}: {status}")
        
        print(f"\nOS Compatibility:")
        for result in self.results['os']:
            status = result.get('status', 'UNKNOWN')
            symbol = '✓' if status == 'PASSED' else '✗'
            os_info = result.get('os_info', {})
            print(f"  {symbol} {os_info.get('system', 'Unknown')} {os_info.get('release', '')}: {status}")
        
        print(f"\nDevice Compatibility:")
        for result in self.results['device']:
            status = result.get('status', 'UNKNOWN')
            symbol = '✓' if status == 'PASSED' else '✗'
            print(f"  {symbol} {result['device']}: {status}")
        
        print(f"\nNetwork Compatibility:")
        for result in self.results['network']:
            status = result.get('status', 'UNKNOWN')
            symbol = '✓' if status == 'PASSED' else '✗'
            print(f"  {symbol} {result['network'].upper()}: {status}")
        
        print(f"\n{'='*70}")


def main():
    """Main execution"""
    runner = CompatibilityTestRunner()
    
    # Run all tests
    runner.run_all_tests()
    
    # Generate summary report
    runner.generate_summary_report()
    
    # Print summary
    runner.print_summary()
    
    # Determine exit code
    all_passed = all(
        all(r.get('status') == 'PASSED' for r in runner.results[category])
        for category in runner.results
        if runner.results[category]
    )
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
