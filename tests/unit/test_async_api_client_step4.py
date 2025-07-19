#!/usr/bin/env python3
"""
Unit tests for AsyncEnhancedAPIClient - Step 4: Request Processing and Error Handling Tests

This file tests request processing, error handling, batch operations, and edge cases.
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
    AsyncOpenAIClient,
    AsyncGeminiClient,
    AsyncAPIRequest,
    AsyncAPIResponse,
    AsyncAPIRequestType
)


class TestRequestProcessing:
    """Test request processing functionality."""
    
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
    async def test_make_actual_request_openai_embedding(self, client):
        """Test making actual OpenAI embedding request."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        mock_openai_client.create_single_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        client.openai_client = mock_openai_client
        
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt"
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is True
        assert response.service_used == "openai"
        assert response.request_type == AsyncAPIRequestType.EMBEDDING
        assert response.response_data == {"embedding": [0.1, 0.2, 0.3]}
        assert response.response_time > 0
        mock_openai_client.create_single_embedding.assert_called_once_with("test prompt")
    
    @pytest.mark.asyncio
    async def test_make_actual_request_openai_completion(self, client):
        """Test making actual OpenAI completion request."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        mock_openai_client.create_completion = AsyncMock(return_value="Generated text")
        client.openai_client = mock_openai_client
        
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.COMPLETION,
            prompt="test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is True
        assert response.service_used == "openai"
        assert response.request_type == AsyncAPIRequestType.COMPLETION
        assert response.response_data == {"text": "Generated text"}
        mock_openai_client.create_completion.assert_called_once_with(
            "test prompt", max_tokens=100, temperature=0.7
        )
    
    @pytest.mark.asyncio
    async def test_make_actual_request_gemini(self, client):
        """Test making actual Gemini request."""
        # Mock Gemini client
        mock_gemini_client = Mock()
        mock_gemini_client.generate_content = AsyncMock(return_value="Gemini response")
        client.gemini_client = mock_gemini_client
        
        request = AsyncAPIRequest(
            service_type="gemini",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            prompt="test prompt"
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is True
        assert response.service_used == "gemini"
        assert response.request_type == AsyncAPIRequestType.TEXT_GENERATION
        assert response.response_data == {"text": "Gemini response"}
        mock_gemini_client.generate_content.assert_called_once_with("test prompt")
    
    @pytest.mark.asyncio
    async def test_make_actual_request_unsupported_service(self, client):
        """Test making request with unsupported service."""
        request = AsyncAPIRequest(
            service_type="unsupported_service",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            prompt="test prompt"
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is False
        assert response.service_used == "unsupported_service"
        assert response.error == "Service unsupported_service not available"
    
    @pytest.mark.asyncio
    async def test_make_actual_request_unsupported_request_type(self, client):
        """Test making request with unsupported request type for OpenAI."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        client.openai_client = mock_openai_client
        
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.CLASSIFICATION,  # Unsupported
            prompt="test prompt"
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is False
        assert response.service_used == "openai"
        assert "Unsupported request type" in response.error


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
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
    async def test_request_with_client_exception(self, client):
        """Test request processing when client raises exception."""
        # Mock OpenAI client that raises exception
        mock_openai_client = Mock()
        mock_openai_client.create_single_embedding = AsyncMock(side_effect=Exception("API Error"))
        client.openai_client = mock_openai_client
        
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt"
        )
        
        response = await client._make_actual_request(request)
        
        assert response.success is False
        assert response.service_used == "openai"
        assert response.error == "API Error"
        assert response.response_data is None
    
    @pytest.mark.asyncio
    async def test_process_concurrent_requests_with_exceptions(self, client):
        """Test concurrent request processing with some requests failing."""
        # Mock make_actual_request to return mix of success and failure
        async def mock_make_request(request):
            if "fail" in request.prompt:
                raise Exception("Simulated failure")
            return AsyncAPIResponse(
                success=True,
                service_used=request.service_type,
                request_type=request.request_type,
                response_data={"text": "success"},
                response_time=0.1
            )
        
        client._make_actual_request = AsyncMock(side_effect=mock_make_request)
        
        requests = [
            AsyncAPIRequest("openai", AsyncAPIRequestType.COMPLETION, "success 1"),
            AsyncAPIRequest("openai", AsyncAPIRequestType.COMPLETION, "fail prompt"),
            AsyncAPIRequest("openai", AsyncAPIRequestType.COMPLETION, "success 2"),
        ]
        
        responses = await client.process_concurrent_requests(requests)
        
        assert len(responses) == 3
        assert responses[0].success is True
        assert responses[1].success is False
        assert responses[2].success is True
        assert "Simulated failure" in responses[1].error
    
    @pytest.mark.asyncio
    async def test_create_embeddings_service_unavailable(self, client):
        """Test create_embeddings when service is unavailable."""
        # No OpenAI client set
        client.openai_client = None
        
        with pytest.raises(ValueError, match="Service openai not available"):
            await client.create_embeddings(["test text"], service="openai")
    
    @pytest.mark.asyncio
    async def test_generate_content_service_unavailable(self, client):
        """Test generate_content when service is unavailable."""
        # Mock failed request
        mock_response = AsyncAPIResponse(
            success=False,
            service_used="gemini",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            response_data=None,
            response_time=0.0,
            error="Service unavailable"
        )
        
        client._process_request_with_cache = AsyncMock(return_value=mock_response)
        
        with pytest.raises(ValueError, match="Content generation failed"):
            await client.generate_content("test prompt", service="gemini")


