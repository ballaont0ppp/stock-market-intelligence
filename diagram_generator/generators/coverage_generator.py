"""Test coverage diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class TestCoverageDiagramGenerator(DiagramGenerator):
    """Generates test coverage visualizations."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.TEST_COVERAGE
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = []
        edges = []
        
        # Analyze test coverage (simplified)
        for file_analysis in analysis_data.file_analyses:
            if 'test' not in file_analysis.file_path:
                module_name = file_analysis.file_path.replace('/', '_').replace('.py', '')
                # Assume 80% coverage for demo
                coverage = 80
                color = "green" if coverage >= 80 else "yellow" if coverage >= 60 else "red"
                
                nodes.append(Node(
                    id=module_name,
                    label=f"{module_name} ({coverage}%)",
                    type="module",
                    metadata={'coverage': coverage, 'color': color}
                ))
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="TD")
        return self._create_diagram("Test Coverage Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
