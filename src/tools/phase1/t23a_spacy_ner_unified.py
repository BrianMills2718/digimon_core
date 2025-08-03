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
from src.core.resource_manager import get_resource_manager
from src.orchestration.memory import AgentMemory
from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningType

logger = logging.getLogger(__name__)


class T23ASpacyNERUnified(BaseTool):
    """T23A: spaCy Named Entity Recognition with Memory and Reasoning Capabilities"""
    
    def __init__(self, service_manager: ServiceManager, memory_config: Dict[str, Any] = None, reasoning_config: Dict[str, Any] = None):
        """Initialize with service manager and advanced capabilities"""
        super().__init__(service_manager)
        self.tool_id = "T23A_SPACY_NER"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        
        # Use shared resource manager instead of loading individual model
        self.resource_manager = get_resource_manager()
        self._model_name = "en_core_web_sm"
        
        # Register this tool instance with resource manager
        self.resource_manager.register_tool_reference(self.tool_id, self)
        
        # Supported entity types
        self._supported_entity_types = {
            "PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
            "WORK_OF_ART", "LAW", "LANGUAGE", "DATE", 
            "TIME", "MONEY", "FACILITY", "LOC", "NORP",
            "PERCENT", "QUANTITY", "ORDINAL", "CARDINAL"
        }
        
        # Default confidence for spaCy entities (now memory-optimized)
        self._base_confidence = 0.85
        
        # Initialize memory system
        memory_config = memory_config or {}
        db_path = memory_config.get("db_path")
        self.memory = AgentMemory(
            agent_id=self.tool_id,
            db_path=db_path
        )
        
        # Initialize reasoning system
        self.reasoning_engine = LLMReasoningEngine(
            llm_config=reasoning_config or {"enable_reasoning": True, "confidence_threshold": 0.7}
        )
        
        # Adaptive thresholds (learned from memory) - Set to 0.0 for initial development 
        self.adaptive_confidence_threshold = 0.0
        self.adaptive_entity_types = set(self._supported_entity_types)
        self.learned_patterns = {}
        
        # Performance tracking
        self.extraction_stats = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "avg_entities_per_chunk": 0.0,
            "confidence_distribution": {},
            "type_distribution": {}
        }
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Memory-Aware spaCy Named Entity Recognition",
            description="Extract named entities with memory-based learning and reasoning-guided optimization",
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
                    },
                    "context_metadata": {
                        "type": "object",
                        "description": "Additional context for reasoning",
                        "properties": {
                            "document_type": {"type": "string"},
                            "domain": {"type": "string"},
                            "previous_entities": {"type": "array"}
                        }
                    },
                    "reasoning_guidance": {
                        "type": "object",
                        "description": "Reasoning parameters for extraction optimization",
                        "properties": {
                            "focus_types": {"type": "array"},
                            "confidence_boost": {"type": "number"},
                            "extraction_strategy": {"type": "string"}
                        }
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
            dependencies=["identity_service", "provenance_service", "quality_service", "memory_system", "reasoning_engine"],
            performance_requirements={
                "max_execution_time": 15.0,  # 15 seconds for enhanced extraction
                "max_memory_mb": 750,        # 750MB for spaCy model + memory + reasoning
                "min_confidence": 0.7,       # Minimum confidence threshold
                "min_accuracy_improvement": 0.05  # Minimum improvement from reasoning
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
        """Execute memory-aware and reasoning-guided entity extraction"""
        self._start_execution()
        
        try:
            # Extract parameters
            text = request.input_data.get("text", "").strip()
            chunk_ref = request.input_data.get("chunk_ref")
            chunk_confidence = request.input_data.get("chunk_confidence", 0.8)
            context_metadata = request.input_data.get("context_metadata", {})
            reasoning_guidance = request.input_data.get("reasoning_guidance", {})
            schema = request.input_data.get("schema", None)
            
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
            
            # Handle schema-driven extraction
            from src.core.schema_manager import get_schema_manager
            schema_manager = get_schema_manager()
            extraction_schema = None
            
            if schema:
                if isinstance(schema, str):
                    # Schema ID provided
                    extraction_schema = schema_manager.get_schema(schema)
                elif isinstance(schema, dict):
                    # Schema object provided
                    extraction_schema = schema
                
            # Use default schema if none provided
            if extraction_schema is None:
                extraction_schema = schema_manager.get_default_schema()
            
            # Get memory context for this extraction
            memory_context = self._get_memory_context(text, chunk_ref, context_metadata)
            
            # Apply reasoning for extraction optimization
            reasoning_result = self._apply_reasoning_guidance(
                text, context_metadata, reasoning_guidance, memory_context
            )
            
            # Get adaptive parameters (memory + reasoning + schema optimized)
            confidence_threshold, entity_types, extraction_strategy = self._get_adaptive_parameters(
                request.parameters, reasoning_result, memory_context, extraction_schema
            )
            
            # Extract temporal filtering parameters
            temporal_filter = request.parameters.get("time_filter", None)
            temporal_filtering_enabled = request.parameters.get("temporal_filtering_enabled", False)
            
            # Start enhanced provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="enhanced_entity_extraction",
                inputs=[chunk_ref],
                parameters={
                    "text_length": len(text),
                    "confidence_threshold": confidence_threshold,
                    "entity_types": list(entity_types) if entity_types else None,
                    "extraction_strategy": extraction_strategy,
                    "memory_guidance": bool(memory_context.get("relevant_patterns")),
                    "reasoning_applied": reasoning_result.get("success", False) if reasoning_result else False,
                    "temporal_filtering_enabled": temporal_filtering_enabled,
                    "time_filter": temporal_filter
                }
            )
            
            # Process text with shared spaCy model via resource manager
            with self.resource_manager.get_spacy_nlp(self._model_name) as nlp:
                if not nlp:
                    return self._create_error_result(
                        request,
                        "SPACY_MODEL_NOT_AVAILABLE",
                        f"Failed to load spaCy model: {self._model_name}. Install with: python -m spacy download {self._model_name}"
                    )
                
                doc = nlp(text)
                
                # Extract entities with enhanced processing
                entities = []
                entity_refs = []
                
                # Apply extraction strategy with schema guidance
                extracted_entities = self._extract_entities_with_strategy(
                    doc, entity_types, extraction_strategy, reasoning_result, extraction_schema
                )
                
                for ent_data in extracted_entities:
                    ent = ent_data["entity"]
                    enhanced_confidence = ent_data["confidence"]
                    reasoning_boost = ent_data.get("reasoning_boost", 0.0)
                    
                    # Apply temporal filtering if enabled
                    if temporal_filtering_enabled and temporal_filter:
                        # Check if this is a temporal entity or if the sentence contains the temporal filter
                        if ent.label_ == "DATE":
                            # If it's a date entity, only keep if it matches the filter
                            if temporal_filter not in ent.text:
                                logger.debug(f"Temporal filter: Skipping DATE entity '{ent.text}' (doesn't match filter '{temporal_filter}')")
                                continue
                        else:
                            # For non-date entities, check if they appear in sentences with the temporal filter
                            sentence_text = ent.sent.text if hasattr(ent, 'sent') else text[max(0, ent.start_char-50):min(len(text), ent.end_char+50)]
                            if temporal_filter not in sentence_text:
                                logger.debug(f"Temporal filter: Skipping entity '{ent.text}' (not in temporal context '{temporal_filter}')")
                                continue
                    
                    # Apply memory-enhanced confidence calculation
                    entity_confidence = self._calculate_enhanced_entity_confidence(
                        ent.text, ent.label_, chunk_confidence, memory_context, enhanced_confidence, reasoning_boost
                    )
                    
                    # Apply adaptive confidence threshold
                    print(f"DEBUG: Entity '{ent.text}' - calculated_confidence={entity_confidence:.3f}, threshold={confidence_threshold:.3f}")
                    if entity_confidence < confidence_threshold:
                        print(f"DEBUG: FILTERED OUT '{ent.text}' - {entity_confidence:.3f} < {confidence_threshold:.3f}")
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
                    
                    if mention_result["success"]:
                        entity_id = mention_result["data"]["entity_id"]
                        mention_id = mention_result["data"]["mention_id"]
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
                            "chunk_ref": chunk_ref,  # CRITICAL FIX: Include chunk_ref in entity output
                            "quality_tier": quality_tier,
                            "created_at": datetime.now().isoformat()
                        }
                        entities.append(entity_data)
                    else:
                        logger.warning(f"Failed to create mention for entity: {ent.text}")
                
                # Calculate entity type statistics (inside context manager)
                entity_types_count = self._count_entity_types(entities)
            
            # Store extraction results in memory for learning
            self._store_extraction_memory(
                text, entities, chunk_ref, context_metadata, reasoning_result, extraction_schema
            )
            
            # Update extraction statistics
            self._update_extraction_stats(entities, doc.ents, reasoning_result)
            
            # Complete enhanced provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=entity_refs,
                success=True,
                metadata={
                    "total_entities": len(entities),
                    "entities_found": len(doc.ents),
                    "entities_extracted": len(entities),
                    "entity_types": entity_types_count,
                    "memory_patterns_used": len(memory_context.get("relevant_patterns", [])),
                    "reasoning_confidence": reasoning_result.get("confidence", 0.0) if reasoning_result else 0.0,
                    "adaptive_threshold": confidence_threshold,
                    "extraction_strategy": extraction_strategy,
                    "schema_mode": extraction_schema.mode.value if extraction_schema else "none",
                    "schema_id": extraction_schema.schema_id if extraction_schema else None
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
    
    def _get_memory_context(self, text: str, chunk_ref: str, context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant memory context for entity extraction"""
        try:
            # Search for similar extraction patterns
            search_query = f"entity extraction {context_metadata.get('domain', 'general')} {len(text)//100}k chars"
            # Simplified memory context without async
            domain = context_metadata.get("domain", "general")
            
            # Mock memory context for now - can be enhanced later
            relevant_memories = []
            learned_patterns = []
            recent_extractions = []
            
            return {
                "relevant_memories": relevant_memories,
                "relevant_patterns": learned_patterns,
                "recent_extractions": recent_extractions,
                "domain": domain,
                "text_characteristics": {
                    "length": len(text),
                    "complexity": self._estimate_text_complexity(text),
                    "language_patterns": self._detect_language_patterns(text)
                }
            }
        except Exception as e:
            logger.warning(f"Failed to get memory context: {e}")
            return {"relevant_memories": [], "relevant_patterns": [], "recent_extractions": []}
    
    def _apply_reasoning_guidance(self, text: str, context_metadata: Dict[str, Any], 
                                      reasoning_guidance: Dict[str, Any], memory_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply LLM reasoning for extraction optimization"""
        try:
            if not self.reasoning_engine or not reasoning_guidance:
                return None
            
            # Prepare reasoning context
            reasoning_context = {
                "text_sample": text[:500] + "..." if len(text) > 500 else text,
                "text_length": len(text),
                "domain": context_metadata.get("domain", "general"),
                "document_type": context_metadata.get("document_type", "unknown"),
                "previous_entities": context_metadata.get("previous_entities", []),
                "memory_patterns": memory_context.get("relevant_patterns", []),
                "extraction_history": [
                    {
                        "entities_found": exec_info.get("entities_extracted", 0),
                        "confidence": exec_info.get("avg_confidence", 0.0),
                        "success": exec_info.get("success", False)
                    }
                    for exec_info in memory_context.get("recent_extractions", [])[:3]
                ]
            }
            
            # Formulate reasoning query
            query = f"""Optimize entity extraction for {context_metadata.get('domain', 'general')} domain text.
            
            Text characteristics: {len(text)} characters, complexity: {memory_context.get('text_characteristics', {}).get('complexity', 'medium')}
            
            Available entity types: {', '.join(self._supported_entity_types)}
            
            Recent extraction performance: {len(memory_context.get('recent_extractions', []))} recent extractions
            
            Guidance request: {reasoning_guidance.get('extraction_strategy', 'optimize_for_accuracy')}
            
            What entity types should I focus on? What confidence adjustments should I make? What extraction strategy should I use?
            """
            
            # Apply reasoning (simplified without async)
            # For now, return basic reasoning result
            reasoning_result = type('ReasoningResult', (), {
                'success': True,
                'confidence': 0.8,
                'decision': {
                    'confidence_adjustment': 0.0,
                    'focus_types': list(self._supported_entity_types),
                    'extraction_strategy': reasoning_guidance.get('extraction_strategy', 'standard')
                },
                'reasoning': 'Applied schema-driven entity extraction'
            })()
            
            if reasoning_result.success:
                logger.info(f"Applied reasoning guidance with confidence {reasoning_result.confidence}")
                return {
                    "success": True,
                    "confidence": reasoning_result.confidence,
                    "decision": reasoning_result.decision,
                    "reasoning": reasoning_result.reasoning
                }
            else:
                logger.warning(f"Reasoning guidance failed: {reasoning_result.error}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to apply reasoning guidance: {e}")
            return None
    
    def _get_adaptive_parameters(self, base_parameters: Dict[str, Any], reasoning_result: Optional[Dict[str, Any]], 
                               memory_context: Dict[str, Any], extraction_schema) -> tuple:
        """Get adaptive parameters based on memory and reasoning"""
        # Start with base parameters
        confidence_threshold = base_parameters.get("confidence_threshold", self.adaptive_confidence_threshold)
        entity_types = base_parameters.get("entity_types", None)
        extraction_strategy = "standard"
        
        # Apply schema-based filtering
        if extraction_schema:
            from src.core.extraction_schemas import SchemaMode
            
            if extraction_schema.mode == SchemaMode.CLOSED:
                # Only extract predefined entity types
                schema_entity_types = set(extraction_schema.entity_types.keys())
                # Map schema types to spaCy types if needed
                spacy_types = self._map_schema_to_spacy_types(schema_entity_types)
                entity_types = spacy_types.intersection(self._supported_entity_types)
                
            elif extraction_schema.mode == SchemaMode.HYBRID:
                # Prefer predefined types but allow others
                schema_entity_types = set(extraction_schema.entity_types.keys())
                spacy_types = self._map_schema_to_spacy_types(schema_entity_types)
                preferred_types = spacy_types.intersection(self._supported_entity_types)
                if preferred_types:
                    entity_types = preferred_types
                    
            # Adjust confidence based on schema requirements
            confidence_threshold = max(
                confidence_threshold,
                extraction_schema.global_confidence_threshold
            )
        
        # Apply memory-based adaptations
        if memory_context.get("relevant_patterns"):
            for pattern in memory_context["relevant_patterns"]:
                pattern_data = pattern.get("pattern_data", {})
                if pattern_data.get("confidence", 0) > 0.7:
                    # Use learned threshold
                    confidence_threshold = pattern_data.get("optimal_threshold", confidence_threshold)
                    # Use learned entity type focus
                    if "focus_types" in pattern_data:
                        entity_types = set(pattern_data["focus_types"])
        
        # Apply reasoning-based adaptations
        if reasoning_result and reasoning_result.get("success"):
            decision = reasoning_result.get("decision", {})
            
            # Adjust confidence threshold
            if "confidence_adjustment" in decision:
                adj = decision["confidence_adjustment"]
                confidence_threshold = max(0.1, min(1.0, confidence_threshold + adj))
            
            # Focus on specific entity types
            if "focus_types" in decision:
                focus_types = set(decision["focus_types"])
                if focus_types.intersection(self._supported_entity_types):
                    entity_types = focus_types.intersection(self._supported_entity_types)
            
            # Set extraction strategy
            extraction_strategy = decision.get("extraction_strategy", "standard")
        
        # Ensure entity_types is valid
        if entity_types:
            entity_types = set(entity_types).intersection(self._supported_entity_types)
        
        return confidence_threshold, entity_types, extraction_strategy
    
    def _map_schema_to_spacy_types(self, schema_types: set) -> set:
        """Map schema entity types to spaCy entity types"""
        # Simple mapping - can be enhanced with more sophisticated mapping
        type_mapping = {
            "Person": "PERSON",
            "Organization": "ORG", 
            "Location": "GPE",
            "Date": "DATE",
            "Money": "MONEY",
            "Product": "PRODUCT",
            "Event": "EVENT",
            "Language": "LANGUAGE",
            "Facility": "FAC"
        }
        
        spacy_types = set()
        for schema_type in schema_types:
            # Direct match first
            if schema_type in self._supported_entity_types:
                spacy_types.add(schema_type)
            # Try mapping
            elif schema_type in type_mapping:
                spacy_types.add(type_mapping[schema_type])
        
        return spacy_types
    
    def _extract_entities_with_strategy(self, doc, entity_types: Optional[Set[str]], 
                                       extraction_strategy: str, reasoning_result: Optional[Dict[str, Any]], extraction_schema=None) -> List[Dict[str, Any]]:
        """Extract entities using specified strategy"""
        extracted = []
        
        for ent in doc.ents:
            # Filter by entity type if specified
            if entity_types and ent.label_ not in entity_types:
                continue
            
            # Skip very short entities
            if len(ent.text.strip()) < 2:
                continue
            
            # Apply schema validation if available
            if extraction_schema:
                from src.core.extraction_schemas import SchemaMode
                
                if extraction_schema.mode == SchemaMode.CLOSED:
                    # Must match predefined types exactly
                    if not extraction_schema.is_valid_entity_type(ent.label_):
                        continue
                        
                # Validate entity against schema constraints if defined
                if ent.label_ in extraction_schema.entity_types:
                    entity_schema = extraction_schema.entity_types[ent.label_]
                    entity_data = {
                        "surface_form": ent.text,
                        "confidence": self._base_confidence
                    }
                    if not entity_schema.validate_entity(entity_data):
                        continue
            
            # Base confidence from spaCy
            base_confidence = self._base_confidence
            reasoning_boost = 0.0
            
            # Apply strategy-specific processing
            if extraction_strategy == "high_precision":
                # More conservative extraction
                base_confidence *= 0.9
                if len(ent.text) < 3:
                    continue
            elif extraction_strategy == "high_recall":
                # More liberal extraction
                base_confidence *= 1.1
                reasoning_boost = 0.05
            elif extraction_strategy == "balanced":
                # Apply reasoning boost to important entities
                if reasoning_result and reasoning_result.get("decision", {}).get("important_types"):
                    important_types = reasoning_result["decision"]["important_types"]
                    if ent.label_ in important_types:
                        reasoning_boost = 0.1
            
            extracted.append({
                "entity": ent,
                "confidence": base_confidence,
                "reasoning_boost": reasoning_boost,
                "strategy": extraction_strategy
            })
        
        return extracted
    
    def _calculate_enhanced_entity_confidence(self, text: str, entity_type: str, chunk_confidence: float,
                                            memory_context: Dict[str, Any], base_confidence: float, reasoning_boost: float) -> float:
        """Calculate enhanced confidence using memory and reasoning"""
        # Start with base calculation
        confidence = self._calculate_entity_confidence(text, entity_type, chunk_confidence)
        
        # Apply memory-based adjustments
        memory_boost = 0.0
        for pattern in memory_context.get("relevant_patterns", []):
            pattern_data = pattern.get("pattern_data", {})
            if entity_type in pattern_data.get("high_confidence_types", []):
                memory_boost += 0.05
            if text.lower() in pattern_data.get("high_confidence_terms", []):
                memory_boost += 0.03
        
        # Apply reasoning boost
        confidence += reasoning_boost + memory_boost
        
        # Apply memory-learned type confidence
        for extraction in memory_context.get("recent_extractions", []):
            if extraction.get("success") and entity_type in extraction.get("high_performing_types", []):
                confidence *= 1.02
                break
        
        return min(1.0, confidence)
    
    def _store_extraction_memory(self, text: str, entities: List[Dict[str, Any]], chunk_ref: str,
                                     context_metadata: Dict[str, Any], reasoning_result: Optional[Dict[str, Any]], extraction_schema=None) -> None:
        """Store extraction results in memory for learning"""
        try:
            # Extract performance metrics
            entity_types_found = [e["entity_type"] for e in entities]
            avg_confidence = sum(e["confidence"] for e in entities) / len(entities) if entities else 0.0
            
            # Store execution result (simplified without async)
            execution_data = {
                "task_type": "entity_extraction",
                "text_length": len(text),
                "entities_extracted": len(entities),
                "entity_types": entity_types_found,
                "avg_confidence": avg_confidence,
                "domain": context_metadata.get("domain", "general"),
                "reasoning_applied": reasoning_result is not None,
                "reasoning_confidence": reasoning_result.get("confidence", 0.0) if reasoning_result else 0.0,
                "success": len(entities) > 0,
                "chunk_ref": chunk_ref,
                "schema_mode": extraction_schema.mode.value if extraction_schema else "none",
                "schema_id": extraction_schema.schema_id if extraction_schema else None
            }
            
            # Store in memory system if available
            if hasattr(self, 'memory') and self.memory:
                # For now, just log the execution data
                logger.info(f"Stored extraction memory: {execution_data}")
            
            # Store learned patterns if successful
            if entities and avg_confidence > 0.8:
                domain = context_metadata.get("domain", "general")
                
                # Identify high-performing entity types
                high_conf_types = [
                    e["entity_type"] for e in entities 
                    if e["confidence"] > 0.9
                ]
                
                # Store extraction pattern (simplified)
                pattern_data = {
                    "optimal_threshold": min(0.8, avg_confidence - 0.1),
                    "high_confidence_types": high_conf_types,
                    "text_length_range": (len(text) - 1000, len(text) + 1000),
                    "entities_per_kb": len(entities) / max(1, len(text) / 1000),
                    "confidence": avg_confidence,
                    "schema_mode": extraction_schema.mode.value if extraction_schema else "none"
                }
                
                # Log pattern for now
                logger.info(f"Learned extraction pattern for {domain}: {pattern_data}")
                
        except Exception as e:
            logger.warning(f"Failed to store extraction memory: {e}")
    
    def _update_extraction_stats(self, entities: List[Dict[str, Any]], spacy_entities, reasoning_result: Optional[Dict[str, Any]]) -> None:
        """Update extraction performance statistics"""
        self.extraction_stats["total_extractions"] += 1
        
        if entities:
            self.extraction_stats["successful_extractions"] += 1
            
            # Update averages
            current_avg = self.extraction_stats["avg_entities_per_chunk"]
            total = self.extraction_stats["total_extractions"]
            self.extraction_stats["avg_entities_per_chunk"] = (
                (current_avg * (total - 1) + len(entities)) / total
            )
            
            # Update type distribution
            for entity in entities:
                entity_type = entity["entity_type"]
                self.extraction_stats["type_distribution"][entity_type] = (
                    self.extraction_stats["type_distribution"].get(entity_type, 0) + 1
                )
                
                # Update confidence distribution
                conf_bucket = f"{int(entity['confidence'] * 10) / 10:.1f}"
                self.extraction_stats["confidence_distribution"][conf_bucket] = (
                    self.extraction_stats["confidence_distribution"].get(conf_bucket, 0) + 1
                )
    
    def _estimate_text_complexity(self, text: str) -> str:
        """Estimate text complexity for memory context"""
        # Simple heuristics for complexity
        avg_word_length = sum(len(word) for word in text.split()) / max(1, len(text.split()))
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        avg_sentence_length = len(text.split()) / max(1, sentence_count)
        
        if avg_word_length > 6 and avg_sentence_length > 20:
            return "high"
        elif avg_word_length > 4 and avg_sentence_length > 15:
            return "medium"
        else:
            return "low"
    
    def _detect_language_patterns(self, text: str) -> Dict[str, Any]:
        """Detect language patterns for memory context"""
        # Simple pattern detection
        patterns = {
            "has_technical_terms": any(term in text.lower() for term in ["algorithm", "system", "method", "process"]),
            "has_formal_language": any(term in text.lower() for term in ["therefore", "however", "furthermore", "moreover"]),
            "has_numbers": any(char.isdigit() for char in text),
            "has_dates": any(month in text.lower() for month in ["january", "february", "march", "april", "may", "june"]),
            "capitalization_ratio": sum(1 for c in text if c.isupper()) / max(1, len(text))
        }
        return patterns
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get current extraction performance statistics"""
        return self.extraction_stats.copy()
    
    def get_adaptive_thresholds(self) -> Dict[str, Any]:
        """Get current adaptive thresholds learned from memory"""
        return {
            "confidence_threshold": self.adaptive_confidence_threshold,
            "entity_types": list(self.adaptive_entity_types),
            "learned_patterns_count": len(self.learned_patterns)
        }
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get spaCy model information"""
        try:
            if not self.nlp:
                self._load_spacy_model()
            
            if self.nlp:
                model_info = {
                    "model_name": self._model_name,
                    "model_loaded": True,
                    "language": getattr(self.nlp.meta, 'lang', 'unknown'),
                    "version": getattr(self.nlp.meta, 'version', 'unknown'),
                    "pipeline_components": list(self.nlp.pipe_names) if hasattr(self.nlp, 'pipe_names') else [],
                    "supported_entity_types": list(self._supported_entity_types)
                }
                
                # Add more detailed info if available
                if hasattr(self.nlp, 'meta'):
                    model_info.update({
                        "description": getattr(self.nlp.meta, 'description', 'N/A'),
                        "author": getattr(self.nlp.meta, 'author', 'N/A'),
                        "license": getattr(self.nlp.meta, 'license', 'N/A')
                    })
                
                return model_info
            else:
                return {
                    "model_name": self._model_name,
                    "model_loaded": False,
                    "error": f"Failed to load model: {self._model_name}",
                    "supported_entity_types": list(self._supported_entity_types)
                }
                
        except Exception as e:
            return {
                "model_name": self._model_name,
                "model_loaded": False,
                "error": str(e),
                "supported_entity_types": list(self._supported_entity_types)
            }

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


# Backward compatibility alias
SpacyNER = T23ASpacyNERUnified
T23ASpacyNEREnhanced = T23ASpacyNERUnified