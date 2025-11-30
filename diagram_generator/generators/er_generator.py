"""ER diagram generator."""

from typing import List, Dict
from pathlib import Path

from diagram_generator.core.base_generator import DiagramGenerator
from diagram_generator.core.types import (
    AnalysisData,
    Diagram,
    DiagramType,
    Entity,
    Relationship,
    Column,
    ForeignKey,
    Cardinality,
)
from diagram_generator.formatters.mermaid_formatter import MermaidFormatter


class ERDiagramGenerator(DiagramGenerator):
    """Generates entity-relationship diagrams from database models."""
    
    def __init__(self):
        """Initialize the ER diagram generator."""
        self.formatter = MermaidFormatter()
    
    def get_diagram_type(self) -> DiagramType:
        """Return the diagram type."""
        return DiagramType.ER_DIAGRAM
    
    def generate(self, analysis_data: AnalysisData) -> Diagram:
        """Generate ER diagram from analysis data.
        
        Args:
            analysis_data: Combined analysis data from code analyzers
            
        Returns:
            Generated ER diagram
        """
        entities = []
        relationships = []
        
        # Extract entities from database models
        for file_analysis in analysis_data.file_analyses:
            # Only process model files
            if self._is_model_file(file_analysis.file_path):
                for class_info in file_analysis.classes:
                    entity = self._create_entity_from_class(class_info)
                    if entity:
                        entities.append(entity)
        
        # Extract relationships from entities
        relationships = self._extract_relationships(entities, analysis_data)
        
        # Generate Mermaid code
        mermaid_code = self.formatter.format_er_diagram(entities, relationships)
        
        # Create diagram
        source_files = [fa.file_path for fa in analysis_data.file_analyses if self._is_model_file(fa.file_path)]
        diagram = self._create_diagram(
            title="Entity Relationship Diagram",
            mermaid_code=mermaid_code,
            source_files=source_files
        )
        
        return diagram
    
    def _is_model_file(self, file_path: str) -> bool:
        """Check if a file is a model file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if it's a model file
        """
        path = Path(file_path)
        return 'models' in path.parts or path.stem.endswith('_model')
    
    def _create_entity_from_class(self, class_info) -> Entity:
        """Create an Entity from a class definition.
        
        Args:
            class_info: ClassInfo object
            
        Returns:
            Entity object or None if not a database model
        """
        # Check if this is a database model (has Column attributes)
        columns = []
        primary_keys = []
        foreign_keys = []
        
        for attr in class_info.attributes:
            # Parse attribute to extract column information
            column_info = self._parse_column_attribute(attr)
            if column_info:
                column = Column(
                    name=column_info['name'],
                    type=column_info['type'],
                    nullable=column_info.get('nullable', True),
                    unique=column_info.get('unique', False)
                )
                columns.append(column)
                
                if column_info.get('primary_key'):
                    primary_keys.append(column.name)
                
                if column_info.get('foreign_key'):
                    fk = ForeignKey(
                        column=column.name,
                        referenced_table=column_info['foreign_key']['table'],
                        referenced_column=column_info['foreign_key']['column']
                    )
                    foreign_keys.append(fk)
        
        # Only create entity if it has columns
        if columns:
            return Entity(
                name=class_info.name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys
            )
        
        return None
    
    def _parse_column_attribute(self, attr_str: str) -> Dict:
        """Parse a column attribute string to extract metadata.
        
        Args:
            attr_str: Attribute string (e.g., "user_id: int")
            
        Returns:
            Dictionary with column metadata or None
        """
        # Simple parsing - in real implementation, would use AST
        if ':' not in attr_str:
            return None
        
        parts = attr_str.split(':')
        name = parts[0].strip()
        type_info = parts[1].strip() if len(parts) > 1 else 'str'
        
        # Extract type
        column_type = type_info.split()[0] if type_info else 'str'
        
        # Check for common patterns
        is_primary_key = 'id' in name.lower() and name.endswith('_id') and name == name.split('_')[0] + '_id'
        is_foreign_key = name.endswith('_id') and not is_primary_key
        
        result = {
            'name': name,
            'type': column_type,
            'nullable': 'Optional' in type_info or 'None' in type_info,
            'unique': False,
            'primary_key': is_primary_key
        }
        
        if is_foreign_key:
            # Extract referenced table from name (e.g., user_id -> users)
            table_name = name.replace('_id', '') + 's'
            result['foreign_key'] = {
                'table': table_name,
                'column': table_name[:-1] + '_id'
            }
        
        return result
    
    def _extract_relationships(self, entities: List[Entity], analysis_data: AnalysisData) -> List[Relationship]:
        """Extract relationships between entities.
        
        Args:
            entities: List of entities
            analysis_data: Analysis data
            
        Returns:
            List of relationships
        """
        relationships = []
        entity_map = {e.name: e for e in entities}
        
        # Extract relationships from foreign keys
        for entity in entities:
            for fk in entity.foreign_keys:
                # Find the referenced entity
                referenced_entity_name = self._find_entity_by_table(fk.referenced_table, entity_map)
                
                if referenced_entity_name:
                    # Determine cardinality
                    cardinality = self._determine_cardinality(entity, fk, entity_map[referenced_entity_name])
                    
                    relationship = Relationship(
                        name=f"has_{entity.name}",
                        source_entity=referenced_entity_name,
                        target_entity=entity.name,
                        cardinality=cardinality
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _find_entity_by_table(self, table_name: str, entity_map: Dict[str, Entity]) -> str:
        """Find entity name by table name.
        
        Args:
            table_name: Table name
            entity_map: Map of entity names to entities
            
        Returns:
            Entity name or None
        """
        # Try direct match
        if table_name in entity_map:
            return table_name
        
        # Try singular form
        singular = table_name.rstrip('s')
        if singular in entity_map:
            return singular
        
        # Try capitalized versions
        for entity_name in entity_map.keys():
            if entity_name.lower() == table_name.lower():
                return entity_name
            if entity_name.lower() == singular.lower():
                return entity_name
        
        return None
    
    def _determine_cardinality(self, source_entity: Entity, fk: ForeignKey, target_entity: Entity) -> Cardinality:
        """Determine the cardinality of a relationship.
        
        Args:
            source_entity: Source entity
            fk: Foreign key
            target_entity: Target entity
            
        Returns:
            Cardinality enum value
        """
        # Check if the foreign key column is unique
        for column in source_entity.columns:
            if column.name == fk.column and column.unique:
                return Cardinality.ONE_TO_ONE
        
        # Default to many-to-one (most common)
        return Cardinality.MANY_TO_ONE
