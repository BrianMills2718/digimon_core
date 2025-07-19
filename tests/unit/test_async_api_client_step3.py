#!/usr/bin/env python3
"""
Unit tests for AsyncEnhancedAPIClient - Step 3: Caching and Performance Metrics Tests

This file tests caching functionality, performance tracking, and optimization features.
Part of comprehensive 80%+ coverage unit testing suite.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.async_api_client import (
    AsyncEnhancedAPIClient,
    AsyncAPIRequest,
    AsyncAPIResponse,
    AsyncAPIRequestType
)


class TestCachingFunctionality:
    """Test response caching functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {}
        return mock_config
    
    @pytest.fixture
    def client(self, mock_config_manager):
        """Create AsyncEnhancedAPIClient for testing."""
        return AsyncEnhancedAPIClient(config_manager=mock_config_manager)
    
    def test_get_cache_key_generation(self, client):
        """Test cache key generation for requests."""
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt",
            max_tokens=100,
            temperature=0.7,
            model="text-embedding-3-small"
        )
        
        cache_key = client._get_cache_key(request)
        
        assert isinstance(cache_key, int)
        
        # Same request should generate same key
        cache_key2 = client._get_cache_key(request)
        assert cache_key == cache_key2
    
    def test_get_cache_key_different_requests(self, client):
        """Test cache key generation for different requests."""
        request1 = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt 1"
        )
        
        request2 = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt 2"
        )
        
        cache_key1 = client._get_cache_key(request1)
        cache_key2 = client._get_cache_key(request2)
        
        assert cache_key1 != cache_key2
    
    @pytest.mark.asyncio
    async def test_cache_response(self, client):
        """Test caching successful responses."""
        cache_key = "test_cache_key"
        response = AsyncAPIResponse(
            success=True,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data={"embedding": [0.1, 0.2, 0.3]},
            response_time=1.0
        )
        
        await client._cache_response(cache_key, response)
        
        assert cache_key in client.response_cache
        cached_response, timestamp = client.response_cache[cache_key]
        assert cached_response == response
        assert isinstance(timestamp, float)
    
    @pytest.mark.asyncio
    async def test_check_cache_valid(self, client):
        """Test checking valid cached responses."""
        cache_key = "test_cache_key"
        response = AsyncAPIResponse(
            success=True,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data={"embedding": [0.1, 0.2, 0.3]},
            response_time=1.0
        )
        
        # Cache the response
        await client._cache_response(cache_key, response)
        
        # Check cache
        cached_response = await client._check_cache(cache_key)
        
        assert cached_response == response
        assert client.performance_metrics["cache_hits"] == 1
    
    @pytest.mark.asyncio
    async def test_check_cache_expired(self, client):
        """Test checking expired cached responses."""
        cache_key = "test_cache_key"
        response = AsyncAPIResponse(
            success=True,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data={"embedding": [0.1, 0.2, 0.3]},
            response_time=1.0
        )
        
        # Cache the response with old timestamp
        old_timestamp = time.time() - client.cache_ttl - 10
        client.response_cache[cache_key] = (response, old_timestamp)
        
        # Check cache - should return None and remove expired entry
        cached_response = await client._check_cache(cache_key)
        
        assert cached_response is None
        assert cache_key not in client.response_cache
    
    @pytest.mark.asyncio
    async def test_check_cache_missing(self, client):
        """Test checking cache for non-existent key."""
        cached_response = await client._check_cache("nonexistent_key")
        
        assert cached_response is None
        assert client.performance_metrics["cache_hits"] == 0
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_when_full(self, client):
        """Test cache cleanup when cache size exceeds limit."""
        # Fill cache with expired entries
        current_time = time.time()
        expired_time = current_time - client.cache_ttl - 10
        
        for i in range(1005):  # Exceed the 1000 limit
            cache_key = f"key_{i}"
            response = AsyncAPIResponse(
                success=True,
                service_used="openai",
                request_type=AsyncAPIRequestType.EMBEDDING,
                response_data={"embedding": [0.1, 0.2, 0.3]},
                response_time=1.0
            )
            if i < 500:  # First 500 are expired
                client.response_cache[cache_key] = (response, expired_time)
            else:  # Rest are fresh
                client.response_cache[cache_key] = (response, current_time)
        
        # Cache a new response - should trigger cleanup
        new_response = AsyncAPIResponse(
            success=True,
            service_used="gemini",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            response_data={"text": "test"},
            response_time=1.0
        )
        
        await client._cache_response("new_key", new_response)
        
        # Expired entries should be removed
        for i in range(500):
            assert f"key_{i}" not in client.response_cache


