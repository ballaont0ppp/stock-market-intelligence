"""
Admin Service
Handles administrative operations for user, company, broker, and system management
"""
from datetime import datetime, timedelta
from sqlalchemy import func, desc, or_
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user
from app import db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.holding import Holdings
from app.models.order import Order
from app.models.company import Company
from app.models.broker import Broker
from app.models.notification import Notification
from app.models.dividend import Dividend
from app.models.job_log import JobLog
from app.utils.exceptions import ValidationError, BusinessLogicError
from app.services.audit_service import AuditService
import logging
import yfinance as yf
import csv
from io import StringIO

logger = logging.getLogger(__name__)


class AdminService:
    """Service for administrative operations"""
    
    # ==================== USER MANAGEMENT ====================
    
    @staticmethod
    def get_all_users(filters=None, page=1, per_page=20):
        """
        Get all users with optional filtering and pagination
        
        Args:
            filters: Dictionary with filter criteria
                - search: Search by email or name
                - status: Filter by account status (active/suspended)
                - is_admin: Filter by admin status
                - created_after: Filter by creation date
                - created_before: Filter by creation date
            page: Page number (default 1)
            per_page: Items per page (default 20)
        
        Returns:
            dict: {
                'users': List of User objects,
                'total': Total count,
                'page': Current page,
                'pages': Total pages
            }
        """
        try:
            query = User.query
            
            # Apply filters
            if filters:
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            User.email.like(search_term),
                            User.full_name.like(search_term)
                        )
                    )
                
                if filters.get('status'):
                    query = query.filter(User.account_status == filters['status'])
                
                if filters.get('is_admin') is not None:
                    query = query.filter(User.is_admin == filters['is_admin'])
                
                if filters.get('created_after'):
                    query = query.filter(User.created_at >= filters['created_after'])
                
                if filters.get('created_before'):
                    query = query.filter(User.created_at <= filters['created_before'])
            
            # Order by creation date (newest first)
            query = query.order_by(desc(User.created_at))
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'users': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise Exception(f"Failed to retrieve users: {str(e)}")
    
    @staticmethod
    def get_user_details(user_id):
        """
        Get detailed information about a user
        
        Args:
            user_id: User ID
        
        Returns:
            dict: User details including profile, wallet, holdings, and activity
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get wallet info
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            
            # Get holdings with current values
            holdings = Holdings.query.filter_by(user_id=user_id).all()
            holdings_data = []
            total_portfolio_value = 0
            
            for holding in holdings:
                from app.services.stock_repository import StockRepository
                current_price = StockRepository.get_current_price(holding.company.symbol)
                current_value = float(current_price) * holding.quantity
                total_portfolio_value += current_value
                
                holdings_data.append({
                    'symbol': holding.company.symbol,
                    'company_name': holding.company.company_name,
                    'quantity': holding.quantity,
                    'average_price': float(holding.average_purchase_price),
                    'current_price': float(current_price),
                    'current_value': current_value,
                    'gain_loss': current_value - float(holding.total_invested)
                })
            
            # Get order statistics
            total_orders = Order.query.filter_by(user_id=user_id).count()
            completed_orders = Order.query.filter_by(
                user_id=user_id,
                order_status='COMPLETED'
            ).count()
            
            # Get recent transactions (last 50)
            recent_transactions = Transaction.query.filter_by(
                user_id=user_id
            ).order_by(desc(Transaction.created_at)).limit(50).all()
            
            # Calculate performance metrics
            buy_orders = Order.query.filter_by(
                user_id=user_id,
                order_type='BUY',
                order_status='COMPLETED'
            ).all()
            
            sell_orders = Order.query.filter_by(
                user_id=user_id,
                order_type='SELL',
                order_status='COMPLETED'
            ).all()
            
            total_invested = sum(float(order.total_amount) for order in buy_orders)
            total_proceeds = sum(float(order.total_amount) for order in sell_orders)
            realized_gains = sum(float(order.realized_gain_loss or 0) for order in sell_orders)
            
            return {
                'user': user,
                'wallet': {
                    'balance': float(wallet.balance) if wallet else 0,
                    'total_deposited': float(wallet.total_deposited) if wallet else 0,
                    'total_withdrawn': float(wallet.total_withdrawn) if wallet else 0
                },
                'portfolio': {
                    'holdings': holdings_data,
                    'total_value': total_portfolio_value,
                    'total_invested': total_invested,
                    'unrealized_gains': total_portfolio_value - (total_invested - total_proceeds)
                },
                'activity': {
                    'total_orders': total_orders,
                    'completed_orders': completed_orders,
                    'total_transactions': len(recent_transactions),
                    'recent_transactions': recent_transactions
                },
                'performance': {
                    'total_invested': total_invested,
                    'total_proceeds': total_proceeds,
                    'realized_gains': realized_gains,
                    'net_worth': float(wallet.balance) + total_portfolio_value if wallet else total_portfolio_value
                }
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting user details for user {user_id}: {str(e)}")
            raise Exception(f"Failed to retrieve user details: {str(e)}")
    
    @staticmethod
    def update_user(user_id, data):
        """
        Update user information
        
        Args:
            user_id: User ID
            data: Dictionary with fields to update
        
        Returns:
            User: Updated user object
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Track changes for audit log
            changes = {}
            
            # Update allowed fields
            if 'full_name' in data:
                old_value = user.full_name
                new_value = data['full_name'].strip() if data['full_name'] else None
                if old_value != new_value:
                    changes['full_name'] = {'old': old_value, 'new': new_value}
                    user.full_name = new_value
            
            if 'email' in data:
                # Check if email is already taken by another user
                existing = User.query.filter(
                    User.email == data['email'],
                    User.user_id != user_id
                ).first()
                if existing:
                    raise ValueError("Email already in use")
                old_value = user.email
                new_value = data['email'].lower().strip()
                if old_value != new_value:
                    changes['email'] = {'old': old_value, 'new': new_value}
                    user.email = new_value
            
            if 'risk_tolerance' in data:
                if data['risk_tolerance'] not in ['conservative', 'moderate', 'aggressive']:
                    raise ValueError("Invalid risk tolerance value")
                old_value = user.risk_tolerance
                new_value = data['risk_tolerance']
                if old_value != new_value:
                    changes['risk_tolerance'] = {'old': old_value, 'new': new_value}
                    user.risk_tolerance = new_value
            
            if 'investment_goals' in data:
                old_value = user.investment_goals
                new_value = data['investment_goals']
                if old_value != new_value:
                    changes['investment_goals'] = {'old': old_value, 'new': new_value}
                    user.investment_goals = new_value
            
            if 'preferred_sectors' in data:
                changes['preferred_sectors'] = {'new': data['preferred_sectors']}
                user.preferred_sectors = data['preferred_sectors']
            
            if 'notification_preferences' in data:
                changes['notification_preferences'] = {'new': data['notification_preferences']}
                user.notification_preferences = data['notification_preferences']
            
            if 'is_admin' in data:
                old_value = user.is_admin
                new_value = bool(data['is_admin'])
                if old_value != new_value:
                    changes['is_admin'] = {'old': old_value, 'new': new_value}
                    user.is_admin = new_value
            
            db.session.commit()
            
            # Log audit trail
            admin_id = current_user.user_id if current_user.is_authenticated else None
            AuditService.log_action(
                admin_id=admin_id,
                action_type='UPDATE',
                entity_type='USER',
                entity_id=user_id,
                changes=changes,
                description=f"Updated user {user.email}"
            )
            
            logger.info(f"User {user_id} updated successfully by admin {admin_id}")
            return user
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise Exception(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def suspend_user(user_id, reason):
        """
        Suspend a user account
        
        Args:
            user_id: User ID
            reason: Reason for suspension
        
        Returns:
            bool: True if successful
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            if user.account_status == 'suspended':
                raise ValueError("User is already suspended")
            
            user.account_status = 'suspended'
            
            # Create notification for user
            notification = Notification(
                user_id=user_id,
                notification_type='SYSTEM',
                title='Account Suspended',
                message=f'Your account has been suspended. Reason: {reason}',
                is_read=False
            )
            db.session.add(notification)
            
            db.session.commit()
            
            # Log audit trail
            admin_id = current_user.user_id if current_user.is_authenticated else None
            AuditService.log_action(
                admin_id=admin_id,
                action_type='SUSPEND',
                entity_type='USER',
                entity_id=user_id,
                changes={'status': {'old': 'active', 'new': 'suspended'}},
                description=f"Suspended user {user.email}. Reason: {reason}"
            )
            
            logger.info(f"User {user_id} suspended by admin {admin_id}. Reason: {reason}")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error suspending user {user_id}: {str(e)}")
            raise Exception(f"Failed to suspend user: {str(e)}")
    
    @staticmethod
    def activate_user(user_id):
        """
        Activate a suspended user account
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            if user.account_status == 'active':
                raise ValueError("User is already active")
            
            user.account_status = 'active'
            
            # Create notification for user
            notification = Notification(
                user_id=user_id,
                notification_type='SYSTEM',
                title='Account Activated',
                message='Your account has been reactivated. You can now log in and use the platform.',
                is_read=False
            )
            db.session.add(notification)
            
            db.session.commit()
            
            # Log audit trail
            admin_id = current_user.user_id if current_user.is_authenticated else None
            AuditService.log_action(
                admin_id=admin_id,
                action_type='ACTIVATE',
                entity_type='USER',
                entity_id=user_id,
                changes={'status': {'old': 'suspended', 'new': 'active'}},
                description=f"Activated user {user.email}"
            )
            
            logger.info(f"User {user_id} activated by admin {admin_id}")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error activating user {user_id}: {str(e)}")
            raise Exception(f"Failed to activate user: {str(e)}")
    
    @staticmethod
    def delete_user(user_id):
        """
        Delete a user account (with cascade handling)
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Check if user is an admin (prevent deleting last admin)
            if user.is_admin:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    raise ValueError("Cannot delete the last admin user")
            
            user_email = user.email
            
            # Delete user (cascade will handle related records)
            db.session.delete(user)
            db.session.commit()
            
            # Log audit trail
            admin_id = current_user.user_id if current_user.is_authenticated else None
            AuditService.log_action(
                admin_id=admin_id,
                action_type='DELETE',
                entity_type='USER',
                entity_id=user_id,
                description=f"Deleted user {user_email}"
            )
            
            logger.info(f"User {user_id} deleted successfully by admin {admin_id}")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise Exception(f"Failed to delete user: {str(e)}")
    
    @staticmethod
    def adjust_wallet_balance(user_id, amount, reason):
        """
        Manually adjust user's wallet balance (admin operation)
        
        Args:
            user_id: User ID
            amount: Amount to add (positive) or subtract (negative)
            reason: Reason for adjustment
        
        Returns:
            Transaction: Created transaction record
        """
        try:
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not wallet:
                raise ValueError("Wallet not found for user")
            
            # Validate amount
            if amount == 0:
                raise ValueError("Adjustment amount cannot be zero")
            
            # Check if adjustment would make balance negative
            new_balance = float(wallet.balance) + amount
            if new_balance < 0:
                raise ValueError("Adjustment would result in negative balance")
            
            # Record balance before adjustment
            balance_before = float(wallet.balance)
            
            # Apply adjustment
            wallet.balance = new_balance
            wallet.last_updated = datetime.utcnow()
            
            # Update totals
            if amount > 0:
                wallet.total_deposited = float(wallet.total_deposited) + amount
            else:
                wallet.total_withdrawn = float(wallet.total_withdrawn) + abs(amount)
            
            # Create transaction record
            transaction_type = 'DEPOSIT' if amount > 0 else 'WITHDRAWAL'
            transaction = Transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=abs(amount),
                balance_before=balance_before,
                balance_after=new_balance,
                description=f"Admin adjustment: {reason}"
            )
            db.session.add(transaction)
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                notification_type='TRANSACTION',
                title='Wallet Adjustment',
                message=f'Your wallet balance was adjusted by ${abs(amount):.2f}. Reason: {reason}',
                is_read=False
            )
            db.session.add(notification)
            
            db.session.commit()
            
            # Log audit trail
            admin_id = current_user.user_id if current_user.is_authenticated else None
            AuditService.log_action(
                admin_id=admin_id,
                action_type='ADJUST_BALANCE',
                entity_type='WALLET',
                entity_id=wallet.wallet_id,
                changes={
                    'balance': {'old': balance_before, 'new': new_balance},
                    'amount': amount,
                    'reason': reason
                },
                description=f"Adjusted wallet balance for user {user_id} by ${amount:.2f}. Reason: {reason}"
            )
            
            logger.info(f"Wallet balance adjusted for user {user_id}: {amount} ({reason}) by admin {admin_id}")
            return transaction
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adjusting wallet balance for user {user_id}: {str(e)}")
            raise Exception(f"Failed to adjust wallet balance: {str(e)}")


    # ==================== COMPANY MANAGEMENT ====================
    
    @staticmethod
    def get_all_companies(filters=None, page=1, per_page=20):
        """
        Get all companies with optional filtering and pagination
        
        Args:
            filters: Dictionary with filter criteria
                - search: Search by symbol or company name
                - sector: Filter by sector
                - is_active: Filter by active status
            page: Page number (default 1)
            per_page: Items per page (default 20)
        
        Returns:
            dict: Paginated companies data
        """
        try:
            query = Company.query
            
            # Apply filters
            if filters:
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            Company.symbol.like(search_term),
                            Company.company_name.like(search_term)
                        )
                    )
                
                if filters.get('sector'):
                    query = query.filter(Company.sector == filters['sector'])
                
                if filters.get('is_active') is not None:
                    query = query.filter(Company.is_active == filters['is_active'])
            
            # Order by symbol
            query = query.order_by(Company.symbol)
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'companies': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting companies: {str(e)}")
            raise Exception(f"Failed to retrieve companies: {str(e)}")
    
    @staticmethod
    def create_company(data):
        """
        Create a new company with yfinance data fetching
        
        Args:
            data: Dictionary with company data
                - symbol: Stock symbol (required)
                - company_name: Company name (optional, fetched from yfinance if not provided)
                - sector: Sector (optional)
                - industry: Industry (optional)
                - description: Description (optional)
        
        Returns:
            Company: Created company object
        """
        try:
            # Validate required fields
            if not data.get('symbol'):
                raise ValueError("Stock symbol is required")
            
            symbol = data['symbol'].upper().strip()
            
            # Check if company already exists
            existing = Company.query.filter_by(symbol=symbol).first()
            if existing:
                raise ValueError(f"Company with symbol {symbol} already exists")
            
            # Try to fetch data from yfinance
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Use yfinance data if available, otherwise use provided data
                company = Company(
                    symbol=symbol,
                    company_name=data.get('company_name') or info.get('longName') or info.get('shortName') or symbol,
                    sector=data.get('sector') or info.get('sector'),
                    industry=data.get('industry') or info.get('industry'),
                    market_cap=info.get('marketCap'),
                    description=data.get('description') or info.get('longBusinessSummary'),
                    website=info.get('website'),
                    ceo=info.get('companyOfficers', [{}])[0].get('name') if info.get('companyOfficers') else None,
                    employees=info.get('fullTimeEmployees'),
                    headquarters=f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(', '),
                    is_active=True
                )
                
            except Exception as yf_error:
                logger.warning(f"Could not fetch yfinance data for {symbol}: {str(yf_error)}")
                # Create company with provided data only
                company = Company(
                    symbol=symbol,
                    company_name=data.get('company_name') or symbol,
                    sector=data.get('sector'),
                    industry=data.get('industry'),
                    description=data.get('description'),
                    is_active=True
                )
            
            db.session.add(company)
            db.session.commit()
            
            logger.info(f"Company {symbol} created successfully")
            return company
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating company: {str(e)}")
            raise Exception(f"Failed to create company: {str(e)}")
    
    @staticmethod
    def update_company(company_id, data):
        """
        Update company information
        
        Args:
            company_id: Company ID
            data: Dictionary with fields to update
        
        Returns:
            Company: Updated company object
        """
        try:
            company = Company.query.get(company_id)
            if not company:
                raise ValueError("Company not found")
            
            # Update allowed fields
            if 'company_name' in data:
                company.company_name = data['company_name']
            
            if 'sector' in data:
                company.sector = data['sector']
            
            if 'industry' in data:
                company.industry = data['industry']
            
            if 'description' in data:
                company.description = data['description']
            
            if 'website' in data:
                company.website = data['website']
            
            if 'ceo' in data:
                company.ceo = data['ceo']
            
            if 'employees' in data:
                company.employees = data['employees']
            
            if 'headquarters' in data:
                company.headquarters = data['headquarters']
            
            company.last_updated = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Company {company_id} updated successfully")
            return company
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating company {company_id}: {str(e)}")
            raise Exception(f"Failed to update company: {str(e)}")
    
    @staticmethod
    def deactivate_company(company_id):
        """
        Deactivate a company (soft delete)
        
        Args:
            company_id: Company ID
        
        Returns:
            bool: True if successful
        """
        try:
            company = Company.query.get(company_id)
            if not company:
                raise ValueError("Company not found")
            
            if not company.is_active:
                raise ValueError("Company is already deactivated")
            
            # Check if company has active holdings
            active_holdings = Holdings.query.filter_by(company_id=company_id).count()
            if active_holdings > 0:
                raise ValueError(f"Cannot deactivate company with {active_holdings} active holdings")
            
            company.is_active = False
            company.last_updated = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Company {company_id} deactivated")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deactivating company {company_id}: {str(e)}")
            raise Exception(f"Failed to deactivate company: {str(e)}")
    
    @staticmethod
    def bulk_import_companies(csv_content):
        """
        Bulk import companies from CSV file
        
        Args:
            csv_content: CSV file content (string or file object)
        
        Returns:
            dict: Import results with success and error counts
        """
        try:
            # Parse CSV
            if hasattr(csv_content, 'read'):
                csv_content = csv_content.read().decode('utf-8')
            
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row in csv_reader:
                try:
                    # Expected columns: symbol, company_name, sector, industry
                    symbol = row.get('symbol', '').strip().upper()
                    if not symbol:
                        continue
                    
                    # Check if already exists
                    if Company.query.filter_by(symbol=symbol).first():
                        error_count += 1
                        errors.append(f"{symbol}: Already exists")
                        continue
                    
                    # Create company
                    AdminService.create_company({
                        'symbol': symbol,
                        'company_name': row.get('company_name', '').strip(),
                        'sector': row.get('sector', '').strip(),
                        'industry': row.get('industry', '').strip()
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"{symbol}: {str(e)}")
            
            logger.info(f"Bulk import completed: {success_count} success, {error_count} errors")
            
            return {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error in bulk import: {str(e)}")
            raise Exception(f"Failed to import companies: {str(e)}")
    
    # ==================== BROKER MANAGEMENT ====================
    
    @staticmethod
    def get_all_brokers(filters=None):
        """
        Get all brokers with optional filtering
        
        Args:
            filters: Dictionary with filter criteria
                - is_active: Filter by active status
        
        Returns:
            list: List of Broker objects
        """
        try:
            query = Broker.query
            
            # Apply filters
            if filters:
                if filters.get('is_active') is not None:
                    query = query.filter(Broker.is_active == filters['is_active'])
            
            # Order by broker name
            query = query.order_by(Broker.broker_name)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting brokers: {str(e)}")
            raise Exception(f"Failed to retrieve brokers: {str(e)}")
    
    @staticmethod
    def create_broker(user_id, data):
        """
        Create a new broker linked to a user
        
        Args:
            user_id: User ID to link broker to
            data: Dictionary with broker data
                - broker_name: Broker name (required)
                - license_number: License number (optional)
                - phone: Phone number (optional)
                - email: Email (optional)
        
        Returns:
            Broker: Created broker object
        """
        try:
            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Check if user already has a broker
            existing = Broker.query.filter_by(user_id=user_id).first()
            if existing:
                raise ValueError("User already has a broker account")
            
            # Validate required fields
            if not data.get('broker_name'):
                raise ValueError("Broker name is required")
            
            # Make user an admin if not already
            if not user.is_admin:
                user.is_admin = True
            
            # Create broker
            broker = Broker(
                user_id=user_id,
                broker_name=data['broker_name'],
                license_number=data.get('license_number'),
                phone=data.get('phone'),
                email=data.get('email') or user.email,
                is_active=True
            )
            
            db.session.add(broker)
            db.session.commit()
            
            logger.info(f"Broker created for user {user_id}")
            return broker
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating broker: {str(e)}")
            raise Exception(f"Failed to create broker: {str(e)}")
    
    @staticmethod
    def update_broker(broker_id, data):
        """
        Update broker information
        
        Args:
            broker_id: Broker ID
            data: Dictionary with fields to update
        
        Returns:
            Broker: Updated broker object
        """
        try:
            broker = Broker.query.get(broker_id)
            if not broker:
                raise ValueError("Broker not found")
            
            # Update allowed fields
            if 'broker_name' in data:
                broker.broker_name = data['broker_name']
            
            if 'license_number' in data:
                broker.license_number = data['license_number']
            
            if 'phone' in data:
                broker.phone = data['phone']
            
            if 'email' in data:
                broker.email = data['email']
            
            db.session.commit()
            logger.info(f"Broker {broker_id} updated successfully")
            return broker
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating broker {broker_id}: {str(e)}")
            raise Exception(f"Failed to update broker: {str(e)}")
    
    @staticmethod
    def deactivate_broker(broker_id):
        """
        Deactivate a broker
        
        Args:
            broker_id: Broker ID
        
        Returns:
            bool: True if successful
        """
        try:
            broker = Broker.query.get(broker_id)
            if not broker:
                raise ValueError("Broker not found")
            
            if not broker.is_active:
                raise ValueError("Broker is already deactivated")
            
            broker.is_active = False
            
            db.session.commit()
            logger.info(f"Broker {broker_id} deactivated")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deactivating broker {broker_id}: {str(e)}")
            raise Exception(f"Failed to deactivate broker: {str(e)}")
    
    @staticmethod
    def assign_user_to_broker(user_id, broker_id):
        """
        Assign a user to a broker (for tracking purposes)
        
        Args:
            user_id: User ID
            broker_id: Broker ID
        
        Returns:
            bool: True if successful
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            broker = Broker.query.get(broker_id)
            if not broker:
                raise ValueError("Broker not found")
            
            # This is a placeholder for future broker-user relationship tracking
            # For now, we just increment the assigned users count
            broker.assigned_users_count += 1
            
            db.session.commit()
            logger.info(f"User {user_id} assigned to broker {broker_id}")
            return True
            
        except ValueError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error assigning user to broker: {str(e)}")
            raise Exception(f"Failed to assign user to broker: {str(e)}")
    
    # ==================== SYSTEM MONITORING ====================
    
    @staticmethod
    def get_system_metrics():
        """
        Get system-wide metrics for dashboard overview
        
        Returns:
            dict: System metrics including users, transactions, portfolio, and health
        """
        try:
            # User metrics
            total_users = User.query.count()
            active_users = User.query.filter_by(account_status='active').count()
            
            # Users who traded in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_traders = db.session.query(Order.user_id).filter(
                Order.created_at >= thirty_days_ago,
                Order.order_status == 'COMPLETED'
            ).distinct().count()
            
            # New users today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            new_users_today = User.query.filter(User.created_at >= today_start).count()
            
            suspended_users = User.query.filter_by(account_status='suspended').count()
            
            # Transaction metrics
            transactions_today = Transaction.query.filter(
                Transaction.created_at >= today_start
            ).count()
            
            # Calculate today's volume
            today_orders = Order.query.filter(
                Order.created_at >= today_start,
                Order.order_status == 'COMPLETED'
            ).all()
            volume_today = sum(float(order.total_amount) for order in today_orders)
            
            # Total volume
            all_orders = Order.query.filter_by(order_status='COMPLETED').all()
            total_volume = sum(float(order.total_amount) for order in all_orders)
            
            # Portfolio metrics
            all_holdings = Holdings.query.all()
            total_holdings_count = len(all_holdings)
            
            # Calculate total portfolio value
            total_portfolio_value = 0
            for holding in all_holdings:
                try:
                    from app.services.stock_repository import StockRepository
                    current_price = StockRepository.get_current_price(holding.company.symbol)
                    total_portfolio_value += float(current_price) * holding.quantity
                except:
                    pass
            
            # System health (simplified)
            system_health = {
                'database': 'green',  # If we got here, DB is working
                'api': 'green',  # Assume API is working
                'ml_models': 'green',  # Assume models are working
                'overall': 'green'
            }
            
            # Top traded stocks
            top_stocks_query = db.session.query(
                Company.symbol,
                func.count(Order.order_id).label('trade_count')
            ).join(Order).filter(
                Order.order_status == 'COMPLETED'
            ).group_by(Company.symbol).order_by(
                desc('trade_count')
            ).limit(5).all()
            
            top_stocks = [
                {'symbol': symbol, 'trades': count}
                for symbol, count in top_stocks_query
            ]
            
            return {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'recent_traders': recent_traders,
                    'new_today': new_users_today,
                    'suspended': suspended_users
                },
                'transactions': {
                    'today': transactions_today,
                    'volume_today': volume_today,
                    'total_volume': total_volume
                },
                'portfolio': {
                    'total_value': total_portfolio_value,
                    'total_holdings': total_holdings_count
                },
                'system_health': system_health,
                'top_stocks': top_stocks
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            raise Exception(f"Failed to retrieve system metrics: {str(e)}")
    
    @staticmethod
    def get_transaction_monitoring(filters=None, page=1, per_page=50):
        """
        Get real-time transaction monitoring data
        
        Args:
            filters: Dictionary with filter criteria
                - start_date: Filter by start date
                - end_date: Filter by end date
                - transaction_type: Filter by type
                - user_id: Filter by user
                - company_id: Filter by company
            page: Page number
            per_page: Items per page
        
        Returns:
            dict: Paginated transactions
        """
        try:
            query = Transaction.query
            
            # Apply filters
            if filters:
                if filters.get('start_date'):
                    query = query.filter(Transaction.created_at >= filters['start_date'])
                
                if filters.get('end_date'):
                    query = query.filter(Transaction.created_at <= filters['end_date'])
                
                if filters.get('transaction_type'):
                    query = query.filter(Transaction.transaction_type == filters['transaction_type'])
                
                if filters.get('user_id'):
                    query = query.filter(Transaction.user_id == filters['user_id'])
                
                if filters.get('company_id'):
                    query = query.filter(Transaction.company_id == filters['company_id'])
            
            # Order by most recent first
            query = query.order_by(desc(Transaction.created_at))
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'transactions': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction monitoring: {str(e)}")
            raise Exception(f"Failed to retrieve transactions: {str(e)}")
    
    @staticmethod
    def get_api_usage_stats():
        """
        Get API usage statistics for yfinance and Twitter API
        
        Returns:
            dict: API usage statistics
        """
        try:
            # This is a simplified version
            # In production, you would track API calls in a separate table
            
            # Get job logs for price updates
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            price_update_jobs = JobLog.query.filter(
                JobLog.job_name.like('%price%'),
                JobLog.started_at >= today_start
            ).all()
            
            total_api_calls = sum(job.stocks_processed for job in price_update_jobs if job.stocks_processed)
            failed_calls = sum(job.stocks_failed for job in price_update_jobs if job.stocks_failed)
            
            # Calculate average response time (placeholder)
            avg_response_time = 0.5  # seconds
            
            return {
                'yfinance': {
                    'total_calls_today': total_api_calls,
                    'failed_calls': failed_calls,
                    'success_rate': ((total_api_calls - failed_calls) / total_api_calls * 100) if total_api_calls > 0 else 0,
                    'avg_response_time': avg_response_time
                },
                'twitter': {
                    'total_calls_today': 0,  # Placeholder
                    'rate_limit_remaining': 100,  # Placeholder
                    'rate_limit_reset': None  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting API usage stats: {str(e)}")
            raise Exception(f"Failed to retrieve API usage stats: {str(e)}")
    
    @staticmethod
    def get_audit_log(filters=None, page=1, per_page=50):
        """
        Get audit log of admin actions
        
        Args:
            filters: Dictionary with filter criteria
                - start_date: Filter by start date
                - end_date: Filter by end date
                - admin_id: Filter by admin user
                - action_type: Filter by action type
            page: Page number
            per_page: Items per page
        
        Returns:
            dict: Paginated audit log entries
        """
        try:
            # For now, we'll use job logs as a proxy for audit logs
            # In production, you would have a dedicated audit_logs table
            
            query = JobLog.query
            
            # Apply filters
            if filters:
                if filters.get('start_date'):
                    query = query.filter(JobLog.started_at >= filters['start_date'])
                
                if filters.get('end_date'):
                    query = query.filter(JobLog.started_at <= filters['end_date'])
                
                if filters.get('job_name'):
                    query = query.filter(JobLog.job_name.like(f"%{filters['job_name']}%"))
            
            # Order by most recent first
            query = query.order_by(desc(JobLog.started_at))
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'logs': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting audit log: {str(e)}")
            raise Exception(f"Failed to retrieve audit log: {str(e)}")
