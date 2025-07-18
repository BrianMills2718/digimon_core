"""Async API Client for Enhanced Performance

This module provides async versions of API clients for improved performance
with concurrent requests. Implements Phase 1 async optimization to achieve
15-20% performance gains as specified in the roadmap.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import os

from .api_auth_manager import APIAuthManager, APIServiceType, APIAuthError
from .logging_config import get_logger
from .config import ConfigurationManager

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


class AsyncOpenAIClient:
    """Async OpenAI client for embeddings and completions"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("core.async_openai_client")
        
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
            
        self.logger.info("Async OpenAI client initialized")
    
    async def create_embeddings(self, texts: List[str], model: str = None) -> List[List[float]]:
        """Create embeddings for multiple texts asynchronously"""
        if not self.client:
            raise RuntimeError("OpenAI async client not available")
            
        model = model or self.model
        
        try:
            # Create embeddings in parallel for better performance
            start_time = time.time()
            
            # Split into batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=model,
                    input=batch
                )
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Small delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            self.logger.info(f"Created {len(all_embeddings)} embeddings in {response_time:.2f}s")
            
            return all_embeddings
            
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {e}")
            raise
    
    async def create_single_embedding(self, text: str, model: str = None) -> List[float]:
        """Create embedding for a single text"""
        embeddings = await self.create_embeddings([text], model)
        return embeddings[0]
    
    async def create_completion(self, prompt: str, model: str = "gpt-3.5-turbo", 
                               max_tokens: int = 150, temperature: float = 0.7) -> str:
        """Create a completion using OpenAI API"""
        if not self.client:
            raise RuntimeError("OpenAI async client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error creating completion: {e}")
            raise
    
    async def close(self):
        """Close the async client"""
        if self.client:
            await self.client.close()


