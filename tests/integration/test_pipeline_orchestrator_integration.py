"""
Integration tests for PipelineOrchestrator before decomposition

This test suite captures the complete behavior of the 1,460-line pipeline orchestrator
to ensure all functionality is preserved during decomposition.

Test Categories:
1. Basic pipeline execution
2. Service coordination and health monitoring  
3. Workflow management with checkpoints
4. Query execution interface
5. Configuration and validation integration
6. Error handling and recovery
7. Performance tracking and metrics
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from src.core.pipeline_orchestrator import (
    PipelineOrchestrator, PipelineConfig, OptimizationLevel, Phase,
    PipelineResult, QueryResult
)
from src.core.workflow_models import WorkflowSpec, DocumentResult, WorkflowStatus
from src.core.tool_protocol import Tool


class MockTool(Tool):
    """Mock tool for testing pipeline execution"""
    
    def __init__(self, name: str, result_data: Dict[str, Any] = None, should_fail: bool = False):
        self.tool_name = name
        self.result_data = result_data or {}
        self.should_fail = should_fail
        self.execute_called = False
        self.last_input = None
        self.last_context = None
    
    def execute(self, input_data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute mock tool"""
        self.execute_called = True
        self.last_input = input_data
        self.last_context = context
        
        if self.should_fail:
            raise RuntimeError(f"Mock tool {self.tool_name} intentionally failed")
        
        # Return merged result
        result = {**input_data, **self.result_data}
        result[f"{self.tool_name}_executed"] = True
        return result


