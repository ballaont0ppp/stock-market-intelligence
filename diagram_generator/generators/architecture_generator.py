"""Architecture diagram generator."""

from typing import List, Set, Dict
from pathlib import Path

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import (
    AnalysisData,
    Diagram,
    DiagramType,
    Node,
    Edge,
)
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class ArchitectureDiagramGenerator(DiagramGenerator):
    """Generates component architecture diagrams showing system structure and layers."""
    
    def __init__(self):
        """Initialize the architecture diagram generator."""
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        """Return the diagram type."""
        return DiagramType.ARCHITECTURE
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        """Generate architecture diagram from analysis data.
        
        Args:
            analysis_data: Combined analysis data from code analyzers
            
        Returns:
            Generated architecture diagram
        """
        nodes = []
        edges = []
        
        # Identify architectural layers
        layers = self._identify_layers(analysis_data)
        
        # Create nodes for each module/component
        for file_analysis in analysis_data.file_analyses:
            file_path = file_analysis.file_path
            layer = self._determine_layer(file_path, layers)
            module_name = self._get_module_name(file_path)
            
            # Create node for this module
            node = Node(
                id=module_name,
                label=module_name,
                type='component',
                metadata={'layer': layer, 'file_path': file_path}
            )
            nodes.append(node)
        
        # Create edges for dependencies
        for file_analysis in analysis_data.file_analyses:
            file_path = file_analysis.file_path
            from_module = self._get_module_name(file_path)
            
            # Add edges for imports
            for import_info in file_analysis.imports:
                # Check if this is an internal import
                if self._is_internal_import(import_info.module, analysis_data):
                    to_module = self._normalize_module_name(import_info.module)
                    
                    edge = Edge(
                        from_node=from_module,
                        to_node=to_module,
                        type='dependency',
                        label=''
                    )
                    edges.append(edge)
        
        # Remove duplicate edges
        edges = self._deduplicate_edges(edges)
        
        # Mark external dependencies
        external_deps = self._identify_external_dependencies(analysis_data)
        for dep in external_deps:
            node = Node(
                id=dep,
                label=dep,
                type='external',
                metadata={'external': True}
            )
            nodes.append(node)
        
        # Generate Mermaid code
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="TD")
        
        # Create diagram
        source_files = [fa.file_path for fa in analysis_data.file_analyses]
        diagram = self._create_diagram(
            title="System Architecture",
            mermaid_code=mermaid_code,
            source_files=source_files
        )
        
        return diagram
    
    def _identify_layers(self, analysis_data: AnalysisData) -> Dict[str, str]:
        """Identify architectural layers in the codebase.
        
        Args:
            analysis_data: Analysis data
            
        Returns:
            Dictionary mapping layer names to patterns
        """
        layers = {
            'routes': 'presentation',
            'services': 'business',
            'models': 'data',
            'utils': 'infrastructure',
            'forms': 'presentation',
            'jobs': 'infrastructure',
            'templates': 'presentation',
        }
        return layers
    
    def _determine_layer(self, file_path: str, layers: Dict[str, str]) -> str:
        """Determine which layer a file belongs to.
        
        Args:
            file_path: Path to the file
            layers: Layer mapping
            
        Returns:
            Layer name
        """
        path_parts = Path(file_path).parts
        
        for part in path_parts:
            if part in layers:
                return layers[part]
        
        return 'other'
    
    def _get_module_name(self, file_path: str) -> str:
        """Extract module name from file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Module name
        """
        path = Path(file_path)
        # Remove .py extension and convert to module notation
        module_parts = list(path.parts[:-1]) + [path.stem]
        
        # Remove common prefixes
        if module_parts and module_parts[0] in ['app', 'src']:
            module_parts = module_parts[1:]
        
        return '.'.join(module_parts)
    
    def _normalize_module_name(self, module: str) -> str:
        """Normalize module name for consistency.
        
        Args:
            module: Module name
            
        Returns:
            Normalized module name
        """
        # Remove leading dots from relative imports
        module = module.lstrip('.')
        
        # Remove common prefixes
        if module.startswith('app.'):
            module = module[4:]
        elif module.startswith('src.'):
            module = module[4:]
        
        return module
    
    def _is_internal_import(self, module: str, analysis_data: AnalysisData) -> bool:
        """Check if an import is internal to the project.
        
        Args:
            module: Module name
            analysis_data: Analysis data
            
        Returns:
            True if internal, False if external
        """
        # Check if module starts with project-specific prefixes
        internal_prefixes = ['app', 'src', '.']
        
        for prefix in internal_prefixes:
            if module.startswith(prefix):
                return True
        
        # Check if module exists in analyzed files
        normalized = self._normalize_module_name(module)
        for file_analysis in analysis_data.file_analyses:
            if normalized in self._get_module_name(file_analysis.file_path):
                return True
        
        return False
    
    def _identify_external_dependencies(self, analysis_data: AnalysisData) -> Set[str]:
        """Identify external dependencies.
        
        Args:
            analysis_data: Analysis data
            
        Returns:
            Set of external dependency names
        """
        external_deps = set()
        
        for file_analysis in analysis_data.file_analyses:
            for import_info in file_analysis.imports:
                if not self._is_internal_import(import_info.module, analysis_data):
                    # Get top-level package name
                    top_level = import_info.module.split('.')[0]
                    external_deps.add(top_level)
        
        return external_deps
    
    def _deduplicate_edges(self, edges: List[Edge]) -> List[Edge]:
        """Remove duplicate edges.
        
        Args:
            edges: List of edges
            
        Returns:
            Deduplicated list of edges
        """
        seen = set()
        unique_edges = []
        
        for edge in edges:
            key = (edge.from_node, edge.to_node, edge.type)
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)
        
        return unique_edges
