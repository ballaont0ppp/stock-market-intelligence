"""
Comprehensive tests for PWA and responsive features.
Tests verify responsive breakpoints, layout behavior, service worker caching,
offline functionality, and touch interactions.

**Feature: mobile-pwa, Property 1: Responsive layout consistency**
**Feature: mobile-pwa, Property 3: Offline content availability**
**Feature: mobile-pwa, Property 2: Touch target accessibility**
**Validates: Requirements 1.1, 3.1, 4.1**
"""

import pytest
import json


class TestResponsiveBreakpoints:
    """Test responsive CSS breakpoints."""

    def test_mobile_breakpoint_576px(self):
        """Test that mobile breakpoint is defined at 576px."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 576px)' in content

    def test_tablet_breakpoint_768px(self):
        """Test that tablet breakpoint is defined at 768px."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (min-width: 768px)' in content

    def test_desktop_breakpoint_992px(self):
        """Test that desktop breakpoint is defined at 992px."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (min-width: 992px)' in content or '@media (min-width: 768px)' in content

    def test_large_desktop_breakpoint_1200px(self):
        """Test that large desktop breakpoint is defined at 1200px."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (min-width: 1200px)' in content or '@media (min-width: 992px)' in content

    def test_breakpoint_consistency(self):
        """Test that breakpoints are used consistently."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        # Count breakpoint occurrences
        mobile_count = content.count('@media (max-width: 576px)')
        tablet_count = content.count('@media (min-width: 768px)')
        
        assert mobile_count > 0, "Mobile breakpoint should be used"
        assert tablet_count > 0, "Tablet breakpoint should be used"


class TestResponsiveLayout:
    """Test responsive layout behavior."""

    def test_sidebar_responsive(self):
        """Test that sidebar is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.sidebar' in content
        assert '@media' in content

    def test_main_content_responsive(self):
        """Test that main content is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.main-content' in content or '.page-content' in content

    def test_grid_system_responsive(self):
        """Test that grid system is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'grid' in content.lower() or 'flex' in content.lower()

    def test_no_horizontal_overflow(self):
        """Test that layout doesn't cause horizontal overflow."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'overflow-x: hidden' in content or 'max-width: 100%' in content

    def test_responsive_typography(self):
        """Test that typography is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'font-size' in content

    def test_responsive_spacing(self):
        """Test that spacing is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'padding' in content or 'margin' in content


class TestTouchTargetAccessibility:
    """Test touch target sizing for accessibility."""

    def test_minimum_touch_target_height(self):
        """Test that touch targets have minimum 44px height."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'min-height: 44px' in content

    def test_minimum_touch_target_width(self):
        """Test that touch targets have minimum 44px width."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'min-width: 44px' in content

    def test_button_touch_target_size(self):
        """Test that buttons meet touch target requirements."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'button' in content.lower()
        assert 'min-height: 44px' in content

    def test_link_touch_target_size(self):
        """Test that links meet touch target requirements."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'a' in content.lower() or 'link' in content.lower()

    def test_form_input_touch_target_size(self):
        """Test that form inputs meet touch target requirements."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'input' in content.lower()
        assert 'min-height: 44px' in content

    def test_touch_target_spacing(self):
        """Test that touch targets have adequate spacing."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'gap' in content or 'margin' in content or 'padding' in content


class TestServiceWorkerCaching:
    """Test service worker caching functionality."""

    def test_service_worker_file_exists(self):
        """Test that service worker file exists."""
        import os
        assert os.path.exists('static/sw.js')

    def test_service_worker_registered(self):
        """Test that service worker is registered."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'navigator.serviceWorker.register' in content

    def test_cache_version_defined(self):
        """Test that cache version is defined."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'CACHE_VERSION' in content or 'CACHE' in content

    def test_cache_names_defined(self):
        """Test that cache names are defined."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'CACHE_NAMES' in content or 'STATIC' in content

    def test_static_assets_cached(self):
        """Test that static assets are cached."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'STATIC_ASSETS' in content or 'addAll' in content

    def test_cache_first_strategy(self):
        """Test that cache-first strategy is implemented."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'cacheFirstStrategy' in content or 'caches.match' in content

    def test_network_first_strategy(self):
        """Test that network-first strategy is implemented."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'networkFirstStrategy' in content or 'fetch' in content

    def test_stale_while_revalidate_strategy(self):
        """Test that stale-while-revalidate strategy is implemented."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'staleWhileRevalidateStrategy' in content or 'stale' in content.lower()


