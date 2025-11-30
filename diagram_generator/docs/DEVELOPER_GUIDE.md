# Diagram Generator - Developer Guide

## Architecture Overview

The Diagram Generator follows a modular pipeline architecture with three main stages:

1. **Analysis Stage**: Parse source code and extract structural information
2. **Generation Stage**: Transform analyzed data into Mermaid diagrams
3. **Output Stage**: Write diagrams to files with versioning

## Project Structure

```
diagram_generator/
├── core/
│   ├── base_generator.py      # Abstract base for generators
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Custom exceptions
│   ├── orchestrator.py         # Pipeline coordinator
│   └── types.py                # Data models and enums
├── analyzers/
│   ├── code_analyzer.py        # Python AST parsing
│   ├── database_analyzer.py    # SQLAlchemy model analysis
│   ├── route_analyzer.py       # Flask route extraction
│   ├── dependency_analyzer.py  # Dependency graph building
│   └── metadata_extractor.py   # Docstrings and type hints
├── generators/
│   ├── architecture_generator.py
│   ├── er_generator.py
│   ├── class_generator.py
│   ├── sequence_generator.py
│   └── ... (12 total generators)
├── formatters/
│   └── mermaid_formatter.py    # Mermaid syntax generation
├── utils/
│   ├── file_manager.py         # File I/O and versioning
│   └── change_detector.py      # Incremental update logic
├── tests/
│   └── test_*_properties.py    # Property-based tests
└── cli.py                      # Command-line interface
```

## Core Components

### DiagramGenerator (Abstract Base)

All diagram generators inherit from this base class:

```python
from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import DiagramType, AnalysisData, Diagram

class MyDiagramGenerator(DiagramGenerator):
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.MY_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        # Extract relevant data
        nodes = []
        edges = []
        
        # Process analysis data
        for file_analysis in analysis_data.file_analyses:
            # ... extract information
            pass
        
        # Generate Mermaid code
        mermaid_code = self.formatter.format_graph(nodes, edges)
        
        # Create diagram with metadata
        return self._create_diagram(
            title="My Diagram",
            mermaid_code=mermaid_code,
            source_files=[fa.file_path for fa in analysis_data.file_analyses]
        )
```

### Data Models

Key data structures defined in `core/types.py`:

```python
@dataclass
class FileAnalysis:
    """Analysis result for a single file"""
    file_path: str
    module_name: str
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[ImportInfo]
    docstring: Optional[str]

@dataclass
class AnalysisData:
    """Combined analysis data for diagram generation"""
    file_analyses: List[FileAnalysis]
    database_schema: Optional[DatabaseSchema]
    route_map: Optional[RouteMap]
    dependency_graph: Optional[DependencyGraph]

@dataclass
class Diagram:
    """Generated diagram"""
    diagram_type: DiagramType
    title: str
    mermaid_code: str
    metadata: DiagramMetadata
    source_files: List[str]
```

## Adding a New Diagram Type

### Step 1: Define Diagram Type

Add to `core/types.py`:

```python
class DiagramType(Enum):
    # ... existing types
    MY_NEW_DIAGRAM = "my_new_diagram"
```

### Step 2: Create Generator

Create `generators/my_new_generator.py`:

```python
from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import DiagramType, AnalysisData, Diagram
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter

class MyNewDiagramGenerator(DiagramGenerator):
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.MY_NEW_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        # Implementation here
        pass
```

### Step 3: Register Generator

Add to `generators/__init__.py`:

```python
from .my_new_generator import MyNewDiagramGenerator

__all__ = [
    # ... existing generators
    'MyNewDiagramGenerator'
]
```

### Step 4: Add to Orchestrator

Update `core/orchestrator.py` to include your generator in the generation pipeline.

### Step 5: Write Tests

Create `tests/test_my_new_generator_properties.py`:

```python
from hypothesis import given, strategies as st, settings
from diagram_generator.generators.my_new_generator import MyNewDiagramGenerator

class TestMyNewGeneratorProperties:
    @given(analysis_data=analysis_data_strategy())
    @settings(max_examples=100)
    def test_my_property(self, analysis_data):
        """Property: Description of what should hold true.
        
        **Feature: diagram-generation-system, Property X: Property name**
        **Validates: Requirements X.Y**
        """
        generator = MyNewDiagramGenerator()
        diagram = generator.generate(analysis_data)
        
        # Assert property holds
        assert some_condition(diagram)
```

## Testing

### Property-Based Testing

We use Hypothesis for property-based testing with 100 iterations per test:

```python
from hypothesis import given, strategies as st, settings

@given(st.lists(st.text(), min_size=1, max_size=10))
@settings(max_examples=100)
def test_property(input_list):
    result = my_function(input_list)
    assert len(result) == len(input_list)
```

