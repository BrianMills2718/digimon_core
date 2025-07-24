"""
Test-Driven Development: API Rate Limiter Tests

Following TDD methodology for respectful API usage patterns:
1. Write tests first (RED phase)
2. Implement minimal code (GREEN phase)
3. Refactor for quality (REFACTOR phase)
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from src.core.api_rate_limiter import APIRateLimiter, RateLimitConfig, RateLimitExceededError
from src.core.exceptions import ServiceUnavailableError


class TestAPIRateLimiter:
    """Test suite for API Rate Limiter implementation"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter with test configuration"""
        return APIRateLimiter({
            'arxiv': RateLimitConfig(
                requests_per_second=2.0,
                requests_per_minute=10,
                requests_per_hour=100,
                burst_capacity=5
            ),
            'pubmed': RateLimitConfig(
                requests_per_second=3.0,
                requests_per_minute=30,
                requests_per_hour=1000,
                burst_capacity=10
            )
        })
    
    def test_rate_limit_config_creation(self):
        """Test: Rate limit configuration is created correctly"""
        config = RateLimitConfig(
            requests_per_second=1.0,
            requests_per_minute=60,
            requests_per_hour=3600,
            burst_capacity=10
        )
        
        assert config.requests_per_second == 1.0
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 3600
        assert config.burst_capacity == 10
    
    @pytest.mark.asyncio
    async def test_acquire_permits_normal_operation(self, rate_limiter):
        """Test: Normal operation allows requests within limits"""
        # Should allow initial requests up to burst capacity
        for i in range(3):
            await rate_limiter.acquire('arxiv')
            assert True  # If we get here, acquisition succeeded
    
    @pytest.mark.asyncio
    async def test_rate_limiting_enforced(self, rate_limiter):
        """Test: Rate limiting is enforced for rapid requests"""
        # Fill up burst capacity quickly
        for i in range(5):
            await rate_limiter.acquire('arxiv')
        
        # Next request should be rate limited
        start_time = time.time()
        await rate_limiter.acquire('arxiv')
        elapsed = time.time() - start_time
        
        # Should have waited at least 0.4 seconds (1/2.5 requests per second)
        assert elapsed >= 0.4
    
    @pytest.mark.asyncio
    async def test_different_services_have_independent_limits(self, rate_limiter):
        """Test: Different services have independent rate limits"""
        # Fill up arxiv capacity
        for i in range(5):
            await rate_limiter.acquire('arxiv')
        
        # PubMed should still be available immediately
        start_time = time.time()
        await rate_limiter.acquire('pubmed')
        elapsed = time.time() - start_time
        
        # Should not have waited (different service)
        assert elapsed < 0.1
    
    @pytest.mark.asyncio
    async def test_burst_capacity_handling(self, rate_limiter):
        """Test: Burst capacity allows rapid initial requests"""
        start_time = time.time()
        
        # Should handle burst requests quickly
        for i in range(5):  # Burst capacity for arxiv
            await rate_limiter.acquire('arxiv')
        
        elapsed = time.time() - start_time
        
        # All burst requests should complete quickly
        assert elapsed < 0.5
    
    @pytest.mark.asyncio
    async def test_token_bucket_refill(self, rate_limiter):
        """Test: Token bucket refills over time"""
        # Consume all burst capacity
        for i in range(5):
            await rate_limiter.acquire('arxiv')
        
        # Wait for some tokens to refill (2 requests/second = 0.5s per token)
        await asyncio.sleep(1.0)
        
        # Should now be able to make more requests without long delay
        start_time = time.time()
        await rate_limiter.acquire('arxiv')
        elapsed = time.time() - start_time
        
        # Should not have waited long since tokens refilled
        assert elapsed < 0.2
    
    @pytest.mark.asyncio
    async def test_multiple_time_window_limits(self, rate_limiter):
        """Test: Multiple time window limits are enforced"""
        # This test simulates hitting the per-minute limit
        # Note: In real implementation, we'd need to track requests over time
        
        # Get current minute limit stats
        stats = rate_limiter.get_service_stats('arxiv')
        initial_minute_count = stats['requests_this_minute']
        
        # Make several requests
        for i in range(5):
            await rate_limiter.acquire('arxiv')
        
        # Check that minute counter increased
        stats = rate_limiter.get_service_stats('arxiv')
        assert stats['requests_this_minute'] == initial_minute_count + 5
    
    @pytest.mark.asyncio
    async def test_wait_for_availability(self, rate_limiter):
        """Test: wait_for_availability returns correct wait time"""
        # Fill burst capacity
        for i in range(5):
            await rate_limiter.acquire('arxiv')
        
        # Check wait time
        wait_time = await rate_limiter.wait_for_availability('arxiv')
        
        # Should indicate how long to wait for next token
        assert 0.4 <= wait_time <= 0.6  # Approximately 0.5s for 2 req/sec
    
    @pytest.mark.asyncio
    async def test_respect_api_headers(self, rate_limiter):
        """Test: Rate limiter respects API response headers"""
        # Simulate API response with rate limit headers
        headers = {
            'X-RateLimit-Remaining': '5',
            'X-RateLimit-Reset': str(int(time.time()) + 60),
            'Retry-After': '30'
        }
        
        rate_limiter.update_from_headers('arxiv', headers)
        
        # Check that limits were updated based on headers
        stats = rate_limiter.get_service_stats('arxiv')
        assert 'remaining_requests' in stats
        assert stats['remaining_requests'] == 5
    
    @pytest.mark.asyncio
    async def test_429_response_handling(self, rate_limiter):
        """Test: Proper handling of 429 Too Many Requests response"""
        # Simulate 429 response
        retry_after = 60  # seconds
        
        rate_limiter.handle_429_response('arxiv', retry_after)
        
        # Should enforce wait based on retry-after
        wait_time = await rate_limiter.wait_for_availability('arxiv')
        assert wait_time >= 59  # Should wait approximately retry_after seconds
    
    def test_service_statistics(self, rate_limiter):
        """Test: Service statistics are tracked correctly"""
        stats = rate_limiter.get_service_stats('arxiv')
        
        expected_keys = [
            'service_name', 'requests_made', 'requests_this_second',
            'requests_this_minute', 'requests_this_hour', 'tokens_available',
            'last_request_time', 'last_refill_time'
        ]
        
        for key in expected_keys:
            assert key in stats
    
    def test_all_service_statistics(self, rate_limiter):
        """Test: Can get statistics for all services"""
        all_stats = rate_limiter.get_all_stats()
        
        assert 'arxiv' in all_stats
        assert 'pubmed' in all_stats
        assert len(all_stats) == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_are_rate_limited(self, rate_limiter):
        """Test: Concurrent requests are properly rate limited"""
        async def make_request(request_id):
            start_time = time.time()
            await rate_limiter.acquire('arxiv')
            return time.time() - start_time
        
        # Start multiple concurrent requests
        tasks = [make_request(i) for i in range(8)]
        times = await asyncio.gather(*tasks)
        
        # Some requests should have been delayed
        delayed_requests = [t for t in times if t > 0.1]
        assert len(delayed_requests) > 0
    
    @pytest.mark.asyncio
    async def test_unknown_service_handling(self, rate_limiter):
        """Test: Unknown services are handled with default limits"""
        # Should not raise error for unknown service
        await rate_limiter.acquire('unknown_service')
        
        # Should have created default stats
        stats = rate_limiter.get_service_stats('unknown_service')
        assert stats is not None
        assert stats['service_name'] == 'unknown_service'


