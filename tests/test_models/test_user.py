"""
Unit tests for User model
"""
import pytest
from datetime import datetime
from app.models import User
from app import db


@pytest.mark.unit
@pytest.mark.models
class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, app):
        """Test creating a new user"""
        with app.app_context():
            user = User(
                email='newuser@example.com',
                full_name='New User',
                risk_tolerance='moderate'
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            
            assert user.user_id is not None
            assert user.email == 'newuser@example.com'
            assert user.full_name == 'New User'
            assert user.risk_tolerance == 'moderate'
            assert user.is_admin is False
            assert user.account_status == 'active'
            assert user.created_at is not None
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(email='test@example.com')
            password = 'SecurePassword123!'
            user.set_password(password)
            
            assert user.password_hash is not None
            assert user.password_hash != password
            assert user.check_password(password) is True
            assert user.check_password('WrongPassword') is False
    
    def test_unique_email_constraint(self, app, test_user):
        """Test that email must be unique"""
        with app.app_context():
            duplicate_user = User(
                email=test_user.email,
                full_name='Duplicate User'
            )
            duplicate_user.set_password('Password123!')
            db.session.add(duplicate_user)
            
            with pytest.raises(Exception):
                db.session.commit()
            
            db.session.rollback()
    
    def test_user_relationships(self, app, test_user, test_wallet):
        """Test user relationships with other models"""
        with app.app_context():
            user = User.query.get(test_user.user_id)
            
            # Test wallet relationship
            assert user.wallet is not None
            assert user.wallet.user_id == user.user_id
    
    def test_get_id_method(self, app, test_user):
        """Test get_id method for Flask-Login"""
        with app.app_context():
            user = User.query.get(test_user.user_id)
            user_id = user.get_id()
            
            assert isinstance(user_id, str)
            assert user_id == str(test_user.user_id)
    
    def test_user_repr(self, app, test_user):
        """Test user string representation"""
        with app.app_context():
            user = User.query.get(test_user.user_id)
            repr_str = repr(user)
            
            assert test_user.email in repr_str
            assert 'User' in repr_str
    
    def test_admin_flag(self, app, admin_user):
        """Test admin user flag"""
        with app.app_context():
            user = User.query.get(admin_user.user_id)
            
            assert user.is_admin is True
    
    def test_account_status(self, app, test_user):
        """Test account status changes"""
        with app.app_context():
            user = User.query.get(test_user.user_id)
            
            assert user.account_status == 'active'
            
            user.account_status = 'suspended'
            db.session.commit()
            
            user = User.query.get(test_user.user_id)
            assert user.account_status == 'suspended'
    
    def test_json_fields(self, app):
        """Test JSON fields (preferred_sectors, notification_preferences)"""
        with app.app_context():
            user = User(
                email='jsontest@example.com',
                preferred_sectors=['Technology', 'Healthcare'],
                notification_preferences={'email': True, 'sms': False}
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            
            user = User.query.filter_by(email='jsontest@example.com').first()
            assert user.preferred_sectors == ['Technology', 'Healthcare']
            assert user.notification_preferences == {'email': True, 'sms': False}
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
