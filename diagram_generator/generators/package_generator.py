"""Package diagram generator."""

from pathlib import Path
from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, Node, Edge
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class PackageDiagramGenerator(DiagramGenerator):
    """Generates package structure diagrams."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.PACKAGE
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        nodes = []
        edges = []
        packages = set()
        
        # Extract package structure from file paths
        for file_analysis in analysis_data.file_analyses:
            path = Path(file_analysis.file_path)
            if len(path.parts) > 1:
                package = '/'.join(path.parts[:-1])
                packages.add(package)
        
        for package in sorted(packages):
            package_id = package.replace('/', '_')
            nodes.append(Node(id=package_id, label=package, type="package"))
        
        mermaid_code = self.formatter.format_graph(nodes, edges, direction="TD")
        return self._create_diagram("Package Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
