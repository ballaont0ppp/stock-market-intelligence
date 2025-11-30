"""
Unit tests for order routes
"""
import pytest
from app import db


@pytest.mark.unit
@pytest.mark.routes
class TestOrderRoutes:
    """Test order endpoint functionality"""
    
    def test_orders_requires_login(self, client):
        """Test that orders page requires authentication"""
        response = client.get('/orders')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_orders_page_authenticated(self, authenticated_client):
        """Test orders page for authenticated user"""
        response = authenticated_client.get('/orders')
        assert response.status_code == 200
        assert b'Order' in response.data or b'order' in response.data
    
    def test_buy_page_requires_login(self, client):
        """Test that buy page requires authentication"""
        response = client.get('/orders/buy')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_buy_page_authenticated(self, authenticated_client):
        """Test buy page for authenticated user"""
        response = authenticated_client.get('/orders/buy')
        assert response.status_code == 200
        assert b'Buy' in response.data or b'buy' in response.data
    
    def test_sell_page_requires_login(self, client):
        """Test that sell page requires authentication"""
        response = client.get('/orders/sell')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_sell_page_authenticated(self, authenticated_client):
        """Test sell page for authenticated user"""
        response = authenticated_client.get('/orders/sell')
        assert response.status_code == 200
        assert b'Sell' in response.data or b'sell' in response.data
    
    def test_transactions_page_authenticated(self, authenticated_client):
        """Test transactions page for authenticated user"""
        response = authenticated_client.get('/orders/transactions')
        assert response.status_code == 200
        assert b'Transaction' in response.data or b'transaction' in response.data or b'History' in response.data
    
    def test_buy_order_submission(self, authenticated_client, test_company, app):
        """Test submitting a buy order"""
        # Create price history for the test company
        from app.models import PriceHistory
        from datetime import date
        from decimal import Decimal
        
        with app.app_context():
            price_history = PriceHistory(
                company_id=test_company.company_id,
                date=date.today(),
                open=Decimal('150.00'),
                high=Decimal('155.00'),
                low=Decimal('148.00'),
                close=Decimal('152.00'),
                adjusted_close=Decimal('152.00'),
                volume=1000000
            )
            db.session.add(price_history)
            db.session.commit()
        
        response = authenticated_client.post('/orders/buy', data={
            'symbol': 'TEST',
            'quantity': '10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_sell_order_submission(self, authenticated_client, test_holding):
        """Test submitting a sell order"""
        response = authenticated_client.post('/orders/sell', data={
            'symbol': 'TEST',
            'quantity': '5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_buy_order_invalid_symbol(self, authenticated_client):
        """Test buy order with invalid symbol"""
        response = authenticated_client.post('/orders/buy', data={
            'symbol': 'INVALID',
            'quantity': '10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_sell_order_insufficient_shares(self, authenticated_client):
        """Test sell order with insufficient shares"""
        response = authenticated_client.post('/orders/sell', data={
            'symbol': 'TEST',
            'quantity': '999999'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_order_view_details(self, authenticated_client, app, test_user, test_company):
        """Test viewing order details"""
        from app.models import Order
        from decimal import Decimal
        
        # Create a test order
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=10,
                price_per_share=Decimal('150.00'),
                commission_fee=Decimal('1.50'),
                total_amount=Decimal('1501.50'),
                order_status='COMPLETED'
            )
            db.session.add(order)
            db.session.commit()
            order_id = order.order_id
        
        response = authenticated_client.get(f'/orders/{order_id}')
        # Should either show order details or redirect
        assert response.status_code in [200, 302, 404]
