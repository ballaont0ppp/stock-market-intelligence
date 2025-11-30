"""
Dependency Vulnerability Checker
Uses Safety and Snyk to check for known vulnerabilities
"""
import subprocess
import json
import time
import sys
from pathlib import Path

from config import SAFETY_CONFIG, SNYK_TOKEN, REPORTS_DIR, RESULTS_DIR
from utils import SecurityTestResult, ReportGenerator


class DependencyChecker:
    """Dependency vulnerability checker"""
    
    def __init__(self):
        self.result = SecurityTestResult("Dependency Vulnerability Check")
        self.project_root = Path(__file__).parent.parent
        self.requirements_file = self.project_root / 'requirements.txt'
    
    def run_safety_check(self):
        """Run Safety dependency check"""
        print("\n[1/2] Running Safety check...")
        
        if not self.requirements_file.exists():
            print(f"✗ Requirements file not found: {self.requirements_file}")
            return False
        
        cmd = [
            'safety',
            'check',
            '--file', str(self.requirements_file),
            '--json'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    self.process_safety_results(data)
                except json.JSONDecodeError:
                    # Safety might output plain text if no issues
                    if 'No known security vulnerabilities found' in result.stdout:
                        print("✓ No known vulnerabilities found")
                    else:
                        print(f"  Warning: Could not parse Safety output")
            
            return True
            
        except FileNotFoundError:
            print("✗ Safety not found. Install with: pip install safety")
            return False
            
        except Exception as e:
            print(f"✗ Safety check failed: {e}")
            return False
    
    def process_safety_results(self, data: list):
        """Process Safety JSON results"""
        if not data:
            print("✓ No known vulnerabilities found")
            return
        
        print(f"✓ Safety check complete. Found {len(data)} vulnerabilities")
        
        for vuln in data:
            # Determine severity based on CVE score if available
            severity = 'medium'
            if 'severity' in vuln:
                sev = vuln['severity'].lower()
                if sev in ['critical', 'high', 'medium', 'low']:
                    severity = sev
            
            package = vuln.get('package', 'unknown')
            installed = vuln.get('installed_version', 'unknown')
            affected = vuln.get('affected_versions', 'unknown')
            
            self.result.add_finding(
                severity=severity,
                title=f"Vulnerable Dependency: {package}",
                description=vuln.get('advisory', 'No description available'),
                recommendation=f"Upgrade {package} from {installed} to a safe version. Affected versions: {affected}",
                evidence=f"Package: {package}\nInstalled: {installed}\nVulnerable: {affected}",
                cwe=vuln.get('cve', 'N/A')
            )
    
    def run_snyk_check(self):
        """Run Snyk dependency check"""
        print("\n[2/2] Running Snyk check...")
        
        if not SNYK_TOKEN:
            print("  Skipping Snyk (no token configured)")
            return True
        
        # Check if Snyk CLI is installed
        try:
            subprocess.run(['snyk', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("  Skipping Snyk (CLI not installed)")
            print("  Install with: npm install -g snyk")
            return True
        
        # Authenticate
        try:
            subprocess.run(
                ['snyk', 'auth', SNYK_TOKEN],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"  Warning: Snyk authentication failed: {e}")
            return True
        
        # Run Snyk test
        cmd = ['snyk', 'test', '--json']
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    self.process_snyk_results(data)
                except json.JSONDecodeError:
                    print("  Warning: Could not parse Snyk output")
            
            return True
            
        except Exception as e:
            print(f"  Warning: Snyk check failed: {e}")
            return True
    
    def process_snyk_results(self, data: dict):
        """Process Snyk JSON results"""
        vulnerabilities = data.get('vulnerabilities', [])
        
        if not vulnerabilities:
            print("✓ No vulnerabilities found by Snyk")
            return
        
        print(f"✓ Snyk check complete. Found {len(vulnerabilities)} vulnerabilities")
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium').lower()
            
            package = vuln.get('packageName', 'unknown')
            version = vuln.get('version', 'unknown')
            
            self.result.add_finding(
                severity=severity,
                title=f"Snyk: {vuln.get('title', 'Vulnerability')}",
                description=vuln.get('description', 'No description available'),
                recommendation=vuln.get('remediation', 'Update to latest version'),
                evidence=f"Package: {package}\nVersion: {version}\nCVSS Score: {vuln.get('cvssScore', 'N/A')}",
                cwe=vuln.get('identifiers', {}).get('CVE', ['N/A'])[0]
            )
    
    def run_scan(self):
        """Run complete dependency check"""
        start_time = time.time()
        
        print("=" * 70)
        print("Dependency Vulnerability Check")
        print("=" * 70)
        
        # Run checks
        safety_ok = self.run_safety_check()
        snyk_ok = self.run_snyk_check()
        
        if safety_ok and snyk_ok:
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
        print(f"  Critical: {self.result.summary['critical']}")
        print(f"  High: {self.result.summary['high']}")
        print(f"  Medium: {self.result.summary['medium']}")
        print(f"  Low: {self.result.summary['low']}")
        
        return self.result


def main():
    """Main execution"""
    checker = DependencyChecker()
    result = checker.run_scan()
    
    # Save results
    print("\nSaving results...")
    json_path = result.save_json('dependency_check.json')
    print(f"✓ JSON results saved: {json_path}")
    
    # Generate report
    report_path = ReportGenerator.generate_report(result, 'dependency_report.html')
    print(f"✓ HTML report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("Dependency check complete!")
    print("=" * 70)
    
    # Exit with error code if critical/high findings
    if result.summary['critical'] > 0 or result.summary['high'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
