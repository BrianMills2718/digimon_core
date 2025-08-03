"""
Functional Tests - Real Tool Execution (NO MOCKS)

Tests actual tool functionality with real data processing.
Follows CLAUDE.md principle: NO lazy mocking/stubs/fallbacks.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
import json

# Import actual tools for real testing
from src.tools.phase1.t01_pdf_processor import PDFProcessor
from src.tools.phase1.t23a_spacy_ner_unified import SpacyNER
from src.tools.phase2.t50_graph_builder import GraphBuilder
from src.core.dependency_injection import DependencyContainer
from src.core.unified_service_interface import ServiceRequest, ServiceResponse


@pytest.fixture
def real_test_data():
    """Create real test data for functional testing"""
    test_documents = {
        "academic_paper": {
            "content": """
Dr. Sarah Johnson from Stanford University published groundbreaking research on 
machine learning algorithms in Nature journal. The study, conducted with 
Professor Michael Chen from MIT, demonstrates novel applications in healthcare 
diagnostics. The research was funded by the National Science Foundation 
grant NSF-2023-ML-001 and involved collaboration with Google Research.

The paper introduces the Johnson-Chen Algorithm, which improves accuracy 
by 23% over existing methods. Clinical trials at Massachusetts General Hospital 
showed promising results for early cancer detection.
""",
            "expected_entities": [
                {"text": "Dr. Sarah Johnson", "label": "PERSON"},
                {"text": "Stanford University", "label": "ORG"},
                {"text": "Professor Michael Chen", "label": "PERSON"},
                {"text": "MIT", "label": "ORG"},
                {"text": "Nature journal", "label": "ORG"},
                {"text": "National Science Foundation", "label": "ORG"},
                {"text": "Google Research", "label": "ORG"},
                {"text": "Massachusetts General Hospital", "label": "ORG"}
            ]
        },
        "business_document": {
            "content": """
