"""
Property-based tests for MetadataExtractor.

**Feature: diagram-generation-system, Property 40: Docstring extraction**
**Validates: Requirements 13.1**

**Feature: diagram-generation-system, Property 41: Type hint inclusion**
**Validates: Requirements 13.3**
"""

import pytest
import ast
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from diagram_generator.analyzers.metadata_extractor import MetadataExtractor
from diagram_generator.analyzers.code_analyzer import CodeAnalyzer


# Strategy for generating docstrings
docstring_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=126),
    min_size=10,
    max_size=200
).filter(lambda x: '"""' not in x and "'''" not in x)


def generate_class_with_docstring(class_name, docstring):
    """Generate Python class code with docstring."""
    return f'''
class {class_name}:
    """{docstring}"""
    pass
'''


def generate_function_with_docstring(func_name, docstring):
    """Generate Python function code with docstring."""
    return f'''
def {func_name}():
    """{docstring}"""
    pass
'''


@settings(max_examples=100)
@given(
    class_name=st.text(
        alphabet=st.characters(whitelist_categories=('Lu',), min_codepoint=65, max_codepoint=90),
        min_size=1,
        max_size=20
    ),
    docstring=docstring_strategy
)
def test_property_class_docstring_extraction(class_name, docstring):
    """
    Property 40: Docstring extraction (for classes)
    
    For any class with a docstring, that docstring should appear in the
    corresponding diagram element's description.
    
    This test verifies that:
    1. The docstring is extracted from the class
    2. The extracted docstring matches the original
    """
    assume(class_name.isidentifier())
    assume(len(docstring.strip()) > 0)
    
    # Generate code with docstring
    code = generate_class_with_docstring(class_name, docstring)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have exactly one class
        assert len(analysis.classes) == 1
        class_info = analysis.classes[0]
        
        # Property: Docstring should be extracted
        assert class_info.docstring is not None, \
            "Docstring should be extracted"
        
        # Property: Extracted docstring should match original
        assert class_info.docstring == docstring, \
            f"Expected docstring '{docstring}', got '{class_info.docstring}'"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


@settings(max_examples=100)
@given(
    func_name=st.text(
        alphabet=st.characters(whitelist_categories=('Ll',), min_codepoint=97, max_codepoint=122),
        min_size=1,
        max_size=20
    ),
    docstring=docstring_strategy
)
def test_property_function_docstring_extraction(func_name, docstring):
    """
    Property 40: Docstring extraction (for functions)
    
    For any function with a docstring, that docstring should appear in the
    corresponding diagram element's description.
    
    This test verifies that:
    1. The docstring is extracted from the function
    2. The extracted docstring matches the original
    """
    assume(func_name.isidentifier())
    assume(len(docstring.strip()) > 0)
    
    # Generate code with docstring
    code = generate_function_with_docstring(func_name, docstring)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have exactly one function
        assert len(analysis.functions) == 1
        func_info = analysis.functions[0]
        
        # Property: Docstring should be extracted
        assert func_info.docstring is not None, \
            "Docstring should be extracted"
        
        # Property: Extracted docstring should match original
        assert func_info.docstring == docstring, \
            f"Expected docstring '{docstring}', got '{func_info.docstring}'"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_module_docstring_extraction():
    """Test extraction of module-level docstring."""
    code = '''
"""This is a module docstring."""

def some_function():
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Module docstring should be extracted
        assert analysis.docstring is not None
        assert analysis.docstring == "This is a module docstring."
    finally:
        Path(temp_path).unlink()


def test_no_docstring():
    """Test that missing docstrings are handled correctly."""
    code = '''
class NoDocstring:
    pass

def no_docstring():
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Class should have no docstring
        assert len(analysis.classes) == 1
        assert analysis.classes[0].docstring is None
        
        # Function should have no docstring
        assert len(analysis.functions) == 1
        assert analysis.functions[0].docstring is None
    finally:
        Path(temp_path).unlink()


