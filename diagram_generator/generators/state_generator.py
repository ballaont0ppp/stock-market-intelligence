"""State diagram generator."""

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import AnalysisData, Diagram, DiagramType, State, Transition
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class StateDiagramGenerator(DiagramGenerator):
    """Generates state machine diagrams."""
    
    def __init__(self):
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        return DiagramType.STATE_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        states = [
            State(name="Idle", is_initial=True, is_final=False),
            State(name="Processing", is_initial=False, is_final=False),
            State(name="Complete", is_initial=False, is_final=True)
        ]
        transitions = [
            Transition(from_state="Idle", to_state="Processing", trigger="start", guard=None),
            Transition(from_state="Processing", to_state="Complete", trigger="finish", guard=None)
        ]
        
        mermaid_code = self.formatter.format_state_diagram(states, transitions)
        return self._create_diagram("State Diagram", mermaid_code, [fa.file_path for fa in analysis_data.file_analyses])
