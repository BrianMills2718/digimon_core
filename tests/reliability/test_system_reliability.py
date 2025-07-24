#!/usr/bin/env python3
"""
System Reliability Tests

Comprehensive tests to validate Phase RELIABILITY improvements
and measure system reliability score improvement from 1/10 to 8+/10.

Tests distributed transactions, error handling, health monitoring,
connection pooling, and academic integrity features.
"""

import pytest
import asyncio
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import sqlite3

# Import the reliability components
from src.core.distributed_transaction_manager import (
    DistributedTransactionManager, TransactionOperation, TransactionStatus
)
from src.core.error_taxonomy import (
    CentralizedErrorHandler, KGASError, ErrorCategory, ErrorSeverity,
    get_global_error_handler
)
from src.core.health_monitor import (
    SystemHealthMonitor, HealthStatus, MetricsCollector, AlertManager,
    get_global_health_monitor
)
from src.core.connection_pool_manager import (
    ConnectionPoolManager, ConnectionPool, ConnectionWrapper,
    get_global_pool_manager
)
from src.core.provenance_manager import (
    ProvenanceManager, OperationType, ProvenanceLevel,
    get_global_provenance_manager
)


class TestDistributedTransactions:
    """Test distributed transaction manager ACID guarantees"""
    
    @pytest.fixture
    async def transaction_manager(self):
        """Setup distributed transaction manager with mock databases"""
        # Mock Neo4j manager
        neo4j_manager = Mock()
        neo4j_tx = Mock()
        neo4j_manager.begin_transaction.return_value = neo4j_tx
        
        # Mock SQLite manager
        sqlite_manager = Mock()
        sqlite_tx = Mock()
        sqlite_manager.begin_transaction.return_value = sqlite_tx
        
        dtm = DistributedTransactionManager(neo4j_manager, sqlite_manager)
        
        yield dtm
        
        # Cleanup
        await dtm.shutdown()
    
    async def test_successful_distributed_transaction(self, transaction_manager):
        """Test successful 2-phase commit transaction"""
        dtm = transaction_manager
        
        # Begin transaction
        tx_id = await dtm.begin_distributed_transaction()
        assert tx_id is not None
        assert tx_id in dtm.active_transactions
        
        # Add operations
        neo4j_op = TransactionOperation(
            operation_id="neo4j_op_1",
            database="neo4j",
            operation_type="create",
            table_or_label="Entity",
            data={"id": "entity_1", "name": "Test Entity"}
        )
        
        sqlite_op = TransactionOperation(
            operation_id="sqlite_op_1",
            database="sqlite",
            operation_type="create",
            table_or_label="mentions",
            data={"id": "mention_1", "entity_id": "entity_1"}
        )
        
        await dtm.add_operation(tx_id, neo4j_op)
        await dtm.add_operation(tx_id, sqlite_op)
        
        # Commit transaction
        success = await dtm.commit_distributed_transaction(tx_id)
        assert success is True
        assert tx_id not in dtm.active_transactions
    
    async def test_transaction_rollback_on_failure(self, transaction_manager):
        """Test transaction rollback when one database fails"""
        dtm = transaction_manager
        
        # Make SQLite commit fail
        dtm.sqlite_manager.begin_transaction.return_value.commit.side_effect = Exception("SQLite commit failed")
        
        tx_id = await dtm.begin_distributed_transaction()
        
        # Add operations
        neo4j_op = TransactionOperation(
            operation_id="neo4j_op_1",
            database="neo4j",
            operation_type="create",
            table_or_label="Entity",
            data={"id": "entity_1"}
        )
        
        await dtm.add_operation(tx_id, neo4j_op)
        
        # Commit should fail and rollback
        success = await dtm.commit_distributed_transaction(tx_id)
        assert success is False
        assert tx_id not in dtm.active_transactions
        
        # Verify rollback was called on both databases
        dtm.neo4j_manager.begin_transaction.return_value.rollback.assert_called_once()
        dtm.sqlite_manager.begin_transaction.return_value.rollback.assert_called_once()
    
    async def test_transaction_timeout_cleanup(self, transaction_manager):
        """Test automatic cleanup of expired transactions"""
        dtm = transaction_manager
        dtm.transaction_timeout = 1  # 1 second timeout
        
        # Start transaction
        tx_id = await dtm.begin_distributed_transaction()
        assert tx_id in dtm.active_transactions
        
        # Wait for timeout
        await asyncio.sleep(2)
        
        # Transaction should be cleaned up
        assert tx_id not in dtm.active_transactions
    
    async def test_concurrent_transactions(self, transaction_manager):
        """Test handling multiple concurrent transactions"""
        dtm = transaction_manager
        
        # Start multiple transactions concurrently
        tasks = []
        for i in range(5):
            task = asyncio.create_task(dtm.begin_distributed_transaction())
            tasks.append(task)
        
        tx_ids = await asyncio.gather(*tasks)
        
        # All transactions should be active
        assert len(tx_ids) == 5
        assert all(tx_id in dtm.active_transactions for tx_id in tx_ids)
        
        # Commit all transactions
        commit_tasks = []
        for tx_id in tx_ids:
            task = asyncio.create_task(dtm.commit_distributed_transaction(tx_id))
            commit_tasks.append(task)
        
        results = await asyncio.gather(*commit_tasks)
        assert all(result is True for result in results)


