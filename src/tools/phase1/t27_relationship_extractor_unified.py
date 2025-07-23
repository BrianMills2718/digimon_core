"""
T27 Relationship Extractor Unified Tool

Extracts relationships between entities using real spaCy dependency parsing and pattern matching.
Implements unified BaseTool interface with comprehensive relationship extraction capabilities.
"""

import spacy
import re
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

class T27RelationshipExtractorUnified(BaseTool):
    """
    Relationship Extractor tool for extracting semantic relationships between entities.
    
    Features:
    - Real spaCy dependency parsing
    - Pattern-based relationship extraction
    - Proximity-based fallback relationships
    - Multiple relationship types
    - Confidence scoring
    - Quality assessment integration
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T27"
        self.name = "Relationship Extractor"
        self.category = "text_processing"
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize spaCy model for dependency parsing
        self.nlp = None
        self._initialize_spacy()
        
        # Relationship extraction patterns
        self.relationship_patterns = self._initialize_patterns()
        
        # Processing stats
        self.relationships_extracted = 0
        self.patterns_matched = 0
        self.dependency_extractions = 0

    def _initialize_spacy(self):
        """Initialize spaCy model for dependency parsing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("spaCy model loaded successfully")
        except OSError:
            self.logger.warning("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

    def _initialize_patterns(self) -> List[Dict[str, Any]]:
        """Initialize relationship extraction patterns"""
        return [
            {
                "name": "ownership",
                "pattern": r"([^.]+?)\s+(owns?|owned|possesses?|has)\s+([^.]+)",
                "relationship_type": "OWNS",
                "confidence": 0.9
            },
            {
                "name": "employment",
                "pattern": r"([^.]+?)\s+(works?\s+(?:at|for)|employed\s+by|CEO\s+of|president\s+of)\s+([^.]+)",
                "relationship_type": "WORKS_FOR",
                "confidence": 0.85
            },
            {
                "name": "location",
                "pattern": r"([^.]+?)\s+(?:is\s+)?(?:located\s+in|based\s+in|from)\s+([^.]+)",
                "relationship_type": "LOCATED_IN",
                "confidence": 0.8
            },
            {
                "name": "partnership",
                "pattern": r"([^.]+?)\s+(?:partners?\s+with|collaborates?\s+with|works?\s+with)\s+([^.]+)",
                "relationship_type": "PARTNERS_WITH",
                "confidence": 0.75
            },
            {
                "name": "creation",
                "pattern": r"([^.]+?)\s+(?:created|founded|established|built|developed)\s+([^.]+)",
                "relationship_type": "CREATED",
                "confidence": 0.8
            },
            {
                "name": "leadership",
                "pattern": r"([^.]+?)\s+(?:leads?|manages?|heads?|directs?)\s+([^.]+)",
                "relationship_type": "LEADS",
                "confidence": 0.75
            },
            {
                "name": "membership",
                "pattern": r"([^.]+?)\s+(?:is\s+)?(?:member\s+of|belongs\s+to|part\s+of)\s+([^.]+)",
                "relationship_type": "MEMBER_OF",
                "confidence": 0.7
            }
        ]

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute relationship extraction with real spaCy processing"""
        self._start_execution()
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message=validation_result["error"],
                    error_code=ToolErrorCode.INVALID_INPUT,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            text = request.input_data.get("text", "")
            entities = request.input_data.get("entities", [])
            chunk_ref = request.input_data.get("chunk_ref", "")
            confidence_threshold = request.parameters.get("confidence_threshold", 0.5)
            
            # Extract relationships using multiple methods
            relationships = self._extract_relationships_comprehensive(
                text, entities, chunk_ref, confidence_threshold
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(relationships)
            
            # Create service mentions for extracted relationships
            self._create_service_mentions(relationships, request.input_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "relationships": relationships,
                    "relationship_count": len(relationships),
                    "confidence": overall_confidence,
                    "processing_method": "multi_method_extraction",
                    "extraction_stats": {
                        "pattern_matches": self.patterns_matched,
                        "dependency_extractions": self.dependency_extractions,
                        "total_extracted": len(relationships)
                    }
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "spacy_available": self.nlp is not None,
                    "confidence_threshold": confidence_threshold,
                    "entity_count": len(entities),
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            self.logger.error(f"Relationship extraction error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"Relationship extraction failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for relationship extraction"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        if "text" not in input_data:
            return {"valid": False, "error": "Missing required field: text"}
        
        if not input_data["text"] or not input_data["text"].strip():
            return {"valid": False, "error": "Text cannot be empty"}
        
        if "entities" not in input_data:
            return {"valid": False, "error": "Missing required field: entities"}
        
        entities = input_data["entities"]
        if not isinstance(entities, list):
            return {"valid": False, "error": "Entities must be a list"}
        
        if len(entities) < 2:
            return {"valid": False, "error": "Need at least 2 entities for relationship extraction"}
        
        # Validate entity structure
        for i, entity in enumerate(entities):
            if not isinstance(entity, dict):
                return {"valid": False, "error": f"Entity {i} must be a dictionary"}
            
            required_fields = ["text", "label", "start", "end"]
            for field in required_fields:
                if field not in entity:
                    return {"valid": False, "error": f"Entity {i} missing required field: {field}"}
        
        return {"valid": True}

    def _extract_relationships_comprehensive(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships using multiple methods"""
        relationships = []
        
        # Method 1: Pattern-based extraction
        pattern_relationships = self._extract_pattern_relationships(
            text, entities, chunk_ref, confidence_threshold
        )
        relationships.extend(pattern_relationships)
        
        # Method 2: spaCy dependency parsing (if available)
        if self.nlp:
            dependency_relationships = self._extract_dependency_relationships(
                text, entities, chunk_ref, confidence_threshold
            )
            relationships.extend(dependency_relationships)
        
        # Method 3: Proximity-based relationships (fallback)
        proximity_relationships = self._extract_proximity_relationships(
            text, entities, chunk_ref, confidence_threshold
        )
        relationships.extend(proximity_relationships)
        
        # Remove duplicates and filter by confidence
        relationships = self._deduplicate_and_filter_relationships(
            relationships, confidence_threshold
        )
        
        return relationships

    def _extract_pattern_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships using regex patterns"""
        relationships = []
        
        for pattern_info in self.relationship_patterns:
            pattern = pattern_info["pattern"]
            rel_type = pattern_info["relationship_type"]
            base_confidence = pattern_info["confidence"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                if match.lastindex >= 2:
                    subject_text = match.group(1).strip()
                    object_text = match.group(match.lastindex).strip()
                    
                    # Find matching entities
                    subject_entity = self._find_matching_entity(subject_text, entities)
                    object_entity = self._find_matching_entity(object_text, entities)
                    
                    if subject_entity and object_entity and subject_entity != object_entity:
                        confidence = self._calculate_relationship_confidence(
                            base_confidence, 
                            (subject_entity.get("confidence", 0.8) + object_entity.get("confidence", 0.8)) / 2
                        )
                        
                        if confidence >= confidence_threshold:
                            relationship = {
                                "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                                "relationship_type": rel_type,
                                "subject": {
                                    "text": subject_entity["text"],
                                    "label": subject_entity["label"],
                                    "start": subject_entity["start"],
                                    "end": subject_entity["end"]
                                },
                                "object": {
                                    "text": object_entity["text"],
                                    "label": object_entity["label"],
                                    "start": object_entity["start"],
                                    "end": object_entity["end"]
                                },
                                "confidence": confidence,
                                "extraction_method": "pattern_based",
                                "pattern_name": pattern_info["name"],
                                "evidence_text": match.group(0),
                                "source_chunk": chunk_ref,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            relationships.append(relationship)
                            self.patterns_matched += 1
        
        return relationships

    def _extract_dependency_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships using spaCy dependency parsing"""
        if not self.nlp:
            return []
        
        relationships = []
        
        try:
            doc = self.nlp(text)
            
            # Look for subject-verb-object patterns
            for token in doc:
                if token.dep_ in ["nsubj", "nsubjpass"]:  # Subject
                    verb = token.head
                    
                    # Find objects
                    objects = [child for child in verb.children 
                             if child.dep_ in ["dobj", "pobj", "attr"]]
                    
                    for obj in objects:
                        # Find entities that match subject and object
                        subject_entity = self._find_entity_by_position(
                            token.idx, token.idx + len(token.text), entities
                        )
                        object_entity = self._find_entity_by_position(
                            obj.idx, obj.idx + len(obj.text), entities
                        )
                        
                        if subject_entity and object_entity and subject_entity != object_entity:
                            rel_type = self._classify_verb_relationship(verb.lemma_)
                            confidence = self._calculate_relationship_confidence(
                                0.75,  # Base confidence for dependency parsing
                                (subject_entity.get("confidence", 0.8) + object_entity.get("confidence", 0.8)) / 2
                            )
                            
                            if confidence >= confidence_threshold:
                                relationship = {
                                    "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                                    "relationship_type": rel_type,
                                    "subject": subject_entity,
                                    "object": object_entity,
                                    "confidence": confidence,
                                    "extraction_method": "dependency_parsing",
                                    "verb": verb.lemma_,
                                    "evidence_text": f"{token.text} {verb.text} {obj.text}",
                                    "source_chunk": chunk_ref,
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                relationships.append(relationship)
                                self.dependency_extractions += 1
        
        except Exception as e:
            self.logger.warning(f"Dependency parsing failed: {e}")
        
        return relationships

    def _extract_proximity_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships based on entity proximity"""
        relationships = []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda e: e["start"])
        
        for i, entity1 in enumerate(sorted_entities):
            for j, entity2 in enumerate(sorted_entities[i+1:], i+1):
                # Calculate distance
                distance = entity2["start"] - entity1["end"]
                
                # Only consider entities within 50 characters
                if distance < 50:
                    # Look for connecting words
                    between_text = text[entity1["end"]:entity2["start"]].strip()
                    
                    # Check for relationship indicators
                    if any(word in between_text.lower() for word in [
                        "and", "with", "of", "in", "at", "for", "by", "'s"
                    ]):
                        confidence = self._calculate_proximity_confidence(
                            distance, 
                            (entity1.get("confidence", 0.8) + entity2.get("confidence", 0.8)) / 2
                        )
                        
                        if confidence >= confidence_threshold:
                            relationship = {
                                "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                                "relationship_type": "RELATED_TO",
                                "subject": entity1,
                                "object": entity2,
                                "confidence": confidence,
                                "extraction_method": "proximity_based",
                                "entity_distance": distance,
                                "connecting_text": between_text,
                                "source_chunk": chunk_ref,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            relationships.append(relationship)
        
        return relationships

    def _find_matching_entity(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find entity that matches the given text"""
        text_lower = text.lower().strip()
        
        for entity in entities:
            entity_text = entity["text"].lower().strip()
            if entity_text == text_lower:
                return entity
            # Check if text contains the entity or vice versa
            if text_lower in entity_text or entity_text in text_lower:
                return entity
        
        return None

    def _find_entity_by_position(
        self, 
        start_pos: int, 
        end_pos: int, 
        entities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find entity that overlaps with the given position"""
        for entity in entities:
            # Check if positions overlap
            if (start_pos <= entity["start"] < end_pos or 
                entity["start"] <= start_pos < entity["end"]):
                return entity
        return None

    def _classify_verb_relationship(self, verb: str) -> str:
        """Classify relationship type based on verb"""
        verb_to_relation = {
            "own": "OWNS", "have": "HAS", "possess": "OWNS",
            "work": "WORKS_FOR", "employ": "EMPLOYS",
            "create": "CREATED", "found": "FOUNDED", "establish": "ESTABLISHED",
            "lead": "LEADS", "manage": "MANAGES", "head": "HEADS",
            "locate": "LOCATED_IN", "base": "BASED_IN",
            "partner": "PARTNERS_WITH", "collaborate": "COLLABORATES_WITH"
        }
        
        return verb_to_relation.get(verb, "RELATED_TO")

    def _calculate_relationship_confidence(self, pattern_confidence: float, entity_confidence: float) -> float:
        """Calculate relationship confidence score"""
        return min(1.0, (pattern_confidence * 0.6 + entity_confidence * 0.4))

    def _calculate_proximity_confidence(self, distance: int, entity_confidence: float) -> float:
        """Calculate confidence for proximity-based relationships"""
        distance_factor = max(0.3, 1.0 - (distance / 50.0))
        return min(1.0, distance_factor * 0.5 + entity_confidence * 0.5)

    def _calculate_overall_confidence(self, relationships: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for all extracted relationships"""
        if not relationships:
            return 0.0
        
        total_confidence = sum(rel["confidence"] for rel in relationships)
        return total_confidence / len(relationships)

    def _deduplicate_and_filter_relationships(
        self, 
        relationships: List[Dict[str, Any]], 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Remove duplicates and filter by confidence threshold"""
        seen = set()
        unique_relationships = []
        
        for rel in relationships:
            # Create key for deduplication
            key = (
                rel["subject"]["text"],
                rel["object"]["text"],
                rel["relationship_type"]
            )
            
            if key not in seen and rel["confidence"] >= confidence_threshold:
                seen.add(key)
                unique_relationships.append(rel)
                self.relationships_extracted += 1
        
        return unique_relationships

    def _create_service_mentions(self, relationships: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for extracted relationships (placeholder for service integration)"""
        # This would integrate with the service manager to create mentions
        # For now, just log the creation
        if relationships:
            self.logger.info(f"Created {len(relationships)} relationship mentions")

    def get_contract(self):
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "description": "Extract semantic relationships between entities using spaCy and pattern matching",
            "input_specification": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze for relationships"},
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "label": {"type": "string"},
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["text", "label", "start", "end"]
                        },
                        "minItems": 2
                    },
                    "chunk_ref": {"type": "string", "description": "Reference to source chunk"},
                    "confidence_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5}
                },
                "required": ["text", "entities"]
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "relationship_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "subject": {"type": "object"},
                                "object": {"type": "object"},
                                "confidence": {"type": "number"},
                                "extraction_method": {"type": "string"},
                                "evidence_text": {"type": "string"}
                            }
                        }
                    },
                    "relationship_count": {"type": "integer"},
                    "confidence": {"type": "number"}
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ],
            "supported_relationship_types": [
                "OWNS", "WORKS_FOR", "LOCATED_IN", "PARTNERS_WITH", 
                "CREATED", "LEADS", "MEMBER_OF", "RELATED_TO"
            ]
        }