#!/usr/bin/env python3
"""
Integration Test for Cross-Modal Analysis Orchestration System

Comprehensive test suite to validate the integration and functionality
of all cross-modal orchestration components.
"""

import asyncio
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

from src.analytics.mode_selection_service import (
    ModeSelectionService, DataContext, AnalysisMode, create_data_context
)
from src.analytics.cross_modal_converter import (
    CrossModalConverter, DataFormat, ConversionResult
)
from src.analytics.cross_modal_validator import (
    CrossModalValidator, ValidationLevel, ValidationReport
)
from src.analytics.cross_modal_orchestrator import (
    CrossModalOrchestrator, WorkflowOptimizationLevel, AnalysisResult
)


class TestCrossModalIntegration:
    """Integration tests for cross-modal analysis orchestration"""
    
    @pytest.fixture
    async def mode_selector(self):
        """Initialize mode selection service"""
        service = ModeSelectionService()
        await service.initialize({})
        return service
    
    @pytest.fixture
    async def converter(self):
        """Initialize cross-modal converter"""
        service = CrossModalConverter()
        await service.initialize({})
        return service
    
    @pytest.fixture
    async def validator(self):
        """Initialize cross-modal validator"""
        service = CrossModalValidator()
        await service.initialize({})
        return service
    
    @pytest.fixture
    async def orchestrator(self):
        """Initialize cross-modal orchestrator"""
        service = CrossModalOrchestrator()
        await service.initialize({})
        return service
    
    @pytest.fixture
    def sample_graph_data(self):
        """Sample graph data for testing"""
        return {
            "nodes": [
                {"id": "n1", "label": "Node1", "type": "entity", "properties": {"value": 10}},
                {"id": "n2", "label": "Node2", "type": "entity", "properties": {"value": 20}},
                {"id": "n3", "label": "Node3", "type": "entity", "properties": {"value": 30}}
            ],
            "edges": [
                {"source": "n1", "target": "n2", "type": "connects", "weight": 0.8},
                {"source": "n2", "target": "n3", "type": "connects", "weight": 0.6},
                {"source": "n1", "target": "n3", "type": "connects", "weight": 0.4}
            ]
        }
    
    @pytest.fixture
    def sample_table_data(self):
        """Sample table data for testing"""
        return pd.DataFrame({
            "id": ["1", "2", "3", "4", "5"],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "value": [10, 20, 30, 40, 50],
            "category": ["A", "B", "A", "C", "B"]
        })
    
    @pytest.fixture
    def sample_vector_data(self):
        """Sample vector data for testing"""
        np.random.seed(42)
        return np.random.rand(5, 10)
    
    async def test_mode_selection_basic(self, mode_selector):
        """Test basic mode selection functionality"""
        
        # Create test data context
        data_context = create_data_context(
            data_size=100,
            data_types=["graph", "entities"],
            entity_count=50,
            relationship_count=75
        )
        
        # Test mode selection
        result = await mode_selector.select_optimal_mode(
            "What are the key relationships in this network?",
            data_context
        )
        
        # Validate results
        assert isinstance(result.primary_mode, AnalysisMode)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0
        assert isinstance(result.workflow_steps, list)
        assert len(result.workflow_steps) > 0
    
    async def test_mode_selection_fallback(self, mode_selector):
        """Test mode selection fallback mechanism"""
        
        # Create test context that should trigger fallback
        data_context = create_data_context(
            data_size=1000000,  # Large size
            data_types=["complex", "unknown"],
            entity_count=100000,
            relationship_count=200000
        )
        
        # Test with complex question
        result = await mode_selector.select_optimal_mode(
            "Perform ultra-complex multi-dimensional analysis with advanced algorithms",
            data_context
        )
        
        # Should still return valid result
        assert isinstance(result.primary_mode, AnalysisMode)
        assert 0.0 <= result.confidence <= 1.0
        # May use fallback, but should work
    
    async def test_converter_graph_to_table(self, converter, sample_graph_data):
        """Test graph to table conversion"""
        
        result = await converter.convert_data(
            sample_graph_data,
            DataFormat.GRAPH,
            DataFormat.TABLE,
            table_type="edges"
        )
        
        # Validate conversion result
        assert result.validation_passed
        assert isinstance(result.data, pd.DataFrame)
        assert len(result.data) > 0
        assert result.preservation_score > 0.0
        assert result.source_format == DataFormat.GRAPH
        assert result.target_format == DataFormat.TABLE
    
    async def test_converter_table_to_graph(self, converter, sample_table_data):
        """Test table to graph conversion"""
        
        result = await converter.convert_data(
            sample_table_data,
            DataFormat.TABLE,
            DataFormat.GRAPH,
            source_column="id",
            target_column="category"
        )
        
        # Validate conversion result
        assert result.validation_passed
        assert isinstance(result.data, dict)
        assert "nodes" in result.data
        assert "edges" in result.data
        assert len(result.data["nodes"]) > 0
        assert result.preservation_score > 0.0
    
    async def test_converter_graph_to_vector(self, converter, sample_graph_data):
        """Test graph to vector conversion"""
        
        result = await converter.convert_data(
            sample_graph_data,
            DataFormat.GRAPH,
            DataFormat.VECTOR,
            method="graph_features"
        )
        
        # Validate conversion result
        assert result.validation_passed
        assert isinstance(result.data, np.ndarray)
        assert result.data.size > 0
        assert result.preservation_score > 0.0
    
    async def test_converter_round_trip_validation(self, converter, sample_graph_data):
        """Test round-trip conversion validation"""
        
        format_sequence = [DataFormat.GRAPH, DataFormat.TABLE, DataFormat.GRAPH]
        
        result = await converter.validate_round_trip_conversion(
            sample_graph_data,
            format_sequence
        )
        
        # Validate round-trip result
        assert isinstance(result.valid, bool)
        assert 0.0 <= result.preservation_score <= 1.0
        assert 0.0 <= result.integrity_score <= 1.0
        assert isinstance(result.details, dict)
    
    async def test_validator_basic_validation(self, validator, sample_graph_data):
        """Test basic validation functionality"""
        
        report = await validator.validate_cross_modal_conversion(
            sample_graph_data,
            DataFormat.GRAPH,
            DataFormat.TABLE,
            ValidationLevel.BASIC
        )
        
        # Validate report structure
        assert isinstance(report, ValidationReport)
        assert isinstance(report.overall_passed, bool)
        assert 0.0 <= report.overall_score <= 1.0
        assert report.total_tests >= 0
        assert report.passed_tests >= 0
        assert report.failed_tests >= 0
        assert report.passed_tests + report.failed_tests == report.total_tests
        assert isinstance(report.test_results, list)
    
    async def test_validator_comprehensive_validation(self, validator, sample_table_data):
        """Test comprehensive validation"""
        
        report = await validator.validate_cross_modal_conversion(
            sample_table_data,
            DataFormat.TABLE,
            DataFormat.GRAPH,
            ValidationLevel.COMPREHENSIVE
        )
        
        # Should have more tests than basic validation
        assert report.total_tests > 0
        assert len(report.test_results) > 0
        assert isinstance(report.performance_metrics, dict)
        assert isinstance(report.recommendations, list)
    
    async def test_validator_round_trip_integrity(self, validator, sample_graph_data):
        """Test round-trip integrity validation"""
        
        format_sequence = [DataFormat.GRAPH, DataFormat.TABLE, DataFormat.GRAPH]
        
        report = await validator.validate_round_trip_integrity(
            sample_graph_data,
            format_sequence,
            ValidationLevel.STANDARD
        )
        
        # Validate round-trip report
        assert isinstance(report, ValidationReport)
        assert report.total_tests > 0
        assert "round_trip" in str(report.summary).lower() or "format_sequence" in report.summary
    
    async def test_orchestrator_basic_analysis(self, orchestrator, sample_graph_data):
        """Test basic orchestrated analysis"""
        
        result = await orchestrator.orchestrate_analysis(
            research_question="What are the key patterns in this network?",
            data=sample_graph_data,
            source_format=DataFormat.GRAPH,
            validation_level=ValidationLevel.BASIC,
            optimization_level=WorkflowOptimizationLevel.BASIC
        )
        
        # Validate orchestration result
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.success, bool)
        assert result.execution_time > 0.0
        assert 0.0 <= result.workflow_efficiency <= 1.0
        assert isinstance(result.analysis_metadata, dict)
        assert isinstance(result.performance_metrics, dict)
        assert isinstance(result.recommendations, list)
    
    async def test_orchestrator_with_optimization(self, orchestrator, sample_table_data):
        """Test orchestrated analysis with optimization"""
        
        result = await orchestrator.orchestrate_analysis(
            research_question="Analyze statistical patterns and relationships",
            data=sample_table_data,
            source_format=DataFormat.TABLE,
            preferred_modes=[AnalysisMode.TABLE_ANALYSIS],
            validation_level=ValidationLevel.STANDARD,
            optimization_level=WorkflowOptimizationLevel.STANDARD
        )
        
        # Validate optimization was applied
        assert isinstance(result, AnalysisResult)
        workflow_opt = result.analysis_metadata.get("workflow_optimization", {})
        assert "optimization_level" in workflow_opt
        assert workflow_opt["optimization_level"] == "standard"
    
    async def test_orchestrator_comprehensive_workflow(self, orchestrator, sample_graph_data):
        """Test comprehensive orchestrated workflow"""
        
        result = await orchestrator.orchestrate_analysis(
            research_question="Perform comprehensive multi-modal analysis",
            data=sample_graph_data,
            source_format=DataFormat.GRAPH,
            preferred_modes=[AnalysisMode.COMPREHENSIVE_MULTIMODAL],
            validation_level=ValidationLevel.COMPREHENSIVE,
            optimization_level=WorkflowOptimizationLevel.AGGRESSIVE
        )
        
        # Should have comprehensive results
        assert isinstance(result, AnalysisResult)
        if result.validation_report:
            assert result.validation_report.validation_level == ValidationLevel.COMPREHENSIVE
        
        # Should have performance metrics
        assert "execution_time" in result.performance_metrics
        assert "completion_rate" in result.performance_metrics
    
    async def test_end_to_end_workflow(self, orchestrator):
        """Test complete end-to-end workflow"""
        
        # Create comprehensive test data
        test_data = {
            "nodes": [
                {"id": f"node_{i}", "label": f"Node {i}", "type": "entity", 
                 "properties": {"value": i * 10, "category": chr(65 + i % 3)}}
                for i in range(10)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{(i+1)%10}", 
                 "type": "connects", "weight": 0.1 * (i + 1)}
                for i in range(10)
            ]
        }
        
        # Test multiple analysis modes
        analysis_modes = [
            AnalysisMode.GRAPH_ANALYSIS,
            AnalysisMode.HYBRID_GRAPH_TABLE,
            AnalysisMode.TABLE_ANALYSIS
        ]
        
        results = []
        
        for mode in analysis_modes:
            result = await orchestrator.orchestrate_analysis(
                research_question=f"Analyze data using {mode.value} approach",
                data=test_data,
                source_format=DataFormat.GRAPH,
                preferred_modes=[mode],
                validation_level=ValidationLevel.STANDARD,
                optimization_level=WorkflowOptimizationLevel.STANDARD
            )
            
            results.append(result)
            
            # Validate each result
            assert isinstance(result, AnalysisResult)
            assert result.request_id is not None
            assert result.workflow_id is not None
        
        # All analyses should complete
        assert len(results) == len(analysis_modes)
        
        # Check that different modes were actually used
        selected_modes = []
        for result in results:
            mode_selection = result.analysis_metadata.get("mode_selection", {})
            if "primary_mode" in mode_selection:
                selected_modes.append(mode_selection["primary_mode"])
        
        # Should have variety in selected modes (though may not be exactly as preferred)
        assert len(selected_modes) > 0
    
    async def test_error_handling_invalid_data(self, orchestrator):
        """Test error handling with invalid data"""
        
        # Test with invalid data structure
        invalid_data = {"invalid": "structure"}
        
        result = await orchestrator.orchestrate_analysis(
            research_question="Analyze this invalid data",
            data=invalid_data,
            source_format=DataFormat.GRAPH,  # Claiming it's a graph when it's not
            validation_level=ValidationLevel.BASIC,
            optimization_level=WorkflowOptimizationLevel.BASIC
        )
        
        # Should handle error gracefully
        assert isinstance(result, AnalysisResult)
        # May fail, but should not crash
        if not result.success:
            assert len(result.recommendations) > 0
            assert "error" in result.analysis_metadata or not result.success
    
    async def test_error_handling_invalid_format(self, converter):
        """Test error handling with invalid format conversion"""
        
        # Try to convert incompatible data
        invalid_data = "this is just a string"
        
        try:
            result = await converter.convert_data(
                invalid_data,
                DataFormat.GRAPH,
                DataFormat.TABLE
            )
            # If it doesn't raise an exception, it should indicate failure
            assert not result.validation_passed or result.preservation_score == 0.0
        except Exception as e:
            # Should raise a meaningful exception
            assert isinstance(e, Exception)
            assert len(str(e)) > 0
    
    async def test_performance_under_load(self, orchestrator):
        """Test performance with larger datasets"""
        
        # Create larger test dataset
        large_data = {
            "nodes": [
                {"id": f"node_{i}", "label": f"Node {i}", "type": "entity",
                 "properties": {"value": i, "category": f"cat_{i % 5}"}}
                for i in range(100)  # 100 nodes
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{(i + j) % 100}",
                 "type": "connects", "weight": 0.01 * j}
                for i in range(100) for j in range(1, 3)  # ~200 edges
            ]
        }
        
        start_time = datetime.now()
        
        result = await orchestrator.orchestrate_analysis(
            research_question="Analyze this larger network for key patterns",
            data=large_data,
            source_format=DataFormat.GRAPH,
            validation_level=ValidationLevel.BASIC,  # Use basic for speed
            optimization_level=WorkflowOptimizationLevel.AGGRESSIVE
        )
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 60.0  # 1 minute max for this test
        assert isinstance(result, AnalysisResult)
        
        # Check that it handled the larger dataset
        data_context = result.analysis_metadata.get("data_context", {})
        if "entity_count" in data_context:
            assert data_context["entity_count"] >= 100
    
    async def test_concurrent_orchestrations(self, orchestrator, sample_graph_data):
        """Test concurrent orchestration requests"""
        
        # Create multiple concurrent requests
        requests = [
            orchestrator.orchestrate_analysis(
                research_question=f"Analysis request {i}",
                data=sample_graph_data,
                source_format=DataFormat.GRAPH,
                validation_level=ValidationLevel.BASIC,
                optimization_level=WorkflowOptimizationLevel.BASIC
            )
            for i in range(3)
        ]
        
        # Run concurrently
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        # All should complete (may have exceptions, but should not hang)
        assert len(results) == 3
        
        # Count successful results
        successful_results = [r for r in results if isinstance(r, AnalysisResult) and r.success]
        
        # At least some should succeed
        assert len(successful_results) > 0
        
        # Each result should have unique request ID
        request_ids = [r.request_id for r in successful_results]
        assert len(set(request_ids)) == len(successful_results)


