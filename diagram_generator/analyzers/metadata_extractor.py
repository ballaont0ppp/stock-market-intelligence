"""Metadata extractor for extracting documentation and annotations from code."""

import ast
import re
from typing import Dict, List, Optional, Any

from diagram_generator.core.types import TypeHints, Comment


class MetadataExtractor:
    """Extracts metadata from Python source code."""
    
    def extract_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from AST node.
        
        Args:
            node: AST node (Module, ClassDef, or FunctionDef)
            
        Returns:
            Docstring text or None if not present
        """
        return ast.get_docstring(node)
    
    def extract_type_hints(self, func: ast.FunctionDef) -> TypeHints:
        """Extract type hints from function.
        
        Args:
            func: AST FunctionDef node
            
        Returns:
            TypeHints object with parameter and return type information
        """
        parameters = {}
        
        # Extract parameter type hints
        for arg in func.args.args:
            if arg.annotation:
                param_type = self._annotation_to_string(arg.annotation)
                parameters[arg.arg] = param_type
        
        # Extract return type hint
        return_type = None
        if func.returns:
            return_type = self._annotation_to_string(func.returns)
        
        return TypeHints(
            parameters=parameters,
            return_type=return_type
        )
    
    def extract_inline_comments(self, source: str, node: ast.AST) -> List[Comment]:
        """Extract inline comments near AST node.
        
        Args:
            source: Source code as string
            node: AST node to find comments near
            
        Returns:
            List of Comment objects
        """
        comments = []
        lines = source.split('\n')
        
        # Get the line range for the node
        if hasattr(node, 'lineno'):
            start_line = node.lineno - 1  # Convert to 0-indexed
            end_line = getattr(node, 'end_lineno', start_line)
            
            # Look for comments in the lines around the node
            search_start = max(0, start_line - 2)
            search_end = min(len(lines), end_line + 2)
            
            for i in range(search_start, search_end):
                line = lines[i]
                # Find comments in the line
                comment_match = re.search(r'#\s*(.+)$', line)
                if comment_match:
                    comment_text = comment_match.group(1).strip()
                    comments.append(Comment(
                        text=comment_text,
                        line_number=i + 1,  # Convert back to 1-indexed
                        associated_node=getattr(node, 'name', None)
                    ))
        
        return comments
    
    def parse_decorator_metadata(self, decorator: ast.expr) -> Dict[str, Any]:
        """Parse metadata from decorator.
        
        Args:
            decorator: AST decorator expression
            
        Returns:
            Dictionary of metadata extracted from decorator
        """
        metadata = {}
        
        if isinstance(decorator, ast.Name):
            metadata['name'] = decorator.id
            metadata['type'] = 'simple'
        
        elif isinstance(decorator, ast.Call):
            # Decorator with arguments
            if isinstance(decorator.func, ast.Name):
                metadata['name'] = decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                metadata['name'] = self._get_attribute_name(decorator.func)
            else:
                metadata['name'] = 'unknown'
            
            metadata['type'] = 'call'
            
            # Extract positional arguments
            args = []
            for arg in decorator.args:
                args.append(self._expr_to_value(arg))
            metadata['args'] = args
            
            # Extract keyword arguments
            kwargs = {}
            for keyword in decorator.keywords:
                kwargs[keyword.arg] = self._expr_to_value(keyword.value)
            metadata['kwargs'] = kwargs
        
        elif isinstance(decorator, ast.Attribute):
            metadata['name'] = self._get_attribute_name(decorator)
            metadata['type'] = 'attribute'
        
        return metadata
    
    def parse_docstring_format(self, docstring: str) -> Dict[str, Any]:
        """Parse docstring into structured format.
        
        Supports Google, NumPy, and reStructuredText formats.
        
        Args:
            docstring: Docstring text
            
        Returns:
            Dictionary with parsed docstring sections
        """
        if not docstring:
            return {}
        
        result = {
            'summary': '',
            'description': '',
            'args': {},
            'returns': '',
            'raises': {},
            'examples': []
        }
        
        lines = docstring.split('\n')
        
        # Extract summary (first line)
        if lines:
            result['summary'] = lines[0].strip()
        
        # Try to detect format and parse accordingly
        if 'Args:' in docstring or 'Returns:' in docstring:
            # Google style
            result.update(self._parse_google_docstring(docstring))
        elif 'Parameters' in docstring or 'Returns' in docstring:
            # NumPy style
            result.update(self._parse_numpy_docstring(docstring))
        elif ':param' in docstring or ':return:' in docstring:
            # reStructuredText style
            result.update(self._parse_rst_docstring(docstring))
        
        return result
    
    def _parse_google_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse Google-style docstring."""
        result = {}
        lines = docstring.split('\n')
        
        current_section = None
        section_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped in ['Args:', 'Arguments:', 'Parameters:']:
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'args'
                section_content = []
            elif line_stripped in ['Returns:', 'Return:']:
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'returns'
                section_content = []
            elif line_stripped in ['Raises:', 'Raise:']:
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'raises'
                section_content = []
            elif line_stripped in ['Examples:', 'Example:']:
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'examples'
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section and section_content:
            result[current_section] = '\n'.join(section_content)
        
        return result
    
    def _parse_numpy_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse NumPy-style docstring."""
        # Simplified NumPy parsing
        result = {}
        lines = docstring.split('\n')
        
        current_section = None
        section_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped == 'Parameters':
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'args'
                section_content = []
            elif line_stripped == 'Returns':
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'returns'
                section_content = []
            elif line_stripped == 'Raises':
                if current_section and section_content:
                    result[current_section] = '\n'.join(section_content)
                current_section = 'raises'
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section and section_content:
            result[current_section] = '\n'.join(section_content)
        
        return result
    
    def _parse_rst_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse reStructuredText-style docstring."""
        result = {'args': {}, 'raises': {}}
        
        # Extract :param: directives
        param_pattern = r':param\s+(\w+):\s*(.+)'
        for match in re.finditer(param_pattern, docstring):
            param_name = match.group(1)
            param_desc = match.group(2)
            result['args'][param_name] = param_desc
        
        # Extract :return: directive
        return_pattern = r':returns?:\s*(.+)'
        return_match = re.search(return_pattern, docstring)
        if return_match:
            result['returns'] = return_match.group(1)
        
        # Extract :raises: directives
        raises_pattern = r':raises\s+(\w+):\s*(.+)'
        for match in re.finditer(raises_pattern, docstring):
            exception_name = match.group(1)
            exception_desc = match.group(2)
            result['raises'][exception_name] = exception_desc
        
        return result
    
    def _annotation_to_string(self, annotation: ast.expr) -> str:
        """Convert type annotation to string."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return self._get_attribute_name(annotation)
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like List[str]
            value = self._annotation_to_string(annotation.value)
            slice_val = self._annotation_to_string(annotation.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(annotation, ast.Tuple):
            # Handle tuple types
            elements = [self._annotation_to_string(elt) for elt in annotation.elts]
            return f"({', '.join(elements)})"
        elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Handle Union types (X | Y)
            left = self._annotation_to_string(annotation.left)
            right = self._annotation_to_string(annotation.right)
            return f"{left} | {right}"
        else:
            return "Any"
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., 'module.Class')."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return '.'.join(reversed(parts))
    
    def _expr_to_value(self, expr: ast.expr) -> Any:
        """Convert AST expression to Python value."""
        if isinstance(expr, ast.Constant):
            return expr.value
        elif isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.List):
            return [self._expr_to_value(elt) for elt in expr.elts]
        elif isinstance(expr, ast.Dict):
            return {
                self._expr_to_value(k): self._expr_to_value(v)
                for k, v in zip(expr.keys, expr.values)
            }
        elif isinstance(expr, ast.Tuple):
            return tuple(self._expr_to_value(elt) for elt in expr.elts)
        else:
            return str(expr)
