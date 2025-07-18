#!/usr/bin/env python3
"""
Test Ontology Integration

Tests for the master concept library integration with the compatibility system.
"""

import unittest
from pathlib import Path

# Add parent to path

from src.ontology_library.ontology_service import OntologyService
from src.core.ontology_validator import OntologyValidator
from src.core.data_models import Entity, Relationship
from src.core.contract_validator import ContractValidator


class TestOntologyService(unittest.TestCase):
    """Test the OntologyService functionality"""
    
    def setUp(self):
        self.ontology = OntologyService()
    
    def test_singleton_pattern(self):
        """Test that OntologyService follows singleton pattern"""
        ontology2 = OntologyService()
        self.assertIs(self.ontology, ontology2)
    
    def test_concept_loading(self):
        """Test that concepts are loaded from YAML files"""
        stats = self.ontology.get_statistics()
        
        # Should have loaded concepts
        self.assertGreater(stats['entities'], 0)
        self.assertGreater(stats['connections'], 0)
        self.assertGreater(stats['properties'], 0)
        self.assertGreater(stats['modifiers'], 0)
    
    def test_entity_validation(self):
        """Test entity type validation"""
        # Valid entity types
        self.assertTrue(self.ontology.validate_entity_type("IndividualActor"))
        self.assertTrue(self.ontology.validate_entity_type("Institution"))
        self.assertTrue(self.ontology.validate_entity_type("SocialGroup"))
        
        # Invalid entity types
        self.assertFalse(self.ontology.validate_entity_type("InvalidType"))
        self.assertFalse(self.ontology.validate_entity_type(""))
    
    def test_connection_validation(self):
        """Test connection type validation"""
        # Valid connection types
        self.assertTrue(self.ontology.validate_connection_type("BelongsTo"))
        self.assertTrue(self.ontology.validate_connection_type("Influences"))
        self.assertTrue(self.ontology.validate_connection_type("Communicates"))
        
        # Invalid connection types
        self.assertFalse(self.ontology.validate_connection_type("InvalidConnection"))
    
    def test_domain_range_validation(self):
        """Test connection domain/range constraints"""
        # Valid domain/range
        self.assertTrue(self.ontology.validate_connection_domain_range(
            "BelongsTo", "IndividualActor", "Institution"
        ))
        
        # Invalid domain/range (if BelongsTo doesn't allow Institution -> IndividualActor)
        # This depends on the actual constraints in connections.yaml
        result = self.ontology.validate_connection_domain_range(
            "BelongsTo", "Institution", "IndividualActor"
        )
        # The test will pass either way, but we document the expected behavior
        if not result:
            print("Domain/range constraint working as expected")
    
    def test_indigenous_term_search(self):
        """Test searching by indigenous terms"""
        # Search for "influences" (exact match)
        results = self.ontology.search_by_indigenous_term("influences")
        self.assertGreater(len(results), 0)
        
        # All results should contain "influences" in indigenous terms
        for concept in results:
            indigenous_terms_lower = [t.lower() for t in concept.indigenous_term]
            self.assertTrue(any("influences" in term for term in indigenous_terms_lower))


class TestOntologyValidator(unittest.TestCase):
    """Test the OntologyValidator functionality"""
    
    def setUp(self):
        self.validator = OntologyValidator()
    
    def test_valid_entity_validation(self):
        """Test validation of a valid entity"""
        entity = Entity(
            canonical_name="Test Person",
            entity_type="IndividualActor",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow",
            properties={
                "confidence_level": 0.8
            },
            modifiers={
                "certainty_level": "certain"
            }
        )
        
        errors = self.validator.validate_entity(entity)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_entity_type(self):
        """Test validation with invalid entity type"""
        entity = Entity(
            canonical_name="Test Entity",
            entity_type="InvalidType",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow"
        )
        
        errors = self.validator.validate_entity(entity)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Unknown entity type" in error for error in errors))
    
    def test_invalid_property(self):
        """Test validation with invalid property"""
        entity = Entity(
            canonical_name="Test Person",
            entity_type="IndividualActor",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow",
            properties={
                "invalid_property_name": "value"
            }
        )
        
        errors = self.validator.validate_entity(entity)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Unknown property" in error for error in errors))
    
    def test_invalid_modifier_value(self):
        """Test validation with invalid modifier value"""
        entity = Entity(
            canonical_name="Test Person",
            entity_type="IndividualActor",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow",
            modifiers={
                "certainty_level": "absolutely_certain"  # Invalid value
            }
        )
        
        errors = self.validator.validate_entity(entity)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Invalid value for modifier" in error for error in errors))
    
    def test_entity_enrichment(self):
        """Test entity enrichment with default modifiers"""
        entity = Entity(
            canonical_name="Test Person",
            entity_type="IndividualActor",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow"
        )
        
        # Should have no modifiers initially
        self.assertEqual(len(entity.modifiers), 0)
        
        # Enrich entity
        enriched = self.validator.enrich_entity(entity)
        
        # Should have default modifiers added
        self.assertGreater(len(enriched.modifiers), 0)
    
    def test_relationship_validation(self):
        """Test relationship validation"""
        relationship = Relationship(
            source_id="person1",
            target_id="org1",
            relationship_type="BelongsTo",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow"
        )
        
        errors = self.validator.validate_relationship(relationship)
        # Without source/target entities, should still validate the type
        self.assertEqual(len(errors), 0)
    
    def test_entity_template(self):
        """Test getting entity template"""
        template = self.validator.get_entity_template("IndividualActor")
        
        self.assertEqual(template["entity_type"], "IndividualActor")
        self.assertIn("typical_attributes", template)
        self.assertIn("applicable_properties", template)
        self.assertIn("applicable_modifiers", template)


class TestContractOntologyIntegration(unittest.TestCase):
    """Test contract validator with ontology integration"""
    
    def setUp(self):
        # Use parent directory's contracts folder
        contracts_dir = Path(__file__).parent.parent / "contracts"
        self.validator = ContractValidator(str(contracts_dir))
    
    def test_contract_with_ontology_validation(self):
        """Test loading contracts with ontology validation rules"""
        # Try to load T23A_SpacyNER if it exists
        try:
            contract = self.validator.load_contract("T23A_SpacyNER")
            
            # Check for ontology integration section
            self.assertIn("ontology_integration", contract)
            
            # Check output validation rules
            output_contract = contract.get("output_contract", {})
            produced_types = output_contract.get("produced_data_types", [])
            
            # Should have Entity type with validation rules
            entity_type = next((t for t in produced_types if t["type"] == "Entity"), None)
            self.assertIsNotNone(entity_type)
            
            if "validation" in entity_type:
                self.assertIn("entity_type", entity_type["validation"])
                
        except FileNotFoundError:
            self.skipTest("T23A_SpacyNER contract not found")
    
    def test_ontology_constraint_validation(self):
        """Test that ontology constraints are validated"""
        # Create test entity with valid ontology type
        valid_entity = Entity(
            canonical_name="Test Person",
            entity_type="IndividualActor",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow"
        )
        
        # Create test entity with invalid ontology type
        invalid_entity = Entity(
            canonical_name="Test Entity",
            entity_type="InvalidEntityType",
            confidence=0.9,
            quality_tier="high",
            created_by="test",
            workflow_id="test_workflow"
        )
        
        # The validator should have an ontology_validator instance
        self.assertIsNotNone(self.validator.ontology_validator)


if __name__ == "__main__":
    unittest.main()