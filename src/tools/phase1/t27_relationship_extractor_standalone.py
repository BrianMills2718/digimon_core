"""
T27: Relationship Extractor - Standalone Version
Extract relationships between entities from text
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
import re

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T27RelationshipExtractorStandalone(BaseTool):
    """T27: Relationship Extractor - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T27_RELATIONSHIP_EXTRACTOR"
        
        # Relationship patterns
        self.relationship_patterns = {
            'WORKS_FOR': [
                r'{e1}.*?(?:works? for|employed by|employee of|staff at)\s+{e2}',
                r'{e1}.*?(?:CEO|CTO|CFO|president|director|manager) (?:of|at)\s+{e2}'
            ],
            'LOCATED_IN': [
                r'{e1}.*?(?:located in|based in|headquartered in|situated in)\s+{e2}',
                r'{e1}.*?(?:in|at|near)\s+{e2}'
            ],
            'OWNS': [
                r'{e1}.*?(?:owns?|possessed?|has|acquired?)\s+{e2}',
                r'{e2}.*?(?:owned by|belonging to|property of)\s+{e1}'
            ],
            'PARTNERS_WITH': [
                r'{e1}.*?(?:partners? with|collaborates? with|works? with)\s+{e2}',
                r'{e1}.*?(?:and|&)\s+{e2}.*?(?:partner|collaborate|work together)'
            ],
            'CREATED': [
                r'{e1}.*?(?:created?|founded?|established?|built?|developed?)\s+{e2}',
                r'{e2}.*?(?:created by|founded by|established by|built by)\s+{e1}'
            ],
            'LEADS': [
                r'{e1}.*?(?:leads?|manages?|heads?|directs?|runs?)\s+{e2}',
                r'{e2}.*?(?:led by|managed by|headed by|directed by)\s+{e1}'
            ],
            'MEMBER_OF': [
                r'{e1}.*?(?:member of|part of|belongs? to|affiliated with)\s+{e2}',
                r'{e2}.*?(?:includes?|comprises?|consists? of).*?{e1}'
            ]
        }
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Relationship Extractor",
            description="Extract relationships between entities from text",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract relationships from"
                    },
                    "entities": {
                        "type": "array",
                        "description": "List of entities to find relationships between",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"}
                            }
                        }
                    },
                    "chunk_ref": {
                        "type": "string",
                        "description": "Reference to source chunk"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence threshold (0-1)",
                        "default": 0.7
                    }
                },
                "required": ["text", "entities", "chunk_ref"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "relationship_id": {"type": "string"},
                                "source_entity_id": {"type": "string"},
                                "target_entity_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence_text": {"type": "string"}
                            }
                        }
                    },
                    "total_relationships": {"type": "integer"},
                    "relationship_types": {"type": "object"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 15.0,
                "max_memory_mb": 500
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES",
                "EXTRACTION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute relationship extraction"""
        self._start_execution()
        
        try:
            # Extract parameters
            text = request.input_data.get("text")
            entities = request.input_data.get("entities", [])
            chunk_ref = request.input_data.get("chunk_ref")
            confidence_threshold = request.input_data.get("confidence_threshold", 0.7)
            
            # Validate input
            if not text:
                return self._create_error_result(
                    "INVALID_INPUT",
                    "Text input is required"
                )
            
            if not entities or len(entities) < 2:
                return self._create_error_result(
                    "NO_ENTITIES",
                    "At least 2 entities are required to find relationships"
                )
            
            # Extract relationships
            relationships = []
            
            # Try pattern-based extraction
            pattern_relationships = self._extract_pattern_based(
                text, entities, chunk_ref, confidence_threshold
            )
            relationships.extend(pattern_relationships)
            
            # Try proximity-based extraction as fallback
            proximity_relationships = self._extract_proximity_based(
                text, entities, chunk_ref, confidence_threshold
            )
            relationships.extend(proximity_relationships)
            
            # Remove duplicates
            seen = set()
            unique_relationships = []
            for rel in relationships:
                key = (rel["source_entity_id"], rel["target_entity_id"], rel["relationship_type"])
                if key not in seen:
                    seen.add(key)
                    unique_relationships.append(rel)
            
            # Count relationship types
            relationship_types = {}
            for rel in unique_relationships:
                rtype = rel["relationship_type"]
                relationship_types[rtype] = relationship_types.get(rtype, 0) + 1
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="extract_relationships",
                inputs=[chunk_ref],
                parameters={
                    "entity_count": len(entities),
                    "confidence_threshold": confidence_threshold
                }
            )
            
            relationship_ids = [r["relationship_id"] for r in unique_relationships]
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=relationship_ids,
                success=True,
                metadata={"relationship_count": len(unique_relationships)}
            )
            
            return self._create_success_result(
                data={
                    "relationships": unique_relationships,
                    "total_relationships": len(unique_relationships),
                    "relationship_types": relationship_types
                },
                metadata={
                    "operation_id": operation_id,
                    "chunk_ref": chunk_ref,
                    "entity_count": len(entities),
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in relationship extraction: {e}", exc_info=True)
            return self._create_error_result(
                "EXTRACTION_FAILED",
                f"Relationship extraction failed: {str(e)}"
            )
    
    def _extract_pattern_based(self, text: str, entities: List[Dict], 
                               chunk_ref: str, confidence_threshold: float) -> List[Dict]:
        """Extract relationships using pattern matching"""
        relationships = []
        text_lower = text.lower()
        
        # Try each pair of entities
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Try each relationship pattern
                for rel_type, patterns in self.relationship_patterns.items():
                    for pattern in patterns:
                        # Create pattern with entity surface forms
                        e1_escaped = re.escape(entity1["surface_form"].lower())
                        e2_escaped = re.escape(entity2["surface_form"].lower())
                        
                        # Try both directions
                        pattern1 = pattern.replace("{e1}", e1_escaped).replace("{e2}", e2_escaped)
                        pattern2 = pattern.replace("{e1}", e2_escaped).replace("{e2}", e1_escaped)
                        
                        match1 = re.search(pattern1, text_lower, re.IGNORECASE)
                        match2 = re.search(pattern2, text_lower, re.IGNORECASE)
                        
                        if match1:
                            confidence = self._calculate_pattern_confidence(rel_type, match1.group())
                            if confidence >= confidence_threshold:
                                relationships.append({
                                    "relationship_id": f"rel_{chunk_ref}_{uuid.uuid4().hex[:8]}",
                                    "source_entity_id": entity1["entity_id"],
                                    "target_entity_id": entity2["entity_id"],
                                    "relationship_type": rel_type,
                                    "confidence": confidence,
                                    "evidence_text": text[match1.start():match1.end()],
                                    "extraction_method": "pattern",
                                    "created_at": datetime.now().isoformat()
                                })
                        
                        if match2:
                            confidence = self._calculate_pattern_confidence(rel_type, match2.group())
                            if confidence >= confidence_threshold:
                                relationships.append({
                                    "relationship_id": f"rel_{chunk_ref}_{uuid.uuid4().hex[:8]}",
                                    "source_entity_id": entity2["entity_id"],
                                    "target_entity_id": entity1["entity_id"],
                                    "relationship_type": rel_type,
                                    "confidence": confidence,
                                    "evidence_text": text[match2.start():match2.end()],
                                    "extraction_method": "pattern",
                                    "created_at": datetime.now().isoformat()
                                })
        
        return relationships
    
    def _extract_proximity_based(self, text: str, entities: List[Dict],
                                 chunk_ref: str, confidence_threshold: float) -> List[Dict]:
        """Extract relationships based on entity proximity"""
        relationships = []
        
        # Only use proximity for entities that are close together
        MAX_DISTANCE = 100  # characters
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Calculate distance between entities
                distance = min(
                    abs(entity1["start_pos"] - entity2["end_pos"]),
                    abs(entity2["start_pos"] - entity1["end_pos"])
                )
                
                if distance <= MAX_DISTANCE:
                    # Extract text between entities
                    start = min(entity1["end_pos"], entity2["end_pos"])
                    end = max(entity1["start_pos"], entity2["start_pos"])
                    between_text = text[start:end].lower()
                    
                    # Try to determine relationship type from context
                    rel_type = self._infer_relationship_type(between_text)
                    
                    # Low confidence for proximity-based
                    confidence = 0.5 * (1.0 - distance / MAX_DISTANCE)
                    
                    if confidence >= confidence_threshold and rel_type:
                        relationships.append({
                            "relationship_id": f"rel_{chunk_ref}_{uuid.uuid4().hex[:8]}",
                            "source_entity_id": entity1["entity_id"],
                            "target_entity_id": entity2["entity_id"],
                            "relationship_type": rel_type,
                            "confidence": confidence,
                            "evidence_text": text[start:end].strip(),
                            "extraction_method": "proximity",
                            "created_at": datetime.now().isoformat()
                        })
        
        return relationships
    
    def _infer_relationship_type(self, text: str) -> Optional[str]:
        """Infer relationship type from text between entities"""
        text = text.lower()
        
        # Simple keyword-based inference
        if any(word in text for word in ['work', 'employ', 'job', 'staff']):
            return 'WORKS_FOR'
        elif any(word in text for word in ['located', 'based', 'in', 'at']):
            return 'LOCATED_IN'
        elif any(word in text for word in ['own', 'possess', 'has', 'acquire']):
            return 'OWNS'
        elif any(word in text for word in ['partner', 'collaborate', 'together']):
            return 'PARTNERS_WITH'
        elif any(word in text for word in ['create', 'found', 'establish', 'build']):
            return 'CREATED'
        elif any(word in text for word in ['lead', 'manage', 'head', 'direct']):
            return 'LEADS'
        elif any(word in text for word in ['member', 'part', 'belong', 'include']):
            return 'MEMBER_OF'
        else:
            return 'RELATED_TO'  # Generic relationship
    
    def _calculate_pattern_confidence(self, rel_type: str, evidence: str) -> float:
        """Calculate confidence for a pattern match"""
        # Base confidence for pattern matching
        confidence = 0.8
        
        # Adjust based on relationship type reliability
        type_confidence = {
            'WORKS_FOR': 0.85,
            'LOCATED_IN': 0.9,
            'OWNS': 0.75,
            'PARTNERS_WITH': 0.8,
            'CREATED': 0.85,
            'LEADS': 0.85,
            'MEMBER_OF': 0.8,
            'RELATED_TO': 0.6
        }
        
        if rel_type in type_confidence:
            confidence *= type_confidence[rel_type]
        
        # Adjust based on evidence length
        if len(evidence) < 10:
            confidence *= 0.8
        elif len(evidence) > 100:
            confidence *= 0.9
        
        return min(1.0, confidence)


# Test function
def test_standalone_relationship_extractor():
    """Test the standalone relationship extractor"""
    extractor = T27RelationshipExtractorStandalone()
    print(f"✅ Relationship Extractor initialized: {extractor.tool_id}")
    
    # Test text and entities
    test_text = """
    Joe Biden is the President of the United States. He works in Washington D.C.
    The United States partners with the United Kingdom on trade agreements.
    Microsoft Corporation was founded by Bill Gates. The company is headquartered
    in Redmond, Washington.
    """
    
    test_entities = [
        {
            "entity_id": "e1",
            "surface_form": "Joe Biden",
            "entity_type": "PERSON",
            "start_pos": 5,
            "end_pos": 14
        },
        {
            "entity_id": "e2",
            "surface_form": "United States",
            "entity_type": "GPE",
            "start_pos": 35,
            "end_pos": 48
        },
        {
            "entity_id": "e3",
            "surface_form": "Washington D.C.",
            "entity_type": "GPE",
            "start_pos": 62,
            "end_pos": 76
        },
        {
            "entity_id": "e4",
            "surface_form": "United Kingdom",
            "entity_type": "GPE",
            "start_pos": 109,
            "end_pos": 123
        },
        {
            "entity_id": "e5",
            "surface_form": "Microsoft Corporation",
            "entity_type": "ORG",
            "start_pos": 146,
            "end_pos": 167
        },
        {
            "entity_id": "e6",
            "surface_form": "Bill Gates",
            "entity_type": "PERSON",
            "start_pos": 183,
            "end_pos": 193
        }
    ]
    
    request = ToolRequest(
        tool_id="T27",
        operation="extract",
        input_data={
            "text": test_text,
            "entities": test_entities,
            "chunk_ref": "test_chunk_001",
            "confidence_threshold": 0.5
        }
    )
    
    result = extractor.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"Found {data['total_relationships']} relationships")
        print(f"Relationship types: {data['relationship_types']}")
        
        for rel in data['relationships']:
            source = next(e for e in test_entities if e["entity_id"] == rel["source_entity_id"])
            target = next(e for e in test_entities if e["entity_id"] == rel["target_entity_id"])
            print(f"\n  {source['surface_form']} --[{rel['relationship_type']}]--> {target['surface_form']}")
            print(f"    Confidence: {rel['confidence']:.2f}")
            print(f"    Method: {rel['extraction_method']}")
    else:
        print(f"Error: {result.error_message}")
    
    return extractor


if __name__ == "__main__":
    test_standalone_relationship_extractor()