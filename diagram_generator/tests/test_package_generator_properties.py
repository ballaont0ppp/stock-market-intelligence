"""Property-based tests for PackageDiagramGenerator.

**Feature: diagram-generation-system, Property 42: Directory structure preservation**
**Validates: Requirements 14.1**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path

from diagram_generator.generators.package_generator import PackageDiagramGenerator
from diagram_generator.core.types import AnalysisData, FileAnalysis


@st.composite
def file_paths_strategy(draw):
    """Generate realistic file paths."""
    base_dirs = ['app', 'src', 'lib']
    subdirs = ['models', 'services', 'routes', 'utils', 'forms']
    
    base = draw(st.sampled_from(base_dirs))
    subdir = draw(st.sampled_from(subdirs))
    filename = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Lu'))))
    
    return f"{base}/{subdir}/{filename}.py"


class TestPackageGeneratorProperties:
    """Property-based tests for PackageDiagramGenerator."""
    
    @given(st.lists(file_paths_strategy(), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_directory_structure_preservation(self, file_paths):
        """Property 42: Directory structure preservation.
        
        For any set of file paths, all directory structures should be represented in the package diagram.
        
        **Validates: Requirements 14.1**
        """
        generator = PackageDiagramGenerator()
        
        # Create analysis data
        files = {}
        for file_path in file_paths:
            files[file_path] = FileAnalysis(
                file_path=file_path,
                imports=[],
                classes=[],
                functions=[],
                module_docstring=None
            )
        
        analysis_data = AnalysisData(files=files)
        
        # Generate diagram
        diagram = generator.generate(analysis_data)
        
        # Extract expected packages
        expected_packages = set()
        for file_path in file_paths:
            path = Path(file_path)
            if len(path.parts) > 1:
                package = '/'.join(path.parts[:-1])
                expected_packages.add(package)
        
        # Check that all packages appear in the diagram
        diagram_content = diagram.mermaid_code
        for package in expected_packages:
            package_id = package.replace('/', '_')
            assert package_id in diagram_content or package in diagram_content, \
                f"Package {package} not found in package diagram"
