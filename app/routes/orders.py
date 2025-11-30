"""
Orders Blueprint
Routes for buy/sell orders and order history
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from decimal import Decimal

from app import db
from app.services.transaction_engine import TransactionEngine
from app.services.stock_repository import StockRepository
from app.forms.order_forms import BuyOrderForm, SellOrderForm, OrderFilterForm
from app.utils.exceptions import (
    ValidationError,
    InsufficientFundsError,
    InsufficientSharesError,
    ExternalAPIError
)

logger = logging.getLogger(__name__)

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# Services will be initialized on first use
transaction_engine = None
stock_repo = None

def get_transaction_engine():
    """Lazy load transaction engine"""
    global transaction_engine
    if transaction_engine is None:
        transaction_engine = TransactionEngine()
    return transaction_engine

def get_stock_repo():
    """Lazy load stock repository"""
    global stock_repo
    if stock_repo is None:
        stock_repo = StockRepository()
    return stock_repo


@orders_bp.route('/')
@login_required
def index():
    """Display order history"""
    # Get filter form
    filter_form = OrderFilterForm(request.args)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build filters
    filters = {}
    if filter_form.order_type.data:
        filters['order_type'] = filter_form.order_type.data
    if filter_form.status.data:
        filters['status'] = filter_form.status.data
    if filter_form.symbol.data:
        filters['symbol'] = filter_form.symbol.data
    
    # Get order history
    try:
        orders, total = get_transaction_engine().get_order_history(
            user_id=current_user.user_id,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        
        return render_template(
            'orders/index.html',
            orders=orders,
            filter_form=filter_form,
            page=page,
            total_pages=total_pages,
            total=total
        )
    except Exception as e:
        logger.error(f"Error loading order history: {str(e)}")
        flash('Error loading order history', 'error')
        return render_template(
            'orders/index.html',
            orders=[],
            filter_form=filter_form,
            page=1,
            total_pages=1,
            total=0
        )


@orders_bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    """Buy order page"""
    form = BuyOrderForm()
    
    if form.validate_on_submit():
        symbol = form.symbol.data.upper().strip()
        quantity = form.quantity.data
        
        try:
            # Create buy order
            order = get_transaction_engine().create_buy_order(
                user_id=current_user.user_id,
                symbol=symbol,
                quantity=quantity
            )
            
            # Success message
            flash(
                f'Order completed successfully! Purchased {quantity} shares of {symbol} '
                f'at ${order.price_per_share:.2f} per share. '
                f'Total cost: ${order.total_amount:.2f} (including ${order.commission_fee:.2f} commission)',
                'success'
            )
            return redirect(url_for('orders.index'))
            
        except InsufficientFundsError as e:
            flash(str(e), 'error')
        except ValidationError as e:
            flash(str(e), 'error')
        except ExternalAPIError as e:
            flash(f'Unable to fetch stock price: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Buy order error: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'error')
    
    return render_template('orders/buy.html', form=form)


@orders_bp.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    """Sell order page"""
    form = SellOrderForm()
    
    if form.validate_on_submit():
        symbol = form.symbol.data.upper().strip()
        quantity = form.quantity.data
        
        try:
            # Create sell order
            order = get_transaction_engine().create_sell_order(
                user_id=current_user.user_id,
                symbol=symbol,
                quantity=quantity
            )
            
            # Calculate gain/loss percentage
            gain_loss_pct = 0
            if order.realized_gain_loss:
                cost_basis = order.price_per_share * quantity - order.realized_gain_loss
                if cost_basis > 0:
                    gain_loss_pct = (order.realized_gain_loss / cost_basis) * 100
            
            # Success message
            flash(
                f'Order completed successfully! Sold {quantity} shares of {symbol} '
                f'at ${order.price_per_share:.2f} per share. '
                f'Total proceeds: ${order.total_amount:.2f} (after ${order.commission_fee:.2f} commission). '
                f'Realized gain/loss: ${order.realized_gain_loss:.2f} ({gain_loss_pct:+.1f}%)',
                'success'
            )
            return redirect(url_for('orders.index'))
            
        except InsufficientSharesError as e:
            flash(str(e), 'error')
        except ValidationError as e:
            flash(str(e), 'error')
        except ExternalAPIError as e:
            flash(f'Unable to fetch stock price: {str(e)}', 'error')
        except Exception as e:
            logger.error(f"Sell order error: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'error')
    
    return render_template('orders/sell.html', form=form)


@orders_bp.route('/api/price-preview')
@login_required
def price_preview():
    """API endpoint for real-time price preview"""
    symbol = request.args.get('symbol', '').upper().strip()
    quantity = request.args.get('quantity', 0, type=int)
    order_type = request.args.get('type', 'BUY').upper()
    
    if not symbol or quantity <= 0:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    try:
        # Get current price
        price = get_stock_repo().get_current_price_with_mode(symbol)
        
        # Calculate costs/proceeds
        subtotal = price * quantity
        commission = get_transaction_engine().calculate_commission(subtotal)
        
        if order_type == 'BUY':
            total = subtotal + commission
            result = {
                'symbol': symbol,
                'price_per_share': float(price),
                'quantity': quantity,
                'subtotal': float(subtotal),
                'commission': float(commission),
                'total': float(total),
                'type': 'BUY'
            }
        else:  # SELL
            total = subtotal - commission
            result = {
                'symbol': symbol,
                'price_per_share': float(price),
                'quantity': quantity,
                'gross_proceeds': float(subtotal),
                'commission': float(commission),
                'net_proceeds': float(total),
                'type': 'SELL'
            }
        
        return jsonify(result)
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ExternalAPIError as e:
        return jsonify({'error': f'Unable to fetch price: {str(e)}'}), 503
    except Exception as e:
        logger.error(f"Price preview error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """View order details"""
    from app.models.order import Order
    
    order = Order.query.get_or_404(order_id)
    
    # Ensure user owns this order
    if order.user_id != current_user.user_id:
        flash('Access denied', 'error')
        return redirect(url_for('orders.index'))
    
    # Get related transactions
    transactions = order.transactions
    
    return render_template(
        'orders/view.html',
        order=order,
        transactions=transactions
    )


@orders_bp.route('/transactions')
@login_required
def transactions():
    """Display transaction history"""
    from app.forms.order_forms import OrderFilterForm
    
    # Get filter form
    filter_form = OrderFilterForm(request.args)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build filters
    filters = {}
    if request.args.get('transaction_type'):
        filters['transaction_type'] = request.args.get('transaction_type')
    if request.args.get('symbol'):
        filters['symbol'] = request.args.get('symbol')
    if request.args.get('date_from'):
        try:
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
        except ValueError:
            pass
    
    # Get transaction history
    try:
        transaction_list, total = get_transaction_engine().get_transaction_history(
            user_id=current_user.user_id,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        
        # Calculate summary statistics
        from app.models.transaction import Transaction
        from sqlalchemy import func
        
        summary_query = Transaction.query.filter_by(user_id=current_user.user_id)
        
        # Apply same filters to summary
        if filters.get('date_from'):
            summary_query = summary_query.filter(Transaction.created_at >= filters['date_from'])
        if filters.get('date_to'):
            summary_query = summary_query.filter(Transaction.created_at <= filters['date_to'])
        if filters.get('transaction_type'):
            summary_query = summary_query.filter(Transaction.transaction_type == filters['transaction_type'])
        
        # Calculate totals
        buy_total = summary_query.filter(Transaction.transaction_type == 'BUY').with_entities(
            func.sum(Transaction.amount)
        ).scalar() or Decimal('0.00')
        
        sell_total = summary_query.filter(Transaction.transaction_type == 'SELL').with_entities(
            func.sum(Transaction.amount)
        ).scalar() or Decimal('0.00')
        
        fee_total = summary_query.filter(Transaction.transaction_type == 'FEE').with_entities(
            func.sum(Transaction.amount)
        ).scalar() or Decimal('0.00')
        
        summary = {
            'total_transactions': total,
            'buy_total': abs(buy_total),
            'sell_total': sell_total,
            'fee_total': abs(fee_total),
            'net_profit_loss': sell_total + buy_total  # buy_total is negative
        }
        
        return render_template(
            'orders/transactions.html',
            transactions=transaction_list,
            page=page,
            total_pages=total_pages,
            total=total,
            summary=summary,
            filters=filters
        )
    except Exception as e:
        logger.error(f"Error loading transaction history: {str(e)}")
        flash('Error loading transaction history', 'error')
        return render_template(
            'orders/transactions.html',
            transactions=[],
            page=1,
            total_pages=1,
            total=0,
            summary={
                'total_transactions': 0,
                'buy_total': Decimal('0.00'),
                'sell_total': Decimal('0.00'),
                'fee_total': Decimal('0.00'),
                'net_profit_loss': Decimal('0.00')
            },
            filters={}
        )


@orders_bp.route('/transactions/export')
@login_required
def export_transactions():
    """Export transaction history to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    # Get all transactions (no pagination)
    filters = {}
    if request.args.get('transaction_type'):
        filters['transaction_type'] = request.args.get('transaction_type')
    if request.args.get('symbol'):
        filters['symbol'] = request.args.get('symbol')
    if request.args.get('date_from'):
        try:
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
        except ValueError:
            pass
    
    try:
        # Get all transactions matching filters
        from app.models.transaction import Transaction
        query = Transaction.query.filter_by(user_id=current_user.user_id)
        
        if filters.get('date_from'):
            query = query.filter(Transaction.created_at >= filters['date_from'])
        if filters.get('date_to'):
            query = query.filter(Transaction.created_at <= filters['date_to'])
        if filters.get('transaction_type'):
            query = query.filter(Transaction.transaction_type == filters['transaction_type'])
        
        transactions = query.order_by(Transaction.created_at.desc()).all()
        
        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow([
            'Date', 'Type', 'Symbol', 'Company', 'Amount', 
            'Balance Before', 'Balance After', 'Description'
        ])
        
        # Write data
        for transaction in transactions:
            company_symbol = transaction.company.symbol if transaction.company else '-'
            company_name = transaction.company.company_name if transaction.company else '-'
            
            writer.writerow([
                transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.transaction_type,
                company_symbol,
                company_name,
                f"{transaction.amount:.2f}",
                f"{transaction.balance_before:.2f}",
                f"{transaction.balance_after:.2f}",
                transaction.description or ''
            ])
        
        # Create response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
        
    except Exception as e:
        logger.error(f"Error exporting transactions: {str(e)}")
        flash('Error exporting transactions', 'error')
        return redirect(url_for('orders.transactions'))
