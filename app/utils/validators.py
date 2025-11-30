"""
Input Validation Utilities
Provides validation functions for user inputs
"""
import re
from decimal import Decimal, InvalidOperation
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long (maximum 255 characters)"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def validate_amount(amount, min_value=0.01, max_value=1000000000) -> Tuple[bool, str]:
    """
    Validate monetary amount
    
    Args:
        amount: Amount to validate (can be string, int, float, or Decimal)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount is None:
        return False, "Amount is required"
    
    try:
        # Convert to Decimal for precise monetary calculations
        if isinstance(amount, str):
            amount = amount.strip()
            if not amount:
                return False, "Amount is required"
            # Remove currency symbols and commas
            amount = amount.replace('$', '').replace(',', '')
        
        decimal_amount = Decimal(str(amount))
        
        if decimal_amount < 0:
            return False, "Amount cannot be negative"
        
        if decimal_amount < Decimal(str(min_value)):
            return False, f"Amount must be at least ${min_value}"
        
        if decimal_amount > Decimal(str(max_value)):
            return False, f"Amount cannot exceed ${max_value:,.2f}"
        
        # Check decimal places (max 2 for currency)
        if decimal_amount.as_tuple().exponent < -2:
            return False, "Amount cannot have more than 2 decimal places"
        
        return True, ""
        
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid amount format"


def validate_quantity(quantity, min_value=1, max_value=1000000) -> Tuple[bool, str]:
    """
    Validate stock quantity
    
    Args:
        quantity: Quantity to validate (can be string or int)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if quantity is None:
        return False, "Quantity is required"
    
    try:
        # Convert to integer
        if isinstance(quantity, str):
            quantity = quantity.strip()
            if not quantity:
                return False, "Quantity is required"
            # Remove commas
            quantity = quantity.replace(',', '')
        
        int_quantity = int(quantity)
        
        if int_quantity < min_value:
            return False, f"Quantity must be at least {min_value}"
        
        if int_quantity > max_value:
            return False, f"Quantity cannot exceed {max_value:,}"
        
        # Check if it's a whole number
        if float(quantity) != int_quantity:
            return False, "Quantity must be a whole number"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "Invalid quantity format"


def validate_stock_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symbol:
        return False, "Stock symbol is required"
    
    symbol = symbol.strip().upper()
    
    if len(symbol) < 1:
        return False, "Stock symbol is required"
    
    if len(symbol) > 10:
        return False, "Stock symbol is too long (maximum 10 characters)"
    
    # Stock symbols should only contain letters and possibly dots
    if not re.match(r'^[A-Z.]+$', symbol):
        return False, "Stock symbol can only contain letters and dots"
    
    return True, ""


def validate_percentage(percentage, min_value=0, max_value=100) -> Tuple[bool, str]:
    """
    Validate percentage value
    
    Args:
        percentage: Percentage to validate (can be string, int, float, or Decimal)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if percentage is None:
        return False, "Percentage is required"
    
    try:
        # Convert to Decimal
        if isinstance(percentage, str):
            percentage = percentage.strip()
            if not percentage:
                return False, "Percentage is required"
            # Remove percentage symbol
            percentage = percentage.replace('%', '')
        
        decimal_percentage = Decimal(str(percentage))
        
        if decimal_percentage < Decimal(str(min_value)):
            return False, f"Percentage must be at least {min_value}%"
        
        if decimal_percentage > Decimal(str(max_value)):
            return False, f"Percentage cannot exceed {max_value}%"
        
        return True, ""
        
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid percentage format"


def validate_date_range(start_date, end_date) -> Tuple[bool, str]:
    """
    Validate date range
    
    Args:
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not start_date:
        return False, "Start date is required"
    
    if not end_date:
        return False, "End date is required"
    
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    return True, ""


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing potentially harmful characters
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def sanitize_sql_input(text: str) -> str:
    """
    Sanitize input to prevent SQL injection attempts
    
    Note: This is a defense-in-depth measure. Always use parameterized queries
    or SQLAlchemy ORM as the primary defense against SQL injection.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove SQL comment markers
    text = text.replace('--', '')
    text = text.replace('/*', '')
    text = text.replace('*/', '')
    
    # Remove semicolons (statement terminators)
    text = text.replace(';', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_alphanumeric(text: str, allow_spaces: bool = False) -> Tuple[bool, str]:
    """
    Validate that text contains only alphanumeric characters
    
    Args:
        text: Text to validate
        allow_spaces: Whether to allow spaces
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Input is required"
    
    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s]+$'
        error_msg = "Input can only contain letters, numbers, and spaces"
    else:
        pattern = r'^[a-zA-Z0-9]+$'
        error_msg = "Input can only contain letters and numbers"
    
    if not re.match(pattern, text):
        return False, error_msg
    
    return True, ""
