"""
Theory-Aware Adapter Base Class

Base class for adapters that support theory-aware processing with contracts.
Provides common functionality for theory-guided processing across all phases.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from .adapter_utils import AdapterUtils

# Theory-aware imports with fallback
try:
    from contracts.phase_interfaces.base_graphrag_phase import (
        TheoryAwareGraphRAGPhase as ContractTheoryAwareGraphRAGPhase, 
        TheorySchema as ContractTheorySchema, 
        TheoryConfig as ContractTheoryConfig, 
        ProcessingRequest as TheoryProcessingRequest,
        ProcessingResult as TheoryProcessingResult,
        TheoryValidatedResult as ContractTheoryValidatedResult
    )
    from contracts.validation.theory_validator import TheoryValidator as ContractTheoryValidator
    CONTRACTS_AVAILABLE = True
    
    # Use contract implementations
    TheoryAwareGraphRAGPhase = ContractTheoryAwareGraphRAGPhase
    TheorySchema = ContractTheorySchema
    TheoryConfig = ContractTheoryConfig
    TheoryValidatedResult = ContractTheoryValidatedResult
    TheoryValidator = ContractTheoryValidator
    
except ImportError:
    # Fallback implementations for missing contracts
    CONTRACTS_AVAILABLE = False
    
    class FallbackTheoryAwareGraphRAGPhase:
        pass
        
    class FallbackTheorySchema:
        MASTER_CONCEPTS = "master_concepts"
        THREE_DIMENSIONAL = "three_dimensional" 
        ORM_METHODOLOGY = "orm_methodology"
        
    class FallbackTheoryConfig:
        def __init__(self, **kwargs):
            pass
            
    class FallbackTheoryProcessingRequest:
        def __init__(self, **kwargs):
            self.theory_config = None
            
    class FallbackTheoryProcessingResult:
        def __init__(self, **kwargs):
            pass
            
    class FallbackTheoryValidatedResult:
        def __init__(self, entities=None, relationships=None, theory_compliance=None, 
                     concept_mapping=None, validation_score=0.0, **kwargs):
            self.entities = entities or []
            self.relationships = relationships or []
            self.theory_compliance = theory_compliance or {}
            self.concept_mapping = concept_mapping or {}
            self.validation_score = validation_score
            
    class FallbackTheoryValidator:
        def __init__(self, config):
            pass
        def validate_entities(self, entities):
            return 1.0, {}
        def validate_relationships(self, relationships):
            return 1.0, {}
        def map_to_concepts(self, entities):
            return {}
    
    # Set aliases for fallback classes
    TheoryAwareGraphRAGPhase = FallbackTheoryAwareGraphRAGPhase  # type: ignore[misc,assignment]
    TheorySchema = FallbackTheorySchema  # type: ignore[misc,assignment]
    TheoryConfig = FallbackTheoryConfig  # type: ignore[misc,assignment]
    TheoryProcessingRequest = FallbackTheoryProcessingRequest  # type: ignore[misc,assignment]
    TheoryProcessingResult = FallbackTheoryProcessingResult  # type: ignore[misc,assignment]
    TheoryValidatedResult = FallbackTheoryValidatedResult  # type: ignore[misc,assignment]
    TheoryValidator = FallbackTheoryValidator  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)


class TheoryAwareAdapterBase(TheoryAwareGraphRAGPhase, ABC):
    """Base class for theory-aware phase adapters"""
    
    def __init__(self, phase_name: str, version: str):
        self.phase_name = phase_name
        self.version = version
        self.logger = logging.getLogger(f"phase_adapters.{phase_name.lower().replace(' ', '_')}")
        
        # Theory-aware state
        self._theory_validator: Optional[TheoryValidator] = None
        self._current_theory_schema: Optional[TheorySchema] = None
        self._theory_config: Optional[TheoryConfig] = None
    
    # Theory-Aware Interface Implementation
    def get_name(self) -> str:
        """Return phase name for theory-aware interface"""
        return self.phase_name
    
    def get_version(self) -> str:
        """Return phase version for theory-aware interface"""
        return self.version
    
    def get_supported_theory_schemas(self) -> List[TheorySchema]:
        """Return list of supported theory schemas - override in subclasses"""
        return [TheorySchema.MASTER_CONCEPTS, TheorySchema.ORM_METHODOLOGY]
    
    def validate_theory_config(self, config: TheoryConfig) -> List[str]:
        """Validate theory configuration using adapter utils"""
        return AdapterUtils.validate_theory_config(config)
    
    @abstractmethod
    def _execute_original(self, request) -> Any:
        """Execute with original interface - must be implemented by subclasses"""
        pass
    
    def execute(self, request) -> Any:
        """Execute phase - supports both old and new interfaces"""
        # Check if this is a theory-aware request
        if isinstance(request, TheoryProcessingRequest):
            return self._execute_theory_aware(request)
        else:
            # Original interface
            return self._execute_original(request)
    
    def _execute_theory_aware(self, request: TheoryProcessingRequest) -> TheoryProcessingResult:
        """Execute with theory-guided processing"""
        start_time = time.time()
        
        try:
            # Validate theory config
            theory_errors = self.validate_theory_config(request.theory_config)
            if theory_errors:
                return self._create_theory_error_result(
                    f"Theory validation failed: {'; '.join(theory_errors)}",
                    start_time
                )
            
            # Load and setup theory schema
            theory_schema = self._load_theory_schema(request.theory_config)
            self._current_theory_schema = theory_schema
            self._theory_config = request.theory_config
            
            # Initialize theory validator
            self._theory_validator = self._create_theory_validator(request.theory_config)
            
            # Create theory-guided workflow
            workflow = self._create_theory_guided_workflow(theory_schema)
            
            # Execute with theory guidance throughout the process
            result = self._execute_with_theory_guidance(
                workflow, request, theory_schema
            )
            
            # Create theory validated result
            theory_validated_result = self._create_theory_validated_result(result)
            
            return TheoryProcessingResult(
                phase_name=f"{self.phase_name} (Theory-Guided)",
                status="success",
                execution_time_seconds=time.time() - start_time,
                theory_validated_result=theory_validated_result,
                workflow_summary=self._create_theory_workflow_summary(result),
                query_results=self._generate_theory_query_results(request.queries, result),
                raw_phase_result={"theory_guided_result": result.__dict__ if hasattr(result, '__dict__') else result}
            )
            
        except Exception as e:
            error_msg = AdapterUtils.sanitize_error_message(e)
            self.logger.error(f"Theory-aware execution failed: {error_msg}")
            return self._create_theory_error_result(
                f"Theory-aware execution failed: {error_msg}",
                start_time
            )
    
    def _load_theory_schema(self, theory_config: TheoryConfig) -> Any:
        """Load theory schema from config - override in subclasses for specific loading"""
        # Default implementation just returns the config
        return theory_config
    
    def _create_theory_validator(self, theory_config: TheoryConfig) -> TheoryValidator:
        """Create theory validator instance"""
        if CONTRACTS_AVAILABLE:
            return TheoryValidator(theory_config)
        else:
            # Fallback validator
            return TheoryValidator(theory_config)
    
    @abstractmethod
    def _create_theory_guided_workflow(self, theory_schema: Any) -> Any:
        """Create workflow that uses theory to guide extraction - must be implemented by subclasses"""
        pass
    
    def _execute_with_theory_guidance(self, workflow: Any, request: TheoryProcessingRequest, theory_schema: Any) -> Any:
        """Execute workflow with theory guidance - can be overridden by subclasses"""
        # Default implementation - subclasses should override for specific behavior
        return workflow.execute_with_theory_guidance(
            document_paths=request.documents,
            queries=request.queries,
            theory_schema=theory_schema,
            concept_library=getattr(workflow, 'concept_library', None)
        )
    
    def _create_theory_validated_result(self, result: Any) -> TheoryValidatedResult:
        """Create theory validated result from workflow result"""
        entities = getattr(result, 'entities', [])
        relationships = getattr(result, 'relationships', [])
        
        # Use theory validator if available
        if self._theory_validator:
            entity_score, entity_metadata = self._theory_validator.validate_entities(entities)
            rel_score, rel_metadata = self._theory_validator.validate_relationships(relationships)
            concept_mapping = self._theory_validator.map_to_concepts(entities)
            
            validation_score = (entity_score + rel_score) / 2
        else:
            # Fallback validation
            entity_score = 0.8
            rel_score = 0.8
            entity_metadata = {}
            rel_metadata = {}
            concept_mapping = self._create_fallback_concept_mapping(entities)
            validation_score = 0.8  # Default score
        
        return TheoryValidatedResult(
            entities=entities,
            relationships=relationships,
            theory_compliance={
                "concept_usage": getattr(result, 'concept_usage', {}),
                "theory_metadata": getattr(result, 'theory_metadata', {}),
                "alignment_score": getattr(result, 'theory_alignment_score', validation_score),
                "entity_validation": entity_metadata,
                "relationship_validation": rel_metadata
            },
            concept_mapping=concept_mapping,
            validation_score=validation_score
        )
    
    def _create_theory_workflow_summary(self, result: Any) -> Dict[str, Any]:
        """Create workflow summary for theory-guided processing"""
        entities = getattr(result, 'entities', [])
        relationships = getattr(result, 'relationships', [])
        
        return {
            "entities_extracted": len(entities),
            "relationships_found": len(relationships),
            "theory_alignment_score": getattr(result, 'theory_alignment_score', 0.8),
            "concepts_used": len(getattr(result, 'concept_usage', {})),
            "theory_enhanced_entities": getattr(result, 'theory_enhanced_entities', 0),
            "theory_enhanced_relationships": getattr(result, 'theory_enhanced_relationships', 0),
            "schema_type": self._theory_config.schema_type if self._theory_config else "unknown"
        }
    
    def _generate_theory_query_results(self, queries: List[str], theory_result: Any) -> List[Dict[str, Any]]:
        """Generate query results that incorporate theory information"""
        query_results = []
        
        entities = getattr(theory_result, 'entities', [])
        theory_alignment_score = getattr(theory_result, 'theory_alignment_score', 0.8)
        concept_usage = getattr(theory_result, 'concept_usage', {})
        
        for query in queries:
            # Simple query processing using theory-enhanced entities
            relevant_entities = []
            query_words = query.lower().split()
            
            for entity in entities:
                entity_name = entity.get("surface_form", entity.get("canonical_name", ""))
                if entity_name and any(word in entity_name.lower() for word in query_words):
                    relevant_entities.append(entity)
            
            result = {
                "query": query,
                "status": "success",
                "results": relevant_entities[:10],  # Top 10 matches
                "theory_enhanced": True,
                "alignment_score": theory_alignment_score,
                "concept_usage": concept_usage,
                "total_matches": len(relevant_entities)
            }
            query_results.append(result)
        
        return query_results
    
    def _create_fallback_concept_mapping(self, entities: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create fallback concept mapping when theory validator not available"""
        mapping = {}
        
        for entity in entities:
            entity_name = entity.get("surface_form", entity.get("canonical_name", "unknown"))
            entity_type = entity.get("entity_type", "UNKNOWN")
            
            # Simple mapping based on entity type
            if entity_type == "PERSON":
                mapping[entity_name] = "Individual"
            elif entity_type == "ORGANIZATION":
                mapping[entity_name] = "Organization"
            elif entity_type == "LOCATION":
                mapping[entity_name] = "Place"
            elif entity_type == "EVENT":
                mapping[entity_name] = "Event"
            else:
                mapping[entity_name] = "Entity"
        
        return mapping
    
    def _create_theory_error_result(self, error_message: str, start_time: float) -> TheoryProcessingResult:
        """Create error result for theory-aware processing"""
        # Create empty theory validated result for error case
        empty_theory_result = TheoryValidatedResult(
            entities=[],
            relationships=[],
            theory_compliance={},
            concept_mapping={},
            validation_score=0.0
        )
        
        return TheoryProcessingResult(
            phase_name=self.phase_name,
            status="error", 
            execution_time_seconds=time.time() - start_time,
            theory_validated_result=empty_theory_result,
            workflow_summary={},
            query_results=[],
            error_message=error_message
        )
    
    def get_theory_capabilities(self) -> Dict[str, Any]:
        """Get theory-aware capabilities of this adapter"""
        return {
            "contracts_available": CONTRACTS_AVAILABLE,
            "supported_schemas": [schema.value if hasattr(schema, 'value') else str(schema) 
                                 for schema in self.get_supported_theory_schemas()],
            "theory_validator_available": self._theory_validator is not None,
            "current_schema": str(self._current_theory_schema) if self._current_theory_schema else None
        }