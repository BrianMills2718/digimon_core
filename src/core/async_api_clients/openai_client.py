from src.core.standard_config import get_model
"""
Async OpenAI Client

Optimized async client for OpenAI API operations including embeddings and completions.
"""

import asyncio
import time
import os
from typing import List, Optional

from .request_types import AsyncAPIRequestType, AsyncAPIResponse
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager, get_config

# Optional import for OpenAI async client
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AsyncOpenAIClient:
    """Async OpenAI client for embeddings and completions"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
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
    
    async def create_completion(self, prompt: str, model: str = None, 
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

    def health_check(self) -> dict:
        """Check client health status"""
        return {
            "client_available": self.client is not None,
            "api_key_configured": bool(self.api_key),
            "openai_library_available": OPENAI_AVAILABLE
        }
