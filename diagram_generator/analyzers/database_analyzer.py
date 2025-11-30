"""Database analyzer for parsing SQLAlchemy models."""

import ast
import re
from typing import List, Optional

from diagram_generator.core.types import (
    DatabaseSchema,
    Entity,
    Column,
    ForeignKey,
    Relationship,
    Cardinality,
    RelationshipType,
    ClassInfo,
    FileAnalysis,
)
from diagram_generator.core.exceptions import AnalysisError
from diagram_generator.analyzers.code_analyzer import CodeAnalyzer


class DatabaseAnalyzer:
    """Analyzes SQLAlchemy database models."""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self._sqlalchemy_types = {
            'Integer', 'String', 'Text', 'Boolean', 'DateTime', 'Date', 'Time',
            'Float', 'Numeric', 'BigInteger', 'SmallInteger', 'Binary', 'LargeBinary',
            'Enum', 'JSON', 'ARRAY', 'UUID'
        }
    
    def analyze_models(self, model_files: List[str]) -> DatabaseSchema:
        """Analyze database model files.
        
        Args:
            model_files: List of paths to model files
            
        Returns:
            DatabaseSchema object containing all entities
        """
        entities = []
        
        for file_path in model_files:
            try:
                # Analyze the file
                analysis = self.code_analyzer.analyze_file(file_path)
                
                # Extract entities from classes
                for class_info in analysis.classes:
                    if self._is_model_class(class_info):
                        entity = self.extract_entities(class_info)
                        entities.append(entity)
            
            except Exception as e:
                # Log error but continue with other files
                print(f"Warning: Error analyzing {file_path}: {str(e)}")
                continue
        
        return DatabaseSchema(entities=entities)
    
    def extract_entities(self, class_def: ClassInfo) -> Entity:
        """Extract entity information from model class.
        
        Args:
            class_def: ClassInfo object for the model class
            
        Returns:
            Entity object with extracted information
        """
        # Extract table name
        table_name = self._extract_table_name(class_def)
        
        # Extract columns
        columns = self.extract_columns(class_def)
        
        # Extract primary keys
        primary_keys = self._extract_primary_keys(columns)
        
        # Extract foreign keys
        foreign_keys = self._extract_foreign_keys(columns)
        
        # Extract relationships
        relationships = self.extract_relationships(class_def)
        
        return Entity(
            name=class_def.name,
            table_name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            relationships=relationships,
            docstring=class_def.docstring
        )
    
    def extract_relationships(self, class_def: ClassInfo) -> List[Relationship]:
        """Extract relationships between entities.
        
        Args:
            class_def: ClassInfo object for the model class
            
        Returns:
            List of Relationship objects
        """
        relationships = []
        
        # Look for relationship() calls in attributes
        for attr in class_def.attributes:
            # Check if this is a relationship attribute
            # This is a simplified check - in real code, we'd parse the AST more carefully
            if 'relationship' in str(attr.type_hint):
                # Extract target entity from type hint or attribute name
                target_entity = self._extract_relationship_target(attr)
                
                if target_entity:
                    # Infer cardinality (simplified)
                    cardinality = self._infer_cardinality_simple(attr)
                    
                    relationship = Relationship(
                        name=attr.name,
                        source_entity=class_def.name,
                        target_entity=target_entity,
                        cardinality=cardinality,
                        relationship_type=RelationshipType.ASSOCIATION
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def extract_columns(self, class_def: ClassInfo) -> List[Column]:
        """Extract column definitions from model class.
        
        Args:
            class_def: ClassInfo object for the model class
            
        Returns:
            List of Column objects
        """
        columns = []
        
        for attr in class_def.attributes:
            # Check if this is a Column attribute
            if self._is_column_attribute(attr):
                column = self._parse_column(attr)
                if column:
                    columns.append(column)
        
        return columns
    
    def infer_cardinality(self, relationship: Relationship) -> Cardinality:
        """Infer relationship cardinality.
        
        Args:
            relationship: Relationship object
            
        Returns:
            Cardinality enum value
        """
        # This is a simplified implementation
        # In a real implementation, we'd analyze the relationship definition more carefully
        return relationship.cardinality
    
    def _is_model_class(self, class_info: ClassInfo) -> bool:
        """Check if a class is a database model."""
        # Check if it inherits from common base classes
        base_names = ['Model', 'Base', 'db.Model', 'DeclarativeBase']
        
        for base in class_info.bases:
            if any(base_name in base for base_name in base_names):
                return True
        
        # Check if it has Column attributes
        for attr in class_info.attributes:
            if self._is_column_attribute(attr):
                return True
        
        return False
    
    def _extract_table_name(self, class_def: ClassInfo) -> str:
        """Extract table name from model class."""
        # Look for __tablename__ attribute
        for attr in class_def.attributes:
            if attr.name == '__tablename__':
                if attr.value:
                    # Remove quotes from string value
                    return attr.value.strip('"\'')
        
        # Default to lowercase class name with 's' suffix
        return class_def.name.lower() + 's'
    
    def _is_column_attribute(self, attr) -> bool:
        """Check if an attribute is a Column."""
        if attr.type_hint:
            type_str = str(attr.type_hint)
            return 'Column' in type_str or any(t in type_str for t in self._sqlalchemy_types)
        return False
    
    def _parse_column(self, attr) -> Optional[Column]:
        """Parse column information from attribute."""
        # Extract column type
        col_type = self._extract_column_type(attr)
        
        if not col_type:
            return None
        
        # Default values
        nullable = True
        unique = False
        default = None
        constraints = []
        
        # Try to extract additional information from type hint or value
        # This is simplified - real implementation would parse AST more carefully
        if attr.type_hint:
            type_str = str(attr.type_hint)
            if 'nullable=False' in type_str:
                nullable = False
            if 'unique=True' in type_str:
                unique = True
        
        return Column(
            name=attr.name,
            type=col_type,
            nullable=nullable,
            unique=unique,
            default=default,
            constraints=constraints
        )
    
    def _extract_column_type(self, attr) -> Optional[str]:
        """Extract column type from attribute."""
        if not attr.type_hint:
            return None
        
        type_str = str(attr.type_hint)
        
        # Look for SQLAlchemy types
        for sql_type in self._sqlalchemy_types:
            if sql_type in type_str:
                return sql_type
        
        return 'Unknown'
    
    def _extract_primary_keys(self, columns: List[Column]) -> List[str]:
        """Extract primary key column names."""
        # Simplified: look for columns named 'id' or ending with '_id'
        primary_keys = []
        
        for col in columns:
            if col.name == 'id' or col.name.endswith('_id'):
                # Check if it's likely a primary key
                if not col.nullable:
                    primary_keys.append(col.name)
        
        # If no primary keys found, assume 'id' if it exists
        if not primary_keys:
            for col in columns:
                if col.name == 'id':
                    primary_keys.append(col.name)
                    break
        
        return primary_keys
    
    def _extract_foreign_keys(self, columns: List[Column]) -> List[ForeignKey]:
        """Extract foreign key information."""
        foreign_keys = []
        
        # Look for columns that end with '_id' (common convention)
        for col in columns:
            if col.name.endswith('_id') and col.name != 'id':
                # Infer referenced table from column name
                # e.g., 'user_id' -> 'users' table
                table_prefix = col.name[:-3]  # Remove '_id'
                referenced_table = table_prefix + 's'  # Add 's' for plural
                
                foreign_key = ForeignKey(
                    column=col.name,
                    referenced_table=referenced_table,
                    referenced_column='id'
                )
                foreign_keys.append(foreign_key)
        
        return foreign_keys
    
    def _extract_relationship_target(self, attr) -> Optional[str]:
        """Extract target entity from relationship attribute."""
        # Try to extract from type hint
        if attr.type_hint:
            type_str = str(attr.type_hint)
            # Look for class name in quotes or as identifier
            match = re.search(r"['\"](\w+)['\"]", type_str)
            if match:
                return match.group(1)
        
        # Try to infer from attribute name
        # e.g., 'user' -> 'User', 'orders' -> 'Order'
        name = attr.name
        if name:
            # Capitalize first letter and remove trailing 's'
            if name.endswith('s'):
                name = name[:-1]
            return name.capitalize()
        
        return None
    
    def _infer_cardinality_simple(self, attr) -> Cardinality:
        """Infer cardinality from attribute (simplified)."""
        # Check if attribute name is plural (suggests one-to-many)
        if attr.name and attr.name.endswith('s'):
            return Cardinality.ONE_TO_MANY
        
        # Default to many-to-one
        return Cardinality.MANY_TO_ONE