class AsyncGeminiClient:
    """Async Gemini client for text generation"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("core.async_gemini_client")
        
        # Get API key from config or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google/Gemini API key is required")
            
        # Get API configuration
        self.api_config = self.config_manager.get_api_config()
        self.model_name = self.api_config.get("gemini_model", "gemini-2.0-flash-exp")
        
        # Initialize Gemini client if available
        if GOOGLE_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
            self.logger.warning("Google Generative AI not available")
            
        self.logger.info("Async Gemini client initialized")
    
    async def generate_content(self, prompt: str, max_tokens: int = None, 
                              temperature: float = None) -> str:
        """Generate content using Gemini API"""
        if not self.model:
            raise RuntimeError("Gemini model not available")
        
        try:
            # Note: The Google Generative AI library doesn't have native async support
            # We'll use asyncio.to_thread to run the synchronous call in a thread
            start_time = time.time()
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            response_time = time.time() - start_time
            self.logger.info(f"Generated content in {response_time:.2f}s")
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            raise
    
    async def generate_multiple_content(self, prompts: List[str]) -> List[str]:
        """Generate content for multiple prompts concurrently"""
        if not self.model:
            raise RuntimeError("Gemini model not available")
        
        try:
            # Use asyncio.gather to run multiple requests concurrently
            tasks = [self.generate_content(prompt) for prompt in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions that occurred
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Error in concurrent generation: {result}")
                    processed_results.append("")
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Error in concurrent generation: {e}")
            raise


class AsyncEnhancedAPIClient:
    """Enhanced async API client with multiple service support"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("core.async_enhanced_api_client")
        
        # Initialize clients
        self.openai_client = None
        self.gemini_client = None
        
        # Rate limiting
        self.rate_limits = {
            "openai": asyncio.Semaphore(10),  # 10 concurrent requests
            "gemini": asyncio.Semaphore(5)    # 5 concurrent requests
        }
        
        self.logger.info("Async Enhanced API client initialized")
    
    async def initialize_clients(self):
        """Initialize API clients asynchronously"""
        try:
            # Initialize OpenAI client
            if os.getenv("OPENAI_API_KEY"):
                self.openai_client = AsyncOpenAIClient(config_manager=self.config_manager)
                self.logger.info("OpenAI async client initialized")
            
            # Initialize Gemini client
            if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
                self.gemini_client = AsyncGeminiClient(config_manager=self.config_manager)
                self.logger.info("Gemini async client initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing clients: {e}")
            raise
    
    async def create_embeddings(self, texts: List[str], service: str = "openai") -> List[List[float]]:
        """Create embeddings using specified service"""
        if service == "openai" and self.openai_client:
            async with self.rate_limits["openai"]:
                return await self.openai_client.create_embeddings(texts)
        else:
            raise ValueError(f"Service {service} not available for embeddings")
    
    async def generate_content(self, prompt: str, service: str = "gemini") -> str:
        """Generate content using specified service"""
        if service == "gemini" and self.gemini_client:
            async with self.rate_limits["gemini"]:
                return await self.gemini_client.generate_content(prompt)
        elif service == "openai" and self.openai_client:
            async with self.rate_limits["openai"]:
                return await self.openai_client.create_completion(prompt)
        else:
            raise ValueError(f"Service {service} not available for content generation")
    
    async def process_batch(self, requests: List[AsyncAPIRequest]) -> List[AsyncAPIResponse]:
        """Process multiple API requests concurrently"""
        start_time = time.time()
        
        # Group requests by service type
        openai_requests = [r for r in requests if r.service_type == "openai"]
        gemini_requests = [r for r in requests if r.service_type == "gemini"]
        
        # Create tasks for each service
        tasks = []
        
        # Process OpenAI requests
        if openai_requests:
            tasks.append(self._process_openai_batch(openai_requests))
        
        # Process Gemini requests
        if gemini_requests:
            tasks.append(self._process_gemini_batch(gemini_requests))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_responses = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch processing error: {result}")
            else:
                all_responses.extend(result)
        
        total_time = time.time() - start_time
        self.logger.info(f"Processed {len(requests)} requests in {total_time:.2f}s")
        
        return all_responses
    
    async def _process_openai_batch(self, requests: List[AsyncAPIRequest]) -> List[AsyncAPIResponse]:
        """Process OpenAI requests in batch"""
        if not self.openai_client:
            return []
        
        responses = []
        for request in requests:
            try:
                start_time = time.time()
                
                if request.request_type == AsyncAPIRequestType.EMBEDDING:
                    result = await self.openai_client.create_single_embedding(request.prompt)
                    response_data = {"embedding": result}
                elif request.request_type == AsyncAPIRequestType.COMPLETION:
                    result = await self.openai_client.create_completion(
                        request.prompt,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature
                    )
                    response_data = {"text": result}
                else:
                    raise ValueError(f"Unsupported request type: {request.request_type}")
                
                response_time = time.time() - start_time
                
                responses.append(AsyncAPIResponse(
                    success=True,
                    service_used="openai",
                    request_type=request.request_type,
                    response_data=response_data,
                    response_time=response_time
                ))
                
            except Exception as e:
                responses.append(AsyncAPIResponse(
                    success=False,
                    service_used="openai",
                    request_type=request.request_type,
                    response_data=None,
                    response_time=0.0,
                    error=str(e)
                ))
        
        return responses
    
    async def _process_gemini_batch(self, requests: List[AsyncAPIRequest]) -> List[AsyncAPIResponse]:
        """Process Gemini requests in batch"""
        if not self.gemini_client:
            return []
        
        responses = []
        for request in requests:
            try:
                start_time = time.time()
                
                if request.request_type == AsyncAPIRequestType.TEXT_GENERATION:
                    result = await self.gemini_client.generate_content(request.prompt)
                    response_data = {"text": result}
                else:
                    raise ValueError(f"Unsupported request type: {request.request_type}")
                
                response_time = time.time() - start_time
                
                responses.append(AsyncAPIResponse(
                    success=True,
                    service_used="gemini",
                    request_type=request.request_type,
                    response_data=response_data,
                    response_time=response_time
                ))
                
            except Exception as e:
                responses.append(AsyncAPIResponse(
                    success=False,
                    service_used="gemini",
                    request_type=request.request_type,
                    response_data=None,
                    response_time=0.0,
                    error=str(e)
                ))
        
        return responses
    
    async def close(self):
        """Close all async clients"""
        if self.openai_client:
            await self.openai_client.close()
        
        self.logger.info("Async API clients closed")


# Global async client instance
_async_client = None


async def get_async_api_client() -> AsyncEnhancedAPIClient:
    """Get the global async API client instance"""
    global _async_client
    if _async_client is None:
        _async_client = AsyncEnhancedAPIClient()
        await _async_client.initialize_clients()
    return _async_client


async def close_async_api_client():
    """Close the global async API client"""
    global _async_client
    if _async_client is not None:
        await _async_client.close()
        _async_client = None