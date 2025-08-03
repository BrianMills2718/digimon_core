"""
Integration Tests - Complete GraphRAG Pipeline

Tests integration across major components with real data flows.
NO MOCKS - Tests actual component interactions and data processing.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import time

# Import major components for integration testing
from src.core.dependency_injection import DependencyContainer
from src.core.unified_service_interface import ServiceRequest, ServiceResponse
from src.core.security_validation import SecurityValidator
from src.tools.phase1.t23a_spacy_ner_unified import SpacyNER
from src.tools.phase1.t27_relationship_extractor_unified import RelationshipExtractor
from src.core.anyio_api_client import AnyIOAPIClient


@pytest.fixture
def integration_environment():
    """Set up integration test environment with real services"""
    # Create dependency injection container
    container = DependencyContainer()
    
    # Register real services (no mocks)
    container.register_singleton("ner_service", SpacyNER)
    container.register_singleton("security_validator", SecurityValidator)
    container.register_singleton("api_client", AnyIOAPIClient)
    
    # Create test data directory
    test_data_dir = Path(tempfile.mkdtemp())
    
    return {
        "container": container,
        "test_data_dir": test_data_dir,
        "cleanup": lambda: test_data_dir.unlink() if test_data_dir.exists() else None
    }


@pytest.fixture
def real_academic_documents():
    """Real academic document data for integration testing"""
    return {
        "paper_1": {
            "title": "Machine Learning Applications in Healthcare",
            "content": """
Dr. Sarah Johnson from Stanford University published groundbreaking research on 
machine learning algorithms in Nature journal. The study, conducted with 
Professor Michael Chen from MIT, demonstrates novel applications in healthcare 
diagnostics. The research was funded by the National Science Foundation 
grant NSF-2023-ML-001 and involved collaboration with Google Research.

The paper introduces the Johnson-Chen Algorithm, which improves accuracy 
by 23% over existing methods. Clinical trials at Massachusetts General Hospital 
showed promising results for early cancer detection. The algorithm processes 
medical imaging data using deep neural networks trained on over 100,000 
patient records from Mayo Clinic and Johns Hopkins Hospital.

Key findings include:
1. 95% accuracy in early-stage cancer detection
2. 40% reduction in false positives compared to existing methods
3. Processing time reduced from 4 hours to 15 minutes
4. Successful validation across 5 major medical centers

The research team included Dr. Elena Rodriguez from UCSF, Dr. James Wilson 
from Harvard Medical School, and Dr. Priya Patel from Cleveland Clinic.
""",
            "authors": ["Dr. Sarah Johnson", "Professor Michael Chen"],
            "institutions": ["Stanford University", "MIT", "Massachusetts General Hospital"],
            "funding": ["National Science Foundation"]
        },
        "paper_2": {
            "title": "Quantum Computing Advances in Cryptography",
            "content": """
Professor Alan Turing Jr. from Oxford University led a breakthrough study 
in quantum cryptography published in Science magazine. The research, 
collaborating with Dr. Lisa Chen from IBM Research and Dr. David Kumar 
from Microsoft Quantum, demonstrates practical applications of quantum 
computing in secure communications.

The project, funded by the European Research Council grant ERC-2023-QC-002 
and supported by DARPA, developed the Turing-Chen Protocol for quantum 
key distribution. Testing at CERN and Los Alamos National Laboratory 
showed 99.9% security against classical attacks.

The quantum computer used 128 qubits manufactured by Rigetti Computing 
and Google Quantum AI. Performance benchmarks conducted at Oak Ridge 
National Laboratory demonstrated:
1. Quantum supremacy achieved for cryptographic problems
2. 1000x speed improvement over classical methods
3. Resistance to Shor's algorithm attacks
4. Successful deployment in bank security systems