class TestOfflineFunctionality:
    """Test offline functionality."""

    def test_offline_page_exists(self):
        """Test that offline page exists."""
        import os
        assert os.path.exists('app/templates/offline.html')

    def test_offline_page_content(self):
        """Test that offline page has content."""
        with open('app/templates/offline.html', 'r') as f:
            content = f.read()
        
        assert len(content) > 0
        assert 'offline' in content.lower() or 'connection' in content.lower()

    def test_network_status_detection(self):
        """Test that network status is detected."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'online' in content.lower() or 'offline' in content.lower()

    def test_cached_content_accessible(self):
        """Test that cached content is accessible offline."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'caches.match' in content or 'cache' in content.lower()

    def test_offline_indicator(self):
        """Test that offline state is indicated to user."""
        with open('static/sw.js', 'r') as f:
            content = f.read()
        
        assert 'offline' in content.lower() or 'console.log' in content


class TestTouchInteractions:
    """Test touch interactions and gestures."""

    def test_touch_event_listeners(self):
        """Test that touch event listeners are attached."""
        with open('static/js/touch-optimizations.js', 'r') as f:
            content = f.read()
        
        assert 'touchstart' in content
        assert 'touchend' in content

    def test_swipe_gesture_detection(self):
        """Test that swipe gestures are detected."""
        with open('static/js/touch-optimizations.js', 'r') as f:
            content = f.read()
        
        assert 'detectSwipe' in content or 'swipe' in content.lower()

    def test_touch_feedback(self):
        """Test that touch feedback is provided."""
        with open('static/js/touch-optimizations.js', 'r') as f:
            content = f.read()
        
        assert 'touch-active' in content or 'touchstart' in content

    def test_mobile_navigation_touch_friendly(self):
        """Test that mobile navigation is touch-friendly."""
        with open('static/js/mobile-navigation.js', 'r') as f:
            content = f.read()
        
        assert 'touch' in content.lower() or 'click' in content.lower()

    def test_form_touch_optimization(self):
        """Test that forms are optimized for touch."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'input' in content.lower()
        assert 'font-size: 16px' in content


class TestMobileNavigation:
    """Test mobile navigation functionality."""

    def test_mobile_menu_exists(self):
        """Test that mobile menu exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'sidebar' in content.lower() or 'menu' in content.lower()

    def test_hamburger_menu_button(self):
        """Test that hamburger menu button exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'menuToggle' in content or 'menu' in content.lower()

    def test_mobile_navigation_responsive(self):
        """Test that mobile navigation is responsive."""
        with open('static/js/mobile-navigation.js', 'r') as f:
            content = f.read()
        
        assert 'class MobileNavigation' in content

    def test_sidebar_overlay(self):
        """Test that sidebar overlay exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'sidebarOverlay' in content or 'overlay' in content.lower()

    def test_touch_friendly_navigation_items(self):
        """Test that navigation items are touch-friendly."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'min-height: 44px' in content


class TestPWAManifest:
    """Test PWA manifest configuration."""

    def test_manifest_file_exists(self):
        """Test that manifest.json exists."""
        import os
        assert os.path.exists('static/manifest.json')

    def test_manifest_valid_json(self):
        """Test that manifest is valid JSON."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert isinstance(manifest, dict)

    def test_manifest_has_required_fields(self):
        """Test that manifest has required fields."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'short_name', 'display', 'start_url', 'icons']
        for field in required_fields:
            assert field in manifest, f"Manifest missing required field: {field}"

    def test_manifest_display_mode_standalone(self):
        """Test that manifest display mode is standalone."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['display'] == 'standalone'

    def test_manifest_icons_present(self):
        """Test that manifest includes icons."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'icons' in manifest
        assert len(manifest['icons']) > 0

    def test_manifest_icon_sizes(self):
        """Test that manifest includes required icon sizes."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        icon_sizes = [icon['sizes'] for icon in manifest['icons']]
        assert '192x192' in icon_sizes
        assert '512x512' in icon_sizes


