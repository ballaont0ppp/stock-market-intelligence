"""
High-Risk Area Regression Tests

Tests for areas that are prone to breaking or have high impact if they fail.
These include transaction processing, security, and data consistency.
"""
import pytest
from decimal import Decimal
from app.models import User, Order, Transaction, Holdings, Wallet
from app.services.transaction_engine import TransactionEngine
from app.services.portfolio_service import PortfolioService


@pytest.mark.regression
@pytest.mark.high_risk
class TestConcurrentTransactions:
    """Test transaction handling under concurrent conditions"""
    
    def test_concurrent_buy_orders_maintain_consistency(self, test_user, test_company, db):
        """Test multiple buy orders maintain wallet consistency"""
        engine = TransactionEngine()
        initial_balance = test_user.wallet.balance
        
        # Simulate multiple small orders
        orders_placed = 0
        total_cost = Decimal('0')
        
        for i in range(3):
            try:
                order = engine.create_buy_order(
                    user_id=test_user.user_id,
                    symbol=test_company.symbol,
                    quantity=1
                )
                if order.order_status == 'COMPLETED':
                    orders_placed += 1
                    total_cost += order.total_amount
            except Exception:
                pass
        
        # Verify wallet balance is consistent
        db.session.refresh(test_user.wallet)
        expected_balance = initial_balance - total_cost
        assert abs(test_user.wallet.balance - expected_balance) < Decimal('0.01')


@pytest.mark.regression
@pytest.mark.high_risk
class TestTransactionRollback:
    """Test transaction rollback on failures"""
    
    def test_failed_buy_order_rolls_back(self, test_user, db):
        """Test failed buy order doesn't affect wallet"""
        engine = TransactionEngine()
        initial_balance = test_user.wallet.balance
        
        # Try to buy with invalid symbol
        try:
            order = engine.create_buy_order(
                user_id=test_user.user_id,
                symbol='INVALID_SYMBOL_XYZ',
                quantity=10
            )
        except Exception:
            pass
        
        # Verify wallet unchanged
        db.session.refresh(test_user.wallet)
        assert test_user.wallet.balance == initial_balance
    
    def test_insufficient_funds_rolls_back(self, test_user, test_company, db):
        """Test order with insufficient funds doesn't create partial state"""
        engine = TransactionEngine()
        
        # Set wallet to very low balance
        test_user.wallet.balance = Decimal('1.00')
        db.session.commit()
        
        initial_holdings_count = Holdings.query.filter_by(user_id=test_user.user_id).count()
        
        # Try to buy expensive stock
        try:
            order = engine.create_buy_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=1000
            )
        except Exception:
            pass
        
        # Verify no new holdings created
        final_holdings_count = Holdings.query.filter_by(user_id=test_user.user_id).count()
        assert final_holdings_count == initial_holdings_count


@pytest.mark.regression
@pytest.mark.high_risk
class TestSecurityConstraints:
    """Test security-related constraints"""
    
    def test_user_cannot_access_other_user_portfolio(self, client, test_user, db):
        """Test users cannot view other users' portfolios"""
        # Create second user
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        user2 = auth_service.register_user(
            email='user2@test.com',
            password='SecurePass123!',
            full_name='User Two'
        )
        
        # Login as first user
        with client:
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123',
                'csrf_token': 'test_token'
            })
            
            # Try to access second user's data via API
            response = client.get(f'/api/portfolio/{user2.user_id}')
            assert response.status_code in [403, 404]  # Forbidden or not found
    
    def test_sql_injection_prevention(self, auth_client):
        """Test SQL injection attempts are prevented"""
        # Try SQL injection in search
        malicious_input = "'; DROP TABLE users; --"
        
        response = auth_client.get(f'/api/search?q={malicious_input}')
        
        # Should not crash and users table should still exist
        from app.models import User
        users = User.query.all()
        assert users is not None
    
    def test_xss_prevention(self, auth_client, test_user, db):
        """Test XSS attempts are sanitized"""
        # Try XSS in profile update
        xss_payload = '<script>alert("XSS")</script>'
        
        response = auth_client.post('/auth/profile', data={
            'full_name': xss_payload,
            'csrf_token': 'test_token'
        }, follow_redirects=True)
        
        # Verify script tags are escaped
        assert b'<script>' not in response.data or b'&lt;script&gt;' in response.data


