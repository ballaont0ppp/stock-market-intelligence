"""
Device Compatibility Testing
Tests the application across different devices and screen sizes
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
from webdriver_manager.chrome import ChromeDriverManager
from config import *


class DeviceCompatibilityTester:
    """Test application compatibility across different devices"""
    
    def __init__(self):
        self.results = []
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            if SELENIUM_CONFIG['headless']:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.implicitly_wait(SELENIUM_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            
            return True
        except Exception as e:
            print(f"Error setting up driver: {str(e)}")
            return False
    
    def teardown_driver(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def set_viewport(self, width, height):
        """Set viewport size"""
        try:
            self.driver.set_window_size(width, height)
            time.sleep(1)  # Wait for resize
            return True
        except Exception as e:
            print(f"Error setting viewport: {str(e)}")
            return False
    
    def take_screenshot(self, device_name, page_name):
        """Take a screenshot"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{device_name}_{page_name}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return None
    
    def test_responsive_layout(self):
        """Test if layout adapts to viewport"""
        try:
            # Get viewport dimensions
            viewport_width = self.driver.execute_script('return window.innerWidth')
            viewport_height = self.driver.execute_script('return window.innerHeight')
            
            # Check for horizontal scroll
            body_width = self.driver.execute_script('return document.body.scrollWidth')
            has_horizontal_scroll = body_width > viewport_width
            
            # Check if mobile menu is visible
            try:
                hamburger = self.driver.find_element(By.CSS_SELECTOR, '.navbar-toggler')
                mobile_menu_visible = hamburger.is_displayed()
            except:
                mobile_menu_visible = False
            
            # Check if content is readable
            body = self.driver.find_element(By.TAG_NAME, 'body')
            font_size = body.value_of_css_property('font-size')
            
            return {
                'success': not has_horizontal_scroll,
                'viewport_width': viewport_width,
                'viewport_height': viewport_height,
                'body_width': body_width,
                'has_horizontal_scroll': has_horizontal_scroll,
                'mobile_menu_visible': mobile_menu_visible,
                'font_size': font_size,
                'layout_adapts': not has_horizontal_scroll
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_touch_targets(self):
        """Test if touch targets are large enough"""
        try:
            # Find all interactive elements
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            
            min_size = COMPATIBILITY_REQUIREMENTS['touch_target_size']
            small_targets = []
            
            for element in buttons + links + inputs:
                if element.is_displayed():
                    size = element.size
                    if size['width'] < min_size or size['height'] < min_size:
                        small_targets.append({
                            'tag': element.tag_name,
                            'text': element.text[:30] if element.text else '',
                            'width': size['width'],
                            'height': size['height']
                        })
            
            return {
                'success': len(small_targets) == 0,
                'total_elements': len(buttons + links + inputs),
                'small_targets': len(small_targets),
                'small_target_details': small_targets[:5],  # First 5
                'min_required_size': min_size,
                'all_targets_adequate': len(small_targets) == 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_text_readability(self):
        """Test if text is readable on device"""
        try:
            # Check font sizes
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body_font_size = float(body.value_of_css_property('font-size').replace('px', ''))
            
            # Check headings
            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                h1_font_size = float(h1.value_of_css_property('font-size').replace('px', ''))
            except:
                h1_font_size = None
            
            # Check line height
            line_height = body.value_of_css_property('line-height')
            
            return {
                'success': body_font_size >= 14,  # Minimum readable size
                'body_font_size': body_font_size,
                'h1_font_size': h1_font_size,
                'line_height': line_height,
                'text_readable': body_font_size >= 14
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_image_scaling(self):
        """Test if images scale properly"""
        try:
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            
            oversized_images = []
            for img in images:
                if img.is_displayed():
                    natural_width = self.driver.execute_script('return arguments[0].naturalWidth', img)
                    displayed_width = img.size['width']
                    
                    if displayed_width > natural_width * 1.5:  # Scaled up too much
                        oversized_images.append({
                            'src': img.get_attribute('src')[:50],
                            'natural_width': natural_width,
                            'displayed_width': displayed_width
                        })
            
            return {
                'success': len(oversized_images) == 0,
                'total_images': len(images),
                'oversized_images': len(oversized_images),
                'oversized_details': oversized_images[:3],
                'images_scale_properly': len(oversized_images) == 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_form_usability(self):
        """Test if forms are usable on device"""
        try:
            # Find form inputs
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            
            input_info = []
            for inp in inputs:
                if inp.is_displayed():
                    input_type = inp.get_attribute('type')
                    size = inp.size
                    input_info.append({
                        'type': input_type,
                        'width': size['width'],
                        'height': size['height']
                    })
            
            # Check if inputs are large enough
            small_inputs = [i for i in input_info if i['height'] < 40]
            
            return {
                'success': len(small_inputs) == 0,
                'total_inputs': len(input_info),
                'small_inputs': len(small_inputs),
                'forms_usable': len(small_inputs) == 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_navigation_usability(self):
        """Test if navigation is usable on device"""
        try:
            # Check navbar
            navbar = self.driver.find_element(By.CSS_SELECTOR, '.navbar')
            navbar_height = navbar.size['height']
            
            # Check if menu items are accessible
            nav_links = navbar.find_elements(By.TAG_NAME, 'a')
            
            return {
                'success': True,
                'navbar_height': navbar_height,
                'nav_links_count': len(nav_links),
                'navigation_usable': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_page_load_performance(self):
        """Test page load performance on device"""
        try:
            # Measure page load time
            navigation_start = self.driver.execute_script('return window.performance.timing.navigationStart')
            load_complete = self.driver.execute_script('return window.performance.timing.loadEventEnd')
            
            load_time = (load_complete - navigation_start) / 1000.0  # Convert to seconds
            
            # Get performance metrics
            performance = self.driver.execute_script('''
                return {
                    domContentLoaded: window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart,
                    domInteractive: window.performance.timing.domInteractive - window.performance.timing.navigationStart,
                    loadComplete: window.performance.timing.loadEventEnd - window.performance.timing.navigationStart
                }
            ''')
            
            return {
                'success': load_time < PERFORMANCE_THRESHOLDS['page_load_time'],
                'load_time': load_time,
                'dom_content_loaded': performance['domContentLoaded'] / 1000.0,
                'dom_interactive': performance['domInteractive'] / 1000.0,
                'meets_threshold': load_time < PERFORMANCE_THRESHOLDS['page_load_time']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_device(self, device_config, device_name):
        """Run all tests for a specific device"""
        print(f"\n  Testing {device_name}...")
        
        # Set viewport
        if not self.set_viewport(device_config['width'], device_config['height']):
            return {
                'device': device_name,
                'status': 'FAILED',
                'error': 'Failed to set viewport'
            }
        
        test_results = {
            'device': device_name,
            'width': device_config['width'],
            'height': device_config['height'],
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        try:
            # Load home page
            self.driver.get(APP_URL)
            time.sleep(2)
            
            # Run tests
            print(f"    - Testing responsive layout...")
            test_results['tests']['responsive_layout'] = self.test_responsive_layout()
            self.take_screenshot(device_name, 'home')
            
            print(f"    - Testing touch targets...")
            test_results['tests']['touch_targets'] = self.test_touch_targets()
            
            print(f"    - Testing text readability...")
            test_results['tests']['text_readability'] = self.test_text_readability()
            
            print(f"    - Testing image scaling...")
            test_results['tests']['image_scaling'] = self.test_image_scaling()
            
            print(f"    - Testing form usability...")
            test_results['tests']['form_usability'] = self.test_form_usability()
            
            print(f"    - Testing navigation usability...")
            test_results['tests']['navigation_usability'] = self.test_navigation_usability()
            
            print(f"    - Testing page load performance...")
            test_results['tests']['page_load_performance'] = self.test_page_load_performance()
            
            # Test login page
            self.driver.get(f"{APP_URL}/login")
            time.sleep(1)
            self.take_screenshot(device_name, 'login')
            
            # Calculate overall status
            failed_tests = sum(1 for test in test_results['tests'].values() 
                             if not test.get('success', False))
            test_results['status'] = 'PASSED' if failed_tests == 0 else 'FAILED'
            test_results['failed_tests'] = failed_tests
            test_results['total_tests'] = len(test_results['tests'])
            
        except Exception as e:
            test_results['status'] = 'ERROR'
            test_results['error'] = str(e)
        
        return test_results
    
    def run_all_tests(self):
        """Run tests on all device configurations"""
        print(f"\n{'#'*60}")
        print(f"# DEVICE COMPATIBILITY TESTING")
        print(f"# Application: {APP_NAME}")
        print(f"# URL: {APP_URL}")
        print(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}")
        
        if not self.setup_driver():
            print("Failed to initialize driver")
            return []
        
        try:
            # Test desktop resolutions
            if DEVICES['desktop']['enabled']:
                print(f"\nTesting Desktop Devices:")
                for resolution in DEVICES['desktop']['resolutions']:
                    result = self.test_device(resolution, f"Desktop_{resolution['name']}")
                    self.results.append(result)
            
            # Test tablet devices
            if DEVICES['tablet']['enabled']:
                print(f"\nTesting Tablet Devices:")
                for device in DEVICES['tablet']['devices']:
                    result = self.test_device(device, f"Tablet_{device['name']}")
                    self.results.append(result)
            
            # Test mobile devices
            if DEVICES['mobile']['enabled']:
                print(f"\nTesting Mobile Devices:")
                for device in DEVICES['mobile']['devices']:
                    result = self.test_device(device, f"Mobile_{device['name']}")
                    self.results.append(result)
        
        finally:
            self.teardown_driver()
        
        return self.results
    
    def generate_report(self):
        """Generate HTML report"""
        report_file = os.path.join(REPORTS_DIR, f'device_compatibility_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Device Compatibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #17a2b8; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .device-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #17a2b8; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 1.2em; color: #17a2b8; }}
        .device-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .device-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #f8f9fa; }}
        .device-card h3 {{ margin-top: 0; color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Device Compatibility Test Report</h1>
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
                <span class="metric-label">Devices Tested:</span>
                <span class="metric-value">{len(self.results)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value {('passed' if all(r.get('status') == 'PASSED' for r in self.results) else 'failed')}">
                    {('ALL PASSED' if all(r.get('status') == 'PASSED' for r in self.results) else 'SOME FAILED')}
                </span>
            </div>
        </div>
        
        <h2>Device Test Results</h2>
        <div class="device-grid">
"""
        
        for result in self.results:
            device = result['device']
            status = result.get('status', 'UNKNOWN')
            status_class = 'passed' if status == 'PASSED' else 'failed'
            
            html_content += f"""
            <div class="device-card">
                <h3>{device}</h3>
                <p><strong>Resolution:</strong> {result['width']}x{result['height']}</p>
                <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
                <p><strong>Tests:</strong> {result.get('total_tests', 0) - result.get('failed_tests', 0)}/{result.get('total_tests', 0)} passed</p>
            </div>
"""
        
        html_content += """
        </div>
        
        <h2>Detailed Test Results</h2>
"""
        
        for result in self.results:
            device = result['device']
            status = result.get('status', 'UNKNOWN')
            status_class = 'passed' if status == 'PASSED' else 'failed'
            
            html_content += f"""
        <div class="device-section">
            <h3>{device} - <span class="{status_class}">{status}</span></h3>
            <p><strong>Resolution:</strong> {result['width']}x{result['height']}</p>
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
    tester = DeviceCompatibilityTester()
    
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
        print(f"{result['device']}: {status}")
    print(f"{'='*60}")
    print(f"Report: {report_file}")
    
    # Return exit code
    all_passed = all(r.get('status') == 'PASSED' for r in results)
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
