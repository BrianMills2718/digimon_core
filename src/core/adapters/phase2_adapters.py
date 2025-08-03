"""
Phase 2 Tool Adapters

Extracted from tool_adapters.py - Adapters for Phase 2 ontology-aware processing tools.
These adapters bridge the unified Tool protocol to Phase 2 ontology-enhanced tools.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager
from ..tool_protocol import ToolExecutionError, ToolValidationError, ToolValidationResult
from .base_adapters import BaseToolAdapter

logger = get_logger("core.adapters.phase2")


class OntologyAwareExtractorAdapter(BaseToolAdapter):
    """Adapter for Ontology-Aware Entity Extractor"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor as _OntologyAwareExtractor
            self._tool = _OntologyAwareExtractor(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import OntologyAwareExtractor: {e}")
            self._tool = None
            
        self.tool_name = "OntologyAwareExtractorAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to OntologyAwareExtractor interface"""
        if self._tool is None:
            raise ToolExecutionError("OntologyAwareExtractorAdapter", "OntologyAwareExtractor not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("OntologyAwareExtractorAdapter", validation_result.validation_errors)
        
        try:
            chunks = input_data.get("chunks", [])
            ontology_config = input_data.get("ontology_config", {})
            
            enhanced_entities = []
            
            for chunk in chunks:
                if chunk.get("text"):
                    result = self._tool.extract_entities_ontology_aware(
                        text=chunk["text"],
                        chunk_id=chunk.get("chunk_id"),
                        ontology_config=ontology_config
                    )
                    
                    if result.get("status") == "success":
                        enhanced_entities.extend(result.get("entities", []))
            
            return {
                "ontology_enhanced_entities": enhanced_entities,
                "ontology_metadata": {
                    "ontology_used": ontology_config.get("ontology_name", "default"),
                    "enhancement_method": "ontology_aware_extraction"
                },
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("OntologyAwareExtractorAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get OntologyAwareExtractor tool information"""
        return {
            "name": "Ontology-Aware Entity Extractor",
            "version": "1.0",
            "description": "Extracts entities with ontological enhancement and validation",
            "contract_id": "T23C_OntologyAwareExtractor",
            "capabilities": ["ontology_aware_extraction", "entity_enhancement", "semantic_validation"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate OntologyAwareExtractor input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "chunks" not in input_data:
            errors.append("Missing required field: chunks")
        elif not isinstance(input_data["chunks"], list):
            errors.append("chunks must be a list")
        
        # Validate ontology_config if present
        if "ontology_config" in input_data:
            ontology_config = input_data["ontology_config"]
            if not isinstance(ontology_config, dict):
                errors.append("ontology_config must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class OntologyGraphBuilderAdapter(BaseToolAdapter):
    """Adapter for Ontology-Aware Graph Builder"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder as _OntologyGraphBuilder
            self._tool = _OntologyGraphBuilder(
                neo4j_uri=self.neo4j_config.get("uri"),
                neo4j_user=self.neo4j_config.get("username"),
                neo4j_password=self.neo4j_config.get("password")
            )
        except ImportError as e:
            logger.error(f"Failed to import OntologyAwareGraphBuilder: {e}")
            self._tool = None
        except Exception as e:
            logger.error(f"Failed to initialize OntologyAwareGraphBuilder: {e}")
            self._tool = None
            
        self.tool_name = "OntologyGraphBuilderAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to OntologyGraphBuilder interface"""
        if self._tool is None:
            raise ToolExecutionError("OntologyGraphBuilderAdapter", "OntologyAwareGraphBuilder not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("OntologyGraphBuilderAdapter", validation_result.validation_errors)
        
        try:
            entities = input_data.get("entities", input_data.get("ontology_enhanced_entities", []))
            relationships = input_data.get("relationships", [])
            ontology_config = input_data.get("ontology_config", {})
            
            # Build ontology-aware graph
            result = self._tool.build_graph_with_ontology(
                entities=entities,
                relationships=relationships,
                ontology_config=ontology_config
            )
            
            if result.get("status") == "success":
                return {
                    "ontology_graph_results": result.get("graph_data", {}),
                    "ontology_validation_results": result.get("validation_results", {}),
                    "graph_metadata": result.get("metadata", {}),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Ontology graph building failed: %s", result.get("error"))
                return {
                    "ontology_graph_results": {},
                    "ontology_validation_results": {"error": result.get("error")},
                    "graph_metadata": {"status": "failed"},
                    **input_data
                }
                
        except Exception as e:
            raise ToolExecutionError("OntologyGraphBuilderAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get OntologyGraphBuilder tool information"""
        return {
            "name": "Ontology-Aware Graph Builder",
            "version": "1.0",
            "description": "Builds knowledge graphs with ontological constraints and validation",
            "contract_id": "T31_OntologyGraphBuilder",
            "capabilities": ["ontology_aware_graph_building", "semantic_validation", "constraint_enforcement"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate OntologyGraphBuilder input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        
        # Check for entities (required)
        has_entities = False
        if "entities" in input_data and isinstance(input_data["entities"], list):
            has_entities = True
        elif "ontology_enhanced_entities" in input_data and isinstance(input_data["ontology_enhanced_entities"], list):
            has_entities = True
        
        if not has_entities:
            errors.append("Missing required field: entities or ontology_enhanced_entities")
        
        # Check for relationships (optional but should be list if present)
        if "relationships" in input_data and not isinstance(input_data["relationships"], list):
            errors.append("relationships must be a list")
        
        # Validate ontology_config if present
        if "ontology_config" in input_data:
            ontology_config = input_data["ontology_config"]
            if not isinstance(ontology_config, dict):
                errors.append("ontology_config must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class OntologyValidatorAdapter(BaseToolAdapter):
    """Adapter for Ontology Validation"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self.tool_name = "OntologyValidatorAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute ontology validation"""
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("OntologyValidatorAdapter", validation_result.validation_errors)
        
        try:
            entities = input_data.get("entities", [])
            relationships = input_data.get("relationships", [])
            ontology_config = input_data.get("ontology_config", {})
            
            # Perform ontology validation
            validation_results = self._validate_against_ontology(entities, relationships, ontology_config)
            
            return {
                "ontology_validation": validation_results,
                "validation_summary": {
                    "entities_validated": len(entities),
                    "relationships_validated": len(relationships),
                    "validation_passed": validation_results.get("valid", False)
                },
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("OntologyValidatorAdapter", str(e), e)
    
    def _validate_against_ontology(self, entities: List[Dict], relationships: List[Dict], 
                                  ontology_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entities and relationships against ontology"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "entity_validation": {},
            "relationship_validation": {}
        }
        
        # Basic entity type validation
        valid_entity_types = ontology_config.get("entity_types", [
            "PERSON", "ORGANIZATION", "LOCATION", "PRODUCT", "EVENT"
        ])
        
        for entity in entities:
            entity_type = entity.get("type", "").upper()
            entity_id = entity.get("entity_id", entity.get("name", "unknown"))
            
            if entity_type and entity_type not in valid_entity_types:
                validation_results["errors"].append(
                    f"Invalid entity type '{entity_type}' for entity '{entity_id}'"
                )
                validation_results["valid"] = False
            
            validation_results["entity_validation"][entity_id] = {
                "type_valid": entity_type in valid_entity_types,
                "type": entity_type
            }
        
        # Basic relationship validation
        valid_relationship_types = ontology_config.get("relationship_types", [
            "WORKS_FOR", "LOCATED_IN", "FOUNDED", "PRODUCES", "PART_OF"
        ])
        
        for i, relationship in enumerate(relationships):
            rel_type = relationship.get("type", "").upper()
            rel_id = f"relationship_{i}"
            
            if rel_type and rel_type not in valid_relationship_types:
                validation_results["errors"].append(
                    f"Invalid relationship type '{rel_type}' in {rel_id}"
                )
                validation_results["valid"] = False
            
            validation_results["relationship_validation"][rel_id] = {
                "type_valid": rel_type in valid_relationship_types,
                "type": rel_type
            }
        
        return validation_results
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get OntologyValidator tool information"""
        return {
            "name": "Ontology Validator",
            "version": "1.0",
            "description": "Validates entities and relationships against ontological constraints",
            "contract_id": "OntologyValidator",
            "capabilities": ["ontology_validation", "constraint_checking", "semantic_validation"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate OntologyValidator input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        
        # Check for entities or relationships (at least one required)
        has_data = False
        if "entities" in input_data and isinstance(input_data["entities"], list):
            has_data = True
        if "relationships" in input_data and isinstance(input_data["relationships"], list):
            has_data = True
        
        if not has_data:
            errors.append("Must provide either entities or relationships for validation")
        
        # Validate ontology_config if present
        if "ontology_config" in input_data:
            ontology_config = input_data["ontology_config"]
            if not isinstance(ontology_config, dict):
                errors.append("ontology_config must be a dictionary")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )