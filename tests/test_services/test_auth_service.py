"""
Unit tests for AuthService
"""
import pytest
from app.services.auth_service import AuthService
from app.models import User, Wallet
from app import db


@pytest.mark.unit
@pytest.mark.services
class TestAuthService:
    """Test AuthService functionality"""
    
    def test_register_user_success(self, app):
        """Test successful user registration"""
        with app.app_context():
            user, error = AuthService.register_user(
                email='newuser@test.com',
                password='ValidPass123!',
                full_name='New User'
            )
            
            assert user is not None
            assert error is None
            assert user.email == 'newuser@test.com'
            assert user.full_name == 'New User'
            assert user.password_hash is not None
            
            # Check wallet was created
            wallet = Wallet.query.filter_by(user_id=user.user_id).first()
            assert wallet is not None
            assert wallet.balance == 100000.00
            
            # Cleanup
            db.session.delete(wallet)
            db.session.delete(user)
            db.session.commit()
    
    def test_register_user_duplicate_email(self, app, test_user):
        """Test registration with duplicate email"""
        with app.app_context():
            with pytest.raises(ValueError, match="Email already registered"):
                AuthService.register_user(
                    email=test_user.email,
                    password='ValidPass123!',
                    full_name='Duplicate User'
                )
    
    def test_register_user_invalid_email(self, app):
        """Test registration with invalid email"""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid email address"):
                AuthService.register_user(
                    email='invalid-email',
                    password='ValidPass123!',
                    full_name='Test User'
                )
    
    def test_register_user_weak_password(self, app):
        """Test registration with weak password"""
        with app.app_context():
            with pytest.raises(ValueError):
                AuthService.register_user(
                    email='test@example.com',
                    password='weak',
                    full_name='Test User'
                )
    
    def test_authenticate_user_success(self, app, test_user):
        """Test successful authentication"""
        with app.app_context():
            user = AuthService.authenticate_user(
                email=test_user.email,
                password='Test123!@#'
            )
            
            assert user is not None
            assert user.user_id == test_user.user_id
            assert user.last_login is not None
    
    def test_authenticate_user_wrong_password(self, app, test_user):
        """Test authentication with wrong password"""
        with app.app_context():
            user = AuthService.authenticate_user(
                email=test_user.email,
                password='WrongPassword123!'
            )
            
            assert user is None
    
    def test_authenticate_user_nonexistent(self, app):
        """Test authentication with nonexistent user"""
        with app.app_context():
            user = AuthService.authenticate_user(
                email='nonexistent@example.com',
                password='Password123!'
            )
            
            assert user is None
    
    def test_authenticate_suspended_user(self, app, test_user):
        """Test authentication with suspended account"""
        with app.app_context():
            user = User.query.get(test_user.user_id)
            user.account_status = 'suspended'
            db.session.commit()
            
            with pytest.raises(ValueError, match="suspended"):
                AuthService.authenticate_user(
                    email=test_user.email,
                    password='Test123!@#'
                )
            
            # Restore status
            user.account_status = 'active'
            db.session.commit()
    
    def test_update_profile(self, app, test_user):
        """Test updating user profile"""
        with app.app_context():
            updated_user = AuthService.update_profile(
                user_id=test_user.user_id,
                data={
                    'full_name': 'Updated Name',
                    'risk_tolerance': 'aggressive',
                    'investment_goals': 'Long-term growth',
                    'preferred_sectors': ['Technology', 'Healthcare']
                }
            )
            
            assert updated_user.full_name == 'Updated Name'
            assert updated_user.risk_tolerance == 'aggressive'
            assert updated_user.investment_goals == 'Long-term growth'
            assert updated_user.preferred_sectors == ['Technology', 'Healthcare']
    
    def test_update_profile_invalid_risk_tolerance(self, app, test_user):
        """Test updating profile with invalid risk tolerance"""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid risk tolerance"):
                AuthService.update_profile(
                    user_id=test_user.user_id,
                    data={'risk_tolerance': 'invalid'}
                )
    
    def test_change_password_success(self, app, test_user):
        """Test successful password change"""
        with app.app_context():
            result = AuthService.change_password(
                user_id=test_user.user_id,
                old_password='Test123!@#',
                new_password='NewPassword123!'
            )
            
            assert result is True
            
            # Verify new password works
            user = User.query.get(test_user.user_id)
            assert user.check_password('NewPassword123!')
            
            # Restore original password
            user.set_password('Test123!@#')
            db.session.commit()
    
    def test_change_password_wrong_old_password(self, app, test_user):
        """Test password change with wrong old password"""
        with app.app_context():
            with pytest.raises(ValueError, match="Current password is incorrect"):
                AuthService.change_password(
                    user_id=test_user.user_id,
                    old_password='WrongPassword123!',
                    new_password='NewPassword123!'
                )
    
    def test_change_password_same_as_old(self, app, test_user):
        """Test password change with same password"""
        with app.app_context():
            with pytest.raises(ValueError, match="must be different"):
                AuthService.change_password(
                    user_id=test_user.user_id,
                    old_password='Test123!@#',
                    new_password='Test123!@#'
                )
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        assert AuthService.validate_email('test@example.com') is True
        assert AuthService.validate_email('user.name@domain.co.uk') is True
        assert AuthService.validate_email('user+tag@example.com') is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        assert AuthService.validate_email('invalid') is False
        assert AuthService.validate_email('invalid@') is False
        assert AuthService.validate_email('@example.com') is False
        assert AuthService.validate_email('') is False
        assert AuthService.validate_email(None) is False
    
    def test_validate_password_valid(self):
        """Test password validation with valid passwords"""
        assert AuthService.validate_password('ValidPass123!') is None
        assert AuthService.validate_password('Abcdefgh1') is None
    
    def test_validate_password_too_short(self):
        """Test password validation with short password"""
        error = AuthService.validate_password('Short1')
        assert error is not None
        assert 'at least 8 characters' in error
    
    def test_validate_password_no_uppercase(self):
        """Test password validation without uppercase"""
        error = AuthService.validate_password('lowercase123')
        assert error is not None
        assert 'uppercase' in error
    
    def test_validate_password_no_lowercase(self):
        """Test password validation without lowercase"""
        error = AuthService.validate_password('UPPERCASE123')
        assert error is not None
        assert 'lowercase' in error
    
    def test_validate_password_no_digit(self):
        """Test password validation without digit"""
        error = AuthService.validate_password('NoDigitsHere')
        assert error is not None
        assert 'number' in error
    
    def test_hash_and_verify_password(self):
        """Test password hashing and verification"""
        password = 'TestPassword123!'
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password('WrongPassword', hashed) is False
