"""Test the async rate limiter implementation."""

import pytest
import asyncio
import time
from src.core.async_rate_limiter import AsyncRateLimiter, RateLimiter


class TestAsyncRateLimiter:
    """Test suite for async rate limiter."""
    
    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self):
        """Test basic rate limiting functionality."""
        limiter = AsyncRateLimiter()
        
        # Set rate limit to 6 calls per minute (0.1 per second)
        await limiter.set_rate_limit("test_service", 6)
        
        # Try to make 10 calls rapidly
        start_time = time.time()
        call_times = []
        
        for i in range(10):
            await limiter.acquire("test_service")
            call_times.append(time.time() - start_time)
        
        # First 6 calls should be immediate
        for i in range(6):
            assert call_times[i] < 0.1, f"Call {i} took {call_times[i]}s"
        
        # Remaining calls should be rate limited
        # Each should wait approximately 10 seconds (60s/6 calls)
        for i in range(6, 10):
            expected_delay = (i - 5) * 10
            assert abs(call_times[i] - expected_delay) < 1.0, \
                f"Call {i} at {call_times[i]}s, expected ~{expected_delay}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_rate_limiting(self):
        """Test rate limiting with concurrent requests."""
        limiter = AsyncRateLimiter()
        
        # Set rate limit to 10 calls per minute
        await limiter.set_rate_limit("concurrent_test", 10)
        
        # Make 20 concurrent requests
        async def make_request(request_id):
            start = time.time()
            await limiter.acquire("concurrent_test")
            return request_id, time.time() - start
        
        tasks = [make_request(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # Sort by completion time
        results.sort(key=lambda x: x[1])
        
        # First 10 should complete quickly
        for i in range(10):
            assert results[i][1] < 0.5, f"Request {results[i][0]} took {results[i][1]}s"
        
        # Next 10 should be delayed
        for i in range(10, 20):
            # Should wait at least 6 seconds (60s/10 calls)
            assert results[i][1] >= 5.5, f"Request {results[i][0]} only waited {results[i][1]}s"
    
    @pytest.mark.asyncio
    async def test_token_bucket_refill(self):
        """Test token bucket refill mechanism."""
        limiter = AsyncRateLimiter()
        
        # Set rate limit to 60 calls per minute (1 per second)
        await limiter.set_rate_limit("refill_test", 60)
        
        # Use all tokens
        for _ in range(60):
            await limiter.acquire("refill_test")
        
        # Check availability - should have no tokens
        availability = await limiter.get_availability("refill_test")
        assert not availability['available']
        assert availability['tokens'] < 1.0
        
        # Wait 2 seconds for refill
        await asyncio.sleep(2.0)
        
        # Should have ~2 tokens now
        availability = await limiter.get_availability("refill_test")
        assert availability['available']
        assert 1.5 <= availability['tokens'] <= 2.5
    
    @pytest.mark.asyncio
    async def test_no_blocking(self):
        """Test that rate limiter doesn't block event loop."""
        limiter = AsyncRateLimiter()
        
        # Set very restrictive rate limit
        await limiter.set_rate_limit("blocking_test", 1)  # 1 per minute
        
        # Counter to check event loop responsiveness
        counter = 0
        
        async def increment_counter():
            nonlocal counter
            while counter < 100:
                counter += 1
                await asyncio.sleep(0.01)
        
        # Start counter
        counter_task = asyncio.create_task(increment_counter())
        
        # Make rate-limited calls
        start = time.time()
        await limiter.acquire("blocking_test")  # First call immediate
        await limiter.acquire("blocking_test")  # Second call waits ~60s
        duration = time.time() - start
        
        # Counter should have continued running
        assert counter >= 50, f"Counter only reached {counter}, event loop was blocked"
        
        counter_task.cancel()
        try:
            await counter_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in rate limiter."""
        limiter = AsyncRateLimiter()
        
        # Set rate limit to 1 per minute
        await limiter.set_rate_limit("timeout_test", 1)
        
        # First call succeeds
        await limiter.acquire("timeout_test")
        
        # Second call with timeout should fail
        with pytest.raises(asyncio.TimeoutError):
            await limiter.acquire("timeout_test", timeout=0.5)
    
    @pytest.mark.asyncio
    async def test_reset_functionality(self):
        """Test resetting rate limiter."""
        limiter = AsyncRateLimiter()
        
        # Set rate limit and exhaust tokens
        await limiter.set_rate_limit("reset_test", 5)
        for _ in range(5):
            await limiter.acquire("reset_test")
        
        # Should be exhausted
        availability = await limiter.get_availability("reset_test")
        assert not availability['available']
        
        # Reset
        await limiter.reset("reset_test")
        
        # Should have full capacity
        availability = await limiter.get_availability("reset_test")
        assert availability['available']
        assert availability['tokens'] == availability['capacity']
    
    @pytest.mark.asyncio
    async def test_backwards_compatibility(self):
        """Test backwards-compatible RateLimiter wrapper."""
        limiter = RateLimiter(calls_per_second=2)  # 2 calls per second
        
        # Should be able to make 2 calls quickly
        start = time.time()
        await limiter.acquire()
        await limiter.acquire()
        first_two = time.time() - start
        assert first_two < 0.1
        
        # Third call should wait
        await limiter.acquire()
        third = time.time() - start
        assert third >= 0.4  # Should wait ~0.5s