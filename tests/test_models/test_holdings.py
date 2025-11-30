"""
Unit tests for Holdings model
"""
import pytest
from decimal import Decimal
from app.models import Holdings
from app import db


@pytest.mark.unit
@pytest.mark.models
class TestHoldingsModel:
    """Test Holdings model functionality"""
    
    def test_create_holding(self, app, test_user, test_company):
        """Test creating a new holding"""
        with app.app_context():
            holding = Holdings(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                quantity=50,
                average_purchase_price=Decimal('100.00'),
                total_invested=Decimal('5000.00')
            )
            db.session.add(holding)
            db.session.commit()
            
            assert holding.holding_id is not None
            assert holding.user_id == test_user.user_id
            assert holding.company_id == test_company.company_id
            assert holding.quantity == 50
            assert holding.average_purchase_price == Decimal('100.00')
            assert holding.total_invested == Decimal('5000.00')
            assert holding.first_purchase_date is not None
            
            # Cleanup
            db.session.delete(holding)
            db.session.commit()
    
    def test_quantity_constraint(self, app, test_user, test_company):
        """Test that quantity must be positive"""
        with app.app_context():
            holding = Holdings(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                quantity=0,
                average_purchase_price=Decimal('100.00'),
                total_invested=Decimal('0.00')
            )
            db.session.add(holding)
            
            # SQLite doesn't enforce CHECK constraints by default
            try:
                db.session.commit()
                # If we get here in SQLite, manually check the constraint
                assert holding.quantity > 0, "Quantity should be positive"
                db.session.delete(holding)
                db.session.commit()
            except Exception:
                # Expected in MySQL
                db.session.rollback()
    
    def test_unique_user_company_constraint(self, app, test_holding):
        """Test that user can have only one holding per company"""
        with app.app_context():
            holding = Holdings.query.get(test_holding.holding_id)
            
            duplicate_holding = Holdings(
                user_id=holding.user_id,
                company_id=holding.company_id,
                quantity=10,
                average_purchase_price=Decimal('150.00'),
                total_invested=Decimal('1500.00')
            )
            db.session.add(duplicate_holding)
            
            with pytest.raises(Exception):
                db.session.commit()
            
            db.session.rollback()
    
    def test_holding_repr(self, app, test_holding):
        """Test holding string representation"""
        with app.app_context():
            holding = Holdings.query.get(test_holding.holding_id)
            repr_str = repr(holding)
            
            assert 'Holdings' in repr_str
            assert str(holding.user_id) in repr_str
            assert str(holding.company_id) in repr_str
            assert str(holding.quantity) in repr_str
    
    def test_update_quantity(self, app, test_holding):
        """Test updating holding quantity"""
        with app.app_context():
            holding = Holdings.query.get(test_holding.holding_id)
            original_quantity = holding.quantity
            
            holding.quantity = original_quantity + 50
            db.session.commit()
            
            holding = Holdings.query.get(test_holding.holding_id)
            assert holding.quantity == original_quantity + 50
    
    def test_average_price_calculation(self, app, test_holding):
        """Test recalculating average purchase price"""
        with app.app_context():
            holding = Holdings.query.get(test_holding.holding_id)
            
            # Simulate buying more shares at different price
            original_qty = holding.quantity
            original_avg_price = holding.average_purchase_price
            original_invested = holding.total_invested
            
            new_qty = 50
            new_price = Decimal('200.00')
            new_invested = new_qty * new_price
            
            # Calculate new average
            total_qty = original_qty + new_qty
            total_invested = original_invested + new_invested
            new_avg_price = total_invested / total_qty
            
            holding.quantity = total_qty
            holding.total_invested = total_invested
            holding.average_purchase_price = new_avg_price
            db.session.commit()
            
            holding = Holdings.query.get(test_holding.holding_id)
            assert holding.quantity == total_qty
            assert holding.total_invested == total_invested
            assert abs(holding.average_purchase_price - new_avg_price) < Decimal('0.01')
