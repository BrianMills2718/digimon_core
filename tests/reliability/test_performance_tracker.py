"""
Test performance tracking functionality.

Verifies operation timing, baseline establishment, and degradation detection.
"""

import pytest
import asyncio
import time
from pathlib import Path
import json
import tempfile
import shutil

from src.monitoring.performance_tracker import (
    PerformanceTracker, 
    PerformanceMetric, 
    PerformanceBaseline,
    get_performance_tracker
)


class TestPerformanceMetric:
    """Test the PerformanceMetric dataclass."""
    
    def test_performance_metric_creation(self):
        """Test creating performance metrics."""
        metric = PerformanceMetric(
            operation="test_op",
            start_time=1.0,
            end_time=2.5,
            duration=1.5,
            success=True,
            metadata={"test": "data"}
        )
        
        assert metric.operation == "test_op"
        assert metric.duration == 1.5
        assert metric.success is True
        assert metric.metadata == {"test": "data"}
        assert metric.timestamp is not None


class TestPerformanceBaseline:
    """Test the PerformanceBaseline dataclass."""
    
    def test_baseline_creation(self):
        """Test creating performance baseline."""
        baseline = PerformanceBaseline(
            operation="test_op",
            p50=0.5,
            p75=0.75,
            p95=0.95,
            p99=0.99,
            mean=0.6,
            std_dev=0.2,
            sample_count=100,
            established_at="2025-01-23T10:00:00"
        )
        
        assert baseline.operation == "test_op"
        assert baseline.p50 == 0.5
        assert baseline.p95 == 0.95
        assert baseline.mean == 0.6
        assert baseline.std_dev == 0.2
    
    def test_degradation_detection(self):
        """Test degradation detection logic."""
        baseline = PerformanceBaseline(
            operation="test_op",
            p50=0.5,
            p75=0.75,
            p95=0.95,
            p99=0.99,
            mean=0.6,
            std_dev=0.2,
            sample_count=100,
            established_at="2025-01-23T10:00:00"
        )
        
        # Normal performance - should not be degraded
        assert baseline.is_degraded(0.7) is False
        assert baseline.is_degraded(0.9) is False
        
        # Degraded performance - > p95
        assert baseline.is_degraded(1.0) is True
        
        # Degraded performance - > mean + 2*std_dev (0.6 + 0.4 = 1.0)
        assert baseline.is_degraded(1.1) is True


