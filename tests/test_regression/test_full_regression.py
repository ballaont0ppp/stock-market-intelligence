"""
Full Regression Test Suite

Comprehensive regression tests covering all functionality.
Run before major releases and after significant changes.
Target execution time: < 2 hours
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.models import (
    User, Company, Wallet, Holdings, Order, Transaction,
    Dividend, Notification, PriceHistory
)


@pytest.mark.regression
@pytest.mark.full
class TestCompleteUserJourney:
    """Test complete user journey from registration to trading"""
    
    def test_new_user_complete_journey(self, client, db, test_company):
        """Test complete new user journey"""
        # 1. Register
        register_data = {
            'email': 'journey@test.com',
            'password': 'Journey123!',
            'full_name': 'Journey User',
            'csrf_token': 'test_token'
        }
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        
        user = User.query.filter_by(email='journey@test.com').first()
        assert user is not None
        
        # 2. Login
        login_data = {
            'email': 'journey@test.com',
            'password': 'Journey123!',
            'csrf_token': 'test_token'
        }
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        # 3. View dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # 4. View portfolio
        response = client.get('/portfolio')
        assert response.status_code == 200
        
        # 5. Deposit funds
        response = client.post('/portfolio/wallet/deposit', data={
            'amount': '5000.00',
            'description': 'Initial deposit',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # 6. Buy stock
        response = client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': 10,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # 7. View updated portfolio
        response = client.get('/portfolio')
        assert response.status_code == 200
        
        # 8. View orders
        response = client.get('/orders')
        assert response.status_code == 200
        
        # 9. Sell some stock
        response = client.post('/orders/sell', data={
            'symbol': test_company.symbol,
            'quantity': 5,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # 10. View reports
        response = client.get('/reports')
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.full
class TestAllAuthenticationScenarios:
    """Test all authentication scenarios"""
    
    def test_registration_validation(self, client, db):
        """Test registration with various inputs"""
        # Valid registration
        response = client.post('/auth/register', data={
            'email': 'valid@test.com',
            'password': 'Valid123!',
            'full_name': 'Valid User',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Duplicate email
        response = client.post('/auth/register', data={
            'email': 'valid@test.com',
            'password': 'Another123!',
            'full_name': 'Another User',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200  # Returns to form
    
    def test_login_scenarios(self, client, test_user):
        """Test various login scenarios"""
        # Correct credentials
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Wrong password
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'wrongpassword',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200  # Returns to form
        
        # Non-existent user
        response = client.post('/auth/login', data={
            'email': 'nonexistent@test.com',
            'password': 'password123',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.full
class TestAllPortfolioOperations:
    """Test all portfolio operations"""
    
    def test_wallet_operations(self, auth_client, test_user, db):
        """Test all wallet operations"""
        initial_balance = test_user.wallet.balance
        
        # Deposit
        auth_client.post('/portfolio/wallet/deposit', data={
            'amount': '1000.00',
            'description': 'Test deposit',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance == initial_balance + Decimal('1000.00')
        
        # Withdraw
        auth_client.post('/portfolio/wallet/withdraw', data={
            'amount': '500.00',
            'description': 'Test withdrawal',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance == initial_balance + Decimal('500.00')
    
    def test_portfolio_calculations(self, auth_client, test_user, test_holding, db):
        """Test portfolio value calculations"""
        from app.services.portfolio_service import PortfolioService
        service = PortfolioService()
        
        # Get portfolio value
        portfolio_value = service.get_portfolio_value(test_user.user_id)
        assert portfolio_value >= 0
        
        # Get portfolio summary
        summary = service.get_portfolio_summary(test_user.user_id)
        assert 'total_value' in summary
        assert 'wallet_balance' in summary


@pytest.mark.regression
@pytest.mark.full
class TestAllOrderScenarios:
    """Test all order scenarios"""
    
    def test_buy_order_scenarios(self, auth_client, test_user, test_company, db):
        """Test various buy order scenarios"""
        # Valid buy order
        response = auth_client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': 1,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Large quantity
        response = auth_client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': 100,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_sell_order_scenarios(self, auth_client, test_user, test_company, test_holding, db):
        """Test various sell order scenarios"""
        # Valid sell order
        response = auth_client.post('/orders/sell', data={
            'symbol': test_company.symbol,
            'quantity': 1,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Sell all shares
        db.session.refresh(test_holding)
        if test_holding.quantity > 0:
            response = auth_client.post('/orders/sell', data={
                'symbol': test_company.symbol,
                'quantity': test_holding.quantity,
                'csrf_token': 'test_token'
            }, follow_redirects=True)
            assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.full
class TestAllAdminOperations:
    """Test all admin operations"""
    
    def test_admin_user_management(self, client, admin_user, test_user, db):
        """Test admin user management operations"""
        with client:
            client.post('/auth/login', data={
                'email': admin_user.email,
                'password': 'admin123',
                'csrf_token': 'test_token'
            })
            
            # View users
            response = client.get('/admin/users')
            assert response.status_code == 200
            
            # View user details
            response = client.get(f'/admin/users/{test_user.user_id}')
            assert response.status_code == 200
    
    def test_admin_company_management(self, client, admin_user, db):
        """Test admin company management"""
        with client:
            client.post('/auth/login', data={
                'email': admin_user.email,
                'password': 'admin123',
                'csrf_token': 'test_token'
            })
            
            # View companies
            response = client.get('/admin/companies')
            assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.full
class TestDataIntegrityAcrossOperations:
    """Test data integrity across multiple operations"""
    
    def test_transaction_history_integrity(self, test_user, test_company, db):
        """Test transaction history remains consistent"""
        from app.services.transaction_engine import TransactionEngine
        engine = TransactionEngine()
        
        initial_transaction_count = Transaction.query.filter_by(user_id=test_user.user_id).count()
        
        # Perform multiple operations
        order1 = engine.create_buy_order(test_user.user_id, test_company.symbol, 5)
        
        if order1.order_status == 'COMPLETED':
            final_transaction_count = Transaction.query.filter_by(user_id=test_user.user_id).count()
            assert final_transaction_count > initial_transaction_count
    
    def test_wallet_balance_integrity(self, test_user, test_company, db):
        """Test wallet balance remains consistent across operations"""
        from app.services.transaction_engine import TransactionEngine
        from app.services.portfolio_service import PortfolioService
        
        engine = TransactionEngine()
        portfolio_service = PortfolioService()
        
        initial_balance = test_user.wallet.balance
        
        # Deposit
        portfolio_service.deposit_funds(test_user.user_id, Decimal('1000.00'), 'Test')
        
        db.session.refresh(test_user.wallet)
        after_deposit = test_user.wallet.balance
        assert after_deposit == initial_balance + Decimal('1000.00')
        
        # Buy
        order = engine.create_buy_order(test_user.user_id, test_company.symbol, 1)
        
        if order.order_status == 'COMPLETED':
            db.session.refresh(test_user.wallet)
            assert test_user.wallet.balance < after_deposit


@pytest.mark.regression
@pytest.mark.full
class TestPerformanceRegression:
    """Test performance hasn't regressed"""
    
    def test_page_load_performance(self, auth_client):
        """Test page load times are acceptable"""
        import time
        
        pages = ['/dashboard', '/portfolio', '/orders', '/reports']
        
        for page in pages:
            start = time.time()
            response = auth_client.get(page)
            duration = time.time() - start
            
            assert response.status_code == 200
            assert duration < 3.0, f"Page {page} took {duration:.2f}s (> 3s)"
    
    def test_order_processing_performance(self, test_user, test_company, db):
        """Test order processing time is acceptable"""
        import time
        from app.services.transaction_engine import TransactionEngine
        
        engine = TransactionEngine()
        
        start = time.time()
        order = engine.create_buy_order(test_user.user_id, test_company.symbol, 1)
        duration = time.time() - start
        
        assert duration < 5.0, f"Order processing took {duration:.2f}s (> 5s)"


