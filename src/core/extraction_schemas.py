"""Extraction Schema System

Defines schema types for entity/relationship extraction:
- Open Schema: Discover any entities/relations dynamically
- Closed Schema: Extract only predefined types
- Hybrid Schema: Mix of predefined + discovered types
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal, Set
from enum import Enum
import json
from datetime import datetime


class SchemaMode(Enum):
    """Schema extraction modes"""
    OPEN = "open"
    CLOSED = "closed" 
    HYBRID = "hybrid"


@dataclass
class EntityTypeSchema:
    """Schema definition for an entity type"""
    type_name: str
    parent_type: Optional[str] = None
    required_properties: List[str] = field(default_factory=list)
    optional_properties: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.0  # Lowered to 0 for initial development
    
    def get_all_properties(self) -> List[str]:
        """Get all properties (required + optional)"""
        return self.required_properties + self.optional_properties
    
    def validate_entity(self, entity_data: Dict[str, Any]) -> bool:
        """Validate entity data against this schema"""
        # Check required properties
        for prop in self.required_properties:
            if prop not in entity_data:
                return False
        
        # Apply validation rules
        for rule_name, rule_config in self.validation_rules.items():
            if not self._apply_validation_rule(entity_data, rule_name, rule_config):
                return False
        
        return True
    
    def _apply_validation_rule(self, entity_data: Dict[str, Any], rule_name: str, rule_config: Any) -> bool:
        """Apply a specific validation rule"""
        if rule_name == "min_confidence":
            return entity_data.get("confidence", 0.0) >= rule_config
        elif rule_name == "property_types":
            for prop, expected_type in rule_config.items():
                if prop in entity_data and not isinstance(entity_data[prop], expected_type):
                    return False
        return True


@dataclass
class RelationTypeSchema:
    """Schema definition for a relation type"""
    type_name: str
    source_entity_types: List[str] = field(default_factory=list)
    target_entity_types: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.0  # Lowered to 0 for initial development
    directional: bool = True
    
    def validate_relation(self, relation_data: Dict[str, Any]) -> bool:
        """Validate relation data against this schema"""
        # Check entity type constraints
        if self.source_entity_types:
            source_type = relation_data.get("source_entity_type")
            if source_type not in self.source_entity_types:
                return False
        
        if self.target_entity_types:
            target_type = relation_data.get("target_entity_type")
            if target_type not in self.target_entity_types:
                return False
        
        # Check confidence
        confidence = relation_data.get("confidence", 0.0)
        if confidence < self.confidence_threshold:
            return False
        
        return True


@dataclass
class ExtractionSchema:
    """Base extraction schema with inheritance support"""
    mode: SchemaMode
    schema_id: str
    description: str = ""
    inheritance_enabled: bool = True
    auto_infer_hierarchy: bool = False
    entity_hierarchy: Dict[str, str] = field(default_factory=dict)  # child -> parent
    entity_types: Dict[str, EntityTypeSchema] = field(default_factory=dict)
    relation_types: Dict[str, RelationTypeSchema] = field(default_factory=dict)
    global_confidence_threshold: float = 0.0  # Lowered to 0 for initial development
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_entity_hierarchy_path(self, entity_type: str) -> List[str]:
        """Get full hierarchy path for an entity type"""
        path = [entity_type]
        current = entity_type
        
        while current in self.entity_hierarchy:
            parent = self.entity_hierarchy[current]
            if parent in path:  # Circular reference
                break
            path.append(parent)
            current = parent
        
        return path
    
    def is_valid_entity_type(self, entity_type: str) -> bool:
        """Check if entity type is valid in this schema"""
        if self.mode == SchemaMode.OPEN:
            return True
        elif self.mode == SchemaMode.CLOSED:
            return entity_type in self.entity_types
        else:  # HYBRID
            return True  # Allow any type in hybrid mode
    
    def get_inherited_properties(self, entity_type: str) -> List[str]:
        """Get all properties including inherited ones"""
        if not self.inheritance_enabled or entity_type not in self.entity_types:
            return self.entity_types.get(entity_type, EntityTypeSchema(entity_type)).get_all_properties()
        
        all_properties = set()
        hierarchy = self.get_entity_hierarchy_path(entity_type)
        
        for type_name in hierarchy:
            if type_name in self.entity_types:
                all_properties.update(self.entity_types[type_name].get_all_properties())
        
        return list(all_properties)
    
    def validate_extraction_result(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate full extraction result against schema"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "entity_validation": {},
            "relation_validation": {}
        }
        
        # Validate entities
        entities = extraction_result.get("entities", [])
        for entity in entities:
            entity_id = entity.get("id", "unknown")
            entity_type = entity.get("type")
            
            if not self.is_valid_entity_type(entity_type):
                validation_result["errors"].append(f"Invalid entity type: {entity_type}")
                validation_result["valid"] = False
                continue
            
            if entity_type in self.entity_types:
                is_valid = self.entity_types[entity_type].validate_entity(entity)
                validation_result["entity_validation"][entity_id] = is_valid
                if not is_valid:
                    validation_result["errors"].append(f"Entity {entity_id} failed validation")
                    validation_result["valid"] = False
        
        # Validate relations
        relations = extraction_result.get("relations", [])
        for relation in relations:
            relation_id = relation.get("id", "unknown")
            relation_type = relation.get("type")
            
            if self.mode == SchemaMode.CLOSED and relation_type not in self.relation_types:
                validation_result["errors"].append(f"Invalid relation type: {relation_type}")
                validation_result["valid"] = False
                continue
            
            if relation_type in self.relation_types:
                is_valid = self.relation_types[relation_type].validate_relation(relation)
                validation_result["relation_validation"][relation_id] = is_valid
                if not is_valid:
                    validation_result["errors"].append(f"Relation {relation_id} failed validation")
                    validation_result["valid"] = False
        
        return validation_result


@dataclass
class OpenSchema(ExtractionSchema):
    """Open schema for dynamic discovery"""
    
    def __init__(self, schema_id: str, description: str = "", **kwargs):
        super().__init__(
            mode=SchemaMode.OPEN,
            schema_id=schema_id,
            description=description,
            **kwargs
        )
        self.discovery_constraints = kwargs.get("discovery_constraints", {})
    
    def get_extraction_prompt(self) -> str:
        """Get LLM prompt for open extraction"""
        return """Extract all entities and relationships from the text. 
        Discover entity types and relationship types dynamically.
        Return both the discovered schema and the extracted data.
        
        Format your response as JSON with:
        {
          "discovered_types": {
            "entity_types": [...],
            "relation_types": [...],
            "properties": {...}
          },
          "extracted_data": {
            "entities": [...],
            "relations": [...]
          }
        }"""


@dataclass
class ClosedSchema(ExtractionSchema):
    """Closed schema with predefined types only"""
    
    def __init__(self, schema_id: str, description: str = "", **kwargs):
        super().__init__(
            mode=SchemaMode.CLOSED,
            schema_id=schema_id,
            description=description,
            **kwargs
        )
    
    def get_extraction_prompt(self) -> str:
        """Get LLM prompt for closed extraction"""
        entity_types = list(self.entity_types.keys())
        relation_types = list(self.relation_types.keys())
        
        return f"""Extract entities and relationships from the text using ONLY these predefined types:

        Entity Types: {entity_types}
        Relation Types: {relation_types}
        
        Do not extract entities or relations that don't match these exact types.
        
        Format your response as JSON with:
        {{
          "extracted_data": {{
            "entities": [...],
            "relations": [...]
          }}
        }}"""


@dataclass
class HybridSchema(ExtractionSchema):
    """Hybrid schema allowing both predefined and discovered types"""
    
    def __init__(self, schema_id: str, description: str = "", **kwargs):
        super().__init__(
            mode=SchemaMode.HYBRID,
            schema_id=schema_id,
            description=description,
            **kwargs
        )
        self.discovery_confidence_threshold = kwargs.get("discovery_confidence_threshold", 0.7)
        self.max_discoveries = kwargs.get("max_discoveries", 10)
    
    def get_extraction_prompt(self) -> str:
        """Get LLM prompt for hybrid extraction"""
        entity_types = list(self.entity_types.keys())
        relation_types = list(self.relation_types.keys())
        
        return f"""Extract entities and relationships from the text using:

        1. PREDEFINED TYPES (preferred):
           Entity Types: {entity_types}
           Relation Types: {relation_types}
        
        2. DISCOVERED TYPES (if needed):
           You may discover new entity/relation types if they are clearly distinct
           and important. Require high confidence (>{self.discovery_confidence_threshold}) for new types.
        
        Format your response as JSON with:
        {{
          "discovered_types": {{
            "entity_types": [...],
            "relation_types": [...],
            "properties": {{...}}
          }},
          "extracted_data": {{
            "entities": [...],
            "relations": [...]
          }}
        }}"""


# Schema Factory Functions
def create_open_schema(schema_id: str, description: str = "", **kwargs) -> OpenSchema:
    """Create an open schema for dynamic discovery"""
    return OpenSchema(schema_id=schema_id, description=description, **kwargs)


def create_closed_schema(schema_id: str, entity_types: List[str], relation_types: List[str] = None, **kwargs) -> ClosedSchema:
    """Create a closed schema with predefined types"""
    schema = ClosedSchema(schema_id=schema_id, **kwargs)
    
    # Add entity types
    for entity_type in entity_types:
        schema.entity_types[entity_type] = EntityTypeSchema(type_name=entity_type)
    
    # Add relation types
    if relation_types:
        for relation_type in relation_types:
            schema.relation_types[relation_type] = RelationTypeSchema(type_name=relation_type)
    
    return schema


def create_hybrid_schema(schema_id: str, predefined_entities: List[str], predefined_relations: List[str] = None, **kwargs) -> HybridSchema:
    """Create a hybrid schema with predefined types + discovery"""
    schema = HybridSchema(schema_id=schema_id, **kwargs)
    
    # Add predefined entity types
    for entity_type in predefined_entities:
        schema.entity_types[entity_type] = EntityTypeSchema(type_name=entity_type)
    
    # Add predefined relation types
    if predefined_relations:
        for relation_type in predefined_relations:
            schema.relation_types[relation_type] = RelationTypeSchema(type_name=relation_type)
    
    return schema


# Example Schema Templates
def get_academic_paper_schema() -> ClosedSchema:
    """Academic paper extraction schema"""
    return create_closed_schema(
        schema_id="academic_paper",
        description="Schema for academic paper extraction",
        entity_types=["Author", "Institution", "Concept", "Method", "Dataset", "Metric"],
        relation_types=["authored_by", "affiliated_with", "uses_method", "evaluates_on", "achieves_metric"]
    )


def get_business_document_schema() -> ClosedSchema:
    """Business document extraction schema"""
    return create_closed_schema(
        schema_id="business_document", 
        description="Schema for business document extraction",
        entity_types=["Person", "Organization", "Product", "Service", "Location", "Date", "Money"],
        relation_types=["works_for", "located_in", "offers", "costs", "occurs_on"]
    )


def get_general_open_schema() -> OpenSchema:
    """General purpose open schema"""
    return create_open_schema(
        schema_id="general_open",
        description="General purpose open discovery schema"
    )