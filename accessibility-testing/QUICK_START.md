# Accessibility Testing - Quick Start Guide

Get started with accessibility testing in 5 minutes!

## Prerequisites

✓ Python 3.8+  
✓ Chrome or Firefox browser  
✓ Application running locally  
✓ Test user account  

## Quick Setup

### 1. Install Dependencies (2 minutes)

```bash
cd accessibility-testing
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env`:
```env
APP_URL=http://localhost:5000
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=TestPassword123!
```

### 3. Verify Setup (1 minute)

```bash
python verify_setup.py
```

Expected output:
```
✓ PASS: Python Version
✓ PASS: Dependencies
✓ PASS: Configuration
✓ PASS: Directories
✓ PASS: Browser Driver
✓ PASS: Application
```

### 4. Run Tests (1 minute)

```bash
python run_all_tests.py
```

## View Results

Open the generated report:
```
reports/accessibility_report.html
```

Or view the summary:
```
reports/ACCESSIBILITY_SUMMARY.md
```

## What Gets Tested?

### ✓ Visual Accessibility
- Color contrast ratios (4.5:1 minimum)
- Image alt text
- Text resizing up to 200%
- Screen reader compatibility
- Focus indicators

### ✓ Motor Accessibility
- Keyboard navigation
- Touch target sizes (44x44px)
- Focus visibility
- Skip navigation links
- Form accessibility

### ✓ Cognitive Accessibility
- Navigation clarity
- Layout consistency
- Error prevention
- Help documentation
- Language clarity

## Common Commands

```bash
# Run all tests
python run_all_tests.py

# Run specific category
pytest test_visual_accessibility.py -v
pytest test_motor_accessibility.py -v
pytest test_cognitive_accessibility.py -v

# Run single test
pytest test_visual_accessibility.py::TestVisualAccessibility::test_color_contrast_ratios -v

# Generate HTML report
pytest --html=reports/report.html --self-contained-html
```

## Quick Troubleshooting

### Tests fail to start?
```bash
# Verify setup again
python verify_setup.py

# Check if app is running
curl http://localhost:5000
```

### Browser driver issues?
```bash
# Reinstall webdriver-manager
pip install --upgrade webdriver-manager
```

### Authentication fails?
- Check credentials in `.env`
- Verify test user exists in database
- Try logging in manually first

## Next Steps

1. ✓ Review test results
2. ✓ Fix critical issues first
3. ✓ Re-run tests to verify fixes
4. ✓ Add to CI/CD pipeline
5. ✓ Test with real assistive technology

## Need Help?

- Check `README.md` for detailed documentation
- Review `config.py` for configuration options
- See test files for specific test details

## WCAG Compliance Checklist

After running tests, verify:

- [ ] All color contrasts meet 4.5:1 ratio
- [ ] All images have alt text
- [ ] All features work with keyboard only
- [ ] All interactive elements are 44x44px minimum
- [ ] All pages have proper heading hierarchy
- [ ] All forms have labels and help text
- [ ] Navigation is consistent across pages
- [ ] Focus indicators are visible
- [ ] No time-based interactions
- [ ] Language is clear and simple

## Success Criteria

Your application is accessible when:

✓ All automated tests pass  
✓ Manual keyboard navigation works  
✓ Screen reader announces content correctly  
✓ Users with disabilities can complete tasks  
✓ WCAG 2.1 Level AA compliance achieved  

---

**Ready to test?** Run `python run_all_tests.py` now!
