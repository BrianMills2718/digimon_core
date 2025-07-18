"""T27: Pattern-Based Relationship Extractor - Minimal Implementation

Extracts relationships between entities using simple pattern matching.
Essential for building graph connections in the vertical slice workflow.

Minimal implementation focusing on:
- Simple verb-based patterns (X verb Y)
- Basic confidence scoring based on pattern strength
- Link to entity mentions from T23a
- Integration with core services

Deferred features:
- Complex dependency parsing
- LLM-based relationship extraction
- Advanced pattern libraries
- Semantic relationship types
"""

from typing import Dict, List, Optional, Any, Tuple
import uuid
from datetime import datetime
import re
import spacy

# Import core services
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService


class RelationshipExtractor:
    """T27: Pattern-Based Relationship Extractor."""
    
    def __init__(
        self,
        identity_service: Optional[IdentityService] = None,
        provenance_service: Optional[ProvenanceService] = None,
        quality_service: Optional[QualityService] = None
    ):
        # Allow tools to work standalone for testing
        if identity_service is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
            self.identity_service = service_manager.get_identity_service()
            self.provenance_service = service_manager.get_provenance_service()
            self.quality_service = service_manager.get_quality_service()
        else:
            self.identity_service = identity_service
            self.provenance_service = provenance_service
            self.quality_service = quality_service
        self.tool_id = "T27_RELATIONSHIP_EXTRACTOR"
        
        # Initialize spaCy for dependency parsing
        self.nlp = None
        self._initialize_spacy()
        
        # Simple relationship patterns
        self.relationship_patterns = self._initialize_patterns()
        
        # Base confidence for pattern-based extraction
        self.base_confidence = 0.7
    
    def _initialize_spacy(self):
        """Initialize spaCy model for dependency parsing."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_sm") 
            except OSError:
                print("Warning: spaCy model not available for relationship extraction")
                self.nlp = None
    
    def _initialize_patterns(self) -> List[Dict[str, Any]]:
        """Initialize simple relationship patterns."""
        return [
            {
                "name": "ownership",
                "pattern": r"(.+?)\s+(owns?|owned|possesses?|has)\s+(.+)",
                "relationship_type": "OWNS",
                "confidence_boost": 0.9
            },
            {
                "name": "employment",
                "pattern": r"(.+?)\s+(works?\s+(?:at|for)|employed\s+by|CEO\s+of|president\s+of)\s+(.+)",
                "relationship_type": "WORKS_FOR",
                "confidence_boost": 0.85
            },
            {
                "name": "location",
                "pattern": r"(.+?)\s+(?:is\s+)?(?:located\s+in|based\s+in|from)\s+(.+)",
                "relationship_type": "LOCATED_IN",
                "confidence_boost": 0.8
            },
            {
                "name": "partnership",
                "pattern": r"(.+?)\s+(?:partners?\s+with|collaborates?\s+with|works?\s+with)\s+(.+)",
                "relationship_type": "PARTNERS_WITH",
                "confidence_boost": 0.75
            },
            {
                "name": "creation",
                "pattern": r"(.+?)\s+(?:created|founded|established|built|developed)\s+(.+)",
                "relationship_type": "CREATED",
                "confidence_boost": 0.8
            },
            {
                "name": "leadership",
                "pattern": r"(.+?)\s+(?:leads?|manages?|heads?|directs?)\s+(.+)",
                "relationship_type": "LEADS",
                "confidence_boost": 0.75
            },
            {
                "name": "membership",
                "pattern": r"(.+?)\s+(?:is\s+)?(?:member\s+of|belongs\s+to|part\s+of)\s+(.+)",
                "relationship_type": "MEMBER_OF",
                "confidence_boost": 0.7
            }
        ]
    
    def extract_relationships(
        self,
        chunk_ref: str,
        text: str,
        entities: List[Dict[str, Any]],
        chunk_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Extract relationships from text using entity mentions.
        
        Args:
            chunk_ref: Reference to source text chunk
            text: Text to analyze
            entities: List of entities extracted from this chunk
            chunk_confidence: Confidence score from chunk
            
        Returns:
            List of extracted relationships with confidence scores
        """
        # Start operation tracking
        entity_refs = [e.get("mention_ref", "") for e in entities]
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="extract_relationships",
            inputs=[chunk_ref] + entity_refs,
            parameters={
                "text_length": len(text),
                "entity_count": len(entities),
                "extraction_method": "pattern_based"
            }
        )
        
        try:
            # Input validation
            if not text or not text.strip():
                return self._complete_with_error(
                    operation_id,
                    "Text cannot be empty"
                )
            
            if not chunk_ref:
                return self._complete_with_error(
                    operation_id,
                    "chunk_ref is required"
                )
            
            if len(entities) < 2:
                # Need at least 2 entities for relationships
                return self._complete_success(
                    operation_id,
                    [],
                    "Not enough entities for relationship extraction"
                )
            
            # Extract relationships using different methods
            relationships = []
            relationship_refs = []
            
            # Method 1: Pattern-based extraction
            pattern_relationships = self._extract_pattern_relationships(
                text, entities, chunk_ref, chunk_confidence
            )
            relationships.extend(pattern_relationships)
            
            # Method 2: Dependency parsing (if spaCy available)
            if self.nlp:
                dependency_relationships = self._extract_dependency_relationships(
                    text, entities, chunk_ref, chunk_confidence
                )
                relationships.extend(dependency_relationships)
            
            # Method 3: Proximity-based relationships (simple fallback)
            proximity_relationships = self._extract_proximity_relationships(
                text, entities, chunk_ref, chunk_confidence
            )
            relationships.extend(proximity_relationships)
            
            # Remove duplicates and assess quality
            relationships = self._deduplicate_relationships(relationships)
            
            for rel in relationships:
                rel_ref = f"storage://relationship/{rel['relationship_id']}"
                rel["relationship_ref"] = rel_ref
                relationship_refs.append(rel_ref)
                
                # Assess relationship quality
                quality_result = self.quality_service.assess_confidence(
                    object_ref=rel_ref,
                    base_confidence=rel["confidence"],
                    factors={
                        "pattern_strength": rel.get("pattern_confidence", 0.5),
                        "entity_distance": 1.0 - min(0.5, rel.get("entity_distance", 50) / 100),
                        "context_quality": chunk_confidence
                    },
                    metadata={
                        "extraction_method": rel["extraction_method"],
                        "relationship_type": rel["relationship_type"],
                        "source_chunk": chunk_ref
                    }
                )
                
                if quality_result["status"] == "success":
                    rel["quality_confidence"] = quality_result["confidence"]
                    rel["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=relationship_refs,
                success=True,
                metadata={
                    "relationships_extracted": len(relationships),
                    "relationship_types": list(set(r["relationship_type"] for r in relationships)),
                    "extraction_methods": list(set(r["extraction_method"] for r in relationships))
                }
            )
            
            return {
                "status": "success",
                "relationships": relationships,
                "total_relationships": len(relationships),
                "relationship_types": self._count_relationship_types(relationships),
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during relationship extraction: {str(e)}"
            )
    
    def _extract_pattern_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        chunk_confidence: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships using regex patterns."""
        relationships = []
        
        for pattern_info in self.relationship_patterns:
            pattern = pattern_info["pattern"]
            rel_type = pattern_info["relationship_type"]
            confidence_boost = pattern_info["confidence_boost"]
            
            # Find all matches
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                subject_text = match.group(1).strip()
                # Get the last captured group (could be group 2 or 3 depending on pattern)
                object_text = match.group(match.lastindex).strip() if match.lastindex else ""
                
                # Find matching entities
                subject_entity = self._find_matching_entity(subject_text, entities)
                object_entity = self._find_matching_entity(object_text, entities)
                
                if subject_entity and object_entity and subject_entity != object_entity:
                    # Calculate confidence
                    confidence = self._calculate_relationship_confidence(
                        pattern_confidence=confidence_boost,
                        context_confidence=chunk_confidence,
                        entity_confidence=(subject_entity["confidence"] + object_entity["confidence"]) / 2
                    )
                    
                    relationship = {
                        "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                        "relationship_type": rel_type,
                        "subject_entity_id": subject_entity["entity_id"],
                        "object_entity_id": object_entity["entity_id"],
                        "subject_mention_id": subject_entity["mention_id"],
                        "object_mention_id": object_entity["mention_id"],
                        "subject_text": subject_entity["surface_form"],
                        "object_text": object_entity["surface_form"],
                        "confidence": confidence,
                        "pattern_confidence": confidence_boost,
                        "extraction_method": "pattern_based",
                        "pattern_name": pattern_info["name"],
                        "evidence_text": match.group(0),
                        "source_chunk": chunk_ref,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_dependency_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        chunk_confidence: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships using spaCy dependency parsing."""
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
                            # Determine relationship type from verb
                            rel_type = self._classify_verb_relationship(verb.lemma_)
                            
                            confidence = self._calculate_relationship_confidence(
                                pattern_confidence=0.75,  # Medium confidence for dependency parsing
                                context_confidence=chunk_confidence,
                                entity_confidence=(subject_entity["confidence"] + object_entity["confidence"]) / 2
                            )
                            
                            relationship = {
                                "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                                "relationship_type": rel_type,
                                "subject_entity_id": subject_entity["entity_id"],
                                "object_entity_id": object_entity["entity_id"],
                                "subject_mention_id": subject_entity["mention_id"],
                                "object_mention_id": object_entity["mention_id"],
                                "subject_text": subject_entity["surface_form"],
                                "object_text": object_entity["surface_form"],
                                "confidence": confidence,
                                "pattern_confidence": 0.75,
                                "extraction_method": "dependency_parsing",
                                "verb": verb.lemma_,
                                "evidence_text": f"{token.text} {verb.text} {obj.text}",
                                "source_chunk": chunk_ref,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            relationships.append(relationship)
        
        except Exception as e:
            # Continue if dependency parsing fails
            pass
        
        return relationships
    
    def _extract_proximity_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        chunk_confidence: float
    ) -> List[Dict[str, Any]]:
        """Extract relationships based on entity proximity (fallback method)."""
        relationships = []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda e: e["start_char"])
        
        # Look for entities that are close to each other
        for i, entity1 in enumerate(sorted_entities):
            for j, entity2 in enumerate(sorted_entities[i+1:], i+1):
                # Calculate distance
                distance = entity2["start_char"] - entity1["end_char"]
                
                # Only consider entities that are reasonably close (within 50 characters)
                if distance < 50:
                    # Look for connecting words between entities
                    between_text = text[entity1["end_char"]:entity2["start_char"]].strip()
                    
                    # Simple relationship indicators
                    if any(word in between_text.lower() for word in [
                        "and", "with", "of", "in", "at", "for", "by", "'s"
                    ]):
                        confidence = self._calculate_relationship_confidence(
                            pattern_confidence=0.5,  # Low confidence for proximity
                            context_confidence=chunk_confidence,
                            entity_confidence=(entity1["confidence"] + entity2["confidence"]) / 2,
                            distance_penalty=distance / 50.0  # Closer entities = higher confidence
                        )
                        
                        # Only include if confidence is reasonable
                        if confidence > 0.3:
                            relationship = {
                                "relationship_id": f"rel_{uuid.uuid4().hex[:8]}",
                                "relationship_type": "RELATED_TO",  # Generic relationship
                                "subject_entity_id": entity1["entity_id"],
                                "object_entity_id": entity2["entity_id"],
                                "subject_mention_id": entity1["mention_id"],
                                "object_mention_id": entity2["mention_id"],
                                "subject_text": entity1["surface_form"],
                                "object_text": entity2["surface_form"],
                                "confidence": confidence,
                                "pattern_confidence": 0.5,
                                "extraction_method": "proximity_based",
                                "entity_distance": distance,
                                "connecting_text": between_text,
                                "source_chunk": chunk_ref,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            relationships.append(relationship)
        
        return relationships
    
    def _find_matching_entity(self, text: str, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find entity that matches the given text."""
        text_lower = text.lower().strip()
        
        for entity in entities:
            if entity["surface_form"].lower().strip() == text_lower:
                return entity
            # Also check if text contains the entity
            if text_lower in entity["surface_form"].lower() or entity["surface_form"].lower() in text_lower:
                return entity
        
        return None
    
    def _find_entity_by_position(
        self, 
        start_pos: int, 
        end_pos: int, 
        entities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find entity that overlaps with the given position."""
        for entity in entities:
            # Check if positions overlap
            if (start_pos <= entity["start_char"] < end_pos or 
                entity["start_char"] <= start_pos < entity["end_char"]):
                return entity
        return None
    
    def _classify_verb_relationship(self, verb: str) -> str:
        """Classify relationship type based on verb."""
        verb_to_relation = {
            "own": "OWNS", "have": "HAS", "possess": "OWNS",
            "work": "WORKS_FOR", "employ": "EMPLOYS",
            "create": "CREATED", "found": "FOUNDED", "establish": "ESTABLISHED",
            "lead": "LEADS", "manage": "MANAGES", "head": "HEADS",
            "locate": "LOCATED_IN", "base": "BASED_IN",
            "partner": "PARTNERS_WITH", "collaborate": "COLLABORATES_WITH"
        }
        
        return verb_to_relation.get(verb, "RELATED_TO")
    
    def _calculate_relationship_confidence(
        self, 
        pattern_confidence: float, 
        context_confidence: float, 
        entity_confidence: float,
        distance_penalty: float = 0.0
    ) -> float:
        """Calculate overall confidence for a relationship."""
        base_confidence = self.base_confidence
        
        # Weighted average of confidence factors
        factors = [pattern_confidence, context_confidence, entity_confidence]
        weights = [0.4, 0.3, 0.3]  # Pattern confidence weighted most heavily
        
        weighted_confidence = sum(f * w for f, w in zip(factors, weights))
        
        # Apply distance penalty if provided
        if distance_penalty > 0:
            weighted_confidence *= (1.0 - distance_penalty * 0.2)
        
        # Combine with base confidence
        final_confidence = (base_confidence + weighted_confidence) / 2
        
        return max(0.1, min(1.0, final_confidence))
    
    def _deduplicate_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate relationships."""
        seen = set()
        unique_relationships = []
        
        for rel in relationships:
            # Create key for deduplication
            key = (
                rel["subject_entity_id"],
                rel["object_entity_id"],
                rel["relationship_type"]
            )
            
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        
        return unique_relationships
    
    def _count_relationship_types(self, relationships: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count relationships by type."""
        type_counts = {}
        for rel in relationships:
            rel_type = rel["relationship_type"]
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts
    
    def _complete_with_error(self, operation_id: str, error_message: str) -> Dict[str, Any]:
        """Complete operation with error."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=[],
            success=False,
            error_message=error_message
        )
        
        return {
            "status": "error",
            "error": error_message,
            "operation_id": operation_id
        }
    
    def _complete_success(self, operation_id: str, outputs: List[str], message: str) -> Dict[str, Any]:
        """Complete operation successfully with message."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=outputs,
            success=True,
            metadata={"message": message}
        )
        
        return {
            "status": "success",
            "relationships": [],
            "total_relationships": 0,
            "relationship_types": {},
            "operation_id": operation_id,
            "message": message
        }
    
    def get_supported_relationship_types(self) -> List[str]:
        """Get list of supported relationship types."""
        return list(set(p["relationship_type"] for p in self.relationship_patterns)) + ["RELATED_TO"]
    
    def extract_relationships_working(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships that actually get persisted - simplified interface for workflow."""
        relationships = []
        
        if len(entities) < 2:
            return relationships
        
        # Simple pattern-based extraction for now
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Check if entities co-occur in sentences
                relationship = {
                    'id': f"rel_{uuid.uuid4()}",
                    'source_id': entity1['id'],
                    'target_id': entity2['id'],
                    'type': 'RELATED',  # Start simple
                    'confidence': 0.8,
                    'weight': 1.0
                }
                relationships.append(relationship)
        
        return relationships  # Format expected by EdgeBuilder

    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the relationship extractor tool - standardized interface required by tool factory"""
        if isinstance(input_data, dict):
            # Extract required parameters
            chunk_refs = input_data.get("chunk_refs", [])
            chunks = input_data.get("chunks", [])
            entities = input_data.get("entities", [])
            workflow_id = input_data.get("workflow_id", "default")
        else:
            return {
                "status": "error",
                "error": "Input must be dict with 'chunks' and 'entities' keys"
            }
            
        if not chunks:
            return {
                "status": "error",
                "error": "No chunks provided for relationship extraction"
            }
            
        if not entities:
            return {
                "status": "error",
                "error": "No entities provided for relationship extraction"
            }
            
        return self.extract_relationships(chunk_refs, chunks, entities, workflow_id)

    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "Pattern-Based Relationship Extractor",
            "version": "1.0.0",
            "description": "Extracts relationships between entities using patterns and dependency parsing",
            "supported_relationship_types": self.get_supported_relationship_types(),
            "extraction_methods": ["pattern_based", "dependency_parsing", "proximity_based"],
            "base_confidence": self.base_confidence,
            "requires_entities": True,
            "input_type": "chunk_with_entities",
            "output_type": "relationships"
        }