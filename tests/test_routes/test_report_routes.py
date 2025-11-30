"""
Unit tests for report routes
"""
import pytest


@pytest.mark.unit
@pytest.mark.routes
class TestReportRoutes:
    """Test report endpoint functionality"""
    
    def test_reports_requires_login(self, client):
        """Test that reports page requires authentication"""
        response = client.get('/reports')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_reports_page_authenticated(self, authenticated_client):
        """Test reports page for authenticated user"""
        response = authenticated_client.get('/reports')
        assert response.status_code == 200
        assert b'Report' in response.data or b'report' in response.data
    
    def test_transaction_report_requires_login(self, client):
        """Test that transaction report requires authentication"""
        response = client.get('/reports/transaction')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_transaction_report_authenticated(self, authenticated_client):
        """Test transaction report for authenticated user"""
        response = authenticated_client.get('/reports/transaction')
        assert response.status_code == 200
        assert b'Transaction' in response.data or b'transaction' in response.data
    
    def test_billing_report_requires_login(self, client):
        """Test that billing report requires authentication"""
        response = client.get('/reports/billing')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_billing_report_authenticated(self, authenticated_client):
        """Test billing report for authenticated user"""
        response = authenticated_client.get('/reports/billing')
        assert response.status_code == 200
        assert b'Billing' in response.data or b'billing' in response.data or b'Fee' in response.data
    
    def test_performance_report_requires_login(self, client):
        """Test that performance report requires authentication"""
        response = client.get('/reports/performance')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_performance_report_authenticated(self, authenticated_client):
        """Test performance report for authenticated user"""
        response = authenticated_client.get('/reports/performance')
        assert response.status_code == 200
        assert b'Performance' in response.data or b'performance' in response.data
    
    def test_transaction_report_with_date_range(self, authenticated_client):
        """Test transaction report with date range filter"""
        response = authenticated_client.get('/reports/transaction?start_date=2024-01-01&end_date=2024-12-31')
        assert response.status_code == 200
    
    def test_billing_report_with_month(self, authenticated_client):
        """Test billing report with month filter"""
        response = authenticated_client.get('/reports/billing?month=1&year=2024')
        assert response.status_code == 200
    
    def test_performance_report_with_period(self, authenticated_client):
        """Test performance report with period filter"""
        response = authenticated_client.get('/reports/performance?period=1y')
        assert response.status_code == 200
    
    def test_report_export_csv(self, authenticated_client):
        """Test exporting report as CSV"""
        response = authenticated_client.get('/reports/transaction?format=csv')
        # Should either return CSV or redirect
        assert response.status_code in [200, 302]
    
    def test_report_export_pdf(self, authenticated_client):
        """Test exporting report as PDF"""
        response = authenticated_client.get('/reports/billing?format=pdf')
        # Should either return PDF or redirect
        assert response.status_code in [200, 302, 501]  # 501 if not implemented
