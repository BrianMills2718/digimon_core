"""
Demo script showing unified error handling framework.

This demonstrates the error taxonomy, recovery strategies, and
escalation procedures for the KGAS system.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.error_taxonomy import (
    CentralizedErrorHandler, get_global_error_handler,
    handle_errors, ErrorCategory, ErrorSeverity
)


async def demonstrate_error_categorization():
    """Demonstrate automatic error categorization."""
    print("\n🏷️  Error Categorization Demo\n")
    
    handler = CentralizedErrorHandler()
    
    # Different error types
    errors = [
        ("Data corruption in entity mappings", "DataCorruptionError"),
        ("Network timeout connecting to Neo4j", "NetworkError"),
        ("Memory pool exhausted", "MemoryError"),
        ("Citation fabrication detected", "IntegrityError"),
        ("Invalid configuration parameter", "ConfigError"),
        ("Authentication failed", "AuthError")
    ]
    
    for error_msg, error_type in errors:
        error = Exception(error_msg)
        context = {
            "service_name": "DemoService",
            "operation": "test_operation",
            "error_type": error_type
        }
        
        result = await handler.handle_error(error, context)
        
        print(f"📍 Error: {error_msg}")
        print(f"   Category: {result.category.value}")
        print(f"   Severity: {result.severity.value}")
        print(f"   Recovery suggestions: {len(result.recovery_suggestions)}")
        print()


async def demonstrate_recovery_strategies():
    """Demonstrate automatic recovery strategies."""
    print("\n🔧 Recovery Strategy Demo\n")
    
    handler = CentralizedErrorHandler()
    
    # Track recovery attempts
    recovery_attempts = []
    
    # Custom recovery strategy
    async def custom_network_recovery(error):
        recovery_attempts.append(f"Attempting recovery for {error.error_id}")
        await asyncio.sleep(0.1)  # Simulate recovery work
        return True  # Simulate success
    
    handler.register_recovery_strategy("network_timeout", custom_network_recovery)
    
    # Test network error (recoverable)
    print("1️⃣ Network Error (Recoverable):")
    network_error = Exception("Network timeout occurred")
    result = await handler.handle_error(network_error, {
        "service_name": "NetworkService",
        "operation": "fetch_data"
    })
    print(f"   Strategy: {handler._select_recovery_strategy(result).value}")
    print(f"   Recovery attempts: {len(recovery_attempts)}")
    
    # Test data corruption (non-recoverable)
    print("\n2️⃣ Data Corruption (Non-Recoverable):")
    corruption_error = Exception("Critical data corruption detected")
    result = await handler.handle_error(corruption_error, {
        "service_name": "DataService",
        "operation": "validate"
    })
    print(f"   Strategy: {handler._select_recovery_strategy(result).value}")
    print(f"   Escalated: Yes (critical error)")


async def demonstrate_error_escalation():
    """Demonstrate error escalation for critical issues."""
    print("\n🚨 Error Escalation Demo\n")
    
    handler = CentralizedErrorHandler()
    
    # Track escalations
    escalated_errors = []
    
    async def escalation_handler(error):
        escalated_errors.append({
            "error_id": error.error_id,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": error.message
        })
        print(f"   🚨 ESCALATED: {error.message}")
    
    handler.register_escalation_handler(escalation_handler)
    
    # Generate escalatable errors
    critical_errors = [
        "Academic integrity violation: fabricated citations",
        "Data corruption affecting 1000+ records",
        "System failure: core services unavailable"
    ]
    
    for error_msg in critical_errors:
        print(f"\n❌ Error: {error_msg}")
        error = Exception(error_msg)
        await handler.handle_error(error, {
            "service_name": "CriticalService",
            "operation": "monitor"
        })
    
    print(f"\n📊 Total escalations: {len(escalated_errors)}")


async def demonstrate_system_health_monitoring():
    """Demonstrate system health assessment from errors."""
    print("\n🏥 System Health Monitoring Demo\n")
    
    handler = CentralizedErrorHandler()
    
    # Initial health check
    health = handler.get_system_health_from_errors()
    print(f"Initial health score: {health['health_score']}/10")
    print(f"Status: {health['status']}")
    
    # Generate some minor errors
    print("\n📝 Generating minor errors...")
    for i in range(5):
        error = Exception(f"Minor validation error {i}")
        await handler.handle_error(error, {
            "service_name": "ValidationService",
            "operation": "check"
        })
    
    health = handler.get_system_health_from_errors()
    print(f"Health after minor errors: {health['health_score']}/10")
    print(f"Status: {health['status']}")
    
    # Generate critical error
    print("\n⚠️  Generating critical error...")
    error = Exception("Data corruption detected in core database")
    await handler.handle_error(error, {
        "service_name": "DatabaseService",
        "operation": "integrity_check"
    })
    
    health = handler.get_system_health_from_errors()
    print(f"Health after critical error: {health['health_score']}/10")
    print(f"Status: {health['status']}")
    
    # Show error breakdown
    print(f"\n📊 Error Breakdown:")
    for category, count in health['error_summary']['error_breakdown'].items():
        print(f"   {category}: {count}")


async def demonstrate_decorator_usage():
    """Demonstrate using error handling decorators."""
    print("\n🎯 Decorator Usage Demo\n")
    
    # Example service with error handling
    class DemoService:
        def __init__(self):
            self.operation_count = 0
        
        @handle_errors("DemoService", "risky_operation")
        async def risky_operation(self, should_fail=False):
            self.operation_count += 1
            if should_fail:
                raise Exception("Simulated operation failure")
            return {"result": "success", "count": self.operation_count}
        
        @handle_errors("DemoService", "data_operation")
        async def data_operation(self, corrupt=False):
            if corrupt:
                raise Exception("Data corruption detected during operation")
            return {"status": "data processed"}
    
    service = DemoService()
    
    # Successful operation
    print("✅ Successful operation:")
    result = await service.risky_operation()
    print(f"   Result: {result}")
    
    # Failed operation (handled)
    print("\n❌ Failed operation (handled):")
    try:
        result = await service.risky_operation(should_fail=True)
    except Exception as e:
        print(f"   Exception caught: {e}")
    
    # Check error metrics
    handler = get_global_error_handler()
    metrics = handler.error_metrics.get_error_summary()
    print(f"\n📊 Error metrics:")
    print(f"   Total errors: {metrics['total_errors']}")
    print(f"   Error categories: {list(metrics['error_breakdown'].keys())}")


async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("Unified Error Handling Framework Demonstration")
    print("=" * 60)
    
    await demonstrate_error_categorization()
    await demonstrate_recovery_strategies()
    await demonstrate_error_escalation()
    await demonstrate_system_health_monitoring()
    await demonstrate_decorator_usage()
    
    print("\n" + "=" * 60)
    print("✅ Error Handling Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())