"""
Custom Exception Classes
Application-specific exceptions for better error handling
"""


class ValidationError(Exception):
    """Raised when user input validation fails"""
    pass


class BusinessLogicError(Exception):
    """Raised when business rule violations occur"""
    pass


class InsufficientFundsError(BusinessLogicError):
    """Raised when wallet balance is insufficient for a transaction"""
    pass


class InsufficientSharesError(BusinessLogicError):
    """Raised when user doesn't own enough shares for a sell order"""
    pass


class ExternalAPIError(Exception):
    """Raised when external API calls fail (yfinance, Twitter, etc.)"""
    pass


class StockNotFoundError(ValidationError):
    """Raised when a stock symbol is not found"""
    pass
