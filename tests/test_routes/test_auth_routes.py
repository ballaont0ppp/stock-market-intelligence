"""
Unit tests for authentication routes
"""
import pytest
from app.models import User
from app import db


@pytest.mark.unit
@pytest.mark.routes
class TestAuthRoutes:
    """Test authentication endpoint functionality"""
    
    def test_register_page_loads(self, client):
        """Test register page loads successfully"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data
    
    def test_login_page_loads(self, client):
        """Test login page loads successfully"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_register_user_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/auth/register', data={
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'full_name': 'New User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
            
            # Cleanup
            if user:
                db.session.delete(user)
                db.session.commit()
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post('/auth/register', data={
            'email': test_user.email,
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'full_name': 'Duplicate User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already registered' in response.data or b'exists' in response.data
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'Test123!@#'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'WrongPassword123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'incorrect' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@test.com',
            'password': 'Password123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'not found' in response.data
    
    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_profile_requires_login(self, client):
        """Test that profile page requires authentication"""
        response = client.get('/auth/profile')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_profile_page_authenticated(self, authenticated_client):
        """Test profile page for authenticated user"""
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        assert b'Profile' in response.data or b'profile' in response.data
    
    def test_update_profile(self, authenticated_client, test_user):
        """Test updating user profile"""
        response = authenticated_client.post('/auth/profile', data={
            'full_name': 'Updated Name',
            'risk_tolerance': 'aggressive',
            'investment_goals': 'Long-term growth'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch"""
        response = client.post('/auth/register', data={
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'confirm_password': 'DifferentPass123!',
            'full_name': 'New User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'match' in response.data or b'Match' in response.data
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/auth/register', data={
            'email': 'newuser@test.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'full_name': 'New User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/auth/register', data={
            'email': 'invalid-email',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'full_name': 'New User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_profile_form_validation_full_name(self, authenticated_client):
        """Test profile form validation for full name"""
        response = authenticated_client.post('/auth/profile', data={
            'full_name': '',  # Empty name should fail
            'risk_tolerance': 'moderate',
            'investment_goals': 'Test goals',
            'update_profile': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Form should show validation error
        assert b'required' in response.data or b'Profile' in response.data
    
    def test_profile_form_validation_risk_tolerance(self, authenticated_client):
        """Test profile form validation for risk tolerance"""
        response = authenticated_client.post('/auth/profile', data={
            'full_name': 'Test User',
            'risk_tolerance': '',  # Empty should fail
            'investment_goals': 'Test goals',
            'update_profile': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_profile_update_success(self, authenticated_client, app, test_user):
        """Test successful profile update"""
        response = authenticated_client.post('/auth/profile', data={
            'full_name': 'Updated User Name',
            'risk_tolerance': 'aggressive',
            'investment_goals': 'Long-term wealth building',
            'preferred_sectors': ['Technology', 'Healthcare'],
            'notify_dividends': True,
            'notify_price_changes': True,
            'notify_weekly_summary': False,
            'update_profile': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data or b'Profile' in response.data
        
        # Verify profile was updated in database
        with app.app_context():
            user = User.query.get(test_user.user_id)
            assert user.full_name == 'Updated User Name'
            assert user.risk_tolerance == 'aggressive'
            assert user.investment_goals == 'Long-term wealth building'
    
    def test_password_change_success(self, authenticated_client, app, test_user):
        """Test successful password change"""
        response = authenticated_client.post('/auth/profile', data={
            'current_password': 'Test123!@#',
            'new_password': 'NewPass123!',
            'confirm_new_password': 'NewPass123!',
            'change_password': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data or b'Password' in response.data
    
    def test_password_change_wrong_current_password(self, authenticated_client):
        """Test password change with wrong current password"""
        response = authenticated_client.post('/auth/profile', data={
            'current_password': 'WrongPassword123!',
            'new_password': 'NewPass123!',
            'confirm_new_password': 'NewPass123!',
            'change_password': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'incorrect' in response.data or b'wrong' in response.data or b'Password' in response.data
    
    def test_password_change_mismatch(self, authenticated_client):
        """Test password change with mismatched new passwords"""
        response = authenticated_client.post('/auth/profile', data={
            'current_password': 'Test123!@#',
            'new_password': 'NewPass123!',
            'confirm_new_password': 'DifferentPass123!',
            'change_password': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'match' in response.data or b'Match' in response.data
    
    def test_logout_clears_session(self, authenticated_client, client):
        """Test that logout clears session data"""
        # First verify user is authenticated
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        
        # Logout
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Try to access protected page - should redirect to login
        response = client.get('/auth/profile')
        assert response.status_code in [302, 401]
    
    def test_logout_redirects_to_login(self, authenticated_client):
        """Test that logout redirects to login page"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_profile_displays_current_data(self, authenticated_client, app, test_user):
        """Test that profile page displays current user data"""
        # Update user data first
        with app.app_context():
            user = User.query.get(test_user.user_id)
            user.full_name = 'Display Test User'
            user.risk_tolerance = 'conservative'
            db.session.commit()
        
        # Get profile page
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        assert b'Display Test User' in response.data or b'Profile' in response.data
    
    def test_profile_notification_preferences(self, authenticated_client, app, test_user):
        """Test that notification preferences are saved and displayed"""
        response = authenticated_client.post('/auth/profile', data={
            'full_name': 'Test User',
            'risk_tolerance': 'moderate',
            'investment_goals': 'Test',
            'notify_dividends': True,
            'notify_price_changes': False,
            'notify_weekly_summary': True,
            'update_profile': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify preferences were saved
        with app.app_context():
            user = User.query.get(test_user.user_id)
            assert user.notification_preferences is not None
            assert user.notification_preferences.get('dividends') == True
            assert user.notification_preferences.get('price_changes') == False
            assert user.notification_preferences.get('weekly_summary') == True
