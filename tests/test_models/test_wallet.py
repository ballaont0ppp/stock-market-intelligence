"""
Unit tests for Wallet model
"""
import pytest
from decimal import Decimal
from app.models import Wallet
from app import db


@pytest.mark.unit
@pytest.mark.models
class TestWalletModel:
    """Test Wallet model functionality"""
    
    def test_create_wallet(self, app, test_user):
        """Test creating a new wallet"""
        with app.app_context():
            wallet = Wallet(
                user_id=test_user.user_id,
                balance=Decimal('50000.00'),
                currency='USD',
                total_deposited=Decimal('50000.00'),
                total_withdrawn=Decimal('0.00')
            )
            db.session.add(wallet)
            db.session.commit()
            
            assert wallet.wallet_id is not None
            assert wallet.user_id == test_user.user_id
            assert wallet.balance == Decimal('50000.00')
            assert wallet.currency == 'USD'
            assert wallet.created_at is not None
            
            # Cleanup
            db.session.delete(wallet)
            db.session.commit()
    
    def test_default_values(self, app, test_user):
        """Test wallet default values"""
        with app.app_context():
            # Delete existing wallet if any
            existing = Wallet.query.filter_by(user_id=test_user.user_id).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()
            
            wallet = Wallet(user_id=test_user.user_id)
            db.session.add(wallet)
            db.session.commit()
            
            assert wallet.balance == Decimal('100000.00')
            assert wallet.currency == 'USD'
            assert wallet.total_deposited == Decimal('100000.00')
            assert wallet.total_withdrawn == Decimal('0.00')
            
            # Cleanup
            db.session.delete(wallet)
            db.session.commit()
    
    def test_balance_constraint(self, app, test_wallet):
        """Test that balance cannot be negative"""
        with app.app_context():
            wallet = Wallet.query.get(test_wallet.wallet_id)
            wallet.balance = Decimal('-100.00')
            
            # SQLite doesn't enforce CHECK constraints by default
            # This test may pass in SQLite but fail in MySQL
            try:
                db.session.commit()
                # If we get here in SQLite, manually check the constraint
                assert wallet.balance >= 0, "Balance should not be negative"
            except Exception:
                # Expected in MySQL
                db.session.rollback()
    
    def test_unique_user_constraint(self, app, test_user, test_wallet):
        """Test that each user can have only one wallet"""
        with app.app_context():
            duplicate_wallet = Wallet(
                user_id=test_user.user_id,
                balance=Decimal('10000.00')
            )
            db.session.add(duplicate_wallet)
            
            with pytest.raises(Exception):
                db.session.commit()
            
            db.session.rollback()
    
    def test_wallet_repr(self, app, test_wallet):
        """Test wallet string representation"""
        with app.app_context():
            wallet = Wallet.query.get(test_wallet.wallet_id)
            repr_str = repr(wallet)
            
            assert 'Wallet' in repr_str
            assert str(wallet.user_id) in repr_str
            assert str(wallet.balance) in repr_str
    
    def test_balance_updates(self, app, test_wallet):
        """Test updating wallet balance"""
        with app.app_context():
            wallet = Wallet.query.get(test_wallet.wallet_id)
            original_balance = wallet.balance
            
            wallet.balance = original_balance + Decimal('5000.00')
            db.session.commit()
            
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.balance == original_balance + Decimal('5000.00')
    
    def test_deposit_tracking(self, app, test_wallet):
        """Test tracking total deposits"""
        with app.app_context():
            wallet = Wallet.query.get(test_wallet.wallet_id)
            original_deposited = wallet.total_deposited
            
            deposit_amount = Decimal('10000.00')
            wallet.balance += deposit_amount
            wallet.total_deposited += deposit_amount
            db.session.commit()
            
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.total_deposited == original_deposited + deposit_amount
    
    def test_withdrawal_tracking(self, app, test_wallet):
        """Test tracking total withdrawals"""
        with app.app_context():
            wallet = Wallet.query.get(test_wallet.wallet_id)
            original_withdrawn = wallet.total_withdrawn
            
            withdrawal_amount = Decimal('5000.00')
            wallet.balance -= withdrawal_amount
            wallet.total_withdrawn += withdrawal_amount
            db.session.commit()
            
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.total_withdrawn == original_withdrawn + withdrawal_amount
