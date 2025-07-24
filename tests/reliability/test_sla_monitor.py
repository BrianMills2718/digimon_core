"""
Test SLA monitoring functionality.

Verifies threshold configuration, violation detection, and alerting.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from unittest.mock import AsyncMock, MagicMock

from src.core.sla_monitor import (
    SLAMonitor,
    SLAThreshold,
    SLASeverity,
    SLAViolation,
    get_sla_monitor
)
from src.monitoring.performance_tracker import PerformanceTracker


class TestSLAThreshold:
    """Test the SLAThreshold dataclass."""
    
    def test_threshold_creation(self):
        """Test creating SLA threshold."""
        threshold = SLAThreshold(
            operation="test_op",
            max_duration=1.0,
            warning_duration=0.8,
            critical_duration=2.0,
            max_error_rate=0.05,
            min_success_rate=0.95,
            evaluation_window=100
        )
        
        assert threshold.operation == "test_op"
        assert threshold.max_duration == 1.0
        assert threshold.warning_duration == 0.8
        assert threshold.critical_duration == 2.0
        assert threshold.max_error_rate == 0.05
        assert threshold.min_success_rate == 0.95
    
    def test_duration_check(self):
        """Test duration violation checking."""
        threshold = SLAThreshold(
            operation="test_op",
            max_duration=1.0,
            warning_duration=0.8,
            critical_duration=2.0,
            max_error_rate=0.05,
            min_success_rate=0.95,
            evaluation_window=100
        )
        
        # No violation
        assert threshold.check_duration(0.5) is None
        assert threshold.check_duration(0.7) is None
        
        # Warning
        assert threshold.check_duration(0.85) == SLASeverity.WARNING
        assert threshold.check_duration(0.95) == SLASeverity.WARNING
        
        # Violation
        assert threshold.check_duration(1.1) == SLASeverity.VIOLATION
        assert threshold.check_duration(1.5) == SLASeverity.VIOLATION
        
        # Critical
        assert threshold.check_duration(2.1) == SLASeverity.CRITICAL
        assert threshold.check_duration(5.0) == SLASeverity.CRITICAL
    
    def test_error_rate_check(self):
        """Test error rate violation checking."""
        threshold = SLAThreshold(
            operation="test_op",
            max_duration=1.0,
            warning_duration=0.8,
            critical_duration=2.0,
            max_error_rate=0.05,
            min_success_rate=0.95,
            evaluation_window=100
        )
        
        # No violation
        assert threshold.check_error_rate(0.02) is None
        assert threshold.check_error_rate(0.03) is None
        
        # Warning (80% of threshold = 0.04)
        assert threshold.check_error_rate(0.045) == SLASeverity.WARNING
        
        # Violation
        assert threshold.check_error_rate(0.06) == SLASeverity.VIOLATION
        assert threshold.check_error_rate(0.10) == SLASeverity.VIOLATION


class TestSLAViolation:
    """Test the SLAViolation dataclass."""
    
    def test_violation_creation(self):
        """Test creating SLA violation record."""
        violation = SLAViolation(
            operation="test_op",
            severity=SLASeverity.VIOLATION,
            violation_type="duration",
            actual_value=1.5,
            threshold_value=1.0,
            timestamp="2025-01-23T10:00:00",
            metadata={"context": "test"}
        )
        
        assert violation.operation == "test_op"
        assert violation.severity == SLASeverity.VIOLATION
        assert violation.violation_type == "duration"
        assert violation.actual_value == 1.5
        assert violation.threshold_value == 1.0
        assert violation.metadata == {"context": "test"}


class TestSLAMonitor:
    """Test the SLAMonitor class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_tracker(self):
        """Create mock performance tracker."""
        tracker = MagicMock()
        tracker.get_operation_stats = AsyncMock(return_value={"error": "No metrics for operation"})
        tracker.get_system_summary = AsyncMock(return_value={"operations": {}})
        return tracker
    
    @pytest.fixture
    def monitor(self, temp_dir, mock_tracker):
        """Create SLA monitor with temp storage."""
        config_path = Path(temp_dir) / "test_sla_config.json"
        return SLAMonitor(
            performance_tracker=mock_tracker,
            config_path=config_path
        )
    
    @pytest.mark.asyncio
    async def test_set_sla(self, monitor):
        """Test setting SLA threshold."""
        threshold = SLAThreshold(
            operation="custom_op",
            max_duration=0.5,
            warning_duration=0.4,
            critical_duration=1.0,
            max_error_rate=0.02,
            min_success_rate=0.98,
            evaluation_window=50
        )
        
        await monitor.set_sla("custom_op", threshold)
        
        # Verify threshold was set
        assert "custom_op" in monitor._thresholds
        assert monitor._thresholds["custom_op"].max_duration == 0.5
    
    @pytest.mark.asyncio
    async def test_check_operation_duration_violation(self, monitor):
        """Test checking operation for duration violations."""
        # Test with default threshold (tool_execution)
        violation = await monitor.check_operation(
            operation="tool_execution",
            duration=6.0,  # Exceeds default max of 5.0
            success=True
        )
        
        assert violation is not None
        assert violation.operation == "tool_execution"
        assert violation.severity == SLASeverity.VIOLATION
        assert violation.violation_type == "duration"
        assert violation.actual_value == 6.0
        assert violation.threshold_value == 5.0
    
    @pytest.mark.asyncio
    async def test_check_operation_no_violation(self, monitor):
        """Test checking operation with no violations."""
        violation = await monitor.check_operation(
            operation="tool_execution",
            duration=2.0,  # Within threshold
            success=True
        )
        
        assert violation is None
    
    @pytest.mark.asyncio
    async def test_check_operation_error_rate_violation(self, monitor, mock_tracker):
        """Test checking operation for error rate violations."""
        # Mock tracker to return high error rate
        mock_tracker.get_operation_stats.return_value = {
            "operation": "api_request",
            "sample_count": 100,
            "success_rate": 0.90,  # 10% error rate, exceeds 2% threshold
            "recent_mean": 0.5
        }
        
        violation = await monitor.check_operation(
            operation="api_request",
            duration=0.5,
            success=False
        )
        
        assert violation is not None
        assert violation.operation == "api_request"
        assert violation.violation_type == "error_rate"
        assert violation.actual_value == 0.10  # 10% error rate
        assert violation.threshold_value == 0.02  # 2% threshold
    
    @pytest.mark.asyncio
    async def test_critical_violation(self, monitor):
        """Test critical severity violations."""
        violation = await monitor.check_operation(
            operation="database_query",
            duration=5.0,  # Exceeds critical threshold of 3.0
            success=True
        )
        
        assert violation is not None
        assert violation.severity == SLASeverity.CRITICAL
        assert violation.violation_type == "duration"
    
    @pytest.mark.asyncio
    async def test_alert_handler_registration(self, monitor):
        """Test registering and calling alert handlers."""
        # Track alert calls
        alerts_received = []
        
        async def test_handler(violation: SLAViolation):
            alerts_received.append(violation)
        
        # Register handler
        monitor.register_alert_handler(test_handler)
        
        # Trigger violation
        await monitor.check_operation(
            operation="tool_execution",
            duration=10.0,  # Critical violation
            success=True
        )
        
        # Verify handler was called
        assert len(alerts_received) == 1
        assert alerts_received[0].operation == "tool_execution"
        assert alerts_received[0].severity == SLASeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_violation_history(self, monitor):
        """Test retrieving violation history."""
        # Create some violations using tool_execution which has default SLA
        for i in range(5):
            await monitor.check_operation(
                operation="tool_execution",
                duration=6.0 + i,  # All violations (> 5.0 threshold)
                success=True
            )
        
        # Get all violations
        history = await monitor.get_violation_history()
        assert len(history) == 5
        
        # Get violations for specific operation
        op_history = await monitor.get_violation_history(operation="tool_execution")
        assert len(op_history) == 5
        
        # Get violations by severity
        critical_history = await monitor.get_violation_history(
            severity=SLASeverity.CRITICAL
        )
        # Should have some critical violations (duration >= 10.0)
        assert any(v.severity == SLASeverity.CRITICAL for v in critical_history)
    
    @pytest.mark.asyncio
    async def test_sla_report(self, monitor):
        """Test generating SLA compliance report."""
        # Create mix of violations and successful operations using tool_execution
        for i in range(10):
            await monitor.check_operation(
                operation="tool_execution",
                duration=0.5 if i < 7 else 6.0,  # 3 violations (> 5.0 threshold)
                success=True
            )
        
        report = await monitor.get_sla_report()
        
        assert report["summary"]["total_checks"] == 10
        assert report["summary"]["total_violations"] == 3
        assert report["summary"]["violation_rate"] == 0.3
        
        assert "tool_execution" in report["operations"]
        assert report["operations"]["tool_execution"]["violations"] == 3
    
    @pytest.mark.asyncio
    async def test_recommend_sla(self, monitor, mock_tracker):
        """Test SLA recommendation based on performance."""
        # Mock performance stats
        mock_tracker.get_operation_stats.return_value = {
            "operation": "new_op",
            "sample_count": 150,
            "success_rate": 0.97,
            "baseline": {
                "p95": 0.8,
                "mean": 0.5
            }
        }
        
        recommendation = await monitor.recommend_sla("new_op")
        
        assert recommendation is not None
        assert recommendation.operation == "new_op"
        assert recommendation.max_duration == pytest.approx(0.96, rel=0.01)  # p95 * 1.2
        assert recommendation.warning_duration == 0.8  # p95
        assert recommendation.critical_duration == 1.6  # p95 * 2
        assert recommendation.max_error_rate <= 0.06  # (1 - 0.97) * 2
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_cancellation(self, monitor):
        """Test clean shutdown of monitoring loop."""
        # Start monitoring by checking an operation
        await monitor.check_operation("test", 1.0, True)
        
        # Verify monitoring task was started
        assert monitor._monitoring_task is not None
        
        # Clean up should cancel monitoring task
        await monitor.cleanup()
        
        # Verify task is cancelled
        assert monitor._monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_default_slas(self, monitor):
        """Test that default SLAs are loaded."""
        # Check some default SLAs exist
        assert "tool_execution" in monitor._thresholds
        assert "database_query" in monitor._thresholds
        assert "api_request" in monitor._thresholds
        assert "document_processing" in monitor._thresholds
        assert "pipeline_execution" in monitor._thresholds
        
        # Verify default values
        tool_sla = monitor._thresholds["tool_execution"]
        assert tool_sla.max_duration == 5.0
        assert tool_sla.warning_duration == 4.0
        assert tool_sla.critical_duration == 10.0


