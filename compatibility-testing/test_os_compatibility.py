"""
Operating System Compatibility Testing
Tests the application across different operating systems
"""
import os
import sys
import platform
import subprocess
import json
from datetime import datetime
from config import *


class OSCompatibilityTester:
    """Test application compatibility across different operating systems"""
    
    def __init__(self):
        self.results = []
        self.current_os = self.detect_os()
        
    def detect_os(self):
        """Detect current operating system"""
        system = platform.system()
        release = platform.release()
        version = platform.version()
        
        return {
            'system': system,
            'release': release,
            'version': version,
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def test_python_compatibility(self):
        """Test Python version compatibility"""
        try:
            version_info = sys.version_info
            python_version = f"{version_info.major}.{version_info.minor}.{version_info.patch}"
            
            # Check minimum Python version (3.8+)
            is_compatible = version_info.major == 3 and version_info.minor >= 8
            
            return {
                'success': is_compatible,
                'python_version': python_version,
                'version_info': {
                    'major': version_info.major,
                    'minor': version_info.minor,
                    'patch': version_info.patch
                },
                'executable': sys.executable,
                'compatible': is_compatible
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_dependencies(self):
        """Test if all required dependencies are available"""
        try:
            import flask
            import sqlalchemy
            import pandas
            import numpy
            import tensorflow
            
            dependencies = {
                'flask': flask.__version__,
                'sqlalchemy': sqlalchemy.__version__,
                'pandas': pandas.__version__,
                'numpy': numpy.__version__,
                'tensorflow': tensorflow.__version__
            }
            
            return {
                'success': True,
                'dependencies': dependencies,
                'all_available': True
            }
        except ImportError as e:
            return {
                'success': False,
                'error': f"Missing dependency: {str(e)}",
                'all_available': False
            }
    
    def test_file_system(self):
        """Test file system operations"""
        try:
            # Test directory creation
            test_dir = os.path.join(RESULTS_DIR, 'os_test_temp')
            os.makedirs(test_dir, exist_ok=True)
            
            # Test file write
            test_file = os.path.join(test_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            # Test file read
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Test file delete
            os.remove(test_file)
            os.rmdir(test_dir)
            
            return {
                'success': True,
                'can_create_directory': True,
                'can_write_file': True,
                'can_read_file': content == 'test content',
                'can_delete_file': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_network_connectivity(self):
        """Test network connectivity"""
        try:
            import requests
            
            # Test connection to application
            response = requests.get(APP_URL, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'can_connect': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'can_connect': False
            }
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            # This would need actual database credentials
            # For now, we'll just check if the driver is available
            import pymysql
            
            return {
                'success': True,
                'driver_available': True,
                'driver_version': pymysql.__version__
            }
        except ImportError:
            return {
                'success': False,
                'driver_available': False,
                'error': 'MySQL driver not available'
            }
    
    def test_process_management(self):
        """Test process management capabilities"""
        try:
            import psutil
            
            # Get system info
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'success': True,
                'cpu_count': cpu_count,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_percent': memory.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_percent': disk.percent
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_environment_variables(self):
        """Test environment variable access"""
        try:
            # Check if .env file exists
            env_file = os.path.join(os.path.dirname(BASE_DIR), '.env')
            env_file_exists = os.path.exists(env_file)
            
            # Check key environment variables
            required_vars = [
                'FLASK_APP',
                'FLASK_ENV',
                'DATABASE_URL',
                'SECRET_KEY'
            ]
            
            available_vars = {var: os.getenv(var) is not None for var in required_vars}
            
            return {
                'success': True,
                'env_file_exists': env_file_exists,
                'required_vars': available_vars,
                'all_vars_set': all(available_vars.values())
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_command_execution(self):
        """Test command execution capabilities"""
        try:
            # Test basic command execution
            if self.current_os['system'] == 'Windows':
                result = subprocess.run(['cmd', '/c', 'echo', 'test'], 
                                      capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(['echo', 'test'], 
                                      capture_output=True, text=True, timeout=5)
            
            return {
                'success': result.returncode == 0,
                'can_execute_commands': result.returncode == 0,
                'output': result.stdout.strip()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_path_handling(self):
        """Test path handling across OS"""
        try:
            # Test path operations
            test_path = os.path.join('test', 'path', 'file.txt')
            normalized_path = os.path.normpath(test_path)
            absolute_path = os.path.abspath(test_path)
            
            # Test path separator
            separator = os.sep
            
            return {
                'success': True,
                'path_separator': separator,
                'test_path': test_path,
                'normalized_path': normalized_path,
                'can_handle_paths': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_permissions(self):
        """Test file permissions"""
        try:
            # Test if we can check permissions
            test_file = __file__
            can_read = os.access(test_file, os.R_OK)
            can_write = os.access(test_file, os.W_OK)
            can_execute = os.access(test_file, os.X_OK)
            
            return {
                'success': True,
                'can_read': can_read,
                'can_write': can_write,
                'can_execute': can_execute,
                'permissions_work': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_os_tests(self):
        """Run all OS compatibility tests"""
        print(f"\n{'='*60}")
        print(f"Testing {self.current_os['system']} {self.current_os['release']}")
        print(f"{'='*60}")
        
        test_results = {
            'os_info': self.current_os,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Run all tests
        tests = [
            ('Python Compatibility', self.test_python_compatibility),
            ('Dependencies', self.test_dependencies),
            ('File System', self.test_file_system),
            ('Network Connectivity', self.test_network_connectivity),
            ('Database Connectivity', self.test_database_connectivity),
            ('Process Management', self.test_process_management),
            ('Environment Variables', self.test_environment_variables),
            ('Command Execution', self.test_command_execution),
            ('Path Handling', self.test_path_handling),
            ('Permissions', self.test_permissions)
        ]
        
        for test_name, test_func in tests:
            print(f"  Testing {test_name}...")
            try:
                test_results['tests'][test_name] = test_func()
            except Exception as e:
                test_results['tests'][test_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Calculate overall status
        failed_tests = sum(1 for test in test_results['tests'].values() 
                         if not test.get('success', False))
        test_results['status'] = 'PASSED' if failed_tests == 0 else 'FAILED'
        test_results['failed_tests'] = failed_tests
        test_results['total_tests'] = len(test_results['tests'])
        
        self.results.append(test_results)
        return test_results
    
    def generate_report(self):
        """Generate HTML report"""
        report_file = os.path.join(REPORTS_DIR, f'os_compatibility_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OS Compatibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #28a745; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .os-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        .test-result {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #28a745; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 1.2em; color: #28a745; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Operating System Compatibility Test Report</h1>
        <div class="summary">
            <h2>Test Summary</h2>
            <div class="metric">
                <span class="metric-label">Application:</span>
                <span class="metric-value">{APP_NAME}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Date:</span>
                <span class="metric-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
"""
        
        for result in self.results:
            os_info = result['os_info']
            html_content += f"""
            <div class="metric">
                <span class="metric-label">Operating System:</span>
                <span class="metric-value">{os_info['system']} {os_info['release']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Platform:</span>
                <span class="metric-value">{os_info['platform']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value {('passed' if result.get('status') == 'PASSED' else 'failed')}">
                    {result.get('status', 'UNKNOWN')}
                </span>
            </div>
        </div>
        
        <div class="os-section">
            <h2>System Information</h2>
            <table>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>System</td>
                    <td>{os_info['system']}</td>
                </tr>
                <tr>
                    <td>Release</td>
                    <td>{os_info['release']}</td>
                </tr>
                <tr>
                    <td>Version</td>
                    <td>{os_info['version']}</td>
                </tr>
                <tr>
                    <td>Machine</td>
                    <td>{os_info['machine']}</td>
                </tr>
                <tr>
                    <td>Processor</td>
                    <td>{os_info['processor']}</td>
                </tr>
                <tr>
                    <td>Python Version</td>
                    <td>{os_info['python_version']}</td>
                </tr>
            </table>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
"""
            
            for test_name, test_data in result['tests'].items():
                test_status = 'PASSED' if test_data.get('success', False) else 'FAILED'
                test_class = 'passed' if test_status == 'PASSED' else 'failed'
                details = json.dumps(test_data, indent=2)
                
                html_content += f"""
                <tr>
                    <td>{test_name}</td>
                    <td class="{test_class}">{test_status}</td>
                    <td><pre style="font-size: 0.8em; max-height: 150px; overflow: auto;">{details}</pre></td>
                </tr>
"""
            
            html_content += """
            </table>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"\nReport generated: {report_file}")
        return report_file


def main():
    """Main test execution"""
    tester = OSCompatibilityTester()
    
    # Run tests
    results = tester.run_os_tests()
    
    # Generate report
    report_file = tester.generate_report()
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Operating System: {results['os_info']['system']} {results['os_info']['release']}")
    print(f"Status: {results['status']}")
    print(f"Tests Passed: {results['total_tests'] - results['failed_tests']}/{results['total_tests']}")
    print(f"{'='*60}")
    print(f"Report: {report_file}")
    
    # Return exit code
    return 0 if results['status'] == 'PASSED' else 1


if __name__ == '__main__':
    exit(main())
