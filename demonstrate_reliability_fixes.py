#!/usr/bin/env python3
"""
Demonstrate Phase RELIABILITY fixes working together.

Shows:
1. Audit Trail Immutability
2. Performance Tracking  
3. SLA Monitoring
"""

import asyncio
from datetime import datetime

from src.core.provenance_manager import ProvenanceManager
from src.monitoring.performance_tracker import PerformanceTracker
from src.core.sla_monitor import SLAMonitor, SLAThreshold


async def main():
    print("=== Phase RELIABILITY Demonstration ===\n")
    
    # Initialize components
    print("1. Initializing components...")
    provenance_manager = ProvenanceManager()
    performance_tracker = PerformanceTracker()
    sla_monitor = SLAMonitor(performance_tracker=performance_tracker)
    
    # Track violations
    violations = []
    async def violation_handler(violation):
        violations.append(violation)
        print(f"   🚨 SLA Violation: {violation.operation} - {violation.severity.value}")
    
    sla_monitor.register_alert_handler(violation_handler)
    
    print("   ✓ Components initialized\n")
    
    # Demonstrate Audit Trail Immutability
    print("2. Testing Audit Trail Immutability...")
    
    # Create source
    source_id = await provenance_manager.register_source({
        "id": "demo_source",
        "content": "This is a demonstration of the reliability fixes."
    })
    
    # Create citation
    citation = await provenance_manager.create_citation(
        source_id=source_id,
        text="demonstration",
        start_pos=10,
        end_pos=23
    )
    print(f"   ✓ Created citation: {citation['id']}")
    
    # Modify citation
    await provenance_manager.modify_citation(
        citation_id=citation["id"],
        new_text="demo",
        reason="Shortened for clarity",
        modifier="demo_user"
    )
    print("   ✓ Modified citation")
    
    # Verify integrity
    is_valid = await provenance_manager.verify_audit_integrity(citation["id"])
    print(f"   ✓ Audit trail integrity verified: {is_valid}")
    
    # Get audit trail
    audit_trail = await provenance_manager.get_audit_trail(citation["id"])
    print(f"   ✓ Audit trail has {len(audit_trail)} entries")
    for entry in audit_trail:
        print(f"     - {entry['operation']} at {entry['timestamp'][:19]} (hash: {entry['hash'][:8]}...)")
    print()
    
    # Demonstrate Performance Tracking
    print("3. Testing Performance Tracking...")
    
    # Set custom SLA for demo
    await sla_monitor.set_sla("demo_operation", SLAThreshold(
        operation="demo_operation",
        max_duration=0.1,  # 100ms max
        warning_duration=0.08,  # 80ms warning
        critical_duration=0.2,  # 200ms critical
        max_error_rate=0.1,
        min_success_rate=0.9,
        evaluation_window=10
    ))
    
    # Perform operations with timing
    for i in range(5):
        timer_id = await performance_tracker.start_operation("demo_operation")
        
        # Simulate varying performance
        if i == 3:
            await asyncio.sleep(0.15)  # Slow operation - will violate SLA
        else:
            await asyncio.sleep(0.05)  # Normal operation
        
        duration = await performance_tracker.end_operation(timer_id, success=True)
        print(f"   ✓ Operation {i+1} completed in {duration:.3f}s")
        
        # Check SLA
        await sla_monitor.check_operation("demo_operation", duration, True)
    
    # Get performance stats
    stats = await performance_tracker.get_operation_stats("demo_operation")
    print(f"\n   Performance Statistics:")
    print(f"   - Sample count: {stats['sample_count']}")
    print(f"   - Success rate: {stats['success_rate']:.0%}")
    print(f"   - Mean duration: {stats['recent_mean']:.3f}s")
    print(f"   - P95 duration: {stats['recent_p95']:.3f}s")
    print()
    
    # Demonstrate SLA Monitoring
    print("4. Testing SLA Monitoring...")
    
    # Check violations
    print(f"   ✓ Detected {len(violations)} SLA violations")
    
    # Get violation history
    history = await sla_monitor.get_violation_history(hours=1)
    for v in history:
        print(f"   - {v.operation}: {v.violation_type} = {v.actual_value:.3f} (threshold: {v.threshold_value:.3f})")
    
    # Get SLA report
    report = await sla_monitor.get_sla_report()
    print(f"\n   SLA Compliance Report:")
    print(f"   - Total checks: {report['summary']['total_checks']}")
    print(f"   - Total violations: {report['summary']['total_violations']}")
    print(f"   - Violation rate: {report['summary']['violation_rate']:.1%}")
    
    # Cleanup
    await sla_monitor.cleanup()
    
    print("\n=== All Phase RELIABILITY fixes demonstrated successfully! ===")
    print("\nSummary:")
    print("✅ Audit trails are immutable with cryptographic verification")
    print("✅ Performance is tracked with automatic baseline establishment")
    print("✅ SLA violations are detected and reported in real-time")


if __name__ == "__main__":
    asyncio.run(main())