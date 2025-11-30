"""Component diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class ComponentDiagramGenerator(DiagramGenerator):
    """Generates component dependency diagrams."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.COMPONENT
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = []
        edges = []
        
        # Create nodes for major components
        components = set()
        for file_analysis in analysis_data.file_analyses:
            parts = file_analysis.file_path.split('/')
            if len(parts) > 1:
                component = parts[1] if parts[0] in ['app', 'src'] else parts[0]
                components.add(component)
        
        for component in components:
            nodes.append(Node(id=component, label=component.title(), type="component"))
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="TD")
        return self._create_diagram("Component Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
