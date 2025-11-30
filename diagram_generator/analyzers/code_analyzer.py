"""Code analyzer for parsing Python source files."""

import ast
from pathlib import Path
from typing import List, Optional

from diagram_generator.core.types import (
    FileAnalysis,
    DirectoryAnalysis,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    ParameterInfo,
    AttributeInfo,
    DecoratorInfo,
)
from diagram_generator.core.exceptions import ParseError, AnalysisError


class CodeAnalyzer:
    """Analyzes Python source code using AST parsing."""
    
    def __init__(self):
        self._external_modules = {
            'flask', 'sqlalchemy', 'pytest', 'numpy', 'pandas',
            'requests', 'django', 'fastapi', 'pydantic', 'typing',
            'datetime', 'json', 'os', 'sys', 're', 'collections',
            'itertools', 'functools', 'pathlib', 'logging'
        }
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileAnalysis object containing extracted information
            
        Raises:
            ParseError: If the file cannot be parsed
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ParseError(
                f"File not found: {file_path}",
                {"file_path": file_path}
            )
        
        if not path.suffix == '.py':
            raise ParseError(
                f"Not a Python file: {file_path}",
                {"file_path": file_path}
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse the source code into an AST
            tree = ast.parse(source, filename=str(path))
            
            # Extract module name from file path
            module_name = self._get_module_name(path)
            
            # Extract docstring
            docstring = ast.get_docstring(tree)
            
            # Extract classes, functions, and imports
            classes = self.extract_classes(tree)
            functions = self.extract_functions(tree)
            imports = self.extract_imports(tree)
            
            return FileAnalysis(
                file_path=str(path),
                module_name=module_name,
                classes=classes,
                functions=functions,
                imports=imports,
                docstring=docstring,
                ast_tree=tree
            )
            
        except SyntaxError as e:
            raise ParseError(
                f"Syntax error in {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e), "line": e.lineno}
            )
        except Exception as e:
            raise ParseError(
                f"Error parsing {file_path}: {str(e)}",
                {"file_path": file_path, "error": str(e)}
            )
    
    def analyze_directory(self, dir_path: str, max_depth: int = 10) -> DirectoryAnalysis:
        """Recursively analyze a directory.
        
        Args:
            dir_path: Path to the directory
            max_depth: Maximum depth for recursion
            
        Returns:
            DirectoryAnalysis object containing all file analyses
            
        Raises:
            AnalysisError: If the directory cannot be analyzed
        """
        path = Path(dir_path)
        
        if not path.exists():
            raise AnalysisError(
                f"Directory not found: {dir_path}",
                {"dir_path": dir_path}
            )
        
        if not path.is_dir():
            raise AnalysisError(
                f"Not a directory: {dir_path}",
                {"dir_path": dir_path}
            )
        
        file_analyses = []
        
        # Find all Python files
        for py_file in path.rglob('*.py'):
            # Check depth
            relative_path = py_file.relative_to(path)
            depth = len(relative_path.parts) - 1
            
            if depth > max_depth:
                continue
            
            try:
                analysis = self.analyze_file(str(py_file))
                file_analyses.append(analysis)
            except ParseError as e:
                # Log error but continue with other files
                print(f"Warning: {e.message}")
                continue
        
        return DirectoryAnalysis(
            directory_path=str(path),
            file_analyses=file_analyses
        )
    
    def extract_classes(self, ast_node: ast.Module) -> List[ClassInfo]:
        """Extract class definitions from AST.
        
        Args:
            ast_node: AST Module node
            
        Returns:
            List of ClassInfo objects
        """
        classes = []
        
        for node in ast.walk(ast_node):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                classes.append(class_info)
        
        return classes
    
    def extract_functions(self, ast_node: ast.Module) -> List[FunctionInfo]:
        """Extract function definitions from AST.
        
        Args:
            ast_node: AST Module node
            
        Returns:
            List of FunctionInfo objects
        """
        functions = []
        
        # Only extract top-level functions (not methods)
        for node in ast_node.body:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_info = self._extract_function_info(node)
                functions.append(func_info)
        
        return functions
    
    def extract_imports(self, ast_node: ast.Module) -> List[ImportInfo]:
        """Extract import statements from AST.
        
        Args:
            ast_node: AST Module node
            
        Returns:
            List of ImportInfo objects
        """
        imports = []
        
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        names=[],
                        alias=alias.asname,
                        is_from_import=False,
                        is_external=self._is_external_module(alias.name)
                    )
                    imports.append(import_info)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names = [alias.name for alias in node.names]
                    import_info = ImportInfo(
                        module=node.module,
                        names=names,
                        alias=None,
                        is_from_import=True,
                        is_external=self._is_external_module(node.module)
                    )
                    imports.append(import_info)
        
        return imports
    
    def extract_decorators(self, node: ast.FunctionDef) -> List[DecoratorInfo]:
        """Extract decorator information from a function.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            List of DecoratorInfo objects
        """
        decorators = []
        
        for decorator in node.decorator_list:
            decorator_info = self._extract_decorator_info(decorator)
            decorators.append(decorator_info)
        
        return decorators
    
    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition."""
        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item)
                methods.append(method_info)
        
        # Extract attributes
        attributes = self._extract_class_attributes(node)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorator_info = self._extract_decorator_info(decorator)
            decorators.append(decorator_info)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            attributes=attributes,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno
        )
    
    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract information from a function definition."""
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_type = None
            if arg.annotation:
                param_type = self._get_type_annotation(arg.annotation)
            
            parameters.append(ParameterInfo(
                name=arg.arg,
                type_hint=param_type
            ))
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._get_type_annotation(node.returns)
        
        # Extract decorators
        decorators = self.extract_decorators(node)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract function calls (simplified)
        calls = self._extract_function_calls(node)
        
        return FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            docstring=docstring,
            calls=calls,
            line_number=node.lineno
        )
    
    def _extract_decorator_info(self, decorator: ast.expr) -> DecoratorInfo:
        """Extract information from a decorator."""
        if isinstance(decorator, ast.Name):
            return DecoratorInfo(name=decorator.id)
        
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                name = decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                name = self._get_attribute_name(decorator.func)
            else:
                name = "unknown"
            
            # Extract arguments (simplified)
            args = []
            for arg in decorator.args:
                if isinstance(arg, ast.Constant):
                    args.append(str(arg.value))
            
            return DecoratorInfo(name=name, args=args)
        
        elif isinstance(decorator, ast.Attribute):
            name = self._get_attribute_name(decorator)
            return DecoratorInfo(name=name)
        
        return DecoratorInfo(name="unknown")
    
    def _extract_class_attributes(self, node: ast.ClassDef) -> List[AttributeInfo]:
        """Extract class attributes."""
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Type-annotated attribute
                attr_type = self._get_type_annotation(item.annotation) if item.annotation else None
                attributes.append(AttributeInfo(
                    name=item.target.id,
                    type_hint=attr_type
                ))
            
            elif isinstance(item, ast.Assign):
                # Regular attribute assignment
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(AttributeInfo(
                            name=target.id
                        ))
        
        return attributes
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(self._get_attribute_name(child.func))
        
        return calls
    
    def _get_type_annotation(self, annotation: ast.expr) -> str:
        """Convert type annotation to string."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return self._get_attribute_name(annotation)
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like List[str]
            value = self._get_type_annotation(annotation.value)
            slice_val = self._get_type_annotation(annotation.slice)
            return f"{value}[{slice_val}]"
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
    
    def _get_module_name(self, path: Path) -> str:
        """Get module name from file path."""
        # Remove .py extension and convert path separators to dots
        parts = path.with_suffix('').parts
        return '.'.join(parts)
    
    def _is_external_module(self, module_name: str) -> bool:
        """Check if a module is external (not part of the project)."""
        # Check if it's a standard library or known external package
        root_module = module_name.split('.')[0]
        return root_module in self._external_modules
