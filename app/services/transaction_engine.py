"""
Transaction Engine Service
Handles buy/sell order processing, validation, and execution
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Tuple, Optional, Dict, List
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app import db
from app.models.order import Order
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.holding import Holdings
from app.models.company import Company
from app.services.stock_repository import StockRepository
from app.services.notification_service import NotificationService
from app.utils.error_handlers import (
    ValidationError,
    InsufficientFundsError,
    InsufficientSharesError,
    handle_errors
)

logger = logging.getLogger(__name__)


class TransactionEngine:
    """Engine for processing stock buy/sell transactions"""
    
    # Commission rate: 0.1% of transaction value
    COMMISSION_RATE = Decimal('0.001')
    
    def __init__(self):
        """Initialize the transaction engine"""
        self.stock_repo = StockRepository()
        self.notification_service = NotificationService()
    
    def calculate_commission(self, amount: Decimal) -> Decimal:
        """
        Calculate commission fee (0.1% of transaction amount)
        
        Args:
            amount: Transaction amount
            
        Returns:
            Commission fee as Decimal
        """
        commission = amount * self.COMMISSION_RATE
        # Round to 2 decimal places
        return commission.quantize(Decimal('0.01'))
    
    @handle_errors('database')
    def validate_buy_order(self, user_id: int, symbol: str, quantity: int, price_per_share: Decimal) -> Tuple[bool, str]:
        """
        Validate a buy order
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares to buy
            price_per_share: Price per share
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate quantity
        if quantity <= 0:
            return False, "Quantity must be a positive integer"
        
        if quantity > 1000000:
            return False, "Quantity cannot exceed 1,000,000 shares per order"
        
        # Validate symbol exists
        company = self.stock_repo.get_company_by_symbol(symbol)
        if not company:
            return False, f"Invalid stock symbol: {symbol}"
        
        # Validate price
        if price_per_share <= 0:
            return False, "Price per share must be positive"
        
        # Calculate total cost
        subtotal = price_per_share * quantity
        commission = self.calculate_commission(subtotal)
        total_cost = subtotal + commission
        
        # Check wallet balance
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return False, "Wallet not found"
        
        if wallet.balance < total_cost:
            return False, (
                f"Insufficient funds for this purchase. "
                f"Required: ${total_cost:,.2f}, Available: ${wallet.balance:,.2f}"
            )
        
        return True, ""
    
    @handle_errors('database')
    def validate_sell_order(self, user_id: int, symbol: str, quantity: int) -> Tuple[bool, str]:
        """
        Validate a sell order
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares to sell
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate quantity
        if quantity <= 0:
            return False, "Quantity must be a positive integer"
        
        # Validate symbol exists
        company = self.stock_repo.get_company_by_symbol(symbol)
        if not company:
            return False, f"Invalid stock symbol: {symbol}"
        
        # Check if user owns the stock
        holding = Holdings.query.filter_by(
            user_id=user_id,
            company_id=company.company_id
        ).first()
        
        if not holding:
            return False, f"You do not own any shares of {symbol}"
        
        # Check if user has enough shares
        if holding.quantity < quantity:
            return False, (
                f"Insufficient shares to sell. "
                f"You own {holding.quantity} shares of {symbol}, "
                f"but attempted to sell {quantity} shares"
            )
        
        return True, ""
    
    @handle_errors('database')
    def create_buy_order(self, user_id: int, symbol: str, quantity: int) -> Order:
        """
        Create and execute a buy order
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares to buy
            
        Returns:
            Completed Order object
            
        Raises:
            ValidationError: If validation fails
            InsufficientFundsError: If wallet balance is insufficient
        """
        symbol = symbol.upper().strip()
        
        # Get company
        company = self.stock_repo.get_company_by_symbol(symbol)
        if not company:
            # Try to create company from yfinance
            try:
                company = self.stock_repo.create_company(symbol)
            except Exception as e:
                raise ValidationError(f"Invalid stock symbol: {symbol}")
        
        # Fetch current market price
        try:
            price_per_share = self.stock_repo.get_current_price_with_mode(symbol)
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
            raise ValidationError(f"Unable to fetch current price for {symbol}")
        
        # Calculate costs
        subtotal = price_per_share * quantity
        commission = self.calculate_commission(subtotal)
        total_cost = subtotal + commission
        
        # Create order record with PENDING status
        order = Order(
            user_id=user_id,
            company_id=company.company_id,
            order_type='BUY',
            quantity=quantity,
            price_per_share=price_per_share,
            commission_fee=commission,
            total_amount=total_cost,
            order_status='PENDING',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()  # Get order_id without committing
        
        try:
            # Validate order
            is_valid, error_msg = self.validate_buy_order(user_id, symbol, quantity, price_per_share)
            if not is_valid:
                order.order_status = 'FAILED'
                order.failure_reason = error_msg
                db.session.commit()
                raise InsufficientFundsError(error_msg) if "Insufficient funds" in error_msg else ValidationError(error_msg)
            
            # Execute the order with database locks
            self._execute_buy_order(order, user_id, company.company_id, quantity, price_per_share, commission, total_cost)
            
            logger.info(
                f"Buy order completed: user={user_id}, symbol={symbol}, "
                f"quantity={quantity}, price=${price_per_share}, total=${total_cost}"
            )
            return order
            
        except (ValidationError, InsufficientFundsError) as e:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            order.order_status = 'FAILED'
            order.failure_reason = f"System error: {str(e)}"
            db.session.commit()
            logger.error(f"Buy order failed for user {user_id}: {str(e)}")
            raise ValidationError("Order failed due to system error. Please try again.")
    
    def _execute_buy_order(
        self, 
        order: Order, 
        user_id: int, 
        company_id: int, 
        quantity: int, 
        price_per_share: Decimal, 
        commission: Decimal, 
        total_cost: Decimal
    ):
        """
        Execute buy order with atomic transaction
        
        Args:
            order: Order object
            user_id: User ID
            company_id: Company ID
            quantity: Number of shares
            price_per_share: Price per share
            commission: Commission fee
            total_cost: Total cost including commission
        """
        # Acquire locks on wallet and holdings
        wallet = db.session.query(Wallet).filter_by(user_id=user_id).with_for_update().first()
        if not wallet:
            raise ValidationError("Wallet not found")
        
        # Double-check balance with lock
        if wallet.balance < total_cost:
            raise InsufficientFundsError(
                f"Insufficient funds. Required: ${total_cost:,.2f}, Available: ${wallet.balance:,.2f}"
            )
        
        # Record balance before transaction
        balance_before = wallet.balance
        
        # Deduct from wallet
        wallet.balance -= total_cost
        wallet.last_updated = datetime.utcnow()
        
        # Create or update holding
        holding = db.session.query(Holdings).filter_by(
            user_id=user_id,
            company_id=company_id
        ).with_for_update().first()
        
        if holding:
            # Update existing holding - recalculate average purchase price
            total_shares = holding.quantity + quantity
            total_investment = holding.total_invested + (price_per_share * quantity)
            holding.average_purchase_price = total_investment / total_shares
            holding.quantity = total_shares
            holding.total_invested = total_investment
            holding.last_updated = datetime.utcnow()
        else:
            # Create new holding
            holding = Holdings(
                user_id=user_id,
                company_id=company_id,
                quantity=quantity,
                average_purchase_price=price_per_share,
                total_invested=price_per_share * quantity,
                first_purchase_date=datetime.utcnow()
            )
            db.session.add(holding)
        
        # Create transaction record for the purchase
        buy_transaction = Transaction(
            user_id=user_id,
            transaction_type='BUY',
            order_id=order.order_id,
            company_id=company_id,
            amount=-(price_per_share * quantity),  # Negative because it's a debit
            balance_before=balance_before,
            balance_after=wallet.balance + commission,  # Before commission deduction
            description=f"Purchased {quantity} shares of {order.company.symbol} at ${price_per_share}/share",
            created_at=datetime.utcnow()
        )
        db.session.add(buy_transaction)
        
        # Create transaction record for commission
        fee_transaction = Transaction(
            user_id=user_id,
            transaction_type='FEE',
            order_id=order.order_id,
            company_id=company_id,
            amount=-commission,  # Negative because it's a debit
            balance_before=wallet.balance + commission,
            balance_after=wallet.balance,
            description=f"Commission fee for buy order (0.1%)",
            created_at=datetime.utcnow()
        )
        db.session.add(fee_transaction)
        
        # Update order status
        order.order_status = 'COMPLETED'
        order.executed_at = datetime.utcnow()
        
        # Commit all changes
        db.session.commit()
        
        # Create notification for order completion
        try:
            self.notification_service.create_notification(
                user_id=user_id,
                notification_type='TRANSACTION',
                title='Buy Order Completed',
                message=f'Successfully purchased {quantity} shares of {order.company.symbol} at ${price_per_share:.2f}/share. Total: ${total_cost:.2f}'
            )
        except Exception as e:
            logger.error(f"Failed to create notification for buy order {order.order_id}: {str(e)}")
    
    @handle_errors('database')
    def create_sell_order(self, user_id: int, symbol: str, quantity: int) -> Order:
        """
        Create and execute a sell order
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares to sell
            
        Returns:
            Completed Order object
            
        Raises:
            ValidationError: If validation fails
            InsufficientSharesError: If user doesn't own enough shares
        """
        symbol = symbol.upper().strip()
        
        # Get company
        company = self.stock_repo.get_company_by_symbol(symbol)
        if not company:
            raise ValidationError(f"Invalid stock symbol: {symbol}")
        
        # Fetch current market price
        try:
            price_per_share = self.stock_repo.get_current_price_with_mode(symbol)
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
            raise ValidationError(f"Unable to fetch current price for {symbol}")
        
        # Calculate proceeds
        gross_proceeds = price_per_share * quantity
        commission = self.calculate_commission(gross_proceeds)
        net_proceeds = gross_proceeds - commission
        
        # Create order record with PENDING status
        order = Order(
            user_id=user_id,
            company_id=company.company_id,
            order_type='SELL',
            quantity=quantity,
            price_per_share=price_per_share,
            commission_fee=commission,
            total_amount=net_proceeds,
            order_status='PENDING',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()  # Get order_id without committing
        
        try:
            # Validate order
            is_valid, error_msg = self.validate_sell_order(user_id, symbol, quantity)
            if not is_valid:
                order.order_status = 'FAILED'
                order.failure_reason = error_msg
                db.session.commit()
                raise InsufficientSharesError(error_msg) if "Insufficient shares" in error_msg else ValidationError(error_msg)
            
            # Execute the order with database locks
            self._execute_sell_order(order, user_id, company.company_id, quantity, price_per_share, commission, gross_proceeds, net_proceeds)
            
            logger.info(
                f"Sell order completed: user={user_id}, symbol={symbol}, "
                f"quantity={quantity}, price=${price_per_share}, proceeds=${net_proceeds}"
            )
            return order
            
        except (ValidationError, InsufficientSharesError) as e:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            order.order_status = 'FAILED'
            order.failure_reason = f"System error: {str(e)}"
            db.session.commit()
            logger.error(f"Sell order failed for user {user_id}: {str(e)}")
            raise ValidationError("Order failed due to system error. Please try again.")
    
    def _execute_sell_order(
        self, 
        order: Order, 
        user_id: int, 
        company_id: int, 
        quantity: int, 
        price_per_share: Decimal, 
        commission: Decimal,
        gross_proceeds: Decimal,
        net_proceeds: Decimal
    ):
        """
        Execute sell order with atomic transaction
        
        Args:
            order: Order object
            user_id: User ID
            company_id: Company ID
            quantity: Number of shares
            price_per_share: Price per share
            commission: Commission fee
            gross_proceeds: Gross proceeds before commission
            net_proceeds: Net proceeds after commission
        """
        # Acquire locks on wallet and holdings
        wallet = db.session.query(Wallet).filter_by(user_id=user_id).with_for_update().first()
        if not wallet:
            raise ValidationError("Wallet not found")
        
        holding = db.session.query(Holdings).filter_by(
            user_id=user_id,
            company_id=company_id
        ).with_for_update().first()
        
        if not holding:
            raise InsufficientSharesError(f"You do not own any shares of this stock")
        
        # Double-check shares with lock
        if holding.quantity < quantity:
            raise InsufficientSharesError(
                f"Insufficient shares. You own {holding.quantity} shares, but attempted to sell {quantity} shares"
            )
        
        # Calculate realized gain/loss
        cost_basis = holding.average_purchase_price * quantity
        realized_gain_loss = (price_per_share * quantity) - cost_basis
        order.realized_gain_loss = realized_gain_loss
        
        # Record balance before transaction
        balance_before = wallet.balance
        
        # Credit wallet with net proceeds
        wallet.balance += net_proceeds
        wallet.last_updated = datetime.utcnow()
        
        # Update or delete holding
        holding.quantity -= quantity
        holding.total_invested -= cost_basis
        
        if holding.quantity == 0:
            # Delete holding if no shares left
            db.session.delete(holding)
        else:
            holding.last_updated = datetime.utcnow()
        
        # Create transaction record for the sale
        sell_transaction = Transaction(
            user_id=user_id,
            transaction_type='SELL',
            order_id=order.order_id,
            company_id=company_id,
            amount=gross_proceeds,  # Positive because it's a credit
            balance_before=balance_before,
            balance_after=wallet.balance + commission,  # Before commission deduction
            description=f"Sold {quantity} shares of {order.company.symbol} at ${price_per_share}/share",
            created_at=datetime.utcnow()
        )
        db.session.add(sell_transaction)
        
        # Create transaction record for commission
        fee_transaction = Transaction(
            user_id=user_id,
            transaction_type='FEE',
            order_id=order.order_id,
            company_id=company_id,
            amount=-commission,  # Negative because it's a debit
            balance_before=wallet.balance + commission,
            balance_after=wallet.balance,
            description=f"Commission fee for sell order (0.1%)",
            created_at=datetime.utcnow()
        )
        db.session.add(fee_transaction)
        
        # Update order status
        order.order_status = 'COMPLETED'
        order.executed_at = datetime.utcnow()
        
        # Commit all changes
        db.session.commit()
        
        # Create notification for order completion
        try:
            gain_loss_text = f"Gain: ${realized_gain_loss:.2f}" if realized_gain_loss >= 0 else f"Loss: ${abs(realized_gain_loss):.2f}"
            self.notification_service.create_notification(
                user_id=user_id,
                notification_type='TRANSACTION',
                title='Sell Order Completed',
                message=f'Successfully sold {quantity} shares of {order.company.symbol} at ${price_per_share:.2f}/share. Proceeds: ${net_proceeds:.2f}. {gain_loss_text}'
            )
        except Exception as e:
            logger.error(f"Failed to create notification for sell order {order.order_id}: {str(e)}")
    
    @handle_errors('database')
    def get_order_history(
        self, 
        user_id: int, 
        filters: Optional[Dict] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Order], int]:
        """
        Get order history with filtering and pagination
        
        Args:
            user_id: User ID
            filters: Optional filters (date_from, date_to, order_type, status, symbol)
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Tuple of (list of orders, total count)
        """
        # Start with base query
        query = Order.query.filter_by(user_id=user_id)
        
        # Apply filters
        if filters:
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(Order.created_at >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(Order.created_at <= filters['date_to'])
            
            if 'order_type' in filters and filters['order_type']:
                query = query.filter(Order.order_type == filters['order_type'])
            
            if 'status' in filters and filters['status']:
                query = query.filter(Order.order_status == filters['status'])
            
            if 'symbol' in filters and filters['symbol']:
                # Join with Company to filter by symbol
                query = query.join(Company).filter(Company.symbol.ilike(f"%{filters['symbol']}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering (most recent first)
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ).items
        
        logger.info(f"Retrieved {len(orders)} orders for user {user_id} (total: {total})")
        return orders, total
    
    @handle_errors('database')
    def get_transaction_history(
        self, 
        user_id: int, 
        filters: Optional[Dict] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        """
        Get transaction history with filtering and pagination
        
        Args:
            user_id: User ID
            filters: Optional filters (date_from, date_to, transaction_type, symbol)
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Tuple of (list of transactions, total count)
        """
        # Start with base query
        query = Transaction.query.filter_by(user_id=user_id)
        
        # Apply filters
        if filters:
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(Transaction.created_at >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(Transaction.created_at <= filters['date_to'])
            
            if 'transaction_type' in filters and filters['transaction_type']:
                query = query.filter(Transaction.transaction_type == filters['transaction_type'])
            
            if 'symbol' in filters and filters['symbol']:
                # Join with Company to filter by symbol
                query = query.join(Company, Transaction.company_id == Company.company_id).filter(
                    Company.symbol.ilike(f"%{filters['symbol']}%")
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering (most recent first)
        transactions = query.order_by(Transaction.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ).items
        
        logger.info(f"Retrieved {len(transactions)} transactions for user {user_id} (total: {total})")
        return transactions, total
