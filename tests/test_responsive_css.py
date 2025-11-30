"""
Tests for responsive CSS framework implementation.
Tests verify that responsive breakpoints, grid system, and typography utilities work correctly.
"""

import pytest
from bs4 import BeautifulSoup


class TestResponsiveCSSFramework:
    """Test responsive CSS framework implementation."""

    def test_responsive_css_files_exist(self):
        """Test that all responsive CSS files are present."""
        import os
        
        css_files = [
            'static/css/components.css',
            'static/css/design-system.css',
            'static/css/pages.css'
        ]
        
        for css_file in css_files:
            assert os.path.exists(css_file), f"CSS file {css_file} not found"

    def test_components_css_contains_responsive_framework(self):
        """Test that components.css contains responsive framework utilities."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for responsive framework sections
        assert 'RESPONSIVE CSS FRAMEWORK' in content
        assert 'FLEXIBLE GRID SYSTEM' in content
        assert 'RESPONSIVE TYPOGRAPHY' in content
        assert 'RESPONSIVE SPACING UTILITIES' in content
        assert 'RESPONSIVE DISPLAY UTILITIES' in content
        assert 'RESPONSIVE FLEXBOX UTILITIES' in content
        assert 'RESPONSIVE CONTAINER UTILITIES' in content
        assert 'RESPONSIVE CARD UTILITIES' in content
        assert 'RESPONSIVE BUTTON UTILITIES' in content
        assert 'RESPONSIVE TABLE UTILITIES' in content
        assert 'RESPONSIVE FORM UTILITIES' in content

    def test_design_system_css_contains_responsive_utilities(self):
        """Test that design-system.css contains responsive typography and spacing."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive utilities
        assert 'RESPONSIVE TYPOGRAPHY UTILITIES' in content
        assert 'RESPONSIVE SPACING SCALE' in content
        assert 'RESPONSIVE PADDING SCALE' in content
        assert 'RESPONSIVE MARGIN SCALE' in content
        assert 'RESPONSIVE WIDTH UTILITIES' in content
        assert 'RESPONSIVE HEIGHT UTILITIES' in content
        assert 'RESPONSIVE BORDER RADIUS' in content
        assert 'RESPONSIVE SHADOW UTILITIES' in content

    def test_pages_css_contains_responsive_layouts(self):
        """Test that pages.css contains responsive page layouts."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        # Check for responsive layout sections
        assert 'RESPONSIVE DASHBOARD LAYOUT' in content
        assert 'RESPONSIVE PORTFOLIO LAYOUT' in content
        assert 'RESPONSIVE CARD LAYOUTS' in content
        assert 'RESPONSIVE FORM LAYOUT' in content
        assert 'RESPONSIVE TABLE LAYOUT' in content
        assert 'RESPONSIVE TOPBAR' in content
        assert 'RESPONSIVE PAGE CONTENT' in content

    def test_mobile_first_breakpoints_defined(self):
        """Test that mobile-first breakpoints are properly defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for breakpoint definitions
        breakpoints = [
            '@media (min-width: 576px)',  # Tablet
            '@media (min-width: 768px)',  # Small Desktop
            '@media (min-width: 992px)',  # Desktop
            '@media (min-width: 1200px)'  # Large Desktop
        ]
        
        for breakpoint in breakpoints:
            assert breakpoint in content, f"Breakpoint {breakpoint} not found"

    def test_grid_system_classes_defined(self):
        """Test that grid system classes are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for grid classes
        grid_classes = [
            '.grid-container',
            '.grid-auto',
            '.grid-2',
            '.grid-3',
            '.grid-4',
            '.grid-6'
        ]
        
        for grid_class in grid_classes:
            assert grid_class in content, f"Grid class {grid_class} not found"

    def test_responsive_typography_classes_defined(self):
        """Test that responsive typography classes are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive text classes
        text_classes = [
            '.text-responsive-sm',
            '.text-responsive-base',
            '.text-responsive-lg',
            '.text-responsive-xl',
            '.text-responsive-2xl'
        ]
        
        for text_class in text_classes:
            assert text_class in content, f"Text class {text_class} not found"

    def test_responsive_spacing_classes_defined(self):
        """Test that responsive spacing classes are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive spacing classes
        spacing_classes = [
            '.space-responsive-xs',
            '.space-responsive-sm',
            '.space-responsive-md',
            '.space-responsive-lg',
            '.space-responsive-xl',
            '.space-responsive-2xl'
        ]
        
        for spacing_class in spacing_classes:
            assert spacing_class in content, f"Spacing class {spacing_class} not found"

    def test_responsive_padding_classes_defined(self):
        """Test that responsive padding classes are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive padding classes
        padding_classes = [
            '.pad-responsive-xs',
            '.pad-responsive-sm',
            '.pad-responsive-md',
            '.pad-responsive-lg',
            '.pad-responsive-xl',
            '.pad-responsive-2xl'
        ]
        
        for padding_class in padding_classes:
            assert padding_class in content, f"Padding class {padding_class} not found"

    def test_responsive_display_utilities_defined(self):
        """Test that responsive display utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for display utilities
        display_utilities = [
            '.show-mobile',
            '.hide-mobile',
            '.show-tablet',
            '.show-desktop',
            '.mobile-only',
            '.tablet-only',
            '.desktop-up'
        ]
        
        for utility in display_utilities:
            assert utility in content, f"Display utility {utility} not found"

    def test_responsive_flexbox_utilities_defined(self):
        """Test that responsive flexbox utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for flexbox utilities
        flexbox_utilities = [
            '.flex-responsive',
            '.flex-responsive-row'
        ]
        
        for utility in flexbox_utilities:
            assert utility in content, f"Flexbox utility {utility} not found"

    def test_responsive_container_utilities_defined(self):
        """Test that responsive container utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for container utilities
        assert '.container-responsive' in content

    def test_responsive_card_utilities_defined(self):
        """Test that responsive card utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for card utilities
        assert '.card-responsive' in content

    def test_responsive_button_utilities_defined(self):
        """Test that responsive button utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for button utilities
        assert '.btn-responsive' in content

    def test_responsive_table_utilities_defined(self):
        """Test that responsive table utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for table utilities
        table_utilities = [
            '.table-responsive-wrapper',
            '.table-responsive'
        ]
        
        for utility in table_utilities:
            assert utility in content, f"Table utility {utility} not found"

    def test_responsive_form_utilities_defined(self):
        """Test that responsive form utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for form utilities
        form_utilities = [
            '.form-group-responsive',
            '.form-row-responsive'
        ]
        
        for utility in form_utilities:
            assert utility in content, f"Form utility {utility} not found"

    def test_responsive_modal_utilities_defined(self):
        """Test that responsive modal utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for modal utilities
        assert '.modal-responsive' in content

    def test_responsive_aspect_ratio_utilities_defined(self):
        """Test that responsive aspect ratio utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for aspect ratio utilities
        aspect_ratio_utilities = [
            '.aspect-ratio-container',
            '.aspect-ratio-16-9',
            '.aspect-ratio-4-3',
            '.aspect-ratio-1-1',
            '.aspect-ratio-content'
        ]
        
        for utility in aspect_ratio_utilities:
            assert utility in content, f"Aspect ratio utility {utility} not found"

    def test_responsive_touch_utilities_defined(self):
        """Test that responsive touch utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for touch utilities
        touch_utilities = [
            '.touch-target',
            '.no-tap-highlight'
        ]
        
        for utility in touch_utilities:
            assert utility in content, f"Touch utility {utility} not found"

    def test_dashboard_responsive_layout_defined(self):
        """Test that dashboard responsive layout is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        # Check for dashboard responsive layout
        assert '.dashboard-stats' in content
        assert 'grid-template-columns: 1fr' in content  # Mobile-first

    def test_portfolio_responsive_layout_defined(self):
        """Test that portfolio responsive layout is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        # Check for portfolio responsive layout
        assert '.portfolio-summary' in content
        assert '.portfolio-charts' in content

    def test_responsive_width_utilities_defined(self):
        """Test that responsive width utilities are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for width utilities
        width_utilities = [
            '.w-responsive-full',
            '.w-responsive-half',
            '.w-responsive-third',
            '.w-responsive-quarter'
        ]
        
        for utility in width_utilities:
            assert utility in content, f"Width utility {utility} not found"

    def test_responsive_height_utilities_defined(self):
        """Test that responsive height utilities are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for height utilities
        height_utilities = [
            '.h-responsive-auto',
            '.h-responsive-full',
            '.h-responsive-screen',
            '.h-responsive-min-screen'
        ]
        
        for utility in height_utilities:
            assert utility in content, f"Height utility {utility} not found"

    def test_responsive_border_radius_utilities_defined(self):
        """Test that responsive border radius utilities are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for border radius utilities
        border_radius_utilities = [
            '.rounded-responsive-sm',
            '.rounded-responsive-md',
            '.rounded-responsive-lg',
            '.rounded-responsive-xl'
        ]
        
        for utility in border_radius_utilities:
            assert utility in content, f"Border radius utility {utility} not found"

    def test_responsive_shadow_utilities_defined(self):
        """Test that responsive shadow utilities are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for shadow utilities
        shadow_utilities = [
            '.shadow-responsive-none',
            '.shadow-responsive-sm',
            '.shadow-responsive-md',
            '.shadow-responsive-lg'
        ]
        
        for utility in shadow_utilities:
            assert utility in content, f"Shadow utility {utility} not found"

    def test_responsive_margin_utilities_defined(self):
        """Test that responsive margin utilities are defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for margin utilities
        margin_utilities = [
            '.mar-responsive-xs',
            '.mar-responsive-sm',
            '.mar-responsive-md',
            '.mar-responsive-lg',
            '.mar-responsive-xl',
            '.mar-responsive-2xl'
        ]
        
        for utility in margin_utilities:
            assert utility in content, f"Margin utility {utility} not found"

    def test_touch_target_minimum_size(self):
        """Test that touch targets are at least 44x44px."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for 44px minimum touch target
        assert 'min-height: 44px' in content
        assert 'min-width: 44px' in content

    def test_smooth_scrolling_defined(self):
        """Test that smooth scrolling is defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for smooth scrolling
        assert 'scroll-behavior: smooth' in content

    def test_momentum_scrolling_defined(self):
        """Test that momentum scrolling is defined for mobile."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for momentum scrolling
        assert '-webkit-overflow-scrolling: touch' in content

    def test_responsive_print_utilities_defined(self):
        """Test that responsive print utilities are defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for print utilities
        assert '@media print' in content
        assert '.no-print' in content
        assert '.print-only' in content


class TestResponsiveGridSystem:
    """Test responsive grid system implementation."""

    def test_grid_auto_fit_defined(self):
        """Test that grid auto-fit is defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        assert '.grid-auto' in content
        assert 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))' in content

    def test_grid_columns_responsive(self):
        """Test that grid columns are responsive."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        # Check for responsive grid columns
        assert 'grid-template-columns: 1fr' in content  # Mobile
        assert 'grid-template-columns: repeat(2, 1fr)' in content  # Tablet
        assert 'grid-template-columns: repeat(3, 1fr)' in content  # Small Desktop
        assert 'grid-template-columns: repeat(4, 1fr)' in content  # Desktop


class TestResponsiveTypography:
    """Test responsive typography implementation."""

    def test_heading_sizes_responsive(self):
        """Test that heading sizes are responsive."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive heading sizes
        assert 'h1' in content
        assert 'h2' in content
        assert 'h3' in content
        assert 'font-size' in content

    def test_body_font_size_responsive(self):
        """Test that body font size is responsive."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        # Check for responsive body font size
        assert 'body' in content
        assert 'font-size: 16px' in content  # Default body font size


class TestResponsiveSpacing:
    """Test responsive spacing implementation."""

    def test_padding_responsive_defined(self):
        """Test that responsive padding is defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        assert '.p-responsive' in content
        assert '.px-responsive' in content
        assert '.py-responsive' in content

    def test_margin_responsive_defined(self):
        """Test that responsive margin is defined."""
        with open('static/css/components.css', 'r') as f:
            content = f.read()
        
        assert '.m-responsive' in content
        assert '.mx-responsive' in content
        assert '.my-responsive' in content

    def test_gap_responsive_defined(self):
        """Test that responsive gap is defined."""
        with open('static/css/design-system.css', 'r') as f:
            content = f.read()
        
        assert '.space-responsive-xs' in content
        assert '.space-responsive-md' in content
        assert '.space-responsive-xl' in content