class TestBatchProcessing:
    """Test batch processing functionality."""
    
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
    async def test_create_embeddings_batch_single_text(self, client):
        """Test create_embeddings with single text (no batching)."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        mock_openai_client.create_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        client.openai_client = mock_openai_client
        
        result = await client.create_embeddings(["single text"], service="openai")
        
        assert result == [[0.1, 0.2, 0.3]]
        mock_openai_client.create_embeddings.assert_called_once_with(["single text"])
    
    @pytest.mark.asyncio
    async def test_create_embeddings_batch_multiple_texts(self, client):
        """Test create_embeddings with multiple texts (batching)."""
        # Mock OpenAI client
        mock_openai_client = Mock()
        mock_openai_client.create_embeddings = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
        client.openai_client = mock_openai_client
        
        texts = ["text 1", "text 2"]
        result = await client.create_embeddings(texts, service="openai")
        
        assert len(result) == 2
        assert result == [[0.1, 0.2], [0.3, 0.4]]
    
    @pytest.mark.asyncio
    async def test_process_batch_mixed_services(self, client):
        """Test process_batch with mixed OpenAI and Gemini requests."""
        # Mock clients
        mock_openai_client = Mock()
        mock_openai_client.create_single_embedding = AsyncMock(return_value=[0.1, 0.2])
        mock_gemini_client = Mock()
        mock_gemini_client.generate_content = AsyncMock(return_value="Generated")
        
        client.openai_client = mock_openai_client
        client.gemini_client = mock_gemini_client
        
        requests = [
            AsyncAPIRequest("openai", AsyncAPIRequestType.EMBEDDING, "text 1"),
            AsyncAPIRequest("gemini", AsyncAPIRequestType.TEXT_GENERATION, "prompt 1"),
            AsyncAPIRequest("openai", AsyncAPIRequestType.EMBEDDING, "text 2"),
        ]
        
        responses = await client.process_batch(requests)
        
        assert len(responses) == 3
        # Check OpenAI responses
        openai_responses = [r for r in responses if r.service_used == "openai"]
        assert len(openai_responses) == 2
        for response in openai_responses:
            assert response.success is True
            assert response.response_data == {"embedding": [0.1, 0.2]}
        
        # Check Gemini responses
        gemini_responses = [r for r in responses if r.service_used == "gemini"]
        assert len(gemini_responses) == 1
        assert gemini_responses[0].success is True
        assert gemini_responses[0].response_data == {"text": "Generated"}
    
    @pytest.mark.asyncio
    async def test_process_openai_batch_no_client(self, client):
        """Test _process_openai_batch when OpenAI client is None."""
        client.openai_client = None
        
        requests = [
            AsyncAPIRequest("openai", AsyncAPIRequestType.EMBEDDING, "text")
        ]
        
        responses = await client._process_openai_batch(requests)
        
        assert responses == []
    
    @pytest.mark.asyncio
    async def test_process_gemini_batch_no_client(self, client):
        """Test _process_gemini_batch when Gemini client is None."""
        client.gemini_client = None
        
        requests = [
            AsyncAPIRequest("gemini", AsyncAPIRequestType.TEXT_GENERATION, "prompt")
        ]
        
        responses = await client._process_gemini_batch(requests)
        
        assert responses == []


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""
    
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
    async def test_empty_request_list(self, client):
        """Test processing empty request list."""
        responses = await client.process_concurrent_requests([])
        
        assert responses == []
    
    @pytest.mark.asyncio
    async def test_process_batch_empty_requests(self, client):
        """Test process_batch with empty request list."""
        responses = await client.process_batch([])
        
        assert responses == []
    
    @pytest.mark.asyncio
    async def test_close_without_initialization(self, client):
        """Test closing client that was never initialized."""
        # Should not raise exception
        await client.close()
        
        assert client.processing_active is False
        assert len(client.response_cache) == 0
    
    @pytest.mark.asyncio
    async def test_multiple_close_calls(self, client):
        """Test calling close multiple times."""
        await client.initialize_clients()
        
        # First close
        await client.close()
        assert client.processing_active is False
        
        # Second close should not raise exception
        await client.close()
        assert client.processing_active is False
    
    def test_get_cache_key_with_none_values(self, client):
        """Test cache key generation with None values."""
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test",
            max_tokens=None,
            temperature=None,
            model=None
        )
        
        cache_key = client._get_cache_key(request)
        
        assert isinstance(cache_key, int)
    
    def test_get_cache_key_with_very_long_prompt(self, client):
        """Test cache key generation with very long prompt."""
        long_prompt = "a" * 1000  # Very long prompt
        
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt=long_prompt
        )
        
        cache_key = client._get_cache_key(request)
        
        assert isinstance(cache_key, int)
        # Cache key should be generated from first 100 chars
    
    @pytest.mark.asyncio
    async def test_benchmark_with_zero_requests(self, client):
        """Test benchmark_performance with zero requests."""
        result = await client.benchmark_performance(num_requests=0)
        
        # Should handle gracefully
        assert "sequential_time" in result
        assert "concurrent_time" in result
        assert isinstance(result["performance_improvement_percent"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])