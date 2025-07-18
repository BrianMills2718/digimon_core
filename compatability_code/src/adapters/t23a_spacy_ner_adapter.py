"""Adapter for T23A SpacyNER tool with ontology validation."""

from typing import Dict, Any, List
from ..adapters.base_adapter import BaseToolAdapter
from ..core.data_models import Entity, QualityTier


class SpacyNERAdapter(BaseToolAdapter):
    """Adapter for SpacyNER tool that enforces contracts and ontology validation."""
    
    def __init__(self):
        super().__init__("T23A_SpacyNER", "tool")
        # Mock SpaCy model - in real implementation would load actual model
        self.nlp = None  # Would be: spacy.load("en_core_web_sm")
    
    def _execute_tool_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SpacyNER extraction logic."""
        chunks = input_data["chunks"]
        min_confidence = input_data.get("min_confidence", 0.5)
        entity_types = input_data.get("entity_types", [])
        
        all_entities = []
        entity_index = 0
        
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            text = chunk["text"]
            
            # Mock entity extraction - in real implementation would use SpaCy
            # For demo, extract some common patterns
            mock_entities = self._mock_extract_entities(text, chunk_id)
            
            for ent in mock_entities:
                if ent["confidence"] >= min_confidence:
                    if not entity_types or ent["type"] in entity_types:
                        ent["entity_id"] = f"entity_{entity_index:04d}"
                        entity_index += 1
                        all_entities.append(ent)
        
        # Create summary
        entity_type_counts = {}
        for ent in all_entities:
            ent_type = ent["type"]
            entity_type_counts[ent_type] = entity_type_counts.get(ent_type, 0) + 1
        
        return {
            "entities": all_entities,
            "summary": {
                "total_entities": len(all_entities),
                "entity_types": entity_type_counts,
                "chunks_processed": len(chunks),
                "extraction_method": "spacy_ner"
            }
        }
    
    def _mock_extract_entities(self, text: str, chunk_id: str) -> List[Dict[str, Any]]:
        """Mock entity extraction for demonstration."""
        entities = []
        
        # Simple pattern matching for demo
        import re
        
        # Find capitalized words (potential person/org names)
        cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        for match in re.finditer(cap_pattern, text):
            name = match.group()
            # Skip common words
            if name.lower() not in ['the', 'this', 'that', 'these', 'those']:
                # Determine type based on context or patterns
                if any(title in name for title in ['Dr.', 'Mr.', 'Ms.', 'Mrs.']):
                    ent_type = "IndividualActor"
                elif any(word in name for word in ['University', 'Institute', 'Corporation', 'Inc.']):
                    ent_type = "Institution"
                elif any(word in name for word in ['Street', 'Avenue', 'City', 'Park']):
                    ent_type = "Location"
                else:
                    ent_type = "Concept"  # Default for unknown
                
                entities.append({
                    "text": name,
                    "type": ent_type,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "confidence": 0.85,  # Mock confidence
                    "source_chunk_id": chunk_id,
                    "extraction_method": "pattern_matching"
                })
        
        # Find dates/events
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2}, \d{4})\b'
        for match in re.finditer(date_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "Event",
                "start_pos": match.start(),
                "end_pos": match.end(),
                "confidence": 0.9,
                "source_chunk_id": chunk_id,
                "extraction_method": "pattern_matching"
            })
        
        return entities
    
    def _apply_ontology_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ontology validation to extracted entities."""
        validated_entities = []
        validation_summary = {
            "total_validated": 0,
            "validation_errors": [],
            "type_corrections": 0,
            "enriched_count": 0
        }
        
        for entity_dict in result["entities"]:
            # Create Entity object for validation
            entity = Entity(
                id=self._generate_id(),
                canonical_name=entity_dict["text"],
                entity_type=entity_dict["type"],
                name=entity_dict["text"],  # For BaseObject
                type=entity_dict["type"],  # For BaseObject
                source_id=entity_dict["source_chunk_id"],
                confidence=entity_dict["confidence"],
                quality_tier=QualityTier.MEDIUM,
                created_by="T23A_SpacyNER",
                workflow_id="demo_workflow"
            )
            
            # Validate and enrich
            errors = self.ontology_validator.validate_entity(entity)
            is_valid = len(errors) == 0
            
            if is_valid:
                # Enrich with ontology defaults
                enriched_entity = self.ontology_validator.enrich_entity(entity)
                
                # Convert back to dict format with ontology metadata
                validated_dict = entity_dict.copy()
                validated_dict["ontology_validated"] = True
                validated_dict["entity_concept"] = entity.entity_type
                
                if enriched_entity.properties:
                    validated_dict["properties"] = enriched_entity.properties
                    validation_summary["enriched_count"] += 1
                
                if enriched_entity.modifiers:
                    validated_dict["modifiers"] = enriched_entity.modifiers
                
                validated_entities.append(validated_dict)
                validation_summary["total_validated"] += 1
            else:
                # Try to correct the type
                suggested_type = self.ontology_validator.suggest_entity_type(entity_dict["text"])
                if suggested_type and suggested_type != entity.entity_type:
                    entity.entity_type = suggested_type
                    errors = self.ontology_validator.validate_entity(entity)
                    is_valid = len(errors) == 0
                    if is_valid:
                        validated_dict = entity_dict.copy()
                        validated_dict["type"] = suggested_type
                        validated_dict["ontology_validated"] = True
                        validated_dict["type_corrected"] = True
                        validated_dict["original_type"] = entity_dict["type"]
                        validated_entities.append(validated_dict)
                        validation_summary["total_validated"] += 1
                        validation_summary["type_corrections"] += 1
                    else:
                        # Still invalid, skip this entity
                        validation_summary["validation_errors"].append({
                            "entity": entity_dict["text"],
                            "errors": errors
                        })
                else:
                    validation_summary["validation_errors"].append({
                        "entity": entity_dict["text"],
                        "errors": errors
                    })
        
        # Update result with validated entities
        result["entities"] = validated_entities
        result["summary"]["total_entities"] = len(validated_entities)
        result["summary"]["ontology_validation"] = validation_summary
        
        return result