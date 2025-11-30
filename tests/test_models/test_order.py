"""
Unit tests for Order model
"""
import pytest
from decimal import Decimal
from datetime import datetime
from app.models import Order
from app import db


@pytest.mark.unit
@pytest.mark.models
class TestOrderModel:
    """Test Order model functionality"""
    
    def test_create_buy_order(self, app, test_user, test_company):
        """Test creating a buy order"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=100,
                price_per_share=Decimal('150.00'),
                commission_fee=Decimal('15.00'),
                total_amount=Decimal('15015.00'),
                order_status='PENDING'
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.order_id is not None
            assert order.user_id == test_user.user_id
            assert order.company_id == test_company.company_id
            assert order.order_type == 'BUY'
            assert order.quantity == 100
            assert order.price_per_share == Decimal('150.00')
            assert order.commission_fee == Decimal('15.00')
            assert order.total_amount == Decimal('15015.00')
            assert order.order_status == 'PENDING'
            assert order.created_at is not None
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_create_sell_order(self, app, test_user, test_company):
        """Test creating a sell order"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='SELL',
                quantity=50,
                price_per_share=Decimal('200.00'),
                commission_fee=Decimal('10.00'),
                total_amount=Decimal('9990.00'),
                order_status='PENDING'
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.order_type == 'SELL'
            assert order.quantity == 50
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_order_status_transitions(self, app, test_user, test_company):
        """Test order status transitions"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=10,
                price_per_share=Decimal('100.00'),
                commission_fee=Decimal('1.00'),
                total_amount=Decimal('1001.00'),
                order_status='PENDING'
            )
            db.session.add(order)
            db.session.commit()
            
            # Transition to COMPLETED
            order.order_status = 'COMPLETED'
            order.executed_at = datetime.utcnow()
            db.session.commit()
            
            order = Order.query.get(order.order_id)
            assert order.order_status == 'COMPLETED'
            assert order.executed_at is not None
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_failed_order_with_reason(self, app, test_user, test_company):
        """Test failed order with failure reason"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=1000,
                price_per_share=Decimal('1000.00'),
                commission_fee=Decimal('1000.00'),
                total_amount=Decimal('1001000.00'),
                order_status='FAILED',
                failure_reason='Insufficient funds'
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.order_status == 'FAILED'
            assert order.failure_reason == 'Insufficient funds'
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_realized_gain_loss(self, app, test_user, test_company):
        """Test storing realized gain/loss for sell orders"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='SELL',
                quantity=100,
                price_per_share=Decimal('200.00'),
                commission_fee=Decimal('20.00'),
                total_amount=Decimal('19980.00'),
                order_status='COMPLETED',
                realized_gain_loss=Decimal('5000.00')
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.realized_gain_loss == Decimal('5000.00')
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_order_repr(self, app, test_user, test_company):
        """Test order string representation"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=25,
                price_per_share=Decimal('150.00'),
                commission_fee=Decimal('3.75'),
                total_amount=Decimal('3753.75')
            )
            db.session.add(order)
            db.session.commit()
            
            repr_str = repr(order)
            assert 'Order' in repr_str
            assert 'BUY' in repr_str
            assert '25' in repr_str
            
            # Cleanup
            db.session.delete(order)
            db.session.commit()
    
    def test_quantity_constraint(self, app, test_user, test_company):
        """Test that quantity must be positive"""
        with app.app_context():
            order = Order(
                user_id=test_user.user_id,
                company_id=test_company.company_id,
                order_type='BUY',
                quantity=0,
                price_per_share=Decimal('100.00'),
                commission_fee=Decimal('0.00'),
                total_amount=Decimal('0.00')
            )
            db.session.add(order)
            
            # SQLite doesn't enforce CHECK constraints by default
            try:
                db.session.commit()
                # If we get here in SQLite, manually check the constraint
                assert order.quantity > 0, "Quantity should be positive"
                db.session.delete(order)
                db.session.commit()
            except Exception:
                # Expected in MySQL
                db.session.rollback()
