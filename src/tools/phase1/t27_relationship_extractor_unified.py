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
from src.core.resource_manager import get_resource_manager
from src.orchestration.memory import AgentMemory
from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningType

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
    
    def __init__(self, service_manager: ServiceManager, memory_config: Dict[str, Any] = None, reasoning_config: Dict[str, Any] = None):
        super().__init__(service_manager)
        self.tool_id = "T27_RELATIONSHIP_EXTRACTOR"
        self.name = "Reasoning-Enhanced Relationship Extractor"
        self.category = "text_processing"
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
        # Use shared resource manager instead of loading individual model
        self.resource_manager = get_resource_manager()
        self._model_name = "en_core_web_sm"
        
        # Register this tool instance with resource manager
        self.resource_manager.register_tool_reference(self.tool_id, self)
        
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
        
        # Relationship extraction patterns (now adaptive)
        self.relationship_patterns = self._initialize_patterns()
        self.learned_patterns = {}
        self.adaptive_patterns = []
        
        # Processing stats
        self.relationships_extracted = 0
        self.patterns_matched = 0
        self.dependency_extractions = 0
        self.reasoning_guided_extractions = 0
        self.memory_guided_extractions = 0


    def _initialize_patterns(self) -> List[Dict[str, Any]]:
        """Initialize comprehensive relationship extraction patterns"""
        return [
            # OWNERSHIP patterns
            {
                "name": "ownership",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:owns?|owned|possesses?|possess|has|have|controls?|control)\s+([A-Z][^,.!?]*)",
                "relationship_type": "OWNS",
                "confidence": 0.9
            },
            {
                "name": "ownership_passive",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:is|are|was|were)\s+owned\s+by\s+([A-Z][^,.!?]*)",
                "relationship_type": "OWNED_BY",
                "confidence": 0.85
            },
            
            # EMPLOYMENT patterns (much more comprehensive)
            {
                "name": "employment_basic",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:works?\s+(?:at|for)|employed\s+(?:at|by)|joins?|joined)\s+([A-Z][^,.!?]*)",
                "relationship_type": "WORKS_FOR",
                "confidence": 0.85
            },
            {
                "name": "employment_titles",
                "pattern": r"([A-Z][^,.!?]*?),?\s+(?:CEO|CTO|CFO|president|director|manager|head|chief|founder|co-founder)\s+(?:of|at)\s+([A-Z][^,.!?]*)",
                "relationship_type": "WORKS_FOR",
                "confidence": 0.95
            },
            {
                "name": "employment_reverse",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:employs?|hires?|hired)\s+([A-Z][^,.!?]*)",
                "relationship_type": "EMPLOYS",
                "confidence": 0.8
            },
            
            # LOCATION patterns (expanded)
            {
                "name": "location_in",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:is|are|was|were)?\s*(?:located|based|situated|positioned)\s+(?:in|at|on)\s+([A-Z][^,.!?]*)",
                "relationship_type": "LOCATED_IN",
                "confidence": 0.8
            },
            {
                "name": "location_from",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:from|of)\s+([A-Z][^,.!?]*)",
                "relationship_type": "FROM",
                "confidence": 0.7
            },
            {
                "name": "location_headquarters",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:headquarters|offices?|facilities?)\s+(?:are|is)?\s*(?:in|at|located in)\s+([A-Z][^,.!?]*)",
                "relationship_type": "HEADQUARTERED_IN",
                "confidence": 0.85
            },
            
            # PARTNERSHIP/COLLABORATION patterns
            {
                "name": "partnership",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:partners?\s+with|collaborates?\s+with|works?\s+with|teams?\s+up\s+with|allies?\s+with)\s+([A-Z][^,.!?]*)",
                "relationship_type": "PARTNERS_WITH",
                "confidence": 0.75
            },
            {
                "name": "joint_venture",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:and|&)\s+([A-Z][^,.!?]*?)\s+(?:joint\s+venture|partnership|collaboration|alliance)",
                "relationship_type": "JOINT_VENTURE",
                "confidence": 0.8
            },
            
            # CREATION/FOUNDING patterns (expanded)
            {
                "name": "creation",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:created|founded|established|built|developed|started|launched|formed)\s+([A-Z][^,.!?]*)",
                "relationship_type": "CREATED",
                "confidence": 0.8
            },
            {
                "name": "creation_passive",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:was|were)\s+(?:created|founded|established|built|developed|started|launched|formed)\s+by\s+([A-Z][^,.!?]*)",
                "relationship_type": "CREATED_BY",
                "confidence": 0.85
            },
            
            # LEADERSHIP patterns (expanded)
            {
                "name": "leadership",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:leads?|manages?|heads?|directs?|oversees?|supervises?|runs?|operates?)\s+([A-Z][^,.!?]*)",
                "relationship_type": "LEADS",
                "confidence": 0.75
            },
            {
                "name": "leadership_passive",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:is|are|was|were)\s+(?:led|managed|headed|directed|overseen|supervised|run|operated)\s+by\s+([A-Z][^,.!?]*)",
                "relationship_type": "LED_BY",
                "confidence": 0.8
            },
            
            # MEMBERSHIP patterns (expanded) 
            {
                "name": "membership",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:is|are|was|were)?\s*(?:member\s+of|belongs\s+to|part\s+of|affiliated\s+with|associated\s+with)\s+([A-Z][^,.!?]*)",
                "relationship_type": "MEMBER_OF",
                "confidence": 0.7
            },
            {
                "name": "includes_contains",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:includes?|contains?|comprises?|consists?\s+of|has)\s+([A-Z][^,.!?]*)",
                "relationship_type": "INCLUDES",
                "confidence": 0.7
            },
            
            # FINANCIAL/BUSINESS patterns (new)
            {
                "name": "acquisition",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:acquired|bought|purchased|took\s+over)\s+([A-Z][^,.!?]*)",
                "relationship_type": "ACQUIRED",
                "confidence": 0.9
            },
            {
                "name": "investment",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:invested\s+in|funds?|finances?|backs?|backed)\s+([A-Z][^,.!?]*)",
                "relationship_type": "INVESTS_IN",
                "confidence": 0.8
            },
            {
                "name": "competition",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:competes?\s+with|rivals?|against)\s+([A-Z][^,.!?]*)",
                "relationship_type": "COMPETES_WITH",
                "confidence": 0.75
            },
            
            # FAMILY/PERSONAL patterns (new)
            {
                "name": "family_relations",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:is|are|was|were)?\s*(?:son|daughter|father|mother|brother|sister|spouse|wife|husband)\s+(?:of|to)\s+([A-Z][^,.!?]*)",
                "relationship_type": "FAMILY_RELATION",
                "confidence": 0.85
            },
            {
                "name": "education",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:studied|graduated|attended|studied\s+at)\s+([A-Z][^,.!?]*)",
                "relationship_type": "STUDIED_AT",
                "confidence": 0.8
            },
            
            # TEMPORAL patterns (new)
            {
                "name": "succession",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:succeeded|replaced|followed)\s+([A-Z][^,.!?]*)",
                "relationship_type": "SUCCEEDED",
                "confidence": 0.8
            },
            {
                "name": "preceded",
                "pattern": r"([A-Z][^,.!?]*?)\s+(?:preceded|was\s+before|came\s+before)\s+([A-Z][^,.!?]*)",
                "relationship_type": "PRECEDED",
                "confidence": 0.75
            },
            
            # SIMPLE PROXIMITY patterns (fallback - very broad)
            {
                "name": "general_connection",
                "pattern": r"([A-Z][A-Za-z\s]+?)\s+(?:and|with|to|of|for|by|in|at)\s+([A-Z][A-Za-z\s]+)",
                "relationship_type": "RELATED_TO",
                "confidence": 0.4
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
                    "spacy_available": True,  # Resource manager handles spaCy availability
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
            
            required_fields = ["text", "entity_type", "start", "end"]
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
        
        # Method 2: spaCy dependency parsing (via resource manager)
        with self.resource_manager.get_spacy_nlp(self._model_name) as nlp:
            if nlp:
                dependency_relationships = self._extract_dependency_relationships(
                    text, entities, chunk_ref, confidence_threshold, nlp
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
        """Extract relationships using regex patterns with enhanced debugging"""
        relationships = []
        debug_info = {
            "total_patterns_tested": 0,
            "patterns_with_matches": 0,
            "total_matches_found": 0,
            "entity_matches_attempted": 0,
            "successful_entity_matches": 0,
            "relationships_created": 0
        }
        
        self.logger.debug(f"Starting pattern extraction on text length: {len(text)}")
        self.logger.debug(f"Available entities: {[e.get('text', 'Unknown') for e in entities]}")
        
        for pattern_info in self.relationship_patterns:
            debug_info["total_patterns_tested"] += 1
            pattern = pattern_info["pattern"]
            rel_type = pattern_info["relationship_type"]
            base_confidence = pattern_info["confidence"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            pattern_matches = list(matches)  # Convert to list to get count
            
            if pattern_matches:
                debug_info["patterns_with_matches"] += 1
                debug_info["total_matches_found"] += len(pattern_matches)
                self.logger.debug(f"Pattern '{pattern_info['name']}' found {len(pattern_matches)} matches")
            
            for match in pattern_matches:
                if match.lastindex and match.lastindex >= 2:
                    subject_text = match.group(1).strip()
                    object_text = match.group(match.lastindex).strip()
                    
                    self.logger.debug(f"Pattern match: '{subject_text}' -> '{object_text}' (full: '{match.group(0)}')")
                    
                    # Find matching entities with enhanced debugging
                    debug_info["entity_matches_attempted"] += 2
                    subject_entity = self._find_matching_entity(subject_text, entities, debug=True)
                    object_entity = self._find_matching_entity(object_text, entities, debug=True)
                    
                    if subject_entity and object_entity:
                        debug_info["successful_entity_matches"] += 2
                        self.logger.debug(f"Found entity matches: {subject_entity.get('text')} and {object_entity.get('text')}")
                        
                        if subject_entity != object_entity:
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
                                        "entity_type": subject_entity["entity_type"],
                                        "start": subject_entity["start"],
                                        "end": subject_entity["end"]
                                    },
                                    "object": {
                                        "text": object_entity["text"],
                                        "entity_type": object_entity["entity_type"],
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
                                debug_info["relationships_created"] += 1
                                self.patterns_matched += 1
                                self.logger.info(f"Created relationship: {rel_type} between '{subject_entity['text']}' and '{object_entity['text']}'")
                            else:
                                self.logger.debug(f"Relationship confidence {confidence} below threshold {confidence_threshold}")
                        else:
                            self.logger.debug("Subject and object entities are the same, skipping")
                    else:
                        missing = []
                        if not subject_entity:
                            missing.append(f"subject '{subject_text}'")
                        if not object_entity:
                            missing.append(f"object '{object_text}'")
                        self.logger.debug(f"Could not find entity matches for: {', '.join(missing)}")
        
        self.logger.info(f"Pattern extraction complete: {debug_info}")
        return relationships

    def _extract_dependency_relationships(
        self, 
        text: str, 
        entities: List[Dict[str, Any]], 
        chunk_ref: str, 
        confidence_threshold: float,
        nlp
    ) -> List[Dict[str, Any]]:
        """Extract relationships using spaCy dependency parsing"""
        relationships = []
        
        try:
            doc = nlp(text)
            
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

    def _find_matching_entity(self, text: str, entities: List[Dict[str, Any]], debug: bool = False) -> Optional[Dict[str, Any]]:
        """Find entity that matches the given text with enhanced matching logic"""
        text_cleaned = self._clean_text_for_matching(text)
        
        if debug:
            self.logger.debug(f"Looking for entity match for: '{text}' (cleaned: '{text_cleaned}')")
        
        # Try different matching strategies in order of precision
        matching_strategies = [
            ("exact_match", self._exact_match),
            ("case_insensitive_match", self._case_insensitive_match),
            ("contains_match", self._contains_match),
            ("word_overlap_match", self._word_overlap_match),
            ("fuzzy_match", self._fuzzy_match)
        ]
        
        for strategy_name, strategy_func in matching_strategies:
            for entity in entities:
                if strategy_func(text_cleaned, entity):
                    if debug:
                        self.logger.debug(f"Entity match found using {strategy_name}: '{text}' -> '{entity.get('text', 'Unknown')}'")
                    return entity
        
        if debug:
            self.logger.debug(f"No entity match found for: '{text}'. Available entities: {[e.get('text', 'Unknown') for e in entities]}")
        
        return None
    
    def _clean_text_for_matching(self, text: str) -> str:
        """Clean text for better entity matching"""
        # Remove common prefixes and suffixes that might interfere with matching
        text = text.strip()
        # Remove trailing punctuation
        text = re.sub(r'[^\w\s]+$', '', text)
        # Remove leading articles
        text = re.sub(r'^(?:the|a|an)\s+', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def _exact_match(self, text: str, entity: Dict[str, Any]) -> bool:
        """Exact text match"""
        return text == entity.get("text", "").strip()
    
    def _case_insensitive_match(self, text: str, entity: Dict[str, Any]) -> bool:
        """Case insensitive match"""
        return text.lower() == entity.get("text", "").strip().lower()
    
    def _contains_match(self, text: str, entity: Dict[str, Any]) -> bool:
        """Check if text contains entity or vice versa"""
        text_lower = text.lower()
        entity_text = entity.get("text", "").strip().lower()
        return text_lower in entity_text or entity_text in text_lower
    
    def _word_overlap_match(self, text: str, entity: Dict[str, Any]) -> bool:
        """Check if there's significant word overlap"""
        text_words = set(text.lower().split())
        entity_words = set(entity.get("text", "").strip().lower().split())
        
        if not text_words or not entity_words:
            return False
        
        # Require at least 70% word overlap
        overlap = len(text_words.intersection(entity_words))
        return overlap / max(len(text_words), len(entity_words)) >= 0.7
    
    def _fuzzy_match(self, text: str, entity: Dict[str, Any]) -> bool:
        """Fuzzy matching for partial matches"""
        text_lower = text.lower()
        entity_text = entity.get("text", "").strip().lower()
        
        # Simple fuzzy matching - check if most words match
        text_words = text_lower.split()
        entity_words = entity_text.split()
        
        if len(text_words) == 1 and len(entity_words) == 1:
            # For single words, check if one starts with the other
            return text_words[0].startswith(entity_words[0]) or entity_words[0].startswith(text_words[0])
        
        return False

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
                                "entity_type": {"type": "string"},
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["text", "entity_type", "start", "end"]
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


# Backward compatibility alias
RelationshipExtractor = T27RelationshipExtractorUnified