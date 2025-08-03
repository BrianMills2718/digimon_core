#!/usr/bin/env python3
"""
Test Cross-Modal Components Edge Cases and Concurrency

Comprehensive tests for edge cases, error conditions, and concurrent operations
in cross-modal converter and orchestrator components.
"""

import pytest
import asyncio
import threading
import time
import numpy as np
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any

from src.analytics.cross_modal_converter import (
    CrossModalConverter, ConversionError, ConversionIntegrityError,
    DataFormat, ConversionResult, ValidationResult
)
from src.analytics.cross_modal_orchestrator import (
    CrossModalOrchestrator, AnalysisRequest, AnalysisResult,
    AnalysisMode, ValidationLevel, WorkflowOptimizationLevel
)


@pytest.fixture
def mock_services():
    """Create mock services for testing"""
    neo4j_manager = Mock()
    neo4j_manager.execute_read_query = AsyncMock()
    neo4j_manager.execute_write_query = AsyncMock()
    
    embedding_service = Mock()
    embedding_service.generate_text_embeddings = AsyncMock()
    
    validator = Mock()
    validator.validate_cross_modal_conversion = AsyncMock()
    validator.validate_round_trip_integrity = AsyncMock()
    
    return neo4j_manager, embedding_service, validator


@pytest.fixture
def converter(mock_services):
    """Create CrossModalConverter instance"""
    neo4j_manager, embedding_service, validator = mock_services
    converter = CrossModalConverter(
        service_manager=neo4j_manager,
        embedding_service=embedding_service
    )
    converter.preservation_threshold = 0.8
    return converter


@pytest.fixture
def orchestrator(mock_services):
    """Create CrossModalOrchestrator instance"""
    neo4j_manager, embedding_service, validator = mock_services
    orchestrator = CrossModalOrchestrator(service_manager=neo4j_manager)
    # Override with mocked services for testing
    orchestrator.converter = CrossModalConverter(
        service_manager=neo4j_manager, 
        embedding_service=embedding_service
    )
    orchestrator.validator = validator
    return orchestrator


