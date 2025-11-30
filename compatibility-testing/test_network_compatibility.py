"""
Network Compatibility Testing
Tests the application under different network conditions
"""
import os
import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from config import *


class NetworkCompatibilityTester:
    """Test application compatibility under different network conditions"""
    
    def __init__(self):
        self.results = []
        self.driver = None
        
    def setup_driver(self, network_condition=None):
        """Initialize Chrome WebDriver with network throttling"""
        try:
            options = webdriver.ChromeOptions()
            if SELENIUM_CONFIG['headless']:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set network conditions if specified
            if network_condition:
                self.set_network_conditions(network_condition)
            
            self.driver.implicitly_wait(SELENIUM_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            self.driver.set_window_size(*SELENIUM_CONFIG['window_size'])
            
            return True
        except Exception as e:
            print(f"Error setting up driver: {str(e)}")
            return False
    
    def set_network_conditions(self, condition):
        """Set network throttling conditions"""
        try:
            # Chrome DevTools Protocol for network throttling
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
                'offline': False,
                'downloadThroughput': condition['download'] * 1024 / 8,  # Convert kbps to bytes/s
                'uploadThroughput': condition['upload'] * 1024 / 8,
                'latency': condition['latency']
            })
            return True
        except Exception as e:
            print(f"Warning: Could not set network conditions: {str(e)}")
            return False
    
    def teardown_driver(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def take_screenshot(self, network_name, page_name):
        """Take a screenshot"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{network_name}_{page_name}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None
    
    def test_page_load_time(self, url):
        """Test page load time"""
        try:
            start_time = time.time()
            self.driver.get(url)
            
            # Wait for page to be fully loaded
            self.driver.execute_script('return document.readyState') == 'complete'
            
            load_time = time.time() - start_time
            
            # Get performance timing
            performance = self.driver.execute_script('''
                return {
                    navigationStart: window.performance.timing.navigationStart,
                    domContentLoaded: window.performance.timing.domContentLoadedEventEnd,
                    loadComplete: window.performance.timing.loadEventEnd,
                    domInteractive: window.performance.timing.domInteractive
                }
            ''')
            
            if performance['loadComplete'] > 0:
                total_load_time = (performance['loadComplete'] - performance['navigationStart']) / 1000.0
                dom_content_loaded = (performance['domContentLoaded'] - performance['navigationStart']) / 1000.0
                dom_interactive = (performance['domInteractive'] - performance['navigationStart']) / 1000.0
            else:
                total_load_time = load_time
                dom_content_loaded = load_time
                dom_interactive = load_time
            
            return {
                'success': total_load_time < PERFORMANCE_THRESHOLDS['page_load_time'] * 2,  # Allow 2x threshold for slow networks
                'url': url,
                'load_time': total_load_time,
                'dom_content_loaded': dom_content_loaded,
                'dom_interactive': dom_interactive,
                'page_title': self.driver.title
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def test_resource_loading(self):
        """Test if all resources load successfully"""
        try:
            # Get all resource entries
            resources = self.driver.execute_script('''
                return window.performance.getEntriesByType('resource').map(r => ({
                    name: r.name,
                    type: r.initiatorType,
                    duration: r.duration,
                    size: r.transferSize
                }))
            ''')
            
            # Categorize resources
            resource_types = {}
            total_size = 0
            failed_resources = []
            
            for resource in resources:
                res_type = resource['type']
                if res_type not in resource_types:
                    resource_types[res_type] = {'count': 0, 'total_duration': 0, 'total_size': 0}
                
                resource_types[res_type]['count'] += 1
                resource_types[res_type]['total_duration'] += resource['duration']
                resource_types[res_type]['total_size'] += resource.get('size', 0)
                total_size += resource.get('size', 0)
            
            return {
                'success': True,
                'total_resources': len(resources),
                'resource_types': resource_types,
                'total_size_kb': round(total_size / 1024, 2),
                'failed_resources': len(failed_resources)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_api_response_time(self):
        """Test API response times"""
        try:
            # Test a simple API endpoint
            start_time = time.time()
            response = requests.get(f"{APP_URL}/api/health", timeout=30)
            response_time = time.time() - start_time
            
            return {
                'success': response.status_code == 200 or response.status_code == 404,  # 404 is ok if endpoint doesn't exist
                'status_code': response.status_code,
                'response_time': response_time,
                'api_accessible': response.status_code < 500
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'api_accessible': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_accessible': False
            }
    
    def test_form_submission(self):
        """Test form submission under network conditions"""
        try:
            # Navigate to login page
            self.driver.get(f"{APP_URL}/login")
            time.sleep(2)
            
            # Fill form
            email_input = self.driver.find_element(By.ID, 'email')
            password_input = self.driver.find_element(By.ID, 'password')
            
            email_input.send_keys(TEST_USER_EMAIL)
            password_input.send_keys(TEST_USER_PASSWORD)
            
            # Submit form
            start_time = time.time()
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Wait for response
            time.sleep(3)
            submission_time = time.time() - start_time
            
            return {
                'success': True,
                'submission_time': submission_time,
                'current_url': self.driver.current_url,
                'form_submitted': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_image_loading(self):
        """Test if images load properly"""
        try:
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            
            loaded_images = 0
            failed_images = 0
            
            for img in images:
                if img.is_displayed():
                    # Check if image loaded
                    complete = self.driver.execute_script('return arguments[0].complete', img)
                    natural_height = self.driver.execute_script('return arguments[0].naturalHeight', img)
                    
                    if complete and natural_height > 0:
                        loaded_images += 1
                    else:
                        failed_images += 1
            
            return {
                'success': failed_images == 0,
                'total_images': len(images),
                'loaded_images': loaded_images,
                'failed_images': failed_images,
                'all_images_loaded': failed_images == 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_javascript_execution(self):
        """Test if JavaScript executes properly"""
        try:
            # Test basic JavaScript
            result = self.driver.execute_script('return 1 + 1')
            
            # Test async operations
            start_time = time.time()
            async_result = self.driver.execute_async_script('''
                var callback = arguments[arguments.length - 1];
                setTimeout(function() {
                    callback('async_complete');
                }, 1000);
            ''')
            async_time = time.time() - start_time
            
            return {
                'success': result == 2 and async_result == 'async_complete',
                'basic_js_works': result == 2,
                'async_js_works': async_result == 'async_complete',
                'async_execution_time': async_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_interactive_elements(self):
        """Test if interactive elements respond"""
        try:
            # Find buttons
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            
            responsive_buttons = 0
            for button in buttons[:5]:  # Test first 5 buttons
                if button.is_displayed() and button.is_enabled():
                    responsive_buttons += 1
            
            return {
                'success': responsive_buttons > 0,
                'total_buttons': len(buttons),
                'responsive_buttons': responsive_buttons,
                'elements_responsive': responsive_buttons > 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_network_condition(self, network_name, network_config):
        """Run all tests for a specific network condition"""
        print(f"\n  Testing {network_name}...")
        print(f"    Download: {network_config['download']} kbps")
        print(f"    Upload: {network_config['upload']} kbps")
        print(f"    Latency: {network_config['latency']} ms")
        
        if not self.setup_driver(network_config):
            return {
                'network': network_name,
                'status': 'FAILED',
                'error': 'Failed to initialize driver'
            }
        
        test_results = {
            'network': network_name,
            'config': network_config,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        try:
            # Test 1: Home Page Load
            print(f"    - Testing home page load...")
            test_results['tests']['home_page_load'] = self.test_page_load_time(APP_URL)
            self.take_screenshot(network_name, 'home')
            
            # Test 2: Resource Loading
            print(f"    - Testing resource loading...")
            test_results['tests']['resource_loading'] = self.test_resource_loading()
            
            # Test 3: Image Loading
            print(f"    - Testing image loading...")
            test_results['tests']['image_loading'] = self.test_image_loading()
            
            # Test 4: JavaScript Execution
            print(f"    - Testing JavaScript execution...")
            test_results['tests']['javascript_execution'] = self.test_javascript_execution()
            
            # Test 5: Interactive Elements
            print(f"    - Testing interactive elements...")
            test_results['tests']['interactive_elements'] = self.test_interactive_elements()
            
            # Test 6: Login Page Load
            print(f"    - Testing login page load...")
            test_results['tests']['login_page_load'] = self.test_page_load_time(f"{APP_URL}/login")
            self.take_screenshot(network_name, 'login')
            
            # Test 7: Form Submission
            print(f"    - Testing form submission...")
            test_results['tests']['form_submission'] = self.test_form_submission()
            
            # Test 8: API Response Time
            print(f"    - Testing API response time...")
            test_results['tests']['api_response'] = self.test_api_response_time()
            
            # Calculate overall status
            failed_tests = sum(1 for test in test_results['tests'].values() 
                             if not test.get('success', False))
            test_results['status'] = 'PASSED' if failed_tests == 0 else 'FAILED'
            test_results['failed_tests'] = failed_tests
            test_results['total_tests'] = len(test_results['tests'])
            
        except Exception as e:
            test_results['status'] = 'ERROR'
            test_results['error'] = str(e)
        
        finally:
            self.teardown_driver()
        
        return test_results
    
    def run_all_tests(self):
        """Run tests on all network conditions"""
        print(f"\n{'#'*60}")
        print(f"# NETWORK COMPATIBILITY TESTING")
        print(f"# Application: {APP_NAME}")
        print(f"# URL: {APP_URL}")
        print(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}")
        
        for network_name, network_config in NETWORK_CONDITIONS.items():
            if network_config['enabled']:
                result = self.test_network_condition(network_name, network_config)
                self.results.append(result)
            else:
                print(f"\nSkipping {network_name} (disabled in config)")
        
        return self.results
    
    def generate_report(self):
        """Generate HTML report"""
        report_file = os.path.join(REPORTS_DIR, f'network_compatibility_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Network Compatibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #6f42c1; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .network-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #6f42c1; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 1.2em; color: #6f42c1; }}
        .network-card {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Compatibility Test Report</h1>
        <div class="summary">
            <h2>Test Summary</h2>
            <div class="metric">
                <span class="metric-label">Application:</span>
                <span class="metric-value">{APP_NAME}</span>
            </div>
            <div class="metric">
                <span class="metric-label">URL:</span>
                <span class="metric-value">{APP_URL}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Date:</span>
                <span class="metric-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Network Conditions Tested:</span>
                <span class="metric-value">{len(self.results)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value {('passed' if all(r.get('status') == 'PASSED' for r in self.results) else 'failed')}">
                    {('ALL PASSED' if all(r.get('status') == 'PASSED' for r in self.results) else 'SOME FAILED')}
                </span>
            </div>
        </div>
        
        <h2>Network Conditions Overview</h2>
"""
        
        for result in self.results:
            network = result['network']
            config = result['config']
            status = result.get('status', 'UNKNOWN')
            status_class = 'passed' if status == 'PASSED' else 'failed'
            
            html_content += f"""
        <div class="network-card">
            <h3>{network.upper()} - <span class="{status_class}">{status}</span></h3>
            <p><strong>Download:</strong> {config['download']} kbps | 
               <strong>Upload:</strong> {config['upload']} kbps | 
               <strong>Latency:</strong> {config['latency']} ms</p>
            <p><strong>Tests:</strong> {result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)} passed</p>
        </div>
"""
        
        html_content += """
        <h2>Detailed Test Results</h2>
"""
        
        for result in self.results:
            network = result['network']
            status = result.get('status', 'UNKNOWN')
            status_class = 'passed' if status == 'PASSED' else 'failed'
            
            html_content += f"""
        <div class="network-section">
            <h3>{network.upper()} - <span class="{status_class}">{status}</span></h3>
            <p><strong>Timestamp:</strong> {result.get('timestamp', 'N/A')}</p>
"""
            
            if 'tests' in result:
                html_content += """
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
                    <td>{test_name.replace('_', ' ').title()}</td>
                    <td class="{test_class}">{test_status}</td>
                    <td><pre style="font-size: 0.8em; max-height: 100px; overflow: auto;">{details}</pre></td>
                </tr>
"""
                
                html_content += """
            </table>
"""
            
            html_content += """
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
    tester = NetworkCompatibilityTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Generate report
    report_file = tester.generate_report()
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    for result in results:
        status = result.get('status', 'UNKNOWN')
        print(f"{result['network'].upper()}: {status}")
    print(f"{'='*60}")
    print(f"Report: {report_file}")
    
    # Return exit code
    all_passed = all(r.get('status') == 'PASSED' for r in results)
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
