"""
Tests for mobile-optimized forms.
Tests verify that forms have proper input types, mobile keyboards, and touch-friendly controls.

**Feature: mobile-pwa, Property 5: Mobile keyboard optimization**
**Validates: Requirements 4.3**
"""

import pytest


class TestAuthFormsInputTypes:
    """Test authentication forms have proper input types for mobile keyboards."""

    def test_registration_email_input_type(self):
        """Test that registration email field has email input type."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'email'" in content
        assert "'inputmode': 'email'" in content

    def test_registration_password_input_type(self):
        """Test that registration password field has password input type."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "PasswordField" in content
        assert "'autocomplete': 'new-password'" in content

    def test_login_email_input_type(self):
        """Test that login email field has email input type."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'email'" in content

    def test_login_password_autocomplete(self):
        """Test that login password field has current-password autocomplete."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'autocomplete': 'current-password'" in content

    def test_profile_form_has_form_controls(self):
        """Test that profile form has form-control classes."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-control'" in content
        assert "'class': 'form-select'" in content
        assert "'class': 'form-check-input'" in content


class TestOrderFormsInputTypes:
    """Test order forms have proper input types for mobile keyboards."""

    def test_buy_order_symbol_input_type(self):
        """Test that buy order symbol field has proper input type."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content
        assert "'pattern': '[A-Z]{1,10}'" in content

    def test_buy_order_quantity_input_type(self):
        """Test that buy order quantity field has number input type."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content
        assert "'inputmode': 'numeric'" in content

    def test_sell_order_symbol_input_type(self):
        """Test that sell order symbol field has proper input type."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content

    def test_sell_order_quantity_input_type(self):
        """Test that sell order quantity field has number input type."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content

    def test_order_filter_form_has_select_fields(self):
        """Test that order filter form has form-select classes."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-select'" in content
        assert "'aria-label'" in content


class TestPortfolioFormsInputTypes:
    """Test portfolio forms have proper input types for mobile keyboards."""

    def test_deposit_amount_input_type(self):
        """Test that deposit amount field has decimal input type."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content
        assert "'inputmode': 'decimal'" in content
        assert "'step': '0.01'" in content

    def test_deposit_description_textarea(self):
        """Test that deposit description field is a textarea."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "'rows': '3'" in content
        assert "'class': 'form-control'" in content

    def test_withdraw_amount_input_type(self):
        """Test that withdraw amount field has decimal input type."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content
        assert "'inputmode': 'decimal'" in content

    def test_withdraw_description_textarea(self):
        """Test that withdraw description field is a textarea."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "'rows': '3'" in content


class TestPredictionFormsInputTypes:
    """Test prediction forms have proper input types for mobile keyboards."""

    def test_prediction_symbol_input_type(self):
        """Test that prediction symbol field has proper input type."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content
        assert "'pattern': '[A-Z]{1,10}'" in content

    def test_prediction_models_select_field(self):
        """Test that prediction models field is a select field."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-select'" in content
        assert "'aria-label'" in content

    def test_forecast_symbol_input_type(self):
        """Test that forecast symbol field has proper input type."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content

    def test_forecast_days_input_type(self):
        """Test that forecast days field has number input type."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content
        assert "'inputmode': 'numeric'" in content

    def test_forecast_models_select_field(self):
        """Test that forecast models field is a select field."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-select'" in content


class TestDividendFormsInputTypes:
    """Test dividend forms have proper input types for mobile keyboards."""

    def test_dividend_symbol_input_type(self):
        """Test that dividend symbol field has proper input type."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content
        assert "'pattern': '[A-Z]{1,10}'" in content

    def test_dividend_amount_input_type(self):
        """Test that dividend amount field has decimal input type."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'number'" in content
        assert "'inputmode': 'decimal'" in content

    def test_dividend_date_input_type(self):
        """Test that dividend date fields have date input type."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        assert "'type': 'date'" in content
        assert "'inputmode': 'none'" in content

    def test_dividend_type_select_field(self):
        """Test that dividend type field is a select field."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-select'" in content


class TestFormAccessibility:
    """Test that forms have accessibility attributes."""

    def test_forms_have_aria_labels(self):
        """Test that select fields have aria-label attributes."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'aria-label'" in content

    def test_forms_have_placeholders(self):
        """Test that form fields have placeholder text."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'placeholder'" in content

    def test_forms_have_autocomplete(self):
        """Test that form fields have autocomplete attributes."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'autocomplete'" in content