Apple Inc. CEO Tim Cook announced Q4 earnings of $94.9 billion. 
The company's iPhone sales increased 15% compared to last quarter.
Microsoft Corporation reported Azure cloud revenue growth of 31%.
Amazon Web Services continues to lead the cloud market with 
33% market share, followed by Microsoft at 21% and Google Cloud at 10%.
""",
            "expected_entities": [
                {"text": "Apple Inc.", "label": "ORG"},
                {"text": "Tim Cook", "label": "PERSON"},
                {"text": "Microsoft Corporation", "label": "ORG"},
                {"text": "Amazon Web Services", "label": "ORG"},
                {"text": "Google Cloud", "label": "ORG"}
            ]
        }
    }
    return test_documents


class TestRealToolExecution:
    """Test actual tool execution with real data - NO MOCKS"""
    
    def test_spacy_ner_real_execution(self, real_test_data):
        """Test SpaCy NER with real execution - NO MOCKS"""
        # Initialize real NER tool
        ner_tool = SpacyNER()
        
        # Process real text
        text = real_test_data["academic_paper"]["content"]
        result = ner_tool.extract_entities_working(text)
        
        # MEASURABLE assertions on real results
        assert len(result) >= 8, f"Expected at least 8 entities, got {len(result)}"
        
        # Verify specific entities are found
        entity_texts = [entity["name"] for entity in result]
        expected_entities = ["Stanford University", "MIT", "Nature", "Google"]
        
        found_entities = []
        for expected in expected_entities:
            found = any(expected.lower() in entity.lower() for entity in entity_texts)
            if found:
                found_entities.append(expected)
        
        assert len(found_entities) >= 3, f"Expected at least 3 key entities, found: {found_entities}"
        
        # Verify entity structure
        for entity in result:
            assert "name" in entity, "Entity missing 'name' field"
            assert "type" in entity, "Entity missing 'type' field"
            assert "confidence" in entity, "Entity missing 'confidence' field"
            assert isinstance(entity["confidence"], (int, float)), "Confidence must be numeric"
            assert 0 <= entity["confidence"] <= 1, "Confidence must be between 0 and 1"
    
    def test_ner_tool_multiple_documents(self, real_test_data):
        """Test NER tool with multiple different document types"""
        ner_tool = SpacyNER()
        
        results = {}
        for doc_type, doc_data in real_test_data.items():
            result = ner_tool.extract_entities_working(doc_data["content"])
            results[doc_type] = result
            
            # Each document should produce meaningful results
            assert len(result) >= 4, f"{doc_type} should have at least 4 entities"
            
            # Verify expected entity types are found
            entity_types = [entity["type"] for entity in result]
            assert "PERSON" in entity_types or "ORG" in entity_types, f"{doc_type} should find PERSON or ORG entities"
        
        # Verify different documents produce different results
        academic_entities = [e["name"] for e in results["academic_paper"]]
        business_entities = [e["name"] for e in results["business_document"]]
        
        # Should have some different entities
        overlap = set(academic_entities) & set(business_entities)
        total_unique = len(set(academic_entities) | set(business_entities))
        overlap_ratio = len(overlap) / total_unique if total_unique > 0 else 0
        
        assert overlap_ratio < 0.8, "Documents should have mostly different entities"
    
    def test_dependency_injection_real_service_creation(self):
        """Test dependency injection with real service creation"""
        container = DependencyContainer()
        
        # Register real services (not mocks)
        container.register_singleton("ner_service", SpacyNER)
        
        # Resolve and verify real service
        ner_service = container.resolve("ner_service")
        assert isinstance(ner_service, SpacyNER), "Should resolve to real SpacyNER instance"
        
        # Test real functionality through container
        test_text = "Apple Inc. is located in Cupertino, California."
        result = ner_service.extract_entities_working(test_text)
        
        assert len(result) >= 1, "Should extract at least 1 entity"
        entity_names = [e["name"] for e in result]
        assert any("Apple" in name for name in entity_names), "Should find Apple entity"
    
    def test_service_request_response_real_data(self):
        """Test ServiceRequest/Response with real data processing"""
        # Create real service request
        request = ServiceRequest(
            operation="extract_entities",
            parameters={
                "text": "Microsoft CEO Satya Nadella announced new AI initiatives.",
                "confidence_threshold": 0.7
            },
            context={"document_type": "business_news"},
            request_id="test_req_001"
        )
        
        # Process with real tool
        ner_tool = SpacyNER()
        entities = ner_tool.extract_entities_working(request.parameters["text"])
        
        # Filter by confidence threshold
        filtered_entities = [
            e for e in entities 
            if e.get("confidence", 0) >= request.parameters["confidence_threshold"]
        ]
        
        # Create real response
        response = ServiceResponse(
            success=True,
            data={"entities": filtered_entities, "count": len(filtered_entities)},
            metadata={
                "operation": request.operation,
                "processing_time": 0.15,
                "confidence_threshold": request.parameters["confidence_threshold"]
            },
            request_id=request.request_id
        )
        
        # Verify real response structure
        assert response.success is True
        assert "entities" in response.data
        assert "count" in response.data
        assert response.data["count"] >= 1, "Should find at least 1 high-confidence entity"
        assert response.request_id == "test_req_001"
        
        # Verify entities meet confidence threshold
        for entity in response.data["entities"]:
            assert entity.get("confidence", 0) >= 0.7, f"Entity {entity} below confidence threshold"


class TestRealDataProcessingWorkflows:
    """Test complete workflows with real data processing"""
    
    def test_document_processing_pipeline_real(self, real_test_data):
        """Test complete document processing pipeline with real data"""
        # Real document processing workflow
        academic_text = real_test_data["academic_paper"]["content"]
        
        # Step 1: Real NER extraction
        ner_tool = SpacyNER()
        entities = ner_tool.extract_entities_working(academic_text)
        
        assert len(entities) >= 5, "Should extract multiple entities from academic text"
        
        # Step 2: Real entity validation and filtering
        validated_entities = []
        for entity in entities:
            # Real validation logic
            if (entity.get("confidence", 0) >= 0.6 and 
                len(entity.get("name", "")) >= 3 and
                entity.get("type") in ["PERSON", "ORG", "GPE"]):
                validated_entities.append(entity)
        
        assert len(validated_entities) >= 3, "Should have multiple validated entities"
        
        # Step 3: Real relationship extraction (simplified)
        relationships = []
        person_entities = [e for e in validated_entities if e["type"] == "PERSON"]
        org_entities = [e for e in validated_entities if e["type"] == "ORG"]
        
        # Find co-occurrence relationships
        for person in person_entities:
            for org in org_entities:
                # Check if person and org appear near each other in text
                person_pos = academic_text.find(person["name"])
                org_pos = academic_text.find(org["name"])
                
                if person_pos != -1 and org_pos != -1 and abs(person_pos - org_pos) < 200:
                    relationships.append({
                        "source": person["name"],
                        "target": org["name"],
                        "type": "AFFILIATED_WITH",
                        "confidence": min(person.get("confidence", 0.8), org.get("confidence", 0.8))
                    })
        
        assert len(relationships) >= 1, "Should find at least 1 real relationship"
        
        # Step 4: Real result compilation
        result = {
            "entities": validated_entities,
            "relationships": relationships,
            "statistics": {
                "total_entities": len(entities),
                "validated_entities": len(validated_entities),
                "relationships_found": len(relationships),
                "document_length": len(academic_text)
            }
        }
        
        # Verify complete pipeline results
        assert result["statistics"]["total_entities"] >= 5
        assert result["statistics"]["validated_entities"] >= 3
        assert result["statistics"]["relationships_found"] >= 1
        assert result["statistics"]["document_length"] > 500
    
    def test_multi_document_real_processing(self, real_test_data):
        """Test processing multiple real documents"""
        ner_tool = SpacyNER()
        
        all_results = []
        for doc_type, doc_data in real_test_data.items():
            # Process each document
            entities = ner_tool.extract_entities_working(doc_data["content"])
            
            # Add document metadata
            doc_result = {
                "document_type": doc_type,
                "content_length": len(doc_data["content"]),
                "entities": entities,
                "entity_count": len(entities)
            }
            all_results.append(doc_result)
        
        # Verify multi-document processing
        assert len(all_results) == 2, "Should process both documents"
        
        total_entities = sum(result["entity_count"] for result in all_results)
        assert total_entities >= 10, f"Should find at least 10 total entities, found {total_entities}"
        
        # Verify document-specific processing
        for result in all_results:
            assert result["entity_count"] >= 4, f"Each document should have >=4 entities"
            assert result["content_length"] > 200, "Each document should have substantial content"
            
            # Verify entity quality
            for entity in result["entities"]:
                assert len(entity.get("name", "")) >= 2, "Entity names should be meaningful"
                assert entity.get("type") in ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT"], "Valid entity types"


class TestRealErrorConditions:
    """Test real error conditions and error handling"""
    
    def test_ner_tool_empty_input_real(self):
        """Test NER tool with empty input - real error handling"""
        ner_tool = SpacyNER()
        
        # Test empty string
        result = ner_tool.extract_entities_working("")
        assert isinstance(result, list), "Should return empty list for empty input"
        assert len(result) == 0, "Empty input should produce no entities"
        
        # Test whitespace only
        result = ner_tool.extract_entities_working("   \n\t   ")
        assert isinstance(result, list), "Should handle whitespace gracefully"
        assert len(result) == 0, "Whitespace should produce no entities"
    
    def test_ner_tool_invalid_input_real(self):
        """Test NER tool with various invalid inputs"""
        ner_tool = SpacyNER()
        
        # Test very short input
        result = ner_tool.extract_entities_working("a")
        assert isinstance(result, list), "Should handle short input"
        
        # Test special characters
        result = ner_tool.extract_entities_working("!@#$%^&*()")
        assert isinstance(result, list), "Should handle special characters"
        
        # Test non-English characters (if supported)
        result = ner_tool.extract_entities_working("こんにちは 中国 日本")
        assert isinstance(result, list), "Should handle non-English text gracefully"
    
    def test_dependency_injection_missing_service_real(self):
        """Test dependency injection with missing services - real error handling"""
        container = DependencyContainer()
        
        # Try to resolve non-existent service
        try:
            result = container.resolve("non_existent_service")
            assert False, "Should raise exception for missing service"
        except (KeyError, ValueError, Exception) as e:
            # Should handle error gracefully
            assert "non_existent_service" in str(e) or "not found" in str(e).lower()
    
    def test_service_response_error_handling_real(self):
        """Test ServiceResponse error handling with real errors"""
        # Test error response creation
        error_response = ServiceResponse(
            success=False,
            data=None,
            metadata={"error_context": "Real processing failure"},
            error_code="PROCESSING_FAILED",
            error_message="NER processing failed due to invalid model",
            request_id="error_test_001"
        )
        
        # Verify error response structure
        assert error_response.success is False
        assert error_response.data is None
        assert error_response.error_code == "PROCESSING_FAILED"
        assert "NER processing failed" in error_response.error_message
        assert error_response.request_id == "error_test_001"


@pytest.mark.performance
class TestRealPerformanceBaseline:
    """Establish performance baselines with real workloads"""
    
    def test_ner_performance_real_workload(self, real_test_data):
        """Test NER performance with real workload"""
        import time
        
        ner_tool = SpacyNER()
        
        # Combine all test data for larger workload
        combined_text = "\n\n".join([
            doc_data["content"] for doc_data in real_test_data.values()
        ])
        
        # Repeat for realistic workload
        large_text = combined_text * 5  # ~5x larger document
        
        # Measure real processing time
        start_time = time.time()
        result = ner_tool.extract_entities_working(large_text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Performance assertions
        assert processing_time < 10.0, f"Processing should complete in <10s, took {processing_time:.2f}s"
        assert len(result) >= 20, f"Should extract multiple entities from large text, got {len(result)}"
        
        # Calculate performance metrics
        text_length = len(large_text)
        entities_per_second = len(result) / processing_time if processing_time > 0 else 0
        chars_per_second = text_length / processing_time if processing_time > 0 else 0
        
        # Performance baselines
        assert entities_per_second >= 5, f"Should process >=5 entities/sec, got {entities_per_second:.1f}"
        assert chars_per_second >= 1000, f"Should process >=1000 chars/sec, got {chars_per_second:.1f}"
    
    def test_dependency_injection_performance_real(self):
        """Test dependency injection performance with real services"""
        import time
        
        container = DependencyContainer()
        
        # Register multiple real services
        services = {
            "ner_service_1": SpacyNER,
            "ner_service_2": SpacyNER,
            "ner_service_3": SpacyNER
        }
        
        for name, service_class in services.items():
            container.register_singleton(name, service_class)
        
        # Measure resolution performance
        start_time = time.time()
        
        resolved_services = []
        for _ in range(100):  # Resolve 100 times
            for service_name in services.keys():
                service = container.resolve(service_name)
                resolved_services.append(service)
        
        end_time = time.time()
        resolution_time = end_time - start_time
        
        # Performance assertions
        assert resolution_time < 1.0, f"300 resolutions should take <1s, took {resolution_time:.2f}s"
        assert len(resolved_services) == 300, "Should resolve all requested services"
        
        # Verify singleton behavior (same instances)
        for i in range(0, len(resolved_services), len(services)):
            service_set = resolved_services[i:i+len(services)]
            assert len(set(id(s) for s in service_set)) == len(services), "Singletons should reuse instances"