@pytest.fixture
def temp_document():
    """Create temporary test document"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document with some sample text for processing.")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture 
def mock_service_manager():
    """Mock service manager for testing"""
    with patch('src.core.pipeline_orchestrator.get_service_manager') as mock_get_sm:
        mock_sm = Mock()
        mock_sm.identity_service = Mock()
        mock_sm.provenance_service = Mock()
        mock_sm.quality_service = Mock()
        mock_sm.get_neo4j_driver.return_value = None
        mock_get_sm.return_value = mock_sm
        yield mock_sm


@pytest.fixture
def basic_pipeline_config():
    """Basic pipeline configuration for testing"""
    tools = [
        MockTool("PDFLoader", {"documents": [{"text": "sample text"}]}),
        MockTool("TextChunker", {"chunks": [{"text": "sample", "chunk_id": "1"}]}),
        MockTool("SpacyNER", {"entities": [{"name": "Entity1", "type": "PERSON"}]}),
        MockTool("EntityBuilder", {"entities": [{"canonical_name": "Entity1"}]})
    ]
    
    return PipelineConfig(
        tools=tools,
        optimization_level=OptimizationLevel.STANDARD,
        phase=Phase.PHASE1,
        confidence_threshold=0.7
    )


class TestBasicPipelineExecution:
    """Test basic pipeline execution functionality"""
    
    def test_pipeline_execution_with_valid_config(self, basic_pipeline_config, temp_document, mock_service_manager):
        """Test successful pipeline execution with valid configuration"""
        orchestrator = PipelineOrchestrator(basic_pipeline_config)
        
        result = orchestrator.execute([temp_document])
        
        # Verify execution results structure
        assert isinstance(result, dict)
        assert "pipeline_config" in result
        assert "execution_results" in result
        assert "final_result" in result
        assert "execution_metadata" in result
        
        # Verify pipeline config
        config = result["pipeline_config"]
        assert config["optimization_level"] == "standard"
        assert config["phase"] == "phase1"
        assert config["tools_count"] == 4
        assert config["document_count"] == 1
        
        # Verify all tools executed successfully
        exec_results = result["execution_results"]
        assert len(exec_results) == 4
        for i, tool_result in enumerate(exec_results):
            assert tool_result["tool_index"] == i
            assert tool_result["status"] == "success"
            assert tool_result["execution_time"] > 0
            assert "result_summary" in tool_result
        
        # Verify metadata
        metadata = result["execution_metadata"]
        assert metadata["success"] is True
        assert metadata["total_time"] > 0
        assert metadata["error_summary"] is None
        
        # Verify tools were called in sequence
        for tool in basic_pipeline_config.tools:
            assert tool.execute_called
    
    def test_pipeline_execution_with_tool_failure(self, mock_service_manager):
        """Test pipeline execution when one tool fails"""
        tools = [
            MockTool("Tool1", {"step1": "complete"}),
            MockTool("Tool2", should_fail=True),  # This tool will fail
            MockTool("Tool3", {"step3": "complete"})  # This should not execute
        ]
        
        config = PipelineConfig(tools=tools)
        orchestrator = PipelineOrchestrator(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            result = orchestrator.execute([temp_path])
            
            # Verify execution stopped at failure
            exec_results = result["execution_results"]
            assert len(exec_results) == 2  # Only first two tools
            
            # First tool succeeded
            assert exec_results[0]["status"] == "success"
            
            # Second tool failed
            assert exec_results[1]["status"] == "error"
            assert "error" in exec_results[1]
            assert "Tool2" in exec_results[1]["error"]
            
            # Verify overall failure
            assert result["execution_metadata"]["success"] is False
            assert result["execution_metadata"]["error_summary"] is not None
            
            # Third tool should not have been called
            assert not tools[2].execute_called
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_pipeline_execution_input_validation(self, basic_pipeline_config, mock_service_manager):
        """Test input validation for pipeline execution"""
        orchestrator = PipelineOrchestrator(basic_pipeline_config)
        
        # Empty document paths
        with pytest.raises(ValueError, match="document_paths cannot be empty"):
            orchestrator.execute([])
        
        # Non-list document paths
        with pytest.raises(TypeError, match="document_paths must be a list"):
            orchestrator.execute("not_a_list")
        
        # Non-existent file
        with pytest.raises(FileNotFoundError):
            orchestrator.execute(["/non/existent/file.txt"])
        
        # Invalid queries parameter
        with pytest.raises(TypeError, match="queries must be a list or None"):
            orchestrator.execute(["/some/file.txt"], queries="invalid")
    
    def test_execution_statistics_tracking(self, basic_pipeline_config, temp_document, mock_service_manager):
        """Test execution statistics are properly tracked"""
        orchestrator = PipelineOrchestrator(basic_pipeline_config)
        
        result = orchestrator.execute([temp_document])
        stats = orchestrator.get_execution_stats()
        
        # Verify stats structure
        assert isinstance(stats, dict)
        assert "total_execution_time" in stats
        assert "tool_execution_times" in stats
        assert "average_tool_time" in stats
        assert "config_summary" in stats
        assert "memory_usage" in stats
        assert "errors" in stats
        
        # Verify values
        assert stats["total_execution_time"] > 0
        assert len(stats["tool_execution_times"]) == 4
        assert stats["average_tool_time"] > 0
        assert stats["config_summary"]["phase"] == "phase1"
        assert len(stats["errors"]) == 0  # No errors in successful execution


class TestServiceCoordination:
    """Test service coordination and health monitoring"""
    
    @pytest.mark.asyncio
    async def test_service_health_monitoring_initialization(self, mock_service_manager):
        """Test service health monitoring is properly initialized"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {
                'IdentityService': {
                    'health_endpoint': 'http://localhost:8002/health',
                    'health_timeout': 5.0,
                    'critical': True
                },
                'AnalyticsService': {
                    'health_endpoint': 'http://localhost:8001/health',
                    'health_timeout': 3.0,
                    'critical': True
                }
            }
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Verify health monitor was initialized
            assert orchestrator.health_monitor is not None
            assert orchestrator.health_monitor.check_interval == 30
            
            # Verify services were registered
            registered_services = list(orchestrator.health_monitor.services.keys())
            assert 'IdentityService' in registered_services
            assert 'AnalyticsService' in registered_services
    
    @pytest.mark.asyncio
    async def test_get_service_health(self, mock_service_manager):
        """Test getting service health status"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j', 
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            health_status = await orchestrator.get_service_health()
            
            # Should return dictionary even if no services registered
            assert isinstance(health_status, dict)
    
    @pytest.mark.asyncio
    async def test_mark_service_unhealthy(self, mock_service_manager):
        """Test marking a service as unhealthy"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {
                'TestService': {
                    'health_endpoint': 'http://localhost:8000/health',
                    'health_timeout': 5.0,
                    'critical': True
                }
            }
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Mark service as unhealthy
            await orchestrator.mark_service_unhealthy('TestService')
            
            # Verify service was removed from active monitoring
            assert 'TestService' not in orchestrator.health_monitor.services
            
            # Verify it was stored for restoration
            assert hasattr(orchestrator, '_disabled_services')
            assert 'TestService' in orchestrator._disabled_services


