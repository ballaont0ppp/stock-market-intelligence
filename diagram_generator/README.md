# Diagram Generation System

An automated documentation tool that analyzes codebases and generates comprehensive software diagrams in Mermaid format.

## Features

- **Multiple Diagram Types**: Architecture, ER, Class, Sequence, Component, Package, and more
- **Property-Based Testing**: Comprehensive test coverage with Hypothesis
- **Incremental Updates**: Only regenerate diagrams when source files change
- **Configurable**: Flexible configuration for diagram types, detail levels, and exclusions
- **Mermaid Format**: Generate diagrams in Mermaid syntax for easy version control

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Generate All Diagrams

```bash
python -m diagram_generator.cli generate --source ./app --output ./diagrams
```

### Use Configuration File

```bash
python -m diagram_generator.cli generate --config config.yaml
```

### Validate Diagram Syntax

```bash
python -m diagram_generator.cli validate diagrams/architecture.md
```

## Configuration

Create a `config.yaml` file:

```yaml
enabled_diagrams:
  - architecture
  - er_diagram
  - class_diagram
  - sequence_diagram

output_dir: "diagrams"
source_dir: "."

exclusion_patterns:
  - "*/venv/*"
  - "*/__pycache__/*"
  - "*/tests/*"

create_backups: true
preserve_manual_edits: true
```

## Supported Diagram Types

- **Architecture**: Component architecture with layers
- **ER Diagram**: Entity-relationship diagrams from database models
- **Class Diagram**: UML class diagrams from Python code
- **Sequence Diagram**: Request flow diagrams from API routes
- **Component**: Module dependency diagrams
- **Package**: Package structure diagrams
- **Data Flow**: Data flow diagrams
- **State**: State machine diagrams
- **Use Case**: Use case diagrams from routes
- **Activity**: Activity diagrams from functions
- **Deployment**: Deployment diagrams
- **Test Coverage**: Test coverage visualizations

## Testing

Run all tests:

```bash
pytest diagram_generator/tests/
```

Run property-based tests:

```bash
pytest diagram_generator/tests/ -k property
```

## Project Structure

```
diagram_generator/
├── core/              # Core types and base classes
├── analyzers/         # Code analyzers (Python, DB, Routes)
├── generators/        # Diagram generators
├── formatters/        # Mermaid formatters
├── utils/             # Utilities (file manager, change detector)
├── tests/             # Test suite
└── cli.py             # Command-line interface
```

## Development

### Adding a New Diagram Type

1. Add the diagram type to `core/types.py`
2. Create a generator in `generators/`
3. Add formatting logic to `formatters/mermaid_formatter.py`
4. Write property tests in `tests/`

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=diagram_generator --cov-report=html

# Specific test file
pytest diagram_generator/tests/test_code_analyzer_properties.py
```

## License

MIT License