class TestCrossModalConverterEdgeCases:
    """Test edge cases for CrossModalConverter"""
    
    @pytest.mark.asyncio
    async def test_empty_data_conversion(self, converter):
        """Test conversion with empty data"""
        # Disable validation for empty data tests (edge case)
        converter.enable_validation = False
        
        # Empty graph - should work
        empty_graph = {"nodes": [], "edges": []}
        result = await converter.convert_data(
            empty_graph, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert isinstance(result.data, pd.DataFrame)
        assert result.data.empty
        
        # Empty DataFrame - should fail with proper error
        empty_df = pd.DataFrame()
        with pytest.raises(ConversionError) as exc_info:
            await converter.convert_data(
                empty_df, DataFormat.TABLE, DataFormat.GRAPH
            )
        assert "invalid input data" in str(exc_info.value).lower()
        
        # Empty vector - should fail with proper error
        empty_vector = np.array([])
        with pytest.raises(ConversionError) as exc_info:
            await converter.convert_data(
                empty_vector, DataFormat.VECTOR, DataFormat.TABLE
            )
        assert "no converter available" in str(exc_info.value).lower() or "conversion failed" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_malformed_data_handling(self, converter):
        """Test handling of malformed data structures"""
        # Malformed graph (missing required fields)
        malformed_graph = {"nodes": [{"invalid": "structure"}]}  # Missing id, label
        
        with pytest.raises(ConversionError) as exc_info:
            await converter.convert_data(
                malformed_graph, DataFormat.GRAPH, DataFormat.TABLE
            )
        assert "conversion failed" in str(exc_info.value).lower()
        
        # DataFrame with all NaN values
        nan_df = pd.DataFrame({"col1": [np.nan, np.nan], "col2": [np.nan, np.nan]})
        result = await converter.convert_data(
            nan_df, DataFormat.TABLE, DataFormat.VECTOR
        )
        # Should handle gracefully, not crash
        assert result.data is not None
        
        # Invalid vector shape
        invalid_vector = np.array([[[[1, 2]]]])  # 4D array
        with pytest.raises(ConversionError):
            await converter.convert_data(
                invalid_vector, DataFormat.VECTOR, DataFormat.TABLE
            )
    
    @pytest.mark.asyncio
    async def test_large_data_handling(self, converter):
        """Test conversion with large data structures"""
        # Large graph (1000 nodes, 5000 edges)
        large_graph = {
            "nodes": [{"id": i, "label": f"Node_{i}", "properties": {"value": i}} 
                     for i in range(1000)],
            "edges": [{"source": i % 1000, "target": (i + 1) % 1000, "type": "CONNECTS"} 
                     for i in range(5000)]
        }
        
        result = await converter.convert_data(
            large_graph, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert isinstance(result.data, pd.DataFrame)
        assert len(result.data) > 0
        
        # Large DataFrame (10k rows, 100 columns)
        large_df = pd.DataFrame(
            np.random.rand(10000, 100),
            columns=[f"col_{i}" for i in range(100)]
        )
        
        result = await converter.convert_data(
            large_df, DataFormat.TABLE, DataFormat.VECTOR
        )
        assert isinstance(result.data, np.ndarray)
        assert result.data.size > 0
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self, converter):
        """Test handling of unicode and special characters"""
        unicode_graph = {
            "nodes": [
                {"id": 1, "label": "测试节点", "properties": {"name": "🌟 Special"}},
                {"id": 2, "label": "Ñodé", "properties": {"desc": "café & résumé"}},
                {"id": 3, "label": "Москва", "properties": {"city": "العربية"}}
            ],
            "edges": [
                {"source": 1, "target": 2, "type": "CONNECTS_TO", "properties": {"weight": "∞"}},
                {"source": 2, "target": 3, "type": "RELATES_TO", "properties": {"note": "→←↑↓"}}
            ]
        }
        
        result = await converter.convert_data(
            unicode_graph, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert isinstance(result.data, pd.DataFrame)
        
        # Verify unicode preservation in conversion
        df_content = result.data.to_string()
        assert "测试节点" in df_content or "🌟" in df_content  # Some unicode preserved
    
    @pytest.mark.asyncio
    async def test_circular_references(self, converter):
        """Test handling of circular references in data"""
        # Graph with self-loops and cycles
        circular_graph = {
            "nodes": [
                {"id": 1, "label": "A"},
                {"id": 2, "label": "B"},
                {"id": 3, "label": "C"}
            ],
            "edges": [
                {"source": 1, "target": 1, "type": "SELF_LOOP"},  # Self-loop
                {"source": 1, "target": 2, "type": "TO_B"},
                {"source": 2, "target": 3, "type": "TO_C"},
                {"source": 3, "target": 1, "type": "BACK_TO_A"}  # Cycle
            ]
        }
        
        result = await converter.convert_data(
            circular_graph, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert isinstance(result.data, pd.DataFrame)
        # Should handle cycles without infinite loops
    
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self, converter):
        """Test behavior under memory pressure"""
        # Create data that approaches memory limits
        memory_intensive_data = []
        for i in range(1000):
            large_string = "x" * 10000  # 10KB per entry
            memory_intensive_data.append({
                "id": i,
                "label": f"Node_{i}",
                "properties": {"large_field": large_string}
            })
        
        large_graph = {
            "nodes": memory_intensive_data,
            "edges": []
        }
        
        # Should handle without crashing (may use more memory but not fail)
        result = await converter.convert_data(
            large_graph, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_conversions(self, converter):
        """Test concurrent conversion operations"""
        # Disable validation for concurrency testing
        converter.enable_validation = False
        
        # Create multiple different conversion tasks
        tasks = []
        
        # Graph to table conversions
        for i in range(5):
            graph_data = {
                "nodes": [{"id": j, "label": f"Node_{i}_{j}"} for j in range(10)],
                "edges": [{"source": j, "target": (j+1)%10, "type": "EDGE"} for j in range(10)]
            }
            task = converter.convert_data(graph_data, DataFormat.GRAPH, DataFormat.TABLE)
            tasks.append(task)
        
        # Table to vector conversions
        for i in range(5):
            df_data = pd.DataFrame({
                "col1": range(10),
                "col2": [f"value_{i}_{j}" for j in range(10)]
            })
            task = converter.convert_data(df_data, DataFormat.TABLE, DataFormat.VECTOR)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all succeeded
        for result in results:
            assert not isinstance(result, Exception), f"Task failed: {result}"
            assert isinstance(result, ConversionResult)
    
    @pytest.mark.asyncio
    async def test_race_conditions_shared_state(self, converter):
        """Test for race conditions in shared state access"""
        # Test concurrent access to conversion statistics
        async def perform_conversion(i):
            graph_data = {
                "nodes": [{"id": 1, "label": f"Node_{i}"}],
                "edges": []
            }
            return await converter.convert_data(
                graph_data, DataFormat.GRAPH, DataFormat.TABLE
            )
        
        # Run many concurrent conversions
        tasks = [perform_conversion(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Verify statistics are consistent
        assert converter.conversion_count == 50
        assert len(converter.conversion_times) == 50
        
        # No race condition corruption
        assert all(t > 0 for t in converter.conversion_times)
    
    @pytest.mark.asyncio
    async def test_embedding_service_failures(self, converter, mock_services):
        """Test handling of embedding service failures"""
        _, embedding_service, _ = mock_services
        
        # Test intermittent failures
        call_count = 0
        def failing_embedding(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Service temporarily unavailable")
            return np.random.rand(len(args[0]), 384)
        
        embedding_service.generate_text_embeddings.side_effect = failing_embedding
        
        # Should handle failures gracefully and retry/fallback
        vector_data = np.random.rand(5, 384)
        result = await converter.convert_data(
            vector_data, DataFormat.VECTOR, DataFormat.TABLE
        )
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_conversion_timeout_handling(self, converter):
        """Test handling of long-running conversions"""
        # Create a conversion that would take a long time
        huge_graph = {
            "nodes": [{"id": i, "label": f"Node_{i}"} for i in range(10000)],
            "edges": [{"source": i, "target": (i+1)%10000, "type": "EDGE"} 
                     for i in range(50000)]
        }
        
        # Test with timeout
        try:
            result = await asyncio.wait_for(
                converter.convert_data(huge_graph, DataFormat.GRAPH, DataFormat.TABLE),
                timeout=5.0  # 5 second timeout
            )
            # Should complete or handle timeout gracefully
            assert result is not None
        except asyncio.TimeoutError:
            # Timeout is acceptable for large data
            pass


class TestCrossModalOrchestratorEdgeCases:
    """Test edge cases for CrossModalOrchestrator"""
    
    @pytest.mark.asyncio
    async def test_invalid_analysis_requests(self, orchestrator):
        """Test handling of invalid analysis requests"""
        # Empty research question
        with pytest.raises(Exception):  # Should validate input
            await orchestrator.orchestrate_analysis(
                research_question="",
                data={},
                source_format=DataFormat.GRAPH
            )
        
        # None data
        with pytest.raises(Exception):
            await orchestrator.orchestrate_analysis(
                research_question="Valid question",
                data=None,
                source_format=DataFormat.GRAPH
            )
        
        # Mismatched data format
        graph_data = {"nodes": [], "edges": []}
        with pytest.raises(Exception):
            await orchestrator.orchestrate_analysis(
                research_question="Test question",
                data=graph_data,
                source_format=DataFormat.TABLE  # Wrong format
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_orchestration_requests(self, orchestrator):
        """Test concurrent orchestration requests"""
        # Create multiple analysis requests
        requests = []
        for i in range(10):
            graph_data = {
                "nodes": [{"id": j, "label": f"Node_{i}_{j}"} for j in range(5)],
                "edges": []
            }
            
            request = orchestrator.orchestrate_analysis(
                research_question=f"Question {i}",
                data=graph_data,
                source_format=DataFormat.GRAPH,
                preferred_modes=[AnalysisMode.GRAPH_ANALYSIS]
            )
            requests.append(request)
        
        # Execute concurrently
        results = await asyncio.gather(*requests, return_exceptions=True)
        
        # Verify all completed
        successful_results = [r for r in results if isinstance(r, AnalysisResult)]
        assert len(successful_results) >= 8  # Allow some failures
    
    @pytest.mark.asyncio
    async def test_workflow_step_failures(self, orchestrator):
        """Test handling of individual workflow step failures"""
        # Mock converter to fail on specific operations
        orchestrator.converter.convert_data = AsyncMock(
            side_effect=ConversionError("Conversion failed")
        )
        
        graph_data = {"nodes": [{"id": 1, "label": "Test"}], "edges": []}
        
        result = await orchestrator.orchestrate_analysis(
            research_question="Test question",
            data=graph_data,
            source_format=DataFormat.GRAPH
        )
        
        # Should handle failure gracefully
        assert result is not None
        # May have partial results or error information
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self, orchestrator):
        """Test behavior under resource exhaustion"""
        # Simulate high load with many concurrent requests
        heavy_requests = []
        
        for i in range(20):  # More than typical capacity
            large_graph = {
                "nodes": [{"id": j, "label": f"Node_{j}"} for j in range(100)],
                "edges": [{"source": j, "target": (j+1)%100, "type": "EDGE"} 
                         for j in range(200)]
            }
            
            request = orchestrator.orchestrate_analysis(
                research_question=f"Heavy question {i}",
                data=large_graph,
                source_format=DataFormat.GRAPH
            )
            heavy_requests.append(request)
        
        # Should handle gracefully without system crash
        results = await asyncio.gather(*heavy_requests, return_exceptions=True)
        
        # Some should succeed, system should remain stable
        exceptions = [r for r in results if isinstance(r, Exception)]
        successes = [r for r in results if isinstance(r, AnalysisResult)]
        
        # At least some should succeed, system shouldn't crash entirely
        assert len(successes) > 0 or len(exceptions) < len(heavy_requests)


class TestCrossModalConcurrencyStress:
    """Stress tests for concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_conversions(self, converter):
        """Test high concurrency conversion stress"""
        num_concurrent = 100
        
        async def random_conversion(i):
            # Randomly choose conversion type
            if i % 3 == 0:
                # Graph to table
                data = {
                    "nodes": [{"id": j, "label": f"N_{i}_{j}"} for j in range(5)],
                    "edges": []
                }
                return await converter.convert_data(data, DataFormat.GRAPH, DataFormat.TABLE)
            elif i % 3 == 1:
                # Table to vector
                data = pd.DataFrame({"col": range(5)})
                return await converter.convert_data(data, DataFormat.TABLE, DataFormat.VECTOR)
            else:
                # Vector to table
                data = np.random.rand(5, 10)
                return await converter.convert_data(data, DataFormat.VECTOR, DataFormat.TABLE)
        
        # Execute high concurrency
        start_time = time.time()
        tasks = [random_conversion(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Verify performance and stability
        successful = [r for r in results if isinstance(r, ConversionResult)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        print(f"Concurrent conversions: {len(successful)} success, {len(failed)} failed in {duration:.2f}s")
        
        # Most should succeed
        assert len(successful) >= num_concurrent * 0.8  # 80% success rate minimum
        
        # Should complete in reasonable time
        assert duration < 30  # 30 seconds max
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, converter):
        """Test for memory leaks in repeated operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many conversions
        for i in range(100):
            graph_data = {
                "nodes": [{"id": j, "label": f"Node_{j}"} for j in range(10)],
                "edges": []
            }
            
            result = await converter.convert_data(
                graph_data, DataFormat.GRAPH, DataFormat.TABLE
            )
            
            # Explicitly delete to help garbage collection
            del result
            del graph_data
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (< 100MB)
        assert memory_growth < 100 * 1024 * 1024, f"Memory leak detected: {memory_growth} bytes"
    
    @pytest.mark.asyncio  
    async def test_threading_safety(self, converter):
        """Test thread safety with mixed async/sync operations"""
        results = []
        exceptions = []
        
        def sync_operation(i):
            try:
                # Simulate sync operation that might interfere
                time.sleep(0.01)
                converter.conversion_count += 1  # Potential race condition
                results.append(f"sync_{i}")
            except Exception as e:
                exceptions.append(e)
        
        async def async_operation(i):
            try:
                graph_data = {
                    "nodes": [{"id": 1, "label": f"Node_{i}"}],
                    "edges": []
                }
                result = await converter.convert_data(
                    graph_data, DataFormat.GRAPH, DataFormat.TABLE
                )
                results.append(f"async_{i}")
            except Exception as e:
                exceptions.append(e)
        
        # Mix of async and threaded operations
        async_tasks = [async_operation(i) for i in range(20)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            sync_futures = [executor.submit(sync_operation, i) for i in range(20)]
            
            # Run both concurrently
            await asyncio.gather(*async_tasks)
            
            # Wait for sync operations
            for future in sync_futures:
                future.result()
        
        # Verify no exceptions and reasonable results
        assert len(exceptions) == 0, f"Threading safety violations: {exceptions}"
        assert len(results) == 40  # All operations completed


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])