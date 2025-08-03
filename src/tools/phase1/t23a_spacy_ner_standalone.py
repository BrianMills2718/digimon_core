"""
T23A: SpaCy Named Entity Recognition - Standalone Version
Extract named entities from text using SpaCy
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)

# Try to import spacy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available - NER will be limited")


class T23ASpacyNERStandalone(BaseTool):
    """T23A: SpaCy NER - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T23A_SPACY_NER"
        self.nlp = None
        self.supported_entity_types = {
            'PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT',
            'WORK_OF_ART', 'LAW', 'LANGUAGE', 'FACILITY',
            'MONEY', 'DATE', 'TIME', 'PERCENT', 'QUANTITY'
        }
        self._initialize_spacy()
    
    def _initialize_spacy(self):
        """Initialize spaCy model"""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not installed")
            return
        
        try:
            # Try to load the small English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully loaded spaCy model: en_core_web_sm")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}")
            logger.info("Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="SpaCy Named Entity Recognition",
            description="Extract named entities from text using SpaCy NLP",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract entities from"
                    },
                    "chunk_ref": {
                        "type": "string", 
                        "description": "Reference to source chunk"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence threshold (0-1)",
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
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"}
                            }
                        }
                    },
                    "total_entities": {"type": "integer"},
                    "entity_types": {"type": "object"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 10.0,
                "max_memory_mb": 500
            },
            error_conditions=[
                "EMPTY_TEXT",
                "SPACY_NOT_AVAILABLE",
                "EXTRACTION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction"""
        self._start_execution()
        
        try:
            # Extract parameters
            text = request.input_data.get("text")
            chunk_ref = request.input_data.get("chunk_ref")
            confidence_threshold = request.input_data.get("confidence_threshold", 0.8)
            
            # Validate input
            if not text or not text.strip():
                return self._create_error_result(
                    "EMPTY_TEXT",
                    "Text input cannot be empty"
                )
            
            # Check spaCy availability
            if not self.nlp:
                if SPACY_AVAILABLE:
                    # Try to initialize again
                    self._initialize_spacy()
                
                if not self.nlp:
                    # Fallback to simple regex-based extraction
                    logger.warning("Using fallback regex extraction")
                    entities = self._fallback_extraction(text, chunk_ref, confidence_threshold)
                else:
                    # Use spaCy
                    entities = self._spacy_extraction(text, chunk_ref, confidence_threshold)
            else:
                # Use spaCy
                entities = self._spacy_extraction(text, chunk_ref, confidence_threshold)
            
            # Count entity types
            entity_types = {}
            for entity in entities:
                etype = entity["entity_type"]
                entity_types[etype] = entity_types.get(etype, 0) + 1
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="extract_entities",
                inputs=[chunk_ref],
                parameters={
                    "confidence_threshold": confidence_threshold,
                    "extraction_method": "spacy" if self.nlp else "regex"
                }
            )
            
            entity_ids = [e["entity_id"] for e in entities]
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=entity_ids,
                success=True,
                metadata={"entity_count": len(entities)}
            )
            
            return self._create_success_result(
                data={
                    "entities": entities,
                    "total_entities": len(entities),
                    "entity_types": entity_types
                },
                metadata={
                    "operation_id": operation_id,
                    "chunk_ref": chunk_ref,
                    "extraction_method": "spacy" if self.nlp else "regex",
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in entity extraction: {e}", exc_info=True)
            return self._create_error_result(
                "EXTRACTION_FAILED",
                f"Entity extraction failed: {str(e)}"
            )
    
    def _spacy_extraction(self, text: str, chunk_ref: str, confidence_threshold: float) -> List[Dict]:
        """Extract entities using spaCy"""
        entities = []
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        for ent in doc.ents:
            # Filter by entity types
            if ent.label_ not in self.supported_entity_types:
                continue
            
            # Skip very short entities
            if len(ent.text.strip()) < 2:
                continue
            
            # Calculate confidence (spaCy doesn't provide confidence, so we estimate)
            confidence = self._estimate_confidence(ent.text, ent.label_)
            
            if confidence < confidence_threshold:
                continue
            
            entity = {
                "entity_id": f"entity_{chunk_ref}_{uuid.uuid4().hex[:8]}",
                "surface_form": ent.text,
                "entity_type": ent.label_,
                "confidence": confidence,
                "start_pos": ent.start_char,
                "end_pos": ent.end_char,
                "created_at": datetime.now().isoformat()
            }
            
            entities.append(entity)
        
        return entities
    
    def _fallback_extraction(self, text: str, chunk_ref: str, confidence_threshold: float) -> List[Dict]:
        """Fallback regex-based entity extraction"""
        import re
        entities = []
        
        # Simple patterns for common entity types
        patterns = {
            'PERSON': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # John Smith
                r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.? [A-Z][a-z]+\b',  # Mr. Smith
            ],
            'ORG': [
                r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation)\b',
                r'\b[A-Z][a-z]+ [A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd)\b',
            ],
            'GPE': [
                r'\b(?:United States|United Kingdom|China|Russia|India|Brazil)\b',
                r'\b[A-Z][a-z]+(?:ville|town|city|burg|shire)\b',
            ],
            'DATE': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b',
            ]
        }
        
        for entity_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                for match in re.finditer(pattern, text):
                    surface_form = match.group()
                    
                    # Skip if too short
                    if len(surface_form.strip()) < 2:
                        continue
                    
                    # Low confidence for regex extraction
                    confidence = 0.6
                    
                    if confidence < confidence_threshold:
                        continue
                    
                    entity = {
                        "entity_id": f"entity_{chunk_ref}_{uuid.uuid4().hex[:8]}",
                        "surface_form": surface_form,
                        "entity_type": entity_type,
                        "confidence": confidence,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    entities.append(entity)
        
        return entities
    
    def _estimate_confidence(self, text: str, entity_type: str) -> float:
        """Estimate confidence for an entity"""
        # Base confidence for spaCy
        confidence = 0.85
        
        # Adjust based on entity type reliability
        type_confidence = {
            'PERSON': 0.9,
            'ORG': 0.85,
            'GPE': 0.9,
            'DATE': 0.95,
            'TIME': 0.95,
            'MONEY': 0.95,
            'PERCENT': 0.95,
            'QUANTITY': 0.9
        }
        
        if entity_type in type_confidence:
            confidence *= type_confidence[entity_type]
        
        # Adjust based on text length
        if len(text) < 3:
            confidence *= 0.7
        elif len(text) > 50:
            confidence *= 0.8
        
        return min(1.0, confidence)


# Test function
def test_standalone_ner():
    """Test the standalone NER"""
    ner = T23ASpacyNERStandalone()
    print(f"✅ NER initialized: {ner.tool_id}")
    print(f"SpaCy available: {ner.nlp is not None}")
    
    # Test text
    test_text = """
    President Joe Biden met with Prime Minister Boris Johnson in Washington D.C. 
    on January 15, 2024. They discussed the $1.5 billion trade agreement between 
    the United States and the United Kingdom. Microsoft Corporation and Apple Inc. 
    were also mentioned as key partners in the technology sector.
    """
    
    request = ToolRequest(
        tool_id="T23A",
        operation="extract",
        input_data={
            "text": test_text,
            "chunk_ref": "test_chunk_001",
            "confidence_threshold": 0.5
        }
    )
    
    result = ner.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"Found {data['total_entities']} entities")
        print(f"Entity types: {data['entity_types']}")
        
        for entity in data['entities'][:5]:  # Show first 5
            print(f"\n  {entity['surface_form']} ({entity['entity_type']})")
            print(f"    Confidence: {entity['confidence']:.2f}")
            print(f"    Position: {entity['start_pos']}-{entity['end_pos']}")
    else:
        print(f"Error: {result.error_message}")
    
    return ner


if __name__ == "__main__":
    test_standalone_ner()