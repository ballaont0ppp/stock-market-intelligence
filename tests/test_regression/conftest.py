"""
Regression Test Fixtures and Configuration

Provides test data and fixtures specifically for regression testing.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.models import User, Company, Wallet, Holdings, PriceHistory


@pytest.fixture
def regression_test_user(db):
    """Create a test user with specific state for regression tests"""
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    
    user = auth_service.register_user(
        email='regression@test.com',
        password='RegressionTest123!',
        full_name='Regression Test User'
    )
    
    # Set specific wallet balance for predictable tests
    user.wallet.balance = Decimal('50000.00')
    db.session.commit()
    
    return user


@pytest.fixture
def regression_test_companies(db):
    """Create multiple test companies for regression tests"""
    companies = []
    
    symbols = ['REGR', 'TEST', 'DEMO']
    names = ['Regression Corp', 'Test Industries', 'Demo Systems']
    
    for symbol, name in zip(symbols, names):
        company = Company(
            symbol=symbol,
            company_name=name,
            sector='Technology',
            industry='Software',
            market_cap=1000000000,
            is_active=True
        )
        db.session.add(company)
        companies.append(company)
    
    db.session.commit()
    
    # Add price history for each company
    for company in companies:
        for i in range(30):  # 30 days of history
            date = datetime.now().date() - timedelta(days=i)
            price = PriceHistory(
                company_id=company.company_id,
                date=date,
                open=Decimal('100.00') + Decimal(str(i)),
                high=Decimal('105.00') + Decimal(str(i)),
                low=Decimal('95.00') + Decimal(str(i)),
                close=Decimal('102.00') + Decimal(str(i)),
                adjusted_close=Decimal('102.00') + Decimal(str(i)),
                volume=1000000
            )
            db.session.add(price)
    
    db.session.commit()
    return companies


@pytest.fixture
def regression_test_holdings(db, regression_test_user, regression_test_companies):
    """Create test holdings for regression tests"""
    holdings = []
    
    for i, company in enumerate(regression_test_companies[:2]):  # Holdings in first 2 companies
        holding = Holdings(
            user_id=regression_test_user.user_id,
            company_id=company.company_id,
            quantity=10 * (i + 1),  # 10, 20 shares
            average_purchase_price=Decimal('100.00'),
            total_invested=Decimal('100.00') * (10 * (i + 1))
        )
        db.session.add(holding)
        holdings.append(holding)
    
    db.session.commit()
    return holdings


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing admin functionality"""
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    
    admin = auth_service.register_user(
        email='admin@test.com',
        password='admin123',
        full_name='Admin User'
    )
    
    admin.is_admin = True
    db.session.commit()
    
    return admin


@pytest.fixture
def regression_baseline_data(db):
    """Create baseline data for regression comparison"""
    baseline = {
        'total_users': User.query.count(),
        'total_companies': Company.query.count(),
        'total_wallets': Wallet.query.count(),
        'timestamp': datetime.now()
    }
    return baseline


@pytest.fixture
def performance_baseline():
    """Baseline performance metrics for regression testing"""
    return {
        'max_page_load_time': 3.0,  # seconds
        'max_order_processing_time': 5.0,  # seconds
        'max_api_response_time': 1.0,  # seconds
        'max_query_time': 0.5  # seconds
    }
