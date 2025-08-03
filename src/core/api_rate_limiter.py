"""
Production-ready API Rate Limiter for External Service Integration

Provides respectful API usage patterns with comprehensive rate limiting,
burst handling, and adaptive rate management based on API responses.

Features:
- Token bucket algorithm for smooth rate limiting
- Multiple time window enforcement (per-second, per-minute, per-hour)
- API response header parsing for dynamic limits
- 429 response handling with exponential backoff
- Burst capacity for initial request handling
- Thread-safe concurrent operation
- Comprehensive metrics collection
"""

import asyncio
import time
import threading
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import math

from .exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, service_name: str, wait_time: float):
        self.service_name = service_name
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded for {service_name}, wait {wait_time:.2f}s")


@dataclass
class RateLimitConfig:
    """Configuration for service rate limits"""
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_capacity: int = 10
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        if self.requests_per_hour <= 0:
            raise ValueError("requests_per_hour must be positive")
        if self.burst_capacity <= 0:
            raise ValueError("burst_capacity must be positive")


@dataclass
class ServiceTokenBucket:
    """Token bucket for individual service rate limiting"""
    capacity: float
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float
    
    def refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Attempt to consume tokens"""
        self.refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_tokens(self, tokens: float = 1.0) -> float:
        """Calculate time until specified tokens are available"""
        self.refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


@dataclass
class ServiceStats:
    """Statistics for a service's API usage"""
    service_name: str
    requests_made: int = 0
    requests_this_second: int = 0
    requests_this_minute: int = 0
    requests_this_hour: int = 0
    tokens_available: float = 0.0
    last_request_time: Optional[float] = None
    last_refill_time: Optional[float] = None
    remaining_requests: Optional[int] = None  # From API headers
    reset_time: Optional[int] = None  # From API headers
    retry_after: Optional[int] = None  # From 429 responses


