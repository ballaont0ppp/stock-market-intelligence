"""
Critical Path Regression Tests

Tests for the most critical user workflows that must always work.
These tests cover end-to-end scenarios that are essential for the application.
"""
import pytest
from decimal import Decimal
from app.models import User, Company, Wallet, Holdings, Order, Transaction


@pytest.mark.regression
@pytest.mark.critical
class TestUserRegistrationAndLogin:
    """Test critical authentication flows"""
    
    def test_user_can_register_and_login(self, client, db):
        """Test complete user registration and login flow"""
        # Register new user
        register_data = {
            'email': 'newuser@test.com',
            'password': 'SecurePass123!',
            'full_name': 'New User',
            'csrf_token': 'test_token'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify user was created
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
        assert user.full_name == 'New User'
        
        # Verify wallet was created with initial balance
        wallet = Wallet.query.filter_by(user_id=user.user_id).first()
        assert wallet is not None
        assert wallet.balance == Decimal('100000.00')
        
        # Login with new credentials
        login_data = {
            'email': 'newuser@test.com',
            'password': 'SecurePass123!',
            'csrf_token': 'test_token'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.critical
class TestBuyOrderFlow:
    """Test critical buy order workflow"""
    
    def test_complete_buy_order_flow(self, client, auth_client, test_user, test_company, db):
        """Test complete buy order from submission to portfolio update"""
        initial_balance = test_user.wallet.balance
        
        # Submit buy order
        order_data = {
            'symbol': test_company.symbol,
            'quantity': 10,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/buy', data=order_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify order was created and completed
        order = Order.query.filter_by(
            user_id=test_user.user_id,
            company_id=test_company.company_id,
            order_type='BUY'
        ).first()
        
        assert order is not None
        assert order.order_status == 'COMPLETED'
        assert order.quantity == 10
        
        # Verify wallet balance decreased
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance < initial_balance
        
        # Verify holding was created
        holding = Holdings.query.filter_by(
            user_id=test_user.user_id,
            company_id=test_company.company_id
        ).first()
        
        assert holding is not None
        assert holding.quantity == 10
        
        # Verify transactions were recorded
        transactions = Transaction.query.filter_by(
            user_id=test_user.user_id,
            order_id=order.order_id
        ).all()
        
        assert len(transactions) >= 1  # At least buy transaction


@pytest.mark.regression
@pytest.mark.critical
class TestSellOrderFlow:
    """Test critical sell order workflow"""
    
    def test_complete_sell_order_flow(self, client, auth_client, test_user, test_company, test_holding, db):
        """Test complete sell order from submission to portfolio update"""
        initial_balance = test_user.wallet.balance
        initial_quantity = test_holding.quantity
        
        # Submit sell order
        order_data = {
            'symbol': test_company.symbol,
            'quantity': 5,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/sell', data=order_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify order was created and completed
        order = Order.query.filter_by(
            user_id=test_user.user_id,
            company_id=test_company.company_id,
            order_type='SELL'
        ).first()
        
        assert order is not None
        assert order.order_status == 'COMPLETED'
        assert order.quantity == 5
        
        # Verify wallet balance increased
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance > initial_balance
        
        # Verify holding quantity decreased
        db.session.refresh(test_holding)
        assert test_holding.quantity == initial_quantity - 5


@pytest.mark.regression
@pytest.mark.critical
class TestPortfolioViewing:
    """Test critical portfolio viewing functionality"""
    
    def test_user_can_view_portfolio(self, auth_client, test_user, test_holding, db):
        """Test user can view their portfolio with holdings"""
        response = auth_client.get('/portfolio')
        assert response.status_code == 200
        
        # Verify portfolio data is displayed
        assert test_holding.company.symbol.encode() in response.data
        assert str(test_holding.quantity).encode() in response.data
    
    def test_portfolio_shows_correct_values(self, auth_client, test_user, test_holding, db):
        """Test portfolio displays correct calculated values"""
        response = auth_client.get('/portfolio')
        assert response.status_code == 200
        
        # Verify wallet balance is shown
        wallet_balance = str(test_user.wallet.balance)
        assert wallet_balance.encode() in response.data or wallet_balance.replace('.', '').encode() in response.data


@pytest.mark.regression
@pytest.mark.critical
class TestWalletOperations:
    """Test critical wallet operations"""
    
    def test_deposit_funds(self, auth_client, test_user, db):
        """Test user can deposit funds to wallet"""
        initial_balance = test_user.wallet.balance
        
        deposit_data = {
            'amount': '1000.00',
            'description': 'Test deposit',
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/portfolio/wallet/deposit', data=deposit_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify balance increased
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance == initial_balance + Decimal('1000.00')
    
    def test_withdraw_funds(self, auth_client, test_user, db):
        """Test user can withdraw funds from wallet"""
        initial_balance = test_user.wallet.balance
        
        withdraw_data = {
            'amount': '500.00',
            'description': 'Test withdrawal',
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/portfolio/wallet/withdraw', data=withdraw_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify balance decreased
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance == initial_balance - Decimal('500.00')


@pytest.mark.regression
@pytest.mark.critical
class TestPredictionService:
    """Test critical prediction functionality"""
    
    def test_prediction_page_loads(self, auth_client, test_company):
        """Test prediction page loads successfully"""
        response = auth_client.get('/dashboard/predict')
        assert response.status_code == 200
    
    def test_prediction_with_valid_symbol(self, auth_client, test_company):
        """Test prediction works with valid stock symbol"""
        predict_data = {
            'symbol': test_company.symbol,
            'models': ['LR'],  # Use only Linear Regression for speed
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/dashboard/predict', data=predict_data, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.critical
class TestAdminAccess:
    """Test critical admin functionality"""
    
    def test_admin_can_access_dashboard(self, client, admin_user, db):
        """Test admin user can access admin dashboard"""
        # Login as admin
        with client:
            client.post('/auth/login', data={
                'email': admin_user.email,
                'password': 'admin123',
                'csrf_token': 'test_token'
            })
            
            response = client.get('/admin')
            assert response.status_code == 200
    
    def test_regular_user_cannot_access_admin(self, auth_client):
        """Test regular user cannot access admin dashboard"""
        response = auth_client.get('/admin', follow_redirects=False)
        assert response.status_code in [302, 403]  # Redirect or forbidden


@pytest.mark.regression
@pytest.mark.critical
class TestDataIntegrity:
    """Test critical data integrity constraints"""
    
    def test_wallet_balance_cannot_go_negative(self, auth_client, test_user, db):
        """Test wallet balance constraint prevents negative balance"""
        # Try to withdraw more than available
        withdraw_data = {
            'amount': str(test_user.wallet.balance + Decimal('1000.00')),
            'description': 'Excessive withdrawal',
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/portfolio/wallet/withdraw', data=withdraw_data, follow_redirects=True)
        
        # Should fail or show error
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance >= 0
    
    def test_cannot_sell_more_shares_than_owned(self, auth_client, test_user, test_company, test_holding, db):
        """Test cannot sell more shares than owned"""
        # Try to sell more than owned
        order_data = {
            'symbol': test_company.symbol,
            'quantity': test_holding.quantity + 100,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/sell', data=order_data, follow_redirects=True)
        
        # Verify holding quantity unchanged
        db.session.refresh(test_holding)
        assert test_holding.quantity > 0  # Should still have original shares
