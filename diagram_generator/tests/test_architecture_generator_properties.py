"""Property-based tests for ArchitectureDiagramGenerator.

**Feature: diagram-generation-system, Property 1: Module completeness**
**Validates: Requirements 1.1**
"""

import pytest
from hypothesis import given, strategies as st, settings

from diagram_generator.generators.architecture_generator import ArchitectureDiagramGenerator
from diagram_generator.core.types import (
    AnalysisData,
    FileAnalysis,
    ImportInfo,
    ClassInfo,
    FunctionInfo,
)


# Strategies for generating test data
@st.composite
def file_analysis_strategy(draw):
    """Generate a FileAnalysis object."""
    num_imports = draw(st.integers(min_value=0, max_value=5))
    imports = [
        ImportInfo(
            module=draw(st.sampled_from(['app.models', 'app.services', 'flask', 'sqlalchemy'])),
            names=draw(st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=3)),
            is_from_import=draw(st.booleans())
        )
        for _ in range(num_imports)
    ]
    
    file_path = draw(st.text(min_size=1, max_size=50))
    
    return FileAnalysis(
        file_path=file_path,
        module_name=file_path.replace('/', '.').replace('.py', ''),
        imports=imports,
        classes=[],
        functions=[],
        docstring=None
    )


@st.composite
def analysis_data_strategy(draw):
    """Generate an AnalysisData object with multiple files."""
    num_files = draw(st.integers(min_value=1, max_value=10))
    
    file_analyses = []
    for i in range(num_files):
        file_path = f"app/{draw(st.sampled_from(['models', 'services', 'routes', 'utils']))}/file{i}.py"
        file_analysis = draw(file_analysis_strategy())
        file_analysis.file_path = file_path
        file_analysis.module_name = file_path.replace('/', '.').replace('.py', '')
        file_analyses.append(file_analysis)
    
    return AnalysisData(file_analyses=file_analyses)


class TestArchitectureGeneratorProperties:
    """Property-based tests for ArchitectureDiagramGenerator."""
    
    @given(analysis_data=analysis_data_strategy())
    @settings(max_examples=100)
    def test_module_completeness(self, analysis_data):
        """Property 1: Module completeness.
        
        For any analysis data, all modules in the input should appear in the generated diagram.
        
        **Validates: Requirements 1.1**
        """
        generator = ArchitectureDiagramGenerator()
        
        # Generate diagram
        diagram = generator.generate(analysis_data)
        
        # Extract module names from analysis data
        expected_modules = set()
        for file_analysis in analysis_data.file_analyses:
            module_name = generator._get_module_name(file_analysis.file_path)
            expected_modules.add(module_name)
        
        # Extract module names from diagram
        diagram_content = diagram.mermaid_code
        
        # Check that all expected modules appear in the diagram
        for module in expected_modules:
            assert module in diagram_content, \
                f"Module {module} from source files not found in architecture diagram"
    
    @given(analysis_data=analysis_data_strategy())
    @settings(max_examples=100)
    def test_diagram_has_valid_structure(self, analysis_data):
        """Property: Generated diagram has valid Mermaid structure.
        
        For any analysis data, the generated diagram should start with 'graph' declaration.
        """
        generator = ArchitectureDiagramGenerator()
        
        # Generate diagram
        diagram = generator.generate(analysis_data)
        
        # Check diagram structure
        assert diagram.mermaid_code.startswith('graph '), \
            "Architecture diagram should start with 'graph' declaration"
        assert diagram.diagram_type.name == 'ARCHITECTURE', \
            "Diagram type should be ARCHITECTURE"
    
    @given(analysis_data=analysis_data_strategy())
    @settings(max_examples=100)
    def test_source_files_tracked(self, analysis_data):
        """Property: All source files are tracked in diagram metadata.
        
        For any analysis data, all input files should be listed in the diagram's source_files.
        """
        generator = ArchitectureDiagramGenerator()
        
        # Generate diagram
        diagram = generator.generate(analysis_data)
        
        # Check that all source files are tracked
        expected_files = set(fa.file_path for fa in analysis_data.file_analyses)
        actual_files = set(diagram.source_files)
        
        assert expected_files == actual_files, \
            f"Source files mismatch. Expected: {expected_files}, Got: {actual_files}"
    
    @given(st.sampled_from(['app/routes/auth.py', 'app/services/user_service.py', 
                            'app/models/user.py', 'app/utils/helpers.py']))
    @settings(max_examples=100)
    def test_layer_identification(self, file_path):
        """Property 2: Layer identification.
        
        For any file path, the layer should be correctly identified based on directory structure.
        
        **Validates: Requirements 1.2**
        """
        generator = ArchitectureDiagramGenerator()
        layers = generator._identify_layers(AnalysisData(file_analyses=[]))
        
        # Determine expected layer
        layer = generator._determine_layer(file_path, layers)
        
        # Verify layer is one of the known layers
        valid_layers = {'presentation', 'business', 'data', 'infrastructure', 'other'}
        assert layer in valid_layers, \
            f"Layer {layer} is not a valid layer type"
        
        # Verify specific mappings
        if 'routes' in file_path or 'forms' in file_path:
            assert layer == 'presentation', \
                f"Routes/forms should be in presentation layer, got {layer}"
        elif 'services' in file_path:
            assert layer == 'business', \
                f"Services should be in business layer, got {layer}"
        elif 'models' in file_path:
            assert layer == 'data', \
                f"Models should be in data layer, got {layer}"
        elif 'utils' in file_path or 'jobs' in file_path:
            assert layer == 'infrastructure', \
                f"Utils/jobs should be in infrastructure layer, got {layer}"
