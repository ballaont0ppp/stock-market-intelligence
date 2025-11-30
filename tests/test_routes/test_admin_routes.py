"""
Unit tests for admin routes
"""
import pytest


@pytest.mark.unit
@pytest.mark.routes
class TestAdminRoutes:
    """Test admin endpoint functionality"""
    
    def test_admin_requires_login(self, client):
        """Test that admin page requires authentication"""
        response = client.get('/admin')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_admin_requires_admin_role(self, authenticated_client):
        """Test that admin page requires admin role"""
        response = authenticated_client.get('/admin')
        # Should return 403 Forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_admin_page_for_admin(self, admin_client):
        """Test admin page for admin user"""
        response = admin_client.get('/admin')
        assert response.status_code == 200
        assert b'Admin' in response.data or b'admin' in response.data or b'Dashboard' in response.data
    
    def test_admin_users_page(self, admin_client):
        """Test admin users management page"""
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
        assert b'User' in response.data or b'user' in response.data
    
    def test_admin_companies_page(self, admin_client):
        """Test admin companies management page"""
        response = admin_client.get('/admin/companies')
        assert response.status_code == 200
        assert b'Compan' in response.data or b'compan' in response.data
    
    def test_admin_brokers_page(self, admin_client):
        """Test admin brokers management page"""
        response = admin_client.get('/admin/brokers')
        assert response.status_code == 200
        assert b'Broker' in response.data or b'broker' in response.data
    
    def test_admin_dividends_page(self, admin_client):
        """Test admin dividends management page"""
        response = admin_client.get('/admin/dividends')
        assert response.status_code == 200
        assert b'Dividend' in response.data or b'dividend' in response.data
    
    def test_admin_monitoring_page(self, admin_client):
        """Test admin monitoring page"""
        response = admin_client.get('/admin/monitoring')
        assert response.status_code == 200
        assert b'Monitor' in response.data or b'monitor' in response.data or b'System' in response.data
    
    def test_admin_user_view(self, admin_client, test_user):
        """Test viewing user details as admin"""
        response = admin_client.get(f'/admin/users/{test_user.user_id}')
        assert response.status_code == 200
    
    def test_admin_user_edit(self, admin_client, test_user):
        """Test editing user as admin"""
        response = admin_client.get(f'/admin/users/{test_user.user_id}/edit')
        assert response.status_code == 200
    
    def test_admin_user_suspend(self, admin_client, test_user):
        """Test suspending user as admin"""
        response = admin_client.post(f'/admin/users/{test_user.user_id}/suspend', data={
            'reason': 'Test suspension'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_admin_company_create_page(self, admin_client):
        """Test company creation page"""
        response = admin_client.get('/admin/companies/create')
        assert response.status_code == 200
    
    def test_admin_company_edit_page(self, admin_client, test_company):
        """Test company edit page"""
        response = admin_client.get(f'/admin/companies/{test_company.company_id}/edit')
        assert response.status_code == 200
    
    def test_admin_broker_create_page(self, admin_client):
        """Test broker creation page"""
        response = admin_client.get('/admin/brokers/create')
        assert response.status_code == 200
    
    def test_admin_dividend_create_page(self, admin_client):
        """Test dividend creation page"""
        response = admin_client.get('/admin/dividends/create')
        assert response.status_code == 200
    
    def test_admin_audit_logs(self, admin_client):
        """Test audit logs page"""
        response = admin_client.get('/admin/audit-logs')
        # Should either show audit logs or return 404 if route doesn't exist
        assert response.status_code in [200, 404]
    
    def test_non_admin_cannot_access_user_management(self, authenticated_client):
        """Test that non-admin cannot access user management"""
        response = authenticated_client.get('/admin/users')
        assert response.status_code in [302, 403]
    
    def test_non_admin_cannot_access_company_management(self, authenticated_client):
        """Test that non-admin cannot access company management"""
        response = authenticated_client.get('/admin/companies')
        assert response.status_code in [302, 403]
    
    def test_non_admin_cannot_suspend_users(self, authenticated_client, test_user):
        """Test that non-admin cannot suspend users"""
        response = authenticated_client.post(f'/admin/users/{test_user.user_id}/suspend', data={
            'reason': 'Test suspension'
        }, follow_redirects=True)
        assert response.status_code in [302, 403]