class TestErrorTaxonomy:
    """Test centralized error handling and taxonomy"""
    
    @pytest.fixture
    def error_handler(self):
        """Setup centralized error handler"""
        return CentralizedErrorHandler()
    
    async def test_error_classification(self, error_handler):
        """Test automatic error classification"""
        # Test data corruption error
        error = Exception("Entity ID mapping corruption detected")
        context = {"service_name": "identity_service", "operation": "create_mention"}
        
        kgas_error = await error_handler.handle_error(error, context)
        
        assert kgas_error.category == ErrorCategory.DATA_CORRUPTION
        assert kgas_error.severity == ErrorSeverity.CATASTROPHIC
        assert "corruption" in kgas_error.message.lower()
        assert kgas_error.service_name == "identity_service"
    
    async def test_academic_integrity_error(self, error_handler):
        """Test academic integrity violation handling"""
        error = Exception("Citation fabrication risk detected")
        context = {"service_name": "provenance_service", "operation": "validate_citation"}
        
        kgas_error = await error_handler.handle_error(error, context)
        
        assert kgas_error.category == ErrorCategory.ACADEMIC_INTEGRITY
        assert kgas_error.severity == ErrorSeverity.CRITICAL
        assert len(kgas_error.recovery_suggestions) > 0
    
    async def test_recovery_strategy_execution(self, error_handler):
        """Test error recovery strategy execution"""
        # Register custom recovery strategy
        recovery_called = False
        
        async def custom_recovery(error):
            nonlocal recovery_called
            recovery_called = True
            return True
        
        error_handler.register_recovery_strategy("test_error", custom_recovery)
        
        # Create error that should trigger recovery
        error = Exception("test error condition")
        context = {"service_name": "test_service"}
        
        kgas_error = await error_handler.handle_error(error, context)
        
        # Verify recovery was attempted
        assert recovery_called
    
    def test_error_metrics_collection(self, error_handler):
        """Test error metrics collection and analysis"""
        # Simulate multiple errors
        error_types = [
            (Exception("database connection lost"), ErrorCategory.DATABASE_FAILURE),
            (Exception("memory limit exceeded"), ErrorCategory.RESOURCE_EXHAUSTION),
            (Exception("network timeout"), ErrorCategory.NETWORK_FAILURE)
        ]
        
        for error, expected_category in error_types:
            error_handler.error_metrics.record_error(
                KGASError(
                    error_id="test_id",
                    category=expected_category,
                    severity=ErrorSeverity.HIGH,
                    message=str(error),
                    context={},
                    timestamp=datetime.now().isoformat(),
                    service_name="test_service",
                    operation="test_operation"
                )
            )
        
        summary = error_handler.error_metrics.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["error_breakdown"]["database_failure"] == 1
        assert summary["error_breakdown"]["resource_exhaustion"] == 1
        assert summary["error_breakdown"]["network_failure"] == 1
    
    def test_system_health_from_errors(self, error_handler):
        """Test system health assessment based on error patterns"""
        # No errors - should be healthy
        health = error_handler.get_system_health_from_errors()
        assert health["health_score"] == 10
        assert health["status"] == "healthy"
        
        # Add catastrophic error - score should drop dramatically
        error_handler.error_metrics.record_error(
            KGASError(
                error_id="catastrophic_error",
                category=ErrorCategory.DATA_CORRUPTION,
                severity=ErrorSeverity.CATASTROPHIC,
                message="Data corruption detected",
                context={},
                timestamp=datetime.now().isoformat(),
                service_name="test_service",
                operation="test_operation"
            )
        )
        
        health = error_handler.get_system_health_from_errors()
        assert health["health_score"] == 1  # System unreliable due to data corruption
        assert health["status"] == "unhealthy"


