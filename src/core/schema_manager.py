"""Schema Manager

Manages extraction schemas including loading, validation, caching, and persistence.
Provides centralized access to all extraction schemas.
"""

import json
import yaml
import os
from typing import Dict, List, Optional, Any, Type, Union
from pathlib import Path
import logging
from datetime import datetime

from .extraction_schemas import (
    ExtractionSchema, OpenSchema, ClosedSchema, HybridSchema,
    SchemaMode, EntityTypeSchema, RelationTypeSchema,
    create_open_schema, create_closed_schema, create_hybrid_schema,
    get_academic_paper_schema, get_business_document_schema, get_general_open_schema
)

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages extraction schemas with loading, validation, and caching"""
    
    def __init__(self, schema_directory: Optional[str] = None):
        """Initialize schema manager
        
        Args:
            schema_directory: Directory containing schema files (JSON/YAML)
        """
        if schema_directory is None:
            from .standard_config import get_file_path
            schema_directory = f"{get_file_path('config_dir')}/schemas"
        self.schema_directory = schema_directory
        self.schemas: Dict[str, ExtractionSchema] = {}
        self.default_schema_id: Optional[str] = None
        
        # Create schema directory if it doesn't exist
        Path(self.schema_directory).mkdir(parents=True, exist_ok=True)
        
        # Load built-in schemas
        self._load_builtin_schemas()
        
        # Load schemas from files
        self._load_schemas_from_directory()
        
        logger.info(f"SchemaManager initialized with {len(self.schemas)} schemas")
    
    def _load_builtin_schemas(self):
        """Load built-in schema templates"""
        self.schemas.update({
            "general_open": get_general_open_schema(),
            "academic_paper": get_academic_paper_schema(),
            "business_document": get_business_document_schema()
        })
        
        # Set default schema
        self.default_schema_id = "general_open"
    
    def _load_schemas_from_directory(self):
        """Load schemas from schema directory"""
        if not os.path.exists(self.schema_directory):
            return
        
        for filename in os.listdir(self.schema_directory):
            if filename.endswith(('.json', '.yaml', '.yml')):
                filepath = os.path.join(self.schema_directory, filename)
                try:
                    schema = self.load_schema_from_file(filepath)
                    if schema:
                        self.schemas[schema.schema_id] = schema
                        logger.info(f"Loaded schema '{schema.schema_id}' from {filename}")
                except Exception as e:
                    logger.error(f"Failed to load schema from {filename}: {e}")
    
    def load_schema_from_file(self, filepath: str) -> Optional[ExtractionSchema]:
        """Load schema from JSON or YAML file
        
        Args:
            filepath: Path to schema file
            
        Returns:
            Loaded schema or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    data = json.load(f)
                else:  # YAML
                    data = yaml.safe_load(f)
            
            return self._create_schema_from_dict(data)
        
        except Exception as e:
            logger.error(f"Failed to load schema from {filepath}: {e}")
            return None
    
    def _create_schema_from_dict(self, data: Dict[str, Any]) -> ExtractionSchema:
        """Create schema object from dictionary data"""
        mode = SchemaMode(data['mode'])
        schema_id = data['schema_id']
        
        # Common parameters
        common_params = {
            'description': data.get('description', ''),
            'inheritance_enabled': data.get('inheritance_enabled', True),
            'auto_infer_hierarchy': data.get('auto_infer_hierarchy', False),
            'entity_hierarchy': data.get('entity_hierarchy', {}),
            'global_confidence_threshold': data.get('global_confidence_threshold', 0.0)  # Lowered to 0 for initial development
        }
        
        # Create schema based on mode
        if mode == SchemaMode.OPEN:
            schema = OpenSchema(schema_id=schema_id, **common_params)
            schema.discovery_constraints = data.get('discovery_constraints', {})
        
        elif mode == SchemaMode.CLOSED:
            schema = ClosedSchema(schema_id=schema_id, **common_params)
        
        else:  # HYBRID
            schema = HybridSchema(schema_id=schema_id, **common_params)
            schema.discovery_confidence_threshold = data.get('discovery_confidence_threshold', 0.7)
            schema.max_discoveries = data.get('max_discoveries', 10)
        
        # Load entity types
        for entity_name, entity_data in data.get('entity_types', {}).items():
            schema.entity_types[entity_name] = EntityTypeSchema(
                type_name=entity_name,
                parent_type=entity_data.get('parent_type'),
                required_properties=entity_data.get('required_properties', []),
                optional_properties=entity_data.get('optional_properties', []),
                validation_rules=entity_data.get('validation_rules', {}),
                confidence_threshold=entity_data.get('confidence_threshold', 0.6)
            )
        
        # Load relation types
        for relation_name, relation_data in data.get('relation_types', {}).items():
            schema.relation_types[relation_name] = RelationTypeSchema(
                type_name=relation_name,
                source_entity_types=relation_data.get('source_entity_types', []),
                target_entity_types=relation_data.get('target_entity_types', []),
                properties=relation_data.get('properties', []),
                confidence_threshold=relation_data.get('confidence_threshold', 0.6),
                directional=relation_data.get('directional', True)
            )
        
        return schema
    
    def save_schema_to_file(self, schema: ExtractionSchema, filepath: str, format: str = 'json'):
        """Save schema to file
        
        Args:
            schema: Schema to save
            filepath: Output file path
            format: File format ('json' or 'yaml')
        """
        data = self._schema_to_dict(schema)
        
        with open(filepath, 'w') as f:
            if format == 'json':
                json.dump(data, f, indent=2)
            else:  # YAML
                yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"Saved schema '{schema.schema_id}' to {filepath}")
    
    def _schema_to_dict(self, schema: ExtractionSchema) -> Dict[str, Any]:
        """Convert schema object to dictionary"""
        data = {
            'mode': schema.mode.value,
            'schema_id': schema.schema_id,
            'description': schema.description,
            'inheritance_enabled': schema.inheritance_enabled,
            'auto_infer_hierarchy': schema.auto_infer_hierarchy,
            'entity_hierarchy': schema.entity_hierarchy,
            'global_confidence_threshold': schema.global_confidence_threshold,
            'created_at': schema.created_at
        }
        
        # Add mode-specific fields
        if isinstance(schema, OpenSchema):
            data['discovery_constraints'] = schema.discovery_constraints
        elif isinstance(schema, HybridSchema):
            data['discovery_confidence_threshold'] = schema.discovery_confidence_threshold
            data['max_discoveries'] = schema.max_discoveries
        
        # Add entity types
        data['entity_types'] = {}
        for name, entity_type in schema.entity_types.items():
            data['entity_types'][name] = {
                'parent_type': entity_type.parent_type,
                'required_properties': entity_type.required_properties,
                'optional_properties': entity_type.optional_properties,
                'validation_rules': entity_type.validation_rules,
                'confidence_threshold': entity_type.confidence_threshold
            }
        
        # Add relation types
        data['relation_types'] = {}
        for name, relation_type in schema.relation_types.items():
            data['relation_types'][name] = {
                'source_entity_types': relation_type.source_entity_types,
                'target_entity_types': relation_type.target_entity_types,
                'properties': relation_type.properties,
                'confidence_threshold': relation_type.confidence_threshold,
                'directional': relation_type.directional
            }
        
        return data
    
    def get_schema(self, schema_id: str) -> Optional[ExtractionSchema]:
        """Get schema by ID
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Schema object or None if not found
        """
        return self.schemas.get(schema_id)
    
    def get_default_schema(self) -> ExtractionSchema:
        """Get default schema
        
        Returns:
            Default schema (general_open if not set)
        """
        if self.default_schema_id and self.default_schema_id in self.schemas:
            return self.schemas[self.default_schema_id]
        return self.schemas["general_open"]
    
    def set_default_schema(self, schema_id: str) -> bool:
        """Set default schema
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            True if successful, False if schema not found
        """
        if schema_id in self.schemas:
            self.default_schema_id = schema_id
            logger.info(f"Set default schema to '{schema_id}'")
            return True
        return False
    
    def register_schema(self, schema: ExtractionSchema, save_to_file: bool = True):
        """Register a new schema
        
        Args:
            schema: Schema to register
            save_to_file: Whether to save schema to file
        """
        self.schemas[schema.schema_id] = schema
        
        if save_to_file:
            filename = f"{schema.schema_id}.json"
            filepath = os.path.join(self.schema_directory, filename)
            self.save_schema_to_file(schema, filepath)
        
        logger.info(f"Registered schema '{schema.schema_id}'")
    
    def list_schemas(self) -> List[str]:
        """List all available schema IDs
        
        Returns:
            List of schema identifiers
        """
        return list(self.schemas.keys())
    
    def get_schemas_by_mode(self, mode: SchemaMode) -> List[ExtractionSchema]:
        """Get all schemas of a specific mode
        
        Args:
            mode: Schema mode to filter by
            
        Returns:
            List of schemas matching the mode
        """
        return [schema for schema in self.schemas.values() if schema.mode == mode]
    
    def validate_schema(self, schema: ExtractionSchema) -> Dict[str, Any]:
        """Validate schema configuration
        
        Args:
            schema: Schema to validate
            
        Returns:
            Validation result with errors/warnings
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        if not schema.schema_id:
            validation_result["errors"].append("Schema ID is required")
            validation_result["valid"] = False
        
        # Check entity hierarchy for cycles
        if schema.inheritance_enabled:
            for child, parent in schema.entity_hierarchy.items():
                path = schema.get_entity_hierarchy_path(child)
                if len(set(path)) != len(path):  # Duplicate means cycle
                    validation_result["errors"].append(f"Circular inheritance detected for {child}")
                    validation_result["valid"] = False
        
        # Check entity type validity
        for entity_name, entity_type in schema.entity_types.items():
            if entity_type.parent_type and entity_type.parent_type not in schema.entity_types:
                validation_result["warnings"].append(f"Parent type '{entity_type.parent_type}' not defined for {entity_name}")
        
        # Check relation type constraints
        for relation_name, relation_type in schema.relation_types.items():
            for entity_type in relation_type.source_entity_types + relation_type.target_entity_types:
                if entity_type not in schema.entity_types:
                    validation_result["warnings"].append(f"Entity type '{entity_type}' in relation '{relation_name}' not defined")
        
        return validation_result
    
    def create_schema_from_extraction(self, extraction_result: Dict[str, Any], schema_id: str) -> OpenSchema:
        """Create open schema from extraction result (reverse engineering)
        
        Args:
            extraction_result: Extraction result with discovered types
            schema_id: ID for the new schema
            
        Returns:
            New open schema based on discovered types
        """
        schema = create_open_schema(schema_id, f"Schema created from extraction at {datetime.now()}")
        
        # Extract discovered types if available
        discovered_types = extraction_result.get("discovered_types", {})
        
        # Add discovered entity types
        for entity_type in discovered_types.get("entity_types", []):
            schema.entity_types[entity_type] = EntityTypeSchema(type_name=entity_type)
        
        # Add discovered relation types
        for relation_type in discovered_types.get("relation_types", []):
            schema.relation_types[relation_type] = RelationTypeSchema(type_name=relation_type)
        
        # Add discovered properties
        properties = discovered_types.get("properties", {})
        for entity_type, props in properties.items():
            if entity_type in schema.entity_types:
                schema.entity_types[entity_type].optional_properties = props
        
        return schema
    
    def merge_schemas(self, schema1: ExtractionSchema, schema2: ExtractionSchema, new_schema_id: str) -> ExtractionSchema:
        """Merge two schemas into a new hybrid schema
        
        Args:
            schema1: First schema to merge
            schema2: Second schema to merge  
            new_schema_id: ID for merged schema
            
        Returns:
            New hybrid schema with combined types
        """
        merged = create_hybrid_schema(new_schema_id, [])
        merged.description = f"Merged schema from {schema1.schema_id} and {schema2.schema_id}"
        
        # Merge entity types
        merged.entity_types.update(schema1.entity_types)
        merged.entity_types.update(schema2.entity_types)
        
        # Merge relation types
        merged.relation_types.update(schema1.relation_types)
        merged.relation_types.update(schema2.relation_types)
        
        # Merge hierarchies
        merged.entity_hierarchy.update(schema1.entity_hierarchy)
        merged.entity_hierarchy.update(schema2.entity_hierarchy)
        
        return merged
    
    def get_schema_statistics(self) -> Dict[str, Any]:
        """Get statistics about all schemas
        
        Returns:
            Dictionary with schema statistics
        """
        stats = {
            "total_schemas": len(self.schemas),
            "schemas_by_mode": {mode.value: 0 for mode in SchemaMode},
            "total_entity_types": 0,
            "total_relation_types": 0,
            "schemas": {}
        }
        
        for schema_id, schema in self.schemas.items():
            stats["schemas_by_mode"][schema.mode.value] += 1
            stats["total_entity_types"] += len(schema.entity_types)
            stats["total_relation_types"] += len(schema.relation_types)
            
            stats["schemas"][schema_id] = {
                "mode": schema.mode.value,
                "entity_types": len(schema.entity_types),
                "relation_types": len(schema.relation_types),
                "inheritance_enabled": schema.inheritance_enabled,
                "description": schema.description
            }
        
        return stats


# Global schema manager instance
_schema_manager: Optional[SchemaManager] = None


def get_schema_manager() -> SchemaManager:
    """Get global schema manager instance"""
    global _schema_manager
    if _schema_manager is None:
        _schema_manager = SchemaManager()
    return _schema_manager


def set_schema_manager(schema_manager: SchemaManager):
    """Set global schema manager instance"""
    global _schema_manager
    _schema_manager = schema_manager