"""
Browser Compatibility Testing
Tests the application across different browsers and versions
"""
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config import *


class BrowserCompatibilityTester:
    """Test application compatibility across different browsers"""
    
    def __init__(self):
        self.results = []
        self.current_browser = None
        self.driver = None
        
    def setup_driver(self, browser_name, version='latest'):
        """Initialize WebDriver for specified browser"""
        try:
            if browser_name == 'chrome':
                options = webdriver.ChromeOptions()
                if SELENIUM_CONFIG['headless']:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--window-size={SELENIUM_CONFIG["window_size"][0]},{SELENIUM_CONFIG["window_size"][1]}')
                
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif browser_name == 'firefox':
                options = webdriver.FirefoxOptions()
                if SELENIUM_CONFIG['headless']:
                    options.add_argument('--headless')
                options.add_argument(f'--width={SELENIUM_CONFIG["window_size"][0]}')
                options.add_argument(f'--height={SELENIUM_CONFIG["window_size"][1]}')
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                
            elif browser_name == 'edge':
                options = webdriver.EdgeOptions()
                if SELENIUM_CONFIG['headless']:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--window-size={SELENIUM_CONFIG["window_size"][0]},{SELENIUM_CONFIG["window_size"][1]}')
                
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
                
            elif browser_name == 'safari':
                # Safari driver is built-in on macOS
                self.driver = webdriver.Safari()
                self.driver.set_window_size(*SELENIUM_CONFIG['window_size'])
            
            # Set timeouts
            self.driver.implicitly_wait(SELENIUM_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            self.driver.set_script_timeout(SELENIUM_CONFIG['script_timeout'])
            
            self.current_browser = browser_name
            return True
            
        except Exception as e:
            print(f"Error setting up {browser_name}: {str(e)}")
            return False
    
    def teardown_driver(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def take_screenshot(self, test_name):
        """Take a screenshot of the current page"""
        if not self.driver:
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{test_name}_{self.current_browser}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None
    
    def get_console_logs(self):
        """Get browser console logs"""
        if not self.driver or self.current_browser == 'firefox':
            return []
        
        try:
            logs = self.driver.get_log('browser')
            return [{'level': log['level'], 'message': log['message']} for log in logs]
        except:
            return []
    
    def test_page_load(self, url):
        """Test if page loads successfully"""
        try:
            start_time = time.time()
            self.driver.get(url)
            load_time = time.time() - start_time
            
            # Check if page loaded
            page_state = self.driver.execute_script('return document.readyState')
            
            return {
                'success': page_state == 'complete',
                'load_time': load_time,
                'url': url,
                'title': self.driver.title,
                'console_errors': [log for log in self.get_console_logs() if log['level'] == 'SEVERE']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def test_element_visibility(self, selectors):
        """Test if key elements are visible"""
        results = {}
        for name, selector in selectors.items():
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                results[name] = {
                    'visible': element.is_displayed(),
                    'enabled': element.is_enabled()
                }
            except Exception as e:
                results[name] = {
                    'visible': False,
                    'error': str(e)
                }
        return results
    
    def test_form_submission(self, form_data):
        """Test form submission"""
        try:
            # Fill form fields
            for field_id, value in form_data.items():
                element = self.driver.find_element(By.ID, field_id)
                element.clear()
                element.send_keys(value)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Wait for response
            time.sleep(2)
            
            return {
                'success': True,
                'current_url': self.driver.current_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_javascript_execution(self):
        """Test if JavaScript executes correctly"""
        try:
            # Test basic JavaScript
            result = self.driver.execute_script('return 1 + 1')
            
            # Test jQuery if available
            jquery_available = self.driver.execute_script('return typeof jQuery !== "undefined"')
            
            # Test custom functions
            custom_functions = self.driver.execute_script('''
                return {
                    hasStockAutocomplete: typeof window.initStockAutocomplete === 'function',
                    hasChartJS: typeof Chart !== 'undefined'
                }
            ''')
            
            return {
                'success': result == 2,
                'jquery_available': jquery_available,
                'custom_functions': custom_functions
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_css_rendering(self):
        """Test if CSS is applied correctly"""
        try:
            # Check if Bootstrap is loaded
            body = self.driver.find_element(By.TAG_NAME, 'body')
            font_family = body.value_of_css_property('font-family')
            
            # Check if custom CSS is loaded
            navbar = self.driver.find_element(By.CSS_SELECTOR, '.navbar')
            navbar_bg = navbar.value_of_css_property('background-color')
            
            return {
                'success': True,
                'font_family': font_family,
                'navbar_background': navbar_bg,
                'bootstrap_loaded': 'system-ui' in font_family or 'Segoe UI' in font_family
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_responsive_design(self, width, height):
        """Test responsive design at specific resolution"""
        try:
            self.driver.set_window_size(width, height)
            time.sleep(1)  # Wait for resize
            
            # Check if mobile menu is visible on small screens
            viewport_width = self.driver.execute_script('return window.innerWidth')
            
            # Check if elements adapt
            body_width = self.driver.execute_script('return document.body.scrollWidth')
            has_horizontal_scroll = body_width > viewport_width
            
            return {
                'success': True,
                'viewport_width': viewport_width,
                'viewport_height': height,
                'has_horizontal_scroll': has_horizontal_scroll,
                'mobile_menu_visible': viewport_width < 768
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_browser_tests(self, browser_name):
        """Run all tests for a specific browser"""
        print(f"\n{'='*60}")
        print(f"Testing {browser_name.upper()}")
        print(f"{'='*60}")
        
        if not self.setup_driver(browser_name):
            return {
                'browser': browser_name,
                'status': 'FAILED',
                'error': 'Failed to initialize browser driver'
            }
        
        test_results = {
            'browser': browser_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        try:
            # Test 1: Home Page Load
            print(f"  Testing home page load...")
            test_results['tests']['home_page'] = self.test_page_load(APP_URL)
            self.take_screenshot('home_page')
            
            # Test 2: Login Page
            print(f"  Testing login page...")
            test_results['tests']['login_page'] = self.test_page_load(f"{APP_URL}/login")
            self.take_screenshot('login_page')
            
            # Test 3: Element Visibility
            print(f"  Testing element visibility...")
            key_elements = {
                'navbar': '.navbar',
                'login_form': 'form',
                'email_input': '#email',
                'password_input': '#password',
                'submit_button': 'button[type="submit"]'
            }
            test_results['tests']['element_visibility'] = self.test_element_visibility(key_elements)
            
            # Test 4: JavaScript Execution
            print(f"  Testing JavaScript execution...")
            test_results['tests']['javascript'] = self.test_javascript_execution()
            
            # Test 5: CSS Rendering
            print(f"  Testing CSS rendering...")
            test_results['tests']['css_rendering'] = self.test_css_rendering()
            
            # Test 6: Responsive Design
            print(f"  Testing responsive design...")
            responsive_tests = {}
            for resolution in DEVICES['desktop']['resolutions']:
                responsive_tests[resolution['name']] = self.test_responsive_design(
                    resolution['width'], 
                    resolution['height']
                )
            test_results['tests']['responsive_design'] = responsive_tests
            
            # Test 7: Login Functionality
            print(f"  Testing login functionality...")
            self.driver.get(f"{APP_URL}/login")
            login_result = self.test_form_submission({
                'email': TEST_USER_EMAIL,
                'password': TEST_USER_PASSWORD
            })
            test_results['tests']['login_functionality'] = login_result
            self.take_screenshot('after_login')
            
            # Test 8: Dashboard Page
            if login_result.get('success'):
                print(f"  Testing dashboard page...")
                test_results['tests']['dashboard'] = self.test_page_load(f"{APP_URL}/dashboard")
                self.take_screenshot('dashboard')
            
            # Calculate overall status
            failed_tests = sum(1 for test in test_results['tests'].values() 
                             if isinstance(test, dict) and not test.get('success', True))
            test_results['status'] = 'PASSED' if failed_tests == 0 else 'FAILED'
            test_results['failed_tests'] = failed_tests
            test_results['total_tests'] = len(test_results['tests'])
            
        except Exception as e:
            test_results['status'] = 'ERROR'
            test_results['error'] = str(e)
        
        finally:
            self.teardown_driver()
        
        self.results.append(test_results)
        return test_results
    
    def run_all_tests(self):
        """Run tests on all enabled browsers"""
        print(f"\n{'#'*60}")
        print(f"# BROWSER COMPATIBILITY TESTING")
        print(f"# Application: {APP_NAME}")
        print(f"# URL: {APP_URL}")
        print(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}")
        
        for browser_name, config in BROWSERS.items():
            if config['enabled']:
                self.run_browser_tests(browser_name)
            else:
                print(f"\nSkipping {browser_name} (disabled in config)")
        
        return self.results
    
    def generate_report(self):
        """Generate HTML report"""
        report_file = os.path.join(REPORTS_DIR, f'browser_compatibility_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Browser Compatibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .browser-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        .test-result {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007bff; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 1.2em; color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Browser Compatibility Test Report</h1>
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
                <span class="metric-label">Browsers Tested:</span>
                <span class="metric-value">{len(self.results)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value {'passed' if all(r.get('status') == 'PASSED' for r in self.results) else 'failed'}">
                    {('ALL PASSED' if all(r.get('status') == 'PASSED' for r in self.results) else 'SOME FAILED')}
                </span>
            </div>
        </div>
"""
        
        # Add results for each browser
        for result in self.results:
            browser = result['browser']
            status = result.get('status', 'UNKNOWN')
            status_class = 'passed' if status == 'PASSED' else 'failed'
            
            html_content += f"""
        <div class="browser-section">
            <h2>{browser.upper()} - <span class="{status_class}">{status}</span></h2>
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
                    if isinstance(test_data, dict):
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
            
            if 'error' in result:
                html_content += f"""
            <div class="test-result" style="border-left-color: #dc3545;">
                <strong>Error:</strong> {result['error']}
            </div>
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
    tester = BrowserCompatibilityTester()
    
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
        print(f"{result['browser'].upper()}: {status}")
    print(f"{'='*60}")
    print(f"Report: {report_file}")
    
    # Return exit code
    all_passed = all(r.get('status') == 'PASSED' for r in results)
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
