"""
Authentication Service
Handles user registration, authentication, and session management
"""
import re
import logging
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt
from app.models.user import User
from app.models.wallet import Wallet

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register_user(email, password, full_name=None):
        """
        Register a new user with email and password
        
        Args:
            email: User's email address
            password: Plain text password
            full_name: User's full name (optional)
        
        Returns:
            tuple: (User object, error message)
        
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Registration attempt for email: {email}")
        
        # Validate email
        if not email or not AuthService.validate_email(email):
            logger.warning(f"Registration failed - invalid email format: {email}")
            raise ValueError("Invalid email address")
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed - email already registered: {email}")
            raise ValueError("Email already registered")
        
        # Validate password
        password_error = AuthService.validate_password(password)
        if password_error:
            logger.warning(f"Registration failed - password validation error for {email}")
            raise ValueError(password_error)
        
        try:
            # Create new user
            user = User(
                email=email.lower().strip(),
                full_name=full_name.strip() if full_name else None
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Get user_id before committing
            
            # Create wallet with initial balance
            wallet = Wallet(
                user_id=user.user_id,
                balance=100000.00,
                total_deposited=100000.00
            )
            db.session.add(wallet)
            
            db.session.commit()
            logger.info(f"User registered successfully: user_id={user.user_id}, email={email}")
            return user, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration failed for {email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to register user: {str(e)}")
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: Plain text password
        
        Returns:
            User object if authentication successful, None otherwise
        """
        if not email or not password:
            logger.warning("Authentication attempt with missing email or password")
            return None
        
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if user and user.check_password(password):
            # Check if account is suspended
            if user.account_status == 'suspended':
                logger.warning(f"Login attempt for suspended account: user_id={user.user_id}, email={email}")
                raise ValueError("Your account has been suspended. Please contact support.")
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Authentication successful: user_id={user.user_id}, email={email}")
            return user
        
        logger.warning(f"Authentication failed - invalid credentials for email: {email}")
        return None
    
    @staticmethod
    def create_session(user, remember=False):
        """
        Create a login session for the user
        
        Args:
            user: User object
            remember: Whether to remember the user (persistent session)
        
        Returns:
            bool: True if session created successfully
        """
        return login_user(user, remember=remember)
    
    @staticmethod
    def destroy_session():
        """
        Destroy the current user session (logout)
        
        Returns:
            bool: True if session destroyed successfully
        """
        logout_user()
        return True
    
    @staticmethod
    def get_current_user():
        """
        Get the currently logged-in user
        
        Returns:
            User object or None
        """
        return current_user if current_user.is_authenticated else None
    
    @staticmethod
    def update_profile(user_id, data):
        """
        Update user profile information
        
        Args:
            user_id: User ID
            data: Dictionary with profile fields to update
        
        Returns:
            User object
        
        Raises:
            ValueError: If validation fails
        """
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"Profile update failed - user not found: user_id={user_id}")
            raise ValueError("User not found")
        
        try:
            # Update allowed fields
            if 'full_name' in data:
                user.full_name = data['full_name'].strip() if data['full_name'] else None
            
            if 'risk_tolerance' in data:
                if data['risk_tolerance'] not in ['conservative', 'moderate', 'aggressive']:
                    raise ValueError("Invalid risk tolerance value")
                user.risk_tolerance = data['risk_tolerance']
            
            if 'investment_goals' in data:
                user.investment_goals = data['investment_goals']
            
            if 'preferred_sectors' in data:
                user.preferred_sectors = data['preferred_sectors']
            
            if 'notification_preferences' in data:
                user.notification_preferences = data['notification_preferences']
            
            db.session.commit()
            logger.info(f"Profile updated successfully: user_id={user_id}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update failed for user_id={user_id}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to update profile: {str(e)}")
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            bool: True if password changed successfully
        
        Raises:
            ValueError: If validation fails
        """
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"Password change failed - user not found: user_id={user_id}")
            raise ValueError("User not found")
        
        # Verify old password
        if not user.check_password(old_password):
            logger.warning(f"Password change failed - incorrect current password: user_id={user_id}")
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        password_error = AuthService.validate_password(new_password)
        if password_error:
            logger.warning(f"Password change failed - validation error: user_id={user_id}")
            raise ValueError(password_error)
        
        # Check if new password is different from old
        if old_password == new_password:
            logger.warning(f"Password change failed - new password same as old: user_id={user_id}")
            raise ValueError("New password must be different from current password")
        
        try:
            user.set_password(new_password)
            db.session.commit()
            logger.info(f"Password changed successfully: user_id={user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change failed for user_id={user_id}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to change password: {str(e)}")
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format
        
        Args:
            email: Email address to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not email:
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        
        Args:
            password: Password to validate
        
        Returns:
            str: Error message if invalid, None if valid
        """
        if not password:
            return "Password is required"
        
        if len(password) < 8:
            return "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return "Password must be less than 128 characters"
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return "Password must contain at least one number"
        
        return None
    
    @staticmethod
    def hash_password(password):
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            str: Hashed password
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(password_hash, password)

