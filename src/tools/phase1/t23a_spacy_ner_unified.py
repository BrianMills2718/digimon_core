"""T23A: spaCy Named Entity Recognition - Unified Interface Implementation

This is the migrated version of T23A that fully implements the UnifiedTool interface.
It maintains backward compatibility while providing the standardized contract-first design.
"""

import time
import psutil
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import spacy
import jsonschema

from src.tools.base_classes.tool_protocol import (
    UnifiedTool, ToolStatus, ToolRequest, ToolResult, ToolContract
)
from src.tools.base_classes.tool_performance_monitor import ToolPerformanceMonitor
from src.core.service_manager import ServiceManager
from src.core.confidence_score import ConfidenceScore

logger = logging.getLogger(__name__)


class SpacyNERUnified(UnifiedTool):
    """T23A: spaCy Named Entity Recognition with unified interface
    
    Extracts named entities from text using spaCy's pre-trained models.
    Fully compliant with the UnifiedTool interface for agent orchestration.
    """
    
    def __init__(self, service_manager: Optional[ServiceManager] = None):
        """Initialize with optional service manager"""
        super().__init__()
        
        # Tool identification
        self.tool_id = "T23A_SPACY_NER"
        self.version = "2.0.0"  # Version 2 indicates unified interface
        self.status = ToolStatus.READY
        
        # Service initialization
        if service_manager is None:
            service_manager = ServiceManager()
        self.service_manager = service_manager
        self.identity_service = service_manager.get_identity_service()
        self.provenance_service = service_manager.get_provenance_service()
        self.quality_service = service_manager.get_quality_service()
        
        # spaCy model (lazy loaded)
        self.nlp = None
        self.model_name = "en_core_web_sm"
        
        # Performance monitoring
        self.performance_monitor = ToolPerformanceMonitor()
        self.performance_monitor.register_performance_requirements(
            self.tool_id,
            self.get_contract().performance_requirements
        )
        
        # Target entity types
        self.target_entity_types = {
            "PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
            "WORK_OF_ART", "LAW", "LANGUAGE", "FACILITY",
            "MONEY", "DATE", "TIME"
        }
        
        # Base confidence score
        self.base_confidence_score = ConfidenceScore.create_medium_confidence(
            value=0.75,
            evidence_weight=3
        )
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="spaCy Named Entity Recognition",
            description="Extract named entities from text using spaCy pre-trained models",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string", 
                        "minLength": 1,
                        "description": "Text to extract entities from"
                    },
                    "chunk_ref": {
                        "type": "string",
                        "description": "Reference to source chunk"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.8,
                        "description": "Minimum confidence for entity extraction"
                    }
                },
                "required": ["text", "chunk_ref"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "mention_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"},
                                "created_at": {"type": "string", "format": "date-time"}
                            },
                            "required": ["entity_id", "surface_form", "entity_type", "confidence"]
                        }
                    },
                    "total_entities": {"type": "integer"},
                    "entity_types": {
                        "type": "object",
                        "additionalProperties": {"type": "integer"}
                    },
                    "processing_stats": {
                        "type": "object",
                        "properties": {
                            "text_length": {"type": "integer"},
                            "entities_found": {"type": "integer"},
                            "entities_extracted": {"type": "integer"},
                            "confidence_threshold": {"type": "number"}
                        }
                    }
                },
                "required": ["entities", "total_entities"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 10.0,
                "max_memory_mb": 500,
                "min_accuracy": 0.85
            },
            error_conditions=[
                "EMPTY_TEXT",
                "SPACY_MODEL_NOT_AVAILABLE",
                "ENTITY_CREATION_FAILED",
                "MEMORY_LIMIT_EXCEEDED",
                "INVALID_INPUT"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction with comprehensive error handling"""
        # Start performance monitoring
        with self.performance_monitor.monitor_tool_execution(
            self.tool_id, 
            request.operation,
            request.input_data
        ) as perf_context:
            
            try:
                # Set status to processing
                self.status = ToolStatus.PROCESSING
                self._start_execution_tracking()
                
                # Validate input against contract
                if not self.validate_input(request.input_data):
                    perf_context.set_error("INVALID_INPUT")
                    return self._create_error_result(
                        "INVALID_INPUT",
                        "Input validation failed against tool contract"
                    )
                
                # Extract parameters
                text = request.input_data.get("text")
                chunk_ref = request.input_data.get("chunk_ref")
                confidence_threshold = request.input_data.get("confidence_threshold", 0.8)
                
                # Validate text is not empty
                if not text or not text.strip():
                    perf_context.set_error("EMPTY_TEXT")
                    return self._create_error_result(
                        "EMPTY_TEXT",
                        "Text input cannot be empty"
                    )
                
                # Start operation tracking
                operation_id = self.provenance_service.start_operation(
                    tool_id=self.tool_id,
                    operation_type="extract_entities",
                    used={"source": chunk_ref},
                    parameters={
                        "confidence_threshold": confidence_threshold,
                        "model": self.model_name
                    }
                )
                
                # Initialize spaCy if needed
                if not self.nlp:
                    self._initialize_spacy()
                    if not self.nlp:
                        perf_context.set_error("SPACY_MODEL_NOT_AVAILABLE")
                        return self._create_error_result(
                            "SPACY_MODEL_NOT_AVAILABLE",
                            f"spaCy model {self.model_name} not available. Install with: python -m spacy download {self.model_name}"
                        )
                
                # Process text with spaCy
                doc = self.nlp(text)
                
                # Extract entities
                entities = []
                entity_refs = []
                
                for ent in doc.ents:
                    # Filter by entity types
                    if ent.label_ not in self.target_entity_types:
                        continue
                    
                    # Skip very short entities
                    if len(ent.text.strip()) < 2:
                        continue
                    
                    # Calculate entity confidence
                    entity_confidence = self._calculate_entity_confidence(
                        ent.text, ent.label_, confidence_threshold
                    )
                    
                    if entity_confidence < confidence_threshold:
                        continue
                    
                    # Create mention through identity service
                    mention_result = self.identity_service.create_mention(
                        surface_form=ent.text,
                        start_pos=ent.start_char,
                        end_pos=ent.end_char,
                        source_ref=chunk_ref,
                        entity_type=ent.label_,
                        confidence=entity_confidence
                    )
                    
                    if mention_result.success:
                        entity_data = {
                            "entity_id": mention_result.data["entity_id"],
                            "mention_id": mention_result.data["mention_id"],
                            "surface_form": ent.text,
                            "entity_type": ent.label_,
                            "confidence": entity_confidence,
                            "start_pos": ent.start_char,
                            "end_pos": ent.end_char,
                            "created_at": datetime.now().isoformat()
                        }
                        entities.append(entity_data)
                        entity_refs.append(f"entity://{entity_data['entity_id']}")
                    else:
                        logger.warning(f"Failed to create mention for entity: {ent.text}")
                
                # Complete operation tracking
                self.provenance_service.complete_operation(
                    operation_id=operation_id,
                    outputs=entity_refs,
                    success=True,
                    metadata={
                        "entities_extracted": len(entities),
                        "entities_found": len(doc.ents),
                        "text_length": len(text)
                    }
                )
                
                # Prepare output data
                output_data = {
                    "entities": entities,
                    "total_entities": len(entities),
                    "entity_types": self._count_entity_types(entities),
                    "processing_stats": {
                        "text_length": len(text),
                        "entities_found": len(doc.ents),
                        "entities_extracted": len(entities),
                        "confidence_threshold": confidence_threshold
                    }
                }
                
                # Set performance context output
                perf_context.set_output(output_data)
                perf_context.set_accuracy(self._calculate_extraction_accuracy(len(entities), len(doc.ents)))
                
                # Create success result
                return self._create_success_result(
                    output_data,
                    {
                        "operation_id": operation_id,
                        "spacy_model": self.get_model_info()
                    }
                )
                
            except Exception as e:
                self.status = ToolStatus.ERROR
                logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
                perf_context.set_error("UNEXPECTED_ERROR")
                return self._create_error_result(
                    "UNEXPECTED_ERROR",
                    f"Unexpected error during entity extraction: {str(e)}"
                )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        try:
            # Validate against JSON schema
            jsonschema.validate(input_data, self.get_contract().input_schema)
            
            # Additional validation
            if isinstance(input_data, dict):
                text = input_data.get("text", "")
                if isinstance(text, str) and len(text) > 1000000:  # 1MB limit
                    logger.error("Text exceeds maximum size limit")
                    return False
            
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        start_time = time.time()
        
        try:
            # Check spaCy model availability
            if not self.nlp:
                self._initialize_spacy()
            
            model_available = self.nlp is not None
            
            # Test model with sample text
            can_process = False
            if model_available:
                try:
                    test_doc = self.nlp("Test entity extraction")
                    can_process = True
                except Exception:
                    pass
            
            # Check service dependencies
            dependencies_healthy = all([
                self.identity_service is not None,
                self.provenance_service is not None,
                self.quality_service is not None
            ])
            
            # Overall health status
            healthy = model_available and can_process and dependencies_healthy
            
            health_data = {
                "healthy": healthy,
                "spacy_model_available": model_available,
                "can_process_text": can_process,
                "dependencies_healthy": dependencies_healthy,
                "tool_status": self.status.value,
                "supported_entity_types": list(self.target_entity_types),
                "model_info": self.get_model_info() if model_available else None
            }
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data=health_data,
                metadata={
                    "health_check_timestamp": datetime.now().isoformat(),
                    "tool_version": self.version
                },
                execution_time=time.time() - start_time,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False, "error": str(e)},
                metadata={"health_check_timestamp": datetime.now().isoformat()},
                execution_time=time.time() - start_time,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        return self.status
    
    def cleanup(self) -> bool:
        """Clean up tool resources"""
        try:
            # Clean up spaCy model
            if self.nlp:
                # spaCy models don't have explicit cleanup, but we can clear the reference
                self.nlp = None
            
            # Clean up performance data if needed
            if hasattr(self.performance_monitor, 'cleanup'):
                self.performance_monitor.cleanup()
            
            self.status = ToolStatus.READY
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False
    
    def _initialize_spacy(self):
        """Initialize spaCy model with lazy loading"""
        try:
            import spacy
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.error(f"spaCy model {self.model_name} not found")
            self.nlp = None
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
    
    def _calculate_entity_confidence(self, text: str, entity_type: str, threshold: float) -> float:
        """Calculate confidence score for extracted entity"""
        # Base confidence from spaCy (we don't have direct access, so we estimate)
        base_confidence = 0.85
        
        # Adjust based on entity type reliability
        type_confidence_map = {
            "PERSON": 0.9,
            "ORG": 0.85,
            "GPE": 0.9,
            "PRODUCT": 0.7,
            "EVENT": 0.75,
            "WORK_OF_ART": 0.7,
            "LAW": 0.85,
            "LANGUAGE": 0.9,
            "FACILITY": 0.8,
            "MONEY": 0.95,
            "DATE": 0.8,
            "TIME": 0.8
        }
        type_factor = type_confidence_map.get(entity_type, 0.75)
        
        # Adjust based on text characteristics
        length_factor = min(1.0, len(text) / 20)  # Longer names more reliable
        
        # Calculate final confidence
        confidence = base_confidence * type_factor * (0.7 + 0.3 * length_factor)
        
        return min(0.95, max(0.1, confidence))
    
    def _count_entity_types(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type"""
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def _calculate_extraction_accuracy(self, extracted: int, found: int) -> float:
        """Calculate extraction accuracy metric"""
        if found == 0:
            return 1.0 if extracted == 0 else 0.0
        return min(1.0, extracted / found)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get spaCy model information"""
        if not self.nlp:
            return {"model": self.model_name, "loaded": False}
        
        return {
            "model": self.model_name,
            "loaded": True,
            "pipeline": self.nlp.pipe_names,
            "lang": self.nlp.lang,
            "version": getattr(self.nlp.meta, "version", "unknown")
        }


# Backward compatibility - create instance
def create_spacy_ner_tool(service_manager: Optional[ServiceManager] = None) -> SpacyNERUnified:
    """Factory function to create spaCy NER tool
    
    Args:
        service_manager: Optional service manager instance
        
    Returns:
        Configured SpacyNERUnified instance
    """
    return SpacyNERUnified(service_manager)