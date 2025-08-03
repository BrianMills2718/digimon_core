"""
T27: Relationship Extractor - FIXED Version with Enhanced Patterns
Extracts relationships between entities using multiple pattern types
REAL IMPLEMENTATION - NO MOCKS
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import logging
from datetime import datetime

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T27RelationshipExtractorFixed(BaseTool):
    """T27: Relationship Extractor with improved patterns"""
    
    def __init__(self, service_manager=None):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T27_RELATIONSHIP_EXTRACTOR"
        
        # Initialize comprehensive relationship patterns
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize comprehensive relationship extraction patterns"""
        # Pattern-based relationships
        self.pattern_relationships = [
            # Professional/Career patterns
            {
                "pattern": r"({entity1})\s+(?:graduated from|attended|studied at|went to)\s+({entity2})",
                "type": "EDUCATED_AT",
                "confidence": 0.9
            },
            {
                "pattern": r"({entity1})\s+(?:served in|served with|was in|worked for|joined)\s+({entity2})",
                "type": "SERVED_IN",
                "confidence": 0.85
            },
            {
                "pattern": r"({entity1})\s+(?:is|was|became|served as)\s+(?:the\s+)?(?:president|ceo|director|head|leader|chairman)\s+(?:of|at)\s+({entity2})",
                "type": "LEADS",
                "confidence": 0.9
            },
            {
                "pattern": r"({entity1})\s+(?:works at|employed by|employee of)\s+({entity2})",
                "type": "WORKS_AT",
                "confidence": 0.85
            },
            
            # Location patterns
            {
                "pattern": r"({entity1})\s+(?:in|at|near|located in|situated in)\s+({entity2})",
                "type": "LOCATED_IN",
                "confidence": 0.8
            },
            {
                "pattern": r"({entity1})\s+(?:is|was)\s+(?:the\s+)?(?:capital|headquarters|center)\s+(?:of|for)\s+({entity2})",
                "type": "CAPITAL_OF",
                "confidence": 0.9
            },
            {
                "pattern": r"({entity1})\s+(?:from|born in|native of|hails from)\s+({entity2})",
                "type": "FROM",
                "confidence": 0.85
            },
            
            # Organizational patterns
            {
                "pattern": r"({entity1})\s+(?:founded|established|created|started)\s+({entity2})",
                "type": "FOUNDED",
                "confidence": 0.9
            },
            {
                "pattern": r"({entity1})\s+(?:owns|owned by|subsidiary of|part of|belongs to)\s+({entity2})",
                "type": "OWNED_BY",
                "confidence": 0.85
            },
            {
                "pattern": r"({entity1})\s+(?:and|&)\s+({entity2})",
                "type": "ASSOCIATED_WITH",
                "confidence": 0.6
            },
            
            # Family/Personal patterns
            {
                "pattern": r"({entity1})\s+(?:married|wed|spouse of|husband of|wife of)\s+({entity2})",
                "type": "MARRIED_TO",
                "confidence": 0.9
            },
            {
                "pattern": r"({entity1})\s+(?:son of|daughter of|child of|parent of|father of|mother of)\s+({entity2})",
                "type": "FAMILY",
                "confidence": 0.9
            }
        ]
        
        # Proximity-based relationships (when entities appear near each other)
        self.proximity_threshold = 50  # characters
        
        # Keywords that indicate relationships
        self.relationship_keywords = {
            "LEADS": ["leads", "headed", "directs", "manages", "oversees", "runs"],
            "MEMBER_OF": ["member", "part of", "belongs to", "affiliated with"],
            "LOCATED_IN": ["in", "at", "located", "based", "situated"],
            "WORKS_AT": ["works", "employed", "job", "position", "role"],
            "PARTNERED_WITH": ["partner", "collaborated", "worked with", "teamed"],
            "COMPETED_WITH": ["competed", "rival", "opponent", "versus", "against"],
            "ACQUIRED": ["acquired", "bought", "purchased", "took over"],
            "INVESTED_IN": ["invested", "funded", "backed", "financed"]
        }
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Relationship Extractor",
            description="Extract relationships between entities in text",
            category="extraction",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract relationships from"
                    },
                    "entities": {
                        "type": "array",
                        "description": "List of entities found in the text",
                        "items": {
                            "type": "object",
                            "properties": {
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"}
                            }
                        }
                    },
                    "chunk_ref": {
                        "type": "string",
                        "description": "Reference to the source chunk"
                    }
                },
                "required": ["text", "entities"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_entity": {"type": "string"},
                                "target_entity": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence": {"type": "string"},
                                "context": {"type": "string"}
                            }
                        }
                    },
                    "total_found": {"type": "integer"}
                }
            },
            dependencies=["provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 5.0,
                "max_memory_mb": 500
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES",
                "EXTRACTION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute relationship extraction with enhanced patterns"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result("INVALID_INPUT", "Input validation failed")
            
            text = request.input_data.get("text", "")
            entities = request.input_data.get("entities", [])
            chunk_ref = request.input_data.get("chunk_ref", "")
            
            if not entities:
                return self._create_error_result("NO_ENTITIES", "No entities provided")
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="extract_relationships",
                inputs=[chunk_ref] if chunk_ref else [],
                parameters={"entity_count": len(entities)}
            )
            
            # Extract relationships using multiple methods
            relationships = []
            
            # 1. Pattern-based extraction
            pattern_rels = self._extract_pattern_relationships(text, entities)
            relationships.extend(pattern_rels)
            
            # 2. Proximity-based extraction
            proximity_rels = self._extract_proximity_relationships(text, entities)
            relationships.extend(proximity_rels)
            
            # 3. Keyword-based extraction
            keyword_rels = self._extract_keyword_relationships(text, entities)
            relationships.extend(keyword_rels)
            
            # Remove duplicates
            unique_relationships = self._deduplicate_relationships(relationships)
            
            # Complete provenance tracking
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[f"rel_{i}" for i in range(len(unique_relationships))],
                success=True,
                metadata={
                    "total_found": len(unique_relationships),
                    "pattern_based": len(pattern_rels),
                    "proximity_based": len(proximity_rels),
                    "keyword_based": len(keyword_rels)
                }
            )
            
            # Return success result
            return self._create_success_result(
                data={
                    "relationships": unique_relationships,
                    "total_found": len(unique_relationships)
                },
                metadata={
                    "operation_id": operation_id,
                    "extraction_methods": ["pattern", "proximity", "keyword"],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return self._create_error_result("EXTRACTION_FAILED", str(e))
    
    def _extract_pattern_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships using regex patterns"""
        relationships = []
        
        # Create entity lookup by surface form
        entity_lookup = {e["surface_form"]: e for e in entities}
        
        for pattern_info in self.pattern_relationships:
            pattern_template = pattern_info["pattern"]
            rel_type = pattern_info["type"]
            base_confidence = pattern_info["confidence"]
            
            # Try all entity pairs
            for e1 in entities:
                for e2 in entities:
                    if e1 == e2:
                        continue
                    
                    # Create pattern with actual entity names
                    pattern = pattern_template.replace("{entity1}", re.escape(e1["surface_form"]))
                    pattern = pattern.replace("{entity2}", re.escape(e2["surface_form"]))
                    
                    # Search for pattern
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        # Extract context around match
                        start = max(0, match.start() - 30)
                        end = min(len(text), match.end() + 30)
                        context = text[start:end].strip()
                        
                        relationships.append({
                            "source_entity": e1["surface_form"],
                            "target_entity": e2["surface_form"],
                            "relationship_type": rel_type,
                            "confidence": base_confidence,
                            "evidence": match.group(0),
                            "context": context,
                            "method": "pattern"
                        })
        
        return relationships
    
    def _extract_proximity_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships based on entity proximity"""
        relationships = []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda e: e.get("start_pos", 0))
        
        # Check proximity between consecutive entities
        for i in range(len(sorted_entities) - 1):
            e1 = sorted_entities[i]
            e2 = sorted_entities[i + 1]
            
            # Calculate distance
            distance = e2.get("start_pos", 0) - e1.get("end_pos", 0)
            
            if 0 < distance <= self.proximity_threshold:
                # Extract text between entities
                start = e1.get("end_pos", 0)
                end = e2.get("start_pos", 0)
                between_text = text[start:end].strip()
                
                # Determine relationship type based on context
                rel_type = self._infer_relationship_type(between_text, e1, e2)
                
                # Calculate confidence based on distance
                confidence = max(0.4, 0.7 - (distance / self.proximity_threshold) * 0.3)
                
                relationships.append({
                    "source_entity": e1["surface_form"],
                    "target_entity": e2["surface_form"],
                    "relationship_type": rel_type,
                    "confidence": confidence,
                    "evidence": between_text,
                    "context": text[max(0, start-30):min(len(text), end+30)],
                    "method": "proximity"
                })
        
        return relationships
    
    def _extract_keyword_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships based on keyword indicators"""
        relationships = []
        
        for rel_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                # Find keyword occurrences
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    # Find entities near this keyword
                    keyword_pos = match.start()
                    nearby_entities = []
                    
                    for entity in entities:
                        entity_pos = entity.get("start_pos", 0)
                        distance = abs(entity_pos - keyword_pos)
                        
                        if distance <= 100:  # Within 100 characters
                            nearby_entities.append((entity, distance))
                    
                    # Sort by distance
                    nearby_entities.sort(key=lambda x: x[1])
                    
                    # Create relationships between closest entities
                    if len(nearby_entities) >= 2:
                        e1 = nearby_entities[0][0]
                        e2 = nearby_entities[1][0]
                        
                        # Extract context
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]
                        
                        relationships.append({
                            "source_entity": e1["surface_form"],
                            "target_entity": e2["surface_form"],
                            "relationship_type": rel_type,
                            "confidence": 0.6,
                            "evidence": keyword,
                            "context": context,
                            "method": "keyword"
                        })
        
        return relationships
    
    def _infer_relationship_type(self, text: str, e1: Dict, e2: Dict) -> str:
        """Infer relationship type based on text between entities"""
        text_lower = text.lower()
        
        # Check for specific patterns
        if any(word in text_lower for word in ["in", "at", "located"]):
            if e2.get("entity_type") in ["GPE", "LOC", "ORG"]:
                return "LOCATED_IN"
        
        if any(word in text_lower for word in ["and", "&", ","]):
            return "ASSOCIATED_WITH"
        
        if any(word in text_lower for word in ["of", "'s", "from"]):
            return "AFFILIATED_WITH"
        
        # Default based on entity types
        type1 = e1.get("entity_type", "")
        type2 = e2.get("entity_type", "")
        
        if type1 == "PERSON" and type2 == "ORG":
            return "WORKS_AT"
        elif type1 == "ORG" and type2 == "GPE":
            return "LOCATED_IN"
        elif type1 == "PERSON" and type2 == "GPE":
            return "FROM"
        
        return "RELATED_TO"
    
    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships, keeping highest confidence"""
        unique = {}
        
        for rel in relationships:
            # Create key from source, target, and type
            key = (rel["source_entity"], rel["target_entity"], rel["relationship_type"])
            
            # Keep relationship with highest confidence
            if key not in unique or rel["confidence"] > unique[key]["confidence"]:
                unique[key] = rel
        
        return list(unique.values())
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not isinstance(input_data, dict):
            return False
        
        if "text" not in input_data or "entities" not in input_data:
            return False
        
        if not isinstance(input_data["text"], str):
            return False
        
        if not isinstance(input_data["entities"], list):
            return False
        
        return True


# Test function
def test_relationship_extractor():
    """Test the fixed relationship extractor"""
    extractor = T27RelationshipExtractorFixed()
    
    # Test text with multiple relationship types
    test_text = """
    Carter graduated from the Naval Academy in Annapolis in 1946. 
    He served in the U.S. Navy before entering politics.
    The Naval Academy is one of the most prestigious military institutions.
    Annapolis is the capital of Maryland and home to the Naval Academy.
    Carter and his wife Rosalynn lived in Plains, Georgia.
    """
    
    # Test entities
    test_entities = [
        {"surface_form": "Carter", "entity_type": "PERSON", "start_pos": 5, "end_pos": 11},
        {"surface_form": "Naval Academy", "entity_type": "ORG", "start_pos": 30, "end_pos": 43},
        {"surface_form": "Annapolis", "entity_type": "GPE", "start_pos": 47, "end_pos": 56},
        {"surface_form": "U.S. Navy", "entity_type": "ORG", "start_pos": 85, "end_pos": 94},
        {"surface_form": "Maryland", "entity_type": "GPE", "start_pos": 214, "end_pos": 222},
        {"surface_form": "Rosalynn", "entity_type": "PERSON", "start_pos": 280, "end_pos": 288},
        {"surface_form": "Plains", "entity_type": "GPE", "start_pos": 298, "end_pos": 304},
        {"surface_form": "Georgia", "entity_type": "GPE", "start_pos": 306, "end_pos": 313}
    ]
    
    request = ToolRequest(
        tool_id="T27",
        operation="extract",
        input_data={
            "text": test_text,
            "entities": test_entities,
            "chunk_ref": "test_chunk"
        },
        parameters={}
    )
    
    result = extractor.execute(request)
    
    if result.status == "success":
        print(f"✅ Extracted {result.data['total_found']} relationships")
        for rel in result.data["relationships"]:
            print(f"   - {rel['source_entity']} → {rel['target_entity']} ({rel['relationship_type']}, conf: {rel['confidence']:.2f})")
            print(f"     Evidence: {rel['evidence']}")
            print(f"     Method: {rel['method']}")
    else:
        print(f"❌ Error: {result.error_message}")
    
    return result


if __name__ == "__main__":
    test_relationship_extractor()