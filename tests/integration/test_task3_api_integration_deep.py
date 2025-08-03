#!/usr/bin/env python3
"""
Deep Integration Test for Task 3: API Authentication
Verifies that OntologyAwareExtractor actually uses enhanced API client
"""

import sys
import datetime
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.core.evidence_logger import evidence_logger
from src.ontology_generator import DomainOntology, EntityType, RelationshipType


def test_api_authentication_actual_integration():
    """Deep test that verifies API client is actually used in real execution"""
    
    evidence_logger.log_task_start(
        "TASK3_API_INTEGRATION_DEEP_TEST",
        "Testing that OntologyAwareExtractor actually uses enhanced API client"
    )
    
    # Test setup
    test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
    workflow_id = "test_api_integration_001"
    
    try:
        # Create real extractor instance
        extractor = OntologyAwareExtractor()
        
        # Verify components are properly initialized
        assert hasattr(extractor, 'api_client'), "API client not initialized"
        assert hasattr(extractor, 'auth_manager'), "Auth manager not initialized"
        
        evidence_logger.log_test_execution("API_CLIENT_INITIALIZATION", {
            "status": "success",
            "has_api_client": hasattr(extractor, 'api_client'),
            "has_auth_manager": hasattr(extractor, 'auth_manager'),
            "google_available": extractor.google_available,
            "openai_available": extractor.openai_available
        })
        
        # CRITICAL TEST: Verify no legacy API clients exist
        legacy_clients_removed = True
        legacy_issues = []
        
        if hasattr(extractor, 'gemini_model'):
            legacy_clients_removed = False
            legacy_issues.append("gemini_model still exists")
        
        if hasattr(extractor, 'openai_client'):
            legacy_clients_removed = False
            legacy_issues.append("openai_client still exists")
        
        evidence_logger.log_test_execution("LEGACY_CLIENT_REMOVAL", {
            "status": "success" if legacy_clients_removed else "failure",
            "legacy_clients_removed": legacy_clients_removed,
            "legacy_issues": legacy_issues
        })
        
        # Patch the API client to track calls
        original_make_request = extractor.api_client.make_request
        api_calls_made = []
        
        def track_api_calls(*args, **kwargs):
            api_calls_made.append({
                'args': args,
                'kwargs': kwargs,
                'timestamp': datetime.datetime.now().isoformat()
            })
            # Return mock response for testing
            class MockResponse:
                def __init__(self):
                    self.success = True
                    self.response_data = {"choices": [{"message": {"content": '{"entities": [{"text": "Apple Inc.", "type": "ORGANIZATION", "confidence": 0.9, "context": "technology company"}], "relationships": []}'}}]}
                    self.service_used = "openai"
                    self.error = None
            
            return MockResponse()
        
        extractor.api_client.make_request = track_api_calls
        
        # Also patch extract_content_from_response
        def mock_extract_content(response):
            if hasattr(response, 'response_data') and response.response_data:
                return response.response_data["choices"][0]["message"]["content"]
            return ""
        
        extractor.api_client.extract_content_from_response = mock_extract_content
        
        # Create test ontology
        ontology = DomainOntology(
            domain_name="test_integration",
            domain_description="Test domain for API integration verification",
            entity_types=[
                EntityType(name="ORGANIZATION", description="Organizations", 
                          attributes=["name"], examples=["Apple Inc.", "Microsoft"]),
                EntityType(name="PERSON", description="People", 
                          attributes=["name"], examples=["Steve Jobs", "Bill Gates"]),
                EntityType(name="LOCATION", description="Places", 
                          attributes=["name"], examples=["California", "Washington"])
            ],
            relationship_types=[
                RelationshipType(name="FOUNDED_BY", description="Founded by relationship", 
                               source_types=["ORGANIZATION"], target_types=["PERSON"],
                               examples=["Apple Inc. was founded by Steve Jobs"])
            ],
            extraction_patterns=["Extract entities and relationships"]
        )
        
        # Execute extraction using the original API
        # Call with positional arguments as expected by the method
        result = extractor.extract_entities(
            test_text,               # text_or_chunk_ref
            ontology,                # text_or_ontology 
            workflow_id,             # source_ref_or_confidence
            confidence_threshold=0.7,
            use_mock_apis=False      # Force real API usage
        )
        
        # CRITICAL VERIFICATION: API client must have been called
        api_client_was_called = len(api_calls_made) > 0
        
        evidence_logger.log_test_execution("API_CLIENT_USAGE_VERIFICATION", {
            "status": "success" if api_client_was_called else "failure",
            "api_calls_made": len(api_calls_made),
            "api_call_details": api_calls_made,
            "extraction_result": {
                "status": result.get("status") if isinstance(result, dict) else "unknown",
                "entities_found": len(result.entities) if hasattr(result, 'entities') else len(result.get("entities", [])),
            }
        })
        
        # Verify extraction succeeded
        extraction_success = True
        if isinstance(result, dict):
            extraction_success = result.get("status") == "success"
        else:
            extraction_success = hasattr(result, 'entities') and len(result.entities) > 0
        
        evidence_logger.log_test_execution("EXTRACTION_SUCCESS_VERIFICATION", {
            "status": "success" if extraction_success else "failure",
            "extraction_successful": extraction_success,
            "result_type": type(result).__name__
        })
        
        # Overall test result
        overall_success = (
            legacy_clients_removed and
            api_client_was_called and
            extraction_success
        )
        
        test_result = {
            "success": overall_success,
            "legacy_clients_removed": legacy_clients_removed,
            "api_client_called": api_client_was_called,
            "extraction_successful": extraction_success,
            "api_calls_made": api_calls_made,
            "extraction_result": result if isinstance(result, dict) else str(result)
        }
        
        evidence_logger.log_task_completion(
            "TASK3_API_INTEGRATION_DEEP_TEST",
            test_result,
            overall_success
        )
        
        return test_result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        evidence_logger.log_task_completion(
            "TASK3_API_INTEGRATION_DEEP_TEST",
            error_result,
            False
        )
        
        return error_result


if __name__ == "__main__":
    print("Running deep API integration test...")
    result = test_api_authentication_actual_integration()
    
    if result["success"]:
        print("✅ API integration test PASSED")
        print(f"   - Legacy clients removed: {result['legacy_clients_removed']}")
        print(f"   - API client called: {result['api_client_called']}")
        print(f"   - Extraction successful: {result['extraction_successful']}")
    else:
        print("❌ API integration test FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        
    print(f"\nDetailed results saved to Evidence.md")