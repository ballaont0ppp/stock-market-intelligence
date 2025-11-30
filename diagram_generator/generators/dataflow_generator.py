"""Data flow diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class DataFlowDiagramGenerator(DiagramGenerator):
    """Generates data flow diagrams showing data movement through the system."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.DATA_FLOW
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = [
            Node(id="User", label="User", type="external"),
            Node(id="System", label="System", type="process"),
            Node(id="Database", label="Database", type="datastore")
        ]
        edges = [
            Edge(from_node="User", to_node="System", type="dataflow", label="requests"),
            Edge(from_node="System", to_node="Database", type="dataflow", label="queries"),
            Edge(from_node="Database", to_node="System", type="dataflow", label="data"),
            Edge(from_node="System", to_node="User", type="dataflow", label="responses")
        ]
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="LR")
        return self._create_diagram("Data Flow Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
