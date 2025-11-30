"""
Unit tests for TransactionEngine
"""
import pytest
from decimal import Decimal
from app.services.transaction_engine import TransactionEngine
from app.models import Order, Wallet
from app import db


@pytest.mark.unit
@pytest.mark.services
class TestTransactionEngine:
    """Test TransactionEngine functionality"""
    
    def test_calculate_commission(self, app):
        """Test commission calculation"""
        with app.app_context():
            engine = TransactionEngine()
            
            # Test 0.1% commission
            amount = Decimal('10000.00')
            commission = engine.calculate_commission(amount)
            
            assert commission == Decimal('10.00')
            
            # Test rounding
            amount = Decimal('12345.67')
            commission = engine.calculate_commission(amount)
            
            assert commission == Decimal('12.35')
    
    def test_validate_buy_order_success(self, app, test_user, test_company, test_wallet):
        """Test successful buy order validation"""
        with app.app_context():
            engine = TransactionEngine()
            
            is_valid, error = engine.validate_buy_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=10,
                price_per_share=Decimal('100.00')
            )
            
            assert is_valid is True
            assert error == ""
    
    def test_validate_buy_order_negative_quantity(self, app, test_user, test_company):
        """Test buy order validation with negative quantity"""
        with app.app_context():
            engine = TransactionEngine()
            
            is_valid, error = engine.validate_buy_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=-10,
                price_per_share=Decimal('100.00')
            )
            
            assert is_valid is False
            assert "positive" in error.lower()
    
    def test_validate_buy_order_invalid_symbol(self, app, test_user):
        """Test buy order validation with invalid symbol"""
        with app.app_context():
            engine = TransactionEngine()
            
            is_valid, error = engine.validate_buy_order(
                user_id=test_user.user_id,
                symbol='INVALID',
                quantity=10,
                price_per_share=Decimal('100.00')
            )
            
            assert is_valid is False
            assert "symbol" in error.lower()
    
    def test_validate_buy_order_insufficient_funds(self, app, test_user, test_company, test_wallet):
        """Test buy order validation with insufficient funds"""
        with app.app_context():
            engine = TransactionEngine()
            
            # Try to buy more than wallet balance allows
            is_valid, error = engine.validate_buy_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=10000,
                price_per_share=Decimal('10000.00')
            )
            
            assert is_valid is False
            assert "insufficient funds" in error.lower()
    
    def test_validate_sell_order_success(self, app, test_user, test_company, test_holding):
        """Test successful sell order validation"""
        with app.app_context():
            engine = TransactionEngine()
            
            is_valid, error = engine.validate_sell_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=10,
                price_per_share=Decimal('150.00')
            )
            
            assert is_valid is True
            assert error == ""
    
    def test_validate_sell_order_insufficient_shares(self, app, test_user, test_company, test_holding):
        """Test sell order validation with insufficient shares"""
        with app.app_context():
            engine = TransactionEngine()
            
            # Try to sell more shares than owned
            is_valid, error = engine.validate_sell_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=test_holding.quantity + 100,
                price_per_share=Decimal('150.00')
            )
            
            assert is_valid is False
            assert "insufficient shares" in error.lower()
    
    def test_validate_sell_order_no_holdings(self, app, test_user, test_company):
        """Test sell order validation when user doesn't own the stock"""
        with app.app_context():
            engine = TransactionEngine()
            
            # Create a different company that user doesn't own
            from app.models import Company
            other_company = Company(
                symbol='OTHER',
                company_name='Other Company',
                sector='Technology'
            )
            db.session.add(other_company)
            db.session.commit()
            
            is_valid, error = engine.validate_sell_order(
                user_id=test_user.user_id,
                symbol='OTHER',
                quantity=10,
                price_per_share=Decimal('150.00')
            )
            
            assert is_valid is False
            assert "do not own" in error.lower() or "insufficient" in error.lower()
            
            # Cleanup
            db.session.delete(other_company)
            db.session.commit()
