"""
Motor Accessibility Tests
Tests for keyboard navigation, focus management, click target sizes, and assistive device compatibility
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from axe_selenium_python import Axe
import config
import time
import json


class TestMotorAccessibility:
    """Test motor accessibility features"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, authenticated_driver):
        """Setup for each test"""
        self.driver = driver
        self.auth_driver = authenticated_driver
        self.wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
    
    def test_keyboard_navigation_all_features(self, driver):
        """Test that all features are accessible via keyboard navigation"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Get all interactive elements
            interactive_elements = test_driver.find_elements(By.CSS_SELECTOR,
                'a, button, input, select, textarea, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])'
            )
            
            # Test tab navigation
            body = test_driver.find_element(By.TAG_NAME, 'body')
            focused_elements = []
            
            for i in range(min(20, len(interactive_elements))):
                body.send_keys(Keys.TAB)
                time.sleep(0.1)
                
                try:
                    active_element = test_driver.switch_to.active_element
                    focused_elements.append({
                        'tag': active_element.tag_name,
                        'type': active_element.get_attribute('type'),
                        'id': active_element.get_attribute('id'),
                        'class': active_element.get_attribute('class'),
                        'text': active_element.text[:50] if active_element.text else ''
                    })
                except:
                    pass
            
            # Test shift+tab (reverse navigation)
            reverse_focused = []
            for i in range(5):
                body.send_keys(Keys.SHIFT + Keys.TAB)
                time.sleep(0.1)
                
                try:
                    active_element = test_driver.switch_to.active_element
                    reverse_focused.append({
                        'tag': active_element.tag_name,
                        'id': active_element.get_attribute('id')
                    })
                except:
                    pass
            
            results[page['name']] = {
                'total_interactive': len(interactive_elements),
                'tab_sequence_length': len(focused_elements),
                'tab_sequence': focused_elements,
                'reverse_navigation': reverse_focused,
                'keyboard_accessible': len(focused_elements) > 0
            }
            
            # Assert keyboard navigation works
            assert len(focused_elements) > 0, \
                f"No elements focusable via keyboard on {page['name']}"
        
        self._save_results('keyboard_navigation_results.json', results)
    
    def test_focus_indicators_visibility(self, driver):
        """Test that focus indicators are clearly visible"""
        results = {}
        
        for page in config.TEST_PAGES[:5]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find focusable elements
            focusable = test_driver.find_elements(By.CSS_SELECTOR,
                'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            )
            
            focus_visibility = []
            for elem in focusable[:15]:  # Test first 15 elements
                try:
                    # Focus element
                    test_driver.execute_script("arguments[0].focus();", elem)
                    time.sleep(0.2)
                    
                    # Get computed styles
                    outline_width = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).outlineWidth;", elem
                    )
                    outline_style = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).outlineStyle;", elem
                    )
                    outline_color = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).outlineColor;", elem
                    )
                    box_shadow = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).boxShadow;", elem
                    )
                    
                    # Check if outline is visible (not 0px and not 'none')
                    has_visible_outline = (
                        outline_width not in ['0px', 'none'] and 
                        outline_style != 'none'
                    )
                    
                    # Check if box-shadow is used for focus
                    has_box_shadow = box_shadow != 'none'
                    
                    focus_visibility.append({
                        'tag': elem.tag_name,
                        'id': elem.get_attribute('id'),
                        'has_visible_outline': has_visible_outline,
                        'has_box_shadow': has_box_shadow,
                        'outline_width': outline_width,
                        'outline_style': outline_style,
                        'outline_color': outline_color,
                        'visible': has_visible_outline or has_box_shadow
                    })
                except Exception as e:
                    pass
            
            visible_count = sum(1 for f in focus_visibility if f['visible'])
            
            results[page['name']] = {
                'total_tested': len(focus_visibility),
                'visible_indicators': visible_count,
                'percentage': (visible_count / len(focus_visibility) * 100) if focus_visibility else 0,
                'details': focus_visibility
            }
            
            # Assert at least 80% of elements have visible focus indicators
            if focus_visibility:
                assert results[page['name']]['percentage'] >= 80, \
                    f"Less than 80% of elements have visible focus indicators on {page['name']}"
        
        self._save_results('focus_visibility_results.json', results)
    
    def test_click_target_sizes(self, driver):
        """Test that all interactive elements meet minimum touch target size (44x44px)"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find all clickable elements
            clickable = test_driver.find_elements(By.CSS_SELECTOR,
                'a, button, input[type="button"], input[type="submit"], input[type="checkbox"], input[type="radio"], [role="button"], [onclick]'
            )
            
            size_results = []
            too_small = []
            
            for elem in clickable:
                try:
                    size = elem.size
                    width = size['width']
                    height = size['height']
                    
                    meets_minimum = (
                        width >= config.MIN_TOUCH_TARGET_SIZE and 
                        height >= config.MIN_TOUCH_TARGET_SIZE
                    )
                    
                    elem_info = {
                        'tag': elem.tag_name,
                        'type': elem.get_attribute('type'),
                        'id': elem.get_attribute('id'),
                        'class': elem.get_attribute('class'),
                        'width': width,
                        'height': height,
                        'meets_minimum': meets_minimum
                    }
                    
                    size_results.append(elem_info)
                    
                    if not meets_minimum and elem.is_displayed():
                        too_small.append(elem_info)
                except:
                    pass
            
            results[page['name']] = {
                'total_clickable': len(clickable),
                'tested': len(size_results),
                'meets_minimum': sum(1 for r in size_results if r['meets_minimum']),
                'too_small': len(too_small),
                'too_small_details': too_small,
                'compliance_rate': (sum(1 for r in size_results if r['meets_minimum']) / len(size_results) * 100) if size_results else 100
            }
        
        self._save_results('click_target_sizes_results.json', results)
        
        # Assert compliance rate is at least 90%
        for page_name, page_data in results.items():
            assert page_data['compliance_rate'] >= 90, \
                f"Click target size compliance below 90% on {page_name}: {page_data['compliance_rate']:.1f}%"
    
    def test_no_time_based_interactions(self, driver):
        """Test that there are no time-based interactions that cannot be extended"""
        results = {}
        
        for page in config.TEST_PAGES[:5]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Check for setTimeout/setInterval in page scripts
            has_timers = test_driver.execute_script("""
                var hasTimers = false;
                var scripts = document.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++) {
                    var content = scripts[i].textContent;
                    if (content.includes('setTimeout') || content.includes('setInterval')) {
                        hasTimers = true;
                        break;
                    }
                }
                return hasTimers;
            """)
            
            # Check for auto-refresh meta tags
            meta_refresh = test_driver.find_elements(By.CSS_SELECTOR, 'meta[http-equiv="refresh"]')
            
            # Check for animations that might be time-based
            animated_elements = test_driver.find_elements(By.CSS_SELECTOR, '[class*="animate"], [class*="transition"]')
            
            results[page['name']] = {
                'has_timers': has_timers,
                'has_meta_refresh': len(meta_refresh) > 0,
                'animated_elements': len(animated_elements),
                'passed': not has_timers and len(meta_refresh) == 0
            }
        
        self._save_results('time_based_interactions_results.json', results)
    
    def test_keyboard_shortcuts(self, driver):
        """Test that keyboard shortcuts don't conflict with assistive technology"""
        results = {}
        
        for page in config.TEST_PAGES[:3]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Check for accesskey attributes (can conflict with screen readers)
            elements_with_accesskey = test_driver.find_elements(By.CSS_SELECTOR, '[accesskey]')
            
            accesskeys = []
            for elem in elements_with_accesskey:
                accesskeys.append({
                    'tag': elem.tag_name,
                    'accesskey': elem.get_attribute('accesskey'),
                    'id': elem.get_attribute('id')
                })
            
            # Check for keyboard event listeners
            has_keydown_listeners = test_driver.execute_script("""
                var listeners = [];
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < Math.min(elements.length, 100); i++) {
                    var elem = elements[i];
                    if (elem.onkeydown || elem.onkeyup || elem.onkeypress) {
                        listeners.push({
                            tag: elem.tagName,
                            id: elem.id,
                            class: elem.className
                        });
                    }
                }
                return listeners;
            """)
            
            results[page['name']] = {
                'accesskey_count': len(accesskeys),
                'accesskeys': accesskeys,
                'keyboard_listeners': len(has_keydown_listeners),
                'listener_details': has_keydown_listeners[:10]  # First 10
            }
        
        self._save_results('keyboard_shortcuts_results.json', results)
    
    def test_skip_navigation_links(self, driver):
        """Test that skip navigation links are present and functional"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Look for skip links
            skip_links = test_driver.find_elements(By.CSS_SELECTOR, 
                'a[href^="#"], a[href*="skip"], a[class*="skip"]'
            )
            
            skip_link_info = []
            for link in skip_links:
                text = link.text.lower()
                href = link.get_attribute('href')
                
                # Check if it's likely a skip link
                if any(keyword in text for keyword in ['skip', 'jump', 'main content', 'navigation']):
                    skip_link_info.append({
                        'text': link.text,
                        'href': href,
                        'visible': link.is_displayed()
                    })
            
            results[page['name']] = {
                'has_skip_links': len(skip_link_info) > 0,
                'skip_links': skip_link_info
            }
        
        self._save_results('skip_navigation_results.json', results)
    
    def test_form_keyboard_accessibility(self, driver):
        """Test that forms are fully accessible via keyboard"""
        results = {}
        
        # Test pages with forms
        form_pages = [p for p in config.TEST_PAGES if 'login' in p['path'].lower() or 'register' in p['path'].lower() or 'order' in p['path'].lower()]
        
        for page in form_pages:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find all forms
            forms = test_driver.find_elements(By.TAG_NAME, 'form')
            
            form_results = []
            for form in forms:
                # Find all form controls
                inputs = form.find_elements(By.CSS_SELECTOR, 'input, select, textarea, button')
                
                focusable_count = 0
                for inp in inputs:
                    try:
                        test_driver.execute_script("arguments[0].focus();", inp)
                        time.sleep(0.1)
                        
                        active = test_driver.switch_to.active_element
                        if active == inp:
                            focusable_count += 1
                    except:
                        pass
                
                form_results.append({
                    'total_controls': len(inputs),
                    'focusable_controls': focusable_count,
                    'fully_accessible': focusable_count == len(inputs)
                })
            
            results[page['name']] = {
                'form_count': len(forms),
                'forms': form_results,
                'all_accessible': all(f['fully_accessible'] for f in form_results)
            }
        
        self._save_results('form_keyboard_accessibility_results.json', results)
        
        # Assert all forms are keyboard accessible
        for page_name, page_data in results.items():
            assert page_data['all_accessible'], \
                f"Not all forms are keyboard accessible on {page_name}"
    
    def _save_results(self, filename, data):
        """Save test results to JSON file"""
        filepath = config.RESULTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {filepath}")