class TestWorkflowManagement:
    """Test workflow management with checkpoints"""
    
    @pytest.mark.asyncio
    async def test_workflow_orchestration_basic(self, mock_service_manager):
        """Test basic workflow orchestration"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {
                'IdentityService': {'base_url': 'http://localhost:8002'},
                'AnalyticsService': {'base_url': 'http://localhost:8001'},
                'TheoryExtractionService': {'base_url': 'http://localhost:8003'},
                'QualityService': {'base_url': 'http://localhost:8004'}
            }
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Create test workflow spec
            workflow_spec = WorkflowSpec(
                documents=[
                    {'id': 'doc1', 'content': 'Test document 1'},
                    {'id': 'doc2', 'content': 'Test document 2'}
                ],
                analysis_modes=['graph', 'table'],
                theory_integration=True,
                quality_validation=True,
                checkpoint_interval=1
            )
            
            # Mock service clients
            with patch('src.core.pipeline_orchestrator.AnalyticsServiceClient') as mock_analytics, \
                 patch('src.core.pipeline_orchestrator.IdentityServiceClient') as mock_identity, \
                 patch('src.core.pipeline_orchestrator.TheoryExtractionServiceClient') as mock_theory, \
                 patch('src.core.pipeline_orchestrator.QualityServiceClient') as mock_quality:
                
                # Setup mock responses
                mock_identity_client = Mock()
                mock_identity_client.__aenter__ = Mock(return_value=mock_identity_client)
                mock_identity_client.__aexit__ = Mock(return_value=None)
                mock_identity_client.resolve_entities = Mock(return_value=Mock(
                    success=True, 
                    data={'entities': []}, 
                    duration_ms=100
                ))
                mock_identity.return_value = mock_identity_client
                
                mock_analytics_client = Mock()
                mock_analytics_client.__aenter__ = Mock(return_value=mock_analytics_client)
                mock_analytics_client.__aexit__ = Mock(return_value=None)
                mock_analytics_client.analyze_document = Mock(return_value=Mock(
                    success=True, 
                    data={'analysis': []}, 
                    duration_ms=150
                ))
                mock_analytics.return_value = mock_analytics_client
                
                mock_theory_client = Mock()
                mock_theory_client.__aenter__ = Mock(return_value=mock_theory_client)  
                mock_theory_client.__aexit__ = Mock(return_value=None)
                mock_theory_client.extract_theories = Mock(return_value=Mock(
                    success=True, 
                    data={'theories': []}, 
                    duration_ms=200
                ))
                mock_theory.return_value = mock_theory_client
                
                mock_quality_client = Mock()
                mock_quality_client.__aenter__ = Mock(return_value=mock_quality_client)
                mock_quality_client.__aexit__ = Mock(return_value=None) 
                mock_quality_client.assess_quality = Mock(return_value=Mock(
                    success=True, 
                    data={'quality_score': 0.95}, 
                    duration_ms=80
                ))
                mock_quality.return_value = mock_quality_client
                
                # Execute workflow
                result = await orchestrator.orchestrate_research_workflow(workflow_spec)
                
                # Verify result structure
                assert hasattr(result, 'workflow_id')
                assert hasattr(result, 'status')
                assert hasattr(result, 'analysis_results')
                assert hasattr(result, 'overall_quality_score')
                assert hasattr(result, 'duration')
                assert hasattr(result, 'services_used')
                
                # Verify analysis results
                assert len(result.analysis_results) == 2  # Two documents
                for doc_result in result.analysis_results:
                    assert isinstance(doc_result, DocumentResult)
                    assert doc_result.analysis_modes == ['graph', 'table']
                    assert doc_result.theory_extracted is True
                    assert doc_result.quality_score > 0
    
    @pytest.mark.asyncio 
    async def test_workflow_pause_and_resume(self, mock_service_manager):
        """Test workflow pause and resume functionality"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            workflow_spec = WorkflowSpec(
                documents=[{'id': 'doc1', 'content': 'Test'}],
                analysis_modes=['graph'],
                theory_integration=False,
                quality_validation=False,
                checkpoint_interval=1
            )
            
            # Start workflow
            workflow_id = await orchestrator.start_workflow(workflow_spec)
            assert isinstance(workflow_id, str)
            
            # Verify workflow is active
            active_workflows = await orchestrator.get_active_workflows()
            assert workflow_id in active_workflows
            
            # Pause workflow
            paused = await orchestrator.pause_workflow(workflow_id)
            assert paused is True
            
            # Get workflow status
            status = await orchestrator.get_workflow_status(workflow_id)
            assert status['workflow_id'] == workflow_id
            assert status['status'] == 'paused'
            
            # Resume workflow  
            with patch('src.core.pipeline_orchestrator.AnalyticsServiceClient'), \
                 patch('src.core.pipeline_orchestrator.IdentityServiceClient'), \
                 patch('src.core.pipeline_orchestrator.TheoryExtractionServiceClient'), \
                 patch('src.core.pipeline_orchestrator.QualityServiceClient'):
                
                result = await orchestrator.resume_workflow(workflow_id)
                
                # Verify result indicates resumption
                assert hasattr(result, 'resumed_from_checkpoint')
                assert result.resumed_from_checkpoint is True
                assert hasattr(result, 'checkpoint_id')
                assert result.checkpoint_id is not None
    
    @pytest.mark.asyncio
    async def test_workflow_cancellation(self, mock_service_manager):
        """Test workflow cancellation"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            workflow_spec = WorkflowSpec(
                documents=[{'id': 'doc1', 'content': 'Test'}],
                analysis_modes=['graph'],
                theory_integration=False,
                quality_validation=False,
                checkpoint_interval=1
            )
            
            # Start workflow
            workflow_id = await orchestrator.start_workflow(workflow_spec)
            
            # Cancel workflow
            await orchestrator.cancel_workflow(workflow_id)
            
            # Verify workflow was cancelled
            status = await orchestrator.get_workflow_status(workflow_id) 
            assert status['status'] == 'cancelled'
            assert status['cleanup_completed'] is True
            
            # Verify cancellation events were recorded
            events = await orchestrator.get_service_events('workflow_cancelled')
            assert len(events) > 0
            cancel_event = events[0]
            assert cancel_event['workflow_id'] == workflow_id
            assert 'services_notified' in cancel_event


class TestQueryExecution:
    """Test query execution interface"""
    
    def test_execute_query_with_neo4j_driver(self, mock_service_manager):
        """Test query execution when Neo4j driver is available"""
        # Mock Neo4j driver and session
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([Mock(), Mock()]))  # 2 records
        mock_session.run.return_value = mock_result
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session
        
        mock_service_manager.get_neo4j_driver.return_value = mock_driver
        
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Execute query
            result = orchestrator.execute_query("MATCH (n) RETURN n")
            
            # Verify result
            assert isinstance(result, QueryResult)
            assert result.count == 2
            assert len(result.records) == 2
            
            # Verify driver was called
            mock_driver.session.assert_called_once()
            mock_session.run.assert_called_once_with("MATCH (n) RETURN n")
    
    def test_execute_query_no_driver(self, mock_service_manager):
        """Test query execution when Neo4j driver is not available"""
        mock_service_manager.get_neo4j_driver.return_value = None
        
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Execute query should fail
            with pytest.raises(Exception, match="Neo4j driver not available"):
                orchestrator.execute_query("MATCH (n) RETURN n")
    
    def test_execute_count_query(self, mock_service_manager):
        """Test execution of count queries"""
        # Mock driver with count result
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.__getitem__ = Mock(return_value=5)  # Count result
        mock_result.__iter__ = Mock(return_value=iter([mock_record]))
        mock_session.run.return_value = mock_result
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        mock_driver.session.return_value = mock_session
        
        mock_service_manager.get_neo4j_driver.return_value = mock_driver
        
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Execute count query
            result = orchestrator.execute_query("MATCH (n) RETURN COUNT(n)")
            
            # Verify count result
            assert isinstance(result, QueryResult)
            assert result.count == 5
            assert len(result.records) == 1


class TestConfigurationAndValidation:
    """Test configuration and validation integration"""
    
    def test_configuration_loading(self, mock_service_manager):
        """Test configuration is properly loaded"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {'service1': {}}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://test:7687',
                'user': 'testuser',
                'password': 'testpass'
            }
            mock_config.get_system_config.return_value = {
                'checkpoint_storage': 'postgres',
                'strict_schema_validation': True
            }
            mock_config.get_database_config.return_value = {
                'checkpoint_db': 'postgresql://test'
            }
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Verify configuration was loaded
            assert orchestrator.neo4j_uri == 'bolt://test:7687'
            assert orchestrator.neo4j_user == 'testuser'
            assert orchestrator.neo4j_password == 'testpass'
            
            # Verify pipeline validator was configured
            assert orchestrator.pipeline_validator is not None
    
    def test_contract_validation_initialization(self, mock_service_manager):
        """Test contract validation is properly initialized"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            with patch('src.core.pipeline_orchestrator.ContractValidator') as mock_cv, \
                 patch('src.core.pipeline_orchestrator.OntologyValidator') as mock_ov:
                
                mock_cv.return_value = Mock()
                mock_ov.return_value = Mock()
                
                config = PipelineConfig(tools=[])
                orchestrator = PipelineOrchestrator(config)
                
                # Verify validators were initialized
                assert orchestrator.contract_validator is not None
                assert orchestrator.ontology_validator is not None
                assert orchestrator.validation_enabled is True
                
                # Verify constructors were called with correct arguments
                mock_cv.assert_called_once_with("contracts")
                mock_ov.assert_called_once()
    
    def test_validation_failure_during_init(self, mock_service_manager):
        """Test orchestrator fails fast if validation cannot be initialized"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            with patch('src.core.pipeline_orchestrator.ContractValidator') as mock_cv:
                mock_cv.side_effect = Exception("Contract validation init failed")
                
                config = PipelineConfig(tools=[])
                
                # Should fail fast
                with pytest.raises(RuntimeError, match="Failed to initialize contract validator"):
                    PipelineOrchestrator(config)


