"""Core data types and enums for diagram generation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import ast


class DiagramType(Enum):
    """Types of diagrams that can be generated."""
    ARCHITECTURE = "architecture"
    ER_DIAGRAM = "er_diagram"
    CLASS_DIAGRAM = "class_diagram"
    SEQUENCE_DIAGRAM = "sequence_diagram"
    DATA_FLOW = "data_flow"
    STATE_DIAGRAM = "state_diagram"
    USE_CASE = "use_case"
    COMPONENT = "component"
    DEPLOYMENT = "deployment"
    ACTIVITY = "activity"
    PACKAGE = "package"
    TEST_COVERAGE = "test_coverage"


class Cardinality(Enum):
    """Relationship cardinality types."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class RelationshipType(Enum):
    """Types of relationships between entities."""
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"


class DetailLevel(Enum):
    """Level of detail for diagram generation."""
    MINIMAL = "minimal"
    NORMAL = "normal"
    DETAILED = "detailed"


@dataclass
class ParameterInfo:
    """Information about a function parameter."""
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None


@dataclass
class AttributeInfo:
    """Information about a class attribute."""
    name: str
    type_hint: Optional[str] = None
    value: Optional[str] = None
    is_class_var: bool = False


@dataclass
class DecoratorInfo:
    """Information about a decorator."""
    name: str
    args: List[str] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[DecoratorInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    calls: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    bases: List[str] = field(default_factory=list)
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[AttributeInfo] = field(default_factory=list)
    decorators: List[DecoratorInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    line_number: int = 0


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from_import: bool = False
    is_external: bool = False


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    file_path: str
    module_name: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    ast_tree: Optional[ast.Module] = None


@dataclass
class DirectoryAnalysis:
    """Analysis result for a directory."""
    directory_path: str
    file_analyses: List[FileAnalysis] = field(default_factory=list)


@dataclass
class Column:
    """Database column information."""
    name: str
    type: str
    nullable: bool = True
    unique: bool = False
    default: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class ForeignKey:
    """Foreign key information."""
    column: str
    referenced_table: str
    referenced_column: str


@dataclass
class Relationship:
    """Entity relationship information."""
    name: str
    source_entity: str
    target_entity: str
    cardinality: Cardinality
    relationship_type: RelationshipType


@dataclass
class Entity:
    """Database entity information."""
    name: str
    table_name: str
    columns: List[Column] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class DatabaseSchema:
    """Complete database schema information."""
    entities: List[Entity] = field(default_factory=list)


@dataclass
class Participant:
    """Participant in a sequence diagram."""
    name: str
    type: str  # e.g., "actor", "service", "database"


@dataclass
class Message:
    """Message in a sequence diagram."""
    from_participant: str
    to_participant: str
    message: str
    is_return: bool = False


@dataclass
class DBOperation:
    """Database operation in a request flow."""
    operation_type: str  # e.g., "query", "insert", "update", "delete"
    table: str
    description: str


@dataclass
class ExternalCall:
    """External API call in a request flow."""
    service: str
    endpoint: str
    method: str


@dataclass
class RequestFlow:
    """Request flow through the system."""
    participants: List[Participant] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    database_operations: List[DBOperation] = field(default_factory=list)
    external_calls: List[ExternalCall] = field(default_factory=list)


@dataclass
class AuthInfo:
    """Authentication/authorization information."""
    required: bool = False
    roles: List[str] = field(default_factory=list)


@dataclass
class Endpoint:
    """API endpoint information."""
    path: str
    methods: List[str] = field(default_factory=list)
    handler_function: str = ""
    auth_required: bool = False
    roles: List[str] = field(default_factory=list)
    request_flow: Optional[RequestFlow] = None
    docstring: Optional[str] = None


@dataclass
class RouteMap:
    """Map of all routes in the application."""
    endpoints: List[Endpoint] = field(default_factory=list)


@dataclass
class Node:
    """Node in a graph diagram."""
    id: str
    label: str
    type: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Edge in a graph diagram."""
    from_node: str
    to_node: str
    label: str = ""
    type: str = "default"


@dataclass
class DependencyGraph:
    """Dependency graph between modules."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)


@dataclass
class Cycle:
    """Circular dependency cycle."""
    modules: List[str] = field(default_factory=list)


@dataclass
class CouplingMetrics:
    """Coupling metrics for a module."""
    afferent_coupling: int = 0  # Number of modules that depend on this module
    efferent_coupling: int = 0  # Number of modules this module depends on
    instability: float = 0.0  # efferent / (afferent + efferent)


@dataclass
class LayerMap:
    """Map of modules to architectural layers."""
    layers: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class DiagramMetadata:
    """Diagram metadata."""
    generated_at: datetime = field(default_factory=datetime.now)
    generator_version: str = "0.1.0"
    source_hash: str = ""
    manual_edits: bool = False


@dataclass
class Diagram:
    """Generated diagram."""
    diagram_type: DiagramType
    title: str
    mermaid_code: str
    metadata: DiagramMetadata = field(default_factory=DiagramMetadata)
    source_files: List[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of diagram generation."""
    diagrams: List[Diagram] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class GenerationStatus:
    """Status of diagram generation."""
    in_progress: bool = False
    current_diagram: Optional[DiagramType] = None
    completed_diagrams: List[DiagramType] = field(default_factory=list)
    failed_diagrams: List[DiagramType] = field(default_factory=list)


@dataclass
class TypeHints:
    """Type hints for a function."""
    parameters: Dict[str, str] = field(default_factory=dict)
    return_type: Optional[str] = None


@dataclass
class Comment:
    """Inline comment information."""
    text: str
    line_number: int
    associated_node: Optional[str] = None


@dataclass
class State:
    """State in a state diagram."""
    name: str
    entry_action: Optional[str] = None
    exit_action: Optional[str] = None
    is_initial: bool = False
    is_final: bool = False


@dataclass
class Transition:
    """Transition in a state diagram."""
    from_state: str
    to_state: str
    trigger: str
    guard: Optional[str] = None
    action: Optional[str] = None


@dataclass
class AnalysisData:
    """Combined analysis data for diagram generation."""
    file_analyses: List[FileAnalysis] = field(default_factory=list)
    database_schema: Optional[DatabaseSchema] = None
    route_map: Optional[RouteMap] = None
    dependency_graph: Optional[DependencyGraph] = None


@dataclass
class DiagramData:
    """Generic diagram data structure."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of syntax validation."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
