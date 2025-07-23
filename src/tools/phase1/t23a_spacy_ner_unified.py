"""
T23A: spaCy Named Entity Recognition - Unified Interface Implementation

Extracts named entities from text using spaCy's pre-trained models.
"""

from typing import Dict, Any, Optional, List, Set
import uuid
from datetime import datetime
import logging
import time
import psutil
import spacy
from spacy.lang.en import English

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T23ASpacyNERUnified(BaseTool):
    """T23A: spaCy Named Entity Recognition with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T23A"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        
        # Initialize spaCy model (lazy loading)
        self.nlp = None
        self._model_name = "en_core_web_sm"
        
        # Supported entity types
        self._supported_entity_types = {
            "PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
            "WORK_OF_ART", "LAW", "LANGUAGE", "DATE", 
            "TIME", "MONEY", "FACILITY", "LOC", "NORP",
            "PERCENT", "QUANTITY", "ORDINAL", "CARDINAL"
        }
        
        # Default confidence for spaCy entities
        self._base_confidence = 0.85
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="spaCy Named Entity Recognition",
            description="Extract named entities from text using spaCy pre-trained models",
            category="entity_extraction",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract entities from",
                        "minLength": 1
                    },
                    "chunk_ref": {
                        "type": "string",
                        "description": "Reference to source chunk"
                    },
                    "chunk_confidence": {
                        "type": "number",
                        "description": "Confidence score from chunk",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.8
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
                                "quality_tier": {"type": "string"},
                                "created_at": {"type": "string"}
                            },
                            "required": ["entity_id", "surface_form", "entity_type", "confidence"]
                        }
                    },
                    "total_entities": {"type": "integer"},
                    "entity_types": {"type": "object"},
                    "processing_stats": {"type": "object"}
                },
                "required": ["entities", "total_entities", "entity_types"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 10.0,  # 10 seconds for entity extraction
                "max_memory_mb": 500,        # 500MB for spaCy model
                "min_confidence": 0.7        # Minimum confidence threshold
            },
            error_conditions=[
                "EMPTY_TEXT",
                "INVALID_INPUT",
                "SPACY_MODEL_NOT_AVAILABLE",
                "ENTITY_CREATION_FAILED",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        try:
            # First check with base validation
            if not super().validate_input(input_data):
                return False
            
            # Additional validation: text must not be empty
            text = input_data.get("text", "")
            if not text or not text.strip():
                return False
            
            return True
        except Exception:
            return False
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction with unified interface"""
        self._start_execution()
        
        try:
            # Extract parameters
            text = request.input_data.get("text", "").strip()
            chunk_ref = request.input_data.get("chunk_ref")
            chunk_confidence = request.input_data.get("chunk_confidence", 0.8)
            
            # Check for empty text first
            if not text:
                return self._create_error_result(
                    request,
                    "EMPTY_TEXT",
                    "Text cannot be empty"
                )
            
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed. Required: text and chunk_ref"
                )
            
            # Load spaCy model if needed
            if not self.nlp:
                try:
                    self._load_spacy_model()
                except Exception as e:
                    return self._create_error_result(
                        request,
                        "SPACY_MODEL_NOT_AVAILABLE",
                        f"Failed to load spaCy model: {str(e)}"
                    )
            
            # Get parameters
            confidence_threshold = request.parameters.get("confidence_threshold", 0.8)
            entity_types = request.parameters.get("entity_types", None)
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="entity_extraction",
                used={"chunk": chunk_ref},
                parameters={
                    "text_length": len(text),
                    "confidence_threshold": confidence_threshold,
                    "entity_types": entity_types
                }
            )
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            entity_refs = []
            
            for ent in doc.ents:
                # Filter by entity type if specified
                if entity_types and ent.label_ not in entity_types:
                    continue
                
                # Skip very short entities
                if len(ent.text.strip()) < 2:
                    continue
                
                # Calculate entity confidence
                entity_confidence = self._calculate_entity_confidence(
                    ent.text, ent.label_, chunk_confidence
                )
                
                # Apply confidence threshold
                if entity_confidence < confidence_threshold:
                    continue
                
                # Create mention through identity service
                mention_result = self.identity_service.create_mention(
                    surface_form=ent.text,
                    entity_type=ent.label_,
                    source_ref=chunk_ref,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    confidence=entity_confidence
                )
                
                if mention_result["status"] == "success":
                    entity_id = mention_result["entity_id"]
                    mention_id = mention_result["mention_id"]
                    entity_ref = f"storage://entity/{entity_id}"
                    entity_refs.append(entity_ref)
                    
                    # Assess quality
                    quality_result = self.quality_service.assess_confidence(
                        object_ref=entity_ref,
                        base_confidence=entity_confidence,
                        factors={
                            "entity_length": min(1.0, len(ent.text) / 20),
                            "entity_type_confidence": self._get_type_confidence(ent.label_),
                            "context_confidence": chunk_confidence
                        },
                        metadata={
                            "entity_type": ent.label_,
                            "source_chunk": chunk_ref
                        }
                    )
                    
                    quality_tier = "MEDIUM"
                    if quality_result["status"] == "success":
                        entity_confidence = quality_result["confidence"]
                        quality_tier = quality_result["quality_tier"]
                    
                    entity_data = {
                        "entity_id": entity_id,
                        "mention_id": mention_id,
                        "surface_form": ent.text,
                        "entity_type": ent.label_,
                        "confidence": entity_confidence,
                        "start_pos": ent.start_char,
                        "end_pos": ent.end_char,
                        "quality_tier": quality_tier,
                        "created_at": datetime.now().isoformat()
                    }
                    entities.append(entity_data)
                else:
                    logger.warning(f"Failed to create mention for entity: {ent.text}")
            
            # Calculate entity type statistics
            entity_types_count = self._count_entity_types(entities)
            
            # Complete provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=entity_refs,
                success=True,
                metadata={
                    "total_entities": len(entities),
                    "entities_found": len(doc.ents),
                    "entities_extracted": len(entities),
                    "entity_types": entity_types_count
                }
            )
            
            # Get execution metrics
            execution_time, memory_used = self._end_execution()
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "entities": entities,
                    "total_entities": len(entities),
                    "entity_types": entity_types_count,
                    "processing_stats": {
                        "text_length": len(text),
                        "entities_found": len(doc.ents),
                        "entities_extracted": len(entities),
                        "confidence_threshold": confidence_threshold
                    }
                },
                metadata={
                    "operation_id": operation_id,
                    "spacy_model": self._model_name,
                    "tool_version": "1.0.0"
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during entity extraction: {str(e)}"
            )
    
    def _load_spacy_model(self):
        """Load spaCy model lazily"""
        try:
            self.nlp = spacy.load(self._model_name)
            logger.info(f"Loaded spaCy model: {self._model_name}")
        except IOError:
            logger.error(f"spaCy model '{self._model_name}' not found")
            raise
    
    def _calculate_entity_confidence(self, text: str, entity_type: str, chunk_confidence: float) -> float:
        """Calculate confidence score for an entity"""
        # Base confidence from spaCy
        confidence = self._base_confidence
        
        # Adjust based on entity type
        type_confidence = self._get_type_confidence(entity_type)
        confidence *= type_confidence
        
        # Adjust based on text length (longer entities are often more confident)
        length_factor = min(1.0, len(text) / 20)
        confidence *= (0.8 + 0.2 * length_factor)
        
        # Propagate chunk confidence
        confidence *= chunk_confidence
        
        return min(1.0, confidence)
    
    def _get_type_confidence(self, entity_type: str) -> float:
        """Get confidence multiplier for entity type"""
        # More reliable entity types get higher confidence
        type_confidences = {
            "PERSON": 0.95,
            "ORG": 0.93,
            "GPE": 0.92,
            "DATE": 0.90,
            "MONEY": 0.90,
            "PRODUCT": 0.88,
            "EVENT": 0.85,
            "WORK_OF_ART": 0.85,
            "LAW": 0.88,
            "LANGUAGE": 0.90,
            "TIME": 0.88,
            "FACILITY": 0.85,
            "LOC": 0.88,
            "NORP": 0.82,
            "PERCENT": 0.85,
            "QUANTITY": 0.85,
            "ORDINAL": 0.80,
            "CARDINAL": 0.80
        }
        return type_confidences.get(entity_type, 0.80)
    
    def _count_entity_types(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type"""
        type_counts = {}
        for entity in entities:
            entity_type = entity["entity_type"]
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def get_supported_entity_types(self) -> List[str]:
        """Get list of supported entity types"""
        return sorted(list(self._supported_entity_types))
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check spaCy model
            spacy_loaded = False
            try:
                if not self.nlp:
                    self._load_spacy_model()
                spacy_loaded = self.nlp is not None
            except:
                spacy_loaded = False
            
            # Check service dependencies
            services_healthy = True
            if self.services:
                try:
                    _ = self.identity_service
                    _ = self.provenance_service
                    _ = self.quality_service
                except:
                    services_healthy = False
            
            healthy = spacy_loaded and services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "spacy_model_loaded": spacy_loaded,
                    "services_healthy": services_healthy,
                    "supported_entity_types": self.get_supported_entity_types(),
                    "status": self.status.value
                },
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "spacy_model": self._model_name
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False},
                metadata={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up any resources"""
        try:
            # Clear spaCy model from memory if loaded
            if self.nlp:
                self.nlp = None
            self.status = ToolStatus.READY
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False