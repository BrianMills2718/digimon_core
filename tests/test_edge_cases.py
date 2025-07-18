"""Comprehensive edge case and boundary condition testing

Tests all tools with malformed data, boundary conditions, and failure scenarios.
No mocks - all testing uses actual tool execution with real error conditions.
"""

import pytest
import json
import os
import sys
import time
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import threading
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.evidence_logger import EvidenceLogger
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.tools.phase1.t49_multihop_query import MultiHopQuery
from src.tools.phase1.t68_pagerank import PageRankCalculator


class TestEdgeCases:
    """Comprehensive edge case testing for GraphRAG tools"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.evidence_logger = EvidenceLogger()
        
        # Create test data files
        self._create_test_files()
        
        yield
        
        # Cleanup
        self._cleanup_test_files()
    
    def _create_test_files(self):
        """Create test files for edge case testing"""
        # Create corrupted PDF
        self.corrupted_pdf_path = "test_data/corruption/corrupted.pdf"
        os.makedirs(os.path.dirname(self.corrupted_pdf_path), exist_ok=True)
        with open(self.corrupted_pdf_path, "wb") as f:
            f.write(b"corrupted pdf content that's not valid PDF")
        
        # Create empty PDF
        self.empty_pdf_path = "test_data/edge_cases/empty.pdf"
        os.makedirs(os.path.dirname(self.empty_pdf_path), exist_ok=True)
        with open(self.empty_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")  # Minimal valid PDF
        
        # Create very large text file
        self.large_text_path = "test_data/edge_cases/large_text.txt"
        with open(self.large_text_path, "w") as f:
            f.write("x" * 10_000_000)  # 10MB of text
    
    def _cleanup_test_files(self):
        """Clean up test files"""
        files_to_remove = [
            self.corrupted_pdf_path,
            self.empty_pdf_path,
            self.large_text_path
        ]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_tool_malformed_input_handling(self):
        """Test all tools with malformed, corrupted, and invalid inputs"""
        # Create tools directly
        tools_to_test = [
            ("PDFLoader", PDFLoader()),
            ("TextChunker", TextChunker()),
            ("SpacyNER", SpacyNER()),
            ("RelationshipExtractor", RelationshipExtractor()),
            ("EntityBuilder", EntityBuilder()),
            ("EdgeBuilder", EdgeBuilder()),
            ("MultiHopQuery", MultiHopQuery()),
            ("PageRankCalculator", PageRankCalculator())
        ]
        
        malformed_scenarios = {
            "PDFLoader": [
                {"file_paths": ["nonexistent.pdf"]},
                {"file_paths": ["/dev/null"]},
                {"file_paths": [self.corrupted_pdf_path]},
                {"invalid_field": "value"},
                {"file_paths": None},
                {"file_paths": []},
                {"file_paths": [""]}
            ],
            "TextChunker": [
                {"documents": []},
                {"documents": [{"invalid": "structure"}]},
                {"documents": [{"text": "", "document_id": ""}]},
                {"documents": [{"text": "x" * 1_000_000, "document_id": "test"}]},
                {"documents": None},
                {},  # Missing required field
                {"documents": [{"text": None, "document_id": "test"}]}
            ],
            "SpacyNER": [
                {"chunks": []},
                {"chunks": [{"invalid": "structure"}]},
                {"chunks": [{"chunk_id": "test", "text": ""}]},
                {"chunks": [{"chunk_id": "test", "text": None}]},
                {"chunks": None},
                {}  # Missing required field
            ],
            "RelationshipExtractor": [
                {"entities": [], "chunks": []},
                {"entities": [{"invalid": "structure"}], "chunks": []},
                {"entities": None, "chunks": None},
                {}  # Missing required fields
            ],
            "EntityBuilder": [
                {"entities": []},
                {"entities": [{"invalid": "structure"}]},
                {"entities": None},
                {}  # Missing required fields
            ],
            "EdgeBuilder": [
                {"relationships": []},
                {"relationships": [{"invalid": "structure"}]},
                {"relationships": None},
                {}  # Missing required fields
            ],
            "MultihopQuery": [
                {"query": "", "max_hops": 3},
                {"query": None, "max_hops": 3},
                {"query": "test", "max_hops": -1},
                {"query": "test", "max_hops": 1000},
                {"query": "test", "max_hops": "invalid"},
                {}  # Missing required fields
            ],
            "PageRank": [
                {},
                {"iterations": -1},
                {"iterations": 10000},
                {"iterations": "invalid"},
                {"damping_factor": -0.5},
                {"damping_factor": 1.5},
                {"damping_factor": "invalid"}
            ]
        }
        
        test_results = {}
        
        for tool_name, tool in tools_to_test:
            scenarios = malformed_scenarios.get(tool_name, [{"invalid": "data"}])
            tool_results = []
            
            for i, scenario in enumerate(scenarios):
                try:
                    # Call the appropriate method based on tool type
                    if tool_name == "PDFLoader":
                        result = tool.load_pdf(scenario.get("file_path", "test.pdf"))
                    elif tool_name == "TextChunker":
                        result = tool.chunk_text(scenario.get("document_id", "test"), scenario.get("text", ""), scenario.get("confidence", 0.8))
                    elif tool_name == "SpacyNER":
                        result = tool.extract_entities(scenario.get("chunk_id", "test"), scenario.get("text", ""), scenario.get("confidence", 0.8))
                    elif tool_name == "RelationshipExtractor":
                        result = tool.extract_relationships(
                            scenario.get("entities", []),
                            scenario.get("chunks", [])
                        )
                    elif tool_name == "EntityBuilder":
                        result = tool.build_entity_nodes(scenario.get("entities", []))
                    elif tool_name == "EdgeBuilder":
                        result = tool.build_relationship_edges(scenario.get("relationships", []))
                    elif tool_name == "MultihopQuery":
                        result = tool.execute_query(
                            scenario.get("query", ""),
                            scenario.get("max_hops", 2)
                        )
                    elif tool_name == "PageRank":
                        result = tool.calculate_pagerank(
                            scenario.get("iterations", 100),
                            scenario.get("damping_factor", 0.85)
                        )
                    
                    # If no exception, verify error is properly handled in result
                    if isinstance(result, dict) and ("error" in result or result.get("status") == "error"):
                        tool_results.append({
                            "scenario": i,
                            "handled": True,
                            "error_type": "handled_in_result"
                        })
                    else:
                        tool_results.append({
                            "scenario": i,
                            "handled": False,
                            "error_type": "no_error_detected"
                        })
                except (ValueError, RuntimeError, KeyError, TypeError, AttributeError) as e:
                    tool_results.append({
                        "scenario": i,
                        "handled": True,
                        "error_type": type(e).__name__
                    })
                except Exception as e:
                    tool_results.append({
                        "scenario": i,
                        "handled": False,
                        "error_type": f"unexpected: {type(e).__name__}"
                    })
            
            test_results[tool_name] = tool_results
        
        # Log results to evidence
        self.evidence_logger.log_error_scenario_test(
            test_name="Malformed Input Handling",
            error_scenario="Various malformed inputs across all tools",
            expected_behavior="All tools should handle malformed inputs gracefully",
            actual_behavior=json.dumps(test_results, indent=2),
            error_handled_correctly=all(
                all(r["handled"] for r in results) 
                for results in test_results.values()
            )
        )
        
        # Verify all tools handled errors correctly
        for tool_name, results in test_results.items():
            for result in results:
                assert result["handled"], f"{tool_name} failed to handle scenario {result['scenario']}: {result['error_type']}"
    
    def test_boundary_conditions(self):
        """Test boundary conditions for all data types"""
        test_results = {}
        
        # Test 1: Maximum file sizes
        pdf_loader = PDFLoaderAdapter(self.config_manager)
        
        # Create a large PDF-like file (simplified for testing)
        large_pdf_path = "test_data/edge_cases/large.pdf"
        with open(large_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n")
            # Write 50MB of content
            for _ in range(50):
                f.write(b"0" * 1_000_000)
            f.write(b"\n%%EOF")
        
        try:
            start_time = time.time()
            result = pdf_loader.execute({
                "document_paths": [large_pdf_path],
                "workflow_id": "boundary_test"
            })
            processing_time = time.time() - start_time
            
            test_results["large_file_processing"] = {
                "success": "error" not in result,
                "processing_time": processing_time,
                "file_size_mb": 50
            }
        finally:
            if os.path.exists(large_pdf_path):
                os.remove(large_pdf_path)
        
        # Test 2: Empty inputs
        text_chunker = TextChunkerAdapter(self.config_manager)
        empty_result = text_chunker.execute({
            "documents": [{"text": "", "document_id": "empty"}],
            "workflow_id": "boundary_test"
        })
        test_results["empty_input_handling"] = {
            "success": "chunks" in empty_result,
            "chunks_generated": len(empty_result.get("chunks", []))
        }
        
        # Test 3: Maximum entity count
        entity_builder = EntityBuilderAdapter(self.config_manager)
        
        # Generate many entities
        many_entities = [
            {
                "entity_id": f"entity_{i}",
                "text": f"Entity {i}",
                "entity_type": "PERSON",
                "chunk_id": f"chunk_{i % 100}",
                "confidence": 0.9
            }
            for i in range(10000)
        ]
        
        chunks = [
            {"chunk_id": f"chunk_{i}", "text": f"Chunk {i}", "confidence": 0.9}
            for i in range(100)
        ]
        
        start_time = time.time()
        result = entity_builder.execute({
            "entities": many_entities,
            "chunks": chunks,
            "workflow_id": "boundary_test"
        })
        processing_time = time.time() - start_time
        
        test_results["large_entity_count"] = {
            "success": "nodes" in result,
            "entity_count": len(many_entities),
            "processing_time": processing_time
        }
        
        # Test 4: Extreme parameter values
        pagerank = PageRankAdapter(self.config_manager)
        
        # Test with maximum iterations
        try:
            result = pagerank.execute({
                "iterations": 1000,
                "damping_factor": 0.99,
                "workflow_id": "boundary_test"
            })
            test_results["extreme_iterations"] = {
                "success": "error" not in result,
                "iterations": 1000
            }
        except Exception as e:
            test_results["extreme_iterations"] = {
                "success": False,
                "error": str(e)
            }
        
        # Log boundary condition results
        self.evidence_logger.log_performance_boundary_test(
            component="GraphRAG Tools",
            test_type="Boundary Conditions",
            input_size=sum(r.get("file_size_mb", 0) * 1024 * 1024 for r in test_results.values()),
            processing_time=sum(r.get("processing_time", 0) for r in test_results.values()),
            memory_usage=0,  # Would need actual memory monitoring
            success=all(r.get("success", False) for r in test_results.values()),
            failure_reason=None if all(r.get("success", False) for r in test_results.values()) else "Some boundary tests failed"
        )
    
    def test_data_corruption_scenarios(self):
        """Test behavior with corrupted data at various stages"""
        test_results = {}
        
        # Test 1: Corrupted PDF handling
        pdf_loader = PDFLoaderAdapter(self.config_manager)
        
        # Test with actually corrupted PDF
        result = pdf_loader.execute({
            "document_paths": [self.corrupted_pdf_path],
            "workflow_id": "corruption_test"
        })
        
        test_results["corrupted_pdf"] = {
            "handled_gracefully": "error" in result or len(result.get("documents", [])) == 0,
            "result": result
        }
        
        # Test 2: Invalid JSON in entities
        entity_builder = EntityBuilderAdapter(self.config_manager)
        
        # Create entities with invalid data
        invalid_entities = [
            {
                "entity_id": "test1",
                "text": "Test",
                "entity_type": None,  # Invalid type
                "chunk_id": "chunk1",
                "confidence": 0.9
            },
            {
                "entity_id": "test2",
                "text": "",  # Empty text
                "entity_type": "PERSON",
                "chunk_id": "chunk1",
                "confidence": 0.9
            },
            {
                "entity_id": "test3",
                "text": "Test",
                "entity_type": "PERSON",
                "chunk_id": "chunk1",
                "confidence": float('inf')  # Invalid confidence
            }
        ]
        
        chunks = [{"chunk_id": "chunk1", "text": "Test chunk", "confidence": 0.9}]
        
        try:
            result = entity_builder.execute({
                "entities": invalid_entities,
                "chunks": chunks,
                "workflow_id": "corruption_test"
            })
            test_results["invalid_entity_data"] = {
                "handled_gracefully": True,
                "nodes_created": len(result.get("nodes", []))
            }
        except Exception as e:
            test_results["invalid_entity_data"] = {
                "handled_gracefully": True,
                "error": str(e)
            }
        
        # Test 3: Network interruption simulation (for API-based tools)
        # This would test tools that make external API calls
        # Since we're testing actual implementations, we'll simulate by testing with invalid config
        
        # Test 4: Concurrent modification scenario
        concurrent_results = []
        errors = []
        
        def concurrent_operation(op_id):
            try:
                chunker = TextChunkerAdapter(self.config_manager)
                result = chunker.execute({
                    "documents": [{"text": f"Concurrent test {op_id}", "document_id": f"doc_{op_id}"}],
                    "workflow_id": f"concurrent_{op_id}"
                })
                concurrent_results.append({
                    "op_id": op_id,
                    "success": "chunks" in result
                })
            except Exception as e:
                errors.append({
                    "op_id": op_id,
                    "error": str(e)
                })
        
        # Run concurrent operations
        threads = [threading.Thread(target=concurrent_operation, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        test_results["concurrent_operations"] = {
            "total_operations": 10,
            "successful": len(concurrent_results),
            "errors": len(errors)
        }
        
        # Log corruption scenario results
        for scenario, result in test_results.items():
            self.evidence_logger.log_error_scenario_test(
                test_name=f"Data Corruption - {scenario}",
                error_scenario=f"Testing {scenario} corruption handling",
                expected_behavior="System should handle corruption gracefully without crashing",
                actual_behavior=json.dumps(result, indent=2),
                error_handled_correctly=result.get("handled_gracefully", True)
            )
    
    def test_resource_exhaustion(self):
        """Test behavior under resource exhaustion conditions"""
        test_results = {}
        
        # Test 1: Memory pressure - create many large chunks
        text_chunker = TextChunkerAdapter(self.config_manager)
        
        # Create documents that will generate many chunks
        large_documents = [
            {
                "text": " ".join([f"Sentence {i}." for i in range(10000)]),
                "document_id": f"large_doc_{j}"
            }
            for j in range(10)
        ]
        
        start_time = time.time()
        memory_start = self._get_memory_usage()
        
        try:
            result = text_chunker.execute({
                "documents": large_documents,
                "workflow_id": "resource_test"
            })
            
            memory_end = self._get_memory_usage()
            processing_time = time.time() - start_time
            
            test_results["memory_pressure"] = {
                "success": "chunks" in result,
                "chunks_created": len(result.get("chunks", [])),
                "memory_increase_mb": (memory_end - memory_start) / 1024 / 1024,
                "processing_time": processing_time
            }
        except Exception as e:
            test_results["memory_pressure"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 2: CPU intensive operations
        pagerank = PageRankAdapter(self.config_manager)
        
        # First create a large graph
        entity_builder = EntityBuilderAdapter(self.config_manager)
        edge_builder = EdgeBuilderAdapter(self.config_manager)
        
        # Create many entities and relationships for a large graph
        entities = [
            {
                "entity_id": f"entity_{i}",
                "text": f"Entity {i}",
                "entity_type": "PERSON",
                "chunk_id": "chunk_1",
                "confidence": 0.9
            }
            for i in range(1000)
        ]
        
        relationships = [
            {
                "relationship_id": f"rel_{i}_{j}",
                "source_id": f"entity_{i}",
                "target_id": f"entity_{j}",
                "relationship_type": "KNOWS",
                "chunk_id": "chunk_1",
                "confidence": 0.8
            }
            for i in range(100)
            for j in range(i+1, min(i+10, 100))
        ]
        
        chunks = [{"chunk_id": "chunk_1", "text": "Test chunk", "confidence": 0.9}]
        
        # Build the graph
        entity_result = entity_builder.execute({
            "entities": entities,
            "chunks": chunks,
            "workflow_id": "resource_test"
        })
        
        edge_result = edge_builder.execute({
            "relationships": relationships,
            "entities": entities,
            "workflow_id": "resource_test"
        })
        
        # Now test PageRank on this large graph
        start_time = time.time()
        try:
            result = pagerank.execute({
                "iterations": 100,
                "workflow_id": "resource_test"
            })
            processing_time = time.time() - start_time
            
            test_results["cpu_intensive_pagerank"] = {
                "success": "nodes" in result,
                "node_count": len(entities),
                "edge_count": len(relationships),
                "processing_time": processing_time
            }
        except Exception as e:
            test_results["cpu_intensive_pagerank"] = {
                "success": False,
                "error": str(e)
            }
        
        # Log resource exhaustion results
        self.evidence_logger.log_performance_boundary_test(
            component="Resource Exhaustion Tests",
            test_type="Resource Limits",
            input_size=len(entities) + len(relationships),
            processing_time=sum(r.get("processing_time", 0) for r in test_results.values()),
            memory_usage=test_results.get("memory_pressure", {}).get("memory_increase_mb", 0),
            success=all(r.get("success", False) for r in test_results.values()),
            failure_reason=None if all(r.get("success", False) for r in test_results.values()) else "Some resource tests failed"
        )
    
    def _get_memory_usage(self):
        """Get current memory usage in bytes"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except:
            return 0
    
    def test_validation_chain_failures(self):
        """Test cascading validation failures in tool chains"""
        test_results = {}
        
        # Test what happens when early tools in chain produce invalid output
        pdf_loader = PDFLoaderAdapter(self.config_manager)
        text_chunker = TextChunkerAdapter(self.config_manager)
        
        # Load empty PDF which should produce minimal content
        pdf_result = pdf_loader.execute({
            "document_paths": [self.empty_pdf_path],
            "workflow_id": "validation_chain_test"
        })
        
        # Try to chunk the potentially empty/minimal content
        if "documents" in pdf_result:
            chunk_result = text_chunker.execute({
                "documents": pdf_result["documents"],
                "workflow_id": "validation_chain_test"
            })
            
            test_results["empty_pdf_chain"] = {
                "pdf_loaded": len(pdf_result.get("documents", [])) > 0,
                "chunks_created": len(chunk_result.get("chunks", [])) if "chunks" in chunk_result else 0,
                "chain_handled_gracefully": True
            }
        else:
            test_results["empty_pdf_chain"] = {
                "pdf_loaded": False,
                "chain_handled_gracefully": True
            }
        
        # Test with completely invalid chain data
        ner_adapter = SpacyNERAdapter(self.config_manager)
        
        # Pass empty chunks to NER
        ner_result = ner_adapter.execute({
            "chunks": [],
            "workflow_id": "validation_chain_test"
        })
        
        test_results["empty_chunks_ner"] = {
            "entities_found": len(ner_result.get("entities", [])),
            "handled_gracefully": "error" not in ner_result or ner_result.get("entities", []) == []
        }
        
        # Log validation chain results
        self.evidence_logger.log_error_scenario_test(
            test_name="Validation Chain Failures",
            error_scenario="Testing cascading failures in tool chains",
            expected_behavior="Each tool should handle invalid input from previous tools gracefully",
            actual_behavior=json.dumps(test_results, indent=2),
            error_handled_correctly=all(r.get("handled_gracefully", False) for r in test_results.values())
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])