### Running Tests

```bash
# Run all tests
pytest diagram_generator/tests/

# Run specific test file
pytest diagram_generator/tests/test_architecture_generator_properties.py

# Run with coverage
pytest --cov=diagram_generator --cov-report=html
```

## Code Analysis

### AST Parsing

The `CodeAnalyzer` uses Python's `ast` module:

```python
import ast

def analyze_file(self, file_path: str) -> FileAnalysis:
    with open(file_path, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    classes = self.extract_classes(tree)
    functions = self.extract_functions(tree)
    imports = self.extract_imports(tree)
    
    return FileAnalysis(
        file_path=file_path,
        module_name=self._get_module_name(file_path),
        classes=classes,
        functions=functions,
        imports=imports
    )
```

### Extracting Information

Example of extracting class information:

```python
def extract_classes(self, tree: ast.Module) -> List[ClassInfo]:
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = ClassInfo(
                name=node.name,
                bases=[self._get_base_name(base) for base in node.bases],
                methods=self._extract_methods(node),
                attributes=self._extract_attributes(node),
                docstring=ast.get_docstring(node)
            )
            classes.append(class_info)
    
    return classes
```

## Mermaid Formatting

### Using MermaidFormatter

```python
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter

formatter = MermaidFormatter()

# Format graph diagram
mermaid_code = formatter.format_graph(nodes, edges, direction="TD")

# Format ER diagram
mermaid_code = formatter.format_er_diagram(entities, relationships)

# Format sequence diagram
mermaid_code = formatter.format_sequence_diagram(participants, messages)
```

### Custom Formatting

For custom diagram types, you can extend the formatter or create your own:

```python
def format_my_diagram(self, data) -> str:
    lines = ["graph TD"]
    
    for item in data:
        lines.append(f"    {item.id}[{item.label}]")
    
    return "\n".join(lines)
```

## Error Handling

### Custom Exceptions

```python
from diagram_generator.core.exceptions import (
    DiagramGenerationError,
    ParseError,
    AnalysisError,
    ValidationError
)

try:
    diagram = generator.generate(analysis_data)
except ParseError as e:
    logger.error(f"Failed to parse file: {e.context['file_path']}")
except AnalysisError as e:
    logger.warning(f"Analysis incomplete: {e.message}")
```

### Graceful Degradation

```python
def generate(self, analysis_data: AnalysisData) -> Diagram:
    try:
        # Complex analysis
        result = self._complex_analysis(analysis_data)
    except AnalysisError:
        # Fall back to simpler analysis
        result = self._simple_analysis(analysis_data)
    
    return self._create_diagram("Title", result)
```

## Configuration

### Loading Configuration

```python
from diagram_generator.core.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config("diagram_config.yaml")

enabled_diagrams = config_manager.get_enabled_diagrams()
exclusions = config_manager.get_exclusion_patterns()
```

### Configuration Schema

```yaml
diagram_types:
  - architecture
  - er_diagram

output_dir: ./diagrams

exclude:
  - "**/test_*.py"

detail_level: normal

incremental: true
```

## Best Practices

### 1. Type Hints

Always use type hints for better code clarity:

```python
def analyze_file(self, file_path: str) -> FileAnalysis:
    pass
```

### 2. Docstrings

Document all public methods:

```python
def generate(self, analysis_data: AnalysisData) -> Diagram:
    """Generate diagram from analysis data.
    
    Args:
        analysis_data: Combined analysis data from code analyzers
        
    Returns:
        Generated diagram with Mermaid code
        
    Raises:
        GenerationError: If diagram generation fails
    """
```

### 3. Property-Based Tests

Write properties that should hold for all inputs:

```python
@given(analysis_data=analysis_data_strategy())
def test_all_modules_included(self, analysis_data):
    """For any analysis data, all modules should appear in diagram."""
    diagram = generator.generate(analysis_data)
    for file_analysis in analysis_data.file_analyses:
        assert file_analysis.module_name in diagram.mermaid_code
```

### 4. Error Context

Provide context in exceptions:

```python
raise ParseError(
    f"Failed to parse {file_path}",
    {"file_path": file_path, "line": line_number}
)
```

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing file: {file_path}")
logger.info(f"Generated {len(diagrams)} diagrams")
```

### Inspect Analysis Data

```python
# Print analysis data structure
import json
print(json.dumps(analysis_data.__dict__, indent=2, default=str))
```

### Validate Mermaid Syntax

```python
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter

formatter = MermaidFormatter()
result = formatter.validate_syntax(mermaid_code)

if not result.is_valid:
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Implement your feature
5. Ensure all tests pass
6. Submit a pull request

## Resources

- [Mermaid Documentation](https://mermaid-js.github.io/)
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
