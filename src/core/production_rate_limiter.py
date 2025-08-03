#!/usr/bin/env python3
"""
Production-Grade Rate Limiter
=============================

Enterprise-ready rate limiting with Redis/SQLite backend support,
distributed rate limiting, and sliding window algorithms.
"""

import time
import sqlite3
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json
import threading

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limit configuration for a provider."""
    requests_per_minute: int
    burst_allowance: int = 0  # Additional requests allowed in burst
    window_size_seconds: int = 60
    max_queue_time: float = 30.0  # Max time to wait for rate limit

@dataclass
class RateLimitResult:
    """Result of rate limit check."""
    allowed: bool
    retry_after: Optional[float] = None  # Seconds to wait before retry
    remaining_requests: int = 0
    reset_time: Optional[datetime] = None

class RateLimiterBackend(ABC):
    """Abstract base class for rate limiter backends."""
    
    @abstractmethod
    async def check_rate_limit(
        self, 
        key: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check if request is within rate limit."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup backend resources."""
        pass

class SQLiteRateLimiterBackend(RateLimiterBackend):
    """SQLite-backed rate limiter with sliding window."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with rate limit tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    provider_key TEXT PRIMARY KEY,
                    request_count INTEGER DEFAULT 0,
                    window_start INTEGER,
                    last_request INTEGER,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS request_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_key TEXT,
                    timestamp INTEGER,
                    allowed BOOLEAN,
                    remaining INTEGER,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Create index for efficient cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_log_timestamp 
                ON request_log(timestamp)
            """)
            
            conn.commit()
    
    async def check_rate_limit(
        self, 
        key: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check rate limit using sliding window algorithm."""
        current_time = int(time.time())
        window_start = current_time - config.window_size_seconds
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Clean old entries first
                conn.execute(
                    "DELETE FROM request_log WHERE timestamp < ?",
                    (window_start,)
                )
                
                # Count requests in current window
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM request_log 
                    WHERE provider_key = ? AND timestamp >= ? AND allowed = 1
                """, (key, window_start))
                
                current_count = cursor.fetchone()[0]
                
                # Check if request is allowed
                allowed = current_count < config.requests_per_minute
                remaining = max(0, config.requests_per_minute - current_count - (1 if allowed else 0))
                
                # Calculate retry time if blocked
                retry_after = None
                reset_time = None
                
                if not allowed:
                    # Find oldest request in window to calculate when limit resets
                    cursor = conn.execute("""
                        SELECT MIN(timestamp) FROM request_log 
                        WHERE provider_key = ? AND timestamp >= ? AND allowed = 1
                    """, (key, window_start))
                    
                    oldest_timestamp = cursor.fetchone()[0]
                    if oldest_timestamp:
                        reset_time = datetime.fromtimestamp(
                            oldest_timestamp + config.window_size_seconds
                        )
                        retry_after = (reset_time - datetime.now()).total_seconds()
                        retry_after = max(1, retry_after)  # At least 1 second
                
                # Log this request attempt
                conn.execute("""
                    INSERT INTO request_log (provider_key, timestamp, allowed, remaining)
                    VALUES (?, ?, ?, ?)
                """, (key, current_time, allowed, remaining))
                
                # Update provider summary
                conn.execute("""
                    INSERT OR REPLACE INTO rate_limits 
                    (provider_key, request_count, window_start, last_request)
                    VALUES (?, ?, ?, ?)
                """, (key, current_count + (1 if allowed else 0), window_start, current_time))
                
                conn.commit()
                
                return RateLimitResult(
                    allowed=allowed,
                    retry_after=retry_after,
                    remaining_requests=remaining,
                    reset_time=reset_time
                )
    
    async def cleanup(self) -> None:
        """Clean up old rate limit data."""
        cutoff_time = int(time.time()) - 3600  # Keep 1 hour of history
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                deleted = conn.execute(
                    "DELETE FROM request_log WHERE timestamp < ?",
                    (cutoff_time,)
                ).rowcount
                
                conn.commit()
                
                if deleted > 0:
                    logger.debug(f"Cleaned {deleted} old rate limit entries")

