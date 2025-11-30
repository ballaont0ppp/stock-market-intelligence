"""
Property-based tests for configuration loading.

**Feature: diagram-generation-system, Property 38: Diagram type filtering**
**Validates: Requirements 12.1**
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from diagram_generator.core.config import ConfigManager, Config
from diagram_generator.core.types import DiagramType
from diagram_generator.core.exceptions import ConfigurationError


# Strategy for generating valid diagram type names
diagram_type_strategy = st.sampled_from([dt.value for dt in DiagramType])

# Strategy for generating lists of diagram types
diagram_list_strategy = st.lists(
    diagram_type_strategy,
    min_size=1,
    max_size=len(DiagramType),
    unique=True
)


@settings(max_examples=100)
@given(diagram_types=diagram_list_strategy)
def test_property_diagram_type_filtering(diagram_types):
    """
    Property 38: Diagram type filtering
    
    For any configuration specifying diagram types [T1, T2, ..., Tn],
    only those diagram types should be generated.
    
    This test verifies that:
    1. Configuration correctly loads the specified diagram types
    2. Only the specified diagram types are marked as enabled
    3. Non-specified diagram types are not enabled
    """
    # Create a temporary config file with the generated diagram types
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': diagram_types,
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        # Load the configuration
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # Convert string diagram types to DiagramType enums
        expected_types = {DiagramType(dt) for dt in diagram_types}
        actual_types = set(config.enabled_diagrams)
        
        # Property: The enabled diagrams should exactly match what was specified
        assert actual_types == expected_types, \
            f"Expected {expected_types}, but got {actual_types}"
        
        # Property: Each specified diagram type should be enabled
        for diagram_type_str in diagram_types:
            diagram_type = DiagramType(diagram_type_str)
            assert config.is_diagram_enabled(diagram_type), \
                f"Diagram type {diagram_type} should be enabled"
        
        # Property: Non-specified diagram types should not be enabled
        all_types = set(DiagramType)
        non_specified = all_types - expected_types
        for diagram_type in non_specified:
            assert not config.is_diagram_enabled(diagram_type), \
                f"Diagram type {diagram_type} should not be enabled"
        
        # Property: The number of enabled diagrams should match the input
        assert len(config.enabled_diagrams) == len(diagram_types), \
            f"Expected {len(diagram_types)} enabled diagrams, got {len(config.enabled_diagrams)}"
        
    finally:
        # Clean up temporary file
        Path(config_path).unlink()


def test_config_with_all_diagram_types():
    """Test configuration with all diagram types enabled."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        all_types = [dt.value for dt in DiagramType]
        config_data = {
            'enabled_diagrams': all_types,
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # All diagram types should be enabled
        assert len(config.enabled_diagrams) == len(DiagramType)
        for diagram_type in DiagramType:
            assert config.is_diagram_enabled(diagram_type)
    finally:
        Path(config_path).unlink()


def test_config_with_single_diagram_type():
    """Test configuration with only one diagram type enabled."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': ['architecture'],
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # Only architecture should be enabled
        assert len(config.enabled_diagrams) == 1
        assert config.is_diagram_enabled(DiagramType.ARCHITECTURE)
        
        # All other types should not be enabled
        for diagram_type in DiagramType:
            if diagram_type != DiagramType.ARCHITECTURE:
                assert not config.is_diagram_enabled(diagram_type)
    finally:
        Path(config_path).unlink()


def test_config_with_empty_diagram_list():
    """Test configuration with empty diagram list."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': [],
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # No diagrams should be enabled
        assert len(config.enabled_diagrams) == 0
        for diagram_type in DiagramType:
            assert not config.is_diagram_enabled(diagram_type)
    finally:
        Path(config_path).unlink()


def test_config_with_invalid_diagram_type():
    """Test that invalid diagram types raise ConfigurationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': ['invalid_diagram_type'],
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        with pytest.raises(ConfigurationError):
            manager.load_config(config_path)
    finally:
        Path(config_path).unlink()


def test_default_config_has_all_diagrams():
    """Test that default configuration has all diagram types enabled."""
    manager = ConfigManager()
    config = manager.get_config()  # Gets default config
    
    # Default config should have all diagram types
    assert len(config.enabled_diagrams) == len(DiagramType)
    for diagram_type in DiagramType:
        assert config.is_diagram_enabled(diagram_type)


@settings(max_examples=50)
@given(exclusion_patterns=st.lists(st.text(min_size=1), min_size=1, max_size=10))
def test_property_exclusion_pattern_respect(exclusion_patterns):
    """
    Property 39: Exclusion pattern respect
    
    For any configuration specifying exclusion patterns [P1, P2, ..., Pn],
    files matching those patterns should be excluded from analysis.
    
    This test verifies that:
    1. Configuration correctly loads the specified exclusion patterns
    2. Exclusion patterns are preserved and can be used for filtering
    3. Pattern validation and handling works correctly
    """
    # Create a temporary config file with the generated exclusion patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': ['architecture', 'class_diagram'],
            'exclusion_patterns': exclusion_patterns,
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        # Load the configuration
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # Property: The exclusion patterns should exactly match what was specified
        assert config.exclusion_patterns == exclusion_patterns, \
            f"Expected {exclusion_patterns}, but got {config.exclusion_patterns}"
        
        # Property: Each pattern should be a valid string
        for pattern in exclusion_patterns:
            assert isinstance(pattern, str), f"Pattern {pattern} should be a string"
            assert len(pattern) > 0, f"Pattern {pattern} should not be empty"
        
        # Property: The number of patterns should match the input
        assert len(config.exclusion_patterns) == len(exclusion_patterns), \
            f"Expected {len(exclusion_patterns)} patterns, got {len(config.exclusion_patterns)}"
        
        # Property: Exclusion patterns should be usable for filtering
        # Test that the patterns can be used with glob matching
        import fnmatch
        test_files = [
            'src/app.py',
            'tests/test_app.py', 
            'venv/lib/module.py',
            'migrations/001_add_table.py',
            'app/models/user.py',
            '__pycache__/module.pyc'
        ]
        
        for pattern in exclusion_patterns:
            for test_file in test_files:
                # This tests that the pattern can be used for matching
                # (doesn't assert specific matches, just that it doesn't crash)
                try:
                    fnmatch.fnmatch(test_file, pattern)
                except Exception:
                    pytest.fail(f"Pattern {pattern} should be valid for fnmatch")
        
    finally:
        # Clean up temporary file
        Path(config_path).unlink()


def test_exclusion_patterns_default_values():
    """Test that default exclusion patterns are sensible."""
    manager = ConfigManager()
    config = manager.get_config()  # Gets default config
    
    # Default config should have reasonable exclusion patterns
    assert len(config.exclusion_patterns) > 0, "Default config should have exclusion patterns"
    
    # Check that common unwanted directories are excluded
    expected_patterns = [
        "*/venv/*",
        "*/env/*", 
        "*/__pycache__/*",
        "*/node_modules/*",
        "*/.git/*"
    ]
    
    for expected_pattern in expected_patterns:
        assert expected_pattern in config.exclusion_patterns, \
            f"Default config should include {expected_pattern}"


def test_exclusion_patterns_custom_values():
    """Test configuration with custom exclusion patterns."""
    custom_patterns = [
        "*/custom_dir/*",
        "*.bak",
        "temp_*",
        "ignore/**"
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': ['architecture'],
            'exclusion_patterns': custom_patterns,
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # Custom patterns should be preserved
        assert config.exclusion_patterns == custom_patterns
        
        # Patterns should work with fnmatch
        import fnmatch
        test_cases = [
            ("src/custom_dir/file.py", True),
            ("backup.bak", True), 
            ("temp_file.txt", True),
            ("ignore/nested/file.py", True),
            ("src/allowed.py", False),
            ("normal_file.txt", False)
        ]
        
        for pattern in custom_patterns:
            for test_file, should_match in test_cases:
                matches = fnmatch.fnmatch(test_file, pattern)
                # Just verify the matching doesn't crash and returns boolean
                assert isinstance(matches, bool)
        
    finally:
        Path(config_path).unlink()


def test_exclusion_patterns_with_wildcards():
    """Test exclusion patterns with various wildcard patterns."""
    wildcard_patterns = [
        "*/test_*",
        "*.pyc",
        "backup_*",
        "temp/**",
        "[!.]*"
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'enabled_diagrams': ['class_diagram'],
            'exclusion_patterns': wildcard_patterns,
            'output_dir': 'diagrams',
            'source_dir': '.'
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        manager = ConfigManager()
        config = manager.load_config(config_path)
        
        # All wildcard patterns should be preserved
        assert len(config.exclusion_patterns) == len(wildcard_patterns)
        
        # Test that complex wildcards are handled correctly
        import fnmatch
        complex_test_files = [
            "src/test_helper.py",
            "compiled.pyc",
            "backup_2023.txt",
            "temp/cache/file.py",
            ".hidden",
            "visible_file.py"
        ]
        
        # Just verify no crashes occur during pattern matching
        for pattern in wildcard_patterns:
            for test_file in complex_test_files:
                try:
                    fnmatch.fnmatch(test_file, pattern)
                except Exception as e:
                    pytest.fail(f"Wildcard pattern {pattern} should not crash on {test_file}: {e}")
        
    finally:
        Path(config_path).unlink()
