#!/usr/bin/env python3
"""
Unit tests for AsyncEnhancedAPIClient - Step 1: Basic Setup and Initialization Tests

This file tests the core initialization and basic functionality of the async API client.
Part of comprehensive 80%+ coverage unit testing suite.
"""

import pytest
import asyncio
import time
import os
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


class TestAsyncEnhancedAPIClientBasics:
    """Test basic initialization and configuration of AsyncEnhancedAPIClient."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager for testing."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {
            "openai_model": "text-embedding-3-small",
            "gemini_model": "gemini-2.0-flash-exp"
        }
        return mock_config
    
    def test_init_basic(self, mock_config_manager):
        """Test basic initialization of AsyncEnhancedAPIClient."""
        client = AsyncEnhancedAPIClient(config_manager=mock_config_manager)
        
        assert client.config_manager == mock_config_manager
        assert client.openai_client is None
        assert client.gemini_client is None
        assert client.session_initialized is False
        assert client.processing_active is False
        assert len(client.response_cache) == 0
        assert client.performance_metrics["total_requests"] == 0
    
    def test_init_without_config_manager(self):
        """Test initialization without config manager uses default."""
        with patch('src.core.async_api_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config
            mock_config.get_api_config.return_value = {}
            
            client = AsyncEnhancedAPIClient()
            
            assert client.config_manager == mock_config
            mock_get_config.assert_called_once()
    
    def test_rate_limits_configuration(self, mock_config_manager):
        """Test rate limiting semaphores are configured correctly."""
        client = AsyncEnhancedAPIClient(config_manager=mock_config_manager)
        
        # Check rate limit semaphores exist and have correct values
        assert "openai" in client.rate_limits
        assert "gemini" in client.rate_limits
        assert client.rate_limits["openai"]._value == 25
        assert client.rate_limits["gemini"]._value == 15
    
    def test_performance_metrics_initialization(self, mock_config_manager):
        """Test performance metrics are properly initialized."""
        client = AsyncEnhancedAPIClient(config_manager=mock_config_manager)
        
        expected_metrics = {
            "total_requests": 0,
            "concurrent_requests": 0,
            "batch_requests": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        
        for key, expected_value in expected_metrics.items():
            assert client.performance_metrics[key] == expected_value
        
        # Check connection pool stats exist
        assert "connection_pool_stats" in client.performance_metrics
        pool_stats = client.performance_metrics["connection_pool_stats"]
        assert "active_connections" in pool_stats
        assert "idle_connections" in pool_stats
        assert "pool_utilization" in pool_stats
        assert "connection_reuse_rate" in pool_stats


class TestAsyncAPIRequestResponse:
    """Test AsyncAPIRequest and AsyncAPIResponse data classes."""
    
    def test_async_api_request_creation(self):
        """Test AsyncAPIRequest creation with required fields."""
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="test prompt"
        )
        
        assert request.service_type == "openai"
        assert request.request_type == AsyncAPIRequestType.EMBEDDING
        assert request.prompt == "test prompt"
        assert request.max_tokens is None
        assert request.temperature is None
        assert request.model is None
        assert request.additional_params is None
    
    def test_async_api_request_with_optional_params(self):
        """Test AsyncAPIRequest creation with optional parameters."""
        request = AsyncAPIRequest(
            service_type="gemini",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            prompt="test prompt",
            max_tokens=100,
            temperature=0.7,
            model="gemini-pro",
            additional_params={"top_p": 0.9}
        )
        
        assert request.service_type == "gemini"
        assert request.request_type == AsyncAPIRequestType.TEXT_GENERATION
        assert request.prompt == "test prompt"
        assert request.max_tokens == 100
        assert request.temperature == 0.7
        assert request.model == "gemini-pro"
        assert request.additional_params == {"top_p": 0.9}
    
    def test_async_api_response_success(self):
        """Test AsyncAPIResponse creation for successful response."""
        response = AsyncAPIResponse(
            success=True,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data={"embedding": [0.1, 0.2, 0.3]},
            response_time=1.5,
            tokens_used=10
        )
        
        assert response.success is True
        assert response.service_used == "openai"
        assert response.request_type == AsyncAPIRequestType.EMBEDDING
        assert response.response_data == {"embedding": [0.1, 0.2, 0.3]}
        assert response.response_time == 1.5
        assert response.tokens_used == 10
        assert response.error is None
        assert response.fallback_used is False
    
    def test_async_api_response_failure(self):
        """Test AsyncAPIResponse creation for failed response."""
        response = AsyncAPIResponse(
            success=False,
            service_used="gemini",
            request_type=AsyncAPIRequestType.TEXT_GENERATION,
            response_data=None,
            response_time=2.0,
            error="API rate limit exceeded",
            fallback_used=True
        )
        
        assert response.success is False
        assert response.service_used == "gemini"
        assert response.request_type == AsyncAPIRequestType.TEXT_GENERATION
        assert response.response_data is None
        assert response.response_time == 2.0
        assert response.error == "API rate limit exceeded"
        assert response.fallback_used is True
        assert response.tokens_used is None


class TestAsyncAPIRequestType:
    """Test AsyncAPIRequestType enumeration."""
    
    def test_enum_values(self):
        """Test all enum values exist and have correct string values."""
        assert AsyncAPIRequestType.TEXT_GENERATION.value == "text_generation"
        assert AsyncAPIRequestType.EMBEDDING.value == "embedding"
        assert AsyncAPIRequestType.CLASSIFICATION.value == "classification"
        assert AsyncAPIRequestType.COMPLETION.value == "completion"
        assert AsyncAPIRequestType.CHAT.value == "chat"
    
    def test_enum_comparison(self):
        """Test enum comparison and equality."""
        assert AsyncAPIRequestType.EMBEDDING == AsyncAPIRequestType.EMBEDDING
        assert AsyncAPIRequestType.EMBEDDING != AsyncAPIRequestType.TEXT_GENERATION
        assert AsyncAPIRequestType.COMPLETION != AsyncAPIRequestType.CHAT


class TestAsyncOpenAIClient:
    """Test AsyncOpenAIClient initialization and basic functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager for OpenAI client testing."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {
            "openai_model": "text-embedding-3-small"
        }
        return mock_config
    
    def test_init_with_api_key(self, mock_config_manager):
        """Test OpenAI client initialization with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            client = AsyncOpenAIClient(config_manager=mock_config_manager)
            
            assert client.api_key == "test_key"
            assert client.model == "text-embedding-3-small"
            assert client.config_manager == mock_config_manager
    
    def test_init_without_api_key(self, mock_config_manager):
        """Test OpenAI client initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                AsyncOpenAIClient(config_manager=mock_config_manager)
    
    def test_init_with_provided_api_key(self, mock_config_manager):
        """Test OpenAI client initialization with provided API key."""
        client = AsyncOpenAIClient(api_key="provided_key", config_manager=mock_config_manager)
        
        assert client.api_key == "provided_key"
        assert client.model == "text-embedding-3-small"
    
    @patch('src.core.async_api_client.OPENAI_AVAILABLE', False)
    def test_init_without_openai_library(self, mock_config_manager):
        """Test OpenAI client initialization when OpenAI library not available."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            client = AsyncOpenAIClient(config_manager=mock_config_manager)
            
            assert client.client is None
            assert client.api_key == "test_key"


class TestAsyncGeminiClient:
    """Test AsyncGeminiClient initialization and basic functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Mock configuration manager for Gemini client testing."""
        mock_config = Mock()
        mock_config.get_api_config.return_value = {
            "gemini_model": "gemini-2.0-flash-exp"
        }
        return mock_config
    
    def test_init_with_google_api_key(self, mock_config_manager):
        """Test Gemini client initialization with Google API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "google_test_key"}):
            client = AsyncGeminiClient(config_manager=mock_config_manager)
            
            assert client.api_key == "google_test_key"
            assert client.model_name == "gemini-2.0-flash-exp"
            assert client.config_manager == mock_config_manager
    
    def test_init_with_gemini_api_key(self, mock_config_manager):
        """Test Gemini client initialization with Gemini API key."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini_test_key"}):
            client = AsyncGeminiClient(config_manager=mock_config_manager)
            
            assert client.api_key == "gemini_test_key"
            assert client.model_name == "gemini-2.0-flash-exp"
    
    def test_init_without_api_key(self, mock_config_manager):
        """Test Gemini client initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Google/Gemini API key is required"):
                AsyncGeminiClient(config_manager=mock_config_manager)
    
    def test_init_with_provided_api_key(self, mock_config_manager):
        """Test Gemini client initialization with provided API key."""
        client = AsyncGeminiClient(api_key="provided_gemini_key", config_manager=mock_config_manager)
        
        assert client.api_key == "provided_gemini_key"
        assert client.model_name == "gemini-2.0-flash-exp"
    
    @patch('src.core.async_api_client.GOOGLE_AVAILABLE', False)
    def test_init_without_google_library(self, mock_config_manager):
        """Test Gemini client initialization when Google library not available."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            client = AsyncGeminiClient(config_manager=mock_config_manager)
            
            assert client.model is None
            assert client.api_key == "test_key"


class TestAsyncEnhancedAPIClientInitialization:
    """Test AsyncEnhancedAPIClient client initialization methods."""
    
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
    async def test_initialize_clients_basic(self, client):
        """Test basic client initialization."""
        with patch.dict(os.environ, {}, clear=True):
            await client.initialize_clients()
            
            assert client.session_initialized is True
            assert client.http_session is not None
            assert client.openai_client is None
            assert client.gemini_client is None
    
    @pytest.mark.asyncio
    async def test_initialize_clients_with_openai(self, client):
        """Test client initialization with OpenAI API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}):
            with patch('src.core.async_api_client.AsyncOpenAIClient') as mock_openai:
                mock_openai.return_value = Mock()
                
                await client.initialize_clients()
                
                assert client.session_initialized is True
                assert client.openai_client is not None
                mock_openai.assert_called_once_with(config_manager=client.config_manager)
    
    @pytest.mark.asyncio
    async def test_initialize_clients_with_gemini(self, client):
        """Test client initialization with Gemini API key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_google_key"}):
            with patch('src.core.async_api_client.AsyncGeminiClient') as mock_gemini:
                mock_gemini.return_value = Mock()
                
                await client.initialize_clients()
                
                assert client.session_initialized is True
                assert client.gemini_client is not None
                mock_gemini.assert_called_once_with(config_manager=client.config_manager)
    
    @pytest.mark.asyncio
    async def test_initialize_clients_with_both_apis(self, client):
        """Test client initialization with both OpenAI and Gemini API keys."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai", "GOOGLE_API_KEY": "test_google"}):
            with patch('src.core.async_api_client.AsyncOpenAIClient') as mock_openai:
                with patch('src.core.async_api_client.AsyncGeminiClient') as mock_gemini:
                    mock_openai.return_value = Mock()
                    mock_gemini.return_value = Mock()
                    
                    await client.initialize_clients()
                    
                    assert client.session_initialized is True
                    assert client.openai_client is not None
                    assert client.gemini_client is not None
                    assert client.processing_active is True
    
    @pytest.mark.asyncio
    async def test_close_clients(self, client):
        """Test proper cleanup of client resources."""
        # Initialize clients first
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch('src.core.async_api_client.AsyncOpenAIClient') as mock_openai:
                mock_openai_instance = Mock()
                mock_openai_instance.close = AsyncMock()
                mock_openai.return_value = mock_openai_instance
                
                await client.initialize_clients()
                
                # Test close
                await client.close()
                
                assert client.processing_active is False
                assert len(client.response_cache) == 0
                mock_openai_instance.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])