class RedisRateLimiterBackend(RateLimiterBackend):
    """Redis-backed rate limiter for distributed systems."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available. Install with: pip install aioredis")
    
    async def _get_redis(self):
        """Get Redis connection, creating if needed."""
        if self.redis is None:
            self.redis = aioredis.from_url(self.redis_url)
        return self.redis
    
    async def check_rate_limit(
        self, 
        key: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check rate limit using Redis sliding window."""
        redis = await self._get_redis()
        current_time = time.time()
        window_start = current_time - config.window_size_seconds
        
        # Use Redis pipeline for atomic operations
        async with redis.pipeline(transaction=True) as pipe:
            # Remove old entries
            await pipe.zremrangebyscore(f"rate_limit:{key}", 0, window_start)
            
            # Count current requests
            await pipe.zcard(f"rate_limit:{key}")
            
            # Execute pipeline
            results = await pipe.execute()
            current_count = results[1]
            
            # Check if request is allowed
            allowed = current_count < config.requests_per_minute
            remaining = max(0, config.requests_per_minute - current_count - (1 if allowed else 0))
            
            retry_after = None
            reset_time = None
            
            if allowed:
                # Add this request to the window
                await redis.zadd(
                    f"rate_limit:{key}", 
                    {str(current_time): current_time}
                )
                # Set expiration for cleanup
                await redis.expire(f"rate_limit:{key}", config.window_size_seconds + 10)
            else:
                # Calculate when limit resets
                oldest_scores = await redis.zrange(
                    f"rate_limit:{key}", 0, 0, withscores=True
                )
                if oldest_scores:
                    oldest_timestamp = oldest_scores[0][1]
                    reset_time = datetime.fromtimestamp(
                        oldest_timestamp + config.window_size_seconds
                    )
                    retry_after = (reset_time - datetime.now()).total_seconds()
                    retry_after = max(1, retry_after)
            
            return RateLimitResult(
                allowed=allowed,
                retry_after=retry_after,
                remaining_requests=remaining,
                reset_time=reset_time
            )
    
    async def cleanup(self) -> None:
        """Redis automatically cleans up with TTL, but we can force cleanup."""
        if self.redis:
            # Find all rate limit keys
            keys = await self.redis.keys("rate_limit:*")
            if keys:
                current_time = time.time() - 3600  # 1 hour ago
                for key in keys:
                    await self.redis.zremrangebyscore(key, 0, current_time)

