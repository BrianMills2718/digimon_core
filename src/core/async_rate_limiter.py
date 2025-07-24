"""
Async-safe API Rate Limiter for GraphRAG System.

This module provides truly asynchronous rate limiting functionality 
without blocking the event loop.
"""

import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AsyncRateLimiter:
    """
    Truly asynchronous rate limiter using token bucket algorithm.
    
    Features:
    - Non-blocking async operations
    - Token bucket algorithm for smooth rate limiting
    - Per-service rate limits
    - Automatic token refill
    """
    
    def __init__(self):
        """Initialize the async rate limiter."""
        self.rate_limits: Dict[str, int] = {}
        self.token_buckets: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        self._waiters: Dict[str, list] = defaultdict(list)
        logger.info("AsyncRateLimiter initialized")
    
    async def set_rate_limit(self, service_name: str, calls_per_minute: int) -> None:
        """
        Set rate limit for a service.
        
        Args:
            service_name: Name of the service
            calls_per_minute: Maximum calls allowed per minute
        """
        async with self._lock:
            self.rate_limits[service_name] = calls_per_minute
            
            # Initialize token bucket
            self.token_buckets[service_name] = {
                'tokens': float(calls_per_minute),
                'capacity': float(calls_per_minute),
                'refill_rate': calls_per_minute / 60.0,  # tokens per second
                'last_refill': time.time()
            }
            
            logger.info(f"Set rate limit for {service_name}: {calls_per_minute} calls/min")
    
    async def acquire(self, service_name: str = "default", timeout: Optional[float] = None) -> None:
        """
        Acquire permission to make an API call.
        
        Args:
            service_name: Name of the service
            timeout: Maximum time to wait for permission (seconds)
            
        Raises:
            asyncio.TimeoutError: If timeout is exceeded
        """
        if timeout:
            await asyncio.wait_for(self._acquire(service_name), timeout)
        else:
            await self._acquire(service_name)
    
    async def _acquire(self, service_name: str) -> None:
        """Internal method to acquire a token."""
        while True:
            async with self._lock:
                if self._try_consume_token(service_name):
                    return
                
                # No tokens available, need to wait
                wait_time = self._calculate_wait_time(service_name)
            
            # Wait without holding the lock
            await asyncio.sleep(wait_time)
    
    def _try_consume_token(self, service_name: str) -> bool:
        """
        Try to consume a token from the bucket.
        
        Note: Must be called while holding the lock.
        
        Returns:
            True if token was consumed, False otherwise
        """
        if service_name not in self.token_buckets:
            # No rate limit set, allow the call
            return True
        
        bucket = self.token_buckets[service_name]
        current_time = time.time()
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket['last_refill']
        tokens_to_add = time_elapsed * bucket['refill_rate']
        
        # Update token count (cap at capacity)
        bucket['tokens'] = min(bucket['capacity'], bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        
        # Try to consume a token
        if bucket['tokens'] >= 1.0:
            bucket['tokens'] -= 1.0
            return True
        
        return False
    
    def _calculate_wait_time(self, service_name: str) -> float:
        """
        Calculate how long to wait for the next token.
        
        Note: Must be called while holding the lock.
        
        Returns:
            Wait time in seconds
        """
        if service_name not in self.token_buckets:
            return 0.0
        
        bucket = self.token_buckets[service_name]
        
        # Calculate time until we have at least 1 token
        tokens_needed = 1.0 - bucket['tokens']
        wait_time = tokens_needed / bucket['refill_rate']
        
        # Add small buffer to avoid race conditions
        return wait_time + 0.001
    
    async def get_availability(self, service_name: str) -> Dict[str, any]:
        """
        Get current availability information for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with availability information
        """
        async with self._lock:
            if service_name not in self.token_buckets:
                return {
                    'available': True,
                    'tokens': float('inf'),
                    'wait_time': 0.0
                }
            
            # Refill tokens to get current state
            bucket = self.token_buckets[service_name]
            current_time = time.time()
            time_elapsed = current_time - bucket['last_refill']
            tokens_to_add = time_elapsed * bucket['refill_rate']
            current_tokens = min(bucket['capacity'], bucket['tokens'] + tokens_to_add)
            
            wait_time = 0.0
            if current_tokens < 1.0:
                wait_time = self._calculate_wait_time(service_name)
            
            return {
                'available': current_tokens >= 1.0,
                'tokens': current_tokens,
                'wait_time': wait_time,
                'capacity': bucket['capacity'],
                'refill_rate': bucket['refill_rate']
            }
    
    async def reset(self, service_name: Optional[str] = None) -> None:
        """
        Reset rate limiter for a service or all services.
        
        Args:
            service_name: Service to reset, or None for all services
        """
        async with self._lock:
            if service_name:
                if service_name in self.token_buckets:
                    bucket = self.token_buckets[service_name]
                    bucket['tokens'] = bucket['capacity']
                    bucket['last_refill'] = time.time()
                    logger.info(f"Reset rate limiter for {service_name}")
            else:
                for name, bucket in self.token_buckets.items():
                    bucket['tokens'] = bucket['capacity']
                    bucket['last_refill'] = time.time()
                logger.info("Reset all rate limiters")


class RateLimiter:
    """Backwards-compatible wrapper for AsyncRateLimiter."""
    
    def __init__(self, calls_per_second: Optional[float] = None):
        """Initialize with optional calls per second limit."""
        self._async_limiter = AsyncRateLimiter()
        self._loop = None
        self._calls_per_second = calls_per_second
        
        if calls_per_second:
            # Convert to calls per minute
            calls_per_minute = int(calls_per_second * 60)
            try:
                asyncio.get_running_loop()
                # We're in an async context
                asyncio.create_task(
                    self._async_limiter.set_rate_limit("default", calls_per_minute)
                )
            except RuntimeError:
                # Not in async context, will set later
                pass
    
    async def acquire(self) -> None:
        """Acquire permission to make a call."""
        # Ensure rate limit is set
        if self._calls_per_second and "default" not in self._async_limiter.rate_limits:
            calls_per_minute = int(self._calls_per_second * 60)
            await self._async_limiter.set_rate_limit("default", calls_per_minute)
        
        await self._async_limiter.acquire("default")
    
    def __enter__(self):
        """Context manager entry (for sync compatibility)."""
        raise RuntimeError("Use 'async with' for RateLimiter context manager")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass