"""
Tests for mobile-optimized tables and charts.
Tests verify that tables have horizontal scrolling, charts are responsive, and portfolio cards are mobile-friendly.

**Feature: mobile-pwa, Property 1: Responsive layout consistency**
**Validates: Requirements 1.4**
"""

import pytest
import os


class TestMobileTableCSS:
    """Test mobile-optimized table CSS."""

    def test_table_responsive_mobile_class_exists(self):
        """Test that table-responsive-mobile class is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-responsive-mobile' in content

    def test_table_horizontal_scrolling(self):
        """Test that tables have horizontal scrolling enabled."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'overflow-x: auto' in content
        assert '-webkit-overflow-scrolling: touch' in content

    def test_table_sticky_header(self):
        """Test that table headers are sticky."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'position: sticky' in content
        assert 'top: 0' in content

    def test_table_header_styling(self):
        """Test that table headers have proper styling."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-responsive-mobile th' in content
        assert 'white-space: nowrap' in content

    def test_table_row_hover_effect(self):
        """Test that table rows have hover effect."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-responsive-mobile tbody tr:hover' in content

    def test_table_card_mobile_alternative(self):
        """Test that card-based table display exists for mobile."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-card-mobile' in content
        assert '.card-row' in content
        assert '.card-label' in content
        assert '.card-value' in content

    def test_table_card_mobile_responsive(self):
        """Test that card table is shown on mobile."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 767px)' in content
        assert 'display: block' in content


class TestMobileChartCSS:
    """Test mobile-optimized chart CSS."""

    def test_chart_container_mobile_class_exists(self):
        """Test that chart-container-mobile class is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.chart-container-mobile' in content

    def test_chart_responsive_sizing(self):
        """Test that charts have responsive sizing."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'max-width: 100%' in content
        assert 'height: auto' in content

    def test_chart_mobile_breakpoints(self):
        """Test that charts have mobile breakpoints."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 576px)' in content
        assert '@media (min-width: 577px) and (max-width: 767px)' in content
        assert '@media (min-width: 768px)' in content

    def test_chart_loading_state(self):
        """Test that chart has loading state."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.chart-loading' in content
        assert '@keyframes spin' in content

    def test_chart_error_state(self):
        """Test that chart has error state."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.chart-error' in content

    def test_chart_touch_area(self):
        """Test that chart has touch-optimized area."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.chart-touch-area' in content
        assert 'touch-action: manipulation' in content


class TestPortfolioSummaryCards:
    """Test mobile-friendly portfolio summary cards."""

    def test_portfolio_summary_card_class_exists(self):
        """Test that portfolio-summary-card class is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.portfolio-summary-card' in content

    def test_portfolio_card_styling(self):
        """Test that portfolio cards have proper styling."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.portfolio-summary-card-header' in content
        assert '.portfolio-summary-card-title' in content
        assert '.portfolio-summary-card-content' in content

    def test_portfolio_card_grid(self):
        """Test that portfolio cards use responsive grid."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.portfolio-cards-grid' in content
        assert 'display: grid' in content
        assert 'grid-template-columns: repeat(auto-fit' in content

    def test_portfolio_card_values(self):
        """Test that portfolio card values have styling."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.portfolio-summary-card-value' in content
        assert '.portfolio-summary-card-value.positive' in content
        assert '.portfolio-summary-card-value.negative' in content

    def test_portfolio_card_responsive(self):
        """Test that portfolio cards are responsive."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 576px)' in content
        assert 'grid-template-columns: 1fr' in content


