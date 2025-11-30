"""Mermaid formatter for converting diagram data to Mermaid syntax."""

from typing import List
import re

from diagram_generator.core.types import (
    Node,
    Edge,
    Entity,
    Relationship,
    Participant,
    Message,
    State,
    Transition,
    ValidationResult,
)


class MermaidFormatter:
    """Formats diagram data into Mermaid syntax."""
    
    def format_graph(self, nodes: List[Node], edges: List[Edge], direction: str = "TD") -> str:
        """Format a graph diagram.
        
        Args:
            nodes: List of Node objects
            edges: List of Edge objects
            direction: Graph direction (TD, LR, etc.)
            
        Returns:
            Mermaid syntax string
        """
        lines = [f"graph {direction}"]
        
        # Add nodes
        for node in nodes:
            node_id = self.escape_text(node.id)
            label = self.escape_text(node.label)
            lines.append(f"    {node_id}[{label}]")
        
        # Add edges
        for edge in edges:
            from_id = self.escape_text(edge.from_node)
            to_id = self.escape_text(edge.to_node)
            if edge.label:
                label = self.escape_text(edge.label)
                lines.append(f"    {from_id} -->|{label}| {to_id}")
            else:
                lines.append(f"    {from_id} --> {to_id}")
        
        return "\n".join(lines)
    
    def format_er_diagram(self, entities: List[Entity], relationships: List[Relationship]) -> str:
        """Format an ER diagram.
        
        Args:
            entities: List of Entity objects
            relationships: List of Relationship objects
            
        Returns:
            Mermaid syntax string
        """
        lines = ["erDiagram"]
        
        # Add entities with attributes
        for entity in entities:
            lines.append(f"    {entity.name} {{")
            for column in entity.columns:
                pk_marker = " PK" if column.name in entity.primary_keys else ""
                fk_marker = " FK" if any(fk.column == column.name for fk in entity.foreign_keys) else ""
                lines.append(f"        {column.type} {column.name}{pk_marker}{fk_marker}")
            lines.append("    }")
        
        # Add relationships
        for rel in relationships:
            cardinality_map = {
                'ONE_TO_ONE': '||--||',
                'ONE_TO_MANY': '||--o{',
                'MANY_TO_ONE': '}o--||',
                'MANY_TO_MANY': '}o--o{'
            }
            symbol = cardinality_map.get(rel.cardinality.name, '||--||')
            lines.append(f"    {rel.source_entity} {symbol} {rel.target_entity} : {rel.name}")
        
        return "\n".join(lines)
    
    def format_sequence_diagram(self, participants: List[Participant], messages: List[Message]) -> str:
        """Format a sequence diagram.
        
        Args:
            participants: List of Participant objects
            messages: List of Message objects
            
        Returns:
            Mermaid syntax string
        """
        lines = ["sequenceDiagram"]
        
        # Add participants
        for participant in participants:
            lines.append(f"    participant {participant.name}")
        
        # Add messages
        for message in messages:
            arrow = "-->>" if message.is_return else "->>"
            lines.append(f"    {message.from_participant} {arrow} {message.to_participant}: {message.message}")
        
        return "\n".join(lines)
    
    def format_state_diagram(self, states: List[State], transitions: List[Transition]) -> str:
        """Format a state diagram.
        
        Args:
            states: List of State objects
            transitions: List of Transition objects
            
        Returns:
            Mermaid syntax string
        """
        lines = ["stateDiagram-v2"]
        
        # Add initial state
        for state in states:
            if state.is_initial:
                lines.append(f"    [*] --> {state.name}")
        
        # Add transitions
        for transition in transitions:
            label = transition.trigger
            if transition.guard:
                label += f" [{transition.guard}]"
            lines.append(f"    {transition.from_state} --> {transition.to_state}: {label}")
        
        # Add final states
        for state in states:
            if state.is_final:
                lines.append(f"    {state.name} --> [*]")
        
        return "\n".join(lines)
    
    def format_class_diagram(self, nodes: List[Node], edges: List[Edge]) -> str:
        """Format a class diagram.
        
        Args:
            nodes: List of Node objects (representing classes)
            edges: List of Edge objects (representing relationships)
            
        Returns:
            Mermaid syntax string
        """
        lines = ["classDiagram"]
        
        # Add classes
        for node in nodes:
            lines.append(f"    class {node.id} {{")
            if 'attributes' in node.metadata:
                for attr in node.metadata['attributes']:
                    lines.append(f"        {attr}")
            if 'methods' in node.metadata:
                for method in node.metadata['methods']:
                    lines.append(f"        {method}()")
            lines.append("    }")
        
        # Add relationships
        for edge in edges:
            if edge.type == 'inheritance':
                lines.append(f"    {edge.to_node} <|-- {edge.from_node}")
            elif edge.type == 'composition':
                lines.append(f"    {edge.from_node} *-- {edge.to_node}")
            elif edge.type == 'aggregation':
                lines.append(f"    {edge.from_node} o-- {edge.to_node}")
            else:
                lines.append(f"    {edge.from_node} --> {edge.to_node}")
        
        return "\n".join(lines)
    
    def format_activity_diagram(self, nodes: List[Node], edges: List[Edge]) -> str:
        """Format an activity diagram.
        
        Args:
            nodes: List of Node objects (activities, decisions, loops)
            edges: List of Edge objects (flows)
            
        Returns:
            Mermaid syntax string
        """
        lines = ["flowchart TD"]
        
        # Add nodes
        for node in nodes:
            node_id = self.escape_text(node.id)
            label = self.escape_text(node.label)
            
            # Format based on node type
            if node.type == 'decision':
                lines.append(f"    {node_id}{{{label}}}")
            elif node.type == 'start':
                lines.append(f"    {node_id}([{label}])")
            elif node.type == 'end':
                lines.append(f"    {node_id}([{label}])")
            else:  # activity
                lines.append(f"    {node_id}[{label}]")
        
        # Add edges (flows)
        for edge in edges:
            from_id = self.escape_text(edge.from_node)
            to_id = self.escape_text(edge.to_node)
            if edge.label:
                label = self.escape_text(edge.label)
                lines.append(f"    {from_id} -->|{label}| {to_id}")
            else:
                lines.append(f"    {from_id} --> {to_id}")
        
        return "\n".join(lines)
    
    def escape_text(self, text: str) -> str:
        """Escape special characters for Mermaid.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Replace special characters that might break Mermaid syntax
        text = text.replace('"', "'")
        text = text.replace('\n', ' ')
        text = text.replace('[', '(')
        text = text.replace(']', ')')
        # Remove or replace other problematic characters
        text = re.sub(r'[<>{}]', '', text)
        return text
    
    def validate_syntax(self, mermaid_code: str) -> ValidationResult:
        """Validate Mermaid syntax.
        
        Args:
            mermaid_code: Mermaid code to validate
            
        Returns:
            ValidationResult object
        """
        errors = []
        warnings = []
        
        # Basic validation checks
        lines = mermaid_code.split('\n')
        
        if not lines:
            errors.append("Empty diagram")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check for diagram type declaration
        first_line = lines[0].strip()
        valid_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                      'stateDiagram', 'erDiagram', 'gantt', 'pie']
        
        if not any(first_line.startswith(t) for t in valid_types):
            errors.append(f"Invalid diagram type: {first_line}")
        
        # Check for balanced brackets
        open_brackets = mermaid_code.count('[') + mermaid_code.count('(') + mermaid_code.count('{')
        close_brackets = mermaid_code.count(']') + mermaid_code.count(')') + mermaid_code.count('}')
        
        if open_brackets != close_brackets:
            warnings.append("Unbalanced brackets detected")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
