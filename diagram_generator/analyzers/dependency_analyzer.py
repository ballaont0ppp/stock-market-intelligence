"""Dependency analyzer for building module dependency graphs."""

from typing import List, Dict, Set
from collections import defaultdict

from diagram_generator.core.types import (
    DependencyGraph,
    Cycle,
    CouplingMetrics,
    LayerMap,
    FileAnalysis,
    Node,
    Edge,
)


class DependencyAnalyzer:
    """Analyzes module dependencies and builds dependency graphs."""
    
    def __init__(self):
        self._layer_keywords = {
            'presentation': ['routes', 'views', 'templates', 'forms', 'api'],
            'business_logic': ['services', 'managers', 'engines', 'processors'],
            'data_access': ['models', 'repositories', 'database', 'db']
        }
    
    def build_dependency_graph(self, analyses: List[FileAnalysis]) -> DependencyGraph:
        """Build complete dependency graph from file analyses.
        
        Args:
            analyses: List of FileAnalysis objects
            
        Returns:
            DependencyGraph object
        """
        nodes = []
        edges = []
        
        # Create nodes for each module
        module_map = {}
        for analysis in analyses:
            node = Node(
                id=analysis.module_name,
                label=analysis.module_name,
                type='module'
            )
            nodes.append(node)
            module_map[analysis.module_name] = analysis
        
        # Create edges for dependencies
        for analysis in analyses:
            for import_info in analysis.imports:
                # Check if this is an internal import
                if not import_info.is_external:
                    # Create edge from this module to imported module
                    edge = Edge(
                        from_node=analysis.module_name,
                        to_node=import_info.module,
                        label='imports',
                        type='dependency'
                    )
                    edges.append(edge)
        
        return DependencyGraph(nodes=nodes, edges=edges)
    
    def detect_circular_dependencies(self, graph: DependencyGraph) -> List[Cycle]:
        """Detect circular dependency cycles.
        
        Args:
            graph: DependencyGraph object
            
        Returns:
            List of Cycle objects representing circular dependencies
        """
        # Build adjacency list
        adj_list = defaultdict(list)
        for edge in graph.edges:
            adj_list[edge.from_node].append(edge.to_node)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle_modules = path[cycle_start:] + [neighbor]
                    cycles.append(Cycle(modules=cycle_modules))
            
            path.pop()
            rec_stack.remove(node)
        
        # Run DFS from each unvisited node
        for node in graph.nodes:
            if node.id not in visited:
                dfs(node.id)
        
        return cycles
    
    def calculate_coupling(self, module: str, graph: DependencyGraph) -> CouplingMetrics:
        """Calculate coupling metrics for a module.
        
        Args:
            module: Module name
            graph: DependencyGraph object
            
        Returns:
            CouplingMetrics object
        """
        afferent = 0  # Modules that depend on this module
        efferent = 0  # Modules this module depends on
        
        for edge in graph.edges:
            if edge.to_node == module:
                afferent += 1
            if edge.from_node == module:
                efferent += 1
        
        # Calculate instability (0 = stable, 1 = unstable)
        total = afferent + efferent
        instability = efferent / total if total > 0 else 0.0
        
        return CouplingMetrics(
            afferent_coupling=afferent,
            efferent_coupling=efferent,
            instability=instability
        )
    
    def identify_layers(self, graph: DependencyGraph) -> LayerMap:
        """Identify architectural layers from module names.
        
        Args:
            graph: DependencyGraph object
            
        Returns:
            LayerMap object mapping layers to modules
        """
        layers = {
            'presentation': [],
            'business_logic': [],
            'data_access': [],
            'unknown': []
        }
        
        for node in graph.nodes:
            module_name = node.id.lower()
            layer_found = False
            
            # Check each layer's keywords
            for layer, keywords in self._layer_keywords.items():
                if any(keyword in module_name for keyword in keywords):
                    layers[layer].append(node.id)
                    layer_found = True
                    break
            
            if not layer_found:
                layers['unknown'].append(node.id)
        
        return LayerMap(layers=layers)
