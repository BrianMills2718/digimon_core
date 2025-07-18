"""
Pipeline Validation Middleware

Ensures data contracts are enforced at every step of pipeline execution.
Addresses Gemini's finding about missing contract validation integration.
"""

from typing import Any, Dict, List, Optional
from .contract_validator import ContractValidator
from .entity_schema import StandardEntity, StandardRelationship
from .logging_config import get_logger

logger = get_logger("core.pipeline_validation")

class PipelineValidator:
    """Validates data contracts between pipeline tools"""
    
    def __init__(self, strict_mode: bool = False):
        self.contract_validator = ContractValidator()
        self.strict_mode = strict_mode
        
    def validate_tool_input(self, tool_name: str, input_data: Any, expected_schema: Optional[str] = None) -> bool:
        """Validate tool input data against expected schema"""
        try:
            if expected_schema:
                validation_result = self.contract_validator.validate_against_schema(input_data, expected_schema)
                if not validation_result.is_valid:
                    logger.error(f"Tool {tool_name} input validation failed: {validation_result.errors}")
                    if self.strict_mode:
                        raise ValueError(f"Tool input validation failed for {tool_name}: {validation_result.errors}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Input validation error for tool {tool_name}: {e}")
            if self.strict_mode:
                raise
            return False
    
    def validate_tool_output(self, tool_name: str, output_data: Any, expected_schema: Optional[str] = None) -> bool:
        """Validate tool output data against expected schema"""
        try:
            # Validate basic structure
            if not isinstance(output_data, dict):
                logger.error(f"Tool {tool_name} output must be a dictionary")
                if self.strict_mode:
                    raise ValueError(f"Tool {tool_name} output must be a dictionary")
                return False
            
            # Validate status field
            if 'status' not in output_data:
                logger.error(f"Tool {tool_name} output missing required 'status' field")
                if self.strict_mode:
                    raise ValueError(f"Tool {tool_name} output missing required 'status' field")
                return False
            
            # Validate entities if present
            if 'entities' in output_data and output_data['entities']:
                if not self._validate_entities(output_data['entities'], tool_name):
                    return False
            
            # Validate relationships if present
            if 'relationships' in output_data and output_data['relationships']:
                if not self._validate_relationships(output_data['relationships'], tool_name):
                    return False
            
            # Use contract validator for schema validation if specified
            if expected_schema:
                validation_result = self.contract_validator.validate_against_schema(output_data, expected_schema)
                if not validation_result.is_valid:
                    logger.error(f"Tool {tool_name} output schema validation failed: {validation_result.errors}")
                    if self.strict_mode:
                        raise ValueError(f"Tool output schema validation failed for {tool_name}: {validation_result.errors}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Output validation error for tool {tool_name}: {e}")
            if self.strict_mode:
                raise
            return False
    
    def _validate_entities(self, entities: List[Dict[str, Any]], tool_name: str) -> bool:
        """Validate entity data structures"""
        try:
            for i, entity in enumerate(entities):
                # Check required fields based on StandardEntity schema
                required_fields = ['entity_id', 'canonical_name', 'entity_type', 'confidence']
                missing_fields = [field for field in required_fields if field not in entity]
                
                if missing_fields:
                    logger.error(f"Tool {tool_name} entity {i} missing required fields: {missing_fields}")
                    if self.strict_mode:
                        raise ValueError(f"Entity {i} missing required fields: {missing_fields}")
                    return False
                
                # Validate confidence range
                confidence = entity.get('confidence')
                if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                    logger.error(f"Tool {tool_name} entity {i} has invalid confidence: {confidence}")
                    if self.strict_mode:
                        raise ValueError(f"Entity {i} has invalid confidence: {confidence}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Entity validation error for tool {tool_name}: {e}")
            if self.strict_mode:
                raise
            return False
    
    def _validate_relationships(self, relationships: List[Dict[str, Any]], tool_name: str) -> bool:
        """Validate relationship data structures"""
        try:
            for i, relationship in enumerate(relationships):
                # Check required fields based on StandardRelationship schema
                required_fields = ['relationship_id', 'subject_entity_id', 'predicate', 'object_entity_id', 'confidence']
                missing_fields = [field for field in required_fields if field not in relationship]
                
                if missing_fields:
                    logger.error(f"Tool {tool_name} relationship {i} missing required fields: {missing_fields}")
                    if self.strict_mode:
                        raise ValueError(f"Relationship {i} missing required fields: {missing_fields}")
                    return False
                
                # Validate confidence range
                confidence = relationship.get('confidence')
                if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                    logger.error(f"Tool {tool_name} relationship {i} has invalid confidence: {confidence}")
                    if self.strict_mode:
                        raise ValueError(f"Relationship {i} has invalid confidence: {confidence}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Relationship validation error for tool {tool_name}: {e}")
            if self.strict_mode:
                raise
            return False