"""
Unit tests for API routes
Tests all API endpoints including stock search, autocomplete, trending, and notifications
"""
import pytest
import json
from app.models import Company, Notification
from app import db


@pytest.mark.unit
@pytest.mark.routes
class TestStockAPIRoutes:
    """Test stock-related API endpoint functionality"""
    
    def test_search_stocks_requires_login(self, client):
        """Test that stock search requires authentication"""
        response = client.get('/api/stocks/search?q=TEST')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_search_stocks_authenticated(self, authenticated_client, test_company):
        """Test stock search for authenticated user"""
        response = authenticated_client.get('/api/stocks/search?q=TEST')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'results' in data['data']
    
    def test_search_stocks_with_filters(self, authenticated_client, test_company):
        """Test stock search with sector filter"""
        response = authenticated_client.get('/api/stocks/search?q=TEST&sector=Technology')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_search_stocks_pagination(self, authenticated_client, test_company):
        """Test stock search pagination"""
        response = authenticated_client.get('/api/stocks/search?page=1&per_page=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['page'] == 1
        assert data['data']['per_page'] == 10
    
    def test_autocomplete_requires_login(self, client):
        """Test that autocomplete requires authentication"""
        response = client.get('/api/stocks/autocomplete?q=TE')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_autocomplete_authenticated(self, authenticated_client, test_company):
        """Test stock autocomplete for authenticated user"""
        response = authenticated_client.get('/api/stocks/autocomplete?q=TE')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_autocomplete_empty_query(self, authenticated_client):
        """Test autocomplete with empty query"""
        response = authenticated_client.get('/api/stocks/autocomplete?q=')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
    
    def test_autocomplete_limit(self, authenticated_client, test_company):
        """Test autocomplete with limit parameter"""
        response = authenticated_client.get('/api/stocks/autocomplete?q=TE&limit=5')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) <= 5
    
    def test_trending_stocks_requires_login(self, client):
        """Test that trending stocks requires authentication"""
        response = client.get('/api/stocks/trending')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_trending_stocks_authenticated(self, authenticated_client):
        """Test trending stocks for authenticated user"""
        response = authenticated_client.get('/api/stocks/trending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_trending_stocks_with_limit(self, authenticated_client):
        """Test trending stocks with limit parameter"""
        response = authenticated_client.get('/api/stocks/trending?limit=5')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) <= 5
    
    def test_get_stock_details_requires_login(self, client):
        """Test that stock details requires authentication"""
        response = client.get('/api/stocks/TEST')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_get_stock_details_authenticated(self, authenticated_client, test_company):
        """Test get stock details for authenticated user"""
        response = authenticated_client.get('/api/stocks/TEST')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['symbol'] == 'TEST'
        assert data['data']['company_name'] == 'Test Company Inc.'
    
    def test_get_stock_details_not_found(self, authenticated_client):
        """Test get stock details for non-existent stock"""
        response = authenticated_client.get('/api/stocks/NONEXISTENT')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_stock_price_requires_login(self, client):
        """Test that stock price requires authentication"""
        response = client.get('/api/stocks/TEST/price')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_get_stock_price_authenticated(self, authenticated_client, test_company, app):
        """Test get stock price for authenticated user"""
        # Create a price history entry for the test company
        from app.models import PriceHistory
        from datetime import date
        from decimal import Decimal
        
        with app.app_context():
            price_history = PriceHistory(
                company_id=test_company.company_id,
                date=date.today(),
                open=Decimal('150.00'),
                high=Decimal('155.00'),
                low=Decimal('148.00'),
                close=Decimal('152.00'),
                adjusted_close=Decimal('152.00'),
                volume=1000000
            )
            db.session.add(price_history)
            db.session.commit()
        
        response = authenticated_client.get('/api/stocks/TEST/price')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['symbol'] == 'TEST'
        assert 'price' in data['data']
    
    def test_get_sectors_requires_login(self, client):
        """Test that get sectors requires authentication"""
        response = client.get('/api/stocks/sectors')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_get_sectors_authenticated(self, authenticated_client, test_company):
        """Test get sectors for authenticated user"""
        response = authenticated_client.get('/api/stocks/sectors')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)


