from src.core.standard_config import get_api_endpoint
"""
Async API clients for external services.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from src.core.config_manager import get_config

class AsyncOpenAIClient:
    """Async OpenAI API client."""
    
    def __init__(self):
        self.config = get_config()
        self.api_config = self.config.get_api_config('openai')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=self.api_config['timeout'])
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'Authorization': f"Bearer {self.api_config['api_key']}",
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """Create chat completion."""
        if not self.session:
            raise RuntimeError("Client not properly initialized. Use async context manager.")
        
        # Get model from config if not specified
        if model is None:
            from .standard_config import get_api_model
            model = get_api_model("openai")
        
        url = f"{self.api_config['base_url']}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def embeddings(self, texts: List[str], model: str = "text-embedding-3-small") -> Dict[str, Any]:
        """Create embeddings."""
        if not self.session:
            raise RuntimeError("Client not properly initialized. Use async context manager.")
        
        url = f"{self.api_config['base_url']}/embeddings"
        payload = {
            "model": model,
            "input": texts
        }
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

class AsyncAnthropicClient:
    """Async Anthropic API client."""
    
    def __init__(self):
        self.config = get_config()
        self.api_config = self.config.get_api_config('anthropic')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=self.api_config['timeout'])
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'x-api-key': self.api_config['api_key'],
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def messages(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        """Create message completion."""
        if not self.session:
            raise RuntimeError("Client not properly initialized. Use async context manager.")
        
        # Get model from config if not specified
        if model is None:
            from .standard_config import get_api_model
            model = get_api_model("anthropic")
        
        url = "get_api_endpoint("anthropic")/messages"
        payload = {
            "model": model,
            "max_tokens": 4000,
            "messages": messages
        }
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

class AsyncGoogleClient:
    """Async Google API client."""
    
    def __init__(self):
        self.config = get_config()
        self.api_config = self.config.get_api_config('google')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=self.api_config['timeout'])
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_content(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate content using Gemini."""
        if not self.session:
            raise RuntimeError("Client not properly initialized. Use async context manager.")
        
        # Get model from config if not specified
        if model is None:
            from .standard_config import get_api_model
            model = get_api_model("gemini")
        
        url = f"get_api_endpoint("google")/models/{model}:generateContent"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        params = {"key": self.api_config['api_key']}
        
        async with self.session.post(url, json=payload, params=params) as response:
            response.raise_for_status()
            return await response.json()