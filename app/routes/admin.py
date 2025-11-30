"""
Admin Routes
Administrative dashboard and management functions
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app import db
from app.models.dividend import Dividend, DividendPayment
from app.models.company import Company
from app.models.user import User
from app.models.broker import Broker
from app.models.transaction import Transaction
from app.forms.dividend_forms import DividendForm
from app.services.dividend_manager import DividendManager
from app.services.admin_service import AdminService
from app.utils.decorators import admin_required
from app.utils.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard overview with system metrics"""
    try:
        # Get system metrics
        metrics = AdminService.get_system_metrics()
        
        # Get recent activity (last 20 transactions)
        recent_activity = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(20).all()
        
        # Get system alerts (placeholder for now)
        alerts = []
        
        # Check for suspended users
        suspended_count = metrics['users']['suspended']
        if suspended_count > 0:
            alerts.append({
                'type': 'warning',
                'message': f'{suspended_count} user(s) currently suspended'
            })
        
        # Check for failed transactions today
        if metrics['transactions']['today'] == 0:
            alerts.append({
                'type': 'info',
                'message': 'No transactions processed today'
            })
        
        return render_template(
            'admin/index.html',
            metrics=metrics,
            recent_activity=recent_activity,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/index.html', metrics=None, recent_activity=[], alerts=[])


# Dividend Management Routes

@bp.route('/dividends')
@login_required
@admin_required
def dividends():
    """List all dividends"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    company_symbol = request.args.get('company', '')
    dividend_type = request.args.get('type', '')
    status = request.args.get('status', 'all')  # all, upcoming, past
    
    # Build query
    query = Dividend.query.join(Company)
    
    if company_symbol:
        query = query.filter(Company.symbol.ilike(f'%{company_symbol}%'))
    
    if dividend_type:
        query = query.filter(Dividend.dividend_type == dividend_type)
    
    if status == 'upcoming':
        from datetime import date
        query = query.filter(Dividend.payment_date >= date.today())
    elif status == 'past':
        from datetime import date
        query = query.filter(Dividend.payment_date < date.today())
    
    # Order by payment date descending
    query = query.order_by(Dividend.payment_date.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    dividends = pagination.items
    
    return render_template(
        'admin/dividends/index.html',
        dividends=dividends,
        pagination=pagination,
        company_symbol=company_symbol,
        dividend_type=dividend_type,
        status=status
    )


@bp.route('/dividends/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_dividend():
    """Create a new dividend"""
    form = DividendForm()
    
    if form.validate_on_submit():
        try:
            # Get company by symbol
            company = Company.query.filter_by(symbol=form.company_symbol.data.upper()).first()
            
            if not company:
                flash(f'Company with symbol {form.company_symbol.data.upper()} not found', 'error')
                return render_template('admin/dividends/create.html', form=form)
            
            # Prepare dividend data
            dividend_data = {
                'dividend_per_share': float(form.dividend_per_share.data),
                'ex_dividend_date': form.ex_dividend_date.data,
                'record_date': form.record_date.data,
                'payment_date': form.payment_date.data,
                'announcement_date': form.announcement_date.data,
                'dividend_type': form.dividend_type.data
            }
            
            # Create dividend
            dividend_manager = DividendManager()
            dividend = dividend_manager.create_dividend(company.company_id, dividend_data)
            
            flash(
                f'Dividend created successfully for {company.symbol}: '
                f'${dividend.dividend_per_share}/share on {dividend.payment_date}',
                'success'
            )
            return redirect(url_for('admin.dividends'))
            
        except ValidationError as e:
            flash(str(e), 'error')
        except BusinessLogicError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error creating dividend: {str(e)}', 'error')
    
    return render_template('admin/dividends/create.html', form=form)


@bp.route('/dividends/<int:dividend_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_dividend(dividend_id):
    """Edit an existing dividend"""
    dividend = Dividend.query.get_or_404(dividend_id)
    form = DividendForm()
    
    if form.validate_on_submit():
        try:
            # Prepare update data
            update_data = {
                'dividend_per_share': float(form.dividend_per_share.data),
                'ex_dividend_date': form.ex_dividend_date.data,
                'record_date': form.record_date.data,
                'payment_date': form.payment_date.data,
                'announcement_date': form.announcement_date.data,
                'dividend_type': form.dividend_type.data
            }
            
            # Update dividend
            dividend_manager = DividendManager()
            dividend = dividend_manager.update_dividend(dividend_id, update_data)
            
            flash(
                f'Dividend updated successfully for {dividend.company.symbol}',
                'success'
            )
            return redirect(url_for('admin.dividends'))
            
        except ValidationError as e:
            flash(str(e), 'error')
        except BusinessLogicError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error updating dividend: {str(e)}', 'error')
    
    elif request.method == 'GET':
        # Pre-populate form with existing data
        form.company_symbol.data = dividend.company.symbol
        form.dividend_per_share.data = dividend.dividend_per_share
        form.ex_dividend_date.data = dividend.ex_dividend_date
        form.record_date.data = dividend.record_date
        form.payment_date.data = dividend.payment_date
        form.announcement_date.data = dividend.announcement_date
        form.dividend_type.data = dividend.dividend_type
    
    return render_template('admin/dividends/edit.html', form=form, dividend=dividend)


@bp.route('/dividends/<int:dividend_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_dividend(dividend_id):
    """Delete a dividend"""
    try:
        dividend_manager = DividendManager()
        dividend = Dividend.query.get_or_404(dividend_id)
        company_symbol = dividend.company.symbol
        
        dividend_manager.delete_dividend(dividend_id)
        
        flash(f'Dividend for {company_symbol} deleted successfully', 'success')
        
    except ValidationError as e:
        flash(str(e), 'error')
    except BusinessLogicError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting dividend: {str(e)}', 'error')
    
    return redirect(url_for('admin.dividends'))


@bp.route('/dividends/<int:dividend_id>')
@login_required
@admin_required
def view_dividend(dividend_id):
    """View dividend details and payment history"""
    dividend = Dividend.query.get_or_404(dividend_id)
    
    # Get payment history
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    payments_query = DividendPayment.query.filter_by(dividend_id=dividend_id).order_by(
        DividendPayment.paid_at.desc()
    )
    
    pagination = payments_query.paginate(page=page, per_page=per_page, error_out=False)
    payments = pagination.items
    
    # Calculate summary statistics
    total_payments = DividendPayment.query.filter_by(dividend_id=dividend_id).count()
    total_amount = db.session.query(
        db.func.sum(DividendPayment.amount_paid)
    ).filter_by(dividend_id=dividend_id).scalar() or 0
    
    return render_template(
        'admin/dividends/view.html',
        dividend=dividend,
        payments=payments,
        pagination=pagination,
        total_payments=total_payments,
        total_amount=total_amount
    )


# User Management Routes

@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    is_admin = request.args.get('is_admin', '')
    
    # Build filters
    filters = {}
    if search:
        filters['search'] = search
    if status:
        filters['status'] = status
    if is_admin:
        filters['is_admin'] = is_admin == 'true'
    
    try:
        # Get users
        result = AdminService.get_all_users(filters=filters, page=page, per_page=per_page)
        
        return render_template(
            'admin/users/index.html',
            users=result['users'],
            total=result['total'],
            page=result['page'],
            pages=result['pages'],
            has_next=result['has_next'],
            has_prev=result['has_prev'],
            search=search,
            status=status,
            is_admin_filter=is_admin
        )
        
    except Exception as e:
        logger.error(f"Error loading users: {str(e)}")
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users/index.html', users=[], total=0, page=1, pages=0)


@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View detailed user information"""
    try:
        user_details = AdminService.get_user_details(user_id)
        
        return render_template(
            'admin/users/view.html',
            user_details=user_details
        )
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.users'))
    except Exception as e:
        logger.error(f"Error loading user details: {str(e)}")
        flash(f'Error loading user details: {str(e)}', 'error')
        return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'full_name': request.form.get('full_name'),
                'email': request.form.get('email'),
                'risk_tolerance': request.form.get('risk_tolerance'),
                'investment_goals': request.form.get('investment_goals'),
                'is_admin': request.form.get('is_admin') == 'on'
            }
            
            # Update user
            AdminService.update_user(user_id, data)
            
            flash(f'User {user.email} updated successfully', 'success')
            return redirect(url_for('admin.view_user', user_id=user_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('admin/users/edit.html', user=user)


@bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    """Suspend a user account"""
    try:
        reason = request.form.get('reason', 'No reason provided')
        AdminService.suspend_user(user_id, reason)
        
        flash('User suspended successfully', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error suspending user: {str(e)}")
        flash(f'Error suspending user: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))


@bp.route('/users/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_user(user_id):
    """Activate a suspended user account"""
    try:
        AdminService.activate_user(user_id)
        
        flash('User activated successfully', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        flash(f'Error activating user: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    try:
        # Prevent self-deletion
        if user_id == current_user.user_id:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('admin.users'))
        
        user = User.query.get_or_404(user_id)
        user_email = user.email
        
        AdminService.delete_user(user_id)
        
        flash(f'User {user_email} deleted successfully', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/adjust-balance', methods=['POST'])
@login_required
@admin_required
def adjust_user_balance(user_id):
    """Adjust user's wallet balance"""
    try:
        amount = float(request.form.get('amount', 0))
        reason = request.form.get('reason', 'Admin adjustment')
        
        AdminService.adjust_wallet_balance(user_id, amount, reason)
        
        flash(f'Wallet balance adjusted by ${abs(amount):.2f}', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error adjusting balance: {str(e)}")
        flash(f'Error adjusting balance: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))



# Company Management Routes

@bp.route('/companies')
@login_required
@admin_required
def companies():
    """List all companies with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    search = request.args.get('search', '')
    sector = request.args.get('sector', '')
    is_active = request.args.get('is_active', '')
    
    # Build filters
    filters = {}
    if search:
        filters['search'] = search
    if sector:
        filters['sector'] = sector
    if is_active:
        filters['is_active'] = is_active == 'true'
    
    try:
        # Get companies
        result = AdminService.get_all_companies(filters=filters, page=page, per_page=per_page)
        
        # Get unique sectors for filter dropdown
        sectors = db.session.query(Company.sector).distinct().filter(
            Company.sector.isnot(None)
        ).order_by(Company.sector).all()
        sectors = [s[0] for s in sectors]
        
        return render_template(
            'admin/companies/index.html',
            companies=result['companies'],
            total=result['total'],
            page=result['page'],
            pages=result['pages'],
            has_next=result['has_next'],
            has_prev=result['has_prev'],
            search=search,
            sector=sector,
            is_active_filter=is_active,
            sectors=sectors
        )
        
    except Exception as e:
        logger.error(f"Error loading companies: {str(e)}")
        flash(f'Error loading companies: {str(e)}', 'error')
        return render_template('admin/companies/index.html', companies=[], total=0, page=1, pages=0)


@bp.route('/companies/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_company():
    """Create a new company"""
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'symbol': request.form.get('symbol'),
                'company_name': request.form.get('company_name'),
                'sector': request.form.get('sector'),
                'industry': request.form.get('industry'),
                'description': request.form.get('description')
            }
            
            # Create company
            company = AdminService.create_company(data)
            
            flash(f'Company {company.symbol} created successfully', 'success')
            return redirect(url_for('admin.companies'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            flash(f'Error creating company: {str(e)}', 'error')
    
    return render_template('admin/companies/create.html')


@bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(company_id):
    """Edit company information"""
    company = Company.query.get_or_404(company_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'company_name': request.form.get('company_name'),
                'sector': request.form.get('sector'),
                'industry': request.form.get('industry'),
                'description': request.form.get('description'),
                'website': request.form.get('website'),
                'ceo': request.form.get('ceo'),
                'employees': int(request.form.get('employees', 0)) if request.form.get('employees') else None,
                'headquarters': request.form.get('headquarters')
            }
            
            # Update company
            AdminService.update_company(company_id, data)
            
            flash(f'Company {company.symbol} updated successfully', 'success')
            return redirect(url_for('admin.companies'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Error updating company: {str(e)}")
            flash(f'Error updating company: {str(e)}', 'error')
    
    return render_template('admin/companies/edit.html', company=company)


@bp.route('/companies/<int:company_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_company(company_id):
    """Deactivate a company"""
    try:
        company = Company.query.get_or_404(company_id)
        company_symbol = company.symbol
        
        AdminService.deactivate_company(company_id)
        
        flash(f'Company {company_symbol} deactivated successfully', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error deactivating company: {str(e)}")
        flash(f'Error deactivating company: {str(e)}', 'error')
    
    return redirect(url_for('admin.companies'))


@bp.route('/companies/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_companies():
    """Bulk import companies from CSV"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'csv_file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(request.url)
            
            file = request.files['csv_file']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if not file.filename.endswith('.csv'):
                flash('File must be a CSV', 'error')
                return redirect(request.url)
            
            # Import companies
            result = AdminService.bulk_import_companies(file)
            
            flash(
                f'Import completed: {result["success_count"]} companies imported, '
                f'{result["error_count"]} errors',
                'success' if result['error_count'] == 0 else 'warning'
            )
            
            # Show errors if any
            if result['errors']:
                for error in result['errors'][:10]:  # Show first 10 errors
                    flash(error, 'error')
            
            return redirect(url_for('admin.companies'))
            
        except Exception as e:
            logger.error(f"Error importing companies: {str(e)}")
            flash(f'Error importing companies: {str(e)}', 'error')
    
    return render_template('admin/companies/import.html')


# Broker Management Routes

@bp.route('/brokers')
@login_required
@admin_required
def brokers():
    """List all brokers"""
    try:
        # Get filter parameters
        is_active = request.args.get('is_active', '')
        
        # Build filters
        filters = {}
        if is_active:
            filters['is_active'] = is_active == 'true'
        
        # Get brokers
        brokers_list = AdminService.get_all_brokers(filters=filters)
        
        return render_template(
            'admin/brokers/index.html',
            brokers=brokers_list,
            is_active_filter=is_active
        )
        
    except Exception as e:
        logger.error(f"Error loading brokers: {str(e)}")
        flash(f'Error loading brokers: {str(e)}', 'error')
        return render_template('admin/brokers/index.html', brokers=[])


@bp.route('/brokers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_broker():
    """Create a new broker"""
    if request.method == 'POST':
        try:
            # Get form data
            user_id = int(request.form.get('user_id'))
            data = {
                'broker_name': request.form.get('broker_name'),
                'license_number': request.form.get('license_number'),
                'phone': request.form.get('phone'),
                'email': request.form.get('email')
            }
            
            # Create broker
            broker = AdminService.create_broker(user_id, data)
            
            flash(f'Broker {broker.broker_name} created successfully', 'success')
            return redirect(url_for('admin.brokers'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Error creating broker: {str(e)}")
            flash(f'Error creating broker: {str(e)}', 'error')
    
    # Get users without broker accounts
    users_without_broker = User.query.outerjoin(Broker).filter(
        Broker.broker_id.is_(None)
    ).all()
    
    return render_template('admin/brokers/create.html', users=users_without_broker)


@bp.route('/brokers/<int:broker_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_broker(broker_id):
    """Edit broker information"""
    broker = Broker.query.get_or_404(broker_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'broker_name': request.form.get('broker_name'),
                'license_number': request.form.get('license_number'),
                'phone': request.form.get('phone'),
                'email': request.form.get('email')
            }
            
            # Update broker
            AdminService.update_broker(broker_id, data)
            
            flash(f'Broker {broker.broker_name} updated successfully', 'success')
            return redirect(url_for('admin.brokers'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Error updating broker: {str(e)}")
            flash(f'Error updating broker: {str(e)}', 'error')
    
    return render_template('admin/brokers/edit.html', broker=broker)


@bp.route('/brokers/<int:broker_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_broker(broker_id):
    """Deactivate a broker"""
    try:
        broker = Broker.query.get_or_404(broker_id)
        broker_name = broker.broker_name
        
        AdminService.deactivate_broker(broker_id)
        
        flash(f'Broker {broker_name} deactivated successfully', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error deactivating broker: {str(e)}")
        flash(f'Error deactivating broker: {str(e)}', 'error')
    
    return redirect(url_for('admin.brokers'))


# System Monitoring Routes

@bp.route('/monitoring')
@login_required
@admin_required
def monitoring():
    """System monitoring dashboard"""
    try:
        # Get API usage stats
        api_stats = AdminService.get_api_usage_stats()
        
        # Get recent job logs
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        job_logs = AdminService.get_audit_log(page=page, per_page=per_page)
        
        # Get system metrics
        metrics = AdminService.get_system_metrics()
        
        return render_template(
            'admin/monitoring/index.html',
            api_stats=api_stats,
            job_logs=job_logs['logs'],
            total_logs=job_logs['total'],
            page=job_logs['page'],
            pages=job_logs['pages'],
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Error loading monitoring dashboard: {str(e)}")
        flash(f'Error loading monitoring dashboard: {str(e)}', 'error')
        return render_template('admin/monitoring/index.html', api_stats={}, job_logs=[], metrics={})


@bp.route('/monitoring/transactions')
@login_required
@admin_required
def monitoring_transactions():
    """Real-time transaction monitoring"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('type', '')
        
        # Build filters
        filters = {}
        if start_date:
            filters['start_date'] = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            filters['end_date'] = datetime.strptime(end_date, '%Y-%m-%d')
        if transaction_type:
            filters['transaction_type'] = transaction_type
        
        # Get transactions
        result = AdminService.get_transaction_monitoring(filters=filters, page=page, per_page=per_page)
        
        return render_template(
            'admin/monitoring/transactions.html',
            transactions=result['transactions'],
            total=result['total'],
            page=result['page'],
            pages=result['pages'],
            has_next=result['has_next'],
            has_prev=result['has_prev'],
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
    except Exception as e:
        logger.error(f"Error loading transaction monitoring: {str(e)}")
        flash(f'Error loading transactions: {str(e)}', 'error')
        return render_template('admin/monitoring/transactions.html', transactions=[], total=0, page=1, pages=0)


# API Endpoints for AJAX requests

@bp.route('/api/metrics')
@login_required
@admin_required
def api_metrics():
    """Get system metrics as JSON (for auto-refresh)"""
    try:
        metrics = AdminService.get_system_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/recent-activity')
@login_required
@admin_required
def api_recent_activity():
    """Get recent activity as JSON (for auto-refresh)"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        recent_activity = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()
        
        activity_data = []
        for transaction in recent_activity:
            activity_data.append({
                'id': transaction.transaction_id,
                'type': transaction.transaction_type,
                'amount': float(transaction.amount),
                'user_email': transaction.user.email,
                'created_at': transaction.created_at.isoformat(),
                'description': transaction.description
            })
        
        return jsonify(activity_data)
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== AUDIT LOG ROUTES ====================

@bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs with filtering"""
    try:
        from app.services.audit_service import AuditService
        
        # Get filter parameters
        filters = {}
        if request.args.get('admin_id'):
            filters['admin_id'] = int(request.args.get('admin_id'))
        if request.args.get('action_type'):
            filters['action_type'] = request.args.get('action_type')
        if request.args.get('entity_type'):
            filters['entity_type'] = request.args.get('entity_type')
        if request.args.get('date_from'):
            filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
        if request.args.get('date_to'):
            filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
        
        # Get page number
        page = request.args.get('page', 1, type=int)
        
        # Get audit logs
        result = AuditService.get_audit_logs(filters=filters, page=page, per_page=50)
        
        # Get all admins for filter dropdown
        admins = User.query.filter_by(is_admin=True).all()
        
        return render_template(
            'admin/audit_logs.html',
            audit_logs=result['audit_logs'],
            total=result['total'],
            page=result['page'],
            pages=result['pages'],
            has_next=result['has_next'],
            has_prev=result['has_prev'],
            admins=admins,
            filters=filters
        )
        
    except Exception as e:
        logger.error(f"Error viewing audit logs: {str(e)}")
        flash(f'Error loading audit logs: {str(e)}', 'danger')
        return redirect(url_for('admin.index'))


@bp.route('/audit-logs/entity/<entity_type>/<int:entity_id>')
@login_required
@admin_required
def entity_audit_trail(entity_type, entity_id):
    """View audit trail for a specific entity"""
    try:
        from app.services.audit_service import AuditService
        
        # Get audit trail
        audit_logs = AuditService.get_entity_audit_trail(entity_type, entity_id)
        
        return render_template(
            'admin/entity_audit_trail.html',
            audit_logs=audit_logs,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
    except Exception as e:
        logger.error(f"Error viewing entity audit trail: {str(e)}")
        flash(f'Error loading audit trail: {str(e)}', 'danger')
        return redirect(url_for('admin.index'))
