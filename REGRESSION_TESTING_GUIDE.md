# Regression Testing Quick Reference Guide

## Quick Commands

### Run All Tests
```bash
python run_all_regression_tests.py all
```

### Run Individual Suites
```bash
# Smoke tests (< 2 min)
python tests/test_smoke/run_smoke_tests.py

# Sanity tests (< 15 min)
python tests/test_sanity/run_sanity_tests.py

# Full regression (< 2 hours)
python run_all_regression_tests.py full
```

### Run Specific Test Categories
```bash
# Critical path tests
pytest tests/test_regression/test_critical_paths.py -v -m critical

# High-risk area tests
pytest tests/test_regression/test_high_risk_areas.py -v -m high_risk

# All regression tests
pytest tests/test_regression/ -v -m regression
```

## When to Run Which Tests

### After Every Deployment
1. **Smoke Tests** (2 min) - Verify basic functionality
2. **Sanity Tests** (15 min) - Verify changed modules

### Before Every Release
1. **Smoke Tests** (2 min)
2. **Sanity Tests** (15 min)
3. **Critical Path Tests** (20 min)
4. **High-Risk Tests** (30 min)
5. **Full Regression** (2 hours)

### After Major Changes
1. **Smoke Tests** (2 min)
2. **Sanity Tests** (15 min)
3. **Full Regression** (2 hours)

### Daily/Scheduled
- **Full Regression Suite** (2 hours) - Run nightly

## Test Suite Overview

| Suite | Duration | Purpose | When to Run |
|-------|----------|---------|-------------|
| Smoke | < 2 min | Basic functionality check | After every deployment |
| Sanity | < 15 min | Changed modules validation | After every deployment |
| Critical Path | < 20 min | Essential workflows | Before releases |
| High-Risk | < 30 min | Prone-to-break areas | Before releases |
| Full Regression | < 2 hours | Comprehensive testing | Before major releases |

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only smoke tests
pytest -m smoke

# Run only sanity tests
pytest -m sanity

# Run only critical path tests
pytest -m critical

# Run only high-risk tests
pytest -m high_risk

# Run all regression tests
pytest -m regression

# Run full regression suite
pytest -m full
```

## CI/CD Integration

### GitHub Actions Triggers

- **Push/PR to main/develop**: Smoke + Sanity tests
- **Daily at 2 AM**: Full regression suite
- **Manual trigger**: Any suite via workflow_dispatch

### Manual Trigger
1. Go to Actions tab in GitHub
2. Select "Regression Tests" workflow
3. Click "Run workflow"
4. Select suite to run
5. Click "Run workflow" button

## Test Results

### Location
- Test results: `test_results/`
- Coverage reports: `htmlcov/`
- CI/CD artifacts: GitHub Actions artifacts

### Viewing Results

```bash
# View coverage report
open htmlcov/index.html

# View JSON report
cat test_results/regression_report_*.json | jq

# View latest report
ls -t test_results/regression_report_*.json | head -1 | xargs cat | jq
```

## Common Issues

### Tests Failing

1. **Database issues**: Check test database configuration
2. **Missing fixtures**: Verify test data setup
3. **Dependencies**: Run `pip install -r requirements.txt`
4. **Environment**: Check `.env` file configuration

### Slow Tests

1. **Profile**: `pytest --durations=10`
2. **Optimize**: Review slow tests and optimize
3. **Parallel**: Use `pytest -n auto` (requires pytest-xdist)

### Flaky Tests

1. **Isolate**: Run test individually
2. **Review**: Check for race conditions
3. **Retry**: Use `pytest --reruns 3`

## Performance Targets

| Metric | Target |
|--------|--------|
| Smoke Tests | < 2 minutes |
| Sanity Tests | < 15 minutes |
| Critical Path | < 20 minutes |
| High-Risk | < 30 minutes |
| Full Regression | < 2 hours |
| Page Load | < 3 seconds |
| Order Processing | < 5 seconds |
| API Response | < 1 second |

## Coverage Goals

| Area | Target |
|------|--------|
| Overall | > 85% |
| Critical Paths | 100% |
| High-Risk Areas | > 95% |
| Services | > 90% |
| Models | > 90% |
| Routes | > 85% |

## Best Practices

### Writing Tests
1. ✅ Test real user scenarios
2. ✅ Use descriptive test names
3. ✅ One assertion per test (when possible)
4. ✅ Use appropriate markers
5. ✅ Clean up test data
6. ❌ Don't test implementation details
7. ❌ Don't use sleep() for timing
8. ❌ Don't hardcode test data

### Running Tests
1. ✅ Run smoke tests first
2. ✅ Run locally before pushing
3. ✅ Review failures immediately
4. ✅ Keep tests fast
5. ✅ Run full suite before releases
6. ❌ Don't skip failing tests
7. ❌ Don't ignore flaky tests
8. ❌ Don't commit broken tests

## Troubleshooting Commands

```bash
# Run single test
pytest tests/test_regression/test_critical_paths.py::TestUserRegistrationAndLogin::test_user_can_register_and_login -v

# Run with verbose output
pytest tests/test_regression/ -vv

# Run with print statements
pytest tests/test_regression/ -s

# Run with coverage
pytest tests/test_regression/ --cov=app --cov-report=html

# Run and stop on first failure
pytest tests/test_regression/ -x

# Run and show local variables on failure
pytest tests/test_regression/ -l

# Run with profiling
pytest tests/test_regression/ --durations=10

# Run in parallel (requires pytest-xdist)
pytest tests/test_regression/ -n auto
```

## Getting Help

1. **Documentation**: See `tests/test_regression/README.md`
2. **Test Code**: Review test files for examples
3. **CI/CD Logs**: Check GitHub Actions logs
4. **Team**: Contact development team

## Quick Checklist

### Before Committing
- [ ] Run smoke tests locally
- [ ] Run sanity tests locally
- [ ] All tests pass
- [ ] No new warnings
- [ ] Coverage maintained or improved

### Before Deploying
- [ ] Smoke tests pass in CI
- [ ] Sanity tests pass in CI
- [ ] No critical failures
- [ ] Review test reports
- [ ] Verify coverage

### Before Releasing
- [ ] All test suites pass
- [ ] Full regression complete
- [ ] Performance targets met
- [ ] Coverage goals met
- [ ] No known issues

## Resources

- **Test Suite**: `tests/test_regression/`
- **Smoke Tests**: `tests/test_smoke/`
- **Sanity Tests**: `tests/test_sanity/`
- **CI/CD Config**: `.github/workflows/regression-tests.yml`
- **Main Runner**: `run_all_regression_tests.py`
- **Documentation**: `tests/test_regression/README.md`
