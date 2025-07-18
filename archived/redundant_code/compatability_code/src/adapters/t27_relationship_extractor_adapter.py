"""Adapter for T27 RelationshipExtractor tool with ontology validation."""

from typing import Dict, Any, List, Tuple
from ..adapters.base_adapter import BaseToolAdapter
from ..core.data_models import Relationship, QualityTier


class RelationshipExtractorAdapter(BaseToolAdapter):
    """Adapter for RelationshipExtractor tool with domain/range validation."""
    
    def __init__(self):
        super().__init__("T27_RelationshipExtractor", "tool")
    
    def _execute_tool_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute relationship extraction logic."""
        entities = input_data["entities"]
        chunks = input_data["chunks"]
        extraction_method = input_data.get("extraction_method", "dependency_parsing")
        min_confidence = input_data.get("min_confidence", 0.5)
        
        # Create entity lookup by text for quick access
        entity_lookup = {ent["text"]: ent for ent in entities}
        
        all_relationships = []
        relationship_index = 0
        
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            text = chunk["text"]
            
            # Extract relationships from chunk
            chunk_relationships = self._extract_relationships_from_chunk(
                text, chunk_id, entity_lookup, extraction_method
            )
            
            for rel in chunk_relationships:
                if rel["confidence"] >= min_confidence:
                    rel["relationship_id"] = f"rel_{relationship_index:04d}"
                    relationship_index += 1
                    all_relationships.append(rel)
        
        # Create summary
        rel_type_counts = {}
        for rel in all_relationships:
            rel_type = rel["relationship_type"]
            rel_type_counts[rel_type] = rel_type_counts.get(rel_type, 0) + 1
        
        return {
            "relationships": all_relationships,
            "summary": {
                "total_relationships": len(all_relationships),
                "relationship_types": rel_type_counts,
                "chunks_processed": len(chunks),
                "entities_linked": len(set(
                    [r["source_entity_id"] for r in all_relationships] +
                    [r["target_entity_id"] for r in all_relationships]
                )),
                "extraction_method": extraction_method
            }
        }
    
    def _extract_relationships_from_chunk(self, text: str, chunk_id: str, 
                                        entity_lookup: Dict[str, Dict], 
                                        method: str) -> List[Dict[str, Any]]:
        """Extract relationships from a text chunk."""
        relationships = []
        
        # Find entities mentioned in this chunk
        entities_in_chunk = []
        for entity_text, entity_data in entity_lookup.items():
            if entity_text in text:
                entities_in_chunk.append(entity_data)
        
        # Extract relationships between entities in the chunk
        for i, source_entity in enumerate(entities_in_chunk):
            for target_entity in entities_in_chunk[i+1:]:
                # Determine relationship based on patterns
                rel_type, confidence = self._determine_relationship(
                    text, source_entity, target_entity
                )
                
                if rel_type:
                    relationships.append({
                        "source_entity_id": source_entity["entity_id"],
                        "source_entity_text": source_entity["text"],
                        "source_entity_type": source_entity["type"],
                        "target_entity_id": target_entity["entity_id"],
                        "target_entity_text": target_entity["text"],
                        "target_entity_type": target_entity["type"],
                        "relationship_type": rel_type,
                        "confidence": confidence,
                        "source_chunk_id": chunk_id,
                        "extraction_method": method,
                        "evidence": self._extract_evidence(text, source_entity, target_entity)
                    })
        
        return relationships
    
    def _determine_relationship(self, text: str, source: Dict, target: Dict) -> Tuple[str, float]:
        """Determine relationship type between entities based on text patterns."""
        # Simple pattern-based extraction for demo
        source_text = source["text"]
        target_text = target["text"]
        
        # Define patterns for different relationship types
        patterns = [
            # BelongsTo patterns
            (f"{source_text}.*(?:belongs to|is part of|member of).*{target_text}", "BelongsTo", 0.9),
            (f"{source_text}.*(?:in|at|from).*{target_text}", "BelongsTo", 0.7),
            
            # Influences patterns
            (f"{source_text}.*(?:influences|affects|impacts).*{target_text}", "Influences", 0.9),
            (f"{source_text}.*(?:shapes|drives|determines).*{target_text}", "Influences", 0.8),
            
            # Communicates patterns
            (f"{source_text}.*(?:communicates with|talks to|contacts).*{target_text}", "Communicates", 0.9),
            (f"{source_text}.*(?:said to|told|informed).*{target_text}", "Communicates", 0.8),
            
            # Controls patterns
            (f"{source_text}.*(?:controls|manages|oversees).*{target_text}", "Controls", 0.9),
            (f"{source_text}.*(?:directs|governs|administers).*{target_text}", "Controls", 0.85),
            
            # Provides patterns
            (f"{source_text}.*(?:provides|supplies|offers).*{target_text}", "Provides", 0.9),
            (f"{source_text}.*(?:gives|delivers|furnishes).*{target_text}", "Provides", 0.85),
            
            # CollaboratesWith patterns
            (f"{source_text}.*(?:collaborates with|works with|partners with).*{target_text}", "CollaboratesWith", 0.9),
            (f"{source_text}.*(?:and|together with).*{target_text}.*(?:work|collaborate|partner)", "CollaboratesWith", 0.8),
        ]
        
        import re
        for pattern, rel_type, confidence in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return rel_type, confidence
        
        # Default relationship if entities co-occur
        if source_text in text and target_text in text:
            distance = abs(text.find(source_text) - text.find(target_text))
            if distance < 50:  # Close proximity
                return "Observes", 0.6
        
        return None, 0.0
    
    def _extract_evidence(self, text: str, source: Dict, target: Dict) -> str:
        """Extract evidence snippet for the relationship."""
        source_pos = text.find(source["text"])
        target_pos = text.find(target["text"])
        
        start = max(0, min(source_pos, target_pos) - 30)
        end = min(len(text), max(source_pos + len(source["text"]), 
                                target_pos + len(target["text"])) + 30)
        
        evidence = text[start:end].strip()
        if start > 0:
            evidence = "..." + evidence
        if end < len(text):
            evidence = evidence + "..."
        
        return evidence
    
    def _apply_ontology_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ontology validation to extracted relationships."""
        validated_relationships = []
        validation_summary = {
            "total_validated": 0,
            "domain_range_violations": 0,
            "type_corrections": 0,
            "validation_errors": []
        }
        
        for rel_dict in result["relationships"]:
            # Create Relationship object for validation
            relationship = Relationship(
                id=self._generate_id(),
                source_id=rel_dict["source_entity_id"],
                target_id=rel_dict["target_entity_id"],
                relationship_type=rel_dict["relationship_type"],
                name=rel_dict["relationship_type"],  # For BaseObject
                type=rel_dict["relationship_type"],  # For BaseObject
                confidence=rel_dict["confidence"],
                quality_tier=QualityTier.MEDIUM,
                created_by="T27_RelationshipExtractor",
                workflow_id="demo_workflow"
            )
            
            # Create mock entities for domain/range validation
            from ..core.data_models import Entity
            source_entity = Entity(
                id="temp_source",
                canonical_name=rel_dict["source_entity_text"],
                entity_type=rel_dict["source_entity_type"],
                name=rel_dict["source_entity_text"],
                type=rel_dict["source_entity_type"],
                source_id="temp",
                confidence=0.8,
                quality_tier=QualityTier.MEDIUM,
                created_by="temp",
                workflow_id="temp"
            )
            target_entity = Entity(
                id="temp_target",
                canonical_name=rel_dict["target_entity_text"],
                entity_type=rel_dict["target_entity_type"],
                name=rel_dict["target_entity_text"],
                type=rel_dict["target_entity_type"],
                source_id="temp",
                confidence=0.8,
                quality_tier=QualityTier.MEDIUM,
                created_by="temp",
                workflow_id="temp"
            )
            
            # Check domain/range constraints
            errors = self.ontology_validator.validate_relationship(
                relationship,
                source_entity=source_entity,
                target_entity=target_entity
            )
            is_valid = len(errors) == 0
            
            if is_valid:
                # Enrich with ontology information
                validated_dict = rel_dict.copy()
                validated_dict["ontology_validated"] = True
                validated_dict["relationship_concept"] = relationship.type
                
                # Add allowed domain/range info
                concept_info = self.ontology_validator.get_relationship_constraints(relationship.type)
                if concept_info:
                    validated_dict["allowed_domains"] = concept_info.get("domain", [])
                    validated_dict["allowed_ranges"] = concept_info.get("range", [])
                
                validated_relationships.append(validated_dict)
                validation_summary["total_validated"] += 1
            else:
                # Try to find valid relationship type for this domain/range
                valid_types = self.ontology_validator.get_valid_relationships(
                    rel_dict["source_entity_type"],
                    rel_dict["target_entity_type"]
                )
                
                if valid_types:
                    # Use the first valid type as correction
                    corrected_dict = rel_dict.copy()
                    corrected_dict["relationship_type"] = valid_types[0]
                    corrected_dict["ontology_validated"] = True
                    corrected_dict["type_corrected"] = True
                    corrected_dict["original_type"] = rel_dict["relationship_type"]
                    corrected_dict["confidence"] *= 0.8  # Reduce confidence for corrected
                    
                    validated_relationships.append(corrected_dict)
                    validation_summary["total_validated"] += 1
                    validation_summary["type_corrections"] += 1
                else:
                    # No valid relationship possible
                    validation_summary["domain_range_violations"] += 1
                    validation_summary["validation_errors"].append({
                        "source": f"{rel_dict['source_entity_text']} ({rel_dict['source_entity_type']})",
                        "target": f"{rel_dict['target_entity_text']} ({rel_dict['target_entity_type']})",
                        "invalid_type": rel_dict["relationship_type"],
                        "reason": "No valid relationship type for this domain/range combination"
                    })
        
        # Update result with validated relationships
        result["relationships"] = validated_relationships
        result["summary"]["total_relationships"] = len(validated_relationships)
        result["summary"]["ontology_validation"] = validation_summary
        
        return result