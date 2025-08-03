"""
Unit tests for AnyIO API client

Tests the AnyIO structured concurrency implementation for API clients
including OpenAI and Google clients with performance validation.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import List, Dict, Any

from src.core.anyio_api_client import (
    AnyIOOpenAIClient,
    AnyIOGoogleClient,
    AnyIOAPIClient,
    AsyncAPIRequest,
    AsyncAPIResponse,
    AsyncAPIRequestType,
    ConcurrencyMetrics,
    create_anyio_api_client
)


# Mock configurations
@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'api': {
            'openai_model': 'text-embedding-3-small',
            'max_concurrent_requests': 5
        }
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI async client"""
    mock_client = Mock()
    mock_embeddings = Mock()
    mock_chat = Mock()
    mock_completions = Mock()
    
    # Setup embedding response
    mock_embedding_response = Mock()
    mock_embedding_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
    mock_embeddings.create = AsyncMock(return_value=mock_embedding_response)
    
    # Setup completion response
    mock_completion_response = Mock()
    mock_completion_response.choices = [Mock(message=Mock(content="Test response"))]
    mock_completions.create = AsyncMock(return_value=mock_completion_response)
    
    mock_client.embeddings = mock_embeddings
    mock_client.chat = mock_chat
    mock_chat.completions = mock_completions
    
    return mock_client


@pytest.fixture
def mock_google_model():
    """Mock Google Generative AI model"""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Google AI response"
    
    # Make generate_content a regular function, not async
    mock_model.generate_content = Mock(return_value=mock_response)
    
    return mock_model


class TestConcurrencyMetrics:
    """Test ConcurrencyMetrics data structure"""
    
    def test_concurrency_metrics_creation(self):
        """Test creating ConcurrencyMetrics"""
        metrics = ConcurrencyMetrics(
            total_requests=10,
            successful_requests=8,
            failed_requests=2,
            total_time=5.0,
            average_time_per_request=0.5,
            concurrency_efficiency=0.8
        )
        
        assert metrics.total_requests == 10
        assert metrics.successful_requests == 8
        assert metrics.failed_requests == 2
        assert metrics.total_time == 5.0
        assert metrics.average_time_per_request == 0.5
        assert metrics.concurrency_efficiency == 0.8


class TestAsyncAPIRequest:
    """Test AsyncAPIRequest data structure"""
    
    def test_async_api_request_creation(self):
        """Test creating AsyncAPIRequest"""
        request = AsyncAPIRequest(
            service_type="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            prompt="Test prompt",
            max_tokens=100,
            temperature=0.7,
            model="text-embedding-3-small"
        )
        
        assert request.service_type == "openai"
        assert request.request_type == AsyncAPIRequestType.EMBEDDING
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 100
        assert request.temperature == 0.7
        assert request.model == "text-embedding-3-small"


class TestAsyncAPIResponse:
    """Test AsyncAPIResponse data structure"""
    
    def test_async_api_response_success(self):
        """Test creating successful AsyncAPIResponse"""
        response = AsyncAPIResponse(
            success=True,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data=[0.1, 0.2, 0.3],
            response_time=1.5,
            tokens_used=50
        )
        
        assert response.success is True
        assert response.service_used == "openai"
        assert response.request_type == AsyncAPIRequestType.EMBEDDING
        assert response.response_data == [0.1, 0.2, 0.3]
        assert response.response_time == 1.5
        assert response.tokens_used == 50
        assert response.error is None
        assert response.fallback_used is False
        
    def test_async_api_response_error(self):
        """Test creating error AsyncAPIResponse"""
        response = AsyncAPIResponse(
            success=False,
            service_used="openai",
            request_type=AsyncAPIRequestType.EMBEDDING,
            response_data=None,
            response_time=0.5,
            error="API rate limit exceeded"
        )
        
        assert response.success is False
        assert response.response_data is None
        assert response.error == "API rate limit exceeded"


