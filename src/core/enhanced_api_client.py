"""Enhanced API Client with LiteLLM Universal Model Support

This module provides a unified API client that handles authentication,
rate limiting, and automatic model fallbacks using LiteLLM.

CRITICAL IMPLEMENTATION: Replaces fragmented API clients with universal LLM integration
"""

import os
import time
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion
import litellm

from .api_auth_manager import APIAuthManager, APIServiceType, APIAuthError
from .logging_config import get_logger


class APIRequestType(Enum):
    """Types of API requests"""
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    COMPLETION = "completion"
    CHAT = "chat"


class TriggerCondition(Enum):
    """Conditions that trigger model fallback"""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit" 
    ERROR = "error"
    TOKEN_LIMIT = "token_limit"


@dataclass
class ModelConfig:
    """Configuration for LLM models"""
    name: str
    litellm_name: str
    supports_structured_output: bool
    max_tokens: int


@dataclass
class APIRequest:
    """API request configuration"""
    service_type: str
    request_type: APIRequestType
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class APIResponse:
    """API response wrapper"""
    success: bool
    service_used: str
    request_type: APIRequestType
    response_data: Any
    response_time: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    fallback_used: bool = False


class EnhancedAPIClient:
    """Enhanced API client with LiteLLM universal model support
    
    Implements universal LLM integration with automatic fallbacks:
    - Supports all major LLM providers via LiteLLM
    - Automatic model fallbacks on failure/rate limits
    - Maintains backward compatibility with existing interfaces
    - Centralized configuration and credentials management
    """
    
    def __init__(self, auth_manager: APIAuthManager = None, config_path: Optional[str] = None):
        """Initialize enhanced API client with LiteLLM
        
        Args:
            auth_manager: APIAuthManager instance (for backward compatibility)
            config_path: Path to configuration file
        """
        self.auth_manager = auth_manager
        self.logger = get_logger("core.enhanced_api_client")
        
        # Load environment configuration
        self._load_environment(config_path)
        
        # Load model configurations
        self.api_keys = self._load_api_keys()
        self.models = self._load_model_configs()
        self.fallback_config = self._load_fallback_config()
        
        # Configure LiteLLM
        self._configure_litellm()
        
        self.logger.info(f"EnhancedAPIClient initialized with {len(self.models)} models")
    
    def _load_environment(self, config_path: Optional[str] = None):
        """Load environment configuration"""
        if config_path:
            load_dotenv(config_path)
        else:
            # Try to load from standard locations
            current_env = Path(__file__).parent.parent.parent / '.env'
            if current_env.exists():
                load_dotenv(current_env)
            else:
                load_dotenv()
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            'openai': os.getenv('OPENAI_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY')
        }
    
    def _load_model_configs(self) -> Dict[str, ModelConfig]:
        """Load model configurations from environment"""
        models = {}
        
        # Default model configurations
        default_models = {
            'gpt_4_turbo': 'gpt-4-turbo,true,8192',
            'gpt_4o_mini': 'gpt-4o-mini,true,4096', 
            'claude_sonnet_4': 'claude-3-5-sonnet-20241022,false,8192',
            'gemini_flash': 'gemini/gemini-1.5-flash,false,8192'
        }
        
        # Load from environment or use defaults
        for model_key, default_config in default_models.items():
            config_str = os.getenv(model_key.upper(), default_config)
            parts = config_str.split(',')
            if len(parts) >= 3:
                models[model_key] = ModelConfig(
                    name=model_key,
                    litellm_name=parts[0],
                    supports_structured_output=parts[1].lower() == 'true',
                    max_tokens=int(parts[2])
                )
        
        return models
    
    def _load_fallback_config(self) -> Dict[str, Any]:
        """Load fallback configuration"""
        return {
            'primary_model': os.getenv('PRIMARY_MODEL', 'gpt_4o_mini'),
            'fallback_models': [
                os.getenv('FALLBACK_MODEL_1', 'gemini_flash'),
                os.getenv('FALLBACK_MODEL_2', 'claude_sonnet_4')
            ],
            'timeout_seconds': int(os.getenv('TIMEOUT_SECONDS', '30')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'fallback_on_rate_limit': True,
            'fallback_on_timeout': True,
            'fallback_on_error': True
        }
    
    def _configure_litellm(self):
        """Configure LiteLLM with API keys"""
        if self.api_keys['openai']:
            os.environ['OPENAI_API_KEY'] = self.api_keys['openai']
        if self.api_keys['gemini']:
            os.environ['GEMINI_API_KEY'] = self.api_keys['gemini']
        if self.api_keys['anthropic']:
            os.environ['ANTHROPIC_API_KEY'] = self.api_keys['anthropic']
    
    def make_request(self, service: str = None, request_type: str = None, prompt: str = None, 
                     messages: List[Dict] = None, max_tokens: int = None, temperature: float = None,
                     model: str = None, request: APIRequest = None, use_fallback: bool = True, **kwargs) -> APIResponse:
        """Make API request with LiteLLM universal model support
        
        Supports both direct parameters and APIRequest object for backward compatibility.
        Automatically handles model fallbacks using LiteLLM.
        
        Args:
            service: Service name (backward compatibility - maps to model)
            request_type: Type of request ('text_generation', 'chat_completion', 'embedding')
            prompt: Text prompt for generation
            messages: List of messages for chat completion
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            model: Model name to use
            request: APIRequest object (alternative to individual parameters)
            use_fallback: Whether to use fallback models if primary fails
            **kwargs: Additional parameters
            
        Returns:
            APIResponse with results
        """
        start_time = time.time()
        
        # Handle both calling conventions
        if request is not None:
            # Use provided APIRequest object
            api_request = request
            req_messages = self._build_messages_from_request(api_request)
            req_model = api_request.model
            req_max_tokens = api_request.max_tokens
            req_temperature = api_request.temperature
            req_type = api_request.request_type
        else:
            # Build from parameters
            req_type = self._map_request_type(request_type)
            req_model = model
            req_max_tokens = max_tokens
            req_temperature = temperature
            
            # Build messages from prompt or messages
            if messages:
                req_messages = messages
            elif prompt:
                req_messages = [{"role": "user", "content": prompt}]
            else:
                raise ValueError("Must provide either 'prompt' or 'messages'")
        
        # Determine primary model and fallbacks
        primary_model = req_model or self.fallback_config['primary_model']
        fallback_models = self.fallback_config['fallback_models'] if use_fallback else []
        
        # Build model sequence
        models_to_try = [primary_model] + fallback_models
        
        # Try each model in sequence
        attempts = []
        for attempt_num, model_name in enumerate(models_to_try):
            model_config = self._get_model_config(model_name)
            if not model_config:
                self.logger.warning(f"Model config not found for {model_name}, skipping")
                continue
            
            try:
                response = self._try_litellm_completion(
                    model_config, req_messages, req_max_tokens, req_temperature, **kwargs
                )
                
                # Record successful attempt
                attempts.append({
                    "model": model_config.litellm_name,
                    "attempt": attempt_num + 1,
                    "success": True,
                    "duration": time.time() - start_time
                })
                
                return APIResponse(
                    success=True,
                    service_used=model_config.litellm_name,
                    request_type=req_type,
                    response_data=response.choices[0].message.content,
                    response_time=time.time() - start_time,
                    tokens_used=getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None,
                    fallback_used=attempt_num > 0
                )
                
            except Exception as e:
                # Record failed attempt
                attempts.append({
                    "model": model_config.litellm_name,
                    "attempt": attempt_num + 1,
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - start_time
                })
                
                self.logger.warning(f"Model {model_config.litellm_name} failed: {str(e)}")
                
                # Check if we should continue to fallback
                if not self._should_fallback(e) or attempt_num == len(models_to_try) - 1:
                    break
        
        # All models failed
        return APIResponse(
            success=False,
            service_used=models_to_try[0] if models_to_try else "unknown",
            request_type=req_type,
            response_data=None,
            response_time=time.time() - start_time,
            error=f"All models failed. Attempts: {len(attempts)}"
        )
    
    def _get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        # Try exact match first
        if model_name in self.models:
            return self.models[model_name]
        
        # Try to find by litellm name
        for config in self.models.values():
            if config.litellm_name == model_name:
                return config
        
        return None
    
    def _map_request_type(self, request_type: str) -> APIRequestType:
        """Map request type string to enum"""
        request_type_map = {
            "text_generation": APIRequestType.TEXT_GENERATION,
            "chat_completion": APIRequestType.CHAT,
            "chat": APIRequestType.CHAT,
            "embedding": APIRequestType.EMBEDDING,
            "completion": APIRequestType.COMPLETION
        }
        
        result = request_type_map.get(request_type)
        if not result:
            raise ValueError(f"Unsupported request type: {request_type}")
        return result
    
    def _build_messages_from_request(self, request: APIRequest) -> List[Dict]:
        """Build messages from APIRequest object"""
        if request.prompt:
            return [{"role": "user", "content": request.prompt}]
        else:
            raise ValueError("APIRequest must have prompt")
    
    def _should_fallback(self, error: Exception) -> bool:
        """Determine if we should fallback based on error"""
        error_str = str(error).lower()
        
        # Check for rate limits
        if 'rate limit' in error_str or 'rate_limit' in error_str or '429' in error_str:
            return self.fallback_config['fallback_on_rate_limit']
        
        # Check for timeouts
        if 'timeout' in error_str or 'timed out' in error_str:
            return self.fallback_config['fallback_on_timeout']
        
        # Check for token limits
        if 'token limit' in error_str or 'max_tokens' in error_str or 'context length' in error_str:
            return True
        
        # General error fallback
        return self.fallback_config['fallback_on_error']
    
    def _try_litellm_completion(self, model_config: ModelConfig, messages: List[Dict], 
                               max_tokens: Optional[int], temperature: Optional[float], **kwargs):
        """Try to make completion using LiteLLM"""
        params = {
            "model": model_config.litellm_name,
            "messages": messages,
            "timeout": self.fallback_config['timeout_seconds']
        }
        
        # Add optional parameters
        if max_tokens:
            params["max_tokens"] = min(max_tokens, model_config.max_tokens)
        if temperature is not None:
            params["temperature"] = temperature
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make the LiteLLM call
        return completion(**params)
    
