"""
Integration test for complete buy order flow
"""
import pytest
from decimal import Decimal
from app.services.transaction_engine import TransactionEngine
from app.services.auth_service import AuthService
from app.models import User, Wallet, Holdings, Order, Transaction
from app import db


@pytest.mark.integration
class TestBuyOrderFlow:
    """Test complete buy order flow from login to verification"""
    
    def test_complete_buy_order_flow(self, app, test_company):
        """Test complete buy order flow: register -> login -> deposit -> buy -> verify"""
        with app.app_context():
            # Step 1: Register a new user
            auth_service = AuthService()
            user, _ = auth_service.register_user(
                email='buyer@test.com',
                password='BuyTest123!',
                full_name='Test Buyer'
            )
            
            assert user is not None
            assert user.user_id is not None
            
            # Step 2: Verify wallet was created with initial balance
            wallet = Wallet.query.filter_by(user_id=user.user_id).first()
            assert wallet is not None
            assert wallet.balance == Decimal('100000.00')
            initial_balance = wallet.balance
            
            # Step 3: Execute buy order
            engine = TransactionEngine()
            quantity = 10
            price_per_share = Decimal('150.00')
            
            order = engine.create_buy_order(
                user_id=user.user_id,
                symbol=test_company.symbol,
                quantity=quantity
            )
            
            # Step 4: Verify order was created and completed
            assert order is not None
            assert order.order_status == 'COMPLETED'
            assert order.order_type == 'BUY'
            assert order.quantity == quantity
            
            # Step 5: Verify wallet was debited
            wallet = Wallet.query.filter_by(user_id=user.user_id).first()
            assert wallet.balance < initial_balance
            
            # Step 6: Verify holding was created
            holding = Holdings.query.filter_by(
                user_id=user.user_id,
                company_id=test_company.company_id
            ).first()
            assert holding is not None
            assert holding.quantity == quantity
            
            # Step 7: Verify transactions were created
            transactions = Transaction.query.filter_by(user_id=user.user_id).all()
            assert len(transactions) >= 2  # BUY transaction + FEE transaction
            
            buy_transaction = next((t for t in transactions if t.transaction_type == 'BUY'), None)
            assert buy_transaction is not None
            
            # Cleanup
            for transaction in transactions:
                db.session.delete(transaction)
            if holding:
                db.session.delete(holding)
            if order:
                db.session.delete(order)
            db.session.delete(wallet)
            db.session.delete(user)
            db.session.commit()
