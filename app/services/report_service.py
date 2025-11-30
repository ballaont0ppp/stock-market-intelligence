"""
Report Service
Generate transaction, billing, and performance reports
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_
from app import db
from app.models.transaction import Transaction
from app.models.order import Order
from app.models.holding import Holdings
from app.models.company import Company
from app.models.price_history import PriceHistory
from app.services.stock_repository import StockRepository


class ReportService:
    """Service for generating various reports"""
    
    def __init__(self):
        self.stock_repo = StockRepository()
    
    def generate_transaction_report(self, user_id, start_date=None, end_date=None):
        """
        Generate comprehensive transaction report for a user
        
        Args:
            user_id: User ID
            start_date: Start date for report (datetime or None for all time)
            end_date: End date for report (datetime or None for today)
        
        Returns:
            dict: Transaction report with details and summary statistics
        """
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        
        # Build query
        query = Transaction.query.filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        query = query.filter(Transaction.created_at <= end_date)
        
        # Get all transactions ordered by date
        transactions = query.order_by(Transaction.created_at.desc()).all()
        
        # Build transaction details list
        transaction_details = []
        for txn in transactions:
            detail = {
                'transaction_id': txn.transaction_id,
                'date': txn.created_at,
                'type': txn.transaction_type,
                'amount': float(txn.amount),
                'balance_before': float(txn.balance_before),
                'balance_after': float(txn.balance_after),
                'description': txn.description,
                'company_symbol': None,
                'company_name': None
            }
            
            # Add company info if applicable
            if txn.company_id:
                company = Company.query.get(txn.company_id)
                if company:
                    detail['company_symbol'] = company.symbol
                    detail['company_name'] = company.company_name
            
            transaction_details.append(detail)
        
        # Calculate summary statistics
        total_buys = 0
        total_sells = 0
        total_deposits = 0
        total_withdrawals = 0
        total_dividends = 0
        total_commissions = 0
        buy_count = 0
        sell_count = 0
        
        for txn in transactions:
            if txn.transaction_type == 'BUY':
                total_buys += abs(float(txn.amount))
                buy_count += 1
            elif txn.transaction_type == 'SELL':
                total_sells += float(txn.amount)
                sell_count += 1
            elif txn.transaction_type == 'DEPOSIT':
                total_deposits += float(txn.amount)
            elif txn.transaction_type == 'WITHDRAWAL':
                total_withdrawals += abs(float(txn.amount))
            elif txn.transaction_type == 'DIVIDEND':
                total_dividends += float(txn.amount)
            elif txn.transaction_type == 'FEE':
                total_commissions += abs(float(txn.amount))
        
        # Calculate net trading activity
        net_trading = total_sells - total_buys
        
        summary = {
            'total_transactions': len(transactions),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'total_buys': total_buys,
            'total_sells': total_sells,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_dividends': total_dividends,
            'total_commissions': total_commissions,
            'net_trading': net_trading,
            'start_date': start_date,
            'end_date': end_date
        }
        
        return {
            'transactions': transaction_details,
            'summary': summary
        }
    
    def generate_billing_report(self, user_id, month, year):
        """
        Generate billing report showing fees and charges for a specific month
        
        Args:
            user_id: User ID
            month: Month (1-12)
            year: Year (e.g., 2024)
        
        Returns:
            dict: Billing report with transaction counts, volumes, and fee breakdown
        """
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get all transactions for the month
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date,
            Transaction.created_at < end_date
        ).all()
        
        # Get all orders for the month
        orders = Order.query.filter(
            Order.user_id == user_id,
            Order.created_at >= start_date,
            Order.created_at < end_date,
            Order.order_status == 'COMPLETED'
        ).all()
        
        # Calculate transaction counts and volumes
        buy_count = 0
        sell_count = 0
        buy_volume = Decimal('0')
        sell_volume = Decimal('0')
        
        for order in orders:
            if order.order_type == 'BUY':
                buy_count += 1
                buy_volume += order.total_amount
            elif order.order_type == 'SELL':
                sell_count += 1
                sell_volume += order.total_amount
        
        # Calculate fee breakdown
        buy_commissions = Decimal('0')
        sell_commissions = Decimal('0')
        total_fees = Decimal('0')
        
        for txn in transactions:
            if txn.transaction_type == 'FEE':
                fee_amount = abs(txn.amount)
                total_fees += fee_amount
                
                # Determine if this fee is from a buy or sell order
                if txn.order_id:
                    order = Order.query.get(txn.order_id)
                    if order:
                        if order.order_type == 'BUY':
                            buy_commissions += fee_amount
                        elif order.order_type == 'SELL':
                            sell_commissions += fee_amount
        
        # Calculate other transaction types
        deposits = sum(float(txn.amount) for txn in transactions if txn.transaction_type == 'DEPOSIT')
        withdrawals = sum(abs(float(txn.amount)) for txn in transactions if txn.transaction_type == 'WITHDRAWAL')
        dividends = sum(float(txn.amount) for txn in transactions if txn.transaction_type == 'DIVIDEND')
        
        return {
            'month': month,
            'year': year,
            'period': f"{start_date.strftime('%B %Y')}",
            'transaction_counts': {
                'buy_orders': buy_count,
                'sell_orders': sell_count,
                'total_orders': buy_count + sell_count,
                'deposits': sum(1 for txn in transactions if txn.transaction_type == 'DEPOSIT'),
                'withdrawals': sum(1 for txn in transactions if txn.transaction_type == 'WITHDRAWAL'),
                'dividends': sum(1 for txn in transactions if txn.transaction_type == 'DIVIDEND')
            },
            'transaction_volumes': {
                'buy_volume': float(buy_volume),
                'sell_volume': float(sell_volume),
                'total_volume': float(buy_volume + sell_volume),
                'deposits': deposits,
                'withdrawals': withdrawals,
                'dividends': dividends
            },
            'fee_breakdown': {
                'buy_commissions': float(buy_commissions),
                'sell_commissions': float(sell_commissions),
                'total_fees': float(total_fees)
            },
            'summary': {
                'total_transactions': len(transactions),
                'total_fees_paid': float(total_fees),
                'average_fee_per_trade': float(total_fees / (buy_count + sell_count)) if (buy_count + sell_count) > 0 else 0
            }
        }
    
    def generate_performance_report(self, user_id, period='all'):
        """
        Generate performance report showing portfolio performance over time
        
        Args:
            user_id: User ID
            period: Time period ('1w', '1m', '3m', '6m', '1y', 'all')
        
        Returns:
            dict: Performance report with returns, benchmarks, and stock analysis
        """
        # Calculate date range based on period
        end_date = datetime.utcnow()
        
        if period == '1w':
            start_date = end_date - timedelta(days=7)
        elif period == '1m':
            start_date = end_date - timedelta(days=30)
        elif period == '3m':
            start_date = end_date - timedelta(days=90)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:  # 'all'
            start_date = None
        
        # Get current holdings
        holdings = Holdings.query.filter(Holdings.user_id == user_id).all()
        
        # Calculate current portfolio value
        current_portfolio_value = Decimal('0')
        total_invested = Decimal('0')
        holdings_details = []
        
        for holding in holdings:
            company = Company.query.get(holding.company_id)
            if not company:
                continue
            
            # Get current price
            current_price = self.stock_repo.get_current_price(company.symbol)
            if current_price is None:
                current_price = holding.average_purchase_price
            
            current_value = Decimal(str(current_price)) * holding.quantity
            invested = holding.total_invested
            gain_loss = current_value - invested
            gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else Decimal('0')
            
            current_portfolio_value += current_value
            total_invested += invested
            
            holdings_details.append({
                'symbol': company.symbol,
                'company_name': company.company_name,
                'quantity': holding.quantity,
                'average_price': float(holding.average_purchase_price),
                'current_price': float(current_price),
                'invested': float(invested),
                'current_value': float(current_value),
                'gain_loss': float(gain_loss),
                'gain_loss_pct': float(gain_loss_pct)
            })
        
        # Sort by gain/loss percentage
        holdings_details.sort(key=lambda x: x['gain_loss_pct'], reverse=True)
        
        # Get best and worst performers
        best_performer = holdings_details[0] if holdings_details else None
        worst_performer = holdings_details[-1] if holdings_details else None
        
        # Calculate overall returns
        total_gain_loss = current_portfolio_value - total_invested
        total_return_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else Decimal('0')
        
        # Get completed orders for win rate calculation
        completed_orders = Order.query.filter(
            Order.user_id == user_id,
            Order.order_status == 'COMPLETED',
            Order.order_type == 'SELL'
        )
        
        if start_date:
            completed_orders = completed_orders.filter(Order.executed_at >= start_date)
        
        completed_orders = completed_orders.all()
        
        # Calculate win rate
        profitable_trades = sum(1 for order in completed_orders if order.realized_gain_loss and order.realized_gain_loss > 0)
        total_trades = len(completed_orders)
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate portfolio value over time (simplified - using transaction history)
        portfolio_history = self._calculate_portfolio_history(user_id, start_date, end_date)
        
        # Calculate annualized return
        if start_date and total_invested > 0:
            days = (end_date - start_date).days
            if days > 0:
                years = days / 365.25
                annualized_return = ((current_portfolio_value / total_invested) ** (1 / years) - 1) * 100
            else:
                annualized_return = 0
        else:
            annualized_return = 0
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'current_portfolio_value': float(current_portfolio_value),
            'total_invested': float(total_invested),
            'total_gain_loss': float(total_gain_loss),
            'total_return_pct': float(total_return_pct),
            'annualized_return': float(annualized_return),
            'win_rate': win_rate,
            'profitable_trades': profitable_trades,
            'total_trades': total_trades,
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'holdings': holdings_details,
            'portfolio_history': portfolio_history
        }
    
    def _calculate_portfolio_history(self, user_id, start_date, end_date):
        """
        Calculate portfolio value over time
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
        
        Returns:
            list: List of {date, value} dictionaries
        """
        # This is a simplified implementation
        # In a production system, you'd want to cache daily portfolio snapshots
        
        history = []
        
        # Get all transactions in the period
        query = Transaction.query.filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        transactions = query.filter(Transaction.created_at <= end_date).order_by(Transaction.created_at).all()
        
        # Sample dates (weekly for longer periods, daily for shorter)
        if start_date:
            days_diff = (end_date - start_date).days
            if days_diff > 90:
                # Weekly sampling
                sample_interval = 7
            else:
                # Daily sampling
                sample_interval = 1
            
            current_date = start_date
            while current_date <= end_date:
                # Get balance at this date (last transaction before or on this date)
                txn = Transaction.query.filter(
                    Transaction.user_id == user_id,
                    Transaction.created_at <= current_date
                ).order_by(Transaction.created_at.desc()).first()
                
                if txn:
                    history.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'value': float(txn.balance_after)
                    })
                
                current_date += timedelta(days=sample_interval)
        
        return history

    def export_transactions_csv(self, user_id, start_date=None, end_date=None):
        """
        Export transactions to CSV format
        
        Args:
            user_id: User ID
            start_date: Start date for export
            end_date: End date for export
            
        Returns:
            str: CSV formatted string
        """
        import csv
        from io import StringIO
        
        # Get transactions
        query = Transaction.query.filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        transactions = query.order_by(Transaction.created_at.desc()).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date',
            'Type',
            'Symbol',
            'Quantity',
            'Amount',
            'Balance Before',
            'Balance After',
            'Description'
        ])
        
        # Write data
        for txn in transactions:
            company_symbol = ''
            if txn.company_id:
                company = Company.query.get(txn.company_id)
                if company:
                    company_symbol = company.symbol
            
            writer.writerow([
                txn.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                txn.transaction_type,
                company_symbol,
                txn.quantity if txn.quantity else '',
                f"{txn.amount:.2f}",
                f"{txn.balance_before:.2f}" if txn.balance_before else '',
                f"{txn.balance_after:.2f}" if txn.balance_after else '',
                txn.description or ''
            ])
        
        return output.getvalue()
