"""Custom exceptions for diagram generation."""

from typing import Any, Dict


class DiagramGenerationError(Exception):
    """Base exception for diagram generation errors."""
    
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)


class ParseError(DiagramGenerationError):
    """Error parsing source code."""
    pass


class AnalysisError(DiagramGenerationError):
    """Error analyzing code structure."""
    pass


class GenerationError(DiagramGenerationError):
    """Error generating diagram."""
    pass


class ValidationError(DiagramGenerationError):
    """Error validating generated diagram."""
    pass


class ConfigurationError(DiagramGenerationError):
    """Error in configuration."""
    pass


class FileIOError(DiagramGenerationError):
    """Error reading or writing files."""
    pass
