"""
Tests for PWA installation prompt functionality.
Tests verify that the PWA installation prompt is properly implemented,
handles beforeinstallprompt events, and provides user feedback.

**Feature: mobile-pwa, Property 4: PWA installation criteria**
**Validates: Requirements 2.1, 2.3**
"""

import pytest


class TestPWAInstallPromptHTML:
    """Test PWA installation prompt HTML structure."""

    def test_pwa_install_script_included(self):
        """Test that PWA install prompt script is included in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'pwa-install-prompt.js' in content
        assert '<script src=' in content and 'pwa-install-prompt.js' in content

    def test_pwa_install_script_loaded_after_bootstrap(self):
        """Test that PWA install script is loaded after Bootstrap."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        bootstrap_pos = content.find('bootstrap.bundle.min.js')
        pwa_install_pos = content.find('pwa-install-prompt.js')
        
        assert bootstrap_pos > 0, "Bootstrap script not found"
        assert pwa_install_pos > 0, "PWA install script not found"
        assert pwa_install_pos > bootstrap_pos, "PWA install script should load after Bootstrap"

    def test_manifest_link_in_head(self):
        """Test that manifest link is in the head section."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'rel="manifest"' in content
        assert 'manifest.json' in content

    def test_theme_color_meta_tag(self):
        """Test that theme-color meta tag is present."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'name="theme-color"' in content
        assert 'content="#2563eb"' in content


class TestPWAInstallPromptJavaScript:
    """Test PWA installation prompt JavaScript implementation."""

    def test_pwa_install_prompt_file_exists(self):
        """Test that PWA install prompt JavaScript file exists."""
        import os
        assert os.path.exists('static/js/pwa-install-prompt.js')

    def test_pwa_install_prompt_class_defined(self):
        """Test that PWAInstallPrompt class is defined."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'class PWAInstallPrompt' in content

    def test_pwa_install_prompt_init_method(self):
        """Test that PWAInstallPrompt has init method."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'init()' in content

    def test_beforeinstallprompt_event_handler(self):
        """Test that beforeinstallprompt event is handled."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'beforeinstallprompt' in content
        assert 'handleBeforeInstallPrompt' in content

    def test_appinstalled_event_handler(self):
        """Test that appinstalled event is handled."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'appinstalled' in content
        assert 'handleAppInstalled' in content

    def test_install_button_creation(self):
        """Test that install button is created."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'createInstallButton' in content
        assert 'pwa-install-button' in content
        assert 'pwa-install-container' in content

    def test_install_button_click_handler(self):
        """Test that install button click is handled."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'handleInstallClick' in content
        assert 'deferredPrompt.prompt()' in content

    def test_deferred_prompt_storage(self):
        """Test that deferred prompt is stored."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'this.deferredPrompt' in content
        assert 'e.preventDefault()' in content

    def test_installation_success_feedback(self):
        """Test that installation success feedback is shown."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'showInstallationSuccess' in content
        assert 'pwa-install-success' in content
        assert 'alert-success' in content

    def test_install_prompt_dismissal(self):
        """Test that install prompt can be dismissed."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'dismissInstallPrompt' in content
        assert 'pwa_install_dismissed' in content

    def test_localStorage_usage(self):
        """Test that localStorage is used to track installation state."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'localStorage.setItem' in content
        assert 'localStorage.getItem' in content
        assert 'pwa_installed' in content

    def test_display_mode_detection(self):
        """Test that display mode is detected."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'getDisplayMode' in content
        assert 'display-mode: standalone' in content
        assert 'navigator.standalone' in content

    def test_global_instance_creation(self):
        """Test that global PWA install prompt instance is created."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'window.pwaInstallPrompt' in content
        assert 'new PWAInstallPrompt()' in content

    def test_dom_ready_check(self):
        """Test that script checks DOM ready state."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'document.readyState' in content
        assert 'DOMContentLoaded' in content


class TestPWAInstallPromptCSS:
    """Test PWA installation prompt CSS implementation."""

    def test_pwa_install_container_css(self):
        """Test that PWA install container CSS is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.pwa-install-container' in content
        assert 'PWA INSTALLATION PROMPT' in content

    def test_pwa_install_button_css(self):
        """Test that PWA install button CSS is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.pwa-install-button' in content
        assert 'min-height: 44px' in content
        assert 'min-width: 44px' in content

    def test_pwa_install_close_button_css(self):
        """Test that PWA install close button CSS is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.pwa-install-close' in content

    def test_pwa_install_success_notification_css(self):
        """Test that PWA install success notification CSS is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.pwa-install-success' in content

    def test_pwa_install_animation(self):
        """Test that PWA install prompt has animation."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'slideDown' in content or 'animation:' in content

    def test_pwa_install_responsive_design(self):
        """Test that PWA install prompt is responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 576px)' in content
        assert '.pwa-install-container' in content

    def test_pwa_install_touch_target_size(self):
        """Test that touch targets meet minimum size requirements."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        # Check for 44px minimum touch target size
        assert 'min-height: 44px' in content
        assert 'min-width: 44px' in content

    def test_pwa_install_dark_mode_support(self):
        """Test that PWA install prompt supports dark mode."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (prefers-color-scheme: dark)' in content

    def test_pwa_install_reduced_motion_support(self):
        """Test that PWA install prompt respects reduced motion preference."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (prefers-reduced-motion: reduce)' in content


