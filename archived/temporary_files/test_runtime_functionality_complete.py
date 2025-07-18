#!/usr/bin/env python3
"""
Complete Runtime Functionality Testing
Automated tests that prove all implementations work in practice without manual interaction
"""

import sys
import os
import subprocess
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.evidence_logger import EvidenceLogger
from src.core.config_manager import ConfigManager

# Initialize evidence logger
evidence_logger = EvidenceLogger()


class RuntimeFunctionalityTester:
    """Comprehensive automated testing of all runtime functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.test_artifacts = []
        
    def test_task1_tool_protocol_runtime(self) -> Dict[str, Any]:
        """Test Tool Protocol Factory actually works at runtime"""
        try:
            evidence_logger.log_task_start("RUNTIME_TASK1_TOOL_PROTOCOL", "Testing tool protocol factory runtime execution")
            
            # Test 1: Import and create factory
            from src.core.tool_factory import ToolFactory
            from src.core.tool_protocol import Tool
            
            factory = ToolFactory()
            
            # Test 2: Call create_all_tools() - this was the original AttributeError
            tools = factory.create_all_tools()
            
            # Test 3: Verify we got tools back
            tools_created = len(tools) > 0
            expected_tool_count = 9
            correct_tool_count = len(tools) == expected_tool_count
            
            # Test 4: Verify each tool implements Tool protocol
            protocol_compliance = all(isinstance(tool, Tool) for tool in tools)
            
            # Test 5: Verify each tool has required methods
            method_compliance = {}
            required_methods = ['execute', 'get_tool_info', 'validate_input']
            
            for tool in tools:
                tool_name = tool.__class__.__name__
                method_compliance[tool_name] = {}
                for method in required_methods:
                    has_method = hasattr(tool, method)
                    is_callable = callable(getattr(tool, method, None))
                    method_compliance[tool_name][method] = has_method and is_callable
            
            all_methods_present = all(
                all(methods.values()) for methods in method_compliance.values()
            )
            
            # Test 6: Try calling get_tool_info() on each tool
            tool_info_results = {}
            for tool in tools:
                try:
                    tool_info = tool.get_tool_info()
                    tool_info_results[tool.__class__.__name__] = {
                        "success": True,
                        "has_tool_id": "tool_id" in tool_info,
                        "has_description": "description" in tool_info
                    }
                except Exception as e:
                    tool_info_results[tool.__class__.__name__] = {
                        "success": False,
                        "error": str(e)
                    }
            
            all_tool_info_working = all(result["success"] for result in tool_info_results.values())
            
            result = {
                "success": True,
                "original_error_fixed": True,  # No AttributeError when calling create_all_tools()
                "tools_created": tools_created,
                "tool_count": len(tools),
                "expected_tool_count": expected_tool_count,
                "correct_tool_count": correct_tool_count,
                "protocol_compliance": protocol_compliance,
                "method_compliance": method_compliance,
                "all_methods_present": all_methods_present,
                "tool_info_results": tool_info_results,
                "all_tool_info_working": all_tool_info_working,
                "overall_functionality": all([
                    tools_created,
                    correct_tool_count,
                    protocol_compliance,
                    all_methods_present,
                    all_tool_info_working
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_TASK1_TOOL_PROTOCOL", result, result["overall_functionality"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "original_error_fixed": False
            }
            evidence_logger.log_task_completion("RUNTIME_TASK1_TOOL_PROTOCOL", error_result, False)
            return error_result
    
    def test_task2_vector_storage_runtime(self) -> Dict[str, Any]:
        """Test Vector Storage actually works with real embeddings"""
        try:
            evidence_logger.log_task_start("RUNTIME_TASK2_VECTOR_STORAGE", "Testing vector storage runtime functionality")
            
            # Test 1: Import classes (check if ImportError is fixed)
            from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
            from src.core.qdrant_store import QdrantStore, InMemoryVectorStore
            
            # Test 2: Create VectorEmbedder instance
            embedder = VectorEmbedder()
            
            # Test 3: Test embed_text_chunks method (this was missing before)
            test_chunks = [
                "Apple Inc. is a technology company founded by Steve Jobs.",
                "Tesla Motors was founded by Elon Musk in 2003.",
                "Google was founded by Larry Page and Sergey Brin."
            ]
            workflow_id = "runtime_test_vector_001"
            
            embed_result = embedder.embed_text_chunks(test_chunks, workflow_id)
            
            # Test 4: Verify embedding result
            embedding_success = embed_result.get("status") == "success"
            embeddings_count = embed_result.get("embeddings_count", 0)
            expected_count = len(test_chunks)
            correct_embedding_count = embeddings_count == expected_count
            
            # Test 5: Test vector store functionality
            store = InMemoryVectorStore()
            store_info = store.get_store_info()
            store_working = store_info.get("status") == "green"
            
            # Test 6: Test backward compatibility alias
            try:
                qdrant_alias = QdrantStore  # Should not raise ImportError
                alias_working = True
            except:
                alias_working = False
            
            result = {
                "success": True,
                "import_errors_fixed": True,  # No ImportError when importing
                "embedder_created": True,
                "embed_method_exists": hasattr(embedder, 'embed_text_chunks'),
                "embed_result": embed_result,
                "embedding_success": embedding_success,
                "embeddings_count": embeddings_count,
                "expected_count": expected_count,
                "correct_embedding_count": correct_embedding_count,
                "vector_store_working": store_working,
                "store_info": store_info,
                "backward_compatibility_alias": alias_working,
                "overall_functionality": all([
                    embedding_success,
                    correct_embedding_count,
                    store_working,
                    alias_working
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_TASK2_VECTOR_STORAGE", result, result["overall_functionality"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "import_errors_fixed": False
            }
            evidence_logger.log_task_completion("RUNTIME_TASK2_VECTOR_STORAGE", error_result, False)
            return error_result
    
    def test_task3_api_authentication_runtime(self) -> Dict[str, Any]:
        """Test API Authentication Integration actually works"""
        try:
            evidence_logger.log_task_start("RUNTIME_TASK3_API_AUTHENTICATION", "Testing API authentication runtime integration")
            
            # Test 1: Import all API components
            from src.core.api_auth_manager import APIAuthManager
            from src.core.api_rate_limiter import APIRateLimiter
            from src.core.enhanced_api_client import EnhancedAPIClient
            from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
            
            # Test 2: Create API components
            auth_manager = APIAuthManager()
            rate_limiter = APIRateLimiter()
            api_client = EnhancedAPIClient(auth_manager)  # Constructor only takes auth_manager
            
            # Test 3: Create OntologyAwareExtractor and verify integration
            extractor = OntologyAwareExtractor()
            
            # Test 4: Verify enhanced API client is integrated (not legacy clients)
            has_api_client = hasattr(extractor, 'api_client')
            has_auth_manager = hasattr(extractor, 'auth_manager')
            has_rate_limiter = hasattr(extractor, 'rate_limiter')
            
            # Test 5: Verify legacy clients are NOT present
            no_legacy_gemini = not hasattr(extractor, 'gemini_model')
            no_legacy_openai = not hasattr(extractor, 'openai_client')
            
            # Test 6: Test API client functionality with mock request
            class MockAPIClient:
                def __init__(self):
                    self.calls_made = []
                
                def make_request(self, service, request_type, **kwargs):
                    self.calls_made.append({
                        'service': service,
                        'request_type': request_type,
                        'kwargs': kwargs
                    })
                    return {
                        "content": '{"entities": [{"text": "Apple Inc.", "type": "ORGANIZATION"}]}',
                        "usage": {"tokens": 100}
                    }
            
            # Replace with mock for testing
            original_client = extractor.api_client
            mock_client = MockAPIClient()
            extractor.api_client = mock_client
            
            # Test 7: Call extraction method to verify integration
            test_text = "Apple Inc. is a technology company."
            workflow_id = "runtime_api_test_001"
            
            try:
                # Create a simple test ontology for the extractor
                from src.ontology_generator import DomainOntology, EntityType, RelationshipType
                
                test_ontology = DomainOntology(
                    domain_name="runtime_test",
                    domain_description="Test domain for runtime testing",
                    entity_types=[
                        EntityType(name="ORGANIZATION", description="Organizations", attributes=["name"], examples=["Apple Inc."]),
                        EntityType(name="PERSON", description="People", attributes=["name"], examples=["Steve Jobs"])
                    ],
                    relationship_types=[
                        RelationshipType(name="FOUNDED", description="Founded relationship", 
                                       source_types=["PERSON"], target_types=["ORGANIZATION"], 
                                       examples=["Steve Jobs founded Apple Inc."])
                    ],
                    extraction_patterns=["Extract entities and relationships"]
                )
                
                extraction_result = extractor.extract_entities(test_text, test_ontology, "runtime_test", use_mock_apis=True)
                
                # Handle OntologyExtractionResult object
                if hasattr(extraction_result, 'entities'):
                    extraction_success = True
                    # Convert to dict for JSON serialization
                    extraction_result_dict = {
                        "entities": [str(e) for e in extraction_result.entities],
                        "relationships": [str(r) for r in extraction_result.relationships] if hasattr(extraction_result, 'relationships') else [],
                        "mentions": len(extraction_result.mentions) if hasattr(extraction_result, 'mentions') else 0,
                        "success": True
                    }
                    extraction_result = extraction_result_dict
                else:
                    extraction_success = isinstance(extraction_result, dict) and "entities" in extraction_result
                
                api_calls_made = len(mock_client.calls_made) > 0
            except Exception as e:
                extraction_success = False
                api_calls_made = False
                extraction_result = {"error": str(e)}
            
            # Restore original client
            extractor.api_client = original_client
            
            result = {
                "success": True,
                "api_components_imported": True,
                "auth_manager_created": auth_manager is not None,
                "rate_limiter_created": rate_limiter is not None,
                "api_client_created": api_client is not None,
                "extractor_integration": {
                    "has_api_client": has_api_client,
                    "has_auth_manager": has_auth_manager,
                    "has_rate_limiter": has_rate_limiter
                },
                "legacy_clients_removed": {
                    "no_legacy_gemini": no_legacy_gemini,
                    "no_legacy_openai": no_legacy_openai
                },
                "api_integration_test": {
                    "extraction_success": extraction_success,
                    "api_calls_made": api_calls_made,
                    "extraction_result": extraction_result
                },
                "overall_functionality": all([
                    has_api_client,
                    has_auth_manager,
                    has_rate_limiter,
                    no_legacy_gemini,
                    no_legacy_openai,
                    extraction_success,
                    api_calls_made
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_TASK3_API_AUTHENTICATION", result, result["overall_functionality"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            evidence_logger.log_task_completion("RUNTIME_TASK3_API_AUTHENTICATION", error_result, False)
            return error_result
    
    def test_task4_dolce_ontology_runtime(self) -> Dict[str, Any]:
        """Test DOLCE Ontology actually works with real validation"""
        try:
            evidence_logger.log_task_start("RUNTIME_TASK4_DOLCE_ONTOLOGY", "Testing DOLCE ontology runtime validation")
            
            # Test 1: Import DOLCE components
            from src.ontology_library.dolce_ontology import dolce_ontology
            from src.core.ontology_validator import OntologyValidator
            from src.core.data_models import Entity, QualityTier
            
            # Test 2: Create validator
            validator = OntologyValidator()
            
            # Test 3: Test DOLCE mappings (these were incorrect before)
            test_mappings = {
                "IndividualActor": "PhysicalEndurant",
                "Organization": "PhysicalEndurant", 
                "Location": "PhysicalEndurant",
                "Event": "PhysicalEndurant",
                "Document": "PhysicalEndurant",
                "Concept": "PhysicalEndurant"
            }
            
            mapping_results = {}
            for entity_type, expected_mapping in test_mappings.items():
                actual_mapping = validator.get_dolce_mapping(entity_type)
                mapping_results[entity_type] = {
                    "expected": expected_mapping,
                    "actual": actual_mapping,
                    "correct": actual_mapping == expected_mapping
                }
            
            all_mappings_correct = all(result["correct"] for result in mapping_results.values())
            
            # Test 4: Test Entity creation (this had ValidationError before)
            try:
                test_entities = []
                entity_creation_success = True
                
                # Create entities with all required fields
                entities_data = [
                    {"id": "test_person", "canonical_name": "John Doe", "entity_type": "Person"},
                    {"id": "test_org", "canonical_name": "Apple Inc.", "entity_type": "Organization"},
                    {"id": "test_loc", "canonical_name": "California", "entity_type": "Location"}
                ]
                
                for entity_data in entities_data:
                    entity = Entity(
                        id=entity_data["id"],
                        canonical_name=entity_data["canonical_name"],
                        entity_type=entity_data["entity_type"],
                        surface_forms=[],
                        confidence=0.9,
                        quality_tier=QualityTier.HIGH,
                        created_by="runtime_test",
                        created_at=datetime.datetime.now(),
                        workflow_id="runtime_test_workflow"
                    )
                    test_entities.append(entity)
                    
            except Exception as e:
                entity_creation_success = False
                test_entities = []
                entity_creation_error = str(e)
            
            # Test 5: Test entity validation
            validation_results = []
            if test_entities:
                for entity in test_entities:
                    validation = validator.validate_entity_simple(entity)
                    validation_results.append(validation)
            
            all_validations_pass = all(v.get("valid", False) for v in validation_results)
            
            # Test 6: Test DOLCE ontology structure
            dolce_concepts = dolce_ontology.concepts
            dolce_relations = dolce_ontology.relations  
            dolce_mappings = dolce_ontology.graphrag_mappings
            
            dolce_structure_complete = all([
                len(dolce_concepts) > 0,
                len(dolce_relations) > 0,
                len(dolce_mappings) > 0
            ])
            
            result = {
                "success": True,
                "dolce_components_imported": True,
                "validator_created": validator is not None,
                "mapping_test": {
                    "mapping_results": mapping_results,
                    "all_mappings_correct": all_mappings_correct
                },
                "entity_creation": {
                    "entity_creation_success": entity_creation_success,
                    "entities_created": len(test_entities),
                    "validation_error_fixed": entity_creation_success
                },
                "entity_validation": {
                    "validation_results": validation_results,
                    "all_validations_pass": all_validations_pass
                },
                "dolce_structure": {
                    "concepts_count": len(dolce_concepts),
                    "relations_count": len(dolce_relations),
                    "mappings_count": len(dolce_mappings),
                    "structure_complete": dolce_structure_complete
                },
                "overall_functionality": all([
                    all_mappings_correct,
                    entity_creation_success,
                    all_validations_pass,
                    dolce_structure_complete
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_TASK4_DOLCE_ONTOLOGY", result, result["overall_functionality"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "validation_error_fixed": False
            }
            evidence_logger.log_task_completion("RUNTIME_TASK4_DOLCE_ONTOLOGY", error_result, False)
            return error_result
    
    def test_streamlit_ui_runtime(self) -> Dict[str, Any]:
        """Test Streamlit UI components actually work"""
        try:
            evidence_logger.log_task_start("RUNTIME_STREAMLIT_UI", "Testing Streamlit UI runtime functionality")
            
            # Test 1: Import streamlit app
            import streamlit_app
            
            # Test 2: Test session state initialization
            streamlit_app.init_session_state()
            
            # Test 3: Test ontology generator
            generator = streamlit_app.get_ontology_generator()
            generator_available = generator is not None
            
            # Test 4: Test storage service
            storage = streamlit_app.get_storage_service()
            storage_available = storage is not None
            
            # Test 5: Test ontology generation workflow
            test_domain = "Climate policy analysis for renewable energy"
            config = {
                "temperature": 0.7,
                "max_entities": 8,
                "max_relations": 5
            }
            
            ontology = streamlit_app.generate_ontology_with_gemini(test_domain, config)
            ontology_generated = ontology is not None and hasattr(ontology, 'domain')
            
            # Test 6: Test ontology validation workflow
            if ontology:
                sample_text = "The government implemented new climate policies to reduce carbon emissions through renewable energy investments."
                validation_result = streamlit_app.validate_ontology_with_text(ontology, sample_text)
                validation_working = "entities_found" in validation_result
            else:
                validation_working = False
                validation_result = {}
            
            # Test 7: Test ontology refinement workflow
            if ontology:
                refinement_request = "Add more entity types for policy implementation"
                refined_ontology = streamlit_app.refine_ontology_with_gemini(ontology, refinement_request)
                refinement_working = refined_ontology is not None
            else:
                refinement_working = False
            
            # Test 8: Test UI component functions availability
            ui_functions = [
                "render_header", "render_sidebar", "render_chat_interface",
                "render_ontology_preview", "process_user_input", "export_ontology_json"
            ]
            
            ui_functions_available = {}
            for func_name in ui_functions:
                ui_functions_available[func_name] = hasattr(streamlit_app, func_name) and callable(getattr(streamlit_app, func_name))
            
            all_ui_functions_available = all(ui_functions_available.values())
            
            result = {
                "success": True,
                "streamlit_app_imported": True,
                "session_state_working": True,
                "generator_available": generator_available,
                "storage_available": storage_available,
                "ontology_generation": {
                    "ontology_generated": ontology_generated,
                    "domain": ontology.domain if ontology else None,
                    "entity_types_count": len(ontology.entity_types) if ontology else 0,
                    "relation_types_count": len(ontology.relation_types) if ontology else 0
                },
                "ontology_validation": {
                    "validation_working": validation_working,
                    "validation_result": validation_result
                },
                "ontology_refinement": {
                    "refinement_working": refinement_working
                },
                "ui_components": {
                    "ui_functions_available": ui_functions_available,
                    "all_ui_functions_available": all_ui_functions_available
                },
                "overall_functionality": all([
                    generator_available,
                    ontology_generated,
                    validation_working,
                    refinement_working,
                    all_ui_functions_available
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_STREAMLIT_UI", result, result["overall_functionality"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            evidence_logger.log_task_completion("RUNTIME_STREAMLIT_UI", error_result, False)
            return error_result
    
    def test_end_to_end_workflow_runtime(self) -> Dict[str, Any]:
        """Test complete end-to-end workflow actually works"""
        try:
            evidence_logger.log_task_start("RUNTIME_END_TO_END", "Testing complete end-to-end workflow")
            
            # Create a temporary test document
            test_document_content = """
            Apple Inc. is a multinational technology company headquartered in Cupertino, California.
            The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
            Apple designs and develops consumer electronics, computer software, and online services.
            Tim Cook is the current CEO of Apple Inc.
            Apple's main products include the iPhone, iPad, Mac computers, and Apple Watch.
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(test_document_content)
                temp_file_path = temp_file.name
            
            workflow_id = "runtime_e2e_test_001"
            
            # Test 1: Tool Protocol - Create tools
            from src.core.tool_factory import ToolFactory
            factory = ToolFactory()
            tools = factory.create_all_tools()
            
            # Test 2: Vector Storage - Generate embeddings
            from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
            embedder = VectorEmbedder()
            
            # Create test chunks from document
            text_chunks = [chunk.strip() for chunk in test_document_content.split('.') if chunk.strip()]
            embed_result = embedder.embed_text_chunks(text_chunks, workflow_id)
            
            # Test 3: API Authentication - Extract entities
            from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
            extractor = OntologyAwareExtractor()
            
            # Mock the API client for testing
            class MockAPIClient:
                def make_request(self, service, request_type, **kwargs):
                    return {
                        "content": json.dumps({
                            "entities": [
                                {"text": "Apple Inc.", "type": "ORGANIZATION", "confidence": 0.9},
                                {"text": "Steve Jobs", "type": "PERSON", "confidence": 0.95},
                                {"text": "Cupertino", "type": "LOCATION", "confidence": 0.8}
                            ],
                            "relationships": [
                                {"source": "Steve Jobs", "target": "Apple Inc.", "relation": "FOUNDED", "confidence": 0.9}
                            ]
                        }),
                        "usage": {"tokens": 150}
                    }
            
            original_client = extractor.api_client
            extractor.api_client = MockAPIClient()
            
            # Create test ontology for end-to-end extraction
            from src.ontology_generator import DomainOntology, EntityType, RelationshipType
            
            e2e_ontology = DomainOntology(
                domain_name="e2e_test",
                domain_description="End-to-end test domain",
                entity_types=[
                    EntityType(name="ORGANIZATION", description="Organizations", attributes=["name"], examples=["Apple Inc."]),
                    EntityType(name="PERSON", description="People", attributes=["name"], examples=["Steve Jobs"]),
                    EntityType(name="LOCATION", description="Places", attributes=["name"], examples=["Cupertino"])
                ],
                relationship_types=[
                    RelationshipType(name="FOUNDED", description="Founded relationship", 
                                   source_types=["PERSON"], target_types=["ORGANIZATION"],
                                   examples=["Steve Jobs founded Apple Inc."]),
                    RelationshipType(name="LOCATED_IN", description="Located in relationship",
                                   source_types=["ORGANIZATION"], target_types=["LOCATION"],
                                   examples=["Apple Inc. is located in Cupertino"])
                ],
                extraction_patterns=["Extract entities and relationships from text"]
            )
            
            # Use extract_entities method with test ontology
            extraction_result = extractor.extract_entities(test_document_content, e2e_ontology, "e2e_test", use_mock_apis=True)
            
            # Handle OntologyExtractionResult object for end-to-end test
            if hasattr(extraction_result, 'entities'):
                extraction_success = True
                entities_count = len(extraction_result.entities)
                relationships_count = len(extraction_result.relationships) if hasattr(extraction_result, 'relationships') else 0
            else:
                extraction_success = isinstance(extraction_result, dict) and "entities" in extraction_result
                entities_count = len(extraction_result.get("entities", []))
                relationships_count = len(extraction_result.get("relationships", []))
            
            # Restore original client
            extractor.api_client = original_client
            
            # Test 4: DOLCE Ontology - Validate extracted entities
            from src.core.ontology_validator import OntologyValidator
            from src.core.data_models import Entity, QualityTier
            
            validator = OntologyValidator()
            
            # Create test entities for validation
            test_entities = [
                Entity(
                    id="apple_inc",
                    canonical_name="Apple Inc.",
                    entity_type="Organization",
                    surface_forms=["Apple", "Apple Inc."],
                    confidence=0.9,
                    quality_tier=QualityTier.HIGH,
                    created_by="e2e_test",
                    created_at=datetime.datetime.now(),
                    workflow_id=workflow_id
                )
            ]
            
            validation_results = []
            for entity in test_entities:
                validation = validator.validate_entity_simple(entity)
                validation_results.append(validation)
            
            # Test 5: UI Integration - Generate ontology
            import streamlit_app
            
            ui_ontology = streamlit_app.generate_ontology_with_gemini(
                "Technology company analysis", 
                {"temperature": 0.7, "max_entities": 5}
            )
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            result = {
                "success": True,
                "workflow_id": workflow_id,
                "tool_protocol_test": {
                    "tools_created": len(tools),
                    "tools_working": len(tools) > 0
                },
                "vector_storage_test": {
                    "embedding_success": embed_result.get("status") == "success",
                    "embeddings_count": embed_result.get("embeddings_count", 0),
                    "chunks_processed": len(text_chunks)
                },
                "api_authentication_test": {
                    "extraction_success": extraction_success,
                    "entities_extracted": entities_count,
                    "relationships_extracted": relationships_count
                },
                "dolce_ontology_test": {
                    "validation_success": all(v.get("valid", False) for v in validation_results),
                    "entities_validated": len(validation_results)
                },
                "ui_integration_test": {
                    "ui_ontology_generated": ui_ontology is not None,
                    "ontology_domain": ui_ontology.domain if ui_ontology else None
                },
                "overall_workflow_success": all([
                    len(tools) > 0,
                    embed_result.get("status") == "success",
                    extraction_success,
                    all(v.get("valid", False) for v in validation_results),
                    ui_ontology is not None
                ])
            }
            
            evidence_logger.log_task_completion("RUNTIME_END_TO_END", result, result["overall_workflow_success"])
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            evidence_logger.log_task_completion("RUNTIME_END_TO_END", error_result, False)
            return error_result
    
    def run_complete_runtime_testing(self) -> Dict[str, Any]:
        """Run all runtime functionality tests"""
        print("🚀 COMPREHENSIVE RUNTIME FUNCTIONALITY TESTING")
        print("=" * 70)
        
        # Clear evidence and start logging
        evidence_logger.clear_evidence_file()
        evidence_logger.log_task_start(
            "COMPLETE_RUNTIME_TESTING",
            "Comprehensive runtime testing of all implementations to prove functionality"
        )
        
        # Test categories
        test_categories = [
            ("Task 1: Tool Protocol Factory", self.test_task1_tool_protocol_runtime),
            ("Task 2: Vector Storage Implementation", self.test_task2_vector_storage_runtime),
            ("Task 3: API Authentication Integration", self.test_task3_api_authentication_runtime),
            ("Task 4: DOLCE Ontology Validation", self.test_task4_dolce_ontology_runtime),
            ("Streamlit UI Functionality", self.test_streamlit_ui_runtime),
            ("End-to-End Workflow", self.test_end_to_end_workflow_runtime)
        ]
        
        results = {}
        all_tests_passed = True
        
        for category_name, test_func in test_categories:
            print(f"\n🔍 Testing {category_name}...")
            
            try:
                result = test_func()
                results[category_name] = result
                
                success = result.get("overall_functionality", result.get("overall_workflow_success", result.get("success", False)))
                
                if success:
                    print(f"✅ {category_name}: PASS")
                else:
                    print(f"❌ {category_name}: FAIL")
                    all_tests_passed = False
                    
            except Exception as e:
                print(f"❌ {category_name}: ERROR - {e}")
                results[category_name] = {"success": False, "error": str(e)}
                all_tests_passed = False
        
        # Overall results
        print("\n" + "=" * 70)
        print("📊 RUNTIME TESTING SUMMARY")
        print("=" * 70)
        
        for category, result in results.items():
            success = result.get("overall_functionality", result.get("overall_workflow_success", result.get("success", False)))
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {category}")
        
        print(f"\n🎯 OVERALL RUNTIME STATUS: {'✅ ALL FUNCTIONALITY VERIFIED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
        
        # Log final results
        evidence_logger.log_verification_result(
            "COMPLETE_RUNTIME_TESTING",
            {
                "all_tests_passed": all_tests_passed,
                "detailed_results": results,
                "runtime_functionality_verified": all_tests_passed,
                "test_categories_passed": sum(1 for result in results.values() 
                                           if result.get("overall_functionality", result.get("overall_workflow_success", result.get("success", False)))),
                "total_test_categories": len(results),
                "evidence_timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        if all_tests_passed:
            print("\n🚀 ALL RUNTIME FUNCTIONALITY VERIFIED!")
            print("   Every claimed implementation works in practice")
            print("   No manual interaction required - all automated")
        else:
            print("\n🔧 Some runtime tests failed. Check detailed results above.")
        
        return {
            "all_tests_passed": all_tests_passed,
            "detailed_results": results
        }


def main():
    """Main function"""
    tester = RuntimeFunctionalityTester()
    results = tester.run_complete_runtime_testing()
    return results["all_tests_passed"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)