class TestPerformanceAndMetrics:
    """Test performance tracking and metrics"""
    
    @pytest.mark.asyncio
    async def test_workflow_metrics_collection(self, mock_service_manager):
        """Test workflow execution metrics are collected"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Get workflow metrics
            metrics = await orchestrator.get_workflow_metrics('test_workflow_id')
            
            # Verify metrics structure
            assert isinstance(metrics, dict)
            assert 'execution_time_ms' in metrics
            assert 'documents_processed' in metrics
            assert 'service_calls' in metrics
            assert 'resource_usage' in metrics
            assert 'quality_metrics' in metrics
            
            # Verify metric values are reasonable
            assert metrics['execution_time_ms'] > 0
            assert metrics['documents_processed'] >= 0
            assert isinstance(metrics['service_calls'], dict)
            assert isinstance(metrics['resource_usage'], dict)
            assert isinstance(metrics['quality_metrics'], dict)
    
    @pytest.mark.asyncio
    async def test_telemetry_events_collection(self, mock_service_manager):
        """Test telemetry events are collected"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Get telemetry events
            events = await orchestrator.get_telemetry_events('test_workflow_id')
            
            # Verify events structure
            assert isinstance(events, list)
            assert len(events) > 0
            
            for event in events:
                assert isinstance(event, dict)
                assert 'type' in event
                assert 'timestamp' in event
    
    def test_execution_tracking_enablement(self, mock_service_manager):
        """Test execution tracking can be enabled and used"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Enable execution tracking
            orchestrator.enable_execution_tracking()
            
            # Verify tracking is enabled
            assert hasattr(orchestrator, '_execution_tracking')
            assert orchestrator._execution_tracking is True
            assert hasattr(orchestrator, '_execution_timeline')
            assert isinstance(orchestrator._execution_timeline, list)
            
            # Get execution timeline
            timeline = orchestrator.get_execution_timeline()
            assert isinstance(timeline, list)
    
    def test_error_recovery_configuration(self, mock_service_manager):
        """Test error recovery can be configured"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Enable error recovery
            orchestrator.enable_error_recovery(max_retries=5, backoff_factor=1.5)
            
            # Verify error recovery is configured
            assert hasattr(orchestrator, '_error_recovery_enabled')
            assert orchestrator._error_recovery_enabled is True
            assert hasattr(orchestrator, '_max_retries')
            assert orchestrator._max_retries == 5
            assert hasattr(orchestrator, '_backoff_factor')
            assert orchestrator._backoff_factor == 1.5