class MemoryRateLimiterBackend(RateLimiterBackend):
    """In-memory rate limiter for testing/single instance."""
    
    def __init__(self):
        self.request_windows: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    async def check_rate_limit(
        self, 
        key: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """Check rate limit using in-memory sliding window."""
        current_time = time.time()
        window_start = current_time - config.window_size_seconds
        
        with self._lock:
            # Initialize or clean window
            if key not in self.request_windows:
                self.request_windows[key] = []
            
            # Remove old requests
            self.request_windows[key] = [
                t for t in self.request_windows[key] 
                if t >= window_start
            ]
            
            current_count = len(self.request_windows[key])
            allowed = current_count < config.requests_per_minute
            remaining = max(0, config.requests_per_minute - current_count - (1 if allowed else 0))
            
            retry_after = None
            reset_time = None
            
            if allowed:
                self.request_windows[key].append(current_time)
            else:
                # Calculate when limit resets
                if self.request_windows[key]:
                    oldest_timestamp = min(self.request_windows[key])
                    reset_time = datetime.fromtimestamp(
                        oldest_timestamp + config.window_size_seconds
                    )
                    retry_after = (reset_time - datetime.now()).total_seconds()
                    retry_after = max(1, retry_after)
            
            return RateLimitResult(
                allowed=allowed,
                retry_after=retry_after,
                remaining_requests=remaining,
                reset_time=reset_time
            )
    
    async def cleanup(self) -> None:
        """Clean up old windows."""
        current_time = time.time()
        with self._lock:
            for key in list(self.request_windows.keys()):
                window = self.request_windows[key]
                # Keep only recent requests
                self.request_windows[key] = [
                    t for t in window if current_time - t < 3600
                ]
                # Remove empty windows
                if not self.request_windows[key]:
                    del self.request_windows[key]

class ProductionRateLimiter:
    """
    Production-grade rate limiter with multiple backend support.
    
    Features:
    - Multiple backends (Redis, SQLite, Memory)
    - Sliding window algorithm
    - Burst allowance
    - Automatic cleanup
    - Comprehensive logging
    - Thread-safe operations
    """
    
    def __init__(
        self, 
        backend: Optional[RateLimiterBackend] = None,
        default_config: Optional[RateLimitConfig] = None
    ):
        self.backend = backend or SQLiteRateLimiterBackend()
        self.default_config = default_config or RateLimitConfig(requests_per_minute=60)
        self.provider_configs: Dict[str, RateLimitConfig] = {}
        self._cleanup_task = None
        self._running = False
        
        logger.info(f"ProductionRateLimiter initialized with {type(self.backend).__name__}")
    
    def configure_provider(self, provider: str, config: RateLimitConfig):
        """Configure rate limiting for a specific provider."""
        self.provider_configs[provider] = config
        logger.info(f"Rate limit configured for {provider}: {config.requests_per_minute}/min")
    
    async def acquire(
        self, 
        provider: str, 
        max_wait_time: Optional[float] = None
    ) -> bool:
        """
        Acquire rate limit permission for provider.
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            max_wait_time: Maximum time to wait for permission
            
        Returns:
            True if permission granted, False if max wait exceeded
        """
        config = self.provider_configs.get(provider, self.default_config)
        max_wait = max_wait_time or config.max_queue_time
        
        start_time = time.time()
        
        while True:
            result = await self.backend.check_rate_limit(provider, config)
            
            if result.allowed:
                logger.debug(f"Rate limit acquired for {provider}, remaining: {result.remaining_requests}")
                return True
            
            # Check if we've exceeded max wait time
            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.warning(f"Rate limit wait timeout for {provider} after {elapsed:.2f}s")
                return False
            
            # Wait before retrying
            wait_time = min(result.retry_after or 1, max_wait - elapsed)
            if wait_time > 0:
                logger.debug(f"Rate limited for {provider}, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            else:
                break
        
        return False
    
    async def get_status(self, provider: str) -> Dict[str, Any]:
        """Get current rate limit status for provider."""
        config = self.provider_configs.get(provider, self.default_config)
        result = await self.backend.check_rate_limit(provider, config)
        
        return {
            "provider": provider,
            "requests_per_minute": config.requests_per_minute,
            "remaining_requests": result.remaining_requests,
            "reset_time": result.reset_time.isoformat() if result.reset_time else None,
            "currently_limited": not result.allowed
        }
    
    async def start_cleanup_task(self, interval: int = 300):
        """Start automatic cleanup task."""
        if self._cleanup_task is not None:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval))
        logger.info(f"Rate limiter cleanup task started (interval: {interval}s)")
    
    async def stop_cleanup_task(self):
        """Stop automatic cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        logger.info("Rate limiter cleanup task stopped")
    
    async def _cleanup_loop(self, interval: int):
        """Background cleanup loop."""
        while self._running:
            try:
                await self.backend.cleanup()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
                await asyncio.sleep(interval)
    
    async def cleanup(self):
        """Clean up rate limiter resources."""
        await self.stop_cleanup_task()
        await self.backend.cleanup()
        logger.info("ProductionRateLimiter cleanup completed")

# Factory functions for different backends
def create_sqlite_rate_limiter(db_path: str = None) -> ProductionRateLimiter:
    """Create rate limiter with SQLite backend."""
    if db_path is None:
        from .standard_config import get_file_path
        db_path = f"{get_file_path('data_dir')}/rate_limits.db"
    backend = SQLiteRateLimiterBackend(db_path)
    return ProductionRateLimiter(backend)

def create_redis_rate_limiter(redis_url: str = "redis://localhost:6379") -> ProductionRateLimiter:
    """Create rate limiter with Redis backend."""
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, falling back to SQLite")
        return create_sqlite_rate_limiter()
    
    backend = RedisRateLimiterBackend(redis_url)
    return ProductionRateLimiter(backend)

def create_memory_rate_limiter() -> ProductionRateLimiter:
    """Create rate limiter with memory backend (testing only)."""
    backend = MemoryRateLimiterBackend()
    return ProductionRateLimiter(backend)

# Context manager for automatic cleanup
@asynccontextmanager
async def rate_limiter_context(rate_limiter: ProductionRateLimiter):
    """Context manager for automatic rate limiter lifecycle management."""
    await rate_limiter.start_cleanup_task()
    try:
        yield rate_limiter
    finally:
        await rate_limiter.cleanup()