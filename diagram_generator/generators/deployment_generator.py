"""Deployment diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class DeploymentDiagramGenerator(DiagramGenerator):
    """Generates deployment diagrams from configuration."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.DEPLOYMENT
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = [
            Node(id="WebServer", label="Web Server", type="node"),
            Node(id="AppServer", label="Application Server", type="node"),
            Node(id="DBServer", label="Database Server", type="node")
        ]
        edges = [
            Edge(from_node="WebServer", to_node="AppServer", type="connection", label="HTTP"),
            Edge(from_node="AppServer", to_node="DBServer", type="connection", label="SQL")
        ]
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="LR")
        return self._create_diagram("Deployment Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
