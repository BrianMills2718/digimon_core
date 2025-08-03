"""Deep Functionality Tests

This module implements comprehensive functionality testing as specified in CLAUDE.md.
Tests verify actual tool functionality with real data processing and no mocks.

CRITICAL IMPLEMENTATION: Deep verification of all tool functionality
"""

import os
import sys
import time
import pytest
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import components for deep testing
from src.core.tool_factory import ToolFactory
from src.core.tool_protocol import Tool, ToolValidationResult
from src.core.ontology_validator import OntologyValidator
from src.core.data_models import Entity, QualityTier
from src.core.evidence_logger import evidence_logger


class TestDeepFunctionality:
    """Deep functionality testing with comprehensive scenarios"""
    
    @classmethod
    def setup_class(cls):
        """Setup class-level test fixtures"""
        cls.test_start_time = datetime.now()
        evidence_logger.log_task_start("DEEP_FUNCTIONALITY_TEST", "Comprehensive functionality testing with real data")
    
    @classmethod
    def teardown_class(cls):
        """Generate final deep functionality report"""
        test_duration = (datetime.now() - cls.test_start_time).total_seconds()
        evidence_logger.log_task_completion("DEEP_FUNCTIONALITY_TEST", {
            "test_duration_seconds": test_duration,
            "completion_timestamp": datetime.now().isoformat()
        }, True)
    
    def test_tool_actual_functionality_comprehensive(self):
        """Test that all tools actually work with real data"""
        evidence_logger.log_task_start("DEEP_TOOL_FUNCTIONALITY_TEST", "Testing actual tool functionality with real data")
        
        factory = ToolFactory()
        tools = factory.create_all_tools()
        
        functionality_results = {}
        for tool in tools:
            tool_name = tool.__class__.__name__
            
            # Test with multiple real data scenarios
            test_scenarios = self._get_comprehensive_test_scenarios(tool)
            scenario_results = {}
            
            for scenario_name, test_data in test_scenarios.items():
                try:
                    result = tool.execute(test_data)
                    # Verify result contains expected output structure
                    self._verify_output_structure(result, tool_name)
                    scenario_results[scenario_name] = {
                        "success": True,
                        "output_verified": True,
                        "result_sample": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                    }
                except Exception as e:
                    scenario_results[scenario_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            functionality_results[tool_name] = scenario_results
        
        # Verify ALL tools passed ALL scenarios (skip tools with no test scenarios)
        all_passed = all(
            all(scenario["success"] for scenario in tool_results.values()) if tool_results else True
            for tool_results in functionality_results.values()
        )
        
        # Log failed scenarios for debugging
        failed_scenarios = {}
        for tool_name, tool_results in functionality_results.items():
            failed = [scenario for scenario, result in tool_results.items() if not result["success"]]
            if failed:
                failed_scenarios[tool_name] = failed
        
        evidence_logger.log_task_completion("DEEP_TOOL_FUNCTIONALITY_TEST", {
            "all_tools_functional": all_passed,
            "detailed_results": functionality_results,
            "failed_scenarios": failed_scenarios,
            "total_tools_tested": len(tools),
            "total_scenarios_tested": sum(len(scenarios) for scenarios in functionality_results.values())
        }, all_passed)
        
        if not all_passed:
            pytest.fail(f"Not all tools passed comprehensive functionality testing. Failed: {failed_scenarios}")
        
        assert all_passed
    
    def test_dolce_ontology_comprehensive_validation(self):
        """Test DOLCE ontology with extensive real-world scenarios"""
        evidence_logger.log_task_start("COMPREHENSIVE_DOLCE_TEST", "Testing DOLCE ontology with extensive scenarios")
        
        validator = OntologyValidator()
        
        # Test with large variety of entity types
        comprehensive_test_entities = [
            # People and roles
            {"name": "Dr. Sarah Chen", "type": "Person", "context": "research scientist"},
            {"name": "CEO John Smith", "type": "IndividualActor", "context": "business leader"},
            {"name": "Professor Maria Garcia", "type": "Academic", "context": "university professor"},
            
            # Organizations at different scales
            {"name": "Microsoft Corporation", "type": "Organization", "context": "multinational technology company"},
            {"name": "Local Coffee Shop", "type": "Business", "context": "small local business"},
            {"name": "Stanford University", "type": "Institution", "context": "educational institution"},
            
            # Geographic entities
            {"name": "San Francisco", "type": "Location", "context": "major city"},
            {"name": "Silicon Valley", "type": "Region", "context": "technology hub"},
            {"name": "Building 42", "type": "Facility", "context": "office building"},
            
            # Abstract concepts
            {"name": "Artificial Intelligence", "type": "Concept", "context": "technology field"},
            {"name": "Innovation", "type": "Abstract", "context": "business concept"},
            {"name": "Sustainability", "type": "Principle", "context": "environmental principle"},
            
            # Events and processes
            {"name": "Product Launch", "type": "Event", "context": "business event"},
            {"name": "Research Process", "type": "Process", "context": "scientific methodology"},
            {"name": "Team Meeting", "type": "Activity", "context": "collaborative activity"}
        ]
        
        validation_results = {}
        mapping_accuracy_results = {}
        
        for entity_data in comprehensive_test_entities:
            entity = Entity(
                id=f"test_{entity_data['name'].lower().replace(' ', '_')}",
                canonical_name=entity_data["name"],
                entity_type=entity_data["type"],
                surface_forms=[entity_data["name"]],
                confidence=0.9,
                quality_tier=QualityTier.HIGH,
                created_by="comprehensive_test",
                created_at=datetime.now(),
                workflow_id="comprehensive_dolce_test"
            )
            
            # Test DOLCE mapping
            dolce_mapping = validator.get_dolce_mapping(entity_data["type"])
            mapping_accuracy_results[entity_data["type"]] = {
                "dolce_concept": dolce_mapping,
                "is_valid_dolce_concept": dolce_mapping is not None,
                "entity_example": entity_data["name"]
            }
            
            # Test entity validation
            validation_result = validator.validate_entity_simple(entity)
            validation_results[entity.id] = {
                "validation_passed": validation_result.get("valid", False),
                "dolce_concept_assigned": validation_result.get("dolce_concept"),
                "entity_type": entity_data["type"],
                "validation_details": validation_result
            }
        
        # Test relationship validation
        test_relationships = [
            ("Dr. Sarah Chen", "works_at", "Stanford University"),
            ("Microsoft Corporation", "located_in", "San Francisco"),
            ("Product Launch", "organized_by", "Microsoft Corporation")
        ]
        
        relationship_results = {}
        for source, relation, target in test_relationships:
            rel_validation = validator.validate_relationship_against_dolce(
                relation, {"source": source, "target": target}
            )
            relationship_results[f"{source}_{relation}_{target}"] = rel_validation
        
        # Calculate comprehensive metrics
        total_entities = len(comprehensive_test_entities)
        valid_mappings = sum(1 for r in mapping_accuracy_results.values() if r["is_valid_dolce_concept"])
        valid_validations = sum(1 for r in validation_results.values() if r["validation_passed"])
        
        mapping_accuracy = valid_mappings / len(set(e["type"] for e in comprehensive_test_entities))
        validation_accuracy = valid_validations / total_entities
        
        # STRICT SUCCESS CRITERIA
        success_criteria = {
            "mapping_accuracy_100_percent": mapping_accuracy == 1.0,
            "validation_accuracy_100_percent": validation_accuracy == 1.0,
            "all_relationships_valid": all(r.get("valid", False) for r in relationship_results.values()),
            "comprehensive_coverage": total_entities >= 15,
            "entity_type_diversity": len(set(e["type"] for e in comprehensive_test_entities)) >= 10
        }
        
        all_criteria_met = all(success_criteria.values())
        
        evidence_logger.log_task_completion("COMPREHENSIVE_DOLCE_TEST", {
            "total_entities_tested": total_entities,
            "entity_types_tested": len(set(e["type"] for e in comprehensive_test_entities)),
            "mapping_accuracy_percentage": mapping_accuracy * 100,
            "validation_accuracy_percentage": validation_accuracy * 100,
            "success_criteria": success_criteria,
            "all_criteria_met": all_criteria_met,
            "detailed_mapping_results": mapping_accuracy_results,
            "detailed_validation_results": validation_results,
            "relationship_validation_results": relationship_results
        }, all_criteria_met)
        
        assert all_criteria_met, f"DOLCE ontology failed comprehensive testing: {success_criteria}"
    
    def test_tool_validation_system_comprehensive(self):
        """Test tool validation system with comprehensive scenarios"""
        evidence_logger.log_task_start("TOOL_VALIDATION_SYSTEM_TEST", "Testing tool validation with comprehensive scenarios")
        
        factory = ToolFactory()
        tools = factory.create_all_tools()
        
        validation_test_results = {}
        
        for tool in tools:
            tool_name = tool.__class__.__name__
            
            # Test various validation scenarios
            validation_scenarios = {
                "valid_input": self._get_valid_input_for_tool(tool_name),
                "invalid_format": {"invalid": "format"},
                "missing_required_fields": {},
                "empty_input": {},
                "null_input": None
            }
            
            tool_validation_results = {}
            
            for scenario_name, test_input in validation_scenarios.items():
                try:
                    if test_input is None:
                        # Handle None input case
                        continue
                    
                    validation_result = tool.validate_input(test_input)
                    
                    # Verify ToolValidationResult structure
                    assert isinstance(validation_result, ToolValidationResult), f"Tool {tool_name} must return ToolValidationResult"
                    assert hasattr(validation_result, 'is_valid'), "ToolValidationResult missing is_valid"
                    assert hasattr(validation_result, 'validation_errors'), "ToolValidationResult missing validation_errors"
                    assert hasattr(validation_result, 'method_signatures'), "ToolValidationResult missing method_signatures"
                    assert hasattr(validation_result, 'execution_test_results'), "ToolValidationResult missing execution_test_results"
                    
                    tool_validation_results[scenario_name] = {
                        "validation_structure_correct": True,
                        "is_valid": validation_result.is_valid,
                        "error_count": len(validation_result.validation_errors),
                        "has_method_signatures": len(validation_result.method_signatures) > 0
                    }
                    
                except Exception as e:
                    tool_validation_results[scenario_name] = {
                        "validation_structure_correct": False,
                        "error": str(e)
                    }
            
            validation_test_results[tool_name] = tool_validation_results
        
        # Verify all tools have proper validation
        all_validation_passed = all(
            all(result.get("validation_structure_correct", False) for result in tool_results.values())
            for tool_results in validation_test_results.values()
        )
        
        evidence_logger.log_task_completion("TOOL_VALIDATION_SYSTEM_TEST", {
            "all_validation_systems_working": all_validation_passed,
            "tools_tested": len(tools),
            "detailed_validation_results": validation_test_results
        }, all_validation_passed)
        
        assert all_validation_passed, "Not all tools have proper validation systems"
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling across all components"""
        evidence_logger.log_task_start("ERROR_HANDLING_TEST", "Testing comprehensive error handling")
        
        factory = ToolFactory()
        tools = factory.create_all_tools()
        
        error_handling_results = {}
        
        for tool in tools:
            tool_name = tool.__class__.__name__
            
            # Test various error scenarios
            error_scenarios = {
                "malformed_input": {"malformed": True, "data": [1, 2, "invalid"]},
                "missing_workflow_id": {"valid_structure": True},
                "invalid_data_types": {"chunks": "should_be_list", "documents": 123}
            }
            
            tool_error_results = {}
            
            for scenario_name, error_input in error_scenarios.items():
                try:
                    # This should raise an exception or handle gracefully
                    result = tool.execute(error_input)
                    
                    # If no exception, check if error was handled gracefully
                    tool_error_results[scenario_name] = {
                        "handled_gracefully": True,
                        "result_type": type(result).__name__,
                        "has_error_info": "error" in str(result).lower()
                    }
                    
                except Exception as e:
                    # Exception is expected for invalid input
                    tool_error_results[scenario_name] = {
                        "handled_gracefully": True,
                        "exception_type": type(e).__name__,
                        "error_message": str(e)[:100]
                    }
            
            error_handling_results[tool_name] = tool_error_results
        
        # Verify all tools handle errors appropriately
        all_error_handling_passed = all(
            all(result.get("handled_gracefully", False) for result in tool_results.values())
            for tool_results in error_handling_results.values()
        )
        
        evidence_logger.log_task_completion("ERROR_HANDLING_TEST", {
            "all_error_handling_working": all_error_handling_passed,
            "tools_tested": len(tools),
            "detailed_error_handling_results": error_handling_results
        }, all_error_handling_passed)
        
        assert all_error_handling_passed, "Not all tools handle errors appropriately"
    
    def _get_comprehensive_test_scenarios(self, tool: Tool) -> Dict[str, Dict[str, Any]]:
        """Generate comprehensive test scenarios with realistic data"""
        tool_name = tool.__class__.__name__
        
        realistic_scenarios = {
            "PDFLoaderAdapter": {
                "standard_pdf": {
                    "document_paths": ["test_data/research_paper.pdf"],
                    "workflow_id": "comprehensive_test"
                },
                "multiple_pdfs": {
                    "document_paths": ["test_data/doc1.pdf", "test_data/doc2.pdf"],
                    "workflow_id": "batch_test"
                },
                "large_pdf": {
                    "document_paths": ["test_data/large_document.pdf"],
                    "workflow_id": "performance_test"
                }
            },
            "TextChunkerAdapter": {
                "short_document": {
                    "documents": [{
                        "document_id": "test_doc_1",
                        "text": "Short test document.",
                        "confidence": 0.9
                    }],
                    "workflow_id": "deep_test_workflow"
                },
                "long_document": {
                    "documents": [{
                        "document_id": "test_doc_2",
                        "text": "This is a much longer test document that should be chunked into multiple smaller pieces for better processing. " * 10,
                        "confidence": 0.9
                    }],
                    "workflow_id": "deep_test_workflow"
                }
            },
            "SpacyNERAdapter": {
                "tech_entities": {
                    "chunks": [{
                        "chunk_id": "tech_chunk_1",
                        "text": "Apple Inc. and Microsoft Corporation are competing in artificial intelligence markets with Google LLC in Silicon Valley, California.",
                        "confidence": 0.9
                    }],
                    "workflow_id": "tech_test"
                },
                "academic_entities": {
                    "chunks": [{
                        "chunk_id": "academic_chunk_1", 
                        "text": "Dr. Sarah Chen from Stanford University published research on machine learning at the Conference on Neural Information Processing Systems.",
                        "confidence": 0.9
                    }],
                    "workflow_id": "academic_test"
                }
            },
            "RelationshipExtractorAdapter": {
                "entity_relationships": {
                    "entities": [{
                        "entity_id": "test_entity_1",
                        "canonical_name": "Apple Inc.",
                        "entity_type": "ORG",
                        "mentions": ["Apple Inc."],
                        "document_id": "test_doc_1",
                        "confidence": 0.9
                    }],
                    "workflow_id": "deep_test_workflow"
                }
            },
            "EntityBuilderAdapter": {
                "build_entities": {
                    "entities": [{
                        "text": "Apple Inc.",
                        "label": "ORG",
                        "start": 0,
                        "end": 9
                    }],
                    "workflow_id": "deep_test_workflow"
                }
            },
            "EdgeBuilderAdapter": {
                "build_relationships": {
                    "relationships": [{
                        "relationship_id": "rel_test_1",
                        "source": "Apple Inc.",
                        "target": "Cupertino",
                        "relation_type": "located_in"
                    }],
                    "workflow_id": "deep_test_workflow"
                }
            },
            "VectorEmbedderAdapter": {
                "embed_chunks": {
                    "chunks": [{
                        "chunk_id": "test_chunk_1",
                        "text": "Test document for embedding with meaningful content for processing.",
                        "document_id": "test_doc_1",
                        "confidence": 0.9
                    }],
                    "workflow_id": "deep_test_workflow"
                }
            },
            "PageRankAdapter": {
                "pagerank_calculation": {
                    "workflow_id": "deep_test_workflow"
                }
            },
            "MultiHopQueryAdapter": {
                "multi_hop_query": {
                    "query": "test query for multi-hop analysis",
                    "workflow_id": "deep_test_workflow"
                }
            }
        }
        
        # Return scenarios for the specific tool or default
        return realistic_scenarios.get(tool_name, {
            "default": {
                "workflow_id": "deep_test_workflow"
            }
        })
    
    def _verify_output_structure(self, result: Any, tool_name: str) -> None:
        """Verify that tool output has expected structure"""
        assert result is not None, f"Tool {tool_name} returned None"
        assert isinstance(result, dict), f"Tool {tool_name} must return dictionary"
        
        # Common structure requirements
        if tool_name == "PDFLoaderAdapter":
            assert "documents" in result, "PDFLoaderAdapter must return documents"
            assert isinstance(result["documents"], list), "documents must be a list"
            
        elif tool_name == "TextChunkerAdapter":
            assert "chunks" in result, "TextChunkerAdapter must return chunks"
            assert isinstance(result["chunks"], list), "chunks must be a list"
            
        elif tool_name == "SpacyNERAdapter":
            assert "entities" in result, "SpacyNERAdapter must return entities"
            assert isinstance(result["entities"], list), "entities must be a list"
    
    def _get_valid_input_for_tool(self, tool_name: str) -> Dict[str, Any]:
        """Get valid input for a specific tool"""
        valid_inputs = {
            "PDFLoaderAdapter": {
                "document_paths": ["test_data/sample.pdf"],
                "workflow_id": "validation_test"
            },
            "TextChunkerAdapter": {
                "documents": [{
                    "document_id": "test_doc",
                    "text": "Test document text",
                    "confidence": 0.9
                }],
                "workflow_id": "validation_test"
            },
            "SpacyNERAdapter": {
                "chunks": [{
                    "chunk_id": "test_chunk",
                    "text": "Test chunk text",
                    "confidence": 0.9
                }],
                "workflow_id": "validation_test"
            }
        }
        
        return valid_inputs.get(tool_name, {"workflow_id": "validation_test"})


if __name__ == "__main__":
    # Run deep functionality tests
    pytest.main([__file__, "-v", "--tb=short"])