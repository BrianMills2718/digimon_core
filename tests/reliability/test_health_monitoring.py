"""
Test health monitoring system implementation.

Ensures all services report health status, degraded states are detected,
and system-wide health is accurately assessed.
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.core.health_monitor import (
    SystemHealthMonitor, HealthStatus, HealthCheckResult,
    SystemMetric, MetricType, Alert, MetricsCollector,
    AlertManager, get_global_health_monitor,
    health_check_endpoint
)


class TestHealthMonitor:
    """Test suite for health monitoring system."""
    
    @pytest.mark.asyncio
    async def test_service_health_endpoints(self):
        """Test that all services expose health check endpoints."""
        monitor = SystemHealthMonitor()
        
        # Register health checks for services
        services = ["identity", "provenance", "quality", "workflow"]
        
        async def mock_health_check():
            return HealthCheckResult(
                service_name="test",
                status=HealthStatus.HEALTHY,
                message="Service is healthy",
                timestamp=datetime.now(),
                response_time=0.1
            )
        
        for service in services:
            monitor.register_health_check(service, mock_health_check)
        
        # Check system health
        health_report = await monitor.check_system_health()
        
        assert "services" in health_report
        assert len(health_report["services"]) >= len(services)
    
    @pytest.mark.asyncio
    async def test_degraded_state_detection(self):
        """Test detection of degraded service states."""
        monitor = SystemHealthMonitor()
        
        # Mock health check that returns degraded state
        async def degraded_check() -> HealthCheckResult:
            return HealthCheckResult(
                service_name="test_service",
                status=HealthStatus.DEGRADED,
                message="High memory usage detected",
                timestamp=datetime.now(),
                response_time=2.5,
                metadata={
                    "memory_usage": 85,
                    "cpu_usage": 45,
                    "response_time": 2.5
                }
            )
        
        monitor.register_health_check("test_service", degraded_check)
        
        # Run health check
        await monitor._run_all_health_checks()
        result = monitor.last_health_check["test_service"]
        
        assert result.status == HealthStatus.DEGRADED
        assert "High memory usage" in result.message
        assert result.metadata["memory_usage"] == 85
    
    @pytest.mark.asyncio
    async def test_recovery_detection(self):
        """Test detection of service recovery."""
        monitor = SystemHealthMonitor()
        
        # Service that changes state
        service_state = {"healthy": False}
        
        async def changing_health_check() -> HealthCheckResult:
            if service_state["healthy"]:
                return HealthCheckResult(
                    service_name="recovery_test",
                    status=HealthStatus.HEALTHY,
                    message="Service operating normally",
                    timestamp=datetime.now(),
                    response_time=0.1
                )
            else:
                return HealthCheckResult(
                    service_name="recovery_test",
                    status=HealthStatus.UNHEALTHY,
                    message="Service is down",
                    timestamp=datetime.now(),
                    response_time=0.1
                )
        
        monitor.register_health_check("recovery_test", changing_health_check)
        
        # Initially unhealthy
        await monitor._run_health_check("recovery_test", changing_health_check)
        result = monitor.last_health_check["recovery_test"]
        assert result.status == HealthStatus.UNHEALTHY
        
        # Trigger recovery
        service_state["healthy"] = True
        
        # Should detect recovery
        await monitor._run_health_check("recovery_test", changing_health_check)
        result = monitor.last_health_check["recovery_test"]
        assert result.status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_metric_collection(self):
        """Test system metric collection."""
        collector = MetricsCollector()
        
        # Record some metrics
        collector.record_metric("test.requests", 100, MetricType.COUNTER)
        collector.record_metric("test.latency", 250, MetricType.GAUGE, unit="ms")
        collector.record_metric("test.errors", 5, MetricType.COUNTER)
        
        # Get current metrics
        current = collector.get_current_metrics()
        
        assert "test.requests" in current
        assert current["test.requests"].value == 100
        assert current["test.requests"].metric_type == MetricType.COUNTER
        
        assert "test.latency" in current
        assert current["test.latency"].value == 250
        assert current["test.latency"].unit == "ms"
        
        # Test metric history
        history = collector.get_metric_history("test.requests", minutes=60)
        assert len(history) >= 1
        assert history[0].name == "test.requests"
    
    @pytest.mark.asyncio
    async def test_system_wide_health_aggregation(self):
        """Test aggregation of system-wide health status."""
        monitor = SystemHealthMonitor()
        
        # Register services with different states
        async def healthy_check():
            return HealthCheckResult(
                service_name="healthy",
                status=HealthStatus.HEALTHY,
                message="OK",
                timestamp=datetime.now(),
                response_time=0.1
            )
        
        async def degraded_check():
            return HealthCheckResult(
                service_name="degraded",
                status=HealthStatus.DEGRADED,
                message="Slow",
                timestamp=datetime.now(),
                response_time=2.0
            )
        
        async def unhealthy_check():
            return HealthCheckResult(
                service_name="unhealthy",
                status=HealthStatus.UNHEALTHY,
                message="Down",
                timestamp=datetime.now(),
                response_time=5.0
            )
        
        monitor.register_health_check("service1", healthy_check)
        monitor.register_health_check("service2", healthy_check)
        monitor.register_health_check("service3", degraded_check)
        monitor.register_health_check("service4", unhealthy_check)
        
        # Get system health
        system_health = await monitor.check_system_health()
        
        assert system_health["overall_status"] == HealthStatus.DEGRADED.value
        assert len(system_health["services"]) == 4
    
    @pytest.mark.asyncio
    async def test_alert_management(self):
        """Test alert creation and management."""
        alert_manager = AlertManager()
        
        # Track alerts
        alerts_received = []
        
        async def alert_handler(alert: Alert):
            alerts_received.append(alert)
        
        alert_manager.register_alert_handler(alert_handler)
        
        # Create test metric that exceeds threshold
        metric = SystemMetric(
            name="system.cpu.usage",
            value=95.0,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            unit="%"
        )
        
        # Check threshold (should create alert)
        await alert_manager.check_metric_thresholds(metric)
        
        # Verify alert was created
        assert len(alerts_received) == 1
        assert alerts_received[0].severity == "critical"
        assert "cpu" in alerts_received[0].title.lower()
        
        # Check active alerts
        active = alert_manager.get_active_alerts()
        assert len(active) == 1
    
    @pytest.mark.asyncio
    async def test_background_monitoring(self):
        """Test background health monitoring."""
        monitor = SystemHealthMonitor()
        monitor.health_check_interval = 0.5  # Fast checks for testing
        
        # Track health check executions
        check_count = {"count": 0}
        
        async def counting_health_check():
            check_count["count"] += 1
            return HealthCheckResult(
                service_name="test",
                status=HealthStatus.HEALTHY,
                message="OK",
                timestamp=datetime.now(),
                response_time=0.01
            )
        
        monitor.register_health_check("test_service", counting_health_check)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Wait for a few checks
        await asyncio.sleep(1.5)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Should have executed multiple checks
        assert check_count["count"] >= 2
    
    @pytest.mark.asyncio
    async def test_system_resource_health_checks(self):
        """Test built-in system resource health checks."""
        monitor = SystemHealthMonitor()
        
        # Test CPU health check
        cpu_result = await monitor._check_cpu_health()
        assert isinstance(cpu_result, HealthCheckResult)
        assert cpu_result.service_name == "cpu"
        assert cpu_result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.CRITICAL]
        assert "cpu_percent" in cpu_result.metadata
        
        # Test memory health check
        memory_result = await monitor._check_memory_health()
        assert isinstance(memory_result, HealthCheckResult)
        assert memory_result.service_name == "memory"
        assert "total_gb" in memory_result.metadata
        assert "available_gb" in memory_result.metadata
        
        # Test disk health check
        disk_result = await monitor._check_disk_health()
        assert isinstance(disk_result, HealthCheckResult)
        assert disk_result.service_name == "disk"
        assert "total_gb" in disk_result.metadata
        assert "free_gb" in disk_result.metadata
        
        # Test overall system health
        system_result = await monitor._check_system_health()
        assert isinstance(system_result, HealthCheckResult)
        assert system_result.service_name == "system"
    
    @pytest.mark.asyncio
    async def test_health_check_decorator(self):
        """Test health check endpoint decorator."""
        monitor = get_global_health_monitor()
        
        # Define a health check using decorator
        @health_check_endpoint("decorated_service")
        async def my_service_health():
            return HealthCheckResult(
                service_name="decorated_service",
                status=HealthStatus.HEALTHY,
                message="Service is healthy",
                timestamp=datetime.now(),
                response_time=0.05,
                metadata={"version": "1.0.0"}
            )
        
        # Verify it was registered
        assert "decorated_service" in monitor.health_checks
        
        # Execute health check
        result = await monitor._run_health_check("decorated_service", monitor.health_checks["decorated_service"])
        assert result.status == HealthStatus.HEALTHY
        assert result.metadata["version"] == "1.0.0"