class TestPerformanceMetrics:
    """Test performance metrics tracking."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {}
        return mock_config
    
    @pytest.fixture
    def client(self, mock_config_manager):
        """Create AsyncEnhancedAPIClient for testing."""
        return AsyncEnhancedAPIClient(config_manager=mock_config_manager)
    
    def test_initial_performance_metrics(self, client):
        """Test initial state of performance metrics."""
        metrics = client.get_performance_metrics()
        
        assert metrics["total_requests"] == 0
        assert metrics["concurrent_requests"] == 0
        assert metrics["batch_requests"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["average_response_time"] == 0.0
        assert metrics["total_response_time"] == 0.0
        assert metrics["cache_hit_rate_percent"] == 0.0
        assert metrics["cache_size"] == 0
        assert metrics["processing_active"] is False
        assert metrics["session_initialized"] is False
    
    def test_performance_metrics_after_request(self, client):
        """Test performance metrics after simulated request."""
        # Simulate request processing
        client.performance_metrics["total_requests"] = 5
        client.performance_metrics["total_response_time"] = 10.0
        client.performance_metrics["cache_hits"] = 2
        
        # Need to trigger the calculation that happens in get_performance_metrics
        metrics = client.get_performance_metrics()
        
        assert metrics["total_requests"] == 5
        # The average gets calculated in get_performance_metrics, check the raw value
        assert client.performance_metrics["total_response_time"] == 10.0
        assert metrics["cache_hit_rate_percent"] == 40.0
    
    @pytest.mark.asyncio
    async def test_performance_metrics_with_session(self, client):
        """Test performance metrics with initialized session."""
        await client.initialize_clients()
        
        metrics = client.get_performance_metrics()
        
        assert metrics["session_initialized"] is True
        assert metrics["processing_active"] is True
        assert "connection_pool_stats" in metrics
        
        # Clean up
        await client.close()
    
    def test_connection_pool_stats_without_session(self, client):
        """Test connection pool stats when session not initialized."""
        metrics = client.get_performance_metrics()
        
        pool_stats = metrics["connection_pool_stats"]
        assert pool_stats["active_connections"] == 0
        assert pool_stats["idle_connections"] == 0
        assert pool_stats["pool_utilization"] == 0.0
        assert pool_stats["connection_reuse_rate"] == 0.0


class TestOptimizationFeatures:
    """Test optimization features and methods."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {}
        return mock_config
    
    @pytest.fixture
    def client(self, mock_config_manager):
        """Create AsyncEnhancedAPIClient for testing."""
        return AsyncEnhancedAPIClient(config_manager=mock_config_manager)
    
    @pytest.mark.asyncio
    async def test_optimize_connection_pool_without_session(self, client):
        """Test connection pool optimization when session not initialized."""
        result = await client.optimize_connection_pool()
        
        assert "optimizations_applied" in result
        assert "performance_improvements" in result
        assert "recommendations" in result
        assert "Initialize HTTP session for connection pooling" in result["recommendations"]
    
    @pytest.mark.asyncio
    async def test_optimize_connection_pool_with_session(self, client):
        """Test connection pool optimization with initialized session."""
        await client.initialize_clients()
        
        result = await client.optimize_connection_pool()
        
        assert "optimizations_applied" in result
        assert "current_stats" in result
        assert "recommendations" in result
        
        # Check that we get meaningful recommendations
        recommendations = result["recommendations"]
        assert isinstance(recommendations, list)
        
        # Clean up
        await client.close()
    
    @pytest.mark.asyncio
    async def test_optimize_connection_pool_high_utilization(self, client):
        """Test optimization recommendations for high utilization."""
        await client.initialize_clients()
        
        # Mock high utilization
        with patch.object(client, 'get_performance_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "connection_pool_stats": {
                    "pool_utilization": 85.0,
                    "connection_reuse_rate": 75.0
                }
            }
            
            result = await client.optimize_connection_pool()
            
            recommendations = result["recommendations"]
            assert any("increasing connection pool size" in rec for rec in recommendations)
        
        # Clean up
        await client.close()
    
    @pytest.mark.asyncio
    async def test_optimize_connection_pool_low_utilization(self, client):
        """Test optimization recommendations for low utilization."""
        await client.initialize_clients()
        
        # Mock low utilization
        with patch.object(client, 'get_performance_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "connection_pool_stats": {
                    "pool_utilization": 15.0,
                    "connection_reuse_rate": 30.0
                }
            }
            
            result = await client.optimize_connection_pool()
            
            recommendations = result["recommendations"]
            assert any("decreasing connection pool size" in rec for rec in recommendations)
            assert any("keepalive optimization" in rec for rec in recommendations)
        
        # Clean up
        await client.close()


