# contracts/validation/theory_validator.py
import os
import json
import importlib.util
from typing import Dict, List, Any, Tuple
from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema

class TheoryValidator:
    """Validates processing results against theory schemas"""
    
    def __init__(self, theory_config: TheoryConfig):
        self.theory_config = theory_config
        self.concept_library = self._load_concept_library()
        self.meta_schema = self._load_meta_schema()
    
    def _load_concept_library(self) -> Dict[str, Any]:
        """Load Master Concept Library from src/ontology_library/master_concepts.py"""
        try:
            # Import the master concepts module
            spec = importlib.util.spec_from_file_location(
                "master_concepts", 
                self.theory_config.concept_library_path
            )
            if spec and spec.loader:
                master_concepts_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(master_concepts_module)
                
                # Create a registry instance to access the concept definitions
                registry_class = getattr(master_concepts_module, 'MasterConceptRegistry', None)
                if registry_class:
                    return {"registry_class": registry_class, "module": master_concepts_module}
                else:
                    return {"module": master_concepts_module}
            return {}
        except Exception as e:
            print(f"Warning: Could not load concept library from {self.theory_config.concept_library_path}: {e}")
            return {}
    
    def _load_meta_schema(self) -> Dict[str, Any]:
        """Load Theory Meta-Schema if available"""
        if not self.theory_config.theory_meta_schema_path:
            # Try default location
            default_path = "docs/current/_schemas/theory_meta_schema_v9.json"
            if os.path.exists(default_path):
                self.theory_config.theory_meta_schema_path = default_path
            else:
                return {}
        
        try:
            with open(self.theory_config.theory_meta_schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load meta schema from {self.theory_config.theory_meta_schema_path}: {e}")
            return {}
    
    def validate_entities(self, entities: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """Validate entities against theory schema, return (score, details)"""
        if not entities:
            return 0.0, {"error": "No entities to validate"}
        
        validation_details: Dict[str, Any] = {
            "total_entities": len(entities),
            "validated_entities": 0,
            "concept_matches": 0,
            "entity_details": []
        }
        
        # Basic validation logic
        for entity in entities:
            entity_detail = {
                "name": entity.get("name", entity.get("surface_form", "Unknown")),
                "type": entity.get("entity_type", entity.get("type", "Unknown")),
                "has_concept_match": False,
                "concept_mapped_to": None
            }
            
            # Check if entity has required fields
            if entity.get("name") or entity.get("surface_form"):
                validation_details["validated_entities"] += 1
                
                # Basic concept matching (simplified)
                entity_type = entity.get("entity_type", entity.get("type", "")).upper()
                if entity_type in ["PERSON", "ORG", "GPE", "DATE", "MONEY", "PRODUCT"]:
                    validation_details["concept_matches"] += 1
                    entity_detail["has_concept_match"] = True
                    entity_detail["concept_mapped_to"] = f"Entity_{entity_type}"
            
            validation_details["entity_details"].append(entity_detail)
        
        # Calculate validation score
        if validation_details["total_entities"] > 0:
            score = validation_details["validated_entities"] / validation_details["total_entities"]
        else:
            score = 0.0
        
        return score, validation_details
    
    def validate_relationships(self, relationships: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """Validate relationships against theory schema, return (score, details)"""
        if not relationships:
            return 0.0, {"error": "No relationships to validate"}
        
        validation_details: Dict[str, Any] = {
            "total_relationships": len(relationships),
            "validated_relationships": 0,
            "type_matches": 0,
            "relationship_details": []
        }
        
        # Basic validation logic
        for rel in relationships:
            rel_detail = {
                "type": rel.get("type", "Unknown"),
                "source": rel.get("source", "Unknown"),
                "target": rel.get("target", "Unknown"),
                "has_valid_structure": False
            }
            
            # Check if relationship has required fields
            if rel.get("source") and rel.get("target") and rel.get("type"):
                validation_details["validated_relationships"] += 1
                rel_detail["has_valid_structure"] = True
                
                # Basic type validation
                rel_type = rel.get("type", "")
                if rel_type:
                    validation_details["type_matches"] += 1
            
            validation_details["relationship_details"].append(rel_detail)
        
        # Calculate validation score
        if validation_details["total_relationships"] > 0:
            score = validation_details["validated_relationships"] / validation_details["total_relationships"]
        else:
            score = 0.0
        
        return score, validation_details
    
    def map_to_concepts(self, entities: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map extracted entities to Master Concept Library concepts"""
        concept_mapping = {}
        
        for entity in entities:
            entity_name = entity.get("name", entity.get("surface_form", "Unknown"))
            entity_type = entity.get("entity_type", entity.get("type", "Unknown"))
            
            # Basic concept mapping logic
            if entity_type == "PERSON":
                concept_mapping[entity_name] = "Human_Agent"
            elif entity_type == "ORG":
                concept_mapping[entity_name] = "Organization"
            elif entity_type == "GPE":
                concept_mapping[entity_name] = "Geographic_Location"
            elif entity_type == "DATE":
                concept_mapping[entity_name] = "Temporal_Entity"
            elif entity_type == "MONEY":
                concept_mapping[entity_name] = "Economic_Value"
            elif entity_type == "PRODUCT":
                concept_mapping[entity_name] = "Artifact"
            else:
                concept_mapping[entity_name] = f"Generic_{entity_type}"
        
        return concept_mapping
    
    def validate_theory_compliance(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Overall theory compliance validation"""
        entity_score, entity_details = self.validate_entities(entities)
        rel_score, rel_details = self.validate_relationships(relationships)
        concept_mapping = self.map_to_concepts(entities)
        
        overall_score = (entity_score + rel_score) / 2
        
        return {
            "overall_score": overall_score,
            "entity_validation": entity_details,
            "relationship_validation": rel_details,
            "concept_mapping": concept_mapping,
            "theory_schema_used": self.theory_config.schema_type.value,
            "validation_timestamp": str(self._get_current_timestamp())
        }
    
    def _get_current_timestamp(self):
        """Get current timestamp for validation records"""
        from datetime import datetime
        return datetime.now().isoformat()