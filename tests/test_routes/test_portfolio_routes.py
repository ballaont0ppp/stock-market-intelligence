"""
Unit tests for portfolio routes
"""
import pytest


@pytest.mark.unit
@pytest.mark.routes
class TestPortfolioRoutes:
    """Test portfolio endpoint functionality"""
    
    def test_portfolio_requires_login(self, client):
        """Test that portfolio page requires authentication"""
        response = client.get('/portfolio')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_portfolio_page_authenticated(self, authenticated_client):
        """Test portfolio page for authenticated user"""
        response = authenticated_client.get('/portfolio')
        assert response.status_code == 200
        assert b'Portfolio' in response.data or b'portfolio' in response.data or b'Holdings' in response.data
    
    def test_wallet_requires_login(self, client):
        """Test that wallet page requires authentication"""
        response = client.get('/portfolio/wallet')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_wallet_page_authenticated(self, authenticated_client):
        """Test wallet page for authenticated user"""
        response = authenticated_client.get('/portfolio/wallet')
        assert response.status_code == 200
        assert b'Wallet' in response.data or b'wallet' in response.data or b'Balance' in response.data
    
    def test_deposit_funds(self, authenticated_client):
        """Test deposit funds endpoint"""
        response = authenticated_client.post('/portfolio/wallet/deposit', data={
            'amount': '1000.00',
            'description': 'Test deposit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_withdraw_funds(self, authenticated_client):
        """Test withdraw funds endpoint"""
        response = authenticated_client.post('/portfolio/wallet/withdraw', data={
            'amount': '500.00',
            'description': 'Test withdrawal'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_deposit_invalid_amount(self, authenticated_client):
        """Test deposit with invalid amount"""
        response = authenticated_client.post('/portfolio/wallet/deposit', data={
            'amount': '-100.00',
            'description': 'Invalid deposit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_withdraw_insufficient_funds(self, authenticated_client):
        """Test withdrawal with insufficient funds"""
        response = authenticated_client.post('/portfolio/wallet/withdraw', data={
            'amount': '999999999.00',
            'description': 'Excessive withdrawal'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_portfolio_displays_holdings(self, authenticated_client, test_holding):
        """Test that portfolio displays user holdings"""
        response = authenticated_client.get('/portfolio')
        assert response.status_code == 200
        # Should display holdings information
        assert b'TEST' in response.data or b'Holdings' in response.data
    
    def test_wallet_displays_balance(self, authenticated_client, test_wallet):
        """Test that wallet displays balance"""
        response = authenticated_client.get('/portfolio/wallet')
        assert response.status_code == 200
        # Should display balance information
        assert b'Balance' in response.data or b'balance' in response.data