class APIRateLimiter:
    """
    Comprehensive API rate limiter with multiple time windows and adaptive behavior.
    
    Supports:
    - Token bucket algorithm for smooth rate limiting
    - Multiple time window tracking (second, minute, hour)
    - API response header parsing
    - 429 response handling with backoff
    - Concurrent request handling
    """
    
    def __init__(self, service_configs: Optional[Dict[str, RateLimitConfig]] = None):
        """
        Initialize API rate limiter.
        
        Args:
            service_configs: Dictionary mapping service names to their rate limit configs
        """
        self.service_configs = service_configs or {}
        self.token_buckets: Dict[str, ServiceTokenBucket] = {}
        self.service_stats: Dict[str, ServiceStats] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())
        self.forced_delays: Dict[str, float] = {}  # For 429 responses
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize configured services
        for service_name, config in self.service_configs.items():
            self._initialize_service(service_name, config)
        
        logger.debug(f"APIRateLimiter initialized with {len(self.service_configs)} services")
    
    def _initialize_service(self, service_name: str, config: RateLimitConfig) -> None:
        """Initialize rate limiting for a service"""
        with self._lock:
            # Create token bucket
            self.token_buckets[service_name] = ServiceTokenBucket(
                capacity=config.burst_capacity,
                tokens=config.burst_capacity,
                refill_rate=config.requests_per_second,
                last_refill=time.time()
            )
            
            # Initialize stats
            self.service_stats[service_name] = ServiceStats(service_name=service_name)
            
            # Initialize request history
            self.request_history[service_name] = deque()
            
            logger.debug(f"Initialized rate limiting for {service_name}")
    
    async def acquire(self, service_name: str, tokens: float = 1.0) -> None:
        """
        Acquire tokens for API request, waiting if necessary.
        
        Args:
            service_name: Name of the service
            tokens: Number of tokens to acquire
            
        Raises:
            RateLimitExceededError: If rate limit would be exceeded
        """
        # Initialize service with default config if not configured
        if service_name not in self.token_buckets:
            self._initialize_service(service_name, RateLimitConfig())
        
        # Check for forced delay from 429 responses
        with self._lock:
            if service_name in self.forced_delays:
                forced_delay_until = self.forced_delays[service_name]
                current_time = time.time()
                
                if current_time < forced_delay_until:
                    wait_time = forced_delay_until - current_time
                    logger.warning(f"Forced delay for {service_name}: {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    # Remove expired delay
                    del self.forced_delays[service_name]
        
        # Attempt to acquire tokens
        bucket = self.token_buckets[service_name]
        
        # Wait until tokens are available
        while True:
            with self._lock:
                if bucket.consume(tokens):
                    self._record_request(service_name)
                    logger.debug(f"Acquired {tokens} tokens for {service_name}")
                    return
                
                # Calculate wait time
                wait_time = bucket.time_until_tokens(tokens)
            
            if wait_time > 0:
                logger.debug(f"Waiting {wait_time:.2f}s for tokens for {service_name}")
                await asyncio.sleep(min(wait_time, 1.0))  # Cap at 1 second increments
    
    async def wait_for_availability(self, service_name: str) -> float:
        """
        Get the time to wait until next request can be made.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Time to wait in seconds
        """
        if service_name not in self.token_buckets:
            return 0.0
        
        with self._lock:
            # Check forced delays first
            if service_name in self.forced_delays:
                forced_delay_until = self.forced_delays[service_name]
                current_time = time.time()
                if current_time < forced_delay_until:
                    return forced_delay_until - current_time
            
            # Check token availability
            bucket = self.token_buckets[service_name]
            return bucket.time_until_tokens(1.0)
    
    def update_from_headers(self, service_name: str, headers: Dict[str, str]) -> None:
        """
        Update rate limits based on API response headers.
        
        Args:
            service_name: Name of the service
            headers: HTTP response headers
        """
        with self._lock:
            if service_name not in self.service_stats:
                self.service_stats[service_name] = ServiceStats(service_name=service_name)
            
            stats = self.service_stats[service_name]
            
            # Parse common rate limit headers
            if 'X-RateLimit-Remaining' in headers:
                try:
                    stats.remaining_requests = int(headers['X-RateLimit-Remaining'])
                except ValueError:
                    pass
            
            if 'X-RateLimit-Reset' in headers:
                try:
                    stats.reset_time = int(headers['X-RateLimit-Reset'])
                except ValueError:
                    pass
            
            if 'Retry-After' in headers:
                try:
                    stats.retry_after = int(headers['Retry-After'])
                except ValueError:
                    pass
            
            logger.debug(f"Updated rate limits for {service_name} from headers")
    
    def handle_429_response(self, service_name: str, retry_after: Optional[int] = None) -> None:
        """
        Handle 429 Too Many Requests response.
        
        Args:
            service_name: Name of the service
            retry_after: Retry-After header value in seconds
        """
        with self._lock:
            if retry_after is None:
                # Use exponential backoff if no retry-after specified
                retry_after = 60  # Default to 1 minute
            
            # Set forced delay
            self.forced_delays[service_name] = time.time() + retry_after
            
            # Update stats
            if service_name not in self.service_stats:
                self.service_stats[service_name] = ServiceStats(service_name=service_name)
            
            self.service_stats[service_name].retry_after = retry_after
            
            logger.warning(f"Handling 429 for {service_name}, waiting {retry_after}s")
    
    def _record_request(self, service_name: str) -> None:
        """Record a successful request"""
        current_time = time.time()
        
        # Add to request history
        self.request_history[service_name].append(current_time)
        
        # Clean old history (keep last hour)
        cutoff_time = current_time - 3600
        while (self.request_history[service_name] and 
               self.request_history[service_name][0] < cutoff_time):
            self.request_history[service_name].popleft()
        
        # Update stats
        if service_name not in self.service_stats:
            self.service_stats[service_name] = ServiceStats(service_name=service_name)
        
        stats = self.service_stats[service_name]
        stats.requests_made += 1
        stats.last_request_time = current_time
        
        # Count requests in different time windows
        second_cutoff = current_time - 1
        minute_cutoff = current_time - 60
        hour_cutoff = current_time - 3600
        
        history = self.request_history[service_name]
        stats.requests_this_second = len([t for t in history if t > second_cutoff])
        stats.requests_this_minute = len([t for t in history if t > minute_cutoff])
        stats.requests_this_hour = len([t for t in history if t > hour_cutoff])
        
        # Update token availability
        if service_name in self.token_buckets:
            bucket = self.token_buckets[service_name]
            bucket.refill()
            stats.tokens_available = bucket.tokens
            stats.last_refill_time = bucket.last_refill
    
    def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """
        Get statistics for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dictionary containing service statistics
        """
        with self._lock:
            if service_name not in self.service_stats:
                # Return default stats for unknown service
                return {
                    'service_name': service_name,
                    'requests_made': 0,
                    'requests_this_second': 0,
                    'requests_this_minute': 0,
                    'requests_this_hour': 0,
                    'tokens_available': 0.0,
                    'last_request_time': None,
                    'last_refill_time': None
                }
            
            stats = self.service_stats[service_name]
            
            # Update token availability
            if service_name in self.token_buckets:
                bucket = self.token_buckets[service_name]
                bucket.refill()
                stats.tokens_available = bucket.tokens
                stats.last_refill_time = bucket.last_refill
            
            return {
                'service_name': stats.service_name,
                'requests_made': stats.requests_made,
                'requests_this_second': stats.requests_this_second,
                'requests_this_minute': stats.requests_this_minute,
                'requests_this_hour': stats.requests_this_hour,
                'tokens_available': stats.tokens_available,
                'last_request_time': stats.last_request_time,
                'last_refill_time': stats.last_refill_time,
                'remaining_requests': stats.remaining_requests,
                'reset_time': stats.reset_time,
                'retry_after': stats.retry_after
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all services.
        
        Returns:
            Dictionary mapping service names to their statistics
        """
        return {
            service_name: self.get_service_stats(service_name)
            for service_name in self.service_stats
        }
    
    def reset_service(self, service_name: str) -> None:
        """Reset rate limiting state for a service"""
        with self._lock:
            if service_name in self.token_buckets:
                config = self.service_configs.get(service_name, RateLimitConfig())
                bucket = self.token_buckets[service_name]
                bucket.tokens = config.burst_capacity
                bucket.last_refill = time.time()
            
            if service_name in self.service_stats:
                stats = self.service_stats[service_name]
                stats.requests_made = 0
                stats.requests_this_second = 0
                stats.requests_this_minute = 0
                stats.requests_this_hour = 0
                stats.last_request_time = None
            
            if service_name in self.request_history:
                self.request_history[service_name].clear()
            
            if service_name in self.forced_delays:
                del self.forced_delays[service_name]
            
            logger.debug(f"Reset rate limiting for {service_name}")
    
    def add_service(self, service_name: str, config: RateLimitConfig) -> None:
        """Add a new service with rate limiting configuration"""
        self.service_configs[service_name] = config
        self._initialize_service(service_name, config)
        logger.info(f"Added rate limiting for {service_name}")
    
    def remove_service(self, service_name: str) -> None:
        """Remove rate limiting for a service"""
        with self._lock:
            self.service_configs.pop(service_name, None)
            self.token_buckets.pop(service_name, None)
            self.service_stats.pop(service_name, None)
            self.request_history.pop(service_name, None)
            self.forced_delays.pop(service_name, None)
            
            logger.info(f"Removed rate limiting for {service_name}")
    
    def can_make_call(self, service_name: str) -> bool:
        """
        Check if a call can be made without waiting.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if call can be made immediately
        """
        # Initialize service with default config if not configured
        if service_name not in self.token_buckets:
            self._initialize_service(service_name, RateLimitConfig())
        
        with self._lock:
            # Check for forced delay from 429 responses
            if service_name in self.forced_delays:
                forced_delay_until = self.forced_delays[service_name]
                current_time = time.time()
                if current_time < forced_delay_until:
                    return False
                else:
                    # Clean up expired delay
                    del self.forced_delays[service_name]
            
            # Check token availability
            bucket = self.token_buckets[service_name]
            bucket.refill()
            return bucket.tokens >= 1.0
    
    def record_call(self, service_name: str) -> None:
        """
        Record a call for rate limiting purposes.
        
        Args:
            service_name: Name of the service
        """
        # Initialize service with default config if not configured
        if service_name not in self.token_buckets:
            self._initialize_service(service_name, RateLimitConfig())
        
        with self._lock:
            bucket = self.token_buckets[service_name]
            bucket.consume(1.0)
            self._record_request(service_name)
    
    def set_rate_limit(self, service_name: str, requests_per_minute: int) -> None:
        """
        Set rate limit for a service.
        
        Args:
            service_name: Name of the service
            requests_per_minute: Requests per minute limit
        """
        config = RateLimitConfig(
            requests_per_second=requests_per_minute / 60.0,
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_minute * 60,
            burst_capacity=min(10, max(1, int(requests_per_minute / 6)))
        )
        
        if service_name in self.service_configs:
            # Update existing service
            self.service_configs[service_name] = config
            self._initialize_service(service_name, config)
        else:
            # Add new service
            self.add_service(service_name, config)

    def get_health_status(self) -> Dict[str, str]:
        """
        Get health status for all services.
        
        Returns:
            Dictionary mapping service names to their status
        """
        status = {}
        current_time = time.time()
        
        with self._lock:
            for service_name in self.service_configs:
                if service_name in self.forced_delays:
                    if current_time < self.forced_delays[service_name]:
                        status[service_name] = "rate_limited"
                    else:
                        status[service_name] = "healthy"
                        # Clean up expired delay
                        del self.forced_delays[service_name]
                else:
                    bucket = self.token_buckets.get(service_name)
                    if bucket and bucket.tokens < 1.0:
                        status[service_name] = "throttled"
                    else:
                        status[service_name] = "healthy"
        
        return status


# Global rate limiter instance for convenience
_global_rate_limiter: Optional[APIRateLimiter] = None


def get_global_rate_limiter() -> APIRateLimiter:
    """Get the global rate limiter instance"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = APIRateLimiter()
    return _global_rate_limiter


def configure_service_rate_limits(service_configs: Dict[str, RateLimitConfig]) -> None:
    """Configure rate limits for multiple services"""
    rate_limiter = get_global_rate_limiter()
    for service_name, config in service_configs.items():
        rate_limiter.add_service(service_name, config)