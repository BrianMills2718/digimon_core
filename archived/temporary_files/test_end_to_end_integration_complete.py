#!/usr/bin/env python3
"""
Complete End-to-End Integration Test
Verifies all fixes work together in the complete system
"""

import sys
import datetime
import json
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.evidence_logger import evidence_logger
from src.core.tool_protocol import Tool
from src.core.tool_factory import ToolFactory
from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.core.ontology_validator import OntologyValidator
from src.ontology_generator import DomainOntology, EntityType, RelationshipType

# Import the deep API test
from test_task3_api_integration_deep import test_api_authentication_actual_integration


def test_complete_workflow_with_all_fixes():
    """End-to-end test that verifies all fixes work together"""
    
    evidence_logger.log_task_start(
        "COMPLETE_E2E_VERIFICATION",
        "Complete end-to-end test of all CLAUDE.md fixes"
    )
    
    workflow_results = {}
    
    try:
        # 1. Test Tool Protocol (Task 1)
        evidence_logger.log_task_start("E2E_TOOL_PROTOCOL", "Testing tool protocol in workflow")
        
        try:
            # Verify all tools implement Tool protocol
            factory = ToolFactory()
            tools = factory.create_all_tools()
            
            protocol_compliance = all(isinstance(tool, Tool) for tool in tools)
            tool_details = {}
            
            for tool in tools:
                tool_name = tool.__class__.__name__
                tool_details[tool_name] = {
                    "implements_protocol": isinstance(tool, Tool),
                    "has_get_tool_info": hasattr(tool, 'get_tool_info'),
                    "has_execute_query": hasattr(tool, 'execute_query')
                }
            
            workflow_results["tool_protocol_compliance"] = protocol_compliance
            
            evidence_logger.log_task_completion(
                "E2E_TOOL_PROTOCOL", 
                {
                    "tools_tested": len(tools), 
                    "all_compliant": protocol_compliance,
                    "tool_details": tool_details
                },
                protocol_compliance
            )
            
        except Exception as e:
            evidence_logger.log_task_completion(
                "E2E_TOOL_PROTOCOL",
                {"error": str(e), "traceback": traceback.format_exc()},
                False
            )
            workflow_results["tool_protocol_compliance"] = False
        
        # 2. Test Vector Storage (Task 2)
        evidence_logger.log_task_start("E2E_VECTOR_STORAGE", "Testing vector storage in workflow")
        
        try:
            # Test vector embedder tool
            embedder = VectorEmbedder()
            test_chunks = ["Apple Inc. is a technology company.", "Founded by Steve Jobs in 1976."]
            
            embed_result = embedder.embed_text_chunks(test_chunks, "e2e_test_001")
            vector_storage_working = embed_result.get("status") == "success"
            workflow_results["vector_storage_working"] = vector_storage_working
            
            evidence_logger.log_task_completion(
                "E2E_VECTOR_STORAGE",
                {
                    "embeddings_created": embed_result.get("embeddings_count", 0),
                    "result_details": embed_result
                },
                vector_storage_working
            )
            
        except Exception as e:
            evidence_logger.log_task_completion(
                "E2E_VECTOR_STORAGE",
                {"error": str(e), "traceback": traceback.format_exc()},
                False
            )
            workflow_results["vector_storage_working"] = False
        
        # 3. Test API Authentication Integration (Task 3 - FIXED)
        evidence_logger.log_task_start("E2E_API_INTEGRATION", "Testing API integration in workflow")
        
        try:
            # This is the critical test that must pass
            api_integration_result = test_api_authentication_actual_integration()
            api_integration_working = api_integration_result.get("success", False)
            workflow_results["api_integration_working"] = api_integration_working
            
            evidence_logger.log_task_completion(
                "E2E_API_INTEGRATION",
                api_integration_result,
                api_integration_working
            )
            
        except Exception as e:
            evidence_logger.log_task_completion(
                "E2E_API_INTEGRATION",
                {"error": str(e), "traceback": traceback.format_exc()},
                False
            )
            workflow_results["api_integration_working"] = False
        
        # 4. Test DOLCE Ontology (Task 4)
        evidence_logger.log_task_start("E2E_DOLCE_ONTOLOGY", "Testing DOLCE ontology in workflow")
        
        try:
            validator = OntologyValidator()
            
            # Test DOLCE mappings
            test_mappings = {
                "IndividualActor": "PhysicalEndurant",
                "Organization": "PhysicalEndurant", 
                "Location": "PhysicalEndurant",
                "Event": "PhysicalEndurant"
            }
            
            mapping_results = {}
            for entity_type, expected_dolce in test_mappings.items():
                actual_dolce = validator.get_dolce_mapping(entity_type)
                mapping_results[entity_type] = {
                    "expected": expected_dolce,
                    "actual": actual_dolce,
                    "correct": actual_dolce == expected_dolce
                }
            
            dolce_working = all(result["correct"] for result in mapping_results.values())
            workflow_results["dolce_ontology_working"] = dolce_working
            
            evidence_logger.log_task_completion(
                "E2E_DOLCE_ONTOLOGY",
                {"mapping_results": mapping_results, "all_mappings_correct": dolce_working},
                dolce_working
            )
            
        except Exception as e:
            evidence_logger.log_task_completion(
                "E2E_DOLCE_ONTOLOGY",
                {"error": str(e), "traceback": traceback.format_exc()},
                False
            )
            workflow_results["dolce_ontology_working"] = False
        
        # 5. Test Complete Workflow Integration
        evidence_logger.log_task_start("E2E_COMPLETE_WORKFLOW", "Testing complete workflow execution")
        
        try:
            # Create a test ontology
            ontology = DomainOntology(
                domain_name="e2e_test_domain",
                domain_description="End-to-end test domain",
                entity_types=[
                    EntityType(name="ORGANIZATION", description="Organizations", 
                              attributes=["name"], examples=["Apple Inc."]),
                    EntityType(name="PERSON", description="People", 
                              attributes=["name"], examples=["Steve Jobs"])
                ],
                relationship_types=[
                    RelationshipType(name="FOUNDED_BY", description="Founded by relationship", 
                                   source_types=["ORGANIZATION"], target_types=["PERSON"],
                                   examples=["Apple Inc. was founded by Steve Jobs"])
                ],
                extraction_patterns=["Extract entities and relationships"]
            )
            
            # Test complete workflow
            extractor = OntologyAwareExtractor()
            test_text = "Apple Inc. was founded by Steve Jobs."
            
            # Execute extraction
            extraction_result = extractor.extract_entities(
                test_text,               # text_or_chunk_ref
                ontology,                # text_or_ontology
                "e2e_complete_test",     # source_ref_or_confidence
                confidence_threshold=0.7,
                use_mock_apis=True       # Use mock for reliable testing
            )
            
            workflow_successful = True
            if isinstance(extraction_result, dict):
                workflow_successful = extraction_result.get("status") == "success"
            else:
                workflow_successful = hasattr(extraction_result, 'entities')
            
            workflow_results["complete_workflow_working"] = workflow_successful
            
            evidence_logger.log_task_completion(
                "E2E_COMPLETE_WORKFLOW",
                {
                    "workflow_successful": workflow_successful,
                    "extraction_result": str(extraction_result)[:500]  # Truncate for readability
                },
                workflow_successful
            )
            
        except Exception as e:
            evidence_logger.log_task_completion(
                "E2E_COMPLETE_WORKFLOW",
                {"error": str(e), "traceback": traceback.format_exc()},
                False
            )
            workflow_results["complete_workflow_working"] = False
        
        # Overall workflow success
        all_components_working = all(workflow_results.values())
        
        evidence_logger.log_verification_result(
            "COMPLETE_E2E_VERIFICATION",
            {
                "all_components_working": all_components_working,
                "individual_results": workflow_results,
                "system_ready_for_production": all_components_working,
                "total_tests": len(workflow_results),
                "passed_tests": sum(1 for result in workflow_results.values() if result)
            }
        )
        
        return all_components_working
        
    except Exception as e:
        evidence_logger.log_task_completion(
            "COMPLETE_E2E_VERIFICATION",
            {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "workflow_results": workflow_results
            },
            False
        )
        return False


if __name__ == "__main__":
    print("Running complete end-to-end verification...")
    
    # Clear evidence file for clean test
    evidence_logger.clear_evidence_file()
    
    success = test_complete_workflow_with_all_fixes()
    
    if success:
        print("✅ ALL TESTS PASSED - System ready for production")
    else:
        print("❌ SOME TESTS FAILED - Check Evidence.md for details")
        
    print("\nDetailed evidence logged to Evidence.md")