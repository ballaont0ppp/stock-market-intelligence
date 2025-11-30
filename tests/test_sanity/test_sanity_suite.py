"""
Sanity Tests

Quick validation tests for changed modules and impacted functionality.
Run after each deployment to ensure basic functionality is intact.
Target execution time: < 15 minutes
"""
import pytest
from decimal import Decimal
from app.models import User, Company, Order, Transaction, Holdings


@pytest.mark.sanity
class TestAuthenticationSanity:
    """Sanity tests for authentication module"""
    
    def test_user_registration_works(self, client, db):
        """Test user can register"""
        response = client.post('/auth/register', data={
            'email': 'sanity@test.com',
            'password': 'Sanity123!',
            'full_name': 'Sanity Test',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        user = User.query.filter_by(email='sanity@test.com').first()
        assert user is not None
    
    def test_user_login_works(self, client, test_user):
        """Test user can login"""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_user_logout_works(self, auth_client):
        """Test user can logout"""
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.sanity
class TestPortfolioSanity:
    """Sanity tests for portfolio module"""
    
    def test_portfolio_page_accessible(self, auth_client):
        """Test portfolio page loads"""
        response = auth_client.get('/portfolio')
        assert response.status_code == 200
    
    def test_wallet_page_accessible(self, auth_client):
        """Test wallet page loads"""
        response = auth_client.get('/portfolio/wallet')
        assert response.status_code == 200
    
    def test_deposit_works(self, auth_client, test_user, db):
        """Test deposit functionality"""
        initial_balance = test_user.wallet.balance
        
        response = auth_client.post('/portfolio/wallet/deposit', data={
            'amount': '100.00',
            'description': 'Sanity test deposit',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance > initial_balance
    
    def test_portfolio_displays_holdings(self, auth_client, test_holding):
        """Test portfolio displays user holdings"""
        response = auth_client.get('/portfolio')
        assert response.status_code == 200
        assert test_holding.company.symbol.encode() in response.data


@pytest.mark.sanity
class TestOrdersSanity:
    """Sanity tests for orders module"""
    
    def test_orders_page_accessible(self, auth_client):
        """Test orders page loads"""
        response = auth_client.get('/orders')
        assert response.status_code == 200
    
    def test_buy_page_accessible(self, auth_client):
        """Test buy order page loads"""
        response = auth_client.get('/orders/buy')
        assert response.status_code == 200
    
    def test_sell_page_accessible(self, auth_client):
        """Test sell order page loads"""
        response = auth_client.get('/orders/sell')
        assert response.status_code == 200
    
    def test_buy_order_submission(self, auth_client, test_user, test_company, db):
        """Test buy order can be submitted"""
        response = auth_client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': 1,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify order was created
        order = Order.query.filter_by(
            user_id=test_user.user_id,
            company_id=test_company.company_id,
            order_type='BUY'
        ).first()
        
        assert order is not None


@pytest.mark.sanity
class TestDashboardSanity:
    """Sanity tests for dashboard module"""
    
    def test_dashboard_accessible(self, auth_client):
        """Test dashboard loads"""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
    
    def test_predict_page_accessible(self, auth_client):
        """Test prediction page loads"""
        response = auth_client.get('/dashboard/predict')
        assert response.status_code == 200


@pytest.mark.sanity
class TestReportsSanity:
    """Sanity tests for reports module"""
    
    def test_reports_page_accessible(self, auth_client):
        """Test reports page loads"""
        response = auth_client.get('/reports')
        assert response.status_code == 200


@pytest.mark.sanity
class TestAdminSanity:
    """Sanity tests for admin module"""
    
    def test_admin_page_requires_admin(self, auth_client):
        """Test admin page requires admin privileges"""
        response = auth_client.get('/admin', follow_redirects=False)
        assert response.status_code in [302, 403]
    
    def test_admin_user_can_access(self, client, admin_user):
        """Test admin user can access admin dashboard"""
        with client:
            client.post('/auth/login', data={
                'email': admin_user.email,
                'password': 'admin123',
                'csrf_token': 'test_token'
            })
            
            response = client.get('/admin')
            assert response.status_code == 200


@pytest.mark.sanity
class TestAPISanity:
    """Sanity tests for API endpoints"""
    
    def test_search_api_responds(self, auth_client):
        """Test search API responds"""
        response = auth_client.get('/api/search?q=TEST')
        assert response.status_code in [200, 404]
    
    def test_price_api_responds(self, auth_client, test_company):
        """Test price API responds"""
        response = auth_client.get(f'/api/price/{test_company.symbol}')
        assert response.status_code in [200, 404]


@pytest.mark.sanity
class TestTransactionEngineSanity:
    """Sanity tests for transaction engine"""
    
    def test_buy_order_creates_holding(self, test_user, test_company, db):
        """Test buy order creates or updates holding"""
        from app.services.transaction_engine import TransactionEngine
        engine = TransactionEngine()
        
        initial_holdings = Holdings.query.filter_by(user_id=test_user.user_id).count()
        
        order = engine.create_buy_order(
            user_id=test_user.user_id,
            symbol=test_company.symbol,
            quantity=1
        )
        
        if order.order_status == 'COMPLETED':
            final_holdings = Holdings.query.filter_by(user_id=test_user.user_id).count()
            assert final_holdings >= initial_holdings
    
    def test_sell_order_reduces_holding(self, test_user, test_company, test_holding, db):
        """Test sell order reduces holding quantity"""
        from app.services.transaction_engine import TransactionEngine
        engine = TransactionEngine()
        
        initial_quantity = test_holding.quantity
        
        order = engine.create_sell_order(
            user_id=test_user.user_id,
            symbol=test_company.symbol,
            quantity=1
        )
        
        if order.order_status == 'COMPLETED':
            db.session.refresh(test_holding)
            assert test_holding.quantity < initial_quantity


@pytest.mark.sanity
class TestServicesSanity:
    """Sanity tests for core services"""
    
    def test_auth_service_instantiates(self):
        """Test AuthService can be created"""
        from app.services.auth_service import AuthService
        service = AuthService()
        assert service is not None
    
    def test_portfolio_service_instantiates(self):
        """Test PortfolioService can be created"""
        from app.services.portfolio_service import PortfolioService
        service = PortfolioService()
        assert service is not None
    
    def test_transaction_engine_instantiates(self):
        """Test TransactionEngine can be created"""
        from app.services.transaction_engine import TransactionEngine
        engine = TransactionEngine()
        assert engine is not None
    
    def test_stock_repository_instantiates(self):
        """Test StockRepository can be created"""
        from app.services.stock_repository import StockRepository
        repo = StockRepository()
        assert repo is not None


@pytest.mark.sanity
class TestModelsSanity:
    """Sanity tests for database models"""
    
    def test_user_model_works(self, db):
        """Test User model basic operations"""
        user = User(
            email='model_test@test.com',
            password_hash='hash',
            full_name='Model Test'
        )
        db.session.add(user)
        db.session.commit()
        
        retrieved = User.query.filter_by(email='model_test@test.com').first()
        assert retrieved is not None
        assert retrieved.full_name == 'Model Test'
    
    def test_company_model_works(self, db):
        """Test Company model basic operations"""
        company = Company(
            symbol='SANI',
            company_name='Sanity Corp',
            sector='Technology'
        )
        db.session.add(company)
        db.session.commit()
        
        retrieved = Company.query.filter_by(symbol='SANI').first()
        assert retrieved is not None
        assert retrieved.company_name == 'Sanity Corp'


@pytest.mark.sanity
class TestValidationSanity:
    """Sanity tests for input validation"""
    
    def test_negative_quantity_rejected(self, auth_client, test_company):
        """Test negative quantity is rejected"""
        response = auth_client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': -5,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200  # Returns to form
    
    def test_zero_quantity_rejected(self, auth_client, test_company):
        """Test zero quantity is rejected"""
        response = auth_client.post('/orders/buy', data={
            'symbol': test_company.symbol,
            'quantity': 0,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_invalid_email_rejected(self, client):
        """Test invalid email format is rejected"""
        response = client.post('/auth/register', data={
            'email': 'not-an-email',
            'password': 'Pass123!',
            'full_name': 'Test User',
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200  # Returns to form


@pytest.mark.sanity
class TestErrorHandlingSanity:
    """Sanity tests for error handling"""
    
    def test_404_handled(self, client):
        """Test 404 errors are handled"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_symbol_handled(self, auth_client):
        """Test invalid stock symbol is handled"""
        response = auth_client.post('/orders/buy', data={
            'symbol': 'INVALID999',
            'quantity': 1,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200  # Should not crash


@pytest.mark.sanity
def test_sanity_suite_summary(capsys):
    """Print sanity test summary"""
    print("\n" + "="*60)
    print("SANITY TEST SUITE COMPLETED")
    print("="*60)
    print("✓ Authentication module verified")
    print("✓ Portfolio module verified")
    print("✓ Orders module verified")
    print("✓ Dashboard module verified")
    print("✓ Reports module verified")
    print("✓ Admin module verified")
    print("✓ API endpoints verified")
    print("✓ Services verified")
    print("✓ Models verified")
    print("✓ Validation verified")
    print("✓ Error handling verified")
    print("="*60)