class TestFormClasses:
    """Test that forms have proper Bootstrap classes."""

    def test_forms_have_form_control_class(self):
        """Test that text inputs have form-control class."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-control'" in content

    def test_forms_have_form_select_class(self):
        """Test that select fields have form-select class."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-select'" in content

    def test_forms_have_form_check_input_class(self):
        """Test that checkboxes have form-check-input class."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'class': 'form-check-input'" in content


class TestMobileKeyboardOptimization:
    """Test mobile keyboard optimization.
    
    **Feature: mobile-pwa, Property 5: Mobile keyboard optimization**
    **Validates: Requirements 4.3**
    """

    def test_email_fields_trigger_email_keyboard(self):
        """Test that email fields trigger email keyboard on mobile."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        # Email fields should have type='email' and inputmode='email'
        assert "'type': 'email'" in content
        assert "'inputmode': 'email'" in content

    def test_number_fields_trigger_numeric_keyboard(self):
        """Test that number fields trigger numeric keyboard on mobile."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        # Number fields should have type='number' and inputmode='numeric'
        assert "'type': 'number'" in content
        assert "'inputmode': 'numeric'" in content

    def test_decimal_fields_trigger_decimal_keyboard(self):
        """Test that decimal fields trigger decimal keyboard on mobile."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        # Decimal fields should have type='number' and inputmode='decimal'
        assert "'type': 'number'" in content
        assert "'inputmode': 'decimal'" in content

    def test_text_fields_have_inputmode(self):
        """Test that text fields have inputmode attribute."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'inputmode': 'text'" in content

    def test_date_fields_use_native_picker(self):
        """Test that date fields use native date picker."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        # Date fields should have type='date'
        assert "'type': 'date'" in content

    def test_password_fields_have_autocomplete(self):
        """Test that password fields have autocomplete attributes."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "'autocomplete': 'new-password'" in content
        assert "'autocomplete': 'current-password'" in content


class TestFormValidation:
    """Test that forms have proper validation attributes."""

    def test_number_fields_have_min_max(self):
        """Test that number fields have min/max attributes."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'min': '1'" in content

    def test_decimal_fields_have_step(self):
        """Test that decimal fields have step attribute."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "'step': '0.01'" in content

    def test_text_fields_have_pattern(self):
        """Test that text fields have pattern attribute for validation."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "'pattern': '[A-Z]{1,10}'" in content


class TestFormDocumentation:
    """Test that forms have proper documentation."""

    def test_auth_forms_documented(self):
        """Test that auth forms have documentation."""
        with open('app/forms/auth_forms.py', 'r') as f:
            content = f.read()
        
        assert "Mobile-optimized" in content
        assert "mobile keyboards" in content

    def test_order_forms_documented(self):
        """Test that order forms have documentation."""
        with open('app/forms/order_forms.py', 'r') as f:
            content = f.read()
        
        assert "Mobile-optimized" in content

    def test_portfolio_forms_documented(self):
        """Test that portfolio forms have documentation."""
        with open('app/forms/portfolio_forms.py', 'r') as f:
            content = f.read()
        
        assert "Mobile-optimized" in content

    def test_prediction_forms_documented(self):
        """Test that prediction forms have documentation."""
        with open('app/forms/prediction_forms.py', 'r') as f:
            content = f.read()
        
        assert "Mobile-optimized" in content

    def test_dividend_forms_documented(self):
        """Test that dividend forms have documentation."""
        with open('app/forms/dividend_forms.py', 'r') as f:
            content = f.read()
        
        assert "Mobile-optimized" in content
        assert "date pickers" in content
