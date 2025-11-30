"""
Unit tests for PortfolioService
"""
import pytest
from decimal import Decimal
from app.services.portfolio_service import PortfolioService
from app.models import Wallet, Transaction
from app.utils.exceptions import ValidationError, InsufficientFundsError
from app import db


@pytest.mark.unit
@pytest.mark.services
class TestPortfolioService:
    """Test PortfolioService functionality"""
    
    def test_get_wallet_balance(self, app, test_user, test_wallet):
        """Test getting wallet balance"""
        with app.app_context():
            service = PortfolioService()
            balance = service.get_wallet_balance(test_user.user_id)
            
            assert balance == test_wallet.balance
            assert isinstance(balance, Decimal)
    
    def test_get_wallet_balance_not_found(self, app):
        """Test getting balance for nonexistent wallet"""
        with app.app_context():
            service = PortfolioService()
            
            with pytest.raises(ValidationError, match="Wallet not found"):
                service.get_wallet_balance(99999)
    
    def test_deposit_funds_success(self, app, test_user, test_wallet):
        """Test successful fund deposit"""
        with app.app_context():
            service = PortfolioService()
            original_balance = test_wallet.balance
            deposit_amount = Decimal('5000.00')
            
            transaction = service.deposit_funds(
                user_id=test_user.user_id,
                amount=deposit_amount,
                description='Test deposit'
            )
            
            # Verify transaction created
            assert transaction is not None
            assert transaction.transaction_type == 'DEPOSIT'
            assert transaction.amount == deposit_amount
            assert transaction.balance_before == original_balance
            assert transaction.balance_after == original_balance + deposit_amount
            
            # Verify wallet updated
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.balance == original_balance + deposit_amount
            assert wallet.total_deposited == test_wallet.total_deposited + deposit_amount
    
    def test_deposit_funds_negative_amount(self, app, test_user):
        """Test deposit with negative amount"""
        with app.app_context():
            service = PortfolioService()
            
            with pytest.raises(ValidationError, match="must be positive"):
                service.deposit_funds(
                    user_id=test_user.user_id,
                    amount=-100.00
                )
    
    def test_deposit_funds_zero_amount(self, app, test_user):
        """Test deposit with zero amount"""
        with app.app_context():
            service = PortfolioService()
            
            with pytest.raises(ValidationError, match="must be positive"):
                service.deposit_funds(
                    user_id=test_user.user_id,
                    amount=0
                )
    
    def test_withdraw_funds_success(self, app, test_user, test_wallet):
        """Test successful fund withdrawal"""
        with app.app_context():
            service = PortfolioService()
            original_balance = test_wallet.balance
            withdrawal_amount = Decimal('1000.00')
            
            transaction = service.withdraw_funds(
                user_id=test_user.user_id,
                amount=withdrawal_amount,
                description='Test withdrawal'
            )
            
            # Verify transaction created
            assert transaction is not None
            assert transaction.transaction_type == 'WITHDRAWAL'
            assert transaction.amount == withdrawal_amount
            assert transaction.balance_before == original_balance
            assert transaction.balance_after == original_balance - withdrawal_amount
            
            # Verify wallet updated
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.balance == original_balance - withdrawal_amount
            assert wallet.total_withdrawn == test_wallet.total_withdrawn + withdrawal_amount
    
    def test_withdraw_funds_insufficient_balance(self, app, test_user, test_wallet):
        """Test withdrawal with insufficient balance"""
        with app.app_context():
            service = PortfolioService()
            
            # Try to withdraw more than available
            excessive_amount = test_wallet.balance + Decimal('1000.00')
            
            with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
                service.withdraw_funds(
                    user_id=test_user.user_id,
                    amount=excessive_amount
                )
    
    def test_withdraw_funds_negative_amount(self, app, test_user):
        """Test withdrawal with negative amount"""
        with app.app_context():
            service = PortfolioService()
            
            with pytest.raises(ValidationError, match="must be positive"):
                service.withdraw_funds(
                    user_id=test_user.user_id,
                    amount=-100.00
                )
    
    def test_get_holdings(self, app, test_user, test_holding):
        """Test getting user holdings"""
        with app.app_context():
            service = PortfolioService()
            holdings = service.get_holdings(test_user.user_id)
            
            assert len(holdings) > 0
            assert any(h.holding_id == test_holding.holding_id for h in holdings)
    
    def test_get_holdings_empty(self, app, test_user):
        """Test getting holdings for user with no holdings"""
        with app.app_context():
            service = PortfolioService()
            holdings = service.get_holdings(test_user.user_id)
            
            # May be empty or have test_holding depending on fixtures
            assert isinstance(holdings, list)
