"""
Bandit Static Code Analysis
Scans Python code for security vulnerabilities
"""
import subprocess
import json
import time
import sys
from pathlib import Path

from config import BANDIT_CONFIG, REPORTS_DIR, RESULTS_DIR
from utils import SecurityTestResult, ReportGenerator


class BanditScanner:
    """Bandit static code analysis scanner"""
    
    def __init__(self):
        self.result = SecurityTestResult("Static Code Analysis (Bandit)")
        self.project_root = Path(__file__).parent.parent
    
    def run_bandit(self):
        """Run Bandit security linter"""
        print("=" * 70)
        print("Bandit Static Code Analysis")
        print("=" * 70)
        
        print(f"\nScanning project: {self.project_root}")
        print(f"Severity level: {BANDIT_CONFIG['severity_level']}")
        print(f"Confidence level: {BANDIT_CONFIG['confidence_level']}")
        
        # Build Bandit command
        cmd = [
            'bandit',
            '-r', str(self.project_root),
            '-f', 'json',
            '-ll',  # Low severity and confidence
            '--exclude', ','.join(BANDIT_CONFIG['exclude_dirs'])
        ]
        
        print(f"\nRunning Bandit scan...")
        
        try:
            # Run Bandit
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse JSON output
            if result.stdout:
                data = json.loads(result.stdout)
                self.process_bandit_results(data)
            else:
                print("✓ No security issues found")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("✗ Bandit scan timed out")
            self.result.add_finding(
                severity='high',
                title='Scan Timeout',
                description='Bandit scan exceeded timeout limit',
                recommendation='Review project size and exclude unnecessary directories'
            )
            return False
            
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse Bandit output: {e}")
            return False
            
        except FileNotFoundError:
            print("✗ Bandit not found. Please install: pip install bandit")
            return False
            
        except Exception as e:
            print(f"✗ Bandit scan failed: {e}")
            return False
    
    def process_bandit_results(self, data: dict):
        """Process Bandit JSON results"""
        results = data.get('results', [])
        
        print(f"✓ Scan complete. Found {len(results)} issues")
        
        # Severity mapping
        severity_map = {
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        
        for issue in results:
            severity = severity_map.get(
                issue.get('issue_severity', 'LOW'),
                'low'
            )
            
            # Upgrade to critical if high severity and high confidence
            if severity == 'high' and issue.get('issue_confidence') == 'HIGH':
                severity = 'critical'
            
            filename = issue.get('filename', 'unknown')
            line_number = issue.get('line_number', 0)
            code = issue.get('code', '')
            
            self.result.add_finding(
                severity=severity,
                title=issue.get('test_name', 'Unknown Issue'),
                description=issue.get('issue_text', ''),
                recommendation=issue.get('more_info', ''),
                evidence=f"File: {filename}\nLine: {line_number}\n\nCode:\n{code}",
                cwe=issue.get('test_id', '')
            )
        
        # Print summary by severity
        print(f"\nFindings by severity:")
        print(f"  Critical: {self.result.summary['critical']}")
        print(f"  High: {self.result.summary['high']}")
        print(f"  Medium: {self.result.summary['medium']}")
        print(f"  Low: {self.result.summary['low']}")
    
    def run_scan(self):
        """Run complete static code analysis"""
        start_time = time.time()
        
        success = self.run_bandit()
        
        if success:
            self.result.set_status('completed')
        else:
            self.result.set_status('failed')
        
        duration = time.time() - start_time
        self.result.set_duration(duration)
        
        print("\n" + "=" * 70)
        print("Scan Summary")
        print("=" * 70)
        print(f"Status: {self.result.status.upper()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Total Findings: {self.result.summary['total']}")
        
        return self.result


def main():
    """Main execution"""
    scanner = BanditScanner()
    result = scanner.run_scan()
    
    # Save results
    print("\nSaving results...")
    json_path = result.save_json('bandit_scan.json')
    print(f"✓ JSON results saved: {json_path}")
    
    # Generate report
    report_path = ReportGenerator.generate_report(result, 'bandit_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("Static code analysis complete!")
    print("=" * 70)
    
    # Exit with error code if critical/high findings
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
