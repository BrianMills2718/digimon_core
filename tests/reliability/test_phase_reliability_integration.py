"""
Integration tests for Phase RELIABILITY implementations.

Tests all three components working together:
1. Audit Trail Immutability
2. Performance Tracking
3. SLA Monitoring
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from src.core.provenance_manager import ProvenanceManager
from src.monitoring.performance_tracker import PerformanceTracker
from src.core.sla_monitor import SLAMonitor, SLAThreshold, SLASeverity


@pytest.mark.asyncio
async def test_complete_reliability_integration():
    """Test all three reliability components working together."""
    
    # Initialize components
    provenance_manager = ProvenanceManager()
    performance_tracker = PerformanceTracker()
    sla_monitor = SLAMonitor(performance_tracker=performance_tracker)
    
    # Track violations
    violations = []
    
    async def violation_handler(violation):
        violations.append(violation)
    
    sla_monitor.register_alert_handler(violation_handler)
    
    try:
        # 1. Create source document with provenance tracking
        source_id = await provenance_manager.register_source({
            "id": "test_document",
            "content": "This is a test document for reliability testing."
        })
        
        # 2. Create citations with performance tracking
        citations = []
        for i in range(5):
            # Start performance tracking
            timer_id = await performance_tracker.start_operation("citation_creation")
            
            # Create citation
            citation = await provenance_manager.create_citation(
                source_id=source_id,
                text="test",
                start_pos=10,
                end_pos=14,
                metadata={"index": i}
            )
            citations.append(citation)
            
            # End performance tracking
            duration = await performance_tracker.end_operation(timer_id, success=True)
            
            # Check SLA
            await sla_monitor.check_operation("citation_creation", duration, True)
        
        # 3. Modify citations with audit trail
        for i, citation in enumerate(citations[:3]):
            timer_id = await performance_tracker.start_operation("citation_modification")
            
            # Simulate some slow operations
            if i == 2:
                await asyncio.sleep(0.1)  # Slow operation
            
            await provenance_manager.modify_citation(
                citation_id=citation["id"],
                new_text=f"modified test {i}",
                reason=f"Integration test modification {i}",
                modifier=f"test_user_{i}"
            )
            
            duration = await performance_tracker.end_operation(timer_id, success=True)
            await sla_monitor.check_operation("citation_modification", duration, True)
        
        # 4. Verify audit trail integrity
        for citation in citations:
            is_valid = await provenance_manager.verify_audit_integrity(citation["id"])
            assert is_valid is True
        
        # 5. Check performance statistics
        citation_stats = await performance_tracker.get_operation_stats("citation_creation")
        assert citation_stats["sample_count"] == 5
        assert citation_stats["success_rate"] == 1.0
        
        mod_stats = await performance_tracker.get_operation_stats("citation_modification")
        assert mod_stats["sample_count"] == 3
        
        # 6. Set custom SLA and trigger violation
        await sla_monitor.set_sla("citation_modification", SLAThreshold(
            operation="citation_modification",
            max_duration=0.05,
            warning_duration=0.04,
            critical_duration=0.1,
            max_error_rate=0.1,
            min_success_rate=0.9,
            evaluation_window=10
        ))
        
        # This should trigger a violation (we had one slow operation)
        timer_id = await performance_tracker.start_operation("citation_modification")
        await asyncio.sleep(0.06)  # Exceed threshold
        duration = await performance_tracker.end_operation(timer_id, success=True)
        await sla_monitor.check_operation("citation_modification", duration, True)
        
        # 7. Verify SLA violation was detected
        assert len(violations) > 0
        assert any(v.operation == "citation_modification" for v in violations)
        
        # 8. Generate reports
        sla_report = await sla_monitor.get_sla_report()
        assert sla_report["summary"]["total_checks"] > 0
        
        perf_summary = await performance_tracker.get_system_summary()
        assert len(perf_summary["tracked_operations"]) >= 2
        
        # 9. Test persistence (baselines and config)
        temp_dir = tempfile.mkdtemp()
        try:
            perf_path = Path(temp_dir) / "perf_data.json"
            sla_path = Path(temp_dir) / "sla_config.json"
            
            # Create new instances with persistence paths
            perf_tracker2 = PerformanceTracker(storage_path=perf_path)
            sla_monitor2 = SLAMonitor(
                performance_tracker=perf_tracker2,
                config_path=sla_path
            )
            
            # Perform operations to save data
            await sla_monitor2.set_sla("test_op", SLAThreshold(
                operation="test_op",
                max_duration=1.0,
                warning_duration=0.8,
                critical_duration=2.0,
                max_error_rate=0.05,
                min_success_rate=0.95,
                evaluation_window=100
            ))
            
            timer_id = await perf_tracker2.start_operation("test_op")
            await asyncio.sleep(0.01)
            await perf_tracker2.end_operation(timer_id, success=True)
            
            # Wait for saves
            await asyncio.sleep(0.1)
            
            # Verify files exist
            assert perf_path.exists()
            assert sla_path.exists()
            
        finally:
            shutil.rmtree(temp_dir)
        
        # 10. Verify complete integration
        assert all([
            # Provenance tracking works
            len(citations) == 5,
            all(await provenance_manager.verify_audit_integrity(c["id"]) for c in citations),
            
            # Performance tracking works
            citation_stats["sample_count"] == 5,
            mod_stats["sample_count"] >= 3,
            
            # SLA monitoring works
            len(violations) > 0,
            sla_report["summary"]["total_checks"] > 0,
        ])
        
        print("\n✅ All Phase RELIABILITY components integrated successfully!")
        print(f"- Created {len(citations)} citations with audit trails")
        print(f"- Tracked {perf_summary['total_operations']} operations")
        print(f"- Detected {len(violations)} SLA violations")
        print(f"- All audit trails verified as intact")
        
    finally:
        # Cleanup
        await sla_monitor.cleanup()


@pytest.mark.asyncio
async def test_reliability_under_load():
    """Test reliability components under concurrent load."""
    
    provenance_manager = ProvenanceManager()
    performance_tracker = PerformanceTracker()
    sla_monitor = SLAMonitor(performance_tracker=performance_tracker)
    
    try:
        # Register source
        source_id = await provenance_manager.register_source({
            "id": "load_test_source",
            "content": "A" * 1000  # Large content
        })
        
        # Concurrent citation operations
        async def create_and_modify_citation(index):
            # Create
            timer_id = await performance_tracker.start_operation("concurrent_create")
            citation = await provenance_manager.create_citation(
                source_id=source_id,
                text="A" * 10,
                start_pos=index * 10,
                end_pos=(index + 1) * 10
            )
            duration = await performance_tracker.end_operation(timer_id, success=True)
            await sla_monitor.check_operation("concurrent_create", duration, True)
            
            # Modify
            timer_id = await performance_tracker.start_operation("concurrent_modify")
            await provenance_manager.modify_citation(
                citation_id=citation["id"],
                new_text="B" * 10,
                reason="Load test",
                modifier=f"user_{index}"
            )
            duration = await performance_tracker.end_operation(timer_id, success=True)
            await sla_monitor.check_operation("concurrent_modify", duration, True)
            
            # Verify
            is_valid = await provenance_manager.verify_audit_integrity(citation["id"])
            return is_valid
        
        # Run concurrent operations
        tasks = [create_and_modify_citation(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All audit trails should be valid
        assert all(results)
        
        # Check performance metrics
        create_stats = await performance_tracker.get_operation_stats("concurrent_create")
        modify_stats = await performance_tracker.get_operation_stats("concurrent_modify")
        
        assert create_stats["sample_count"] == 20
        assert modify_stats["sample_count"] == 20
        
        # Generate final report
        sla_report = await sla_monitor.get_sla_report()
        print(f"\n📊 Load Test Results:")
        print(f"- Total operations: {sla_report['summary']['total_checks']}")
        print(f"- Violation rate: {sla_report['summary']['violation_rate']:.2%}")
        
    finally:
        await sla_monitor.cleanup()


@pytest.mark.asyncio
async def test_error_handling_integration():
    """Test error handling across all components."""
    
    provenance_manager = ProvenanceManager()
    performance_tracker = PerformanceTracker()
    sla_monitor = SLAMonitor(performance_tracker=performance_tracker)
    
    try:
        # Test invalid citation creation
        timer_id = await performance_tracker.start_operation("invalid_citation")
        
        with pytest.raises(ValueError):
            await provenance_manager.create_citation(
                source_id="nonexistent",
                text="test",
                start_pos=0,
                end_pos=4
            )
        
        # Mark operation as failed
        duration = await performance_tracker.end_operation(timer_id, success=False)
        await sla_monitor.check_operation("invalid_citation", duration, False)
        
        # Check error tracking
        stats = await performance_tracker.get_operation_stats("invalid_citation")
        assert stats["success_rate"] == 0.0  # All operations failed
        
        # Error rate should trigger SLA violation if threshold set
        await sla_monitor.set_sla("invalid_citation", SLAThreshold(
            operation="invalid_citation",
            max_duration=10.0,
            warning_duration=5.0,
            critical_duration=20.0,
            max_error_rate=0.5,  # 50% error rate threshold
            min_success_rate=0.5,
            evaluation_window=10
        ))
        
        # This should trigger error rate violation
        violation = await sla_monitor.check_operation("invalid_citation", 1.0, False)
        assert violation is not None
        assert violation.violation_type == "error_rate"
        
    finally:
        await sla_monitor.cleanup()


if __name__ == "__main__":
    # Run integration tests
    asyncio.run(test_complete_reliability_integration())
    asyncio.run(test_reliability_under_load())
    asyncio.run(test_error_handling_integration())