class TestAnyIOOpenAIClient:
    """Test AnyIO OpenAI client implementation"""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_config):
        """Test OpenAI client initialization"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = Mock()
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    
                    assert client.api_key == "test-key"
                    assert client.max_concurrent_requests == 10
                    assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_concurrent(self, mock_config, mock_openai_client):
        """Test concurrent embedding generation"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = mock_openai_client
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    
                    texts = ["Text 1", "Text 2", "Text 3"]
                    embeddings, metrics = await client.generate_embeddings_concurrent(texts)
                    
                    # Check results
                    assert len(embeddings) == 3
                    assert all(isinstance(emb, list) for emb in embeddings)
                    
                    # Check metrics
                    assert isinstance(metrics, ConcurrencyMetrics)
                    assert metrics.total_requests == 3
                    assert metrics.successful_requests == 3
                    assert metrics.failed_requests == 0
                    assert metrics.concurrency_efficiency == 1.0
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_list(self, mock_config):
        """Test embedding generation with empty input"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = AnyIOOpenAIClient(api_key="test-key")
            
            embeddings, metrics = await client.generate_embeddings_concurrent([])
            
            assert embeddings == []
            assert metrics.total_requests == 0
            assert metrics.successful_requests == 0
            assert metrics.concurrency_efficiency == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_completions_concurrent(self, mock_config, mock_openai_client):
        """Test concurrent completion generation"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = mock_openai_client
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    
                    prompts = ["Prompt 1", "Prompt 2"]
                    completions, metrics = await client.generate_completions_concurrent(prompts, max_tokens=50)
                    
                    # Check results
                    assert len(completions) == 2
                    assert all(isinstance(comp, str) for comp in completions)
                    
                    # Check metrics
                    assert metrics.total_requests == 2
                    assert metrics.successful_requests == 2
    
    @pytest.mark.asyncio
    async def test_embedding_generation_with_failures(self, mock_config):
        """Test handling of embedding generation failures"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                mock_client = Mock()
                mock_embeddings = Mock()
                
                # First call succeeds, second fails
                mock_embeddings.create = AsyncMock(side_effect=[
                    Mock(data=[Mock(embedding=[0.1, 0.2])]),
                    Exception("API Error")
                ])
                mock_client.embeddings = mock_embeddings
                
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = mock_client
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    
                    texts = ["Text 1", "Text 2"]
                    embeddings, metrics = await client.generate_embeddings_concurrent(texts)
                    
                    # Should have one successful embedding
                    assert len(embeddings) == 1
                    assert metrics.successful_requests == 1
                    assert metrics.failed_requests == 1
                    assert metrics.concurrency_efficiency == 0.5


class TestAnyIOGoogleClient:
    """Test AnyIO Google client implementation"""
    
    @pytest.mark.asyncio
    async def test_google_client_initialization(self, mock_config):
        """Test Google client initialization"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.GOOGLE_AVAILABLE', True):
                with patch('src.core.anyio_api_client.genai') as mock_genai:
                    mock_model = Mock()
                    mock_genai.GenerativeModel.return_value = mock_model
                    
                    client = AnyIOGoogleClient(api_key="test-key")
                    
                    assert client.api_key == "test-key"
                    assert client.max_concurrent_requests == 5
                    assert client.model is not None
    
    @pytest.mark.asyncio
    async def test_generate_content_concurrent(self, mock_config, mock_google_model):
        """Test concurrent content generation"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.GOOGLE_AVAILABLE', True):
                with patch('src.core.anyio_api_client.genai') as mock_genai:
                    mock_genai.GenerativeModel.return_value = mock_google_model
                    mock_genai.configure = Mock()
                    
                    client = AnyIOGoogleClient(api_key="test-key")
                    
                    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
                    content, metrics = await client.generate_content_concurrent(prompts)
                    
                    # Check results
                    assert len(content) == 3
                    assert all(isinstance(text, str) for text in content)
                    
                    # Check metrics
                    assert metrics.total_requests == 3
                    assert metrics.successful_requests == 3
    
    @pytest.mark.asyncio
    async def test_generate_content_empty_prompts(self, mock_config):
        """Test content generation with empty prompts"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            client = AnyIOGoogleClient(api_key="test-key")
            
            content, metrics = await client.generate_content_concurrent([])
            
            assert content == []
            assert metrics.total_requests == 0
            assert metrics.concurrency_efficiency == 0.0


