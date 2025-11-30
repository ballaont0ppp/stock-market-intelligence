# Regression Testing Suite

Comprehensive regression testing framework for the Stock Portfolio Management Platform.

## Overview

This regression testing suite ensures that new changes don't break existing functionality. It consists of multiple test levels designed to catch regressions at different stages of development and deployment.

## Test Suites

### 1. Smoke Tests (`tests/test_smoke/`)
**Purpose**: Quick validation that the application is functional after deployment  
**Duration**: < 2 minutes  
**When to run**: After every deployment, before any other tests  
**Coverage**:
- Application starts successfully
- Database connection works
- User can login
- Dashboard loads
- Critical API endpoints respond
- Background jobs are configured

**Run command**:
```bash
python tests/test_smoke/run_smoke_tests.py
```

### 2. Sanity Tests (`tests/test_sanity/`)
**Purpose**: Validate changed modules and impacted functionality  
**Duration**: < 15 minutes  
**When to run**: After each deployment, after smoke tests pass  
**Coverage**:
- Authentication module
- Portfolio module
- Orders module
- Dashboard module
- Reports module
- Admin module
- API endpoints
- Core services
- Database models
- Input validation
- Error handling

**Run command**:
```bash
python tests/test_sanity/run_sanity_tests.py
```

### 3. Critical Path Tests (`tests/test_regression/test_critical_paths.py`)
**Purpose**: Verify essential user workflows  
**Duration**: 10-20 minutes  
**When to run**: Before releases, after major changes  
**Coverage**:
- User registration and login
- Complete buy order flow
- Complete sell order flow
- Portfolio viewing
- Wallet operations
- Prediction service
- Admin access
- Data integrity constraints

**Run command**:
```bash
pytest tests/test_regression/test_critical_paths.py -v -m critical
```

### 4. High-Risk Area Tests (`tests/test_regression/test_high_risk_areas.py`)
**Purpose**: Test areas prone to breaking or with high impact  
**Duration**: 15-30 minutes  
**When to run**: Before releases, after changes to critical areas  
**Coverage**:
- Concurrent transactions
- Transaction rollback
- Security constraints
- Data consistency
- Error handling
- Session management
- Database constraints

**Run command**:
```bash
pytest tests/test_regression/test_high_risk_areas.py -v -m high_risk
```

### 5. Full Regression Suite (`tests/test_regression/test_full_regression.py`)
**Purpose**: Comprehensive testing of all functionality  
**Duration**: < 2 hours  
**When to run**: Before major releases, after significant changes  
**Coverage**:
- Complete user journeys
- All authentication scenarios
- All portfolio operations
- All order scenarios
- All admin operations
- Data integrity across operations
- Performance regression
- Security regression

**Run command**:
```bash
python run_all_regression_tests.py full
```

## Running Tests

### Quick Start

Run all regression tests:
```bash
python run_all_regression_tests.py all
```

Run specific suite:
```bash
python run_all_regression_tests.py smoke
python run_all_regression_tests.py sanity
python run_all_regression_tests.py full
```

### Using pytest directly

Run all regression tests:
```bash
pytest tests/test_regression/ -v -m regression
```

Run critical path tests only:
```bash
pytest tests/test_regression/ -v -m critical
```

Run high-risk tests only:
```bash
pytest tests/test_regression/ -v -m high_risk
```

Run with coverage:
```bash
pytest tests/test_regression/ -v -m regression --cov=app --cov-report=html
```

## Test Markers

The following pytest markers are available:

- `@pytest.mark.regression` - All regression tests
- `@pytest.mark.critical` - Critical path tests
- `@pytest.mark.high_risk` - High-risk area tests
- `@pytest.mark.smoke` - Smoke tests
- `@pytest.mark.sanity` - Sanity tests
- `@pytest.mark.full` - Full regression tests

## CI/CD Integration

### GitHub Actions

The regression test suite is integrated with GitHub Actions:

- **On Push/PR**: Runs smoke and sanity tests
- **Daily Schedule**: Runs full regression suite at 2 AM
- **Manual Trigger**: Can run any suite via workflow_dispatch

Configuration: `.github/workflows/regression-tests.yml`

### Running in CI/CD

