"""
Integration test for complete sell order flow
"""
import pytest
from decimal import Decimal
from app.services.transaction_engine import TransactionEngine
from app.models import Wallet, Holdings, Order, Transaction
from app import db


@pytest.mark.integration
class TestSellOrderFlow:
    """Test complete sell order flow"""
    
    def test_complete_sell_order_flow(self, app, test_user, test_company, test_wallet, test_holding):
        """Test complete sell order flow: verify holdings -> sell -> verify proceeds"""
        with app.app_context():
            # Step 1: Verify initial state
            initial_balance = test_wallet.balance
            initial_quantity = test_holding.quantity
            
            # Step 2: Execute sell order
            engine = TransactionEngine()
            sell_quantity = 50
            
            order = engine.create_sell_order(
                user_id=test_user.user_id,
                symbol=test_company.symbol,
                quantity=sell_quantity
            )
            
            # Step 3: Verify order was created and completed
            assert order is not None
            assert order.order_status == 'COMPLETED'
            assert order.order_type == 'SELL'
            assert order.quantity == sell_quantity
            
            # Step 4: Verify wallet was credited
            wallet = Wallet.query.get(test_wallet.wallet_id)
            assert wallet.balance > initial_balance
            
            # Step 5: Verify holding was reduced
            holding = Holdings.query.get(test_holding.holding_id)
            if sell_quantity < initial_quantity:
                assert holding is not None
                assert holding.quantity == initial_quantity - sell_quantity
            else:
                # If all shares sold, holding should be deleted
                assert holding is None or holding.quantity == 0
            
            # Step 6: Verify transactions were created
            transactions = Transaction.query.filter_by(
                user_id=test_user.user_id,
                order_id=order.order_id
            ).all()
            assert len(transactions) >= 1
            
            sell_transaction = next((t for t in transactions if t.transaction_type == 'SELL'), None)
            assert sell_transaction is not None
            
            # Step 7: Verify realized gain/loss was calculated
            assert order.realized_gain_loss is not None
