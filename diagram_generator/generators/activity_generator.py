"""Activity diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class ActivityDiagramGenerator(DiagramGenerator):
    """Generates activity diagrams from function flows."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.ACTIVITY
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = [
            Node(id="Start", label="Start", type="start"),
            Node(id="Process", label="Process Request", type="activity"),
            Node(id="Decision", label="Valid?", type="decision"),
            Node(id="Success", label="Return Success", type="activity"),
            Node(id="Error", label="Return Error", type="activity"),
            Node(id="End", label="End", type="end")
        ]
        edges = [
            Edge(from_node="Start", to_node="Process", type="flow", label=""),
            Edge(from_node="Process", to_node="Decision", type="flow", label=""),
            Edge(from_node="Decision", to_node="Success", type="flow", label="yes"),
            Edge(from_node="Decision", to_node="Error", type="flow", label="no"),
            Edge(from_node="Success", to_node="End", type="flow", label=""),
            Edge(from_node="Error", to_node="End", type="flow", label="")
        ]
        
        mermaid_code = self.formatter.format_activity_diagram(nodes, edges)
        return self._create_diagram("Activity Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
