#!/usr/bin/env python3
"""
DEPRECATED: Universal LLM Service - Use EnhancedAPIClient instead

This service has been deprecated in favor of the proven EnhancedAPIClient pattern.
The EnhancedAPIClient already provides all the functionality that UniversalLLMService 
was designed to provide:
- LiteLLM integration with automatic fallbacks
- Rate limiting and error handling  
- Configuration management
- Model switching and provider abstraction
- Structured response handling

MIGRATION PATH: Replace UniversalLLMService usage with EnhancedAPIClient
"""

import warnings
warnings.warn(
    "UniversalLLMService is deprecated. Use EnhancedAPIClient instead. "
    "See src.core.enhanced_api_client for the standardized LLM client.",
    DeprecationWarning,
    stacklevel=2
)

import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from enum import Enum

try:
    from .unified_service_interface import CoreService, ServiceResponse, create_service_response
    from .config_manager import ConfigurationManager, LLMConfig
    from .circuit_breaker import CircuitBreaker
    from .production_rate_limiter import (
        ProductionRateLimiter, RateLimitConfig, 
        create_sqlite_rate_limiter, create_redis_rate_limiter
    )
    from ..universal_model_tester.universal_model_client import UniversalModelClient, TriggerCondition
except ImportError:
    # Fallback for direct execution
    from src.core.unified_service_interface import CoreService, ServiceResponse, create_service_response
    from src.core.config_manager import ConfigurationManager, LLMConfig
    from src.core.circuit_breaker import CircuitBreaker
    from src.core.production_rate_limiter import (
        ProductionRateLimiter, RateLimitConfig,
        create_sqlite_rate_limiter, create_redis_rate_limiter
    )
    from universal_model_tester.universal_model_client import UniversalModelClient, TriggerCondition

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Standard task types with predefined temperature settings."""
    EXTRACTION = "extraction"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    CLASSIFICATION = "classification"
    CONVERSATION = "conversation"

@dataclass
class LLMRequest:
    """Standardized LLM request structure."""
    prompt: str
    task_type: TaskType = TaskType.CONVERSATION
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    schema: Optional[Dict[str, Any]] = None
    fallback_models: Optional[List[str]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class LLMResponse:
    """Standardized LLM response structure."""
    content: str
    model_used: str
    task_type: TaskType
    success: bool
    attempts: int
    execution_time: float
    cost_estimate: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Legacy RateLimiter class removed - replaced by ProductionRateLimiter

class UniversalLLMService(CoreService):
    """
    Universal LLM Service providing unified interface for all LLM interactions.
    
    Features:
    - Automatic fallbacks between providers
    - Rate limiting per provider
    - Circuit breaker pattern
    - Task-specific temperature defaults
    - Structured output support
    - Comprehensive error handling
    - Performance monitoring
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.llm_config = self.config_manager.llm
        
        # Initialize universal model client
        self.client = UniversalModelClient()
        
        # Initialize production-grade rate limiter
        self.rate_limiter = None
        if self.llm_config.enable_rate_limiting:
            try:
                # Try Redis first, fallback to SQLite
                self.rate_limiter = create_redis_rate_limiter()
                logger.info("Initialized Redis rate limiter")
            except Exception:
                self.rate_limiter = create_sqlite_rate_limiter()
                logger.info("Initialized SQLite rate limiter")
            
            # Configure rate limits for each provider
            for provider, limit in self.llm_config.rate_limits.items():
                config = RateLimitConfig(
                    requests_per_minute=limit,
                    burst_allowance=int(limit * 0.1),  # 10% burst allowance
                    window_size_seconds=60,
                    max_queue_time=30.0
                )
                self.rate_limiter.configure_provider(provider, config)
        
        # Initialize circuit breakers for each provider
        self.circuit_breakers = {}
        if self.llm_config.circuit_breaker_threshold > 0:
            for provider in self.llm_config.rate_limits.keys():
                self.circuit_breakers[provider] = CircuitBreaker(
                    name=f"llm_{provider}",
                    failure_threshold=self.llm_config.circuit_breaker_threshold,
                    recovery_timeout=self.llm_config.circuit_breaker_timeout
                )
        
        # Performance tracking
        self.request_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        self._initialized = False
        
        logger.info("UniversalLLMService initialized successfully")
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize service with configuration."""
        try:
            # Validate configuration
            if not self.llm_config.fallback_chain:
                logger.error("No fallback chain configured")
                return False
            
            # Start rate limiter cleanup task
            if self.rate_limiter and not self._initialized:
                asyncio.create_task(self.rate_limiter.start_cleanup_task())
            
            self._initialized = True
            logger.info("UniversalLLMService initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize UniversalLLMService: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check service health and readiness."""
        try:
            # Basic health checks
            if not hasattr(self, 'client') or self.client is None:
                return False
            
            # Check if we have any working providers
            if not self.llm_config.fallback_chain:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and capabilities."""
        return {
            "service_name": "UniversalLLMService",
            "version": "1.0.0",
            "description": "Universal LLM interface with automatic fallbacks",
            "capabilities": [
                "text_completion",
                "structured_output",
                "automatic_fallbacks",
                "rate_limiting",
                "circuit_breaker"
            ],
            "supported_providers": list(self.llm_config.rate_limits.keys()),
            "default_model": self.llm_config.default_model,
            "fallback_models": [item["model"] for item in self.llm_config.fallback_chain],
            "task_types": [task.value for task in TaskType],
            "configuration": {
                "fallbacks_enabled": self.llm_config.enable_fallbacks,
                "rate_limiting_enabled": self.llm_config.enable_rate_limiting,
                "retry_logic_enabled": self.llm_config.enable_retry_logic
            }
        }
    
    async def get_statistics(self) -> ServiceResponse:
        """Get service performance statistics."""
        try:
            # Get rate limiter status for each provider
            rate_limiter_status = {}
            if self.rate_limiter:
                for provider in self.llm_config.rate_limits.keys():
                    try:
                        status = await self.rate_limiter.get_status(provider)
                        rate_limiter_status[provider] = status
                    except Exception as e:
                        rate_limiter_status[provider] = {"error": str(e)}
            
            # Get circuit breaker status
            circuit_breaker_status = {}
            for provider, breaker in self.circuit_breakers.items():
                circuit_breaker_status[provider] = {
                    "state": breaker.get_state(),
                    "failure_count": breaker.failure_count,
                    "last_failure_time": breaker.last_failure_time
                }
            
            stats = {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1),
                "average_response_time": self.total_execution_time / max(self.request_count, 1),
                "rate_limiter_status": rate_limiter_status,
                "circuit_breaker_status": circuit_breaker_status,
                "configuration": {
                    "default_model": self.llm_config.default_model,
                    "fallbacks_enabled": self.llm_config.enable_fallbacks,
                    "rate_limiting_enabled": self.llm_config.enable_rate_limiting,
                    "circuit_breakers_enabled": len(self.circuit_breakers) > 0
                }
            }
            
            return create_service_response(success=True, data=stats)
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return create_service_response(
                success=False,
                error_code="STATS_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up service resources."""
        try:
            # Clean up production rate limiter
            if self.rate_limiter:
                asyncio.create_task(self.rate_limiter.cleanup())
            
            # Reset circuit breakers
            for breaker in self.circuit_breakers.values():
                breaker.reset()
            
            self._initialized = False
            logger.info("UniversalLLMService cleanup completed")
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False
    
    async def complete(self, request: Union[LLMRequest, str], **kwargs) -> ServiceResponse:
        """
        Universal completion interface with automatic fallbacks.
        
        Args:
            request: LLMRequest object or simple string prompt
            **kwargs: Additional parameters that override request settings
            
        Returns:
            ServiceResponse containing LLMResponse with completion results
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Convert string to LLMRequest if needed
            if isinstance(request, str):
                request = LLMRequest(prompt=request)
            
            # Apply kwargs overrides
            for key, value in kwargs.items():
                if hasattr(request, key):
                    setattr(request, key, value)
            
            # Determine temperature from task type if not specified
            if request.temperature is None:
                request.temperature = self.llm_config.temperature_defaults.get(
                    request.task_type.value, 0.7
                )
            
            # Determine model and fallbacks
            model = request.model or self.llm_config.default_model
            fallback_models = request.fallback_models or [
                chain_item["model"] for chain_item in self.llm_config.fallback_chain[1:]
            ]
            
            # Apply production rate limiting
            provider = self._get_provider_for_model(model)
            if self.rate_limiter and provider:
                rate_limited = await self.rate_limiter.acquire(provider, max_wait_time=30.0)
                if not rate_limited:
                    return create_service_response(
                        success=False,
                        error_code="RATE_LIMIT_EXCEEDED",
                        error_message=f"Rate limit exceeded for provider {provider}"
                    )
            
            # Check circuit breaker before making request
            if provider and provider in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[provider]
                if not circuit_breaker.can_execute():
                    return create_service_response(
                        success=False,
                        error_code="CIRCUIT_BREAKER_OPEN",
                        error_message=f"Circuit breaker open for provider {provider}"
                    )
            
            # Prepare messages for universal client
            messages = [{"role": "user", "content": request.prompt}]
            
            # Configure trigger conditions for fallbacks
            trigger_conditions = []
            if self.llm_config.enable_fallbacks:
                trigger_conditions = [
                    TriggerCondition.RATE_LIMIT,
                    TriggerCondition.TIMEOUT,
                    TriggerCondition.ERROR
                ]
            
            # Execute LLM call with circuit breaker protection
            def execute_llm_call():
                return self.client.complete(
                    messages=messages,
                    model=model,
                    schema=request.schema,
                    fallback_models=fallback_models,
                    trigger_conditions=trigger_conditions,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            
            try:
                # Execute with circuit breaker if available
                if provider and provider in self.circuit_breakers:
                    circuit_breaker = self.circuit_breakers[provider]
                    result = circuit_breaker.execute(execute_llm_call)
                else:
                    result = execute_llm_call()
                
                execution_time = time.time() - start_time
                self.total_execution_time += execution_time
                
                # Mark circuit breaker success if used
                if provider and provider in self.circuit_breakers:
                    self.circuit_breakers[provider].record_success()
                
                # Create response
                response = LLMResponse(
                    content=result.get("response", ""),
                    model_used=result.get("model_used", model),
                    task_type=request.task_type,
                    success=True,
                    attempts=len(result.get("attempts", [])),
                    execution_time=execution_time,
                    token_usage=result.get("token_usage"),
                    metadata={
                        "request_metadata": request.metadata,
                        "attempts": result.get("attempts", []),
                        "provider": provider
                    }
                )
                
                return create_service_response(success=True, data=response)
                
            except Exception as llm_error:
                # Mark circuit breaker failure if used
                if provider and provider in self.circuit_breakers:
                    self.circuit_breakers[provider].record_failure()
                raise llm_error
                
        except Exception as e:
            self.error_count += 1
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            logger.error(f"LLM completion failed: {e}")
            
            # Create error response
            error_response = LLMResponse(
                content="",
                model_used=getattr(request, 'model', 'unknown') if isinstance(request, LLMRequest) else 'unknown',
                task_type=getattr(request, 'task_type', TaskType.CONVERSATION) if isinstance(request, LLMRequest) else TaskType.CONVERSATION,
                success=False,
                attempts=1,
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
            
            return create_service_response(
                success=False,
                data=error_response,
                error_code="COMPLETION_FAILED",
                error_message=str(e)
            )
    
    def _get_provider_for_model(self, model: str) -> Optional[str]:
        """Get provider name for a given model."""
        # Map common model names to providers
        if model.startswith("gpt") or model.startswith("o1") or "openai" in model.lower():
            return "openai"
        elif model.startswith("gemini") or "google" in model.lower():
            return "google"
        elif model.startswith("claude") or "anthropic" in model.lower():
            return "anthropic"
        else:
            # Try to find in provider configurations
            for provider_name, provider_config in self.llm_config.providers.items():
                if provider_config.model == model:
                    return provider_name
            return None
    
    async def _test_connectivity(self) -> bool:
        """Test connectivity to at least one LLM provider."""
        try:
            test_request = LLMRequest(
                prompt="Hello, this is a test. Please respond with 'OK'.",
                task_type=TaskType.CONVERSATION,
                max_tokens=10
            )
            
            response = await self.complete(test_request)
            return response.success
        except Exception as e:
            logger.warning(f"Connectivity test failed: {e}")
            return False

# Convenience functions for backward compatibility
async def get_llm_service() -> UniversalLLMService:
    """Get global LLM service instance."""
    # This would typically be managed by the service container
    return UniversalLLMService()

async def complete_text(prompt: str, task_type: TaskType = TaskType.CONVERSATION, **kwargs) -> str:
    """Simple completion function for backward compatibility."""
    service = await get_llm_service()
    request = LLMRequest(prompt=prompt, task_type=task_type, **kwargs)
    response = await service.complete(request)
    
    if response.success:
        return response.data.content
    else:
        raise Exception(f"LLM completion failed: {response.error_message}")