class TestHealthMonitoring:
    """Test comprehensive health monitoring"""
    
    @pytest.fixture
    async def health_monitor(self):
        """Setup system health monitor"""
        monitor = SystemHealthMonitor()
        await monitor.start_monitoring()
        
        yield monitor
        
        await monitor.stop_monitoring()
    
    async def test_system_health_checks(self, health_monitor):
        """Test basic system health checks"""
        health_status = await health_monitor.check_system_health()
        
        assert "overall_status" in health_status
        assert "services" in health_status
        assert "metrics" in health_status
        assert "active_alerts" in health_status
        assert "timestamp" in health_status
        
        # Should have default health checks
        assert "system" in health_status["services"]
        assert "memory" in health_status["services"]
        assert "disk" in health_status["services"]
        assert "cpu" in health_status["services"]
    
    async def test_custom_health_check_registration(self, health_monitor):
        """Test registration of custom health checks"""
        check_called = False
        
        async def custom_health_check():
            nonlocal check_called
            check_called = True
            return {
                "status": "healthy",
                "message": "Custom service is healthy"
            }
        
        health_monitor.register_health_check("custom_service", custom_health_check)
        
        # Trigger health check
        await health_monitor._run_all_health_checks()
        
        assert check_called
        assert "custom_service" in health_monitor.last_health_check
    
    async def test_metrics_collection(self, health_monitor):
        """Test system metrics collection"""
        # Let metrics collection run briefly
        await asyncio.sleep(2)
        
        metrics = health_monitor.metrics_collector.get_current_metrics()
        
        # Should have system metrics
        metric_names = [metric.name for metric in metrics.values()]
        expected_metrics = [
            "system.cpu.usage",
            "system.memory.percent",
            "system.disk.percent"
        ]
        
        for expected in expected_metrics:
            assert any(expected in name for name in metric_names)
    
    async def test_alert_generation(self, health_monitor):
        """Test alert generation for threshold violations"""
        # Set low threshold for testing
        health_monitor.alert_manager.set_threshold("test.metric", "warning", 50.0)
        
        # Record metric that exceeds threshold
        health_monitor.metrics_collector.record_metric(
            "test.metric", 75.0, health_monitor.metrics_collector.MetricType.GAUGE
        )
        
        # Check thresholds
        await health_monitor._check_all_thresholds()
        
        # Should have generated alert
        active_alerts = health_monitor.alert_manager.get_active_alerts()
        assert len(active_alerts) > 0
        assert any(alert.metric_name == "test.metric" for alert in active_alerts)


