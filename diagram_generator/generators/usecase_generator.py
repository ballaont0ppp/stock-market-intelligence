"""Use case diagram generator."""

from pathlib import Path
from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class UseCaseDiagramGenerator(DiagramGenerator):
    """Generates use case diagrams from routes and authentication."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.USE_CASE
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = [Node(id="User", label="User", type="actor")]
        edges = []
        
        # Extract use cases from routes
        for file_analysis in analysis_data.file_analyses:
            if 'routes' in Path(file_analysis.file_path).parts:
                for func in file_analysis.functions:
                    use_case_id = func.name.replace('_', ' ').title()
                    nodes.append(Node(id=use_case_id, label=use_case_id, type="usecase"))
                    edges.append(Edge(from_node="User", to_node=use_case_id, type="association", label=""))
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="LR")
        return self._create_diagram("Use Case Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
