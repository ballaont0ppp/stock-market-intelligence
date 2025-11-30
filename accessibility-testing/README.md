# Accessibility Testing Suite

Comprehensive accessibility testing framework for the Stock Portfolio Management Platform, ensuring WCAG 2.1 Level AA compliance.

## Overview

This testing suite validates that the application meets Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards across three main categories:

1. **Visual Accessibility** - Color contrast, text resizing, screen reader compatibility
2. **Motor Accessibility** - Keyboard navigation, focus indicators, touch target sizes
3. **Cognitive Accessibility** - Navigation clarity, consistent layout, error prevention

## Features

- Automated WCAG 2.1 Level AA compliance testing
- Color contrast ratio validation (4.5:1 minimum)
- Keyboard navigation testing
- Screen reader compatibility checks
- Touch target size validation (44x44px minimum)
- Text resizing tests (up to 200%)
- Semantic HTML structure validation
- ARIA attribute verification
- Comprehensive HTML and JSON reports

## Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser
- Application running at configured URL
- Test user account with credentials

## Installation

1. Navigate to the accessibility-testing directory:
```bash
cd accessibility-testing
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

4. Edit `.env` file with your configuration:
```env
APP_URL=http://localhost:5000
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=TestPassword123!
WCAG_LEVEL=AA
WCAG_VERSION=2.1
```

5. Verify setup:
```bash
python verify_setup.py
```

## Usage

### Run All Tests

```bash
python run_all_tests.py
```

This will:
- Execute all accessibility tests
- Generate HTML report in `reports/accessibility_report.html`
- Create JSON results in `results/` directory
- Generate summary report in `reports/ACCESSIBILITY_SUMMARY.md`

### Run Specific Test Categories

```bash
# Visual accessibility tests only
pytest test_visual_accessibility.py -v

# Motor accessibility tests only
pytest test_motor_accessibility.py -v

# Cognitive accessibility tests only
pytest test_cognitive_accessibility.py -v
```

### Run Specific Tests

```bash
# Test color contrast only
pytest test_visual_accessibility.py::TestVisualAccessibility::test_color_contrast_ratios -v

# Test keyboard navigation only
pytest test_motor_accessibility.py::TestMotorAccessibility::test_keyboard_navigation_all_features -v
```

### Generate Reports

```bash
# HTML report with detailed results
pytest --html=reports/accessibility_report.html --self-contained-html

# JSON output for CI/CD integration
pytest --json-report --json-report-file=reports/accessibility_report.json
```

## Test Categories

### Visual Accessibility Tests

| Test | Description | WCAG Criteria |
|------|-------------|---------------|
| Color Contrast | Validates 4.5:1 ratio for normal text, 3:1 for large text | 1.4.3 |
| Text Resizing | Ensures content works at 200% zoom | 1.4.4 |
| Image Alt Text | Verifies all images have alt attributes | 1.1.1 |
| Screen Reader | Tests ARIA labels and semantic HTML | 4.1.2 |
| High Contrast | Validates functionality in high contrast mode | 1.4.6 |
| Focus Indicators | Ensures visible focus indicators | 2.4.7 |

### Motor Accessibility Tests

| Test | Description | WCAG Criteria |
|------|-------------|---------------|
| Keyboard Navigation | All features accessible via keyboard | 2.1.1 |
| Focus Visibility | Focus indicators clearly visible | 2.4.7 |
| Touch Targets | Minimum 44x44px for interactive elements | 2.5.5 |
| No Time Limits | No time-based interactions | 2.2.1 |
| Skip Links | Skip navigation links present | 2.4.1 |
| Form Accessibility | Forms fully keyboard accessible | 2.1.1 |

### Cognitive Accessibility Tests

| Test | Description | WCAG Criteria |
|------|-------------|---------------|
| Navigation Clarity | Clear and consistent navigation | 3.2.3 |
| Layout Consistency | Consistent page structure | 3.2.4 |
| Error Prevention | Input validation and help text | 3.3.4 |
| Help Documentation | Contextual help available | 3.3.5 |
| Cognitive Load | Reasonable page complexity | 3.1.5 |
| Language Clarity | Clear language and lang attributes | 3.1.1 |

## Configuration Options

### WCAG Compliance Levels

```python
WCAG_LEVEL = 'AA'  # Options: A, AA, AAA
WCAG_VERSION = '2.1'  # Options: 2.0, 2.1, 2.2
```

### Browser Configuration

```python
BROWSER = 'chrome'  # Options: chrome, firefox, edge
HEADLESS_MODE = False  # Set to True for CI/CD
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
```

### Test Pages

Configure which pages to test in `config.py`:

```python
TEST_PAGES = [
    {'name': 'Home', 'path': '/', 'requires_auth': False},
    {'name': 'Dashboard', 'path': '/dashboard', 'requires_auth': True},
    # Add more pages...
]
```

## Understanding Results

### HTML Report

The HTML report (`reports/accessibility_report.html`) provides:
- Test execution summary
- Pass/fail status for each test
- Detailed error messages
- Screenshots on failure
- Execution time

### JSON Results

Individual test results are saved as JSON files in `results/`:
- `color_contrast_results.json` - Color contrast violations
- `keyboard_navigation_results.json` - Keyboard accessibility data
- `click_target_sizes_results.json` - Touch target measurements
- And more...

### Summary Report

The markdown summary (`reports/ACCESSIBILITY_SUMMARY.md`) includes:
- Overall compliance status
- Category-wise results
- Recommendations
- Action items

## Common Issues and Solutions

### Issue: Browser driver not found
**Solution:** Run `python verify_setup.py` to auto-install drivers

### Issue: Application not accessible
**Solution:** Ensure the app is running at the configured URL

### Issue: Authentication fails
**Solution:** Verify test user credentials in `.env` file

### Issue: Tests timeout
**Solution:** Increase timeout values in `config.py`:
```python
PAGE_LOAD_TIMEOUT = 60
ELEMENT_WAIT_TIMEOUT = 20
```

### Issue: Color contrast false positives
**Solution:** Review actual contrast ratios and adjust thresholds if needed

## Best Practices

1. **Run tests regularly** - Include in CI/CD pipeline
2. **Test with real users** - Automated tests don't replace user testing
3. **Use assistive technology** - Test with actual screen readers
4. **Fix critical issues first** - Prioritize by WCAG impact level
5. **Document fixes** - Keep track of accessibility improvements
6. **Maintain compliance** - Re-test after UI changes

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd accessibility-testing
          pip install -r requirements.txt
      - name: Run accessibility tests
        run: |
          cd accessibility-testing
          python run_all_tests.py
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: accessibility-reports
          path: accessibility-testing/reports/
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [axe Accessibility Testing](https://www.deque.com/axe/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test output and error messages
3. Consult WCAG documentation
4. Contact the development team

## License

This testing suite is part of the Stock Portfolio Management Platform project.
