"""Pytest configuration and fixtures."""

import pytest
import tempfile
import yaml
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        'enabled_diagrams': ['architecture', 'er_diagram', 'class_diagram'],
        'detail_levels': {
            'architecture': 'normal',
            'er_diagram': 'detailed'
        },
        'exclusion_patterns': ['*/test/*', '*/__pycache__/*'],
        'output_dir': 'diagrams',
        'source_dir': '.',
        'create_backups': True,
        'preserve_manual_edits': True,
        'max_depth': 10
    }


@pytest.fixture
def config_file(temp_dir, sample_config_data):
    """Create a temporary configuration file."""
    config_path = temp_dir / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(sample_config_data, f)
    return config_path