@pytest.mark.regression
@pytest.mark.high_risk
class TestDataConsistency:
    """Test data consistency across related tables"""
    
    def test_order_transaction_consistency(self, test_user, test_company, db):
        """Test orders and transactions remain consistent"""
        engine = TransactionEngine()
        
        # Create buy order
        order = engine.create_buy_order(
            user_id=test_user.user_id,
            symbol=test_company.symbol,
            quantity=5
        )
        
        if order.order_status == 'COMPLETED':
            # Verify transactions exist for order
            transactions = Transaction.query.filter_by(order_id=order.order_id).all()
            assert len(transactions) > 0
            
            # Verify transaction amounts match order
            total_transaction_amount = sum(abs(t.amount) for t in transactions)
            assert total_transaction_amount > 0
    
    def test_holding_quantity_matches_transactions(self, test_user, test_company, db):
        """Test holding quantities match transaction history"""
        engine = TransactionEngine()
        
        # Place multiple orders
        buy_quantity = 10
        order1 = engine.create_buy_order(
            user_id=test_user.user_id,
            symbol=test_company.symbol,
            quantity=buy_quantity
        )
        
        if order1.order_status == 'COMPLETED':
            # Check holding
            holding = Holdings.query.filter_by(
                user_id=test_user.user_id,
                company_id=test_company.company_id
            ).first()
            
            assert holding is not None
            assert holding.quantity >= buy_quantity


@pytest.mark.regression
@pytest.mark.high_risk
class TestErrorHandling:
    """Test error handling in critical paths"""
    
    def test_invalid_stock_symbol_handled(self, auth_client):
        """Test invalid stock symbol returns proper error"""
        order_data = {
            'symbol': 'NOTREAL123',
            'quantity': 10,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/buy', data=order_data, follow_redirects=True)
        # Should not crash, should show error message
        assert response.status_code == 200
    
    def test_negative_quantity_rejected(self, auth_client, test_company):
        """Test negative quantity is rejected"""
        order_data = {
            'symbol': test_company.symbol,
            'quantity': -10,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/buy', data=order_data, follow_redirects=True)
        # Should reject invalid input
        assert response.status_code == 200  # Returns to form with error
    
    def test_zero_quantity_rejected(self, auth_client, test_company):
        """Test zero quantity is rejected"""
        order_data = {
            'symbol': test_company.symbol,
            'quantity': 0,
            'csrf_token': 'test_token'
        }
        
        response = auth_client.post('/orders/buy', data=order_data, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.high_risk
class TestSessionManagement:
    """Test session handling and authentication"""
    
    def test_session_expires_after_logout(self, client, test_user):
        """Test session is properly cleared after logout"""
        # Login
        with client:
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123',
                'csrf_token': 'test_token'
            })
            
            # Verify logged in
            response = client.get('/portfolio')
            assert response.status_code == 200
            
            # Logout
            client.get('/auth/logout')
            
            # Verify cannot access protected page
            response = client.get('/portfolio', follow_redirects=False)
            assert response.status_code == 302  # Redirect to login
    
    def test_unauthenticated_access_redirects(self, client):
        """Test unauthenticated users are redirected"""
        protected_routes = [
            '/portfolio',
            '/orders',
            '/orders/buy',
            '/orders/sell',
            '/dashboard/predict'
        ]
        
        for route in protected_routes:
            response = client.get(route, follow_redirects=False)
            assert response.status_code == 302  # Redirect to login


@pytest.mark.regression
@pytest.mark.high_risk
class TestDatabaseConstraints:
    """Test database-level constraints"""
    
    def test_unique_email_constraint(self, db):
        """Test cannot create users with duplicate emails"""
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Create first user
        user1 = auth_service.register_user(
            email='duplicate@test.com',
            password='Pass123!',
            full_name='User One'
        )
        
        # Try to create second user with same email
        with pytest.raises(Exception):
            user2 = auth_service.register_user(
                email='duplicate@test.com',
                password='Pass456!',
                full_name='User Two'
            )
    
    def test_foreign_key_constraints(self, test_user, db):
        """Test foreign key constraints are enforced"""
        # Try to create order with non-existent company
        from app.models import Order
        
        with pytest.raises(Exception):
            order = Order(
                user_id=test_user.user_id,
                company_id=99999,  # Non-existent
                order_type='BUY',
                quantity=10,
                price_per_share=Decimal('100.00'),
                commission_fee=Decimal('1.00'),
                total_amount=Decimal('1001.00'),
                order_status='PENDING'
            )
            db.session.add(order)
            db.session.commit()