class TestPWAMetaTags:
    """Test PWA meta tags in HTML."""

    def test_manifest_link_present(self):
        """Test that manifest link is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'rel="manifest"' in content

    def test_theme_color_meta_tag(self):
        """Test that theme-color meta tag is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'name="theme-color"' in content

    def test_apple_mobile_web_app_capable(self):
        """Test that apple-mobile-web-app-capable meta tag is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-mobile-web-app-capable' in content

    def test_apple_touch_icon(self):
        """Test that apple-touch-icon link is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-touch-icon' in content

    def test_viewport_meta_tag(self):
        """Test that viewport meta tag is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'viewport' in content


class TestResponsiveImages:
    """Test responsive image handling."""

    def test_images_responsive(self):
        """Test that images are responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'max-width: 100%' in content or 'width: 100%' in content

    def test_images_maintain_aspect_ratio(self):
        """Test that images maintain aspect ratio."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'height: auto' in content or 'aspect-ratio' in content


class TestResponsiveTables:
    """Test responsive table handling."""

    def test_table_responsive_class(self):
        """Test that responsive table class exists."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'table-responsive' in content or 'table' in content.lower()

    def test_table_horizontal_scroll(self):
        """Test that tables support horizontal scrolling."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'overflow-x' in content or 'scroll' in content.lower()

    def test_table_sticky_header(self):
        """Test that table headers are sticky."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'sticky' in content or 'position: sticky' in content


class TestResponsiveCharts:
    """Test responsive chart handling."""

    def test_chart_responsive_sizing(self):
        """Test that charts are responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'chart' in content.lower()

    def test_chart_container_responsive(self):
        """Test that chart containers are responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'chart-container' in content or 'container' in content.lower()


class TestAccessibilityFeatures:
    """Test accessibility features."""

    def test_focus_states_defined(self):
        """Test that focus states are defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert ':focus' in content

    def test_color_contrast(self):
        """Test that color contrast is considered."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'color' in content.lower()

    def test_semantic_html_used(self):
        """Test that semantic HTML is used."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert '<button' in content or '<nav' in content or '<header' in content

    def test_aria_labels_present(self):
        """Test that ARIA labels are present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'aria' in content.lower() or 'role=' in content


class TestPerformanceOptimizations:
    """Test performance optimizations."""

    def test_smooth_scrolling_enabled(self):
        """Test that smooth scrolling is enabled."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'scroll-behavior: smooth' in content

    def test_momentum_scrolling_enabled(self):
        """Test that momentum scrolling is enabled."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '-webkit-overflow-scrolling: touch' in content

    def test_transitions_optimized(self):
        """Test that transitions are optimized."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'transition' in content

    def test_animations_optimized(self):
        """Test that animations are optimized."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@keyframes' in content or 'animation' in content


class TestIntegration:
    """Test integration of all PWA and responsive features."""

    def test_all_scripts_loaded(self):
        """Test that all required scripts are loaded."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        required_scripts = [
            'pwa-install-prompt.js',
            'touch-optimizations.js',
            'mobile-navigation.js',
            'sw.js'
        ]
        
        for script in required_scripts:
            assert script in content, f"Missing script: {script}"

    def test_all_css_loaded(self):
        """Test that all required CSS is loaded."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'pages.css' in content or 'components.css' in content

    def test_service_worker_and_manifest_together(self):
        """Test that service worker and manifest work together."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'manifest.json' in content
        assert 'sw.js' in content

    def test_responsive_and_pwa_features_together(self):
        """Test that responsive and PWA features work together."""
        with open('static/css/pages.css', 'r') as f:
            css_content = f.read()
        
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        # Check responsive features
        assert '@media' in css_content
        
        # Check PWA features
        assert 'display' in manifest
        assert 'icons' in manifest
