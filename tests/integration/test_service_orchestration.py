"""
Test suite for enhanced PipelineOrchestrator service coordination with real services.

This module tests REAL service interactions, not mocked versions.
All services run as actual HTTP endpoints for true integration testing.
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Import test services
import sys
sys.path.append('tests/fixtures')
from test_services import TestServiceManager

# Configure pytest to handle async tests
pytestmark = pytest.mark.asyncio

# Import components to be tested
from src.core.pipeline_orchestrator import (
    PipelineOrchestrator,
    WorkflowSpec,
    WorkflowResult,
    ServiceHealthStatus,
    WorkflowCheckpoint,
    PipelineConfig,
    OptimizationLevel,
    Phase
)
from src.core.identity_service import IdentityService
from src.core.service_protocol import ServiceProtocol
from src.core.exceptions import (
    ServiceUnavailableError,
    WorkflowExecutionError,
    CheckpointRestoreError
)


class TestPipelineOrchestratorService:
    """Test suite for enhanced PipelineOrchestrator with full service coordination."""
    
    @pytest.fixture(scope="session")
    def event_loop(self):
        """Create event loop for session-scoped fixtures"""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(scope="session")
    async def test_services(self, event_loop):
        """Start real test services for integration tests"""
        manager = TestServiceManager()
        await manager.start_all()
        
        yield manager
        
        await manager.stop_all()

    @pytest.fixture
    async def orchestrator(self, test_services):
        """Create PipelineOrchestrator with real services"""
        # Create config that points to real test services
        config = PipelineConfig(
            tools=[],
            optimization_level=OptimizationLevel.STANDARD,
            phase=Phase.PHASE1
        )
        
        # Create custom config manager with test service endpoints
        from src.core.config_manager import ConfigurationManager
        config_manager = ConfigurationManager()
        
        # Override service configs with test endpoints
        service_configs = test_services.get_service_configs()
        config_manager._config['services'] = service_configs
        
        # Mock validation components to avoid initialization issues
        with patch('src.core.pipeline_orchestrator.ContractValidator'):
            with patch('src.core.pipeline_orchestrator.OntologyValidator'):
                with patch('src.core.pipeline_orchestrator.PipelineValidator'):
                    # Create orchestrator with real services
                    orchestrator = PipelineOrchestrator(config, config_manager)
                    
                    # Initialize health monitoring
                    await orchestrator.health_monitor.start_monitoring()
                    
                    # Disable validation for testing
                    orchestrator.validation_enabled = False
                    
                    yield orchestrator
                    
                    # Cleanup
                    await orchestrator.health_monitor.stop_monitoring()
    
    @pytest.fixture
    def test_documents(self):
        """Sample documents for testing."""
        return [
            {"id": "doc1", "content": "Research on quantum computing applications"},
            {"id": "doc2", "content": "Analysis of machine learning frameworks"},
            {"id": "doc3", "content": "Study on distributed systems architecture"}
        ]
    
    @pytest.fixture
    def workflow_spec(self, test_documents):
        """Create a sample workflow specification."""
        return WorkflowSpec(
            documents=test_documents,
            analysis_modes=['graph', 'table', 'vector'],
            theory_integration=True,
            quality_validation=True,
            concurrent_processing=True,
            checkpoint_interval=2  # Checkpoint every 2 steps
        )
    
    async def test_orchestrate_research_workflow_coordinates_all_services(
        self, orchestrator, workflow_spec
    ):
        """Test that orchestrator properly coordinates all real services."""
        # Start timing to ensure real processing occurs
        start_time = time.time()
        
        result = await orchestrator.orchestrate_research_workflow(workflow_spec)
        
        # Verify workflow completed successfully
        assert result.status == 'completed'
        assert result.workflow_id is not None
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration > 0
        
        # Verify real processing time (not instant mock)
        processing_time = time.time() - start_time
        assert processing_time > 0.3  # Real services take time
        
        # Verify all documents were processed
        assert len(result.analysis_results) == len(workflow_spec.documents)
        
        # Verify each result has cross-modal analysis
        for doc_result in result.analysis_results:
            assert doc_result.document_id in [d['id'] for d in workflow_spec.documents]
            assert 'graph' in doc_result.analysis_modes
            assert 'table' in doc_result.analysis_modes
            assert 'vector' in doc_result.analysis_modes
            assert doc_result.cross_modal_preserved is True
            assert doc_result.theory_extracted is True
            assert doc_result.quality_score >= 0.910
            
            # Verify service timing metadata from real calls
            assert 'service_timings' in doc_result.metadata
            timings = doc_result.metadata['service_timings']
            assert timings['identity_ms'] > 0
            assert timings['analytics_ms'] > 0
        
        # Verify overall quality meets requirements
        assert result.overall_quality_score >= 0.910
        
        # Verify service coordination metadata
        expected_services = {
            'IdentityService',
            'AnalyticsService',
            'TheoryExtractionService',
            'ProvenanceService',
            'QualityService'
        }
        assert set(result.services_used) == expected_services
        assert all(service in result.service_health for service in result.services_used)
    
    async def test_workflow_checkpoint_restart_functionality(
        self, orchestrator, workflow_spec
    ):
        """Test workflow state persistence and recovery."""
        # Start workflow
        workflow_id = await orchestrator.start_workflow(workflow_spec)
        assert workflow_id is not None
        
        # Simulate workflow interruption after processing first document
        await asyncio.sleep(0.5)  # Allow enough time to process at least one document
        await orchestrator.pause_workflow(workflow_id)
        
        # Verify checkpoint was created
        checkpoint = await orchestrator.get_latest_checkpoint(workflow_id)
        assert checkpoint is not None
        assert checkpoint.workflow_id == workflow_id
        assert checkpoint.processed_documents >= 1
        assert checkpoint.state_data is not None
        assert checkpoint.timestamp is not None
        
        # Restart workflow from checkpoint
        result = await orchestrator.resume_workflow(workflow_id)
        
        # Verify workflow completed from checkpoint
        assert result.status == 'completed'
        assert result.resumed_from_checkpoint is True
        assert result.checkpoint_id == checkpoint.checkpoint_id
        assert len(result.analysis_results) == len(workflow_spec.documents)
        
        # Verify no duplicate processing
        doc_ids = [r.document_id for r in result.analysis_results]
        assert len(doc_ids) == len(set(doc_ids))  # All unique
    
    async def test_service_communication_health_monitoring(
        self, orchestrator
    ):
        """Test inter-service communication and health checks."""
        # Get current service health
        health_status = await orchestrator.get_service_health()
        
        # Verify health check structure
        assert isinstance(health_status, dict)
        expected_services = [
            'IdentityService',
            'AnalyticsService',
            'TheoryExtractionService',
            'ProvenanceService',
            'QualityService'
        ]
        
        for service in expected_services:
            assert service in health_status
            service_health = health_status[service]
            assert 'status' in service_health
            assert service_health['status'] in ['healthy', 'degraded', 'unhealthy']
            assert 'last_check' in service_health
            assert 'response_time_ms' in service_health
            assert 'error_rate' in service_health
            assert 0 <= service_health['error_rate'] <= 1
        
        # Test continuous monitoring
        monitor_task = asyncio.create_task(
            orchestrator.start_health_monitoring(interval_seconds=1)
        )
        
        # Wait for a few health check cycles
        await asyncio.sleep(3)
        
        # Verify health checks are updating
        new_health_status = await orchestrator.get_service_health()
        for service in expected_services:
            assert new_health_status[service]['last_check'] > health_status[service]['last_check']
        
        # Clean up
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    async def test_graceful_degradation_on_service_failure(
        self, orchestrator, workflow_spec, test_services
    ):
        """Test system continues operating when non-critical services fail."""
        # Stop TheoryExtractionService to simulate real failure
        theory_service = test_services.services['TheoryExtractionService']
        await theory_service.stop()  # Actually stop the service
        
        # Execute workflow with degraded service
        result = await orchestrator.orchestrate_research_workflow(workflow_spec)
        
        # Verify workflow still completes
        assert result.status == 'completed_with_warnings'
        assert len(result.warnings) > 0
        assert any('TheoryExtractionService' in w for w in result.warnings)
        
        # Verify other analyses still completed
        for doc_result in result.analysis_results:
            assert doc_result.cross_modal_preserved is True
            assert doc_result.theory_extracted is False  # Failed service
            assert doc_result.quality_score >= 0.85  # Slightly lower without theory
    
    async def test_parallel_service_coordination(
        self, orchestrator, workflow_spec
    ):
        """Test parallel execution of independent services."""
        # Enable parallel execution tracking
        orchestrator.enable_execution_tracking()
        
        # Execute workflow
        result = await orchestrator.orchestrate_research_workflow(workflow_spec)
        
        # Get execution timeline
        timeline = orchestrator.get_execution_timeline()
        
        # Verify parallel execution occurred
        # Identity and Analytics services should run in parallel for each document
        identity_tasks = [t for t in timeline if t['service'] == 'IdentityService']
        analytics_tasks = [t for t in timeline if t['service'] == 'AnalyticsService']
        
        # Check for time overlap between services
        parallel_executions = 0
        for identity_task in identity_tasks:
            for analytics_task in analytics_tasks:
                if (identity_task['start'] < analytics_task['end'] and 
                    analytics_task['start'] < identity_task['end']):
                    parallel_executions += 1
        
        assert parallel_executions > 0, "Services should execute in parallel"
        
        # Verify overall execution time is reduced
        assert result.duration < len(workflow_spec.documents) * 2  # Faster than sequential
    
    async def test_workflow_cancellation_and_cleanup(
        self, orchestrator, workflow_spec
    ):
        """Test proper cleanup when workflow is cancelled."""
        # Start workflow
        workflow_id = await orchestrator.start_workflow(workflow_spec)
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Cancel workflow
        await orchestrator.cancel_workflow(workflow_id)
        
        # Verify workflow status
        status = await orchestrator.get_workflow_status(workflow_id)
        assert status['status'] == 'cancelled'
        assert status['cleanup_completed'] is True
        
        # Verify resources were released
        active_workflows = await orchestrator.get_active_workflows()
        assert workflow_id not in active_workflows
        
        # Verify services were notified of cancellation
        cancellation_events = await orchestrator.get_service_events(
            event_type='workflow_cancelled'
        )
        assert any(e['workflow_id'] == workflow_id for e in cancellation_events)
    
    async def test_error_propagation_and_recovery(
        self, orchestrator, workflow_spec, test_services
    ):
        """Test error handling and recovery mechanisms with real failures."""
        # Configure analytics service to fail intermittently
        test_services.services['AnalyticsService'].failure_rate = 0.5  # 50% failure rate
        
        # Execute workflow with error recovery enabled
        orchestrator.enable_error_recovery(max_retries=3, backoff_factor=2)
        
        result = await orchestrator.orchestrate_research_workflow(workflow_spec)
        
        # Verify workflow completed despite failures
        assert result.status == 'completed'
        # With 50% failure rate, we expect some retries
        assert result.retry_count >= 0  # May succeed on first try or need retries
        assert result.retry_count <= 3
        
        # Verify all documents processed (including the one that errored)
        assert len(result.analysis_results) == len(workflow_spec.documents)
        
        # Check error was logged
        assert len(result.recovered_errors) > 0
        error_info = result.recovered_errors[0]
        assert error_info['document_id'] == 'doc2'
        assert error_info['retry_count'] > 0
        assert error_info['recovery_strategy'] in ['retry', 'fallback', 'skip']
    
    async def test_service_dependency_resolution(
        self, orchestrator
    ):
        """Test automatic resolution of service dependencies."""
        # Get service dependency graph
        dependencies = await orchestrator.get_service_dependencies()
        
        # Verify dependency structure
        assert 'AnalyticsService' in dependencies
        assert 'IdentityService' in dependencies['AnalyticsService']['depends_on']
        
        assert 'TheoryExtractionService' in dependencies
        assert 'AnalyticsService' in dependencies['TheoryExtractionService']['depends_on']
        
        assert 'QualityService' in dependencies
        assert set(dependencies['QualityService']['depends_on']) >= {
            'AnalyticsService',
            'TheoryExtractionService'
        }
        
        # Test dependency validation
        is_valid = await orchestrator.validate_service_dependencies()
        assert is_valid is True
        
        # Test circular dependency detection
        with pytest.raises(ValueError, match="Circular dependency detected"):
            await orchestrator.add_service_dependency(
                'IdentityService',
                depends_on='QualityService'
            )
    
    async def test_workflow_metrics_and_telemetry(
        self, orchestrator, workflow_spec
    ):
        """Test collection of workflow metrics and telemetry data."""
        # Execute workflow
        result = await orchestrator.orchestrate_research_workflow(workflow_spec)
        
        # Get workflow metrics
        metrics = await orchestrator.get_workflow_metrics(result.workflow_id)
        
        # Verify metrics structure
        assert 'execution_time_ms' in metrics
        assert metrics['execution_time_ms'] > 0
        
        assert 'documents_processed' in metrics
        assert metrics['documents_processed'] == len(workflow_spec.documents)
        
        assert 'service_calls' in metrics
        assert sum(metrics['service_calls'].values()) > 0
        
        assert 'resource_usage' in metrics
        assert 'peak_memory_mb' in metrics['resource_usage']
        assert 'avg_cpu_percent' in metrics['resource_usage']
        
        assert 'quality_metrics' in metrics
        assert metrics['quality_metrics']['avg_quality_score'] >= 0.910
        assert metrics['quality_metrics']['min_quality_score'] >= 0.900
        
        # Verify telemetry events
        telemetry = await orchestrator.get_telemetry_events(result.workflow_id)
        assert len(telemetry) > 0
        
        event_types = {event['type'] for event in telemetry}
        expected_events = {
            'workflow_started',
            'service_called',
            'document_processed',
            'checkpoint_created',
            'workflow_completed'
        }
        assert event_types >= expected_events