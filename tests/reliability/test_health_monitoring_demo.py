"""
Demo script showing the health monitoring system in action.

Demonstrates real-time health checks, metrics collection, alerting,
and system-wide health assessment.
"""

import asyncio
import sys
import os
import random
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.health_monitor import (
    SystemHealthMonitor, get_global_health_monitor,
    HealthCheckResult, HealthStatus, MetricType,
    health_check_endpoint
)


async def demonstrate_health_checks():
    """Demonstrate basic health check functionality."""
    print("\n🏥 Health Check Demo\n")
    
    monitor = SystemHealthMonitor()
    
    # Define some service health checks
    async def api_health_check():
        # Simulate API health check
        response_time = random.uniform(0.05, 0.2)
        is_healthy = random.random() > 0.1  # 90% healthy
        
        return HealthCheckResult(
            service_name="api",
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.DEGRADED,
            message="API endpoint responding" if is_healthy else "High response times",
            timestamp=datetime.now(),
            response_time=response_time,
            metadata={
                "endpoint": "/health",
                "response_time_ms": response_time * 1000,
                "active_connections": random.randint(10, 100)
            }
        )
    
    async def database_health_check():
        # Simulate database health
        is_connected = random.random() > 0.05  # 95% connected
        query_time = random.uniform(0.001, 0.05)
        
        return HealthCheckResult(
            service_name="database",
            status=HealthStatus.HEALTHY if is_connected else HealthStatus.UNHEALTHY,
            message="Database connected" if is_connected else "Connection failed",
            timestamp=datetime.now(),
            response_time=query_time,
            metadata={
                "connections_active": random.randint(5, 50),
                "connections_idle": random.randint(10, 30),
                "query_time_ms": query_time * 1000
            }
        )
    
    # Register health checks
    monitor.register_health_check("api", api_health_check)
    monitor.register_health_check("database", database_health_check)
    
    # Run health checks
    print("Running health checks...")
    await monitor._run_all_health_checks()
    
    # Display results
    for service_name, result in monitor.last_health_check.items():
        print(f"\n📍 {service_name}:")
        print(f"   Status: {result.status.value}")
        print(f"   Message: {result.message}")
        print(f"   Response time: {result.response_time*1000:.2f}ms")
        if result.metadata:
            print(f"   Metadata: {result.metadata}")


async def demonstrate_metrics_collection():
    """Demonstrate metrics collection and monitoring."""
    print("\n📊 Metrics Collection Demo\n")
    
    monitor = SystemHealthMonitor()
    
    # Start metrics collection
    print("Starting metrics collection...")
    await monitor.metrics_collector.start_collection()
    
    # Simulate some application metrics
    for i in range(5):
        # Record various metrics
        monitor.metrics_collector.record_metric(
            "app.requests.total",
            100 + i * 10,
            MetricType.COUNTER
        )
        
        monitor.metrics_collector.record_metric(
            "app.response_time",
            random.uniform(50, 200),
            MetricType.GAUGE,
            unit="ms"
        )
        
        monitor.metrics_collector.record_metric(
            "app.error_rate",
            random.uniform(0.001, 0.05),
            MetricType.GAUGE,
            unit="%"
        )
        
        await asyncio.sleep(0.5)
    
    # Get current metrics
    current_metrics = monitor.metrics_collector.get_current_metrics()
    
    print("\nCurrent Metrics:")
    for name, metric in current_metrics.items():
        if name.startswith("app."):
            print(f"   {name}: {metric.value:.2f} {metric.unit}")
    
    # Stop collection
    await monitor.metrics_collector.stop_collection()


