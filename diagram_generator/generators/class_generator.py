"""Class diagram generator."""

from typing import List
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


class ClassDiagramGenerator(DiagramGenerator):
    """Generates UML class diagrams showing class structure and relationships."""
    
    def __init__(self):
        """Initialize the class diagram generator."""
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        """Return the diagram type."""
        return DiagramType.CLASS_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        """Generate class diagram from analysis data.
        
        Args:
            analysis_data: Combined analysis data from code analyzers
            
        Returns:
            Generated class diagram
        """
        nodes = []
        edges = []
        
        # Create nodes for each class
        for file_analysis in analysis_data.file_analyses:
            for class_info in file_analysis.classes:
                # Extract attributes and methods
                attributes = []
                methods = []
                
                for attr in class_info.attributes:
                    # Format attribute with visibility
                    visibility = self._get_visibility(attr)
                    attributes.append(f"{visibility}{attr}")
                
                for method in class_info.methods:
                    # Format method with visibility
                    visibility = self._get_visibility(method.name)
                    params = ', '.join(method.parameters)
                    return_type = f": {method.return_type}" if method.return_type else ""
                    methods.append(f"{visibility}{method.name}({params}){return_type}")
                
                # Create node
                node = Node(
                    id=class_info.name,
                    label=class_info.name,
                    type='class',
                    metadata={
                        'attributes': attributes,
                        'methods': methods,
                        'file_path': file_path
                    }
                )
                nodes.append(node)
                
                # Create edges for inheritance
                for base_class in class_info.base_classes:
                    edge = Edge(
                        from_node=class_info.name,
                        to_node=base_class,
                        type='inheritance',
                        label=''
                    )
                    edges.append(edge)
        
        # Generate Mermaid code
        mermaid_code = self.formatter.format_class_diagram(nodes, edges)
        
        # Create diagram
        source_files = [fa.file_path for fa in analysis_data.file_analyses]
        diagram = self._create_diagram(
            title="Class Diagram",
            mermaid_code=mermaid_code,
            source_files=source_files
        )
        
        return diagram
    
    def _get_visibility(self, name: str) -> str:
        """Determine visibility modifier for a member.
        
        Args:
            name: Member name
            
        Returns:
            Visibility symbol (+, -, #, ~)
        """
        if name.startswith('__') and not name.endswith('__'):
            return '-'  # Private
        elif name.startswith('_'):
            return '#'  # Protected
        else:
            return '+'  # Public
