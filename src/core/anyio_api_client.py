"""AnyIO API Client with Structured Concurrency

Migration from asyncio.gather to AnyIO structured concurrency for improved
performance, better error handling, and proper resource management.
Targets >1.5x performance improvement through structured concurrency.
"""

import anyio
import aiohttp
import time
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import os
import ssl
from contextlib import asynccontextmanager

from .api_auth_manager import APIAuthManager, APIServiceType, APIAuthError
from .logging_config import get_logger
from src.core.config_manager import ConfigurationManager, get_config

# Optional import for OpenAI async client
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Optional import for Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = get_logger("core.anyio_api_client")


class AsyncAPIRequestType(Enum):
    """Types of async API requests"""
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    COMPLETION = "completion"
    CHAT = "chat"


@dataclass
class AsyncAPIRequest:
    """Async API request configuration"""
    service_type: str
    request_type: AsyncAPIRequestType
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class AsyncAPIResponse:
    """Async API response wrapper"""
    success: bool
    service_used: str
    request_type: AsyncAPIRequestType
    response_data: Any
    response_time: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    fallback_used: bool = False


@dataclass
class ConcurrencyMetrics:
    """Metrics for concurrent operations"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    average_time_per_request: float
    concurrency_efficiency: float


class AnyIOOpenAIClient:
    """AnyIO-based OpenAI client with structured concurrency"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("core.anyio_openai_client")
        self.max_concurrent_requests = 10  # Configurable concurrency limit
        
        # Get API key from config or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        # Get API configuration
        self.api_config = self.config_manager.get_api_config()
        self.model = self.api_config.get("openai_model", "text-embedding-3-small")
        
        # Initialize async client if available
        if OPENAI_AVAILABLE:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            self.logger.warning("OpenAI async client not available")
            
        self.logger.info("AnyIO OpenAI client initialized")
    
    async def generate_embeddings_concurrent(self, texts: List[str]) -> Tuple[List[List[float]], ConcurrencyMetrics]:
        """Generate embeddings for multiple texts using AnyIO structured concurrency
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Tuple of (embeddings, metrics)
        """
        if not texts:
            return [], ConcurrencyMetrics(0, 0, 0, 0.0, 0.0, 0.0)
            
        start_time = time.time()
        embeddings = [None] * len(texts)
        successful_requests = 0
        failed_requests = 0
        
        async with anyio.create_task_group() as tg:
            semaphore = anyio.Semaphore(self.max_concurrent_requests)
            
            for i, text in enumerate(texts):
                tg.start_soon(self._generate_single_embedding, semaphore, i, text, embeddings)
        
        # Count successful/failed requests
        for embedding in embeddings:
            if embedding is not None:
                successful_requests += 1
            else:
                failed_requests += 1
        
        total_time = time.time() - start_time
        metrics = ConcurrencyMetrics(
            total_requests=len(texts),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_time_per_request=total_time / len(texts) if texts else 0,
            concurrency_efficiency=successful_requests / len(texts) if texts else 0
        )
        
        # Filter out None values (failed requests)
        valid_embeddings = [emb for emb in embeddings if emb is not None]
        
        self.logger.info(f"Generated {len(valid_embeddings)} embeddings in {total_time:.2f}s "
                        f"(efficiency: {metrics.concurrency_efficiency:.2%})")
        
        return valid_embeddings, metrics
    
    async def _generate_single_embedding(self, semaphore: anyio.Semaphore, index: int, 
                                       text: str, results: List):
        """Generate single embedding with semaphore control"""
        async with semaphore:
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                results[index] = response.data[0].embedding
            except Exception as e:
                self.logger.error(f"Failed to generate embedding for text {index}: {e}")
                results[index] = None
    
    async def generate_completions_concurrent(self, prompts: List[str], 
                                            max_tokens: int = 100) -> Tuple[List[str], ConcurrencyMetrics]:
        """Generate completions for multiple prompts using structured concurrency
        
        Args:
            prompts: List of prompts
            max_tokens: Maximum tokens per completion
            
        Returns:
            Tuple of (completions, metrics)
        """
        if not prompts:
            return [], ConcurrencyMetrics(0, 0, 0, 0.0, 0.0, 0.0)
            
        start_time = time.time()
        completions = [None] * len(prompts)
        successful_requests = 0
        failed_requests = 0
        
        async with anyio.create_task_group() as tg:
            semaphore = anyio.Semaphore(self.max_concurrent_requests)
            
            for i, prompt in enumerate(prompts):
                tg.start_soon(self._generate_single_completion, semaphore, i, prompt, 
                            max_tokens, completions)
        
        # Count results
        for completion in completions:
            if completion is not None:
                successful_requests += 1
            else:
                failed_requests += 1
        
        total_time = time.time() - start_time
        metrics = ConcurrencyMetrics(
            total_requests=len(prompts),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_time_per_request=total_time / len(prompts) if prompts else 0,
            concurrency_efficiency=successful_requests / len(prompts) if prompts else 0
        )
        
        # Filter out None values
        valid_completions = [comp for comp in completions if comp is not None]
        
        self.logger.info(f"Generated {len(valid_completions)} completions in {total_time:.2f}s "
                        f"(efficiency: {metrics.concurrency_efficiency:.2%})")
        
        return valid_completions, metrics
    
    async def _generate_single_completion(self, semaphore: anyio.Semaphore, index: int,
                                        prompt: str, max_tokens: int, results: List):
        """Generate single completion with semaphore control"""
        async with semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                results[index] = response.choices[0].message.content
            except Exception as e:
                self.logger.error(f"Failed to generate completion for prompt {index}: {e}")
                results[index] = None


