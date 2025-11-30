"""Base class for all diagram generators."""

from abc import ABC, abstractmethod
from typing import Optional

from .types import (
    AnalysisData,
    Diagram,
    DiagramData,
    DiagramMetadata,
    DiagramType,
)


class DiagramGenerator(ABC):
    """Abstract base class for diagram generators."""
    
    @abstractmethod
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        """Generate diagram from analysis data.
        
        Args:
            analysis_data: Combined analysis data from code analyzers
            
        Returns:
            Generated diagram with Mermaid code
        """
        pass
    
    @abstractmethod
    def get_diagram_type(self) -> DiagramType:
        """Return the type of diagram this generator creates.
        
        Returns:
            DiagramType enum value
        """
        pass
    
    def format_mermaid(self, diagram_data: DiagramData) -> str:
        """Convert diagram data to Mermaid syntax.
        
        This is a basic implementation that can be overridden by subclasses.
        
        Args:
            diagram_data: Generic diagram data structure
            
        Returns:
            Mermaid syntax string
        """
        lines = []
        
        # Add nodes
        for node in diagram_data.nodes:
            lines.append(f"    {node.id}[{node.label}]")
        
        # Add edges
        for edge in diagram_data.edges:
            if edge.label:
                lines.append(f"    {edge.from_node} -->|{edge.label}| {edge.to_node}")
            else:
                lines.append(f"    {edge.from_node} --> {edge.to_node}")
        
        return "\n".join(lines)
    
    def add_metadata(self, diagram: Diagram) -> Diagram:
        """Add generation metadata to diagram.
        
        Args:
            diagram: Diagram to add metadata to
            
        Returns:
            Diagram with updated metadata
        """
        if diagram.metadata is None:
            diagram.metadata = DiagramMetadata()
        
        return diagram
    
    def _create_diagram(
        self,
        title: str,
        mermaid_code: str,
        source_files: Optional[list] = None
    ) -> Diagram:
        """Helper method to create a diagram with metadata.
        
        Args:
            title: Diagram title
            mermaid_code: Generated Mermaid code
            source_files: List of source files used
            
        Returns:
            Diagram object with metadata
        """
        diagram = Diagram(
            diagram_type=self.get_diagram_type(),
            title=title,
            mermaid_code=mermaid_code,
            source_files=source_files or [],
            metadata=DiagramMetadata()
        )
        
        return self.add_metadata(diagram)