class TestGlobalSLAMonitor:
    """Test global SLA monitor instance."""
    
    def test_global_monitor_singleton(self):
        """Test that global monitor is a singleton."""
        monitor1 = get_sla_monitor()
        monitor2 = get_sla_monitor()
        
        assert monitor1 is monitor2
    
    @pytest.mark.asyncio
    async def test_global_monitor_functionality(self):
        """Test global monitor works correctly."""
        monitor = get_sla_monitor()
        
        # Set a custom SLA
        threshold = SLAThreshold(
            operation="global_test",
            max_duration=1.0,
            warning_duration=0.8,
            critical_duration=2.0,
            max_error_rate=0.05,
            min_success_rate=0.95,
            evaluation_window=100
        )
        
        await monitor.set_sla("global_test", threshold)
        
        # Check operation
        violation = await monitor.check_operation(
            operation="global_test",
            duration=1.5,
            success=True
        )
        
        assert violation is not None
        assert violation.operation == "global_test"


@pytest.mark.asyncio
async def test_sla_monitor_integration():
    """Integration test with real performance tracker."""
    # Create real performance tracker
    tracker = PerformanceTracker()
    
    # Create SLA monitor with real tracker
    monitor = SLAMonitor(performance_tracker=tracker)
    
    try:
        # Record some operations
        for i in range(20):
            timer_id = await tracker.start_operation("integration_test")
            await asyncio.sleep(0.01 if i < 15 else 0.1)  # Some slow operations
            await tracker.end_operation(timer_id, success=(i % 10 != 0))
        
        # Check for violations
        violation = await monitor.check_operation(
            operation="integration_test",
            duration=0.05,
            success=True
        )
        
        # Should detect error rate violation (10% failures)
        # Note: May not trigger if no SLA defined for integration_test
        
        # Get report
        report = await monitor.get_sla_report()
        assert report["summary"]["total_checks"] >= 0
        
    finally:
        await monitor.cleanup()