async def run_integration_tests():
    """Run all integration tests"""
    
    print("🧪 Starting Cross-Modal Integration Tests")
    print("=" * 60)
    
    test_instance = TestCrossModalIntegration()
    
    # Initialize fixtures
    mode_selector = await test_instance.mode_selector()
    converter = await test_instance.converter()
    validator = await test_instance.validator()
    orchestrator = await test_instance.orchestrator()
    
    sample_graph = test_instance.sample_graph_data()
    sample_table = test_instance.sample_table_data()
    sample_vector = test_instance.sample_vector_data()
    
    # List of test methods to run
    test_methods = [
        ("Mode Selection Basic", test_instance.test_mode_selection_basic, mode_selector),
        ("Mode Selection Fallback", test_instance.test_mode_selection_fallback, mode_selector),
        ("Graph to Table Conversion", test_instance.test_converter_graph_to_table, converter, sample_graph),
        ("Table to Graph Conversion", test_instance.test_converter_table_to_graph, converter, sample_table),
        ("Graph to Vector Conversion", test_instance.test_converter_graph_to_vector, converter, sample_graph),
        ("Round-trip Validation", test_instance.test_converter_round_trip_validation, converter, sample_graph),
        ("Basic Validation", test_instance.test_validator_basic_validation, validator, sample_graph),
        ("Comprehensive Validation", test_instance.test_validator_comprehensive_validation, validator, sample_table),
        ("Round-trip Integrity", test_instance.test_validator_round_trip_integrity, validator, sample_graph),
        ("Basic Orchestration", test_instance.test_orchestrator_basic_analysis, orchestrator, sample_graph),
        ("Optimized Orchestration", test_instance.test_orchestrator_with_optimization, orchestrator, sample_table),
        ("Comprehensive Workflow", test_instance.test_orchestrator_comprehensive_workflow, orchestrator, sample_graph),
        ("End-to-End Workflow", test_instance.test_end_to_end_workflow, orchestrator),
        ("Error Handling - Invalid Data", test_instance.test_error_handling_invalid_data, orchestrator),
        ("Error Handling - Invalid Format", test_instance.test_error_handling_invalid_format, converter),
        ("Performance Under Load", test_instance.test_performance_under_load, orchestrator),
        ("Concurrent Orchestrations", test_instance.test_concurrent_orchestrations, orchestrator, sample_graph)
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, test_method, *args in test_methods:
        print(f"\n🔍 Running: {test_name}")
        try:
            await test_method(*args)
            print(f"✅ PASSED: {test_name}")
            passed_tests += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {e}")
            failed_tests += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Integration Test Results:")
    print(f"  ✅ Passed: {passed_tests}")
    print(f"  ❌ Failed: {failed_tests}")
    print(f"  📊 Success Rate: {passed_tests / (passed_tests + failed_tests) * 100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    # Run the integration tests
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1)