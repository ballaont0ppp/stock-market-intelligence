"""Configuration management for diagram generation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml
import os
import logging

from .types import DiagramType, DetailLevel
from .exceptions import ConfigurationError

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration for diagram generation."""
    
    # Diagram types to generate
    enabled_diagrams: List[DiagramType] = field(default_factory=lambda: list(DiagramType))
    
    # Detail level for each diagram type
    detail_levels: Dict[DiagramType, DetailLevel] = field(default_factory=dict)
    
    # File/directory exclusion patterns (glob patterns)
    exclusion_patterns: List[str] = field(default_factory=lambda: [
        "*/venv/*",
        "*/env/*",
        "*/__pycache__/*",
        "*/node_modules/*",
        "*/.git/*",
        "*/migrations/*",
        "*/tests/*",
        "*/test_*",
    ])
    
    # Output directory for generated diagrams
    output_dir: str = "diagrams"
    
    # Source directory to analyze
    source_dir: str = "."
    
    # Whether to create backups before overwriting
    create_backups: bool = True
    
    # Whether to preserve manual edits
    preserve_manual_edits: bool = True
    
    # Maximum depth for directory traversal
    max_depth: int = 10
    
    # Custom templates (not implemented yet)
    custom_templates: Dict[str, str] = field(default_factory=dict)
    
    def get_detail_level(self, diagram_type: DiagramType) -> DetailLevel:
        """Get detail level for a specific diagram type."""
        return self.detail_levels.get(diagram_type, DetailLevel.NORMAL)
    
    def is_diagram_enabled(self, diagram_type: DiagramType) -> bool:
        """Check if a diagram type is enabled."""
        return diagram_type in self.enabled_diagrams


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self):
        self._config: Optional[Config] = None
    
    def load_config(self, config_path: str) -> Config:
        """Load configuration from file."""
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}",
                {"path": config_path}
            )
        
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {path.suffix}",
                        {"path": config_path}
                    )
            
            self._config = self._parse_config(data)
            return self._config
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                f"Error loading configuration: {str(e)}",
                {"path": config_path, "error": str(e)}
            )
    
    def _parse_config(self, data: dict) -> Config:
        """Parse configuration data into Config object."""
        config = Config()
        
        # Parse enabled diagrams
        if 'enabled_diagrams' in data:
            try:
                config.enabled_diagrams = [
                    DiagramType(dt) for dt in data['enabled_diagrams']
                ]
            except ValueError as e:
                raise ConfigurationError(
                    f"Invalid diagram type in configuration: {str(e)}",
                    {"enabled_diagrams": data['enabled_diagrams']}
                )
        
        # Parse detail levels
        if 'detail_levels' in data:
            try:
                config.detail_levels = {
                    DiagramType(dt): DetailLevel(level)
                    for dt, level in data['detail_levels'].items()
                }
            except ValueError as e:
                raise ConfigurationError(
                    f"Invalid detail level in configuration: {str(e)}",
                    {"detail_levels": data['detail_levels']}
                )
        
        # Parse other settings
        if 'exclusion_patterns' in data:
            config.exclusion_patterns = data['exclusion_patterns']
        
        if 'output_dir' in data:
            config.output_dir = data['output_dir']
        
        if 'source_dir' in data:
            config.source_dir = data['source_dir']
        
        if 'create_backups' in data:
            config.create_backups = bool(data['create_backups'])
        
        if 'preserve_manual_edits' in data:
            config.preserve_manual_edits = bool(data['preserve_manual_edits'])
        
        if 'max_depth' in data:
            config.max_depth = int(data['max_depth'])
        
        return config
    
    def get_config(self) -> Config:
        """Get current configuration."""
        if self._config is None:
            self._config = Config()  # Return default config
        return self._config
    
    def get_enabled_diagrams(self) -> List[DiagramType]:
        """Get list of enabled diagram types."""
        return self.get_config().enabled_diagrams
    
    def get_exclusion_patterns(self) -> List[str]:
        """Get file/directory exclusion patterns."""
        return self.get_config().exclusion_patterns
    
    def get_detail_level(self, diagram_type: DiagramType) -> DetailLevel:
        """Get detail level for diagram type."""
        return self.get_config().get_detail_level(diagram_type)
    
    def validate_config(self, config: Config) -> None:
        """Validate configuration."""
        # Check output directory is valid
        if not config.output_dir:
            raise ConfigurationError(
                "Output directory cannot be empty",
                {"output_dir": config.output_dir}
            )
        
        # Check source directory is valid
        if not config.source_dir:
            raise ConfigurationError(
                "Source directory cannot be empty",
                {"source_dir": config.source_dir}
            )
        
    
    def validate_config(self, config: Config, strict: bool = False) -> None:
        """Validate configuration with comprehensive checks.
        
        Args:
            config: Configuration to validate
            strict: If True, treat warnings as errors
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        validation_errors = []
        validation_warnings = []
        
        # Check output directory is valid
        if not config.output_dir:
            validation_errors.append("Output directory cannot be empty")
        else:
            try:
                output_path = Path(config.output_dir)
                # Check if parent directory exists and is writable
                if not output_path.parent.exists():
                    validation_warnings.append(f"Output directory parent does not exist: {output_path.parent}")
                elif not os.access(output_path.parent, os.W_OK):
                    validation_errors.append(f"Output directory is not writable: {output_path}")
            except Exception as e:
                validation_errors.append(f"Invalid output directory format: {str(e)}")
        
        # Check source directory is valid
        if not config.source_dir:
            validation_errors.append("Source directory cannot be empty")
        else:
            try:
                source_path = Path(config.source_dir)
                if not source_path.exists():
                    validation_errors.append(f"Source directory does not exist: {source_path}")
                elif not source_path.is_dir():
                    validation_errors.append(f"Source path is not a directory: {source_path}")
                elif not os.access(source_path, os.R_OK):
                    validation_errors.append(f"Source directory is not readable: {source_path}")
            except Exception as e:
                validation_errors.append(f"Invalid source directory format: {str(e)}")
        
        # Check max depth is positive
        if config.max_depth <= 0:
            validation_errors.append("Max depth must be positive")
        elif config.max_depth > 20:
            validation_warnings.append(f"Max depth is very high ({config.max_depth}), may cause performance issues")
        
        # Check enabled diagrams
        if not config.enabled_diagrams:
            validation_warnings.append("No diagram types enabled - no diagrams will be generated")
        else:
            # Check if all diagram types are valid
            all_diagram_types = set(DiagramType)
            enabled_types = set(config.enabled_diagrams)
            
            if not enabled_types.issubset(all_diagram_types):
                invalid_types = enabled_types - all_diagram_types
                validation_errors.append(f"Invalid diagram types: {invalid_types}")
        
        # Check detail levels
        for diagram_type, detail_level in config.detail_levels.items():
            if detail_level not in [DetailLevel.MINIMAL, DetailLevel.NORMAL, DetailLevel.DETAILED]:
                validation_errors.append(f"Invalid detail level for {diagram_type.value}: {detail_level}")
        
        # Check exclusion patterns
        for pattern in config.exclusion_patterns:
            if not pattern or not isinstance(pattern, str):
                validation_errors.append("Exclusion patterns must be non-empty strings")
                break
            # Test pattern validity
            try:
                import fnmatch
                # Just test that it doesn't crash
                fnmatch.fnmatch("test_file.py", pattern)
            except Exception as e:
                validation_warnings.append(f"Exclusion pattern may be invalid: {pattern} ({str(e)})")
        
        # Report validation results
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in validation_errors)
            raise ConfigurationError(error_msg, {
                "errors": validation_errors,
                "warnings": validation_warnings
            })
        
        if validation_warnings and strict:
            warning_msg = "Configuration validation warnings (treated as errors in strict mode):\n" + "\n".join(f"  - {warning}" for warning in validation_warnings)
            raise ConfigurationError(warning_msg, {"warnings": validation_warnings})
        elif validation_warnings:
            # Log warnings but don't fail
            for warning in validation_warnings:
                logger.warning(f"Config validation warning: {warning}")
    
    def validate_config_file(self, config_path: str, strict: bool = False) -> Dict[str, any]:
        """Validate a configuration file.
        
        Args:
            config_path: Path to configuration file
            strict: If True, treat warnings as errors
            
        Returns:
            Dictionary with validation results
        """
        try:
            config = self.load_config(config_path)
            self.validate_config(config, strict=strict)
            
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "config": config
            }
        except ConfigurationError as e:
            return {
                "valid": False,
                "errors": e.details.get("errors", [str(e)]),
                "warnings": e.details.get("warnings", []),
                "config": None
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Unexpected error during validation: {str(e)}"],
                "warnings": [],
                "config": None
            }
    
    def get_config_schema(self) -> Dict[str, any]:
        """Get the configuration schema for documentation.
        
        Returns:
            Dictionary representing the configuration schema
        """
        return {
            "enabled_diagrams": {
                "type": "list",
                "items": {"type": "string", "enum": [dt.value for dt in DiagramType]},
                "description": "List of diagram types to generate"
            },
            "detail_levels": {
                "type": "object",
                "description": "Detail level for each diagram type"
            },
            "exclusion_patterns": {
                "type": "list",
                "items": {"type": "string"},
                "description": "File/directory patterns to exclude from analysis"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save generated diagrams"
            },
            "source_dir": {
                "type": "string",
                "description": "Source directory to analyze"
            },
            "create_backups": {
                "type": "boolean",
                "description": "Whether to create backups before overwriting"
            },
            "preserve_manual_edits": {
                "type": "boolean",
                "description": "Whether to preserve manual edits in diagrams"
            },
            "max_depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "description": "Maximum directory depth to traverse"
            }
        }
        # Check max depth is positive
        if config.max_depth <= 0:
            raise ConfigurationError(
                "Max depth must be positive",
                {"max_depth": config.max_depth}
            )
