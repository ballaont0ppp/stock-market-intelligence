"""
Portfolio Routes
Portfolio viewing and wallet management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.portfolio_service import PortfolioService, ValidationError, InsufficientFundsError
from app.forms.portfolio_forms import DepositForm, WithdrawForm
from sqlalchemy.exc import SQLAlchemyError
import logging

bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')
logger = logging.getLogger(__name__)


@bp.route('/')
@login_required
def index():
    """Display user's portfolio with holdings and summary"""
    try:
        service = PortfolioService()
        portfolio_summary = service.get_portfolio_summary(current_user.user_id)
        
        return render_template(
            'portfolio/index.html',
            summary=portfolio_summary
        )
    except Exception as e:
        logger.error(f"Error loading portfolio for user {current_user.user_id}: {str(e)}")
        flash('Error loading portfolio. Please try again later.', 'error')
        return redirect(url_for('dashboard.index'))


@bp.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    """Wallet management page with deposit and withdrawal forms"""
    deposit_form = DepositForm()
    withdraw_form = WithdrawForm()
    service = PortfolioService()
    
    try:
        # Get current wallet balance
        balance = service.get_wallet_balance(current_user.user_id)
        
        # Handle deposit form submission
        if deposit_form.validate_on_submit() and 'deposit' in request.form:
            try:
                amount = float(deposit_form.amount.data)
                description = deposit_form.description.data or 'Deposit'
                
                transaction = service.deposit_funds(
                    current_user.user_id,
                    amount,
                    description
                )
                
                flash(f'Successfully deposited ${amount:.2f}', 'success')
                return redirect(url_for('portfolio.wallet'))
                
            except ValidationError as e:
                flash(str(e), 'error')
            except SQLAlchemyError as e:
                logger.error(f"Database error during deposit: {str(e)}")
                flash('An error occurred. Please try again later.', 'error')
        
        # Handle withdrawal form submission
        if withdraw_form.validate_on_submit() and 'withdraw' in request.form:
            try:
                amount = float(withdraw_form.amount.data)
                description = withdraw_form.description.data or 'Withdrawal'
                
                transaction = service.withdraw_funds(
                    current_user.user_id,
                    amount,
                    description
                )
                
                flash(f'Successfully withdrew ${amount:.2f}', 'success')
                return redirect(url_for('portfolio.wallet'))
                
            except ValidationError as e:
                flash(str(e), 'error')
            except InsufficientFundsError as e:
                flash(str(e), 'error')
            except SQLAlchemyError as e:
                logger.error(f"Database error during withdrawal: {str(e)}")
                flash('An error occurred. Please try again later.', 'error')
        
        return render_template(
            'portfolio/wallet.html',
            balance=balance,
            deposit_form=deposit_form,
            withdraw_form=withdraw_form
        )
        
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        logger.error(f"Error loading wallet for user {current_user.user_id}: {str(e)}")
        flash('Error loading wallet. Please try again later.', 'error')
        return redirect(url_for('dashboard.index'))