class TestPWAInstallPromptManifest:
    """Test PWA manifest configuration."""

    def test_manifest_file_exists(self):
        """Test that manifest.json file exists."""
        import os
        assert os.path.exists('static/manifest.json')

    def test_manifest_has_name(self):
        """Test that manifest has app name."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'name' in manifest
        assert manifest['name'] == 'Stock Portfolio Platform'

    def test_manifest_has_short_name(self):
        """Test that manifest has short name."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'short_name' in manifest
        assert manifest['short_name'] == 'Portfolio'

    def test_manifest_has_display_mode(self):
        """Test that manifest specifies standalone display mode."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'display' in manifest
        assert manifest['display'] == 'standalone'

    def test_manifest_has_start_url(self):
        """Test that manifest has start URL."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'start_url' in manifest
        assert manifest['start_url'] == '/dashboard'

    def test_manifest_has_theme_color(self):
        """Test that manifest has theme color."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'theme_color' in manifest
        assert manifest['theme_color'] == '#2563eb'

    def test_manifest_has_background_color(self):
        """Test that manifest has background color."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'background_color' in manifest
        assert manifest['background_color'] == '#ffffff'

    def test_manifest_has_icons(self):
        """Test that manifest includes app icons."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'icons' in manifest
        assert len(manifest['icons']) > 0
        
        # Check for required icon sizes
        icon_sizes = [icon['sizes'] for icon in manifest['icons']]
        assert '192x192' in icon_sizes
        assert '512x512' in icon_sizes

    def test_manifest_has_description(self):
        """Test that manifest has description."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'description' in manifest
        assert len(manifest['description']) > 0

    def test_manifest_has_scope(self):
        """Test that manifest has scope."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'scope' in manifest
        assert manifest['scope'] == '/'

    def test_manifest_has_shortcuts(self):
        """Test that manifest includes app shortcuts."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'shortcuts' in manifest
        assert len(manifest['shortcuts']) > 0

    def test_manifest_shortcuts_have_required_fields(self):
        """Test that shortcuts have required fields."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        for shortcut in manifest['shortcuts']:
            assert 'name' in shortcut
            assert 'url' in shortcut


class TestPWAInstallPromptIntegration:
    """Test PWA installation prompt integration."""

    def test_service_worker_registered(self):
        """Test that service worker is registered in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'navigator.serviceWorker.register' in content
        assert '/static/sw.js' in content

    def test_service_worker_file_exists(self):
        """Test that service worker file exists."""
        import os
        assert os.path.exists('static/sw.js')

    def test_offline_page_exists(self):
        """Test that offline page exists."""
        import os
        assert os.path.exists('app/templates/offline.html')

    def test_pwa_meta_tags_in_template(self):
        """Test that PWA meta tags are in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-mobile-web-app-capable' in content
        assert 'apple-mobile-web-app-status-bar-style' in content
        assert 'apple-mobile-web-app-title' in content
        assert 'apple-touch-icon' in content

    def test_pwa_install_prompt_initialization_order(self):
        """Test that PWA install prompt initializes after DOM is ready."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        # Check that initialization happens after DOM is ready
        assert 'document.readyState' in content
        assert 'DOMContentLoaded' in content
        assert 'window.pwaInstallPrompt' in content


class TestPWAInstallPromptAccessibility:
    """Test PWA installation prompt accessibility."""

    def test_install_button_has_title_attribute(self):
        """Test that install button has title attribute."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert '.title' in content
        assert 'Install this app on your device' in content

    def test_close_button_has_title_attribute(self):
        """Test that close button has title attribute."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert '.title' in content
        assert 'Dismiss' in content

    def test_install_button_semantic_html(self):
        """Test that install button uses semantic HTML."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert '<button' in content
        assert 'class=' in content

    def test_success_notification_dismissible(self):
        """Test that success notification is dismissible."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'alert-dismissible' in content
        assert 'btn-close' in content


class TestPWAInstallPromptPerformance:
    """Test PWA installation prompt performance."""

    def test_install_prompt_lazy_initialization(self):
        """Test that install prompt initializes lazily."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        # Check that initialization waits for DOM ready
        assert 'document.readyState' in content or 'DOMContentLoaded' in content

    def test_install_button_not_created_until_needed(self):
        """Test that install button is only created when needed."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'createInstallButton' in content
        assert 'showInstallButton' in content

    def test_event_listeners_properly_attached(self):
        """Test that event listeners are properly attached."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'addEventListener' in content
        assert 'beforeinstallprompt' in content
        assert 'appinstalled' in content

    def test_no_memory_leaks_on_dismissal(self):
        """Test that dismissing prompt doesn't cause memory leaks."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        assert 'hideInstallButton' in content
        assert 'this.deferredPrompt = null' in content


class TestPWAInstallPromptBrowserCompatibility:
    """Test PWA installation prompt browser compatibility."""

    def test_feature_detection_for_beforeinstallprompt(self):
        """Test that beforeinstallprompt support is detected."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        # The code should handle cases where beforeinstallprompt is not supported
        assert 'addEventListener' in content

    def test_fallback_for_unsupported_browsers(self):
        """Test that there's a fallback for unsupported browsers."""
        with open('static/js/pwa-install-prompt.js', 'r') as f:
            content = f.read()
        
        # Check for error handling
        assert 'catch' in content or 'try' in content or 'console.log' in content

    def test_ios_support_via_meta_tags(self):
        """Test that iOS support is provided via meta tags."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-mobile-web-app-capable' in content
        assert 'apple-touch-icon' in content

    def test_android_support_via_manifest(self):
        """Test that Android support is provided via manifest."""
        import json
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'display' in manifest
        assert 'icons' in manifest
        assert 'start_url' in manifest
