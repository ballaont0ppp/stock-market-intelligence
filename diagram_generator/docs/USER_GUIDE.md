# Diagram Generator - User Guide

## Overview

The Diagram Generator is an automated documentation tool that analyzes Python codebases and generates comprehensive software diagrams in Mermaid format. It supports 12 different diagram types and can incrementally update diagrams when code changes.

## Installation

```bash
# Install from source
cd diagram_generator
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Generate All Diagrams

```bash
python -m diagram_generator.cli generate /path/to/your/project --output ./diagrams
```

### 2. Generate Specific Diagram Types

```bash
python -m diagram_generator.cli generate /path/to/your/project \
    --types architecture,er_diagram,class_diagram \
    --output ./diagrams
```

### 3. Incremental Update

```bash
python -m diagram_generator.cli update /path/to/your/project --output ./diagrams
```

### 4. Validate Diagrams

```bash
python -m diagram_generator.cli validate ./diagrams
```

## Supported Diagram Types

1. **Architecture** - Component architecture with layers
2. **ER Diagram** - Entity-relationship diagrams from database models
3. **Class Diagram** - UML class diagrams with inheritance
4. **Sequence Diagram** - Request flows from API routes
5. **Data Flow** - Data flow diagrams
6. **State Diagram** - State machine diagrams
7. **Use Case** - Use case diagrams from routes
8. **Component** - Component dependency diagrams
9. **Deployment** - Deployment architecture
10. **Activity** - Activity diagrams from functions
11. **Package** - Package structure diagrams
12. **Test Coverage** - Test coverage visualizations

## Configuration

Create a `diagram_config.yaml` file:

```yaml
# Diagram types to generate
diagram_types:
  - architecture
  - er_diagram
  - class_diagram
  - sequence_diagram

# Output directory
output_dir: ./diagrams

# Exclusion patterns
exclude:
  - "**/test_*.py"
  - "**/migrations/**"
  - "**/__pycache__/**"

# Detail level (minimal, normal, detailed)
detail_level: normal

# Enable incremental updates
incremental: true
```

Use the configuration:

```bash
python -m diagram_generator.cli generate /path/to/project --config diagram_config.yaml
```

## CLI Commands

### generate

Generate diagrams from source code.

```bash
python -m diagram_generator.cli generate <source_path> [options]

Options:
  --output, -o PATH          Output directory (default: ./diagrams)
  --config, -c PATH          Configuration file path
  --types, -t TEXT           Comma-separated diagram types
  --exclude, -e TEXT         Exclusion patterns
  --verbose, -v              Verbose output
```

### update

Incrementally update diagrams based on changes.

```bash
python -m diagram_generator.cli update <source_path> [options]

Options:
  --output, -o PATH          Output directory
  --config, -c PATH          Configuration file path
  --verbose, -v              Verbose output
```

### validate

Validate generated Mermaid diagrams.

```bash
python -m diagram_generator.cli validate <diagrams_path> [options]

Options:
  --verbose, -v              Verbose output
```

### config

Manage configuration.

```bash
python -m diagram_generator.cli config [options]

Options:
  --init                     Create example configuration
  --validate PATH            Validate configuration file
```

## Output Format

Diagrams are generated as Markdown files with embedded Mermaid code:

```markdown
# System Architecture

## Metadata
- Generated: 2024-01-15 10:30:00
- Generator Version: 0.1.0
- Source Files: 45

## Diagram

\`\`\`mermaid
graph TD
    auth[Authentication]
    services[Business Services]
    models[Data Models]
    
    auth --> services
    services --> models
\`\`\`

## Source Files
- app/routes/auth.py
- app/services/auth_service.py
- app/models/user.py
```

## Advanced Usage

### Custom Exclusions

```bash
python -m diagram_generator.cli generate ./app \
    --exclude "**/test_*.py,**/migrations/**,**/__pycache__/**"
```

### Specific Output Directory

```bash
python -m diagram_generator.cli generate ./app \
    --output ./docs/diagrams
```

### Verbose Mode

```bash
python -m diagram_generator.cli generate ./app --verbose
```

## Viewing Diagrams

### In VS Code

Install the "Markdown Preview Mermaid Support" extension to view diagrams directly in VS Code.

### In GitHub

GitHub automatically renders Mermaid diagrams in Markdown files.

### Online

Use [Mermaid Live Editor](https://mermaid.live/) to view and edit diagrams.

## Troubleshooting

### Issue: No diagrams generated

**Solution**: Check that your source path contains Python files and that exclusion patterns aren't too broad.

### Issue: Invalid Mermaid syntax

**Solution**: Run `validate` command to identify syntax errors. The generator includes automatic validation.

### Issue: Missing dependencies

**Solution**: Ensure all required packages are installed:
```bash
pip install hypothesis pyyaml
```

### Issue: Incremental update not working

**Solution**: Ensure the output directory contains previously generated diagrams with metadata.

## Best Practices

1. **Use Configuration Files**: Store settings in `diagram_config.yaml` for consistency
2. **Exclude Test Files**: Add test files to exclusions to focus on production code
3. **Incremental Updates**: Use `update` command for large codebases to save time
4. **Version Control**: Commit generated diagrams to track documentation changes
5. **Regular Updates**: Regenerate diagrams after significant code changes

## Examples

### Generate Architecture Diagram Only

```bash
python -m diagram_generator.cli generate ./app --types architecture
```

### Generate with Custom Config

```bash
python -m diagram_generator.cli generate ./app --config my_config.yaml
```

### Validate All Diagrams

```bash
python -m diagram_generator.cli validate ./diagrams --verbose
```

## Support

For issues and questions:
- Check the [Developer Guide](DEVELOPER_GUIDE.md)
- Review example configurations in `config.example.yaml`
- See property-based tests for usage examples