class TestRateLimitIntegration:
    """Integration tests for rate limiter with real API scenarios"""
    
    @pytest.mark.asyncio
    async def test_arxiv_api_rate_limiting(self):
        """Test: Rate limiting works with ArXiv API patterns"""
        # ArXiv allows 3 requests per second
        rate_limiter = APIRateLimiter({
            'arxiv': RateLimitConfig(
                requests_per_second=3.0,
                burst_capacity=10
            )
        })
        
        # Make requests and measure timing
        start_time = time.time()
        
        # First 10 should be fast (burst)
        for i in range(10):
            await rate_limiter.acquire('arxiv')
        
        burst_time = time.time() - start_time
        assert burst_time < 1.0  # Burst should be fast
        
        # Next few should be rate limited
        for i in range(3):
            await rate_limiter.acquire('arxiv')
        
        total_time = time.time() - start_time
        assert total_time >= 1.0  # Should have been rate limited
    
    @pytest.mark.asyncio
    async def test_pubmed_api_rate_limiting(self):
        """Test: Rate limiting works with PubMed API patterns"""
        # PubMed has different limits
        rate_limiter = APIRateLimiter({
            'pubmed': RateLimitConfig(
                requests_per_second=10.0,  # Higher limit
                burst_capacity=20
            )
        })
        
        start_time = time.time()
        
        # Should handle more requests quickly
        for i in range(15):
            await rate_limiter.acquire('pubmed')
        
        elapsed = time.time() - start_time
        assert elapsed < 2.0  # Should be relatively fast
    
    @pytest.mark.asyncio
    async def test_mixed_service_usage(self):
        """Test: Mixed usage of different services"""
        rate_limiter = APIRateLimiter({
            'arxiv': RateLimitConfig(requests_per_second=2.0, burst_capacity=5),
            'pubmed': RateLimitConfig(requests_per_second=5.0, burst_capacity=10)
        })
        
        # Interleave requests to different services
        services = ['arxiv', 'pubmed', 'arxiv', 'pubmed', 'arxiv']
        
        for service in services:
            await rate_limiter.acquire(service)
        
        # Verify both services have request counts
        arxiv_stats = rate_limiter.get_service_stats('arxiv')
        pubmed_stats = rate_limiter.get_service_stats('pubmed')
        
        assert arxiv_stats['requests_made'] == 3
        assert pubmed_stats['requests_made'] == 2