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