class TestMobileTablesChartsJS:
    """Test mobile tables and charts JavaScript."""

    def test_mobile_tables_charts_js_exists(self):
        """Test that mobile tables/charts JavaScript file exists."""
        assert os.path.exists('static/js/mobile-tables-charts.js')

    def test_mobile_tables_charts_class_defined(self):
        """Test that MobileTablesCharts class is defined."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'class MobileTablesCharts' in content

    def test_mobile_tables_charts_init_method(self):
        """Test that MobileTablesCharts has init method."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'init()' in content

    def test_mobile_tables_charts_init_tables(self):
        """Test that MobileTablesCharts initializes tables."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'initTables()' in content

    def test_mobile_tables_charts_init_charts(self):
        """Test that MobileTablesCharts initializes charts."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'initCharts()' in content

    def test_mobile_tables_charts_scroll_indicator(self):
        """Test that MobileTablesCharts adds scroll indicator."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'addScrollIndicator' in content

    def test_mobile_tables_charts_touch_interactions(self):
        """Test that MobileTablesCharts adds touch interactions."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'addTableTouchInteractions' in content
        assert 'addChartTouchInteractions' in content

    def test_mobile_tables_charts_responsive_height(self):
        """Test that MobileTablesCharts sets responsive chart height."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'setChartHeight' in content

    def test_mobile_tables_charts_loading_state(self):
        """Test that MobileTablesCharts handles loading state."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'showChartLoading' in content

    def test_mobile_tables_charts_error_state(self):
        """Test that MobileTablesCharts handles error state."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'showChartError' in content

    def test_mobile_tables_charts_export_data(self):
        """Test that MobileTablesCharts can export table data."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'exportTableData' in content

    def test_mobile_tables_charts_dom_ready(self):
        """Test that MobileTablesCharts initializes on DOM ready."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'DOMContentLoaded' in content


class TestTableResponsiveness:
    """Test table responsiveness on mobile."""

    def test_table_wrapper_class_exists(self):
        """Test that table-wrapper class is defined."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-wrapper' in content

    def test_table_wrapper_scrollable_indicator(self):
        """Test that table wrapper has scrollable indicator."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-wrapper.scrollable' in content

    def test_table_scroll_indicator_gradient(self):
        """Test that scroll indicator has gradient."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'linear-gradient' in content

    def test_table_min_width_columns(self):
        """Test that table columns have minimum width."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'min-width: 100px' in content


class TestChartResponsiveness:
    """Test chart responsiveness on mobile.
    
    **Feature: mobile-pwa, Property 1: Responsive layout consistency**
    **Validates: Requirements 1.4**
    """

    def test_chart_small_screen_height(self):
        """Test that charts have appropriate height on small screens."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 576px)' in content
        assert 'height: 250px' in content

    def test_chart_medium_screen_height(self):
        """Test that charts have appropriate height on medium screens."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (min-width: 577px) and (max-width: 767px)' in content
        assert 'height: 300px' in content

    def test_chart_large_screen_height(self):
        """Test that charts have appropriate height on large screens."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (min-width: 768px)' in content
        assert 'height: 400px' in content

    def test_chart_max_width_constraint(self):
        """Test that charts have max-width constraint."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'max-width: 100%' in content


class TestTableCardDisplay:
    """Test card-based table display for mobile."""

    def test_card_display_hidden_by_default(self):
        """Test that card display is hidden by default."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-card-mobile' in content
        assert 'display: none' in content

    def test_card_display_shown_on_mobile(self):
        """Test that card display is shown on mobile."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '@media (max-width: 767px)' in content
        assert '.table-card-mobile' in content
        assert 'display: block' in content

    def test_card_structure(self):
        """Test that cards have proper structure."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '.table-card-mobile .card' in content
        assert '.table-card-mobile .card-header' in content
        assert '.table-card-mobile .card-body' in content
        assert '.table-card-mobile .card-row' in content

    def test_card_row_layout(self):
        """Test that card rows have proper layout."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert 'display: flex' in content
        assert 'justify-content: space-between' in content


class TestTouchOptimization:
    """Test touch optimization for tables and charts."""

    def test_table_touch_feedback(self):
        """Test that tables have touch feedback."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'touchstart' in content
        assert 'touchend' in content

    def test_chart_touch_feedback(self):
        """Test that charts have touch feedback."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'addChartTouchInteractions' in content

    def test_momentum_scrolling(self):
        """Test that momentum scrolling is enabled."""
        with open('static/css/pages.css', 'r') as f:
            content = f.read()
        
        assert '-webkit-overflow-scrolling: touch' in content


class TestDataExport:
    """Test data export functionality."""

    def test_export_table_data_method(self):
        """Test that tables can export data."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert 'exportTableData' in content

    def test_export_json_format(self):
        """Test that data can be exported as JSON."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert "format === 'json'" in content
        assert 'JSON.stringify' in content

    def test_export_csv_format(self):
        """Test that data can be exported as CSV."""
        with open('static/js/mobile-tables-charts.js', 'r') as f:
            content = f.read()
        
        assert "format === 'csv'" in content


class TestScriptIntegration:
    """Test that mobile tables/charts script is integrated."""

    def test_script_in_base_template(self):
        """Test that mobile tables/charts script is in base template."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        assert 'mobile-tables-charts.js' in content

    def test_script_loaded_before_main_js(self):
        """Test that mobile tables/charts script is loaded before main.js."""
        with open('app/templates/base.html', 'r') as f:
            content = f.read()
        
        mobile_pos = content.find('mobile-tables-charts.js')
        main_pos = content.find('main.js')
        
        assert mobile_pos > 0
        assert main_pos > 0
        assert mobile_pos < main_pos
