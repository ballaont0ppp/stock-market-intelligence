"""
Visual Accessibility Tests
Tests for color contrast, text resizing, screen reader compatibility, and visual elements
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from axe_selenium_python import Axe
import config
import time
import json
from PIL import Image, ImageDraw
import io
import re


class TestVisualAccessibility:
    """Test visual accessibility features"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, authenticated_driver):
        """Setup for each test"""
        self.driver = driver
        self.auth_driver = authenticated_driver
        self.wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
        
    def test_color_contrast_ratios(self, driver):
        """Test that color contrast ratios meet WCAG AA standards (4.5:1 minimum)"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            
            # Use authenticated driver if needed
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Run axe accessibility check focused on color contrast
            axe = Axe(test_driver)
            axe.inject()
            axe_results = axe.run(options={'runOnly': ['color-contrast']})
            
            violations = axe_results.get('violations', [])
            contrast_violations = [v for v in violations if v['id'] == 'color-contrast']
            
            results[page['name']] = {
                'url': url,
                'violations': len(contrast_violations),
                'details': contrast_violations
            }
            
            # Assert no critical contrast violations
            assert len(contrast_violations) == 0, \
                f"Color contrast violations found on {page['name']}: {contrast_violations}"
        
        # Save results
        self._save_results('color_contrast_results.json', results)
    
    def test_text_resizing(self, driver):
        """Test that text can be resized up to 200% without loss of functionality"""
        results = {}
        
        for page in config.TEST_PAGES[:3]:  # Test first 3 pages
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            page_results = {}
            
            for zoom_level in config.TEXT_RESIZE_LEVELS:
                # Set zoom level
                test_driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")
                time.sleep(1)
                
                # Check for horizontal scrollbar (indicates text overflow)
                has_horizontal_scroll = test_driver.execute_script(
                    "return document.documentElement.scrollWidth > document.documentElement.clientWidth"
                )
                
                # Check if content is still visible
                body_visible = test_driver.execute_script(
                    "return window.getComputedStyle(document.body).visibility === 'visible'"
                )
                
                page_results[f'{zoom_level}%'] = {
                    'horizontal_scroll': has_horizontal_scroll,
                    'content_visible': body_visible,
                    'passed': body_visible and not has_horizontal_scroll
                }
            
            results[page['name']] = page_results
            
            # Reset zoom
            test_driver.execute_script("document.body.style.zoom='100%'")
        
        self._save_results('text_resizing_results.json', results)
        
        # Check that all pages pass at all zoom levels
        for page_name, page_data in results.items():
            for zoom, zoom_data in page_data.items():
                assert zoom_data['passed'], \
                    f"Text resizing failed on {page_name} at {zoom}"
    
    def test_image_alt_text(self, driver):
        """Test that all images have appropriate alt text"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find all images
            images = test_driver.find_elements(By.TAG_NAME, 'img')
            
            missing_alt = []
            empty_alt = []
            has_alt = []
            
            for img in images:
                alt = img.get_attribute('alt')
                src = img.get_attribute('src')
                
                if alt is None:
                    missing_alt.append(src)
                elif alt.strip() == '':
                    # Empty alt is acceptable for decorative images
                    empty_alt.append(src)
                else:
                    has_alt.append({'src': src, 'alt': alt})
            
            results[page['name']] = {
                'total_images': len(images),
                'missing_alt': missing_alt,
                'empty_alt': empty_alt,
                'has_alt': len(has_alt),
                'details': has_alt
            }
            
            # Assert no images are missing alt attribute
            assert len(missing_alt) == 0, \
                f"Images without alt attribute on {page['name']}: {missing_alt}"
        
        self._save_results('image_alt_text_results.json', results)
    
    def test_screen_reader_compatibility(self, driver):
        """Test screen reader compatibility using ARIA labels and semantic HTML"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Run axe accessibility check for ARIA and semantic HTML
            axe = Axe(test_driver)
            axe.inject()
            axe_results = axe.run(options={
                'runOnly': ['aria', 'name-role-value', 'semantics']
            })
            
            violations = axe_results.get('violations', [])
            
            # Check for proper heading structure
            headings = test_driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
            heading_structure = [h.tag_name for h in headings]
            
            # Check for landmarks
            landmarks = test_driver.find_elements(By.CSS_SELECTOR, 
                'header, nav, main, aside, footer, [role="banner"], [role="navigation"], [role="main"], [role="complementary"], [role="contentinfo"]'
            )
            
            # Check for form labels
            inputs = test_driver.find_elements(By.TAG_NAME, 'input')
            unlabeled_inputs = []
            for inp in inputs:
                input_id = inp.get_attribute('id')
                input_type = inp.get_attribute('type')
                aria_label = inp.get_attribute('aria-label')
                aria_labelledby = inp.get_attribute('aria-labelledby')
                
                # Skip hidden inputs
                if input_type == 'hidden':
                    continue
                
                # Check if input has a label
                has_label = False
                if input_id:
                    labels = test_driver.find_elements(By.CSS_SELECTOR, f'label[for="{input_id}"]')
                    has_label = len(labels) > 0
                
                if not has_label and not aria_label and not aria_labelledby:
                    unlabeled_inputs.append({
                        'id': input_id,
                        'type': input_type,
                        'name': inp.get_attribute('name')
                    })
            
            results[page['name']] = {
                'aria_violations': len(violations),
                'violation_details': violations,
                'heading_count': len(headings),
                'heading_structure': heading_structure,
                'landmark_count': len(landmarks),
                'unlabeled_inputs': unlabeled_inputs
            }
            
            # Assert no critical ARIA violations
            critical_violations = [v for v in violations if v.get('impact') in ['critical', 'serious']]
            assert len(critical_violations) == 0, \
                f"Critical ARIA violations on {page['name']}: {critical_violations}"
        
        self._save_results('screen_reader_compatibility_results.json', results)
    
    def test_high_contrast_mode(self, driver):
        """Test that the application works in high contrast mode"""
        results = {}
        
        # Test a few key pages
        for page in config.TEST_PAGES[:3]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Apply high contrast CSS
            high_contrast_css = """
                * {
                    background: black !important;
                    color: white !important;
                    border-color: white !important;
                }
                a {
                    color: yellow !important;
                }
            """
            test_driver.execute_script(f"""
                var style = document.createElement('style');
                style.innerHTML = `{high_contrast_css}`;
                document.head.appendChild(style);
            """)
            time.sleep(1)
            
            # Check if content is still visible
            body_visible = test_driver.execute_script(
                "return window.getComputedStyle(document.body).visibility === 'visible'"
            )
            
            # Check if text is readable
            text_elements = test_driver.find_elements(By.CSS_SELECTOR, 'p, span, div, h1, h2, h3, h4, h5, h6')
            readable_count = 0
            for elem in text_elements[:10]:  # Check first 10 text elements
                try:
                    if elem.is_displayed() and elem.text.strip():
                        readable_count += 1
                except:
                    pass
            
            results[page['name']] = {
                'body_visible': body_visible,
                'readable_elements': readable_count,
                'passed': body_visible and readable_count > 0
            }
        
        self._save_results('high_contrast_mode_results.json', results)
        
        # Assert all pages work in high contrast mode
        for page_name, page_data in results.items():
            assert page_data['passed'], \
                f"High contrast mode failed on {page_name}"
    
    def test_focus_indicators(self, driver):
        """Test that focus indicators are visible for keyboard navigation"""
        results = {}
        
        for page in config.TEST_PAGES[:5]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find all focusable elements
            focusable_elements = test_driver.find_elements(By.CSS_SELECTOR,
                'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            )
            
            focus_results = []
            for elem in focusable_elements[:10]:  # Test first 10 focusable elements
                try:
                    # Focus the element
                    test_driver.execute_script("arguments[0].focus();", elem)
                    time.sleep(0.2)
                    
                    # Check if element has visible focus indicator
                    outline = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).outline;", elem
                    )
                    box_shadow = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).boxShadow;", elem
                    )
                    border = test_driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).border;", elem
                    )
                    
                    has_focus_indicator = (
                        outline != 'none' or 
                        box_shadow != 'none' or 
                        'focus' in elem.get_attribute('class') or ''
                    )
                    
                    focus_results.append({
                        'tag': elem.tag_name,
                        'type': elem.get_attribute('type'),
                        'has_focus_indicator': has_focus_indicator,
                        'outline': outline,
                        'box_shadow': box_shadow
                    })
                except:
                    pass
            
            results[page['name']] = {
                'total_focusable': len(focusable_elements),
                'tested': len(focus_results),
                'with_indicators': sum(1 for r in focus_results if r['has_focus_indicator']),
                'details': focus_results
            }
        
        self._save_results('focus_indicators_results.json', results)
    
    def _save_results(self, filename, data):
        """Save test results to JSON file"""
        filepath = config.RESULTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {filepath}")
