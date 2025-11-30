"""
Tests for PWA manifest and icons.
Tests verify that the PWA manifest is properly configured and icons are generated.
"""

import pytest
import json
import os
from PIL import Image


class TestPWAManifest:
    """Test PWA manifest configuration."""

    def test_manifest_file_exists(self):
        """Test that manifest.json file exists."""
        assert os.path.exists('static/manifest.json')

    def test_manifest_is_valid_json(self):
        """Test that manifest.json is valid JSON."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        assert isinstance(manifest, dict)

    def test_manifest_has_required_fields(self):
        """Test that manifest has all required fields."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_name(self):
        """Test that manifest has correct name."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['name'] == 'Stock Portfolio Platform'
        assert manifest['short_name'] == 'Portfolio'

    def test_manifest_start_url(self):
        """Test that manifest has correct start URL."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['start_url'] == '/dashboard'

    def test_manifest_display_mode(self):
        """Test that manifest has standalone display mode."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['display'] == 'standalone'

    def test_manifest_theme_color(self):
        """Test that manifest has theme color."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'theme_color' in manifest
        assert manifest['theme_color'] == '#2563eb'

    def test_manifest_background_color(self):
        """Test that manifest has background color."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'background_color' in manifest
        assert manifest['background_color'] == '#ffffff'

    def test_manifest_scope(self):
        """Test that manifest has correct scope."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert manifest['scope'] == '/'

    def test_manifest_orientation(self):
        """Test that manifest has orientation setting."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'orientation' in manifest
        assert manifest['orientation'] == 'portrait-primary'

    def test_manifest_categories(self):
        """Test that manifest has categories."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'categories' in manifest
        assert 'finance' in manifest['categories']

    def test_manifest_icons_exist(self):
        """Test that manifest has icons array."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'icons' in manifest
        assert len(manifest['icons']) > 0

    def test_manifest_icons_have_required_fields(self):
        """Test that each icon has required fields."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        for icon in manifest['icons']:
            assert 'src' in icon
            assert 'sizes' in icon
            assert 'type' in icon

    def test_manifest_has_192px_icon(self):
        """Test that manifest includes 192px icon."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        icon_sizes = [icon['sizes'] for icon in manifest['icons']]
        assert '192x192' in icon_sizes

    def test_manifest_has_512px_icon(self):
        """Test that manifest includes 512px icon."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        icon_sizes = [icon['sizes'] for icon in manifest['icons']]
        assert '512x512' in icon_sizes

    def test_manifest_has_maskable_icons(self):
        """Test that manifest includes maskable icons."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        maskable_icons = [icon for icon in manifest['icons'] if icon.get('purpose') == 'maskable']
        assert len(maskable_icons) > 0

    def test_manifest_has_shortcuts(self):
        """Test that manifest has shortcuts."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'shortcuts' in manifest
        assert len(manifest['shortcuts']) > 0

    def test_manifest_shortcuts_have_required_fields(self):
        """Test that each shortcut has required fields."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        for shortcut in manifest['shortcuts']:
            assert 'name' in shortcut
            assert 'url' in shortcut

    def test_manifest_has_screenshots(self):
        """Test that manifest has screenshots."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'screenshots' in manifest
        assert len(manifest['screenshots']) > 0

    def test_manifest_screenshots_have_required_fields(self):
        """Test that each screenshot has required fields."""
        with open('static/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        for screenshot in manifest['screenshots']:
            assert 'src' in screenshot
            assert 'sizes' in screenshot
            assert 'type' in screenshot


class TestPWAIcons:
    """Test PWA icon generation."""

    def test_icons_directory_exists(self):
        """Test that icons directory exists."""
        assert os.path.exists('static/icons')

    def test_192px_icon_exists(self):
        """Test that 192px icon exists."""
        assert os.path.exists('static/icons/icon-192x192.png')

    def test_512px_icon_exists(self):
        """Test that 512px icon exists."""
        assert os.path.exists('static/icons/icon-512x512.png')

    def test_192px_maskable_icon_exists(self):
        """Test that 192px maskable icon exists."""
        assert os.path.exists('static/icons/icon-192x192-maskable.png')

    def test_512px_maskable_icon_exists(self):
        """Test that 512px maskable icon exists."""
        assert os.path.exists('static/icons/icon-512x512-maskable.png')

    def test_icon_dimensions(self):
        """Test that icons have correct dimensions."""
        icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
        
        for size in icon_sizes:
            icon_path = f'static/icons/icon-{size}x{size}.png'
            assert os.path.exists(icon_path), f"Icon {icon_path} not found"
            
            img = Image.open(icon_path)
            assert img.size == (size, size), f"Icon {icon_path} has wrong dimensions: {img.size}"

    def test_icon_format(self):
        """Test that icons are PNG format."""
        icon_path = 'static/icons/icon-192x192.png'
        img = Image.open(icon_path)
        assert img.format == 'PNG'

    def test_maskable_icon_dimensions(self):
        """Test that maskable icons have correct dimensions."""
        maskable_sizes = [192, 512]
        
        for size in maskable_sizes:
            icon_path = f'static/icons/icon-{size}x{size}-maskable.png'
            assert os.path.exists(icon_path)
            
            img = Image.open(icon_path)
            assert img.size == (size, size)

    def test_screenshot_exists(self):
        """Test that screenshots exist."""
        screenshots = [
            'static/icons/screenshot-540x720.png',
            'static/icons/screenshot-1280x720.png'
        ]
        
        for screenshot in screenshots:
            assert os.path.exists(screenshot)

    def test_screenshot_dimensions(self):
        """Test that screenshots have correct dimensions."""
        screenshots = [
            ('static/icons/screenshot-540x720.png', (540, 720)),
            ('static/icons/screenshot-1280x720.png', (1280, 720))
        ]
        
        for path, expected_size in screenshots:
            img = Image.open(path)
            assert img.size == expected_size

    def test_shortcut_icons_exist(self):
        """Test that shortcut icons exist."""
        shortcuts = ['dashboard', 'portfolio', 'orders']
        
        for shortcut in shortcuts:
            icon_path = f'static/icons/shortcut-{shortcut}-96x96.png'
            assert os.path.exists(icon_path)

    def test_shortcut_icon_dimensions(self):
        """Test that shortcut icons have correct dimensions."""
        shortcuts = ['dashboard', 'portfolio', 'orders']
        
        for shortcut in shortcuts:
            icon_path = f'static/icons/shortcut-{shortcut}-96x96.png'
            img = Image.open(icon_path)
            assert img.size == (96, 96)


class TestPWAMetaTags:
    """Test PWA meta tags in base template."""

    def test_manifest_link_in_template(self):
        """Test that manifest link is in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'manifest.json' in content
        assert 'rel="manifest"' in content

    def test_theme_color_meta_tag(self):
        """Test that theme-color meta tag exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'name="theme-color"' in content
        assert '#2563eb' in content

    def test_apple_mobile_web_app_capable(self):
        """Test that apple-mobile-web-app-capable meta tag exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-mobile-web-app-capable' in content
        assert 'content="yes"' in content

    def test_apple_mobile_web_app_title(self):
        """Test that apple-mobile-web-app-title meta tag exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-mobile-web-app-title' in content
        assert 'Portfolio' in content

    def test_apple_touch_icon_link(self):
        """Test that apple-touch-icon link exists."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'apple-touch-icon' in content
        assert 'icon-192x192.png' in content

    def test_favicon_links(self):
        """Test that favicon links exist."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'icon-192x192.png' in content
        assert 'icon-512x512.png' in content
