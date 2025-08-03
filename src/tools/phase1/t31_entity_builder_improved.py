"""
T31: Entity Builder - Improved Version with Better Deduplication
Build graph entities with improved entity resolution and deduplication
REAL IMPLEMENTATION - NO MOCKS
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
from collections import defaultdict
import re
from difflib import SequenceMatcher

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T31EntityBuilderImproved(BaseTool):
    """T31: Entity Builder with improved deduplication"""
    
    def __init__(self, service_manager=None):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T31_ENTITY_BUILDER"
        # Get Neo4j driver from service manager
        self.neo4j_driver = self.service_manager.get_neo4j_driver()
        if not self.neo4j_driver:
            raise RuntimeError("Neo4j driver required for T31 Entity Builder")
        
        # Entity type priorities (higher priority types win in conflicts)
        self.type_priority = {
            "PERSON": 10,
            "ORG": 9,
            "GPE": 8,
            "LOC": 7,
            "PRODUCT": 6,
            "EVENT": 5,
            "WORK_OF_ART": 4,
            "LAW": 3,
            "LANGUAGE": 2,
            "DATE": 1,
            "TIME": 0
        }
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Entity Builder",
            description="Build graph entities with improved deduplication",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "description": "List of entity mentions to build from",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "source_refs": {
                        "type": "array",
                        "description": "Source references for provenance"
                    },
                    "merge_strategy": {
                        "type": "string",
                        "description": "Strategy for merging duplicate entities",
                        "enum": ["exact", "fuzzy", "type_aware", "aggressive"],
                        "default": "aggressive"
                    }
                },
                "required": ["entities"]
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
                                "canonical_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "mention_count": {"type": "integer"},
                                "confidence": {"type": "number"},
                                "properties": {"type": "object"}
                            }
                        }
                    },
                    "total_entities": {"type": "integer"},
                    "merged_count": {"type": "integer"},
                    "neo4j_stored": {"type": "integer"}
                }
            },
            dependencies=["neo4j", "identity_service", "provenance_service"],
            performance_requirements={
                "max_execution_time": 20.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES",
                "BUILD_FAILED",
                "NEO4J_ERROR"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity building with improved deduplication"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result("INVALID_INPUT", "Input validation failed")
            
            input_entities = request.input_data.get("entities", [])
            if not input_entities:
                return self._create_error_result("NO_ENTITIES", "No entities provided")
            
            source_refs = request.input_data.get("source_refs", [])
            merge_strategy = request.input_data.get("merge_strategy", "aggressive")
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="build_entities",
                inputs=source_refs,
                parameters={
                    "entity_count": len(input_entities),
                    "merge_strategy": merge_strategy
                }
            )
            
            # First, load existing entities from Neo4j for better matching
            existing_entities = self._load_existing_entities()
            
            # Group entities by canonical form with improved matching
            entity_groups = self._group_entities_improved(
                input_entities, existing_entities, merge_strategy
            )
            
            # Build and store entities in Neo4j
            built_entities = []
            neo4j_stored = 0
            merged_existing = 0
            
            with self.neo4j_driver.session() as session:
                for canonical_key, mentions in entity_groups.items():
                    # Check if this matches an existing entity
                    existing_match = self._find_existing_match(
                        canonical_key, mentions, existing_entities
                    )
                    
                    if existing_match:
                        # Update existing entity
                        entity = self._update_existing_entity(
                            session, existing_match, mentions
                        )
                        merged_existing += 1
                    else:
                        # Create new entity
                        entity = self._merge_mentions(canonical_key, mentions)
                        
                        # Store in Neo4j
                        if self._store_entity_in_neo4j(session, entity):
                            neo4j_stored += 1
                    
                    built_entities.append(entity)
            
            # Calculate merge statistics
            merged_count = len(input_entities) - len(built_entities) + merged_existing
            
            # Complete provenance tracking
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[e["entity_id"] for e in built_entities],
                success=True,
                metadata={
                    "total_entities": len(built_entities),
                    "merged_count": merged_count,
                    "neo4j_stored": neo4j_stored,
                    "existing_updated": merged_existing
                }
            )
            
            # Return success result
            return self._create_success_result(
                data={
                    "entities": built_entities,
                    "total_entities": len(built_entities),
                    "merged_count": merged_count,
                    "neo4j_stored": neo4j_stored
                },
                metadata={
                    "operation_id": operation_id,
                    "merge_strategy": merge_strategy,
                    "existing_updated": merged_existing,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Entity building failed: {e}")
            return self._create_error_result("BUILD_FAILED", str(e))
    
    def _load_existing_entities(self) -> Dict[str, Dict]:
        """Load existing entities from Neo4j for matching"""
        existing = {}
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (e:Entity)
                    WHERE e.canonical_name IS NOT NULL
                    RETURN e.entity_id as id, 
                           e.canonical_name as name,
                           e.entity_type as type,
                           e.surface_forms as forms,
                           e.mention_count as mentions
                    LIMIT 10000
                """)
                
                for record in result:
                    key = self._create_entity_key(
                        record["name"], 
                        record["type"]
                    )
                    existing[key] = {
                        "entity_id": record["id"],
                        "canonical_name": record["name"],
                        "entity_type": record["type"],
                        "surface_forms": record["forms"] or [],
                        "mention_count": record["mentions"] or 0
                    }
                    
        except Exception as e:
            logger.warning(f"Could not load existing entities: {e}")
            
        return existing
    
    def _group_entities_improved(self, entities: List[Dict], existing: Dict, 
                                 strategy: str) -> Dict[str, List[Dict]]:
        """Group entities with improved matching against existing entities"""
        groups = defaultdict(list)
        
        for entity in entities:
            surface_form = entity["surface_form"]
            entity_type = entity.get("entity_type", "UNKNOWN")
            
            # Try to find best match
            best_match_key = None
            best_match_score = 0.0
            
            if strategy == "aggressive":
                # Check against existing entities
                for existing_key, existing_entity in existing.items():
                    score = self._calculate_match_score(
                        surface_form, entity_type,
                        existing_entity["canonical_name"],
                        existing_entity["entity_type"],
                        existing_entity.get("surface_forms", [])
                    )
                    
                    if score > best_match_score and score >= 0.7:
                        best_match_key = existing_key
                        best_match_score = score
            
            # If no good match found, create new key
            if not best_match_key:
                if strategy == "exact":
                    key = surface_form.lower()
                elif strategy == "fuzzy":
                    key = self._normalize_text(surface_form)
                elif strategy in ["type_aware", "aggressive"]:
                    # Normalize and include type
                    normalized = self._normalize_text_aggressive(surface_form)
                    # For aggressive, also handle entity type conflicts
                    if strategy == "aggressive":
                        entity_type = self._resolve_entity_type(
                            surface_form, entity_type
                        )
                    key = f"{entity_type}:{normalized}"
                else:
                    key = surface_form
                
                best_match_key = key
            
            groups[best_match_key].append(entity)
        
        return groups
    
    def _calculate_match_score(self, surface: str, type1: str, 
                               canonical: str, type2: str, 
                               known_forms: List[str]) -> float:
        """Calculate match score between entities"""
        score = 0.0
        
        # Normalize for comparison
        surface_norm = self._normalize_text_aggressive(surface)
        canonical_norm = self._normalize_text_aggressive(canonical)
        
        # Direct match
        if surface_norm == canonical_norm:
            score = 0.9
        else:
            # Check similarity
            similarity = SequenceMatcher(None, surface_norm, canonical_norm).ratio()
            score = similarity * 0.7
        
        # Check against known surface forms
        for form in known_forms:
            form_norm = self._normalize_text_aggressive(form)
            if surface_norm == form_norm:
                score = max(score, 0.85)
                break
            elif SequenceMatcher(None, surface_norm, form_norm).ratio() > 0.8:
                score = max(score, 0.75)
        
        # Type compatibility bonus/penalty
        if type1 == type2:
            score *= 1.1
        elif self._are_types_compatible(type1, type2):
            score *= 1.0
        else:
            score *= 0.5
        
        return min(score, 1.0)
    
    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two entity types are compatible"""
        compatible_groups = [
            {"PERSON", "PER"},
            {"ORG", "ORGANIZATION", "COMPANY"},
            {"GPE", "LOC", "LOCATION", "PLACE"},
            {"DATE", "TIME", "DATETIME"},
            {"PRODUCT", "WORK_OF_ART"}
        ]
        
        for group in compatible_groups:
            if type1 in group and type2 in group:
                return True
        
        return False
    
    def _resolve_entity_type(self, surface_form: str, initial_type: str) -> str:
        """Resolve entity type conflicts based on context"""
        # Common patterns that indicate entity types
        person_patterns = [
            r'\b(Mr|Mrs|Ms|Dr|Prof|Sir|Lord|Lady)\b',
            r'\b(President|Senator|Governor|Mayor)\b'
        ]
        
        org_patterns = [
            r'\b(Academy|University|College|School|Institute)\b',
            r'\b(Company|Corporation|Inc|Ltd|LLC)\b',
            r'\b(Department|Agency|Bureau|Office)\b'
        ]
        
        gpe_patterns = [
            r'\b(City|Town|State|Country|Province)\b',
            r'(capital|headquarters)\s+of'
        ]
        
        # Check patterns
        for pattern in person_patterns:
            if re.search(pattern, surface_form, re.IGNORECASE):
                return "PERSON"
        
        for pattern in org_patterns:
            if re.search(pattern, surface_form, re.IGNORECASE):
                return "ORG"
        
        for pattern in gpe_patterns:
            if re.search(pattern, surface_form, re.IGNORECASE):
                return "GPE"
        
        # Return original type if no pattern matches
        return initial_type
    
    def _normalize_text(self, text: str) -> str:
        """Basic text normalization"""
        return text.lower().strip().replace(".", "").replace(",", "")
    
    def _normalize_text_aggressive(self, text: str) -> str:
        """Aggressive text normalization for better matching"""
        # Remove articles
        text = re.sub(r'\b(the|a|an)\b', '', text, flags=re.IGNORECASE)
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        # Lowercase
        return text.lower().strip()
    
    def _create_entity_key(self, name: str, entity_type: str) -> str:
        """Create a key for entity lookup"""
        normalized = self._normalize_text_aggressive(name)
        return f"{entity_type}:{normalized}"
    
    def _find_existing_match(self, canonical_key: str, mentions: List[Dict], 
                             existing: Dict) -> Optional[Dict]:
        """Find if this entity matches an existing one"""
        if canonical_key in existing:
            return existing[canonical_key]
        
        # Try fuzzy matching
        for existing_key, existing_entity in existing.items():
            for mention in mentions:
                score = self._calculate_match_score(
                    mention["surface_form"],
                    mention.get("entity_type", "UNKNOWN"),
                    existing_entity["canonical_name"],
                    existing_entity["entity_type"],
                    existing_entity.get("surface_forms", [])
                )
                
                if score >= 0.8:
                    return existing_entity
        
        return None
    
    def _update_existing_entity(self, session, existing: Dict, 
                                mentions: List[Dict]) -> Dict:
        """Update an existing entity with new mentions"""
        # Collect all surface forms
        new_forms = list(set(m["surface_form"] for m in mentions))
        all_forms = list(set(existing.get("surface_forms", []) + new_forms))
        
        # Update mention count
        new_count = existing.get("mention_count", 0) + len(mentions)
        
        # Update confidence (weighted average)
        old_confidence = existing.get("confidence", 0.5)
        old_weight = existing.get("mention_count", 1)
        new_confidence = sum(m.get("confidence", 0.5) for m in mentions) / len(mentions)
        new_weight = len(mentions)
        
        avg_confidence = (
            (old_confidence * old_weight + new_confidence * new_weight) /
            (old_weight + new_weight)
        )
        
        # Update in Neo4j
        result = session.run("""
            MATCH (e:Entity {entity_id: $entity_id})
            SET e.mention_count = $mention_count,
                e.confidence = $confidence,
                e.surface_forms = $surface_forms,
                e.updated_at = datetime()
            RETURN e.entity_id as entity_id,
                   e.canonical_name as canonical_name,
                   e.entity_type as entity_type
        """,
        entity_id=existing["entity_id"],
        mention_count=new_count,
        confidence=avg_confidence,
        surface_forms=all_forms)
        
        record = result.single()
        
        return {
            "entity_id": existing["entity_id"],
            "canonical_name": existing["canonical_name"],
            "entity_type": existing["entity_type"],
            "mention_count": new_count,
            "confidence": avg_confidence,
            "properties": {
                "surface_forms": all_forms,
                "updated_at": datetime.now().isoformat()
            }
        }
    
    def _merge_mentions(self, canonical_key: str, mentions: List[Dict]) -> Dict:
        """Merge multiple mentions into a canonical entity"""
        # Extract type from key if present
        if ":" in canonical_key:
            entity_type, canonical_name = canonical_key.split(":", 1)
        else:
            entity_type = "UNKNOWN"
            canonical_name = canonical_key
        
        # Use most common surface form as canonical name
        surface_forms = [m["surface_form"] for m in mentions]
        most_common = max(set(surface_forms), key=surface_forms.count)
        
        # If canonical_name is normalized, use the most common surface form
        if not canonical_name or canonical_name == self._normalize_text_aggressive(most_common):
            canonical_name = most_common
        
        # Aggregate confidence scores
        avg_confidence = sum(m.get("confidence", 0.5) for m in mentions) / len(mentions)
        
        # Resolve entity type conflicts
        entity_types = [m.get("entity_type", "UNKNOWN") for m in mentions]
        # Use highest priority type
        entity_type = max(
            set(entity_types),
            key=lambda t: self.type_priority.get(t, -1)
        )
        
        # Create canonical entity
        entity_id = f"entity_{uuid.uuid4().hex[:12]}"
        
        return {
            "entity_id": entity_id,
            "canonical_name": canonical_name,
            "entity_type": entity_type,
            "mention_count": len(mentions),
            "confidence": avg_confidence,
            "properties": {
                "surface_forms": list(set(surface_forms)),
                "first_seen": datetime.now().isoformat(),
                "source_count": len(set(m.get("source_ref", "") for m in mentions))
            }
        }
    
    def _store_entity_in_neo4j(self, session, entity: Dict) -> bool:
        """Store entity in Neo4j graph database"""
        try:
            # Create or update entity node
            query = """
            MERGE (e:Entity {entity_id: $entity_id})
            SET e.canonical_name = $canonical_name,
                e.entity_type = $entity_type,
                e.mention_count = $mention_count,
                e.confidence = $confidence,
                e.surface_forms = $surface_forms,
                e.first_seen = $first_seen,
                e.source_count = $source_count,
                e.updated_at = datetime()
            RETURN e.entity_id as entity_id
            """
            
            result = session.run(query,
                entity_id=entity["entity_id"],
                canonical_name=entity["canonical_name"],
                entity_type=entity["entity_type"],
                mention_count=entity["mention_count"],
                confidence=entity["confidence"],
                surface_forms=entity["properties"]["surface_forms"],
                first_seen=entity["properties"]["first_seen"],
                source_count=entity["properties"]["source_count"]
            )
            
            # Consume the result
            record = result.single()
            return record is not None
            
        except Exception as e:
            logger.error(f"Failed to store entity in Neo4j: {e}")
            return False
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not isinstance(input_data, dict):
            return False
        
        if "entities" not in input_data:
            return False
        
        entities = input_data["entities"]
        if not isinstance(entities, list):
            return False
        
        for entity in entities:
            if not isinstance(entity, dict):
                return False
            if "surface_form" not in entity:
                return False
        
        return True


# Test function
def test_entity_builder_improved():
    """Test the improved entity builder"""
    builder = T31EntityBuilderImproved()
    
    # Sample entities with duplicates and conflicts
    test_entities = [
        {
            "entity_id": "ent_1",
            "surface_form": "the Naval Academy",
            "entity_type": "ORG",
            "confidence": 0.95
        },
        {
            "entity_id": "ent_2",
            "surface_form": "Naval Academy",  # Missing "the"
            "entity_type": "ORG",
            "confidence": 0.90
        },
        {
            "entity_id": "ent_3",
            "surface_form": "The Naval Academy",  # Different capitalization
            "entity_type": "ORG",
            "confidence": 0.85
        },
        {
            "entity_id": "ent_4",
            "surface_form": "Annapolis",
            "entity_type": "GPE",  # Correct type
            "confidence": 0.90
        },
        {
            "entity_id": "ent_5",
            "surface_form": "Annapolis",
            "entity_type": "PERSON",  # Wrong type (should be merged)
            "confidence": 0.60
        }
    ]
    
    request = ToolRequest(
        tool_id="T31",
        operation="build_entities",
        input_data={
            "entities": test_entities,
            "source_refs": ["doc_123"],
            "merge_strategy": "aggressive"
        },
        parameters={}
    )
    
    result = builder.execute(request)
    
    if result.status == "success":
        print(f"✅ Built {result.data['total_entities']} entities")
        print(f"   Merged: {result.data['merged_count']}")
        print(f"   Stored in Neo4j: {result.data['neo4j_stored']}")
        for entity in result.data["entities"]:
            print(f"   - {entity['canonical_name']} ({entity['entity_type']}): {entity['mention_count']} mentions")
    else:
        print(f"❌ Error: {result.error_message}")
    
    return result


if __name__ == "__main__":
    test_entity_builder_improved()