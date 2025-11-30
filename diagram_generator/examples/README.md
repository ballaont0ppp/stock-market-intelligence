# Configuration Examples

This directory contains example configuration files for different use cases.

## Available Examples

### 1. minimal_config.yaml

**Use Case**: Quick documentation with essential diagrams only

**Generates**:
- Architecture diagram
- ER diagram

**Best For**:
- Small projects
- Quick overviews
- Initial documentation

**Usage**:
```bash
python -m diagram_generator.cli generate ./app --config examples/minimal_config.yaml
```

### 2. comprehensive_config.yaml

**Use Case**: Complete documentation with all diagram types

**Generates**:
- All 12 diagram types
- Detailed information
- Incremental updates enabled

**Best For**:
- Large projects
- Complete documentation
- Team collaboration

**Usage**:
```bash
python -m diagram_generator.cli generate ./app --config examples/comprehensive_config.yaml
```

### 3. flask_app_config.yaml

**Use Case**: Flask web application documentation

**Generates**:
- Architecture
- ER diagrams
- Sequence diagrams (API flows)
- Use case diagrams
- Component diagrams

**Best For**:
- Flask applications
- API documentation
- Web service architecture

**Usage**:
```bash
python -m diagram_generator.cli generate ./app --config examples/flask_app_config.yaml
```

## Customizing Configurations

### Adding Diagram Types

```yaml
diagram_types:
  - architecture
  - er_diagram
  - class_diagram  # Add more types as needed
```

### Excluding Files

```yaml
exclude:
  - "**/test_*.py"      # Exclude test files
  - "**/migrations/**"  # Exclude database migrations
  - "**/__pycache__/**" # Exclude Python cache
```

### Setting Detail Level

```yaml
detail_level: minimal    # Less detail, faster generation
detail_level: normal     # Balanced (default)
detail_level: detailed   # Maximum detail
```

### Enabling Incremental Updates

```yaml
incremental: true  # Only regenerate changed diagrams
```

## Creating Your Own Configuration

1. Copy an example configuration
2. Modify diagram types to suit your needs
3. Add project-specific exclusions
4. Set appropriate detail level
5. Save as `diagram_config.yaml` in your project root

Example:
```bash
cp examples/flask_app_config.yaml ./diagram_config.yaml
# Edit diagram_config.yaml
python -m diagram_generator.cli generate ./app --config diagram_config.yaml
```

## Configuration Reference

### diagram_types
List of diagram types to generate. Available types:
- `architecture` - Component architecture
- `er_diagram` - Entity-relationship
- `class_diagram` - UML class diagrams
- `sequence_diagram` - Request flows
- `data_flow` - Data flow diagrams
- `state_diagram` - State machines
- `use_case` - Use case diagrams
- `component` - Component dependencies
- `deployment` - Deployment architecture
- `activity` - Activity diagrams
- `package` - Package structure
- `test_coverage` - Test coverage visualization

### output_dir
Directory where diagrams will be saved. Default: `./diagrams`

### exclude
List of glob patterns for files/directories to exclude.

### detail_level
Amount of detail in diagrams:
- `minimal` - Basic structure only
- `normal` - Standard detail (default)
- `detailed` - Maximum information

### incremental
Enable incremental updates (boolean). Default: `false`

### preserve_manual_edits
Preserve manual edits in generated diagrams (boolean). Default: `false`

## Tips

1. **Start Minimal**: Begin with minimal configuration and add diagram types as needed
2. **Exclude Tests**: Always exclude test files to focus on production code
3. **Use Incremental**: Enable incremental updates for large codebases
4. **Version Control**: Commit your configuration file to share with team
5. **Document Changes**: Add comments to explain project-specific settings