class AnyIOGoogleClient:
    """AnyIO-based Google client with structured concurrency"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("core.anyio_google_client")
        self.max_concurrent_requests = 5  # Lower limit for Google API
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
            
        # Configure Gemini
        if GOOGLE_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            self.logger.warning("Google Generative AI not available")
            
        self.logger.info("AnyIO Google client initialized")
    
    async def generate_content_concurrent(self, prompts: List[str]) -> Tuple[List[str], ConcurrencyMetrics]:
        """Generate content for multiple prompts using structured concurrency
        
        Args:
            prompts: List of prompts
            
        Returns:
            Tuple of (generated_content, metrics)
        """
        if not prompts:
            return [], ConcurrencyMetrics(0, 0, 0, 0.0, 0.0, 0.0)
            
        if not self.model:
            raise RuntimeError("Gemini model not available")
        
        start_time = time.time()
        content = [None] * len(prompts)
        successful_requests = 0
        failed_requests = 0
        
        async with anyio.create_task_group() as tg:
            semaphore = anyio.Semaphore(self.max_concurrent_requests)
            
            for i, prompt in enumerate(prompts):
                tg.start_soon(self._generate_single_content, semaphore, i, prompt, content)
        
        # Count results
        for result in content:
            if result is not None:
                successful_requests += 1
            else:
                failed_requests += 1
        
        total_time = time.time() - start_time
        metrics = ConcurrencyMetrics(
            total_requests=len(prompts),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_time_per_request=total_time / len(prompts) if prompts else 0,
            concurrency_efficiency=successful_requests / len(prompts) if prompts else 0
        )
        
        # Filter out None values
        valid_content = [c for c in content if c is not None]
        
        self.logger.info(f"Generated {len(valid_content)} content pieces in {total_time:.2f}s "
                        f"(efficiency: {metrics.concurrency_efficiency:.2%})")
        
        return valid_content, metrics
    
    async def _generate_single_content(self, semaphore: anyio.Semaphore, index: int,
                                     prompt: str, results: List):
        """Generate single content with semaphore control"""
        async with semaphore:
            try:
                # Use anyio.to_thread for blocking operations
                response = await anyio.to_thread.run_sync(
                    self.model.generate_content, prompt
                )
                results[index] = response.text
            except Exception as e:
                self.logger.error(f"Failed to generate content for prompt {index}: {e}")
                results[index] = None


class AnyIOAPIClient:
    """Unified AnyIO API client with structured concurrency"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("core.anyio_api_client")
        
        # Initialize clients
        self.openai_client = None
        self.google_client = None
        
        # Try to initialize OpenAI client
        try:
            self.openai_client = AnyIOOpenAIClient(config_manager=self.config_manager)
        except Exception as e:
            self.logger.warning(f"OpenAI client not available: {e}")
        
        # Try to initialize Google client
        try:
            self.google_client = AnyIOGoogleClient(config_manager=self.config_manager)
        except Exception as e:
            self.logger.warning(f"Google client not available: {e}")
        
        if not self.openai_client and not self.google_client:
            raise RuntimeError("No API clients available")
            
        self.logger.info("AnyIO API client initialized")
    
    async def process_requests_concurrent(self, requests: List[AsyncAPIRequest]) -> Tuple[List[AsyncAPIResponse], ConcurrencyMetrics]:
        """Process multiple API requests concurrently using structured concurrency
        
        Args:
            requests: List of API requests
            
        Returns:
            Tuple of (responses, metrics)
        """
        if not requests:
            return [], ConcurrencyMetrics(0, 0, 0, 0.0, 0.0, 0.0)
        
        start_time = time.time()
        responses = [None] * len(requests)
        successful_requests = 0
        failed_requests = 0
        
        # Use structured concurrency with task group
        async with anyio.create_task_group() as tg:
            semaphore = anyio.Semaphore(10)  # Limit concurrent requests
            
            for i, request in enumerate(requests):
                tg.start_soon(self._process_single_request, semaphore, i, request, responses)
        
        # Count results
        for response in responses:
            if response and response.success:
                successful_requests += 1
            else:
                failed_requests += 1
        
        total_time = time.time() - start_time
        metrics = ConcurrencyMetrics(
            total_requests=len(requests),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            average_time_per_request=total_time / len(requests) if requests else 0,
            concurrency_efficiency=successful_requests / len(requests) if requests else 0
        )
        
        # Filter out None values
        valid_responses = [r for r in responses if r is not None]
        
        self.logger.info(f"Processed {len(valid_responses)} requests in {total_time:.2f}s "
                        f"(efficiency: {metrics.concurrency_efficiency:.2%})")
        
        return valid_responses, metrics
    
    async def _process_single_request(self, semaphore: anyio.Semaphore, index: int,
                                    request: AsyncAPIRequest, results: List):
        """Process single API request with semaphore control"""
        async with semaphore:
            start_time = time.time()
            try:
                # Route request to appropriate client
                if request.service_type == "openai" and self.openai_client:
                    if request.request_type == AsyncAPIRequestType.EMBEDDING:
                        embeddings, _ = await self.openai_client.generate_embeddings_concurrent([request.prompt])
                        response_data = embeddings[0] if embeddings else None
                    else:
                        completions, _ = await self.openai_client.generate_completions_concurrent(
                            [request.prompt], request.max_tokens or 100
                        )
                        response_data = completions[0] if completions else None
                    
                    response_time = time.time() - start_time
                    results[index] = AsyncAPIResponse(
                        success=response_data is not None,
                        service_used="openai",
                        request_type=request.request_type,
                        response_data=response_data,
                        response_time=response_time
                    )
                    
                elif request.service_type == "google" and self.google_client:
                    content, _ = await self.google_client.generate_content_concurrent([request.prompt])
                    response_data = content[0] if content else None
                    
                    response_time = time.time() - start_time
                    results[index] = AsyncAPIResponse(
                        success=response_data is not None,
                        service_used="google",
                        request_type=request.request_type,
                        response_data=response_data,
                        response_time=response_time
                    )
                    
                else:
                    response_time = time.time() - start_time
                    results[index] = AsyncAPIResponse(
                        success=False,
                        service_used="none",
                        request_type=request.request_type,
                        response_data=None,
                        response_time=response_time,
                        error="No suitable client available"
                    )
                    
            except Exception as e:
                response_time = time.time() - start_time
                self.logger.error(f"Failed to process request {index}: {e}")
                results[index] = AsyncAPIResponse(
                    success=False,
                    service_used="error",
                    request_type=request.request_type,
                    response_data=None,
                    response_time=response_time,
                    error=str(e)
                )
    
    async def benchmark_performance(self, num_requests: int = 100) -> Dict[str, Any]:
        """Benchmark AnyIO vs traditional async performance
        
        Args:
            num_requests: Number of test requests
            
        Returns:
            Performance benchmark results
        """
        self.logger.info(f"Starting performance benchmark with {num_requests} requests")
        
        # Create test requests
        test_requests = [
            AsyncAPIRequest(
                service_type="openai",
                request_type=AsyncAPIRequestType.EMBEDDING,
                prompt=f"Test prompt {i}"
            )
            for i in range(num_requests)
        ]
        
        # Benchmark AnyIO implementation
        start_time = time.time()
        responses, metrics = await self.process_requests_concurrent(test_requests)
        anyio_time = time.time() - start_time
        
        benchmark_results = {
            "anyio_implementation": {
                "total_time": anyio_time,
                "requests_per_second": len(responses) / anyio_time if anyio_time > 0 else 0,
                "success_rate": metrics.concurrency_efficiency,
                "average_request_time": metrics.average_time_per_request
            },
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "concurrency_efficiency": metrics.concurrency_efficiency
            }
        }
        
        self.logger.info(f"Benchmark complete: {len(responses)} requests in {anyio_time:.2f}s "
                        f"({len(responses)/anyio_time:.1f} req/s)")
        
        return benchmark_results


# Factory function for creating AnyIO API client
def create_anyio_api_client(config_manager: ConfigurationManager = None) -> AnyIOAPIClient:
    """Create AnyIO API client instance
    
    Args:
        config_manager: Optional configuration manager
        
    Returns:
        Configured AnyIO API client
    """
    return AnyIOAPIClient(config_manager)