"""
Standardized Entity Data Schema for Production Consistency

This module enforces consistent entity data structures across all tools
to eliminate the need for brittle fallback chains in data access.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class EntityType(str, Enum):
    """Standardized entity types"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION" 
    LOCATION = "LOCATION"
    PRODUCT = "PRODUCT"
    DATE = "DATE"
    MONEY = "MONEY"
    OTHER = "OTHER"

class StandardEntity(BaseModel):
    """Standardized entity model that ALL tools must return"""
    
    # Core required fields - NEVER use fallback chains
    entity_id: str = Field(..., description="Unique entity identifier")
    canonical_name: str = Field(..., description="Primary display name - ALWAYS present")
    entity_type: EntityType = Field(..., description="Standardized entity type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    
    # Optional enrichment fields
    surface_form: Optional[str] = Field(None, description="Original text mention")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    source_chunk: Optional[str] = Field(None, description="Source chunk identifier")
    
    # Theory enhancement fields
    theory_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Theory-guided enhancements")

class StandardRelationship(BaseModel):
    """Standardized relationship model that ALL tools must return"""
    
    # Core required fields
    relationship_id: str = Field(..., description="Unique relationship identifier")
    subject_entity_id: str = Field(..., description="Subject entity ID")
    predicate: str = Field(..., description="Relationship type/predicate")
    object_entity_id: str = Field(..., description="Object entity ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    
    # Optional enrichment fields
    source_text: Optional[str] = Field(None, description="Supporting text evidence")
    source_chunk: Optional[str] = Field(None, description="Source chunk identifier")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Theory enhancement fields
    theory_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Theory-guided enhancements")

class EntityValidationError(Exception):
    """Raised when entity data doesn't conform to standard schema"""
    pass

class RelationshipValidationError(Exception):
    """Raised when relationship data doesn't conform to standard schema"""
    pass

def validate_entity(entity_data: Dict[str, Any]) -> StandardEntity:
    """Validate and convert entity data to standard schema"""
    try:
        return StandardEntity(**entity_data)
    except Exception as e:
        raise EntityValidationError(f"Entity validation failed: {e}")

def validate_relationship(relationship_data: Dict[str, Any]) -> StandardRelationship:
    """Validate and convert relationship data to standard schema"""
    try:
        return StandardRelationship(**relationship_data)
    except Exception as e:
        raise RelationshipValidationError(f"Relationship validation failed: {e}")