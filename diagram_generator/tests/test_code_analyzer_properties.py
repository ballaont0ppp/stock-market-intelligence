"""
Property-based tests for CodeAnalyzer.

**Feature: diagram-generation-system, Property 9: Class member completeness**
**Validates: Requirements 3.1**

**Feature: diagram-generation-system, Property 10: Inheritance representation**
**Validates: Requirements 3.2**

**Feature: diagram-generation-system, Property 11: Method signature preservation**
**Validates: Requirements 3.4**
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from diagram_generator.analyzers.code_analyzer import CodeAnalyzer


# Strategies for generating Python code elements
valid_identifier = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=20
).filter(lambda x: x.isidentifier() and not x.startswith('_'))

method_name = valid_identifier
attribute_name = valid_identifier
class_name = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',), min_codepoint=65, max_codepoint=90),
    min_size=1,
    max_size=20
).map(lambda x: x[0].upper() + x[1:] if x else 'A')


def generate_class_code(class_name_str, methods, attributes):
    """Generate Python class code with specified methods and attributes."""
    lines = [f"class {class_name_str}:"]
    
    # Add docstring
    lines.append('    """Test class."""')
    
    # Add attributes
    for attr in attributes:
        lines.append(f"    {attr} = None")
    
    # Add methods
    for method in methods:
        lines.append(f"    def {method}(self):")
        lines.append(f'        """Method {method}."""')
        lines.append("        pass")
    
    # If no methods or attributes, add pass
    if not methods and not attributes:
        lines.append("    pass")
    
    return "\n".join(lines)


@settings(max_examples=100)
@given(
    cls_name=class_name,
    methods=st.lists(method_name, min_size=0, max_size=10, unique=True),
    attributes=st.lists(attribute_name, min_size=0, max_size=10, unique=True)
)
def test_property_class_member_completeness(cls_name, methods, attributes):
    """
    Property 9: Class member completeness
    
    For any class with M methods and A attributes, the generated class diagram
    should show all M methods and all A attributes.
    
    This test verifies that:
    1. All methods are extracted
    2. All attributes are extracted
    3. The counts match exactly
    """
    # Ensure we have valid identifiers
    assume(cls_name.isidentifier())
    assume(all(m.isidentifier() for m in methods))
    assume(all(a.isidentifier() for a in attributes))
    
    # Generate class code
    code = generate_class_code(cls_name, methods, attributes)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have exactly one class
        assert len(analysis.classes) == 1, \
            f"Expected 1 class, found {len(analysis.classes)}"
        
        class_info = analysis.classes[0]
        
        # Property: Class name should match
        assert class_info.name == cls_name, \
            f"Expected class name '{cls_name}', got '{class_info.name}'"
        
        # Property: Number of methods should match
        # Note: We filter out __init__ and other special methods that might be added
        extracted_methods = [m.name for m in class_info.methods if not m.name.startswith('__')]
        assert len(extracted_methods) == len(methods), \
            f"Expected {len(methods)} methods, found {len(extracted_methods)}: {extracted_methods}"
        
        # Property: All methods should be present
        for method in methods:
            assert method in extracted_methods, \
                f"Method '{method}' not found in extracted methods: {extracted_methods}"
        
        # Property: Number of attributes should match
        extracted_attributes = [a.name for a in class_info.attributes]
        assert len(extracted_attributes) == len(attributes), \
            f"Expected {len(attributes)} attributes, found {len(extracted_attributes)}: {extracted_attributes}"
        
        # Property: All attributes should be present
        for attr in attributes:
            assert attr in extracted_attributes, \
                f"Attribute '{attr}' not found in extracted attributes: {extracted_attributes}"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def generate_inheritance_code(base_class, derived_class):
    """Generate Python code with inheritance."""
    return f"""
class {base_class}:
    '''Base class.'''
    pass

class {derived_class}({base_class}):
    '''Derived class.'''
    pass
"""


@settings(max_examples=100)
@given(
    base_class=class_name,
    derived_class=class_name
)
def test_property_inheritance_representation(base_class, derived_class):
    """
    Property 10: Inheritance representation
    
    For any class that inherits from a parent class, the class diagram
    should show an inheritance arrow from child to parent.
    
    This test verifies that:
    1. The derived class is extracted
    2. The base class is recorded in the derived class's bases list
    """
    # Ensure different class names
    assume(base_class != derived_class)
    assume(base_class.isidentifier())
    assume(derived_class.isidentifier())
    
    # Generate code with inheritance
    code = generate_inheritance_code(base_class, derived_class)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have exactly two classes
        assert len(analysis.classes) == 2, \
            f"Expected 2 classes, found {len(analysis.classes)}"
        
        # Find the derived class
        derived_info = next((c for c in analysis.classes if c.name == derived_class), None)
        assert derived_info is not None, \
            f"Derived class '{derived_class}' not found"
        
        # Property: Derived class should have base class in its bases list
        assert base_class in derived_info.bases, \
            f"Base class '{base_class}' not found in derived class bases: {derived_info.bases}"
        
        # Property: Should have exactly one base class
        assert len(derived_info.bases) == 1, \
            f"Expected 1 base class, found {len(derived_info.bases)}: {derived_info.bases}"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def generate_typed_method_code(class_name_str, method_name_str, param_type, return_type):
    """Generate Python method code with type hints."""
    return f"""
