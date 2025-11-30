# Testing Documentation

## Overview

This directory contains comprehensive tests for the Stock Portfolio Management Platform. The test suite includes unit tests, integration tests, and API endpoint tests to ensure code quality and functionality.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── test_models/                # Unit tests for database models
│   ├── test_user.py
│   ├── test_wallet.py
│   ├── test_holdings.py
│   └── test_order.py
├── test_services/              # Unit tests for business logic services
│   ├── test_auth_service.py
│   ├── test_portfolio_service.py
│   └── test_transaction_engine.py
├── test_routes/                # Tests for API endpoints
│   ├── test_auth_routes.py
│   ├── test_portfolio_routes.py
│   ├── test_order_routes.py
│   └── test_admin_routes.py
└── test_integration/           # Integration tests for complete workflows
    ├── test_buy_order_flow.py
    └── test_sell_order_flow.py
```

## Setup

### Install Testing Dependencies

```bash
pip install pytest pytest-flask pytest-cov
```

Or install all dependencies including testing:

```bash
pip install -r requirements.txt
```

### Configuration

The test suite uses an in-memory SQLite database configured in `app/config.py` under `TestingConfig`. This ensures tests run quickly and don't affect the production database.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only model tests
pytest -m models

# Run only service tests
pytest -m services

# Run only route tests
pytest -m routes
```

### Run Specific Test Files

```bash
# Run user model tests
pytest tests/test_models/test_user.py

# Run auth service tests
pytest tests/test_services/test_auth_service.py
```

### Run Specific Test Methods

```bash
pytest tests/test_models/test_user.py::TestUserModel::test_password_hashing
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with Coverage and Terminal Report

```bash
pytest --cov=app --cov-report=term-missing
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.models` - Model tests
- `@pytest.mark.services` - Service tests
- `@pytest.mark.routes` - Route/endpoint tests
- `@pytest.mark.slow` - Slow running tests

## Fixtures

Common fixtures are defined in `conftest.py`:

- `app` - Flask application instance with testing config
- `client` - Test client for making HTTP requests
- `db_session` - Database session with automatic rollback
- `test_user` - Pre-created test user
- `admin_user` - Pre-created admin user
- `test_company` - Pre-created test company
- `test_wallet` - Pre-created test wallet
- `test_holding` - Pre-created test holding
- `authenticated_client` - Test client with authenticated user
- `admin_client` - Test client with authenticated admin

## Writing New Tests

### Model Tests Example

```python
@pytest.mark.unit
@pytest.mark.models
class TestMyModel:
    def test_create_model(self, app):
        with app.app_context():
            # Your test code here
            pass
```

### Service Tests Example

```python
@pytest.mark.unit
@pytest.mark.services
class TestMyService:
    def test_service_method(self, app, test_user):
        with app.app_context():
            # Your test code here
            pass
```

### Route Tests Example

```python
@pytest.mark.unit
@pytest.mark.routes
class TestMyRoutes:
    def test_endpoint(self, authenticated_client):
        response = authenticated_client.get('/my-endpoint')
        assert response.status_code == 200
```

### Integration Tests Example

```python
@pytest.mark.integration
class TestCompleteFlow:
    def test_workflow(self, app, test_user):
        with app.app_context():
            # Test complete workflow
            pass
```

## Coverage Goals

- **Models**: 90%+ coverage
- **Services**: 85%+ coverage
- **Routes**: 80%+ coverage
- **Overall**: 85%+ coverage

## Continuous Integration

Tests should be run automatically on:
- Every commit
- Every pull request
- Before deployment

## Troubleshooting

### Database Errors

If you encounter database errors, ensure:
1. The testing config uses SQLite in-memory database
2. Database is properly initialized in fixtures
3. Transactions are properly rolled back

### Import Errors

If you encounter import errors:
1. Ensure you're running tests from the project root
2. Check that all dependencies are installed
3. Verify PYTHONPATH includes the project root

### Fixture Errors

If fixtures aren't working:
1. Check that `conftest.py` is in the tests directory
2. Ensure fixtures are properly scoped (session/function)
3. Verify cleanup code runs after tests

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test data
3. **Naming**: Use descriptive test names
4. **Assertions**: Use clear, specific assertions
5. **Coverage**: Aim for high coverage but focus on critical paths
6. **Speed**: Keep tests fast (use mocks for external services)
7. **Documentation**: Document complex test scenarios

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/latest/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html)
