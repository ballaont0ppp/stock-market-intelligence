"""
Cognitive Accessibility Tests
Tests for navigation clarity, consistent layout, error prevention, and cognitive load
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
from collections import Counter


class TestCognitiveAccessibility:
    """Test cognitive accessibility features"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, authenticated_driver):
        """Setup for each test"""
        self.driver = driver
        self.auth_driver = authenticated_driver
        self.wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
    
    def test_navigation_clarity(self, driver):
        """Test that navigation is clear and consistent across pages"""
        results = {}
        navigation_structures = []
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find navigation elements
            nav_elements = test_driver.find_elements(By.CSS_SELECTOR, 'nav, [role="navigation"]')
            
            nav_info = []
            for nav in nav_elements:
                # Get all links in navigation
                links = nav.find_elements(By.TAG_NAME, 'a')
                link_texts = [link.text.strip() for link in links if link.text.strip()]
                
                nav_info.append({
                    'link_count': len(links),
                    'link_texts': link_texts,
                    'has_aria_label': nav.get_attribute('aria-label') is not None
                })
            
            # Check for breadcrumbs
            breadcrumbs = test_driver.find_elements(By.CSS_SELECTOR, '[aria-label*="breadcrumb"], .breadcrumb, nav[aria-label="Breadcrumb"]')
            
            # Check for page title/heading
            h1_elements = test_driver.find_elements(By.TAG_NAME, 'h1')
            page_title = h1_elements[0].text if h1_elements else None
            
            results[page['name']] = {
                'navigation_count': len(nav_elements),
                'navigation_details': nav_info,
                'has_breadcrumbs': len(breadcrumbs) > 0,
                'page_title': page_title,
                'has_clear_title': page_title is not None and len(page_title) > 0
            }
            
            # Store navigation structure for consistency check
            if nav_info:
                navigation_structures.append(nav_info[0]['link_texts'])
        
        # Check navigation consistency
        if len(navigation_structures) > 1:
            # Compare first navigation with others
            base_nav = set(navigation_structures[0])
            consistency_scores = []
            
            for nav_struct in navigation_structures[1:]:
                nav_set = set(nav_struct)
                # Calculate Jaccard similarity
                intersection = len(base_nav.intersection(nav_set))
                union = len(base_nav.union(nav_set))
                similarity = (intersection / union * 100) if union > 0 else 0
                consistency_scores.append(similarity)
            
            avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 100
            results['navigation_consistency'] = {
                'average_similarity': avg_consistency,
                'is_consistent': avg_consistency >= 80
            }
        
        self._save_results('navigation_clarity_results.json', results)
        
        # Assert all pages have clear titles
        for page_name, page_data in results.items():
            if page_name != 'navigation_consistency':
                assert page_data['has_clear_title'], \
                    f"Page {page_name} does not have a clear title"
    
    def test_consistent_layout(self, driver):
        """Test that layout is consistent across pages"""
        results = {}
        layout_structures = []
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Analyze page structure
            structure = {
                'has_header': len(test_driver.find_elements(By.CSS_SELECTOR, 'header, [role="banner"]')) > 0,
                'has_nav': len(test_driver.find_elements(By.CSS_SELECTOR, 'nav, [role="navigation"]')) > 0,
                'has_main': len(test_driver.find_elements(By.CSS_SELECTOR, 'main, [role="main"]')) > 0,
                'has_footer': len(test_driver.find_elements(By.CSS_SELECTOR, 'footer, [role="contentinfo"]')) > 0,
                'has_sidebar': len(test_driver.find_elements(By.CSS_SELECTOR, 'aside, .sidebar, [role="complementary"]')) > 0
            }
            
            # Check heading hierarchy
            headings = test_driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
            heading_levels = [int(h.tag_name[1]) for h in headings]
            
            # Check for proper heading order
            proper_order = True
            if heading_levels:
                for i in range(len(heading_levels) - 1):
                    if heading_levels[i+1] - heading_levels[i] > 1:
                        proper_order = False
                        break
            
            results[page['name']] = {
                'structure': structure,
                'heading_count': len(headings),
                'heading_levels': heading_levels,
                'proper_heading_order': proper_order,
                'has_h1': 1 in heading_levels,
                'h1_count': heading_levels.count(1) if heading_levels else 0
            }
            
            layout_structures.append(structure)
        
        # Check layout consistency
        if layout_structures:
            # Count how many pages have each structural element
            structure_counts = {
                'has_header': sum(1 for s in layout_structures if s['has_header']),
                'has_nav': sum(1 for s in layout_structures if s['has_nav']),
                'has_main': sum(1 for s in layout_structures if s['has_main']),
                'has_footer': sum(1 for s in layout_structures if s['has_footer'])
            }
            
            total_pages = len(layout_structures)
            consistency_percentage = {
                key: (count / total_pages * 100) for key, count in structure_counts.items()
            }
            
            results['layout_consistency'] = {
                'structure_counts': structure_counts,
                'consistency_percentage': consistency_percentage,
                'is_consistent': all(pct >= 80 for pct in consistency_percentage.values())
            }
        
        self._save_results('consistent_layout_results.json', results)
        
        # Assert proper heading hierarchy
        for page_name, page_data in results.items():
            if page_name != 'layout_consistency':
                assert page_data['proper_heading_order'], \
                    f"Improper heading order on {page_name}"
                assert page_data['h1_count'] == 1, \
                    f"Page {page_name} should have exactly one h1, found {page_data['h1_count']}"
    
    def test_error_prevention_mechanisms(self, driver):
        """Test that error prevention mechanisms are in place"""
        results = {}
        
        # Test form pages
        form_pages = [p for p in config.TEST_PAGES if any(keyword in p['path'].lower() for keyword in ['login', 'register', 'buy', 'sell', 'profile'])]
        
        for page in form_pages:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Find all forms
            forms = test_driver.find_elements(By.TAG_NAME, 'form')
            
            form_analysis = []
            for form in forms:
                # Check for required field indicators
                required_inputs = form.find_elements(By.CSS_SELECTOR, 'input[required], select[required], textarea[required]')
                
                # Check for input validation attributes
                inputs_with_validation = form.find_elements(By.CSS_SELECTOR, 
                    'input[pattern], input[min], input[max], input[minlength], input[maxlength], input[type="email"], input[type="number"]'
                )
                
                # Check for confirmation fields (password confirmation, etc.)
                confirmation_fields = form.find_elements(By.CSS_SELECTOR, 
                    'input[name*="confirm"], input[id*="confirm"]'
                )
                
                # Check for help text
                help_texts = form.find_elements(By.CSS_SELECTOR, 
                    '.help-text, .form-text, small, [class*="hint"]'
                )
                
                # Check for submit button
                submit_buttons = form.find_elements(By.CSS_SELECTOR, 
                    'button[type="submit"], input[type="submit"]'
                )
                
                form_analysis.append({
                    'required_fields': len(required_inputs),
                    'validated_inputs': len(inputs_with_validation),
                    'confirmation_fields': len(confirmation_fields),
                    'help_texts': len(help_texts),
                    'has_submit_button': len(submit_buttons) > 0,
                    'has_error_prevention': (
                        len(required_inputs) > 0 or 
                        len(inputs_with_validation) > 0 or
                        len(help_texts) > 0
                    )
                })
            
            results[page['name']] = {
                'form_count': len(forms),
                'forms': form_analysis,
                'all_forms_have_prevention': all(f['has_error_prevention'] for f in form_analysis) if form_analysis else False
            }
        
        self._save_results('error_prevention_results.json', results)
    
    def test_help_documentation(self, driver):
        """Test that help documentation is available and accessible"""
        results = {}
        
        for page in config.TEST_PAGES[:5]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Look for help elements
            help_elements = test_driver.find_elements(By.CSS_SELECTOR,
                '[class*="help"], [id*="help"], [aria-label*="help"], [title*="help"], .tooltip, [data-toggle="tooltip"]'
            )
            
            # Look for info icons
            info_icons = test_driver.find_elements(By.CSS_SELECTOR,
                '.fa-info, .fa-question, .fa-help, [class*="info-icon"], [class*="help-icon"]'
            )
            
            # Look for placeholder text in inputs
            inputs_with_placeholder = test_driver.find_elements(By.CSS_SELECTOR, 'input[placeholder], textarea[placeholder]')
            
            # Look for labels with descriptive text
            labels = test_driver.find_elements(By.TAG_NAME, 'label')
            descriptive_labels = [l for l in labels if len(l.text) > 10]
            
            results[page['name']] = {
                'help_elements': len(help_elements),
                'info_icons': len(info_icons),
                'inputs_with_placeholder': len(inputs_with_placeholder),
                'descriptive_labels': len(descriptive_labels),
                'has_help_available': (
                    len(help_elements) > 0 or 
                    len(info_icons) > 0 or 
                    len(inputs_with_placeholder) > 0
                )
            }
        
        self._save_results('help_documentation_results.json', results)
    
    def test_cognitive_load(self, driver):
        """Test that pages don't have excessive cognitive load"""
        results = {}
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Count interactive elements
            interactive_elements = test_driver.find_elements(By.CSS_SELECTOR,
                'a, button, input, select, textarea'
            )
            
            # Count text blocks
            text_blocks = test_driver.find_elements(By.CSS_SELECTOR, 'p, div, span')
            
            # Count images
            images = test_driver.find_elements(By.TAG_NAME, 'img')
            
            # Count forms
            forms = test_driver.find_elements(By.TAG_NAME, 'form')
            
            # Calculate page complexity score
            complexity_score = (
                len(interactive_elements) * 2 +  # Interactive elements have higher weight
                len(text_blocks) * 0.5 +
                len(images) * 1 +
                len(forms) * 5
            )
            
            # Check for animations/distractions
            animated_elements = test_driver.find_elements(By.CSS_SELECTOR, 
                '[class*="animate"], [class*="transition"], [class*="fade"]'
            )
            
            # Check for auto-playing media
            auto_media = test_driver.find_elements(By.CSS_SELECTOR, 
                'video[autoplay], audio[autoplay]'
            )
            
            results[page['name']] = {
                'interactive_elements': len(interactive_elements),
                'text_blocks': len(text_blocks),
                'images': len(images),
                'forms': len(forms),
                'complexity_score': complexity_score,
                'animated_elements': len(animated_elements),
                'auto_playing_media': len(auto_media),
                'acceptable_complexity': complexity_score < 200,  # Threshold
                'no_auto_media': len(auto_media) == 0
            }
        
        self._save_results('cognitive_load_results.json', results)
        
        # Assert no auto-playing media
        for page_name, page_data in results.items():
            assert page_data['no_auto_media'], \
                f"Auto-playing media found on {page_name}"
    
    def test_language_clarity(self, driver):
        """Test that language is clear and understandable"""
        results = {}
        
        for page in config.TEST_PAGES[:5]:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Check for lang attribute
            html_lang = test_driver.find_element(By.TAG_NAME, 'html').get_attribute('lang')
            
            # Get all text content
            body_text = test_driver.find_element(By.TAG_NAME, 'body').text
            
            # Check for jargon indicators (very long words, technical terms)
            words = body_text.split()
            long_words = [w for w in words if len(w) > 15]
            
            # Check for abbreviations without expansion
            abbr_elements = test_driver.find_elements(By.TAG_NAME, 'abbr')
            abbr_with_title = [a for a in abbr_elements if a.get_attribute('title')]
            
            results[page['name']] = {
                'has_lang_attribute': html_lang is not None,
                'lang': html_lang,
                'word_count': len(words),
                'long_words': len(long_words),
                'abbreviations': len(abbr_elements),
                'abbreviations_with_expansion': len(abbr_with_title),
                'clear_language': len(long_words) < len(words) * 0.05  # Less than 5% long words
            }
        
        self._save_results('language_clarity_results.json', results)
        
        # Assert lang attribute is present
        for page_name, page_data in results.items():
            assert page_data['has_lang_attribute'], \
                f"Missing lang attribute on {page_name}"
    
    def test_consistent_identification(self, driver):
        """Test that components are consistently identified across pages"""
        results = {}
        button_texts = []
        link_texts = []
        
        for page in config.TEST_PAGES:
            url = f"{config.APP_URL}{page['path']}"
            test_driver = self.auth_driver if page['requires_auth'] else driver
            test_driver.get(url)
            time.sleep(2)
            
            # Collect button texts
            buttons = test_driver.find_elements(By.TAG_NAME, 'button')
            page_button_texts = [b.text.strip() for b in buttons if b.text.strip()]
            button_texts.extend(page_button_texts)
            
            # Collect link texts
            links = test_driver.find_elements(By.TAG_NAME, 'a')
            page_link_texts = [l.text.strip() for l in links if l.text.strip()]
            link_texts.extend(page_link_texts)
            
            results[page['name']] = {
                'button_count': len(page_button_texts),
                'link_count': len(page_link_texts)
            }
        
        # Analyze consistency
        button_counter = Counter(button_texts)
        link_counter = Counter(link_texts)
        
        # Find buttons/links that appear multiple times with same text
        consistent_buttons = {text: count for text, count in button_counter.items() if count > 1}
        consistent_links = {text: count for text, count in link_counter.items() if count > 1}
        
        results['consistency_analysis'] = {
            'consistent_buttons': consistent_buttons,
            'consistent_links': consistent_links,
            'total_unique_buttons': len(button_counter),
            'total_unique_links': len(link_counter)
        }
        
        self._save_results('consistent_identification_results.json', results)
    
    def _save_results(self, filename, data):
        """Save test results to JSON file"""
        filepath = config.RESULTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {filepath}")