class TestBenchmarkingFunctionality:
    """Test benchmarking and performance validation."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {}
        return mock_config
    
    @pytest.fixture
    def client(self, mock_config_manager):
        """Create AsyncEnhancedAPIClient for testing."""
        return AsyncEnhancedAPIClient(config_manager=mock_config_manager)
    
    @pytest.mark.asyncio
    async def test_benchmark_performance_without_clients(self, client):
        """Test benchmarking when clients are not available."""
        with patch.object(client, '_make_actual_request', new_callable=AsyncMock) as mock_request:
            # Mock successful responses
            mock_request.return_value = AsyncAPIResponse(
                success=True,
                service_used="openai",
                request_type=AsyncAPIRequestType.COMPLETION,
                response_data={"text": "test response"},
                response_time=0.5
            )
            
            result = await client.benchmark_performance(num_requests=4)
            
            assert "sequential_time" in result
            assert "concurrent_time" in result
            assert "performance_improvement_percent" in result
            assert "sequential_successful" in result
            assert "concurrent_successful" in result
            assert "target_improvement" in result
            assert "achieved_target" in result
            assert "metrics" in result
            
            # Should have made requests
            assert mock_request.call_count >= 4
    
    @pytest.mark.asyncio
    async def test_benchmark_performance_structure(self, client):
        """Test benchmark performance result structure."""
        with patch.object(client, '_make_actual_request', new_callable=AsyncMock) as mock_request:
            with patch.object(client, 'process_concurrent_requests', new_callable=AsyncMock) as mock_concurrent:
                
                # Mock responses
                mock_response = AsyncAPIResponse(
                    success=True,
                    service_used="openai", 
                    request_type=AsyncAPIRequestType.COMPLETION,
                    response_data={"text": "test"},
                    response_time=0.1
                )
                
                mock_request.return_value = mock_response
                mock_concurrent.return_value = [mock_response] * 5
                
                result = await client.benchmark_performance(num_requests=10)
                
                # Verify result structure
                required_keys = [
                    "sequential_time",
                    "concurrent_time", 
                    "performance_improvement_percent",
                    "sequential_successful",
                    "concurrent_successful",
                    "target_improvement",
                    "achieved_target",
                    "metrics"
                ]
                
                for key in required_keys:
                    assert key in result
                
                assert result["target_improvement"] == "50-60%"
                assert isinstance(result["achieved_target"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])