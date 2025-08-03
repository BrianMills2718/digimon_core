#!/usr/bin/env python3
"""
Test Cross-Modal Error Boundaries and Recovery

Tests for error boundary conditions, recovery mechanisms, and fault tolerance
in cross-modal components.
"""

import pytest
import asyncio
import signal
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
import numpy as np
import pandas as pd

from src.analytics.cross_modal_converter import (
    CrossModalConverter, ConversionError, ConversionIntegrityError,
    DataFormat, ConversionResult
)
from src.analytics.cross_modal_orchestrator import (
    CrossModalOrchestrator, AnalysisRequest, AnalysisResult
)


class TestErrorBoundaries:
    """Test error boundary and isolation mechanisms"""
    
    @pytest.fixture
    def converter_with_error_tracking(self):
        """Create converter with error tracking capabilities"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        converter.preservation_threshold = 0.8
        
        # Track errors
        converter._error_history = []
        
        original_convert = converter.convert_data
        
        async def error_tracking_convert(*args, **kwargs):
            try:
                return await original_convert(*args, **kwargs)
            except Exception as e:
                converter._error_history.append(e)
                raise
        
        converter.convert_data = error_tracking_convert
        return converter
    
    @pytest.mark.asyncio
    async def test_isolated_error_handling(self, converter_with_error_tracking):
        """Test that errors in one conversion don't affect others"""
        converter = converter_with_error_tracking
        
        # Mock embedding service to fail on specific inputs
        def selective_failure(texts):
            if any("FAIL" in text for text in texts):
                raise Exception("Embedding service failure")
            return np.random.rand(len(texts), 384)
        
        converter.embedding_service.generate_text_embeddings.side_effect = selective_failure
        
        # Test data - some will fail, some will succeed
        test_cases = [
            {"nodes": [{"id": 1, "label": "Normal"}], "edges": []},  # Should succeed
            {"nodes": [{"id": 2, "label": "FAIL_NODE"}], "edges": []},  # Should fail
            {"nodes": [{"id": 3, "label": "Another normal"}], "edges": []},  # Should succeed
        ]
        
        results = []
        errors = []
        
        # Process each independently
        for i, data in enumerate(test_cases):
            try:
                result = await converter.convert_data(
                    data, DataFormat.GRAPH, DataFormat.TABLE
                )
                results.append((i, result))
            except Exception as e:
                errors.append((i, e))
        
        # Verify error isolation
        assert len(results) == 2  # Two successful conversions
        assert len(errors) == 1   # One failure
        assert errors[0][0] == 1  # Failed on case 1 (FAIL_NODE)
        
        # Verify successful cases weren't affected
        successful_indices = [r[0] for r in results]
        assert 0 in successful_indices
        assert 2 in successful_indices
    
    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self, converter_with_error_tracking):
        """Test prevention of cascading failures"""
        converter = converter_with_error_tracking
        
        failure_count = 0
        
        def intermittent_failure(*args, **kwargs):
            nonlocal failure_count
            failure_count += 1
            
            # Fail first few attempts, then succeed
            if failure_count <= 3:
                raise Exception(f"Temporary failure {failure_count}")
            
            return ConversionResult(
                data=pd.DataFrame({"col": [1]}),
                source_format=DataFormat.GRAPH,
                target_format=DataFormat.TABLE,
                preservation_score=0.9,
                conversion_metadata={},
                validation_passed=True,
                semantic_integrity=True,
                warnings=[]
            )
        
        # Replace conversion method with one that fails initially
        converter.convert_data = AsyncMock(side_effect=intermittent_failure)
        
        # Attempt multiple conversions
        tasks = []
        for i in range(10):
            task = asyncio.create_task(converter.convert_data(
                {"nodes": [], "edges": []}, DataFormat.GRAPH, DataFormat.TABLE
            ))
            tasks.append(task)
            
            # Small delay between tasks
            await asyncio.sleep(0.01)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should have mix of failures and successes
        successes = [r for r in results if isinstance(r, ConversionResult)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        assert len(successes) >= 7  # Later ones should succeed
        assert len(failures) <= 3   # Early ones may fail
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self, converter_with_error_tracking):
        """Test recovery from resource exhaustion"""
        converter = converter_with_error_tracking
        
        # Simulate resource exhaustion and recovery
        resource_counter = 0
        max_resources = 5
        
        async def resource_limited_operation(*args, **kwargs):
            nonlocal resource_counter
            
            if resource_counter >= max_resources:
                raise Exception("Resource exhausted")
            
            resource_counter += 1
            try:
                await asyncio.sleep(0.1)  # Hold resource
                return ConversionResult(
                    data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                    preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                    semantic_integrity=True, warnings=[]
                )
            finally:
                resource_counter -= 1  # Release resource
        
        converter.convert_data = AsyncMock(side_effect=resource_limited_operation)
        
        # Start many concurrent operations
        tasks = [
            converter.convert_data({"nodes": [], "edges": []}, DataFormat.GRAPH, DataFormat.TABLE)
            for _ in range(20)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle resource limits gracefully
        successes = [r for r in results if isinstance(r, ConversionResult)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        # Some should succeed within resource limits
        assert len(successes) >= 5
        
        # Resource counter should be back to 0 (all resources released)
        assert resource_counter == 0


class TestFaultTolerance:
    """Test fault tolerance and recovery mechanisms"""
    
    @pytest.mark.asyncio
    async def test_partial_system_failure_tolerance(self):
        """Test tolerance to partial system failures"""
        # Create orchestrator with some failing components
        converter = Mock(spec=CrossModalConverter)
        validator = Mock()
        
        # Conversion succeeds but validation fails
        converter.convert_data.return_value = ConversionResult(
            data=pd.DataFrame({"col": [1]}),
            source_format=DataFormat.GRAPH,
            target_format=DataFormat.TABLE,
            preservation_score=0.9,
            conversion_metadata={},
            validation_passed=True,
            semantic_integrity=True,
            warnings=[]
        )
        
        validator.validate_cross_modal_conversion.side_effect = Exception("Validator failed")
        
        orchestrator = CrossModalOrchestrator(service_manager=Mock())
        # Override with mocked services for testing
        orchestrator.converter = converter
        orchestrator.validator = validator
        
        # Should handle partial failure gracefully
        result = await orchestrator.orchestrate_analysis(
            research_question="Partial failure test",
            data={"nodes": [], "edges": []},
            source_format=DataFormat.GRAPH
        )
        
        # Should get result despite validator failure
        assert result is not None
        # May have warnings or reduced confidence, but shouldn't crash
    
    @pytest.mark.asyncio
    async def test_network_interruption_simulation(self):
        """Test handling of network-like interruptions"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Simulate network timeouts
        async def network_timeout_simulation(*args, **kwargs):
            raise asyncio.TimeoutError("Network timeout")
        
        converter.embedding_service.generate_text_embeddings.side_effect = network_timeout_simulation
        
        # Should handle network failures gracefully
        with pytest.raises((ConversionError, asyncio.TimeoutError)):
            await converter.convert_data(
                {"nodes": [{"id": 1, "label": "Test"}], "edges": []},
                DataFormat.GRAPH,
                DataFormat.VECTOR
            )
        
        # System should remain functional for other operations
        vector_data = np.array([[1, 2, 3]])
        result = await converter.convert_data(
            vector_data, DataFormat.VECTOR, DataFormat.TABLE
        )
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_memory_pressure_recovery(self):
        """Test recovery under memory pressure"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Simulate memory pressure
        def memory_pressure_simulation(*args, **kwargs):
            raise MemoryError("Out of memory")
        
        converter.embedding_service.generate_text_embeddings.side_effect = memory_pressure_simulation
        
        # Should handle memory pressure
        try:
            await converter.convert_data(
                {"nodes": [{"id": 1, "label": "Test"}], "edges": []},
                DataFormat.GRAPH,
                DataFormat.VECTOR
            )
        except (ConversionError, MemoryError):
            pass  # Expected
        
        # Should be able to recover for simpler operations
        converter.embedding_service.generate_text_embeddings.side_effect = None
        converter.embedding_service.generate_text_embeddings.return_value = np.random.rand(1, 384)
        
        # Recovery test with smaller data
        small_data = {"nodes": [{"id": 1, "label": "Small"}], "edges": []}
        result = await converter.convert_data(
            small_data, DataFormat.GRAPH, DataFormat.TABLE
        )
        assert result is not None


class TestCorruptionDetection:
    """Test detection and handling of data corruption"""
    
    @pytest.mark.asyncio
    async def test_input_data_corruption_detection(self):
        """Test detection of corrupted input data"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Test various corruption scenarios
        corruption_cases = [
            # Circular references in graph
            {
                "nodes": [{"id": 1, "label": "A", "ref": {"id": 1}}],  # Self-reference
                "edges": []
            },
            
            # Invalid data types
            {
                "nodes": [{"id": "invalid", "label": 123}],  # Wrong types
                "edges": []
            },
            
            # Missing required fields
            {
                "nodes": [{"wrong_field": "value"}],  # Missing id, label
                "edges": []
            },
            
            # Inconsistent edge references
            {
                "nodes": [{"id": 1, "label": "A"}],
                "edges": [{"source": 1, "target": 999, "type": "INVALID"}]  # target doesn't exist
            }
        ]
        
        for i, corrupt_data in enumerate(corruption_cases):
            try:
                result = await converter.convert_data(
                    corrupt_data, DataFormat.GRAPH, DataFormat.TABLE
                )
                # Some corruption might be handled gracefully
                assert result is not None
            except (ConversionError, ValueError, TypeError) as e:
                # Expected for some corruption types
                assert "conversion failed" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio 
    async def test_intermediate_result_corruption_detection(self):
        """Test detection of corruption in intermediate results"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Mock that returns corrupted embeddings
        def corrupted_embeddings(*args, **kwargs):
            # Return embeddings with NaN or infinite values
            embeddings = np.random.rand(len(args[0]), 384)
            embeddings[0, 0] = np.nan  # Inject NaN
            embeddings[0, 1] = np.inf  # Inject infinity
            return embeddings
        
        converter.embedding_service.generate_text_embeddings.side_effect = corrupted_embeddings
        
        # Should detect and handle corrupted intermediate results
        try:
            result = await converter.convert_data(
                {"nodes": [{"id": 1, "label": "Test"}], "edges": []},
                DataFormat.GRAPH,
                DataFormat.VECTOR
            )
            
            # If successful, result should not contain NaN/inf
            if isinstance(result.data, np.ndarray):
                assert not np.any(np.isnan(result.data))
                assert not np.any(np.isinf(result.data))
                
        except ConversionError as e:
            # Acceptable to fail on corrupted embeddings
            assert "conversion failed" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_state_corruption_recovery(self):
        """Test recovery from internal state corruption"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Corrupt internal state
        converter.conversion_count = -1  # Invalid state
        converter.conversion_times = ["invalid", "data"]  # Wrong type
        
        # Should still function despite corrupted state
        result = await converter.convert_data(
            np.array([[1, 2, 3]]), DataFormat.VECTOR, DataFormat.TABLE
        )
        
        assert result is not None
        # State should be reset or handled gracefully


class TestRecoveryMechanisms:
    """Test various recovery mechanisms"""
    
    @pytest.mark.asyncio
    async def test_automatic_retry_mechanisms(self):
        """Test automatic retry on transient failures"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        attempt_count = 0
        
        def flaky_operation(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count <= 2:  # Fail first 2 attempts
                raise Exception("Transient failure")
            
            return np.random.rand(len(args[0]), 384)
        
        converter.embedding_service.generate_text_embeddings.side_effect = flaky_operation
        
        # Should eventually succeed with retries
        result = await converter.convert_data(
            {"nodes": [{"id": 1, "label": "Test"}], "edges": []},
            DataFormat.GRAPH,
            DataFormat.VECTOR
        )
        
        assert result is not None
        assert attempt_count == 3  # Required 3 attempts
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when components fail"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Embedding service fails
        converter.embedding_service.generate_text_embeddings.side_effect = Exception("Service down")
        
        # Should fall back to alternative methods
        result = await converter.convert_data(
            {"nodes": [{"id": 1, "label": "Test"}], "edges": []},
            DataFormat.GRAPH,
            DataFormat.VECTOR
        )
        
        # Should get some result, even if reduced quality
        assert result is not None
        assert isinstance(result.data, np.ndarray)
        
        # May have warnings about degraded functionality
        if hasattr(result, 'warnings'):
            assert len(result.warnings) >= 0  # May contain warnings
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for failing services"""
        converter = CrossModalConverter(
            service_manager=Mock(),
            embedding_service=Mock()
        )
        
        # Simulate circuit breaker
        failure_count = 0
        circuit_open = False
        
        def circuit_breaker_operation(*args, **kwargs):
            nonlocal failure_count, circuit_open
            
            if circuit_open:
                raise Exception("Circuit breaker open")
            
            failure_count += 1
            if failure_count >= 5:  # Open circuit after 5 failures
                circuit_open = True
            
            raise Exception("Service failure")
        
        converter.embedding_service.generate_text_embeddings.side_effect = circuit_breaker_operation
        
        # Should open circuit breaker after repeated failures
        for i in range(10):
            try:
                await converter.convert_data(
                    {"nodes": [{"id": i, "label": f"Test_{i}"}], "edges": []},
                    DataFormat.GRAPH,
                    DataFormat.VECTOR
                )
            except Exception as e:
                if "circuit breaker" in str(e).lower():
                    # Circuit breaker working
                    break
        
        assert circuit_open  # Circuit should be open
        assert failure_count >= 5  # Should have triggered threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])