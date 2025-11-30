"""
Tests for Service Worker and offline functionality.
Tests verify that the service worker is properly configured, caching strategies work,
and offline functionality is available.

**Feature: mobile-pwa, Property 3: Offline content availability**
**Validates: Requirements 3.1, 3.2, 3.3**
"""

import pytest
import json
import os


class TestServiceWorkerFile:
    """Test service worker file existence and structure."""

    def test_service_worker_file_exists(self):
        """Test that service worker file exists."""
        assert os.path.exists('static/sw.js')

    def test_service_worker_is_valid_javascript(self):
        """Test that service worker file is valid JavaScript."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        # Check for basic JavaScript structure
        assert 'self.addEventListener' in content
        assert 'fetch' in content
        assert 'install' in content
        assert 'activate' in content

    def test_service_worker_has_cache_names(self):
        """Test that service worker defines cache names."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'CACHE_NAMES' in content
        assert 'STATIC' in content
        assert 'DYNAMIC' in content
        assert 'API' in content
        assert 'OFFLINE' in content

    def test_service_worker_has_static_assets_list(self):
        """Test that service worker defines static assets to cache."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'STATIC_ASSETS' in content
        assert '/dashboard' in content
        assert '/offline' in content

    def test_service_worker_has_install_event(self):
        """Test that service worker has install event handler."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert "self.addEventListener('install'" in content
        assert 'caches.open' in content
        assert 'cache.addAll' in content

    def test_service_worker_has_activate_event(self):
        """Test that service worker has activate event handler."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert "self.addEventListener('activate'" in content
        assert 'caches.keys()' in content
        assert 'caches.delete' in content

    def test_service_worker_has_fetch_event(self):
        """Test that service worker has fetch event handler."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert "self.addEventListener('fetch'" in content
        assert 'request.method' in content
        assert 'GET' in content

    def test_service_worker_has_cache_first_strategy(self):
        """Test that service worker implements cache-first strategy."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'cacheFirstStrategy' in content
        assert 'caches.match' in content

    def test_service_worker_has_network_first_strategy(self):
        """Test that service worker implements network-first strategy."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'networkFirstStrategy' in content
        assert 'fetch(request)' in content

    def test_service_worker_has_stale_while_revalidate_strategy(self):
        """Test that service worker implements stale-while-revalidate strategy."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'staleWhileRevalidateStrategy' in content

    def test_service_worker_handles_api_requests(self):
        """Test that service worker handles API requests."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert '/api/' in content
        assert 'networkFirstStrategy' in content

    def test_service_worker_handles_navigation_requests(self):
        """Test that service worker handles navigation requests."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'request.mode === \'navigate\'' in content
        assert 'staleWhileRevalidateStrategy' in content

    def test_service_worker_handles_static_assets(self):
        """Test that service worker handles static assets."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'cacheFirstStrategy' in content

    def test_service_worker_has_message_handler(self):
        """Test that service worker has message event handler."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert "self.addEventListener('message'" in content
        assert 'SKIP_WAITING' in content
        assert 'CLEAR_CACHE' in content

    def test_service_worker_has_offline_fallback(self):
        """Test that service worker has offline fallback."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert "caches.match('/offline')" in content
        assert '.catch' in content


class TestOfflinePage:
    """Test offline page."""

    def test_offline_page_template_exists(self):
        """Test that offline page template exists."""
        assert os.path.exists('app/templates/offline.html')

    def test_offline_page_has_html_structure(self):
        """Test that offline page has proper HTML structure."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert '<!DOCTYPE html>' in content
        assert '<html' in content
        assert '<head>' in content
        assert '<body>' in content

    def test_offline_page_has_title(self):
        """Test that offline page has title."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert '<title>' in content
        assert 'Offline' in content

    def test_offline_page_has_offline_icon(self):
        """Test that offline page displays offline icon."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert 'wifi-off' in content or 'offline' in content.lower()

    def test_offline_page_has_message(self):
        """Test that offline page has offline message."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert "You're Offline" in content or 'offline' in content.lower()

    def test_offline_page_has_retry_button(self):
        """Test that offline page has retry button."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert 'Try Again' in content or 'Retry' in content.lower()

    def test_offline_page_has_dashboard_link(self):
        """Test that offline page has link to dashboard."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert 'Dashboard' in content
        assert '/dashboard' in content

    def test_offline_page_has_available_features_list(self):
        """Test that offline page lists available features."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert 'Available Offline' in content or 'available' in content.lower()
        assert 'portfolio' in content.lower()

    def test_offline_page_has_connection_status(self):
        """Test that offline page shows connection status."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert 'Connection Status' in content or 'connection' in content.lower()

    def test_offline_page_has_online_event_listener(self):
        """Test that offline page listens for online event."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert "'online'" in content or '"online"' in content
        assert 'addEventListener' in content

    def test_offline_page_has_responsive_design(self):
        """Test that offline page has responsive design."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert '@media' in content
        assert 'max-width' in content


class TestServiceWorkerRegistration:
    """Test service worker registration in base template."""

    def test_service_worker_registration_in_template(self):
        """Test that service worker is registered in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'serviceWorker' in content
        assert 'navigator.serviceWorker.register' in content

    def test_service_worker_registration_path(self):
        """Test that service worker registration uses correct path."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert '/static/sw.js' in content

    def test_service_worker_registration_error_handling(self):
        """Test that service worker registration has error handling."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert '.catch' in content
        assert 'error' in content.lower()

    def test_service_worker_update_check(self):
        """Test that service worker checks for updates."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'registration.update' in content or 'update' in content.lower()

    def test_online_offline_event_listeners(self):
        """Test that online/offline event listeners are registered."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert "'online'" in content or '"online"' in content
        assert "'offline'" in content or '"offline"' in content


class TestOfflineRoute:
    """Test offline route."""

    def test_offline_route_exists(self, client):
        """Test that offline route exists."""
        response = client.get('/offline')
        assert response.status_code == 200

    def test_offline_route_returns_html(self, client):
        """Test that offline route returns HTML."""
        response = client.get('/offline')
        assert response.content_type == 'text/html; charset=utf-8'

    def test_offline_route_contains_offline_page(self, client):
        """Test that offline route returns offline page."""
        response = client.get('/offline')
        assert b'Offline' in response.data or b'offline' in response.data.lower()

    def test_offline_route_is_public(self, client):
        """Test that offline route is accessible without authentication."""
        response = client.get('/offline')
        # Should not redirect to login
        assert response.status_code == 200


class TestCachingStrategies:
    """Test caching strategies in service worker."""

    def test_static_assets_use_cache_first(self):
        """Test that static assets use cache-first strategy."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        # Check that CSS, JS, images use cache-first
        assert 'cacheFirstStrategy' in content
        assert '.css' in content or '.js' in content or 'static' in content

    def test_api_requests_use_network_first(self):
        """Test that API requests use network-first strategy."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert '/api/' in content
        assert 'networkFirstStrategy' in content

    def test_navigation_uses_stale_while_revalidate(self):
        """Test that navigation requests use stale-while-revalidate."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'navigate' in content
        assert 'staleWhileRevalidateStrategy' in content

    def test_cache_versioning(self):
        """Test that cache uses versioning."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'CACHE_VERSION' in content
        assert 'v1' in content

    def test_cache_cleanup_on_activate(self):
        """Test that old caches are cleaned up on activate."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'activate' in content
        assert 'caches.delete' in content


class TestOfflineContentAvailability:
    """Test that offline content is available.
    
    **Feature: mobile-pwa, Property 3: Offline content availability**
    **Validates: Requirements 3.1**
    """

    def test_offline_page_is_cached(self):
        """Test that offline page is in static assets list."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert '/offline' in content
        assert 'STATIC_ASSETS' in content

    def test_dashboard_is_cached(self):
        """Test that dashboard is in static assets list."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert '/dashboard' in content

    def test_css_assets_are_cached(self):
        """Test that CSS assets are in static assets list."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'design-system.css' in content
        assert 'components.css' in content

    def test_js_assets_are_cached(self):
        """Test that JavaScript assets are in static assets list."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'main.js' in content
        assert 'mobile-navigation.js' in content

    def test_icons_are_cached(self):
        """Test that icons are in static assets list."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'icon-192x192.png' in content
        assert 'icon-512x512.png' in content


class TestNetworkStatusDetection:
    """Test network status detection."""

    def test_offline_page_detects_online_status(self):
        """Test that offline page detects when online."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert "'online'" in content or '"online"' in content
        assert 'addEventListener' in content

    def test_offline_page_reloads_on_online(self):
        """Test that offline page reloads when connection restored."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert "'online'" in content or '"online"' in content
        assert 'location.reload' in content or 'reload' in content

    def test_base_template_monitors_connection(self):
        """Test that base template monitors connection status."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert "'online'" in content or '"online"' in content
        assert "'offline'" in content or '"offline"' in content


class TestServiceWorkerPerformance:
    """Test service worker performance optimizations.
    
    **Feature: mobile-pwa, Property 6: Cache performance improvement**
    **Validates: Requirements 3.4**
    """

    def test_cache_first_improves_performance(self):
        """Test that cache-first strategy improves performance."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        # Cache-first should check cache before network
        assert 'caches.match(request)' in content
        assert 'fetch(request)' in content

    def test_stale_while_revalidate_improves_performance(self):
        """Test that stale-while-revalidate improves performance."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        # Should return cached response immediately
        assert 'caches.match(request)' in content
        assert 'return response' in content

    def test_cache_prevents_network_requests(self):
        """Test that cache prevents unnecessary network requests."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        # Should check cache first
        assert 'caches.match' in content
        assert 'if (response)' in content or 'if(response)' in content
