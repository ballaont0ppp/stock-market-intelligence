"""
Accessibility Improvements Implementation Script

This script analyzes test results and generates recommendations for fixing
accessibility issues found during testing.
"""
import json
from pathlib import Path
import config
from datetime import datetime


class AccessibilityAnalyzer:
    """Analyze test results and generate improvement recommendations"""
    
    def __init__(self):
        self.results_dir = config.RESULTS_DIR
        self.issues = []
        self.recommendations = []
    
    def analyze_all_results(self):
        """Analyze all test result files"""
        print("Analyzing accessibility test results...\n")
        
        # Analyze each category
        self.analyze_color_contrast()
        self.analyze_image_alt_text()
        self.analyze_keyboard_navigation()
        self.analyze_touch_targets()
        self.analyze_heading_structure()
        self.analyze_form_labels()
        
        return self.generate_report()
    
    def analyze_color_contrast(self):
        """Analyze color contrast results"""
        file_path = self.results_dir / 'color_contrast_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict) and page_data.get('violations', 0) > 0:
                self.issues.append({
                    'category': 'Visual',
                    'severity': 'High',
                    'page': page_name,
                    'issue': f"Color contrast violations found ({page_data['violations']} issues)",
                    'wcag': '1.4.3 Contrast (Minimum)',
                    'recommendation': self._get_contrast_fix(page_data)
                })
    
    def analyze_image_alt_text(self):
        """Analyze image alt text results"""
        file_path = self.results_dir / 'image_alt_text_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict):
                missing = page_data.get('missing_alt', [])
                if missing:
                    self.issues.append({
                        'category': 'Visual',
                        'severity': 'High',
                        'page': page_name,
                        'issue': f"{len(missing)} images missing alt text",
                        'wcag': '1.1.1 Non-text Content',
                        'recommendation': self._get_alt_text_fix(missing)
                    })
    
    def analyze_keyboard_navigation(self):
        """Analyze keyboard navigation results"""
        file_path = self.results_dir / 'keyboard_navigation_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict):
                if not page_data.get('keyboard_accessible', True):
                    self.issues.append({
                        'category': 'Motor',
                        'severity': 'Critical',
                        'page': page_name,
                        'issue': 'Page not fully keyboard accessible',
                        'wcag': '2.1.1 Keyboard',
                        'recommendation': self._get_keyboard_fix()
                    })
    
    def analyze_touch_targets(self):
        """Analyze touch target size results"""
        file_path = self.results_dir / 'click_target_sizes_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict):
                compliance = page_data.get('compliance_rate', 100)
                if compliance < 90:
                    too_small = page_data.get('too_small', 0)
                    self.issues.append({
                        'category': 'Motor',
                        'severity': 'Medium',
                        'page': page_name,
                        'issue': f"{too_small} interactive elements below 44x44px",
                        'wcag': '2.5.5 Target Size',
                        'recommendation': self._get_touch_target_fix(page_data)
                    })
    
    def analyze_heading_structure(self):
        """Analyze heading structure results"""
        file_path = self.results_dir / 'consistent_layout_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict) and page_name != 'layout_consistency':
                if not page_data.get('proper_heading_order', True):
                    self.issues.append({
                        'category': 'Cognitive',
                        'severity': 'Medium',
                        'page': page_name,
                        'issue': 'Improper heading hierarchy',
                        'wcag': '1.3.1 Info and Relationships',
                        'recommendation': self._get_heading_fix(page_data)
                    })
                
                h1_count = page_data.get('h1_count', 0)
                if h1_count != 1:
                    self.issues.append({
                        'category': 'Cognitive',
                        'severity': 'Medium',
                        'page': page_name,
                        'issue': f"Page has {h1_count} h1 elements (should have exactly 1)",
                        'wcag': '1.3.1 Info and Relationships',
                        'recommendation': "Ensure each page has exactly one h1 element as the main heading"
                    })
    
    def analyze_form_labels(self):
        """Analyze form label results"""
        file_path = self.results_dir / 'screen_reader_compatibility_results.json'
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for page_name, page_data in data.items():
            if isinstance(page_data, dict):
                unlabeled = page_data.get('unlabeled_inputs', [])
                if unlabeled:
                    self.issues.append({
                        'category': 'Visual',
                        'severity': 'High',
                        'page': page_name,
                        'issue': f"{len(unlabeled)} form inputs without labels",
                        'wcag': '3.3.2 Labels or Instructions',
                        'recommendation': self._get_label_fix(unlabeled)
                    })
    
    def _get_contrast_fix(self, data):
        """Generate contrast fix recommendation"""
        return """
Fix color contrast issues:
1. Review elements with insufficient contrast
2. Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
3. Adjust colors to meet 4.5:1 ratio for normal text, 3:1 for large text
4. Update CSS variables in design-system.css
5. Test with high contrast mode

Example fix:
```css
/* Before: Insufficient contrast */
.text-muted { color: #999; }

/* After: Meets WCAG AA */
.text-muted { color: #6c757d; }
```
"""
    
    def _get_alt_text_fix(self, missing_images):
        """Generate alt text fix recommendation"""
        return f"""
Add alt text to images:
1. Review {len(missing_images)} images without alt attributes
2. Add descriptive alt text for informative images
3. Use alt="" for decorative images
4. Include context in alt text

Example fixes:
```html
<!-- Informative image -->
<img src="logo.png" alt="Stock Portfolio Platform Logo">

<!-- Decorative image -->
<img src="divider.png" alt="">

<!-- Functional image (button) -->
<img src="search.png" alt="Search">
```

Images to fix:
{chr(10).join(f'- {img}' for img in missing_images[:5])}
"""
    
    def _get_keyboard_fix(self):
        """Generate keyboard navigation fix recommendation"""
        return """
Improve keyboard navigation:
1. Ensure all interactive elements are focusable (tabindex="0" or native focusable elements)
2. Remove tabindex values greater than 0
3. Add keyboard event handlers where needed
4. Test tab order is logical
5. Ensure custom widgets support keyboard interaction

Example fixes:
```html
<!-- Make div clickable and keyboard accessible -->
<div role="button" tabindex="0" onclick="handleClick()" onkeypress="handleKeyPress(event)">
  Click me
</div>

<!-- Better: Use native button -->
<button onclick="handleClick()">Click me</button>
```

```javascript
// Handle keyboard activation
function handleKeyPress(event) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleClick();
  }
}
```
"""
    
    def _get_touch_target_fix(self, data):
        """Generate touch target fix recommendation"""
        too_small_details = data.get('too_small_details', [])
        return f"""
Increase touch target sizes:
1. Ensure all interactive elements are at least 44x44px
2. Add padding to small buttons and links
3. Increase spacing between adjacent targets
4. Test on mobile devices

Example fixes:
```css
/* Minimum touch target size */
button, a, input[type="button"], input[type="submit"] {{
  min-width: 44px;
  min-height: 44px;
  padding: 12px 16px;
}}

/* Increase link padding */
a {{
  padding: 8px 4px;
  display: inline-block;
}}
```

Elements to fix:
{chr(10).join(f"- {elem.get('tag', 'unknown')} ({elem.get('width', 0)}x{elem.get('height', 0)}px)" for elem in too_small_details[:5])}
"""
    
    def _get_heading_fix(self, data):
        """Generate heading structure fix recommendation"""
        heading_levels = data.get('heading_levels', [])
        return f"""
Fix heading hierarchy:
1. Start with h1 for main page title
2. Use h2 for major sections
3. Use h3 for subsections
4. Don't skip heading levels
5. Only one h1 per page

Current heading structure: {heading_levels}

Example fix:
```html
<!-- Before: Skips levels -->
<h1>Dashboard</h1>
<h3>Portfolio Summary</h3>

<!-- After: Proper hierarchy -->
<h1>Dashboard</h1>
<h2>Portfolio Summary</h2>
<h3>Holdings</h3>
```
"""
    
    def _get_label_fix(self, unlabeled):
        """Generate form label fix recommendation"""
        return f"""
Add labels to form inputs:
1. Use <label> elements with for attribute
2. Or use aria-label for inputs
3. Or wrap input in label
4. Provide clear, descriptive labels

Example fixes:
```html
<!-- Method 1: Label with for attribute -->
<label for="email">Email Address</label>
<input type="email" id="email" name="email">

<!-- Method 2: aria-label -->
<input type="search" aria-label="Search stocks" placeholder="Search...">

<!-- Method 3: Wrapped label -->
<label>
  Password
  <input type="password" name="password">
</label>
```

Unlabeled inputs to fix:
{chr(10).join(f"- {inp.get('type', 'text')} input (id: {inp.get('id', 'none')})" for inp in unlabeled[:5])}
"""
    
    def generate_report(self):
        """Generate comprehensive improvement report"""
        report_path = config.REPORTS_DIR / 'ACCESSIBILITY_IMPROVEMENTS.md'
        
        with open(report_path, 'w') as f:
            f.write("# Accessibility Improvements Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Issues Found:** {len(self.issues)}\n\n")
            
            # Summary by severity
            severity_counts = {}
            for issue in self.issues:
                severity = issue['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            f.write("## Issues by Severity\n\n")
            for severity in ['Critical', 'High', 'Medium', 'Low']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    f.write(f"- **{severity}:** {count} issues\n")
            f.write("\n")
            
            # Summary by category
            category_counts = {}
            for issue in self.issues:
                category = issue['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            f.write("## Issues by Category\n\n")
            for category, count in category_counts.items():
                f.write(f"- **{category}:** {count} issues\n")
            f.write("\n")
            
            # Detailed issues
            f.write("## Detailed Issues and Recommendations\n\n")
            
            for i, issue in enumerate(self.issues, 1):
                f.write(f"### {i}. {issue['issue']}\n\n")
                f.write(f"**Page:** {issue['page']}\n\n")
                f.write(f"**Category:** {issue['category']}\n\n")
                f.write(f"**Severity:** {issue['severity']}\n\n")
                f.write(f"**WCAG Criterion:** {issue['wcag']}\n\n")
                f.write(f"**Recommendation:**\n{issue['recommendation']}\n\n")
                f.write("---\n\n")
            
            # Implementation checklist
            f.write("## Implementation Checklist\n\n")
            f.write("### Critical Issues (Fix Immediately)\n\n")
            for issue in [i for i in self.issues if i['severity'] == 'Critical']:
                f.write(f"- [ ] {issue['page']}: {issue['issue']}\n")
            f.write("\n")
            
            f.write("### High Priority Issues\n\n")
            for issue in [i for i in self.issues if i['severity'] == 'High']:
                f.write(f"- [ ] {issue['page']}: {issue['issue']}\n")
            f.write("\n")
            
            f.write("### Medium Priority Issues\n\n")
            for issue in [i for i in self.issues if i['severity'] == 'Medium']:
                f.write(f"- [ ] {issue['page']}: {issue['issue']}\n")
            f.write("\n")
            
            # Next steps
            f.write("## Next Steps\n\n")
            f.write("1. Review all issues and recommendations above\n")
            f.write("2. Prioritize fixes based on severity\n")
            f.write("3. Implement fixes in the codebase\n")
            f.write("4. Re-run accessibility tests to verify fixes\n")
            f.write("5. Test with real assistive technology\n")
            f.write("6. Document accessibility features\n\n")
            
            # Resources
            f.write("## Resources\n\n")
            f.write("- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)\n")
            f.write("- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)\n")
            f.write("- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)\n")
            f.write("- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)\n")
        
        print(f"\n✓ Improvement report generated: {report_path}")
        print(f"✓ Found {len(self.issues)} accessibility issues")
        print(f"✓ Review the report for detailed recommendations")
        
        return report_path


def main():
    """Main function"""
    print("=" * 60)
    print("ACCESSIBILITY IMPROVEMENTS ANALYZER")
    print("=" * 60)
    print()
    
    analyzer = AccessibilityAnalyzer()
    report_path = analyzer.analyze_all_results()
    
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nOpen the report to see detailed recommendations:")
    print(f"  {report_path}")
    print()


if __name__ == '__main__':
    main()