def test_multiline_docstring():
    """Test extraction of multiline docstrings."""
    code = '''
def complex_function():
    """
    This is a complex function.
    
    It does many things:
    - Thing 1
    - Thing 2
    - Thing 3
    
    Returns:
        Something useful
    """
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        assert len(analysis.functions) == 1
        func_info = analysis.functions[0]
        
        # Docstring should be extracted
        assert func_info.docstring is not None
        assert "This is a complex function" in func_info.docstring
        assert "Thing 1" in func_info.docstring
        assert "Returns:" in func_info.docstring
    finally:
        Path(temp_path).unlink()


def generate_typed_function(func_name, param_types, return_type):
    """Generate function with type hints."""
    params = ', '.join([f"{name}: {ptype}" for name, ptype in param_types.items()])
    return f'''
def {func_name}({params}) -> {return_type}:
    """Function with type hints."""
    pass
'''


@settings(max_examples=100)
@given(
    func_name=st.text(
        alphabet=st.characters(whitelist_categories=('Ll',), min_codepoint=97, max_codepoint=122),
        min_size=1,
        max_size=20
    ),
    param_types=st.dictionaries(
        keys=st.text(
            alphabet=st.characters(whitelist_categories=('Ll',), min_codepoint=97, max_codepoint=122),
            min_size=1,
            max_size=10
        ),
        values=st.sampled_from(['str', 'int', 'float', 'bool', 'list', 'dict']),
        min_size=1,
        max_size=5
    ),
    return_type=st.sampled_from(['str', 'int', 'float', 'bool', 'list', 'dict', 'None'])
)
def test_property_type_hint_inclusion(func_name, param_types, return_type):
    """
    Property 41: Type hint inclusion
    
    For any function parameter or return value with a type hint, that type
    should appear in class and sequence diagrams.
    
    This test verifies that:
    1. All parameter type hints are extracted
    2. Return type hint is extracted
    3. Type hints match the source code
    """
    assume(func_name.isidentifier())
    assume(all(name.isidentifier() for name in param_types.keys()))
    
    # Generate code with type hints
    code = generate_typed_function(func_name, param_types, return_type)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have exactly one function
        assert len(analysis.functions) == 1
        func_info = analysis.functions[0]
        
        # Property: All parameters should have type hints
        for param in func_info.parameters:
            if param.name in param_types:
                assert param.type_hint is not None, \
                    f"Parameter '{param.name}' should have type hint"
                assert param.type_hint == param_types[param.name], \
                    f"Expected type '{param_types[param.name]}' for parameter '{param.name}', got '{param.type_hint}'"
        
        # Property: Return type should be extracted
        assert func_info.return_type == return_type, \
            f"Expected return type '{return_type}', got '{func_info.return_type}'"
        
        # Property: Number of parameters should match
        assert len(func_info.parameters) == len(param_types), \
            f"Expected {len(param_types)} parameters, got {len(func_info.parameters)}"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_type_hint_with_generics():
    """Test extraction of generic type hints like List[str]."""
    code = '''
from typing import List, Dict, Optional

def typed_function(items: List[str], mapping: Dict[str, int]) -> Optional[str]:
    """Function with generic type hints."""
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        assert len(analysis.functions) == 1
        func_info = analysis.functions[0]
        
        # Check parameter types
        items_param = next((p for p in func_info.parameters if p.name == 'items'), None)
        assert items_param is not None
        assert 'List' in items_param.type_hint
        
        mapping_param = next((p for p in func_info.parameters if p.name == 'mapping'), None)
        assert mapping_param is not None
        assert 'Dict' in mapping_param.type_hint
        
        # Check return type
        assert 'Optional' in func_info.return_type
    finally:
        Path(temp_path).unlink()


def test_metadata_extractor_directly():
    """Test MetadataExtractor methods directly."""
    extractor = MetadataExtractor()
    
    # Test docstring extraction
    code = '''
class TestClass:
    """Test docstring."""
    pass
'''
    tree = ast.parse(code)
    class_node = tree.body[0]
    
    docstring = extractor.extract_docstring(class_node)
    assert docstring == "Test docstring."
    
    # Test type hint extraction
    code2 = '''
def test_func(x: int, y: str) -> bool:
    pass
'''
    tree2 = ast.parse(code2)
    func_node = tree2.body[0]
    
    type_hints = extractor.extract_type_hints(func_node)
    assert type_hints.parameters['x'] == 'int'
    assert type_hints.parameters['y'] == 'str'
    assert type_hints.return_type == 'bool'
