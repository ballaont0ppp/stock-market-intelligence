#!/usr/bin/env python3
"""Test script to verify diagram generation works."""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_generator.core.config import ConfigManager, Config
from diagram_generator.core.orchestrator import DiagramOrchestrator
from diagram_generator.core.types import DiagramType

def test_diagram_generation():
    """Test basic diagram generation functionality."""
    try:
        # Create a simple configuration
        config = Config()
        config.source_dir = "diagram_generator"
        config.output_dir = "test_output"
        config.enabled_diagrams = [DiagramType.ARCHITECTURE]
        
        # Create orchestrator
        orchestrator = DiagramOrchestrator(config)
        
        # Test generation
        print("Testing diagram generation...")
        result = orchestrator.generate_all_diagrams(config.source_dir)
        
        print(f"Generated {len(result.diagrams)} diagrams")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        
        if result.errors:
            print("Errors encountered:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.diagrams:
            print("Successfully generated diagrams:")
            for diagram in result.diagrams:
                print(f"  - {diagram.title}")
        
        return len(result.errors) == 0
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_diagram_generation()
    if success:
        print("\n✅ Diagram generation test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Diagram generation test FAILED")
        sys.exit(1)