@pytest.mark.unit
@pytest.mark.routes
class TestNotificationAPIRoutes:
    """Test notification-related API endpoint functionality"""
    
    def test_get_notifications_requires_login(self, client):
        """Test that get notifications requires authentication"""
        response = client.get('/api/notifications')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_get_notifications_authenticated(self, authenticated_client, test_user, app):
        """Test get notifications for authenticated user"""
        # Create a test notification
        with app.app_context():
            notification = Notification(
                user_id=test_user.user_id,
                notification_type='SYSTEM',
                title='Test Notification',
                message='This is a test notification',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
        
        response = authenticated_client.get('/api/notifications')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'notifications' in data
        assert 'unread_count' in data
        assert isinstance(data['notifications'], list)
    
    def test_get_notifications_with_limit(self, authenticated_client, test_user, app):
        """Test get notifications with limit parameter"""
        # Create multiple test notifications
        with app.app_context():
            for i in range(5):
                notification = Notification(
                    user_id=test_user.user_id,
                    notification_type='SYSTEM',
                    title=f'Test Notification {i}',
                    message=f'This is test notification {i}',
                    is_read=False
                )
                db.session.add(notification)
            db.session.commit()
        
        response = authenticated_client.get('/api/notifications?limit=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['notifications']) <= 3
    
    def test_get_notifications_unread_only(self, authenticated_client, test_user, app):
        """Test get notifications with unread_only filter"""
        # Create read and unread notifications
        with app.app_context():
            notification1 = Notification(
                user_id=test_user.user_id,
                notification_type='SYSTEM',
                title='Unread Notification',
                message='This is unread',
                is_read=False
            )
            notification2 = Notification(
                user_id=test_user.user_id,
                notification_type='SYSTEM',
                title='Read Notification',
                message='This is read',
                is_read=True
            )
            db.session.add(notification1)
            db.session.add(notification2)
            db.session.commit()
        
        response = authenticated_client.get('/api/notifications?unread_only=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        # All returned notifications should be unread
        for notification in data['notifications']:
            assert notification['is_read'] is False
    
    def test_mark_notification_read_requires_login(self, client):
        """Test that mark notification read requires authentication"""
        response = client.post('/api/notifications/1/read')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_mark_notification_read_authenticated(self, authenticated_client, test_user, app):
        """Test mark notification as read for authenticated user"""
        # Create a test notification
        with app.app_context():
            notification = Notification(
                user_id=test_user.user_id,
                notification_type='SYSTEM',
                title='Test Notification',
                message='This is a test notification',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            notification_id = notification.notification_id
        
        response = authenticated_client.post(f'/api/notifications/{notification_id}/read')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_mark_notification_read_not_found(self, authenticated_client):
        """Test mark notification read for non-existent notification"""
        response = authenticated_client.post('/api/notifications/99999/read')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_mark_notification_read_unauthorized(self, authenticated_client, admin_user, app):
        """Test mark notification read for another user's notification"""
        # Create a notification for admin user
        with app.app_context():
            notification = Notification(
                user_id=admin_user.user_id,
                notification_type='SYSTEM',
                title='Admin Notification',
                message='This is an admin notification',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            notification_id = notification.notification_id
        
        # Try to mark it as read with regular user client
        response = authenticated_client.post(f'/api/notifications/{notification_id}/read')
        assert response.status_code == 403
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_mark_all_notifications_read_requires_login(self, client):
        """Test that mark all notifications read requires authentication"""
        response = client.post('/api/notifications/mark-all-read')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_mark_all_notifications_read_authenticated(self, authenticated_client, test_user, app):
        """Test mark all notifications as read for authenticated user"""
        # Create multiple unread notifications
        with app.app_context():
            for i in range(3):
                notification = Notification(
                    user_id=test_user.user_id,
                    notification_type='SYSTEM',
                    title=f'Test Notification {i}',
                    message=f'This is test notification {i}',
                    is_read=False
                )
                db.session.add(notification)
            db.session.commit()
        
        response = authenticated_client.post('/api/notifications/mark-all-read')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'count' in data
        assert data['count'] >= 3
    
    def test_delete_notification_requires_login(self, client):
        """Test that delete notification requires authentication"""
        response = client.delete('/api/notifications/1')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_delete_notification_authenticated(self, authenticated_client, test_user, app):
        """Test delete notification for authenticated user"""
        # Create a test notification
        with app.app_context():
            notification = Notification(
                user_id=test_user.user_id,
                notification_type='SYSTEM',
                title='Test Notification',
                message='This is a test notification',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            notification_id = notification.notification_id
        
        response = authenticated_client.delete(f'/api/notifications/{notification_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_delete_notification_not_found(self, authenticated_client):
        """Test delete notification for non-existent notification"""
        response = authenticated_client.delete('/api/notifications/99999')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_delete_notification_unauthorized(self, authenticated_client, admin_user, app):
        """Test delete notification for another user's notification"""
        # Create a notification for admin user
        with app.app_context():
            notification = Notification(
                user_id=admin_user.user_id,
                notification_type='SYSTEM',
                title='Admin Notification',
                message='This is an admin notification',
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            notification_id = notification.notification_id
        
        # Try to delete it with regular user client
        response = authenticated_client.delete(f'/api/notifications/{notification_id}')
        assert response.status_code == 403
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


@pytest.mark.unit
@pytest.mark.routes
class TestAPIErrorResponses:
    """Test API error handling and responses"""
    
    def test_api_returns_json_on_error(self, authenticated_client):
        """Test that API returns JSON format on errors"""
        response = authenticated_client.get('/api/stocks/NONEXISTENT')
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_handles_invalid_parameters(self, authenticated_client):
        """Test API handles invalid parameters gracefully"""
        response = authenticated_client.get('/api/stocks/search?page=invalid')
        # Should handle gracefully, either with default or error
        assert response.status_code in [200, 400]
    
    def test_api_handles_missing_required_parameters(self, authenticated_client):
        """Test API handles missing required parameters"""
        # Stock price endpoint requires symbol in URL
        response = authenticated_client.get('/api/stocks//price')
        # Should return 404 for invalid route
        assert response.status_code == 404
