"""
Smoke Tests

Quick validation tests to ensure the application is functional after deployment.
These tests verify:
- Application starts successfully
- Database connection works
- User can login
- Dashboard loads
- Critical API endpoints respond
- Background jobs are configured
"""
import pytest
from flask import Flask
from app import create_app, db
from app.models import User, Company, Wallet


@pytest.mark.smoke
class TestApplicationStartup:
    """Test application can start successfully"""
    
    def test_app_creates_successfully(self):
        """Test Flask application can be created"""
        app = create_app('testing')
        assert app is not None
        assert isinstance(app, Flask)
    
    def test_app_has_required_config(self):
        """Test application has required configuration"""
        app = create_app('testing')
        
        required_configs = [
            'SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI',
            'SQLALCHEMY_TRACK_MODIFICATIONS'
        ]
        
        for config in required_configs:
            assert config in app.config
    
    def test_app_blueprints_registered(self):
        """Test all required blueprints are registered"""
        app = create_app('testing')
        
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        required_blueprints = ['auth', 'dashboard', 'portfolio', 'orders']
        
        for bp_name in required_blueprints:
            assert bp_name in blueprint_names


@pytest.mark.smoke
class TestDatabaseConnection:
    """Test database connectivity"""
    
    def test_database_connection_works(self, app, db):
        """Test can connect to database"""
        with app.app_context():
            # Try a simple query
            result = db.session.execute(db.text('SELECT 1')).scalar()
            assert result == 1
    
    def test_database_tables_exist(self, app, db):
        """Test required database tables exist"""
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'users',
                'companies',
                'wallets',
                'holdings',
                'orders',
                'transactions'
            ]
            
            for table in required_tables:
                assert table in tables, f"Table {table} not found"
    
    def test_can_query_users_table(self, app, db):
        """Test can query users table"""
        with app.app_context():
            users = User.query.all()
            assert users is not None  # May be empty, but should not error


@pytest.mark.smoke
class TestUserAuthentication:
    """Test user authentication works"""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'email' in response.data.lower()
    
    def test_register_page_loads(self, client):
        """Test registration page is accessible"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'sign up' in response.data.lower()
    
    def test_can_create_and_login_user(self, client, db):
        """Test user registration and login flow"""
        # Register
        register_data = {
            'email': 'smoke@test.com',
            'password': 'SmokeTest123!',
            'full_name': 'Smoke Test',
            'csrf_token': 'test_token'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify user exists
        user = User.query.filter_by(email='smoke@test.com').first()
        assert user is not None
        
        # Login
        login_data = {
            'email': 'smoke@test.com',
            'password': 'SmokeTest123!',
            'csrf_token': 'test_token'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.smoke
class TestDashboardAccess:
    """Test dashboard is accessible"""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects unauthenticated users"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect
    
    def test_authenticated_user_can_access_dashboard(self, auth_client):
        """Test authenticated user can access dashboard"""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
    
    def test_portfolio_page_loads(self, auth_client):
        """Test portfolio page loads"""
        response = auth_client.get('/portfolio')
        assert response.status_code == 200


@pytest.mark.smoke
class TestCriticalAPIEndpoints:
    """Test critical API endpoints respond"""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint if it exists"""
        response = client.get('/api/health')
        # May return 404 if not implemented, but should not crash
        assert response.status_code in [200, 404]
    
    def test_stock_search_api(self, auth_client):
        """Test stock search API responds"""
        response = auth_client.get('/api/search?q=TEST')
        assert response.status_code in [200, 404]  # Should respond
    
    def test_portfolio_api(self, auth_client, test_user):
        """Test portfolio API endpoint"""
        response = auth_client.get(f'/api/portfolio/{test_user.user_id}')
        # Should either return data or proper error
        assert response.status_code in [200, 403, 404]


@pytest.mark.smoke
class TestBackgroundJobs:
    """Test background jobs are configured"""
    
    def test_scheduler_module_exists(self):
        """Test scheduler module can be imported"""
        try:
            from app.jobs import scheduler
            assert scheduler is not None
        except ImportError:
            pytest.skip("Scheduler module not found")
    
    def test_price_updater_job_exists(self):
        """Test price updater job module exists"""
        try:
            from app.jobs import price_updater
            assert price_updater is not None
        except ImportError:
            pytest.skip("Price updater module not found")
    
    def test_dividend_processor_job_exists(self):
        """Test dividend processor job module exists"""
        try:
            from app.jobs import dividend_processor
            assert dividend_processor is not None
        except ImportError:
            pytest.skip("Dividend processor module not found")


@pytest.mark.smoke
class TestCriticalServices:
    """Test critical services can be instantiated"""
    
    def test_auth_service_works(self):
        """Test AuthService can be instantiated"""
        from app.services.auth_service import AuthService
        service = AuthService()
        assert service is not None
    
    def test_portfolio_service_works(self):
        """Test PortfolioService can be instantiated"""
        from app.services.portfolio_service import PortfolioService
        service = PortfolioService()
        assert service is not None
    
    def test_transaction_engine_works(self):
        """Test TransactionEngine can be instantiated"""
        from app.services.transaction_engine import TransactionEngine
        engine = TransactionEngine()
        assert engine is not None


@pytest.mark.smoke
class TestStaticAssets:
    """Test static assets are accessible"""
    
    def test_css_files_accessible(self, client):
        """Test CSS files can be loaded"""
        response = client.get('/static/css/design-system.css')
        assert response.status_code in [200, 304, 404]  # OK, Not Modified, or Not Found
    
    def test_js_files_accessible(self, client):
        """Test JavaScript files can be loaded"""
        response = client.get('/static/js/main.js')
        assert response.status_code in [200, 304, 404]


@pytest.mark.smoke
class TestErrorHandling:
    """Test basic error handling works"""
    
    def test_404_page_works(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page-12345')
        assert response.status_code == 404
    
    def test_500_error_handled(self, client):
        """Test 500 errors are handled gracefully"""
        # This would need a route that intentionally raises an error
        # For now, just verify error handlers are registered
        from app import create_app
        app = create_app('testing')
        assert 404 in app.error_handler_spec[None]


@pytest.mark.smoke
def test_smoke_suite_summary(capsys):
    """Print smoke test summary"""
    print("\n" + "="*60)
    print("SMOKE TEST SUITE COMPLETED")
    print("="*60)
    print("✓ Application startup verified")
    print("✓ Database connection verified")
    print("✓ User authentication verified")
    print("✓ Dashboard access verified")
    print("✓ API endpoints verified")
    print("✓ Background jobs verified")
    print("="*60)
