"""
Unit tests for T23A spaCy NER with unified interface.

Tests follow TDD principles with REAL functionality testing.
🚫 NO MOCKS POLICY - Tests use actual service implementations.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.tools.base_tool import ToolRequest, ToolResult, ToolContract
from src.core.service_manager import ServiceManager


class TestT23ASpacyNERUnified:
    """Test suite for T23A spaCy NER with unified interface"""
    
    def setup_method(self):
        """Set up test fixtures with REAL services"""
        # Use REAL ServiceManager with test configuration
        self.service_manager = ServiceManager()
        
        # Import and initialize tool with REAL services
        try:
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            self.tool = T23ASpacyNERUnified(self.service_manager)
        except ImportError:
            pytest.skip("T23A spaCy NER Unified not implemented yet")
    
    def test_tool_initialization(self):
        """Tool initializes with correct tool ID and REAL services"""
        assert self.tool.tool_id == "T23A"
        assert self.tool.identity_service is not None
        assert self.tool.provenance_service is not None  
        assert self.tool.quality_service is not None
        
        # Verify services are REAL implementations, not mocks
        assert hasattr(self.tool.identity_service, 'create_mention')
        assert hasattr(self.tool.provenance_service, 'start_operation')
        assert hasattr(self.tool.quality_service, 'assess_confidence')
    
    def test_get_contract(self):
        """Tool returns proper contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T23A"
        assert contract.name == "spaCy Named Entity Recognition"
        assert contract.description == "Extract named entities from text using spaCy pre-trained models"
        assert contract.category == "entity_extraction"
        
        # Verify input schema
        assert "text" in contract.input_schema["properties"]
        assert "chunk_ref" in contract.input_schema["properties"]
        assert "text" in contract.input_schema["required"]
        assert "chunk_ref" in contract.input_schema["required"]
        
        # Verify output schema
        assert "entities" in contract.output_schema["properties"]
        assert "total_entities" in contract.output_schema["properties"]
        assert "entity_types" in contract.output_schema["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
    
    def test_input_validation_real(self):
        """Tool validates input using REAL contract validation"""
        # Valid input
        valid_input = {
            "text": "Apple Inc. was founded by Steve Jobs in Cupertino.",
            "chunk_ref": "storage://chunk/chunk123"
        }
        assert self.tool.validate_input(valid_input) == True
        
        # Missing required field - REAL validation
        invalid_input = {
            "chunk_ref": "storage://chunk/chunk123"
        }
        assert self.tool.validate_input(invalid_input) == False
        
        # Empty text - REAL validation
        empty_text = {
            "text": "",
            "chunk_ref": "storage://chunk/chunk123"
        }
        assert self.tool.validate_input(empty_text) == False
    
    def test_spacy_entity_extraction_real(self):
        """Test REAL spaCy entity extraction with actual NLP model"""
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": "Microsoft was founded by Bill Gates in Seattle, Washington.",
                "chunk_ref": "storage://chunk/test123"
            },
            parameters={"confidence_threshold": 0.5}  # Lower threshold for real functionality
        )
        
        # Execute with REAL spaCy model and REAL services
        result = self.tool.execute(request)
        
        # Verify REAL spaCy extraction results
        assert result.status == "success"
        assert result.data["total_entities"] >= 3  # Microsoft, Bill Gates, Seattle
        
        entities = result.data["entities"]
        entity_names = [e["surface_form"] for e in entities]
        
        # Verify actual entities were found by REAL spaCy
        assert any("Microsoft" in name for name in entity_names)
        assert any("Bill Gates" in name for name in entity_names)
        assert any("Seattle" in name for name in entity_names)
        
        # Verify entity types from REAL spaCy
        entity_types = [e["entity_type"] for e in entities]
        assert "ORG" in entity_types  # Microsoft
        assert "PERSON" in entity_types  # Bill Gates
        assert "GPE" in entity_types  # Seattle
        
        # Verify REAL service integration
        for entity in entities:
            assert "entity_id" in entity  # From REAL Identity service
            assert "mention_id" in entity  # From REAL Identity service
            assert "confidence" in entity  # From REAL Quality service
            assert 0.0 <= entity["confidence"] <= 1.0
    
    def test_complex_entity_extraction_real(self):
        """Test REAL extraction with complex text containing multiple entity types"""
        complex_text = """
        Dr. Jane Smith from Stanford University published research on machine learning
        at the NIPS 2023 conference in Vancouver, Canada. The paper was funded by
        the National Science Foundation grant #1234567 for $500,000.
        """
        
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": complex_text,
                "chunk_ref": "storage://chunk/complex123"
            },
            parameters={"confidence_threshold": 0.5}  # Lower threshold for real functionality
        )
        
        # Execute with REAL spaCy processing
        result = self.tool.execute(request)
        
        assert result.status == "success"
        entities = result.data["entities"]
        entity_names = [e["surface_form"] for e in entities]
        entity_types = result.data["entity_types"]
        
        # Verify REAL spaCy found various entity types
        assert len(entities) >= 6  # Multiple entities expected
        
        # Check for expected entities (may vary by spaCy model)
        # These are real assertions based on actual spaCy behavior
        person_found = any("Jane Smith" in name or "Dr. Jane Smith" in name for name in entity_names)
        org_found = any("Stanford" in name for name in entity_names)
        location_found = any("Vancouver" in name or "Canada" in name for name in entity_names)
        money_found = any("500,000" in name or "$500,000" in name for name in entity_names)
        
        # At least some of these should be found by REAL spaCy
        found_count = sum([person_found, org_found, location_found, money_found])
        assert found_count >= 2, f"Expected at least 2 entity types, found: {entity_types}"
    
    def test_supported_entity_types_real(self):
        """Test REAL supported entity types"""
        supported_types = self.tool.get_supported_entity_types()
        
        # Verify REAL spaCy entity types
        assert isinstance(supported_types, list)
        assert len(supported_types) > 0
        
        # Check for common spaCy entity types
        expected_types = ["PERSON", "ORG", "GPE", "MONEY", "DATE"]
        found_types = set(supported_types)
        
        for expected_type in expected_types:
            assert expected_type in found_types, f"Expected entity type {expected_type} not found in {supported_types}"
    
    def test_unicode_text_handling_real(self):
        """Test REAL handling of unicode text"""
        unicode_text = "李明在北京大学工作，与José García合作研究。"
        
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": unicode_text,
                "chunk_ref": "storage://chunk/unicode123"
            },
            parameters={}
        )
        
        # Execute with REAL unicode processing
        result = self.tool.execute(request)
        
        assert result.status == "success"
        # Verify tool handles unicode without crashing
        entities = result.data["entities"]
        
        # spaCy may or may not extract non-English entities depending on model
        # But it should not crash and should return valid structure
        assert isinstance(entities, list)
        assert isinstance(result.data["total_entities"], int)
    
    def test_confidence_threshold_real(self):
        """Test REAL confidence threshold filtering"""
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": "Apple Inc. and some ambiguous entity met yesterday.",
                "chunk_ref": "storage://chunk/threshold123"
            },
            parameters={
                "confidence_threshold": 0.9  # High threshold
            }
        )
        
        # Execute with REAL confidence filtering
        result = self.tool.execute(request)
        
        assert result.status == "success"
        entities = result.data["entities"]
        
        # All returned entities should meet the REAL confidence threshold
        for entity in entities:
            assert entity["confidence"] >= 0.9, f"Entity {entity['surface_form']} has confidence {entity['confidence']} below threshold"
    
    def test_empty_text_error_real(self):
        """Test REAL error handling for empty text"""
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": "",
                "chunk_ref": "storage://chunk/empty123"
            },
            parameters={}
        )
        
        # Execute with REAL error handling
        result = self.tool.execute(request)
        
        # Verify REAL error response
        assert result.status == "error"
        assert result.error_code == "EMPTY_TEXT"
        assert "empty" in result.error_message.lower()
    
    def test_missing_chunk_ref_error_real(self):
        """Test REAL error handling for missing chunk reference"""
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": "Some text with entities"
                # Missing chunk_ref
            },
            parameters={}
        )
        
        # Execute with REAL validation and error handling
        result = self.tool.execute(request)
        
        # Verify REAL error response
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "chunk_ref" in result.error_message
    
    def test_health_check_real(self):
        """Test REAL health check functionality"""
        health_result = self.tool.health_check()
        
        # Verify REAL health check results
        assert health_result.status in ["success", "error"]
        assert "healthy" in health_result.data
        assert "spacy_model_loaded" in health_result.data
        assert "supported_entity_types" in health_result.data
        
        # If healthy, verify spaCy model is actually loaded
        if health_result.data["healthy"]:
            assert health_result.data["spacy_model_loaded"] == True
            assert len(health_result.data["supported_entity_types"]) > 0
    
    def test_cleanup_real(self):
        """Test REAL cleanup functionality"""
        # Tool should be in ready state initially
        from src.tools.base_tool import ToolStatus
        assert self.tool.status == ToolStatus.READY
        
        # Cleanup should succeed with REAL implementation
        cleanup_success = self.tool.cleanup()
        assert cleanup_success == True
        assert self.tool.status == ToolStatus.READY
    
    @pytest.mark.performance
    def test_performance_requirements_real(self):
        """Test tool meets REAL performance requirements"""
        # Create substantial text for performance testing
        text = " ".join([f"Person{i} works at Company{i} in City{i}." for i in range(50)])
        
        request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": text,
                "chunk_ref": "storage://chunk/perf123"
            },
            parameters={"confidence_threshold": 0.5}  # Lower threshold for real functionality
        )
        
        import time
        start_time = time.time()
        
        # Execute with REAL performance measurement
        result = self.tool.execute(request)
        
        execution_time = time.time() - start_time
        
        # Verify REAL performance meets requirements
        assert result.status == "success"
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert result.execution_time < 10.0
        
        # Verify substantial processing occurred
        assert result.data["total_entities"] > 10  # Should find many entities
    
    
    
    
    
    
    
    def teardown_method(self):
        """Clean up after each test"""
        # Clean up any REAL resources
        if hasattr(self, 'tool'):
            self.tool.cleanup()