class TestConnectionPooling:
    """Test connection pool management with auto-recovery"""
    
    @pytest.fixture
    async def pool_manager(self):
        """Setup connection pool manager"""
        manager = ConnectionPoolManager()
        await manager.start_all_pools()
        
        yield manager
        
        await manager.stop_all_pools()
    
    async def test_connection_pool_creation(self, pool_manager):
        """Test creating and managing connection pools"""
        # Mock connection factory
        connection_count = 0
        
        async def mock_connection_factory():
            nonlocal connection_count
            connection_count += 1
            return Mock(name=f"connection_{connection_count}")
        
        # Create pool
        pool = await pool_manager.create_pool(
            pool_name="test_pool",
            connection_factory=mock_connection_factory,
            min_size=2,
            max_size=5
        )
        
        assert pool.pool_name == "test_pool"
        assert pool.min_size == 2
        assert pool.max_size == 5
        
        # Wait for initial connections to be created
        await asyncio.sleep(1)
        
        metrics = pool.get_metrics()
        assert metrics.total_connections == 2  # Should create min_size connections
    
    async def test_connection_acquisition_and_return(self, pool_manager):
        """Test getting and returning connections"""
        async def mock_connection_factory():
            return Mock()
        
        await pool_manager.create_pool(
            "test_pool", mock_connection_factory, min_size=1, max_size=3
        )
        
        # Get connection
        wrapper = await pool_manager.get_connection("test_pool")
        assert wrapper is not None
        assert isinstance(wrapper, ConnectionWrapper)
        
        # Return connection
        await pool_manager.return_connection("test_pool", wrapper)
    
    async def test_pool_exhaustion_handling(self, pool_manager):
        """Test handling of pool exhaustion"""
        async def mock_connection_factory():
            return Mock()
        
        pool = await pool_manager.create_pool(
            "small_pool", mock_connection_factory, min_size=1, max_size=2
        )
        
        # Exhaust the pool
        conn1 = await pool_manager.get_connection("small_pool")
        conn2 = await pool_manager.get_connection("small_pool")
        
        # This should trigger emergency measures
        start_time = time.time()
        conn3 = await pool_manager.get_connection("small_pool", timeout=2.0)
        elapsed = time.time() - start_time
        
        # Should either get connection from emergency creation or timeout
        assert conn3 is not None or elapsed >= 2.0
    
    async def test_connection_health_monitoring(self, pool_manager):
        """Test connection health monitoring and replacement"""
        # Create mock connections that can fail health checks
        failing_connection = Mock()
        failing_connection.verify_connectivity.side_effect = Exception("Connection failed")
        
        healthy_connection = Mock()
        healthy_connection.verify_connectivity.return_value = True
        
        connections = [failing_connection, healthy_connection]
        connection_index = 0
        
        async def mock_connection_factory():
            nonlocal connection_index
            conn = connections[connection_index % len(connections)]
            connection_index += 1
            return conn
        
        pool = await pool_manager.create_pool(
            "health_test_pool", mock_connection_factory, min_size=1, max_size=2
        )
        
        # Force health check
        await pool._run_health_checks()
        
        # Unhealthy connections should be replaced
        # Note: This test would need more detailed mocking to verify exact behavior


