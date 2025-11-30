"""
Dividend Manager Service
Handles dividend creation, updates, and distribution
"""
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models import Dividend, DividendPayment, Holdings, Transaction, Wallet, Notification
from app.utils.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)


class DividendManager:
    """Service for managing dividends and dividend payments"""
    
    def create_dividend(self, company_id: int, data: Dict) -> Dividend:
        """
        Create a new dividend announcement
        
        Args:
            company_id: ID of the company
            data: Dictionary containing dividend details
            
        Returns:
            Created Dividend object
        """
        try:
            # Validate required fields
            required_fields = ['dividend_per_share', 'payment_date', 'record_date', 'ex_dividend_date']
            for field in required_fields:
                if field not in data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create dividend
            dividend = Dividend(
                company_id=company_id,
                dividend_per_share=Decimal(str(data['dividend_per_share'])),
                payment_date=data['payment_date'],
                record_date=data['record_date'],
                ex_dividend_date=data['ex_dividend_date'],
                announcement_date=data.get('announcement_date', datetime.now().date()),
                dividend_type=data.get('dividend_type', 'REGULAR')
            )
            
            db.session.add(dividend)
            db.session.commit()
            
            logger.info(f"Created dividend {dividend.dividend_id} for company {company_id}")
            return dividend
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating dividend: {str(e)}")
            raise BusinessLogicError(f"Failed to create dividend: {str(e)}")
    
    def update_dividend(self, dividend_id: int, data: Dict) -> Dividend:
        """Update an existing dividend"""
        try:
            dividend = Dividend.query.get(dividend_id)
            if not dividend:
                raise ValidationError(f"Dividend {dividend_id} not found")
            
            # Update fields
            for key, value in data.items():
                if hasattr(dividend, key):
                    setattr(dividend, key, value)
            
            db.session.commit()
            logger.info(f"Updated dividend {dividend_id}")
            return dividend
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error updating dividend: {str(e)}")
            raise BusinessLogicError(f"Failed to update dividend: {str(e)}")
    
    def delete_dividend(self, dividend_id: int) -> bool:
        """Delete a dividend (only if payment date is in future)"""
        try:
            dividend = Dividend.query.get(dividend_id)
            if not dividend:
                raise ValidationError(f"Dividend {dividend_id} not found")
            
            if dividend.payment_date <= datetime.now().date():
                raise BusinessLogicError("Cannot delete dividend with past payment date")
            
            db.session.delete(dividend)
            db.session.commit()
            logger.info(f"Deleted dividend {dividend_id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error deleting dividend: {str(e)}")
            raise BusinessLogicError(f"Failed to delete dividend: {str(e)}")
    
    def get_upcoming_dividends(self) -> List[Dividend]:
        """Get all upcoming dividends"""
        try:
            return Dividend.query.filter(
                Dividend.payment_date >= datetime.now().date()
            ).order_by(Dividend.payment_date).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching dividends: {str(e)}")
            return []
    
    def calculate_user_dividend(self, user_id: int, dividend: Dividend) -> Decimal:
        """Calculate dividend amount for a user"""
        try:
            holding = Holdings.query.filter_by(
                user_id=user_id,
                company_id=dividend.company_id
            ).first()
            
            if not holding:
                return Decimal('0.00')
            
            amount = dividend.dividend_per_share * holding.quantity
            return amount
            
        except Exception as e:
            logger.error(f"Error calculating dividend for user {user_id}: {str(e)}")
            return Decimal('0.00')
    
    def distribute_dividend(self, dividend_id: int) -> Dict:
        """
        Distribute dividend payments to all eligible users
        
        Returns:
            Dictionary with distribution summary
        """
        try:
            dividend = Dividend.query.get(dividend_id)
            if not dividend:
                raise ValidationError(f"Dividend {dividend_id} not found")
            
            # Get all users with holdings for this company
            holdings = Holdings.query.filter_by(company_id=dividend.company_id).all()
            
            total_paid = Decimal('0.00')
            users_paid = 0
            
            for holding in holdings:
                try:
                    # Calculate dividend amount
                    amount = dividend.dividend_per_share * holding.quantity
                    
                    # Credit user's wallet
                    wallet = Wallet.query.filter_by(user_id=holding.user_id).first()
                    if not wallet:
                        logger.warning(f"No wallet found for user {holding.user_id}")
                        continue
                    
                    balance_before = wallet.balance
                    wallet.balance += amount
                    
                    # Create transaction record
                    transaction = Transaction(
                        user_id=holding.user_id,
                        transaction_type='DIVIDEND',
                        company_id=dividend.company_id,
                        amount=amount,
                        balance_before=balance_before,
                        balance_after=wallet.balance,
                        description=f"Dividend payment: {holding.quantity} shares @ ${dividend.dividend_per_share}"
                    )
                    db.session.add(transaction)
                    
                    # Create dividend payment record
                    payment = DividendPayment(
                        dividend_id=dividend_id,
                        user_id=holding.user_id,
                        holding_id=holding.holding_id,
                        shares_owned=holding.quantity,
                        amount_paid=amount,
                        transaction_id=transaction.transaction_id
                    )
                    db.session.add(payment)
                    
                    # Create notification
                    notification = Notification(
                        user_id=holding.user_id,
                        notification_type='DIVIDEND',
                        title='Dividend Payment Received',
                        message=f"You received ${amount:.2f} dividend payment for {holding.quantity} shares"
                    )
                    db.session.add(notification)
                    
                    total_paid += amount
                    users_paid += 1
                    
                except Exception as e:
                    logger.error(f"Error processing dividend for user {holding.user_id}: {str(e)}")
                    continue
            
            db.session.commit()
            
            logger.info(f"Distributed dividend {dividend_id}: {users_paid} users, ${total_paid:.2f} total")
            
            return {
                'dividend_id': dividend_id,
                'users_paid': users_paid,
                'total_amount': float(total_paid),
                'success': True
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error distributing dividend: {str(e)}")
            raise BusinessLogicError(f"Failed to distribute dividend: {str(e)}")