class TestAnyIOAPIClient:
    """Test unified AnyIO API client"""
    
    @pytest.mark.asyncio
    async def test_unified_client_initialization(self, mock_config):
        """Test unified client initialization"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'GOOGLE_API_KEY': 'google-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                with patch('src.core.anyio_api_client.GOOGLE_AVAILABLE', True):
                    with patch('src.core.anyio_api_client.AnyIOOpenAIClient') as mock_openai:
                        with patch('src.core.anyio_api_client.AnyIOGoogleClient') as mock_google:
                            mock_openai.return_value = Mock()
                            mock_google.return_value = Mock()
                            
                            client = AnyIOAPIClient()
                            
                            assert client.openai_client is not None
                            assert client.google_client is not None
    
    @pytest.mark.asyncio
    async def test_process_requests_concurrent(self, mock_config):
        """Test processing multiple requests concurrently"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                mock_openai_client = Mock()
                mock_openai_client.generate_embeddings_concurrent = AsyncMock(
                    return_value=([[0.1, 0.2]], Mock())
                )
                
                with patch('src.core.anyio_api_client.AnyIOOpenAIClient') as mock_openai_class:
                    mock_openai_class.return_value = mock_openai_client
                    
                    client = AnyIOAPIClient()
                    
                    requests = [
                        AsyncAPIRequest(
                            service_type="openai",
                            request_type=AsyncAPIRequestType.EMBEDDING,
                            prompt="Test prompt 1"
                        ),
                        AsyncAPIRequest(
                            service_type="openai",
                            request_type=AsyncAPIRequestType.EMBEDDING,
                            prompt="Test prompt 2"
                        )
                    ]
                    
                    responses, metrics = await client.process_requests_concurrent(requests)
                    
                    assert len(responses) == 2
                    assert all(isinstance(resp, AsyncAPIResponse) for resp in responses)
                    assert metrics.total_requests == 2
    
    @pytest.mark.asyncio
    async def test_benchmark_performance(self, mock_config):
        """Test performance benchmarking"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                mock_openai_client = Mock()
                mock_openai_client.generate_embeddings_concurrent = AsyncMock(
                    return_value=([[0.1, 0.2]], Mock(concurrency_efficiency=1.0, average_time_per_request=0.1))
                )
                
                with patch('src.core.anyio_api_client.AnyIOOpenAIClient') as mock_openai_class:
                    mock_openai_class.return_value = mock_openai_client
                    
                    client = AnyIOAPIClient()
                    
                    results = await client.benchmark_performance(num_requests=5)
                    
                    assert "anyio_implementation" in results
                    assert "metrics" in results
                    assert results["anyio_implementation"]["total_time"] > 0
                    assert results["metrics"]["total_requests"] == 5


class TestPerformanceAndConcurrency:
    """Test performance and concurrency aspects"""
    
    @pytest.mark.asyncio
    async def test_semaphore_concurrency_control(self, mock_config):
        """Test that semaphore properly controls concurrency"""
        call_times = []
        
        async def mock_embedding_call(*args, **kwargs):
            call_times.append(time.time())
            await asyncio.sleep(0.1)  # Simulate API call delay
            return Mock(data=[Mock(embedding=[0.1, 0.2])])
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                mock_client = Mock()
                mock_embeddings = Mock()
                mock_embeddings.create = mock_embedding_call
                mock_client.embeddings = mock_embeddings
                
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = mock_client
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    client.max_concurrent_requests = 2  # Limit concurrency to 2
                    
                    # Send 5 requests
                    texts = [f"Text {i}" for i in range(5)]
                    start_time = time.time()
                    
                    embeddings, metrics = await client.generate_embeddings_concurrent(texts)
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    # With concurrency limit of 2 and 0.1s per call, should take at least 0.3s
                    # (3 batches: 2 + 2 + 1)
                    assert total_time >= 0.25  # Some tolerance for timing
                    assert len(embeddings) == 5
    
    @pytest.mark.asyncio
    async def test_structured_concurrency_error_handling(self, mock_config):
        """Test that structured concurrency properly handles errors"""
        call_count = 0
        
        async def mock_embedding_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return Mock(data=[Mock(embedding=[0.1, 0.2])])
            else:
                raise Exception("API Error")
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                mock_client = Mock()
                mock_embeddings = Mock()
                mock_embeddings.create = mock_embedding_call
                mock_client.embeddings = mock_embeddings
                
                with patch('src.core.anyio_api_client.openai.AsyncOpenAI') as mock_openai:
                    mock_openai.return_value = mock_client
                    
                    client = AnyIOOpenAIClient(api_key="test-key")
                    
                    texts = [f"Text {i}" for i in range(5)]
                    embeddings, metrics = await client.generate_embeddings_concurrent(texts)
                    
                    # Should have 2 successful embeddings, 3 failures
                    assert len(embeddings) == 2
                    assert metrics.successful_requests == 2
                    assert metrics.failed_requests == 3


class TestCreateAnyIOAPIClient:
    """Test factory function for creating API client"""
    
    def test_create_anyio_api_client(self, mock_config):
        """Test creating API client via factory function"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.anyio_api_client.OPENAI_AVAILABLE', True):
                with patch('src.core.anyio_api_client.AnyIOAPIClient') as mock_client_class:
                    mock_client_class.return_value = Mock()
                    
                    client = create_anyio_api_client()
                    
                    assert client is not None
                    mock_client_class.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_openai_client_no_api_key(self):
        """Test OpenAI client initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AnyIOOpenAIClient()
            
            assert "OpenAI API key is required" in str(exc_info.value)
    
    def test_google_client_no_api_key(self):
        """Test Google client initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AnyIOGoogleClient()
            
            assert "Google API key is required" in str(exc_info.value)
    
    def test_unified_client_no_clients_available(self):
        """Test unified client when no API clients are available"""
        with patch('src.core.anyio_api_client.AnyIOOpenAIClient') as mock_openai:
            with patch('src.core.anyio_api_client.AnyIOGoogleClient') as mock_google:
                mock_openai.side_effect = Exception("OpenAI not available")
                mock_google.side_effect = Exception("Google not available")
                
                with pytest.raises(RuntimeError) as exc_info:
                    AnyIOAPIClient()
                
                assert "No API clients available" in str(exc_info.value)