```yaml
# Example CI/CD configuration
- name: Run Smoke Tests
  run: python tests/test_smoke/run_smoke_tests.py
  timeout-minutes: 5

- name: Run Sanity Tests
  run: python tests/test_sanity/run_sanity_tests.py
  timeout-minutes: 20

- name: Run Full Regression
  run: python run_all_regression_tests.py full --report
  timeout-minutes: 150
```

## Test Data

### Fixtures

Regression-specific fixtures are defined in `tests/test_regression/conftest.py`:

- `regression_test_user` - User with specific state for predictable tests
- `regression_test_companies` - Multiple test companies with price history
- `regression_test_holdings` - Pre-configured holdings
- `admin_user` - Admin user for testing admin functionality
- `regression_baseline_data` - Baseline data for comparison
- `performance_baseline` - Performance metrics baseline

### Test Database

Tests use an in-memory SQLite database configured in `conftest.py`. The database is:
- Created fresh for each test session
- Populated with required test data
- Cleaned up after tests complete

## Best Practices

### Writing Regression Tests

1. **Test Real Scenarios**: Focus on actual user workflows
2. **Be Specific**: Test one thing per test method
3. **Use Descriptive Names**: Test names should describe what they verify
4. **Include Assertions**: Always verify expected outcomes
5. **Clean Up**: Use fixtures for setup and teardown
6. **Mark Appropriately**: Use correct pytest markers

### Example Test

```python
@pytest.mark.regression
@pytest.mark.critical
def test_user_can_buy_stock(self, auth_client, test_user, test_company, db):
    """Test user can successfully purchase stock"""
    initial_balance = test_user.wallet.balance
    
    # Submit buy order
    response = auth_client.post('/orders/buy', data={
        'symbol': test_company.symbol,
        'quantity': 10,
        'csrf_token': 'test_token'
    }, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    
    # Verify order created
    order = Order.query.filter_by(
        user_id=test_user.user_id,
        company_id=test_company.company_id
    ).first()
    assert order is not None
    assert order.order_status == 'COMPLETED'
    
    # Verify wallet updated
    db.session.refresh(test_user.wallet)
    assert test_user.wallet.balance < initial_balance
```

## Troubleshooting

### Tests Failing

1. **Check test database**: Ensure test database is properly configured
2. **Review fixtures**: Verify test data is being created correctly
3. **Check dependencies**: Ensure all required packages are installed
4. **Review logs**: Check application logs for errors
5. **Run in isolation**: Run failing test individually to isolate issue

### Slow Tests

1. **Profile tests**: Use `pytest --durations=10` to find slow tests
2. **Optimize fixtures**: Reuse fixtures where possible
3. **Mock external calls**: Mock API calls to external services
4. **Use test database**: Ensure using in-memory database for tests

### Flaky Tests

1. **Check for race conditions**: Ensure proper synchronization
2. **Review test data**: Ensure consistent test data setup
3. **Check external dependencies**: Mock or stub external services
4. **Add retries**: Use pytest-rerunfailures for flaky tests

## Reporting

### Test Reports

Test results are saved to `test_results/` directory:

- `regression_report_TIMESTAMP.json` - Detailed test results
- `htmlcov/` - Coverage reports (when run with --cov)

### Viewing Reports

Coverage report:
```bash
open htmlcov/index.html
```

JSON report:
```bash
cat test_results/regression_report_*.json | jq
```

## Maintenance

### Adding New Tests

1. Identify the test category (smoke/sanity/critical/high-risk/full)
2. Create test in appropriate file
3. Add appropriate pytest markers
4. Update this README if adding new test suite
5. Run tests locally before committing

### Updating Baselines

When expected behavior changes:

1. Update test assertions
2. Update performance baselines in `conftest.py`
3. Document changes in commit message
4. Review with team before merging

## Performance Targets

- **Smoke Tests**: < 2 minutes
- **Sanity Tests**: < 15 minutes
- **Critical Path Tests**: < 20 minutes
- **High-Risk Tests**: < 30 minutes
- **Full Regression**: < 2 hours

## Coverage Goals

- **Overall Coverage**: > 85%
- **Critical Paths**: 100%
- **High-Risk Areas**: > 95%
- **Services**: > 90%
- **Models**: > 90%

## Support

For questions or issues with the regression test suite:

1. Check this README
2. Review test code and comments
3. Check CI/CD logs
4. Contact the development team

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Markers](https://docs.pytest.org/en/stable/example/markers.html)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