class {class_name_str}:
    '''Test class.'''
    def {method_name_str}(self, param: {param_type}) -> {return_type}:
        '''Method with type hints.'''
        return {return_type}()
"""


@settings(max_examples=100)
@given(
    cls_name=class_name,
    method=method_name,
    param_type=st.sampled_from(['str', 'int', 'float', 'bool', 'list', 'dict']),
    return_type=st.sampled_from(['str', 'int', 'float', 'bool', 'list', 'dict', 'None'])
)
def test_property_method_signature_preservation(cls_name, method, param_type, return_type):
    """
    Property 11: Method signature preservation
    
    For any method with type hints, the class diagram should include
    parameter types and return type matching the source code.
    
    This test verifies that:
    1. Parameter type hints are extracted correctly
    2. Return type hints are extracted correctly
    """
    assume(cls_name.isidentifier())
    assume(method.isidentifier())
    
    # Generate code with typed method
    code = generate_typed_method_code(cls_name, method, param_type, return_type)
    
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
        
        # Should have exactly one method
        assert len(class_info.methods) == 1
        method_info = class_info.methods[0]
        
        # Property: Method name should match
        assert method_info.name == method, \
            f"Expected method name '{method}', got '{method_info.name}'"
        
        # Property: Should have one parameter (besides self)
        params = [p for p in method_info.parameters if p.name != 'self']
        assert len(params) == 1, \
            f"Expected 1 parameter, found {len(params)}"
        
        # Property: Parameter type should match
        param_info = params[0]
        assert param_info.type_hint == param_type, \
            f"Expected parameter type '{param_type}', got '{param_info.type_hint}'"
        
        # Property: Return type should match
        assert method_info.return_type == return_type, \
            f"Expected return type '{return_type}', got '{method_info.return_type}'"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_empty_class():
    """Test extraction of an empty class."""
    code = """
class EmptyClass:
    '''An empty class.'''
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        assert len(analysis.classes) == 1
        class_info = analysis.classes[0]
        assert class_info.name == 'EmptyClass'
        assert len(class_info.methods) == 0
        assert len(class_info.attributes) == 0
    finally:
        Path(temp_path).unlink()


def test_class_with_multiple_inheritance():
    """Test extraction of a class with multiple inheritance."""
    code = """
class Base1:
    pass

class Base2:
    pass

class Derived(Base1, Base2):
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        derived = next((c for c in analysis.classes if c.name == 'Derived'), None)
        assert derived is not None
        assert 'Base1' in derived.bases
        assert 'Base2' in derived.bases
        assert len(derived.bases) == 2
    finally:
        Path(temp_path).unlink()



def generate_import_code(imports):
    """Generate Python code with specified imports."""
    lines = []
    for imp in imports:
        lines.append(f"import {imp}")
    lines.append("")
    lines.append("# Some code")
    lines.append("pass")
    return "\n".join(lines)


@settings(max_examples=100)
@given(
    imports=st.lists(
        st.sampled_from(['os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 'collections']),
        min_size=1,
        max_size=10,
        unique=True
    )
)
def test_property_import_to_dependency_mapping(imports):
    """
    Property 27: Import to dependency mapping
    
    For any import statement from module A to module B, a dependency arrow
    should appear from A to B in the component diagram.
    
    This test verifies that:
    1. All import statements are extracted
    2. The number of imports matches
    3. Each import is correctly identified
    """
    # Generate code with imports
    code = generate_import_code(imports)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Analyze the file
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Property: Number of imports should match
        assert len(analysis.imports) == len(imports), \
            f"Expected {len(imports)} imports, found {len(analysis.imports)}"
        
        # Property: All imports should be present
        extracted_modules = [imp.module for imp in analysis.imports]
        for imp in imports:
            assert imp in extracted_modules, \
                f"Import '{imp}' not found in extracted imports: {extracted_modules}"
        
        # Property: Each import should be marked as external (these are standard library)
        for import_info in analysis.imports:
            assert import_info.is_external, \
                f"Import '{import_info.module}' should be marked as external"
    
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_from_import():
    """Test extraction of 'from X import Y' statements."""
    code = """
from os import path
from typing import List, Dict
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have 2 from imports
        assert len(analysis.imports) == 2
        
        # Check first import
        os_import = next((i for i in analysis.imports if i.module == 'os'), None)
        assert os_import is not None
        assert os_import.is_from_import
        assert 'path' in os_import.names
        
        # Check second import
        typing_import = next((i for i in analysis.imports if i.module == 'typing'), None)
        assert typing_import is not None
        assert typing_import.is_from_import
        assert 'List' in typing_import.names
        assert 'Dict' in typing_import.names
    finally:
        Path(temp_path).unlink()


def test_import_with_alias():
    """Test extraction of imports with aliases."""
    code = """
import numpy as np
import pandas as pd
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_file(temp_path)
        
        # Should have 2 imports
        assert len(analysis.imports) == 2
        
        # Check numpy import
        np_import = next((i for i in analysis.imports if i.module == 'numpy'), None)
        assert np_import is not None
        assert np_import.alias == 'np'
        
        # Check pandas import
        pd_import = next((i for i in analysis.imports if i.module == 'pandas'), None)
        assert pd_import is not None
        assert pd_import.alias == 'pd'
    finally:
        Path(temp_path).unlink()