class TestServiceDependencies:
    """Test service dependency management"""
    
    @pytest.mark.asyncio
    async def test_service_dependencies_retrieval(self, mock_service_manager):
        """Test service dependencies can be retrieved"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Get service dependencies
            dependencies = await orchestrator.get_service_dependencies()
            
            # Verify dependencies structure
            assert isinstance(dependencies, dict)
            expected_services = [
                'AnalyticsService', 'TheoryExtractionService', 
                'QualityService', 'ProvenanceService', 'IdentityService'
            ]
            
            for service in expected_services:
                assert service in dependencies
                assert 'depends_on' in dependencies[service]
                assert isinstance(dependencies[service]['depends_on'], list)
    
    @pytest.mark.asyncio
    async def test_service_dependency_validation(self, mock_service_manager):
        """Test service dependency validation"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Validate dependencies
            is_valid = await orchestrator.validate_service_dependencies()
            
            # Should be valid for default dependencies
            assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, mock_service_manager):
        """Test circular dependency detection"""
        with patch('src.core.pipeline_orchestrator.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.get_services_config.return_value = {}
            mock_config.get_neo4j_config.return_value = {
                'uri': 'bolt://localhost:7687',
                'user': 'neo4j',
                'password': 'password'
            }
            mock_config.get_system_config.return_value = {'checkpoint_storage': 'file'}
            mock_get_config.return_value = mock_config
            
            config = PipelineConfig(tools=[])
            orchestrator = PipelineOrchestrator(config)
            
            # Try to add circular dependency
            with pytest.raises(ValueError, match="Circular dependency detected"):
                await orchestrator.add_service_dependency('ServiceA', 'ServiceB')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])