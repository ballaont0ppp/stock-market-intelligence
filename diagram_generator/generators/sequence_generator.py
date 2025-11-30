"""Sequence diagram generator."""

from typing import List, Set
from pathlib import Path

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import (
    AnalysisData,
    Diagram,
    DiagramType,
    Participant,
    Message,
)
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class SequenceDiagramGenerator(DiagramGenerator):
    """Generates sequence diagrams from route handlers and request flows."""
    
    def __init__(self):
        """Initialize the sequence diagram generator."""
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        """Return the diagram type."""
        return DiagramType.SEQUENCE_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        """Generate sequence diagram from analysis data.
        
        Args:
            analysis_data: Combined analysis data from code analyzers
            
        Returns:
            Generated sequence diagram
        """
        participants = []
        messages = []
        seen_participants = set()
        
        # Extract routes and trace their execution
        for file_analysis in analysis_data.file_analyses:
            if self._is_route_file(file_analysis.file_path):
                for func in file_analysis.functions:
                    if self._is_route_handler(func):
                        # Add client as participant
                        if 'Client' not in seen_participants:
                            participants.append(Participant(name='Client', type='actor'))
                            seen_participants.add('Client')
                        
                        # Add route handler as participant
                        handler_name = func.name
                        if handler_name not in seen_participants:
                            participants.append(Participant(name=handler_name, type='controller'))
                            seen_participants.add(handler_name)
                        
                        # Add initial request message
                        messages.append(Message(
                            from_participant='Client',
                            to_participant=handler_name,
                            message=f"{func.name}()",
                            is_return=False
                        ))
                        
                        # Trace function calls within the handler
                        for call in func.calls:
                            # Determine participant type
                            participant_type = self._determine_participant_type(call)
                            
                            if call not in seen_participants:
                                participants.append(Participant(name=call, type=participant_type))
                                seen_participants.add(call)
                            
                            # Add message
                            messages.append(Message(
                                from_participant=handler_name,
                                to_participant=call,
                                message=f"{call}()",
                                is_return=False
                            ))
                            
                            # Add return message
                            messages.append(Message(
                                from_participant=call,
                                to_participant=handler_name,
                                message="result",
                                is_return=True
                            ))
                        
                        # Add response to client
                        messages.append(Message(
                            from_participant=handler_name,
                            to_participant='Client',
                            message="response",
                            is_return=True
                        ))
        
        # Generate Mermaid code
        mermaid_code = self.formatter.format_sequence_diagram(participants, messages)
        
        # Create diagram
        source_files = [fa.file_path for fa in analysis_data.file_analyses if self._is_route_file(fa.file_path)]
        diagram = self._create_diagram(
            title="Sequence Diagram",
            mermaid_code=mermaid_code,
            source_files=source_files
        )
        
        return diagram
    
    def _is_route_file(self, file_path: str) -> bool:
        """Check if a file contains routes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if it's a route file
        """
        path = Path(file_path)
        return 'routes' in path.parts or 'views' in path.parts
    
    def _is_route_handler(self, func) -> bool:
        """Check if a function is a route handler.
        
        Args:
            func: FunctionInfo object
            
        Returns:
            True if it's a route handler
        """
        # Check for route decorators
        for decorator in func.decorators:
            if 'route' in decorator.lower() or 'get' in decorator.lower() or 'post' in decorator.lower():
                return True
        return False
    
    def _determine_participant_type(self, call_name: str) -> str:
        """Determine the type of participant based on call name.
        
        Args:
            call_name: Name of the called function/method
            
        Returns:
            Participant type
        """
        if 'service' in call_name.lower():
            return 'service'
        elif 'repository' in call_name.lower() or 'model' in call_name.lower():
            return 'database'
        elif 'api' in call_name.lower() or 'client' in call_name.lower():
            return 'external'
        else:
            return 'component'