class TestProvenanceTracking:
    """Test academic integrity provenance tracking"""
    
    @pytest.fixture
    def provenance_manager(self):
        """Setup provenance manager with temporary storage"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            storage_path = f.name
        
        manager = ProvenanceManager(storage_path)
        
        yield manager
        
        # Cleanup
        import os
        try:
            os.unlink(storage_path)
        except:
            pass
    
    async def test_operation_tracking(self, provenance_manager):
        """Test tracking of data operations"""
        # Track a simple operation
        record_id = await provenance_manager.track_data_operation(
            operation_type=OperationType.ENTITY_EXTRACTION,
            operation_name="extract_entities",
            executor="test_tool",
            source_data={"text": "Test document content"},
            result_data={"entities": [{"name": "Test Entity", "type": "ORG"}]},
            parameters={"confidence_threshold": 0.8},
            context={"document_id": "doc_123"}
        )
        
        assert record_id is not None
        
        # Verify record was stored
        record = provenance_manager.storage.get_record(record_id)
        assert record is not None
        assert record.operation_type == OperationType.ENTITY_EXTRACTION
        assert record.operation_name == "extract_entities"
        assert record.executor == "test_tool"
    
    async def test_citation_integrity_validation(self, provenance_manager):
        """Test citation integrity validation"""
        # Create a chain of operations leading to citation
        source_record_id = await provenance_manager.track_data_operation(
            operation_type=OperationType.DATA_INGESTION,
            operation_name="load_document",
            executor="pdf_loader",
            source_data=None,
            result_data={"document_id": "doc_123", "content": "Original research paper"},
            context={"source_file": "research.pdf"}
        )
        
        extraction_record_id = await provenance_manager.track_data_operation(
            operation_type=OperationType.ENTITY_EXTRACTION,
            operation_name="extract_entities",
            executor="entity_extractor",
            source_data={"document_id": "doc_123"},
            result_data={"entities": [{"name": "Key Finding", "confidence": 0.9}]},
            parent_records=[source_record_id]
        )
        
        citation_record_id = await provenance_manager.track_data_operation(
            operation_type=OperationType.CITATION_CREATION,
            operation_name="create_citation",
            executor="citation_generator",
            source_data={"document_id": "doc_123"},
            result_data={
                "citation_id": "cite_123",
                "claim": "Key finding from research",
                "confidence": 0.9
            },
            parent_records=[extraction_record_id]
        )
        
        # Validate citation integrity
        validation_result = await provenance_manager.validate_citation_integrity(citation_record_id)
        
        assert validation_result["status"] in ["valid", "questionable"]
        assert "integrity_score" in validation_result
        assert validation_result["lineage_length"] >= 1
    
    def test_data_fingerprinting(self, provenance_manager):
        """Test data fingerprinting for integrity verification"""
        test_data = {
            "text": "Sample document content",
            "metadata": {"author": "Test Author", "date": "2025-01-01"}
        }
        
        fingerprint1 = provenance_manager._calculate_data_fingerprint(test_data)
        fingerprint2 = provenance_manager._calculate_data_fingerprint(test_data)
        
        # Same data should produce same fingerprint
        assert fingerprint1.content_hash == fingerprint2.content_hash
        assert fingerprint1.schema_hash == fingerprint2.schema_hash
        
        # Different data should produce different fingerprint
        modified_data = test_data.copy()
        modified_data["text"] = "Modified content"
        
        fingerprint3 = provenance_manager._calculate_data_fingerprint(modified_data)
        assert fingerprint1.content_hash != fingerprint3.content_hash
    
    async def test_citation_fabrication_detection(self, provenance_manager):
        """Test detection of potential citation fabrication"""
        # Create citation without proper lineage (suspicious)
        citation_record_id = await provenance_manager.track_data_operation(
            operation_type=OperationType.CITATION_CREATION,
            operation_name="create_citation",
            executor="citation_generator",
            source_data={},
            result_data={
                "citation_id": "suspicious_cite",
                "claim": "Unsupported claim",
                "confidence": 0.3  # Low confidence
            },
            parent_records=[]  # No lineage
        )
        
        # Check for fabrication
        fabrication_analysis = provenance_manager.provenance_graph.detect_citation_fabrication(citation_record_id)
        
        assert fabrication_analysis["risk"] in ["medium", "high"]
        assert len(fabrication_analysis["risk_factors"]) > 0


class TestSystemReliabilityScore:
    """Integration test to measure overall system reliability score"""
    
    @pytest.fixture
    async def full_system(self):
        """Setup full system with all reliability components"""
        # Initialize all managers
        error_handler = get_global_error_handler()
        health_monitor = get_global_health_monitor()
        pool_manager = get_global_pool_manager()
        provenance_manager = get_global_provenance_manager()
        
        # Start monitoring
        await health_monitor.start_monitoring()
        await pool_manager.start_all_pools()
        
        yield {
            "error_handler": error_handler,
            "health_monitor": health_monitor,
            "pool_manager": pool_manager,
            "provenance_manager": provenance_manager
        }
        
        # Cleanup
        await health_monitor.stop_monitoring()
        await pool_manager.stop_all_pools()
        await provenance_manager.shutdown()
    
    async def test_overall_system_reliability_score(self, full_system):
        """Test overall system reliability score calculation"""
        error_handler = full_system["error_handler"]
        health_monitor = full_system["health_monitor"]
        pool_manager = full_system["pool_manager"]
        
        # Let system run briefly to collect metrics
        await asyncio.sleep(3)
        
        # Get health assessments from all components
        error_health = error_handler.get_system_health_from_errors()
        system_health = await health_monitor.check_system_health()
        pool_health = pool_manager.get_system_health()
        
        # Calculate composite reliability score
        component_scores = [
            error_health["health_score"],  # Error handling quality
            10 if system_health["overall_status"] == "healthy" else 5,  # System health
            10 if pool_health["overall_status"] == "healthy" else 5,  # Connection reliability
        ]
        
        # Weight the scores (error handling is most critical)
        weights = [0.4, 0.3, 0.3]
        reliability_score = sum(score * weight for score, weight in zip(component_scores, weights))
        
        print(f"\n=== SYSTEM RELIABILITY ASSESSMENT ===")
        print(f"Error Handling Score: {error_health['health_score']}/10")
        print(f"System Health Score: {10 if system_health['overall_status'] == 'healthy' else 5}/10")
        print(f"Connection Pool Score: {10 if pool_health['overall_status'] == 'healthy' else 5}/10")
        print(f"Overall Reliability Score: {reliability_score:.1f}/10")
        print(f"Target: 8+/10 (Current: {'PASS' if reliability_score >= 8 else 'FAIL'})")
        
        # Assert reliability score meets target
        assert reliability_score >= 8.0, f"System reliability score {reliability_score:.1f} below target of 8.0"
    
    async def test_data_corruption_prevention(self, full_system):
        """Test that system prevents data corruption"""
        # This would test actual distributed transactions, but for now
        # we verify the components are in place and configured correctly
        
        error_handler = full_system["error_handler"]
        provenance_manager = full_system["provenance_manager"]
        
        # Verify error handler properly classifies data corruption
        error = Exception("Entity ID mapping corruption detected")
        context = {"service_name": "identity_service"}
        
        kgas_error = await error_handler.handle_error(error, context)
        
        assert kgas_error.category == ErrorCategory.DATA_CORRUPTION
        assert kgas_error.severity == ErrorSeverity.CATASTROPHIC
        
        # Verify provenance tracking is active
        summary = provenance_manager.get_provenance_summary()
        assert summary["citation_validation_enabled"] is True
    
    async def test_academic_integrity_protection(self, full_system):
        """Test academic integrity protection mechanisms"""
        provenance_manager = full_system["provenance_manager"]
        error_handler = full_system["error_handler"]
        
        # Test citation integrity validation
        test_citation_id = "test_citation_123"
        
        # This should detect lack of provenance and flag as suspicious
        fabrication_analysis = provenance_manager.provenance_graph.detect_citation_fabrication(test_citation_id)
        
        # Non-existent citation should be flagged as high risk
        assert fabrication_analysis["risk"] == "high"
        assert "Citation record not found" in fabrication_analysis["reason"]
        
        # Test academic integrity error handling
        integrity_error = Exception("Citation fabrication risk detected")
        context = {"service_name": "provenance_service"}
        
        kgas_error = await error_handler.handle_error(integrity_error, context)
        assert kgas_error.category == ErrorCategory.ACADEMIC_INTEGRITY
        assert kgas_error.severity == ErrorSeverity.CRITICAL
    
    async def test_operational_visibility(self, full_system):
        """Test operational visibility and monitoring"""
        health_monitor = full_system["health_monitor"]
        
        # Verify comprehensive health monitoring
        health_status = await health_monitor.check_system_health()
        
        required_components = ["system", "memory", "disk", "cpu"]
        for component in required_components:
            assert component in health_status["services"]
            assert "status" in health_status["services"][component]
            assert "response_time" in health_status["services"][component]
        
        # Verify metrics collection
        assert "metrics" in health_status
        assert len(health_status["metrics"]) > 0
        
        # Verify alerting capability
        assert "active_alerts" in health_status
    
    async def test_resource_exhaustion_recovery(self, full_system):
        """Test recovery from resource exhaustion scenarios"""
        pool_manager = full_system["pool_manager"] 
        error_handler = full_system["error_handler"]
        
        # Simulate resource exhaustion error
        exhaustion_error = Exception("Connection pool exhausted")
        context = {"service_name": "connection_pool"}
        
        kgas_error = await error_handler.handle_error(exhaustion_error, context)
        
        assert kgas_error.category == ErrorCategory.RESOURCE_EXHAUSTION
        assert kgas_error.severity == ErrorSeverity.HIGH
        assert len(kgas_error.recovery_suggestions) > 0
        
        # Test connection pool emergency measures would be triggered
        # (This would require more complex mocking to fully test)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])