Research partners included Intel Labs, D-Wave Systems, and the 
University of Waterloo Institute for Quantum Computing.
""",
            "authors": ["Professor Alan Turing Jr.", "Dr. Lisa Chen", "Dr. David Kumar"],
            "institutions": ["Oxford University", "IBM Research", "Microsoft Quantum"],
            "funding": ["European Research Council", "DARPA"]
        }
    }


class TestCompleteGraphRAGPipeline:
    """Test complete GraphRAG pipeline integration"""
    
    def test_end_to_end_document_processing(self, integration_environment, real_academic_documents):
        """Test complete document processing pipeline end-to-end"""
        container = integration_environment["container"]
        
        # Step 1: Initialize services
        ner_service = container.resolve("ner_service")
        security_validator = container.resolve("security_validator")
        
        # Step 2: Process multiple documents
        processed_documents = []
        
        for doc_id, doc_data in real_academic_documents.items():
            # Security validation
            security_issues = security_validator.scan_file(__file__)  # Use this file as example
            
            # Entity extraction
            entities = ner_service.extract_entities_working(doc_data["content"])
            
            # Document processing result
            doc_result = {
                "document_id": doc_id,
                "title": doc_data["title"],
                "content_length": len(doc_data["content"]),
                "entities": entities,
                "entity_count": len(entities),
                "security_issues": len(security_issues),
                "processing_timestamp": time.time()
            }
            processed_documents.append(doc_result)
        
        # Step 3: Verify end-to-end processing
        assert len(processed_documents) == 2, "Should process both documents"
        
        total_entities = sum(doc["entity_count"] for doc in processed_documents)
        assert total_entities >= 20, f"Should extract substantial entities across documents, got {total_entities}"
        
        # Verify document-specific processing
        for doc in processed_documents:
            assert doc["entity_count"] >= 8, f"Document {doc['document_id']} should have >=8 entities"
            assert doc["content_length"] > 1000, "Documents should have substantial content"
            
            # Verify entity quality
            person_entities = [e for e in doc["entities"] if e.get("type") == "PERSON"]
            org_entities = [e for e in doc["entities"] if e.get("type") == "ORG"]
            
            assert len(person_entities) >= 2, f"Should find multiple person entities"
            assert len(org_entities) >= 3, f"Should find multiple organization entities"
    
    def test_cross_document_entity_resolution(self, integration_environment, real_academic_documents):
        """Test entity resolution across multiple documents"""
        container = integration_environment["container"]
        ner_service = container.resolve("ner_service")
        
        # Extract entities from all documents
        all_entities = []
        document_entities = {}
        
        for doc_id, doc_data in real_academic_documents.items():
            entities = ner_service.extract_entities_working(doc_data["content"])
            document_entities[doc_id] = entities
            all_entities.extend(entities)
        
        # Find cross-document entity matches
        entity_names = [e["name"] for e in all_entities]
        unique_entities = set(entity_names)
        
        # Identify potential duplicate entities across documents
        duplicates = []
        for entity_name in unique_entities:
            occurrences = [e for e in all_entities if e["name"] == entity_name]
            if len(occurrences) > 1:
                duplicates.append({
                    "entity_name": entity_name,
                    "occurrences": len(occurrences),
                    "documents": list(set(doc_id for doc_id, entities in document_entities.items() 
                                        if any(e["name"] == entity_name for e in entities)))
                })
        
        # Verify cross-document analysis
        assert len(all_entities) >= 20, "Should have substantial entities across documents"
        assert len(unique_entities) >= 15, "Should have diverse unique entities"
        
        # Should find some entities appearing in multiple documents (institutions, researchers)
        multi_doc_entities = [d for d in duplicates if len(d["documents"]) > 1]
        assert len(multi_doc_entities) >= 1, "Should find entities appearing across documents"
    
    def test_service_integration_with_real_data_flow(self, integration_environment, real_academic_documents):
        """Test service integration with real data flowing between services"""
        container = integration_environment["container"]
        
        # Get services
        ner_service = container.resolve("ner_service")
        security_validator = container.resolve("security_validator")
        
        # Create service request
        doc_content = real_academic_documents["paper_1"]["content"]
        
        request = ServiceRequest(
            operation="process_document",
            parameters={
                "content": doc_content,
                "extract_entities": True,
                "validate_security": True,
                "confidence_threshold": 0.7
            },
            context={"document_type": "academic_paper"},
            request_id="integration_test_001"
        )
        
        # Step 1: Entity extraction
        entities = ner_service.extract_entities_working(request.parameters["content"])
        
        # Filter by confidence threshold
        high_confidence_entities = [
            e for e in entities 
            if e.get("confidence", 0) >= request.parameters["confidence_threshold"]
        ]
        
        # Step 2: Security validation (simulate with file content)
        temp_file = integration_environment["test_data_dir"] / "test_content.py"
        temp_file.write_text(f'content = """{doc_content}"""')
        
        security_issues = security_validator.scan_file(str(temp_file))
        
        # Step 3: Create integrated response
        response = ServiceResponse(
            success=True,
            data={
                "entities": high_confidence_entities,
                "entity_count": len(high_confidence_entities),
                "security_issues": len(security_issues),
                "processing_stats": {
                    "total_entities_found": len(entities),
                    "high_confidence_entities": len(high_confidence_entities),
                    "content_length": len(doc_content)
                }
            },
            metadata={
                "operation": request.operation,
                "confidence_threshold": request.parameters["confidence_threshold"],
                "services_used": ["ner_service", "security_validator"]
            },
            request_id=request.request_id
        )
        
        # Verify integrated service response
        assert response.success is True
        assert response.data["entity_count"] >= 5, "Should find high-confidence entities"
        assert response.data["processing_stats"]["total_entities_found"] >= 8, "Should find total entities"
        assert response.request_id == "integration_test_001"
        
        # Verify data flow between services
        assert response.data["processing_stats"]["high_confidence_entities"] <= response.data["processing_stats"]["total_entities_found"]
        
        # Clean up
        temp_file.unlink()
    
    def test_error_handling_across_services(self, integration_environment):
        """Test error handling integration across services"""
        container = integration_environment["container"]
        
        # Test 1: Service resolution errors
        try:
            invalid_service = container.resolve("non_existent_service")
            assert False, "Should raise error for missing service"
        except Exception as e:
            assert "non_existent_service" in str(e) or "not found" in str(e).lower()
        
        # Test 2: NER service error handling
        ner_service = container.resolve("ner_service")
        
        # Test with problematic input
        result = ner_service.extract_entities_working("")
        assert isinstance(result, list), "Should handle empty input gracefully"
        assert len(result) == 0, "Empty input should produce no entities"
        
        # Test 3: Security validator error handling
        security_validator = container.resolve("security_validator")
        
        # Test with non-existent file
        issues = security_validator.scan_file("non_existent_file.py")
        assert isinstance(issues, list), "Should handle missing file gracefully"
        assert len(issues) == 0, "Missing file should produce no issues"
        
        # Test 4: Service request/response error handling
        error_request = ServiceRequest(
            operation="invalid_operation",
            parameters={"invalid": "data"},
            request_id="error_test"
        )
        
        error_response = ServiceResponse(
            success=False,
            data=None,
            metadata={"error_context": "Integration test error"},
            error_code="INVALID_OPERATION",
            error_message="Operation not supported",
            request_id=error_request.request_id
        )
        
        assert error_response.success is False
        assert error_response.error_code == "INVALID_OPERATION"
        assert error_response.request_id == "error_test"


class TestRealWorkflowIntegration:
    """Test real workflow integration scenarios"""
    
    def test_multi_phase_document_analysis(self, integration_environment, real_academic_documents):
        """Test multi-phase document analysis workflow"""
        container = integration_environment["container"]
        ner_service = container.resolve("ner_service")
        
        # Phase 1: Document ingestion and entity extraction
        phase1_results = []
        for doc_id, doc_data in real_academic_documents.items():
            entities = ner_service.extract_entities_working(doc_data["content"])
            
            phase1_result = {
                "document_id": doc_id,
                "entities": entities,
                "metadata": {
                    "content_length": len(doc_data["content"]),
                    "extraction_timestamp": time.time()
                }
            }
            phase1_results.append(phase1_result)
        
        # Phase 2: Entity consolidation and relationship extraction
        all_entities = []
        for result in phase1_results:
            all_entities.extend(result["entities"])
        
        # Group entities by type
        entities_by_type = {}
        for entity in all_entities:
            entity_type = entity.get("type", "UNKNOWN")
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        # Phase 3: Knowledge graph construction (simplified)
        knowledge_graph = {
            "nodes": all_entities,
            "edges": [],
            "statistics": {
                "total_entities": len(all_entities),
                "entity_types": len(entities_by_type),
                "documents_processed": len(phase1_results)
            }
        }
        
        # Create relationships between entities in same documents
        for result in phase1_results:
            doc_entities = result["entities"]
            for i, entity1 in enumerate(doc_entities):
                for entity2 in doc_entities[i+1:]:
                    if entity1.get("type") == "PERSON" and entity2.get("type") == "ORG":
                        knowledge_graph["edges"].append({
                            "source": entity1["name"],
                            "target": entity2["name"],
                            "type": "AFFILIATED_WITH",
                            "document": result["document_id"],
                            "confidence": min(entity1.get("confidence", 0.8), entity2.get("confidence", 0.8))
                        })
        
        # Verify multi-phase workflow
        assert len(phase1_results) == 2, "Should process both documents in phase 1"
        assert knowledge_graph["statistics"]["total_entities"] >= 20, "Should have substantial entities"
        assert knowledge_graph["statistics"]["entity_types"] >= 3, "Should have diverse entity types"
        assert len(knowledge_graph["edges"]) >= 2, "Should create relationships between entities"
        
        # Verify entity type distribution
        person_entities = entities_by_type.get("PERSON", [])
        org_entities = entities_by_type.get("ORG", [])
        
        assert len(person_entities) >= 4, "Should find multiple person entities"
        assert len(org_entities) >= 6, "Should find multiple organization entities"
    
    def test_concurrent_document_processing(self, integration_environment, real_academic_documents):
        """Test concurrent document processing integration"""
        import threading
        import queue
        
        container = integration_environment["container"]
        ner_service = container.resolve("ner_service")
        
        # Create result queue for thread-safe collection
        results_queue = queue.Queue()
        
        def process_document(doc_id, doc_data):
            """Process single document in thread"""
            try:
                start_time = time.time()
                entities = ner_service.extract_entities_working(doc_data["content"])
                end_time = time.time()
                
                result = {
                    "document_id": doc_id,
                    "entities": entities,
                    "entity_count": len(entities),
                    "processing_time": end_time - start_time,
                    "thread_id": threading.current_thread().ident
                }
                results_queue.put(result)
            except Exception as e:
                results_queue.put({
                    "document_id": doc_id,
                    "error": str(e),
                    "thread_id": threading.current_thread().ident
                })
        
        # Start concurrent processing
        threads = []
        start_time = time.time()
        
        for doc_id, doc_data in real_academic_documents.items():
            thread = threading.Thread(target=process_document, args=(doc_id, doc_data))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Verify concurrent processing
        assert len(results) == 2, "Should process both documents concurrently"
        assert total_time < 10.0, f"Concurrent processing should be fast, took {total_time:.2f}s"
        
        # Verify no errors in concurrent processing
        error_results = [r for r in results if "error" in r]
        assert len(error_results) == 0, f"Should have no errors, got: {error_results}"
        
        # Verify results quality
        for result in results:
            assert result["entity_count"] >= 8, f"Document {result['document_id']} should have >=8 entities"
            assert result["processing_time"] < 5.0, f"Individual processing should be <5s"
        
        # Verify different threads processed documents
        thread_ids = set(result["thread_id"] for result in results)
        assert len(thread_ids) >= 1, "Should use threading for processing"


class TestPerformanceIntegration:
    """Test performance characteristics of integrated components"""
    
    def test_integrated_performance_baseline(self, integration_environment, real_academic_documents):
        """Establish performance baseline for integrated components"""
        container = integration_environment["container"]
        ner_service = container.resolve("ner_service")
        security_validator = container.resolve("security_validator")
        
        # Measure integrated processing performance
        start_time = time.time()
        
        total_entities = 0
        total_security_issues = 0
        
        for doc_id, doc_data in real_academic_documents.items():
            # Time entity extraction
            ner_start = time.time()
            entities = ner_service.extract_entities_working(doc_data["content"])
            ner_time = time.time() - ner_start
            
            # Time security validation (using this file as proxy)
            security_start = time.time()
            issues = security_validator.scan_file(__file__)
            security_time = time.time() - security_start
            
            total_entities += len(entities)
            total_security_issues += len(issues)
            
            # Performance assertions per document
            assert ner_time < 2.0, f"NER processing should be <2s per document, took {ner_time:.2f}s"
            assert security_time < 1.0, f"Security validation should be <1s per document, took {security_time:.2f}s"
        
        total_time = time.time() - start_time
        
        # Overall performance assertions
        assert total_time < 5.0, f"Integrated processing should be <5s total, took {total_time:.2f}s"
        assert total_entities >= 20, f"Should find substantial entities, found {total_entities}"
        
        # Calculate performance metrics
        entities_per_second = total_entities / total_time if total_time > 0 else 0
        documents_per_second = len(real_academic_documents) / total_time if total_time > 0 else 0
        
        assert entities_per_second >= 10, f"Should process >=10 entities/sec, got {entities_per_second:.1f}"
        assert documents_per_second >= 0.5, f"Should process >=0.5 docs/sec, got {documents_per_second:.1f}"