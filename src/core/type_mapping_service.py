"""Type Mapping Service - Maps between different entity type systems

This service provides mappings between different entity type systems:
- spaCy entity types (ORG, GPE, PERSON, etc.) 
- Ontology concepts (Institution, SocialGroup, IndividualActor, etc.)
- Standardized schema types (ORGANIZATION, LOCATION, PERSON, etc.)

Addresses CLAUDE.md Task 2: Implement Type Mapping Layer
"""

from typing import Dict, List, Optional, Set
from src.ontology_library.ontology_service import OntologyService


class TypeMappingService:
    """Maps between different entity type systems"""
    
    def __init__(self):
        self.ontology = OntologyService()
        
        # Mapping from spaCy types to ontology concepts
        self.spacy_to_ontology = {
            'PERSON': 'IndividualActor',
            'ORG': 'Institution', 
            'GPE': 'SocialGroup',  # Geopolitical entities as social groups
            'PRODUCT': 'System',
            'EVENT': 'Event',
            'WORK_OF_ART': 'Message',
            'LAW': 'Norm',
            'LANGUAGE': 'Channel',
            'FACILITY': 'Institution',  # Buildings, airports as institutions
            'MONEY': 'System',  # Monetary values as systems
            'DATE': 'System',  # Temporal entities as systems
            'TIME': 'System'
        }
        
        # Mapping from spaCy types to standardized schema types
        self.spacy_to_schema = {
            'PERSON': 'PERSON',
            'ORG': 'ORGANIZATION',
            'GPE': 'LOCATION',
            'PRODUCT': 'PRODUCT',
            'EVENT': 'OTHER',
            'WORK_OF_ART': 'OTHER',
            'LAW': 'OTHER',
            'LANGUAGE': 'OTHER',
            'FACILITY': 'LOCATION',
            'MONEY': 'MONEY',
            'DATE': 'DATE',
            'TIME': 'DATE'
        }
        
        # Mapping from ontology concepts to schema types
        self.ontology_to_schema = {
            'IndividualActor': 'PERSON',
            'Institution': 'ORGANIZATION',
            'SocialGroup': 'LOCATION',
            'System': 'PRODUCT',
            'Event': 'OTHER',
            'Message': 'OTHER',
            'Norm': 'OTHER',
            'Channel': 'OTHER',
            'Belief': 'OTHER',
            'Attitude': 'OTHER',
            'Identity': 'OTHER',
            'Behavior': 'OTHER',
            'Intention': 'OTHER',
            'Network': 'OTHER',
            'Audience': 'OTHER',
            'Source': 'OTHER'
        }
        
        # Valid schema types
        self.valid_schema_types = {
            'PERSON', 'ORGANIZATION', 'LOCATION', 'PRODUCT', 'DATE', 'MONEY', 'OTHER'
        }
        
    def map_spacy_to_ontology(self, spacy_type: str) -> Optional[str]:
        """Map spaCy entity type to ontology concept"""
        ontology_type = self.spacy_to_ontology.get(spacy_type)
        if ontology_type and self.ontology.validate_entity_type(ontology_type):
            return ontology_type
        return None
        
    def map_spacy_to_schema(self, spacy_type: str) -> str:
        """Map spaCy entity type to standardized schema type"""
        return self.spacy_to_schema.get(spacy_type, 'OTHER')
        
    def map_ontology_to_schema(self, ontology_type: str) -> str:
        """Map ontology concept to standardized schema type"""
        return self.ontology_to_schema.get(ontology_type, 'OTHER')
        
    def validate_entity_type(self, entity_type: str, type_system: str = 'ontology') -> bool:
        """Validate entity type against specified type system"""
        if type_system == 'ontology':
            return self.ontology.validate_entity_type(entity_type)
        elif type_system == 'schema':
            return entity_type in self.valid_schema_types
        elif type_system == 'spacy':
            return entity_type in self.spacy_to_ontology
        return False
        
    def get_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get all type mappings for debugging/validation"""
        return {
            'spacy_to_ontology': self.spacy_to_ontology,
            'spacy_to_schema': self.spacy_to_schema,
            'ontology_to_schema': self.ontology_to_schema
        }
        
    def get_valid_types(self, type_system: str) -> Set[str]:
        """Get all valid types for a given type system"""
        if type_system == 'spacy':
            return set(self.spacy_to_ontology.keys())
        elif type_system == 'ontology':
            return set(self.ontology.registry.entities.keys())
        elif type_system == 'schema':
            return self.valid_schema_types
        return set()
        
    def convert_entity_types(self, entities: List[Dict], from_system: str, to_system: str) -> List[Dict]:
        """Convert entity types from one system to another"""
        converted_entities = []
        
        for entity in entities:
            entity_copy = entity.copy()
            current_type = entity.get('entity_type') or entity.get('type')
            
            if not current_type:
                continue
                
            # Convert type based on systems
            if from_system == 'spacy' and to_system == 'ontology':
                new_type = self.map_spacy_to_ontology(current_type)
            elif from_system == 'spacy' and to_system == 'schema':
                new_type = self.map_spacy_to_schema(current_type)
            elif from_system == 'ontology' and to_system == 'schema':
                new_type = self.map_ontology_to_schema(current_type)
            else:
                new_type = current_type
                
            if new_type:
                entity_copy['entity_type'] = new_type
                entity_copy['original_type'] = current_type
                converted_entities.append(entity_copy)
                
        return converted_entities
        
    def repair_entity_schema(self, entity: Dict) -> Dict:
        """Repair entity to match schema requirements"""
        repaired_entity = entity.copy()
        
        # Fix entity_type field
        current_type = entity.get('entity_type') or entity.get('type')
        if current_type:
            # If it's a spaCy type, convert to schema type
            if current_type in self.spacy_to_schema:
                repaired_entity['entity_type'] = self.spacy_to_schema[current_type]
            # If it's an ontology type, convert to schema type
            elif current_type in self.ontology_to_schema:
                repaired_entity['entity_type'] = self.ontology_to_schema[current_type]
            # If it's already a schema type, keep it
            elif current_type in self.valid_schema_types:
                repaired_entity['entity_type'] = current_type
            # Default to OTHER
            else:
                repaired_entity['entity_type'] = 'OTHER'
                
        # Add canonical_name if missing
        if 'canonical_name' not in repaired_entity:
            surface_form = entity.get('surface_form') or entity.get('text', '')
            repaired_entity['canonical_name'] = surface_form.strip().lower()
            
        return repaired_entity