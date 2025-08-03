from src.core.standard_config import get_model
"""
Async Gemini Client

Optimized async client for Google Gemini API text generation operations.
"""

import asyncio
import time
import os
from typing import List, Optional

from .request_types import AsyncAPIRequestType, AsyncAPIResponse
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager, get_config

# Optional import for Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class AsyncGeminiClient:
    """Async Gemini client for text generation"""
    
    def __init__(self, api_key: str = None, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
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
    
    def health_check(self) -> dict:
        """Check client health status"""
        return {
            "model_available": self.model is not None,
            "api_key_configured": bool(self.api_key),
            "google_library_available": GOOGLE_AVAILABLE,
            "model_name": self.model_name
        }
