"""
Portfolio Service
Handles portfolio management, wallet operations, and performance analytics
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.wallet import Wallet
from app.models.holding import Holdings
from app.models.transaction import Transaction
from app.models.company import Company
from app.models.price_history import PriceHistory
from app.utils.exceptions import ValidationError, InsufficientFundsError
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio and wallet management"""
    
    def get_wallet_balance(self, user_id):
        """
        Get user's wallet balance
        
        Args:
            user_id: User ID
            
        Returns:
            Decimal: Current wallet balance
            
        Raises:
            ValidationError: If wallet not found
        """
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            raise ValidationError(f"Wallet not found for user {user_id}")
        return wallet.balance
    
    def deposit_funds(self, user_id, amount, description="Deposit"):
        """
        Deposit funds into user's wallet
        
        Args:
            user_id: User ID
            amount: Amount to deposit (must be positive)
            description: Transaction description
            
        Returns:
            Transaction: Created transaction record
            
        Raises:
            ValidationError: If amount is invalid
            SQLAlchemyError: If database operation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        
        try:
            # Get wallet with row-level lock for concurrent transaction safety
            wallet = db.session.query(Wallet).filter_by(user_id=user_id).with_for_update().first()
            if not wallet:
                raise ValidationError(f"Wallet not found for user {user_id}")
            
            # Record balance before transaction
            balance_before = wallet.balance
            
            # Update wallet
            wallet.balance += Decimal(str(amount))
            wallet.total_deposited += Decimal(str(amount))
            wallet.last_updated = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                transaction_type='DEPOSIT',
                amount=Decimal(str(amount)),
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=description,
                created_at=datetime.utcnow()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Deposited {amount} to user {user_id}. New balance: {wallet.balance}")
            return transaction
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during deposit for user {user_id}: {str(e)}")
            raise
    
    def withdraw_funds(self, user_id, amount, description="Withdrawal"):
        """
        Withdraw funds from user's wallet
        
        Args:
            user_id: User ID
            amount: Amount to withdraw (must be positive)
            description: Transaction description
            
        Returns:
            Transaction: Created transaction record
            
        Raises:
            ValidationError: If amount is invalid
            InsufficientFundsError: If wallet balance is insufficient
            SQLAlchemyError: If database operation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
        
        try:
            # Get wallet with row-level lock for concurrent transaction safety
            wallet = db.session.query(Wallet).filter_by(user_id=user_id).with_for_update().first()
            if not wallet:
                raise ValidationError(f"Wallet not found for user {user_id}")
            
            # Check sufficient balance
            if wallet.balance < Decimal(str(amount)):
                raise InsufficientFundsError(
                    f"Insufficient funds. Available: {wallet.balance}, Requested: {amount}"
                )
            
            # Record balance before transaction
            balance_before = wallet.balance
            
            # Update wallet
            wallet.balance -= Decimal(str(amount))
            wallet.total_withdrawn += Decimal(str(amount))
            wallet.last_updated = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                transaction_type='WITHDRAWAL',
                amount=Decimal(str(amount)),
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=description,
                created_at=datetime.utcnow()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Withdrew {amount} from user {user_id}. New balance: {wallet.balance}")
            return transaction
            
        except (ValidationError, InsufficientFundsError):
            db.session.rollback()
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during withdrawal for user {user_id}: {str(e)}")
            raise

    def get_holdings(self, user_id):
        """
        Get all holdings for a user with current prices
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of holdings with current price data
        """
        holdings = db.session.query(
            Holdings,
            Company
        ).join(
            Company, Holdings.company_id == Company.company_id
        ).filter(
            Holdings.user_id == user_id,
            Holdings.quantity > 0
        ).all()
        
        result = []
        for holding, company in holdings:
            # Get latest price
            latest_price = db.session.query(PriceHistory).filter_by(
                company_id=company.company_id
            ).order_by(PriceHistory.date.desc()).first()
            
            current_price = latest_price.close if latest_price else Decimal('0.00')
            current_value = current_price * holding.quantity
            unrealized_gain = current_value - holding.total_invested
            unrealized_gain_pct = (unrealized_gain / holding.total_invested * 100) if holding.total_invested > 0 else Decimal('0.00')
            
            result.append({
                'holding_id': holding.holding_id,
                'symbol': company.symbol,
                'company_name': company.company_name,
                'sector': company.sector,
                'quantity': holding.quantity,
                'average_purchase_price': holding.average_purchase_price,
                'total_invested': holding.total_invested,
                'current_price': current_price,
                'current_value': current_value,
                'unrealized_gain': unrealized_gain,
                'unrealized_gain_pct': unrealized_gain_pct,
                'first_purchase_date': holding.first_purchase_date
            })
        
        return result
    
    def get_portfolio_value(self, user_id):
        """
        Calculate total portfolio value (current market value of all holdings)
        
        Args:
            user_id: User ID
            
        Returns:
            Decimal: Total portfolio value
        """
        holdings = self.get_holdings(user_id)
        total_value = sum(h['current_value'] for h in holdings)
        return Decimal(str(total_value))
    
    def calculate_unrealized_gains(self, user_id):
        """
        Calculate unrealized gains/losses for each holding
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Dictionary with total unrealized gain and per-holding breakdown
        """
        holdings = self.get_holdings(user_id)
        
        total_unrealized_gain = Decimal('0.00')
        holdings_breakdown = []
        
        for holding in holdings:
            total_unrealized_gain += holding['unrealized_gain']
            holdings_breakdown.append({
                'symbol': holding['symbol'],
                'company_name': holding['company_name'],
                'unrealized_gain': holding['unrealized_gain'],
                'unrealized_gain_pct': holding['unrealized_gain_pct']
            })
        
        return {
            'total_unrealized_gain': total_unrealized_gain,
            'holdings': holdings_breakdown
        }
    
    def get_portfolio_summary(self, user_id):
        """
        Get comprehensive portfolio summary with aggregated metrics
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Portfolio summary with key metrics
        """
        holdings = self.get_holdings(user_id)
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        
        # Calculate totals
        total_invested = sum(h['total_invested'] for h in holdings)
        total_current_value = sum(h['current_value'] for h in holdings)
        total_unrealized_gain = total_current_value - total_invested
        total_unrealized_gain_pct = (total_unrealized_gain / total_invested * 100) if total_invested > 0 else Decimal('0.00')
        
        # Calculate realized gains from completed SELL transactions
        realized_gains = db.session.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'SELL'
        ).scalar() or Decimal('0.00')
        
        # Get total fees paid
        total_fees = db.session.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'FEE'
        ).scalar() or Decimal('0.00')
        
        return {
            'wallet_balance': wallet.balance if wallet else Decimal('0.00'),
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_unrealized_gain': total_unrealized_gain,
            'total_unrealized_gain_pct': total_unrealized_gain_pct,
            'realized_gains': realized_gains,
            'total_fees': abs(total_fees),
            'total_portfolio_value': total_current_value + (wallet.balance if wallet else Decimal('0.00')),
            'number_of_holdings': len(holdings),
            'holdings': holdings
        }

    def get_performance_metrics(self, user_id):
        """
        Calculate performance metrics including returns and win rate
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Performance metrics
        """
        from app.models.order import Order
        
        # Get portfolio summary
        summary = self.get_portfolio_summary(user_id)
        
        # Calculate total return (realized + unrealized)
        total_return_amount = summary['total_unrealized_gain'] + summary['realized_gains']
        total_return_pct = (total_return_amount / summary['total_invested'] * 100) if summary['total_invested'] > 0 else Decimal('0.00')
        
        # Get all completed orders
        completed_orders = Order.query.filter_by(
            user_id=user_id,
            order_status='COMPLETED'
        ).all()
        
        # Calculate win rate (profitable trades / total trades)
        sell_orders = [o for o in completed_orders if o.order_type == 'SELL']
        profitable_trades = sum(1 for o in sell_orders if o.realized_gain_loss and o.realized_gain_loss > 0)
        total_trades = len(sell_orders)
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else Decimal('0.00')
        
        # Find best and worst performing stocks
        holdings = self.get_holdings(user_id)
        best_performer = None
        worst_performer = None
        
        if holdings:
            best_performer = max(holdings, key=lambda h: h['unrealized_gain_pct'])
            worst_performer = min(holdings, key=lambda h: h['unrealized_gain_pct'])
        
        # Calculate annualized return (simplified - assumes 1 year holding period)
        # In a real implementation, this would use actual holding periods
        annualized_return = total_return_pct  # Simplified
        
        return {
            'total_return_amount': total_return_amount,
            'total_return_pct': total_return_pct,
            'annualized_return': annualized_return,
            'win_rate': win_rate,
            'profitable_trades': profitable_trades,
            'total_trades': total_trades,
            'best_performer': {
                'symbol': best_performer['symbol'],
                'company_name': best_performer['company_name'],
                'return_pct': best_performer['unrealized_gain_pct']
            } if best_performer else None,
            'worst_performer': {
                'symbol': worst_performer['symbol'],
                'company_name': worst_performer['company_name'],
                'return_pct': worst_performer['unrealized_gain_pct']
            } if worst_performer else None
        }
    
    def get_sector_allocation(self, user_id):
        """
        Calculate sector allocation for pie chart
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of sectors with their allocation percentages
        """
        holdings = self.get_holdings(user_id)
        
        if not holdings:
            return []
        
        # Group by sector
        sector_values = {}
        total_value = Decimal('0.00')
        
        for holding in holdings:
            sector = holding['sector'] or 'Unknown'
            value = holding['current_value']
            
            if sector in sector_values:
                sector_values[sector] += value
            else:
                sector_values[sector] = value
            
            total_value += value
        
        # Calculate percentages
        sector_allocation = []
        for sector, value in sector_values.items():
            percentage = (value / total_value * 100) if total_value > 0 else Decimal('0.00')
            sector_allocation.append({
                'sector': sector,
                'value': value,
                'percentage': percentage
            })
        
        # Sort by value descending
        sector_allocation.sort(key=lambda x: x['value'], reverse=True)
        
        return sector_allocation