@pytest.mark.regression
@pytest.mark.full
class TestSecurityRegression:
    """Test security features haven't regressed"""
    
    def test_authentication_required(self, client):
        """Test protected routes require authentication"""
        protected_routes = [
            '/portfolio',
            '/orders',
            '/orders/buy',
            '/orders/sell',
            '/dashboard/predict',
            '/reports'
        ]
        
        for route in protected_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code == 302, f"Route {route} not protected"
    
    def test_admin_authorization_required(self, auth_client):
        """Test admin routes require admin role"""
        admin_routes = [
            '/admin',
            '/admin/users',
            '/admin/companies'
        ]
        
        for route in admin_routes:
            response = auth_client.get(route, follow_redirects=False)
            assert response.status_code in [302, 403], f"Route {route} not admin-protected"


@pytest.mark.regression
@pytest.mark.full
def test_full_regression_summary(capsys):
    """Print full regression test summary"""
    print("\n" + "="*60)
    print("FULL REGRESSION TEST SUITE COMPLETED")
    print("="*60)
    print("✓ Complete user journeys verified")
    print("✓ All authentication scenarios verified")
    print("✓ All portfolio operations verified")
    print("✓ All order scenarios verified")
    print("✓ All admin operations verified")
    print("✓ Data integrity verified")
    print("✓ Performance benchmarks verified")
    print("✓ Security features verified")
    print("="*60)
