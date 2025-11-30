"""
Pytest Configuration
Fixtures and configuration for testing
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Company, Wallet, Holdings, Order, Transaction, Dividend, Broker
from app.services.auth_service import AuthService


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()
        db.session.close()


@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user"""
    with app.app_context():
        auth_service = AuthService()
        user, _ = auth_service.register_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User'
        )
        db.session.commit()
        # Store password for authentication tests
        user._test_password = 'TestPass123!'
        yield user
        # Cleanup
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture(scope='function')
def test_admin(app):
    """Create an admin user"""
    with app.app_context():
        auth_service = AuthService()
        user, _ = auth_service.register_user(
            email='admin@example.com',
            password='AdminPass123!',
            full_name='Admin User'
        )
        user.is_admin = True
        db.session.commit()
        # Store password for authentication tests
        user._test_password = 'AdminPass123!'
        yield user
        # Cleanup
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture(scope='function')
def admin_user(app):
    """Alias for test_admin for backward compatibility"""
    with app.app_context():
        auth_service = AuthService()
        user, _ = auth_service.register_user(
            email='admin2@example.com',
            password='Admin123!@#',
            full_name='Admin User 2'
        )
        user.is_admin = True
        db.session.commit()
        yield user
        # Cleanup
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture(scope='function')
def test_company(app):
    """Create a test company with price history"""
    with app.app_context():
        from datetime import datetime
        from decimal import Decimal
        from app.models import PriceHistory
        import uuid
        
        # Generate unique symbol to avoid conflicts
        unique_symbol = f"TST{uuid.uuid4().hex[:5].upper()}"
        
        company = Company(
            symbol=unique_symbol,
            company_name='Test Company Inc.',
            sector='Technology',
            industry='Software',
            market_cap=1000000000,
            description='A test company',
            is_active=True
        )
        db.session.add(company)
        db.session.flush()  # Get company_id
        
        # Add price history so orders can fetch current price
        price_history = PriceHistory(
            company_id=company.company_id,
            date=datetime.now().date(),
            open=Decimal('150.00'),
            high=Decimal('155.00'),
            low=Decimal('148.00'),
            close=Decimal('152.00'),
            adjusted_close=Decimal('152.00'),
            volume=1000000
        )
        db.session.add(price_history)
        db.session.commit()
        
        yield company
        
        # Cleanup
        try:
            PriceHistory.query.filter_by(company_id=company.company_id).delete()
            db.session.delete(company)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture(scope='function')
def test_wallet(app, test_user):
    """Create a test wallet for user"""
    with app.app_context():
        wallet = Wallet.query.filter_by(user_id=test_user.user_id).first()
        if not wallet:
            wallet = Wallet(
                user_id=test_user.user_id,
                balance=Decimal('100000.00'),
                currency='USD',
                total_deposited=Decimal('100000.00'),
                total_withdrawn=Decimal('0.00')
            )
            db.session.add(wallet)
            db.session.commit()
        yield wallet


@pytest.fixture(scope='function')
def test_holding(app, test_user, test_company):
    """Create a test holding"""
    with app.app_context():
        holding = Holdings(
            user_id=test_user.user_id,
            company_id=test_company.company_id,
            quantity=100,
            average_purchase_price=Decimal('150.00'),
            total_invested=Decimal('15000.00')
        )
        db.session.add(holding)
        db.session.commit()
        yield holding
        # Cleanup
        db.session.delete(holding)
        db.session.commit()


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.user_id)
    return client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    """Create an authenticated admin client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.user_id)
    return client