class TestPerformanceTracker:
    """Test the PerformanceTracker class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def tracker(self, temp_dir):
        """Create performance tracker with temp storage."""
        storage_path = Path(temp_dir) / "test_performance.json"
        return PerformanceTracker(
            window_size=100,
            baseline_samples=10,
            storage_path=storage_path
        )
    
    @pytest.mark.asyncio
    async def test_operation_timing(self, tracker):
        """Test basic operation timing."""
        # Start operation
        timer_id = await tracker.start_operation("test_operation")
        assert timer_id is not None
        
        # Simulate work
        await asyncio.sleep(0.1)
        
        # End operation
        duration = await tracker.end_operation(timer_id, success=True)
        assert duration >= 0.1
        assert duration < 0.2  # Should not take too long
        
        # Verify metrics recorded
        stats = await tracker.get_operation_stats("test_operation")
        assert stats["sample_count"] == 1
        assert stats["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_invalid_timer_id(self, tracker):
        """Test handling of invalid timer ID."""
        with pytest.raises(ValueError, match="No active timer"):
            await tracker.end_operation("invalid_timer_id")
    
    @pytest.mark.asyncio
    async def test_baseline_establishment(self, tracker):
        """Test automatic baseline establishment."""
        # Record enough samples to establish baseline
        for i in range(15):
            timer_id = await tracker.start_operation("baseline_test")
            await asyncio.sleep(0.01)  # Consistent timing
            await tracker.end_operation(timer_id, success=True)
        
        # Check baseline was established
        stats = await tracker.get_operation_stats("baseline_test")
        assert "baseline" in stats
        assert stats["baseline"]["sample_count"] == 10  # Uses last 10 samples
        assert 0.005 < stats["baseline"]["mean"] < 0.02
    
    @pytest.mark.asyncio
    async def test_degradation_detection(self, tracker):
        """Test performance degradation detection."""
        # Establish baseline with fast operations
        for i in range(12):
            timer_id = await tracker.start_operation("degradation_test")
            await asyncio.sleep(0.01)
            await tracker.end_operation(timer_id, success=True)
        
        # Wait for baseline to be established
        await asyncio.sleep(0.1)
        
        # Record initial stats
        initial_summary = await tracker.get_system_summary()
        initial_degraded = initial_summary["degraded_operations"]
        
        # Perform slow operation (degraded)
        timer_id = await tracker.start_operation("degradation_test")
        await asyncio.sleep(0.5)  # Much slower than baseline
        await tracker.end_operation(timer_id, success=True)
        
        # Check degradation was detected
        final_summary = await tracker.get_system_summary()
        assert final_summary["degraded_operations"] > initial_degraded
    
    @pytest.mark.asyncio
    async def test_decorator_async(self, tracker):
        """Test timing decorator for async functions."""
        @tracker.time_operation("decorated_async")
        async def slow_async_function():
            await asyncio.sleep(0.05)
            return "result"
        
        result = await slow_async_function()
        assert result == "result"
        
        stats = await tracker.get_operation_stats("decorated_async")
        assert stats["sample_count"] == 1
        assert stats["success_rate"] == 1.0
        assert 0.04 < stats["recent_mean"] < 0.1
    
    @pytest.mark.asyncio
    async def test_decorator_sync(self, tracker):
        """Test timing decorator for sync functions."""
        @tracker.time_operation("decorated_sync")
        def slow_sync_function():
            time.sleep(0.05)
            return "sync_result"
        
        result = slow_sync_function()
        assert result == "sync_result"
        
        # Give async tasks time to complete
        await asyncio.sleep(0.1)
        
        stats = await tracker.get_operation_stats("decorated_sync")
        assert stats["sample_count"] == 1
        assert stats["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_decorator_exception_handling(self, tracker):
        """Test decorator handles exceptions properly."""
        @tracker.time_operation("failing_operation")
        async def failing_function():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await failing_function()
        
        stats = await tracker.get_operation_stats("failing_operation")
        assert stats["sample_count"] == 1
        assert stats["success_rate"] == 0.0  # Failed operation
    
    @pytest.mark.asyncio
    async def test_persistence(self, temp_dir):
        """Test baseline persistence across instances."""
        storage_path = Path(temp_dir) / "persist_test.json"
        
        # First tracker instance
        tracker1 = PerformanceTracker(
            window_size=100,
            baseline_samples=10,
            storage_path=storage_path
        )
        
        # Establish baseline
        for i in range(12):
            timer_id = await tracker1.start_operation("persist_test")
            await asyncio.sleep(0.01)
            await tracker1.end_operation(timer_id, success=True)
        
        # Wait for baseline save
        await asyncio.sleep(0.2)
        
        # Create new tracker instance
        tracker2 = PerformanceTracker(
            window_size=100,
            baseline_samples=10,
            storage_path=storage_path
        )
        
        # Wait for load
        await asyncio.sleep(0.1)
        
        # Check baseline was loaded
        stats = await tracker2.get_operation_stats("persist_test")
        assert "baseline" in stats
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, tracker):
        """Test handling concurrent operations."""
        async def timed_operation(index):
            timer_id = await tracker.start_operation(f"concurrent_{index % 3}")
            await asyncio.sleep(0.01 + (index % 3) * 0.01)
            await tracker.end_operation(timer_id, success=True)
        
        # Run many concurrent operations
        tasks = [timed_operation(i) for i in range(30)]
        await asyncio.gather(*tasks)
        
        # Check all operations recorded
        summary = await tracker.get_system_summary()
        assert summary["total_operations"] == 30
        assert len(summary["tracked_operations"]) == 3
        
        # Check each operation type
        for i in range(3):
            stats = await tracker.get_operation_stats(f"concurrent_{i}")
            assert stats["sample_count"] == 10
    
    @pytest.mark.asyncio
    async def test_system_summary(self, tracker):
        """Test system summary generation."""
        # Record various operations
        operations = ["op1", "op2", "op3"]
        for op in operations:
            for i in range(5):
                timer_id = await tracker.start_operation(op)
                await asyncio.sleep(0.01)
                success = i != 2  # Fail one operation
                await tracker.end_operation(timer_id, success=success)
        
        summary = await tracker.get_system_summary()
        
        assert summary["total_operations"] == 15
        assert len(summary["tracked_operations"]) == 3
        assert set(summary["tracked_operations"]) == set(operations)
        
        # Check operation details
        for op in operations:
            assert op in summary["operations"]
            assert summary["operations"][op]["sample_count"] == 5
            assert summary["operations"][op]["success_rate"] == 0.8  # 4/5
    
    @pytest.mark.asyncio
    async def test_rolling_window(self, tracker):
        """Test rolling window behavior."""
        # Use small window for testing
        small_tracker = PerformanceTracker(window_size=5, baseline_samples=3)
        
        # Fill window beyond capacity
        for i in range(10):
            timer_id = await small_tracker.start_operation("window_test")
            await asyncio.sleep(0.001 * i)  # Increasing durations
            await small_tracker.end_operation(timer_id, success=True)
        
        stats = await small_tracker.get_operation_stats("window_test")
        
        # Should only have last 5 samples
        assert stats["sample_count"] == 5
        
        # Recent mean should reflect later (slower) operations
        assert stats["recent_mean"] > 0.004


class TestGlobalTracker:
    """Test global tracker instance."""
    
    def test_global_tracker_singleton(self):
        """Test that global tracker is a singleton."""
        tracker1 = get_performance_tracker()
        tracker2 = get_performance_tracker()
        
        assert tracker1 is tracker2
    
    @pytest.mark.asyncio
    async def test_global_tracker_functionality(self):
        """Test global tracker works correctly."""
        tracker = get_performance_tracker()
        
        timer_id = await tracker.start_operation("global_test")
        await asyncio.sleep(0.01)
        duration = await tracker.end_operation(timer_id, success=True)
        
        assert duration > 0.009
        
        stats = await tracker.get_operation_stats("global_test")
        assert stats["sample_count"] >= 1


@pytest.mark.asyncio
async def test_performance_tracker_stress_test():
    """Stress test with many operations."""
    tracker = PerformanceTracker(window_size=1000, baseline_samples=50)
    
    # Define operation types with different characteristics
    operation_profiles = {
        "fast": (0.001, 0.005),
        "medium": (0.01, 0.02),
        "slow": (0.05, 0.1),
        "variable": (0.001, 0.1)
    }
    
    async def run_operation(op_type, duration_range):
        timer_id = await tracker.start_operation(op_type)
        min_d, max_d = duration_range
        await asyncio.sleep(min_d + (max_d - min_d) * (hash(timer_id) % 100) / 100)
        success = hash(timer_id) % 20 != 0  # 5% failure rate
        await tracker.end_operation(timer_id, success=success)
    
    # Run many operations concurrently
    tasks = []
    for _ in range(100):
        for op_type, duration_range in operation_profiles.items():
            tasks.append(run_operation(op_type, duration_range))
    
    await asyncio.gather(*tasks)
    
    # Verify results
    summary = await tracker.get_system_summary()
    assert summary["total_operations"] == 400
    assert len(summary["tracked_operations"]) == 4
    
    # Check baselines established
    for op_type in operation_profiles:
        stats = await tracker.get_operation_stats(op_type)
        assert stats["sample_count"] == 100
        assert 0.9 < stats["success_rate"] < 0.99  # ~95% success
        if stats["sample_count"] >= 50:
            assert "baseline" in stats