async def demonstrate_alerting():
    """Demonstrate alert management."""
    print("\n🚨 Alert Management Demo\n")
    
    monitor = SystemHealthMonitor()
    
    # Track alerts
    alerts_received = []
    
    async def alert_handler(alert):
        alerts_received.append(alert)
        print(f"⚠️  ALERT: [{alert.severity}] {alert.title}")
        print(f"   {alert.message}")
    
    monitor.alert_manager.register_alert_handler(alert_handler)
    
    # Set custom thresholds
    monitor.alert_manager.set_threshold("app.error_rate", "warning", 0.03)
    monitor.alert_manager.set_threshold("app.error_rate", "critical", 0.05)
    
    # Generate metrics that will trigger alerts
    print("Generating metrics that exceed thresholds...")
    
    # Normal metric
    monitor.metrics_collector.record_metric("app.error_rate", 0.01, MetricType.GAUGE, unit="%")
    await monitor.alert_manager.check_metric_thresholds(
        monitor.metrics_collector.get_current_metrics()["app.error_rate"]
    )
    
    # Warning threshold
    monitor.metrics_collector.record_metric("app.error_rate", 0.04, MetricType.GAUGE, unit="%")
    await monitor.alert_manager.check_metric_thresholds(
        monitor.metrics_collector.get_current_metrics()["app.error_rate"]
    )
    
    # Critical threshold
    monitor.metrics_collector.record_metric("app.error_rate", 0.06, MetricType.GAUGE, unit="%")
    await monitor.alert_manager.check_metric_thresholds(
        monitor.metrics_collector.get_current_metrics()["app.error_rate"]
    )
    
    # Show alert summary
    print(f"\n📊 Alert Summary:")
    summary = monitor.alert_manager.get_alert_summary()
    print(f"   Total alerts: {summary['total_alerts']}")
    print(f"   Active alerts: {summary['active_alerts']}")
    for severity, count in summary['alert_breakdown'].items():
        print(f"   {severity}: {count}")


async def demonstrate_system_health():
    """Demonstrate overall system health monitoring."""
    print("\n🏥 System Health Monitoring Demo\n")
    
    monitor = get_global_health_monitor()
    
    # Start monitoring
    print("Starting system health monitoring...")
    monitor.health_check_interval = 2  # Fast checks for demo
    await monitor.start_monitoring()
    
    # Let it run for a bit
    await asyncio.sleep(3)
    
    # Get system health report
    health_report = await monitor.check_system_health()
    
    print(f"\n📊 System Health Report:")
    print(f"   Overall Status: {health_report['overall_status']}")
    print(f"   Timestamp: {health_report['timestamp']}")
    
    print(f"\n   Services:")
    for service, status in health_report['services'].items():
        print(f"   - {service}: {status['status']} ({status['response_time']:.3f}s)")
    
    print(f"\n   System Metrics:")
    for metric_name, metric_data in health_report['metrics'].items():
        if metric_name in ['system.cpu.usage', 'system.memory.percent', 'system.disk.percent']:
            print(f"   - {metric_name}: {metric_data['value']:.1f}{metric_data['unit']}")
    
    if health_report['active_alerts']:
        print(f"\n   Active Alerts:")
        for alert in health_report['active_alerts']:
            print(f"   - [{alert['severity']}] {alert['title']}")
    else:
        print(f"\n   ✅ No active alerts")
    
    # Stop monitoring
    await monitor.stop_monitoring()


async def demonstrate_service_decorator():
    """Demonstrate using the health check decorator."""
    print("\n🎯 Service Health Check Decorator Demo\n")
    
    # Define a service with health check
    @health_check_endpoint("my_service")
    async def my_service_health():
        # Simulate checking service health
        is_healthy = random.random() > 0.2
        
        return HealthCheckResult(
            service_name="my_service",
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.DEGRADED,
            message="Service operational" if is_healthy else "Performance degraded",
            timestamp=datetime.now(),
            response_time=random.uniform(0.01, 0.1),
            metadata={
                "version": "2.1.0",
                "uptime_hours": 127.5,
                "last_deploy": "2025-01-20T15:30:00Z"
            }
        )
    
    # The decorator automatically registered it
    monitor = get_global_health_monitor()
    
    print("Health check registered via decorator")
    
    # Run the health check
    result = await monitor._run_health_check(
        "my_service",
        monitor.health_checks["my_service"]
    )
    
    print(f"\n📍 my_service health check:")
    print(f"   Status: {result.status.value}")
    print(f"   Message: {result.message}")
    print(f"   Version: {result.metadata.get('version')}")
    print(f"   Uptime: {result.metadata.get('uptime_hours')} hours")


async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("Health Monitoring System Demonstration")
    print("=" * 60)
    
    await demonstrate_health_checks()
    await demonstrate_metrics_collection()
    await demonstrate_alerting()
    await demonstrate_system_health()
    await demonstrate_service_decorator()
    
    print("\n" + "=" * 60)
    print("✅ Health Monitoring Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())