"""
Integration Test Framework

Provides comprehensive integration testing with real/mock service combinations,
workflow testing, and end-to-end validation capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import time
import traceback

from .base_test import AsyncBaseTest, TDDTestBase
from .mock_factory import MockServiceFactory, MockBehavior, MockServiceConfig
from .fixtures import ServiceFixtures, FixtureDocument, FixtureEntity
from ..core.dependency_injection import ServiceContainer, ServiceLifecycle
from ..core.interfaces.service_interfaces import ServiceInterface, ServiceResponse

logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Integration testing modes"""
    ALL_REAL = "all_real"          # All services are real implementations
    ALL_MOCK = "all_mock"          # All services are mocked
    MIXED = "mixed"                # Mix of real and mock services
    HYBRID = "hybrid"              # Real core services, mock external services


@dataclass
class IntegrationTestResult:
    """Result of an integration test"""
    test_name: str
    success: bool
    execution_time_ms: float
    services_used: List[str]
    operations_performed: int
    error_message: Optional[str] = None
    detailed_results: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.detailed_results is None:
            self.detailed_results = {}


@dataclass
class ServiceConfiguration:
    """Configuration for a service in integration tests"""
    name: str
    use_real: bool = True
    mock_config: Optional[MockServiceConfig] = None
    initialization_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.initialization_params is None:
            self.initialization_params = {}


class IntegrationTestBase(AsyncBaseTest):
    """
    Base class for integration tests with flexible service configurations
    """
    
    def setUp(self):
        """Initialize integration test environment"""
        super().setUp()
        
        self.integration_mode = IntegrationMode.MIXED
        self.service_configs: Dict[str, ServiceConfiguration] = {}
        self.test_results: List[IntegrationTestResult] = []
        self.fixtures = ServiceFixtures()
        
        # Performance tracking
        self.start_time = None
        self.operation_count = 0
        
        logger.debug("Integration test environment initialized")
    
    def configure_service(self, name: str, use_real: bool = True,
                         mock_config: Optional[MockServiceConfig] = None,
                         **init_params: Any) -> None:
        """Configure how a service should be set up for testing"""
        self.service_configs[name] = ServiceConfiguration(
            name=name,
            use_real=use_real,
            mock_config=mock_config or MockServiceConfig(),
            initialization_params=init_params
        )
        
        logger.debug(f"Configured service '{name}': real={use_real}")
    
    def set_integration_mode(self, mode: IntegrationMode) -> None:
        """Set the integration testing mode"""
        self.integration_mode = mode
        logger.info(f"Integration mode set to: {mode.value}")
    
    async def setup_services(self, service_specs: Dict[str, Any]) -> None:
        """Set up services according to configurations"""
        mock_factory = MockServiceFactory()
        
        for service_name, spec in service_specs.items():
            config = self.service_configs.get(service_name, 
                                            ServiceConfiguration(service_name))
            
            if self._should_use_real_service(service_name, config):
                # Register real service
                service_class = spec.get('class')
                if service_class:
                    self.container.register(
                        service_name,
                        service_class,
                        lifecycle=ServiceLifecycle.SINGLETON,
                        dependencies=spec.get('dependencies', []),
                        config_section=spec.get('config_section'),
                        **(config.initialization_params or {})
                    )
                    logger.debug(f"Registered real service: {service_name}")
            else:
                # Register mock service
                interface_class = spec.get('interface')
                if interface_class:
                    mock_service = mock_factory.create_mock_service(
                        interface_class,
                        config.mock_config
                    )
                    self.container.register(
                        service_name,
                        mock_service,
                        lifecycle=ServiceLifecycle.SINGLETON
                    )
                    logger.debug(f"Registered mock service: {service_name}")
        
        # Start all services
        await self.container.startup_async()
        logger.info("All integration test services started")
    
    def _should_use_real_service(self, service_name: str, 
                               config: ServiceConfiguration) -> bool:
        """Determine if service should be real based on mode and config"""
        if self.integration_mode == IntegrationMode.ALL_REAL:
            return True
        elif self.integration_mode == IntegrationMode.ALL_MOCK:
            return False
        elif self.integration_mode == IntegrationMode.MIXED:
            return config.use_real
        elif self.integration_mode == IntegrationMode.HYBRID:
            # Real for core services, mock for external
            core_services = ['identity_service', 'provenance_service', 'quality_service']
            return service_name in core_services
        
        return config.use_real
    
    async def run_integration_test(self, test_name: str, 
                                 test_func: Callable[..., Any],
                                 *args: Any, **kwargs: Any) -> IntegrationTestResult:
        """Run an integration test with full monitoring"""
        logger.info(f"Starting integration test: {test_name}")
        
        self.start_time = time.time()
        self.operation_count = 0
        
        try:
            # Execute test
            result = await test_func(*args, **kwargs)
            
            execution_time = (time.time() - self.start_time) * 1000
            
            test_result = IntegrationTestResult(
                test_name=test_name,
                success=True,
                execution_time_ms=execution_time,
                services_used=list(self.container._instances.keys()),
                operations_performed=self.operation_count,
                detailed_results=result if isinstance(result, dict) else {"result": result}
            )
            
            logger.info(f"Integration test '{test_name}' completed successfully "
                       f"in {execution_time:.2f}ms")
            
        except Exception as e:
            execution_time = (time.time() - self.start_time) * 1000
            
            test_result = IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                services_used=list(self.container._instances.keys()),
                operations_performed=self.operation_count,
                error_message=str(e),
                detailed_results={"traceback": traceback.format_exc()}
            )
            
            logger.error(f"Integration test '{test_name}' failed: {e}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def _test_service_workflow(self, workflow_name: str,
                                   steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a complete service workflow"""
        logger.info(f"Testing workflow: {workflow_name}")
        
        results: Dict[str, Any] = {"workflow": workflow_name, "steps": []}
        
        for i, step in enumerate(steps):
            step_name = step.get('name', f'step_{i+1}')
            service_name = step['service']
            method_name = step['method']
            params = step.get('params', {})
            
            logger.debug(f"Executing workflow step: {step_name}")
            
            try:
                # Get service and execute method
                service = await self.async_get_service(service_name)
                method = getattr(service, method_name)
                
                step_result = await method(**params)
                self.operation_count += 1
                
                # Validate response if it's a ServiceResponse
                if isinstance(step_result, ServiceResponse):
                    self.assert_service_response(step_result)
                
                step_results = results.setdefault('steps', [])
                step_results.append({
                    'step': step_name,
                    'success': True,
                    'result': step_result.__dict__ if hasattr(step_result, '__dict__') else step_result
                })
                
                logger.debug(f"Workflow step '{step_name}' completed successfully")
                
            except Exception as e:
                step_results = results.setdefault('steps', [])
                step_results.append({
                    'step': step_name,
                    'success': False,
                    'error': str(e)
                })
                logger.error(f"Workflow step '{step_name}' failed: {e}")
                raise
        
        logger.info(f"Workflow '{workflow_name}' completed with {len(steps)} steps")
        return results
    
    async def _test_service_integration(self, primary_service: str, 
                                      secondary_services: List[str],
                                      integration_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test integration between multiple services"""
        logger.info(f"Testing integration: {primary_service} with {secondary_services}")
        
        primary = await self.async_get_service(primary_service)
        secondaries = {name: await self.async_get_service(name) 
                      for name in secondary_services}
        
        scenario_name = integration_scenario.get('name', 'unnamed_scenario')
        operations = integration_scenario.get('operations', [])
        
        results = {
            'scenario': scenario_name,
            'primary_service': primary_service,
            'secondary_services': secondary_services,
            'operations': []
        }
        
        for operation in operations:
            op_name = operation.get('name', 'unnamed_operation')
            service_calls = operation.get('calls', [])
            
            logger.debug(f"Executing integration operation: {op_name}")
            
            operation_result = {'operation': op_name, 'calls': []}
            
            for call in service_calls:
                service_name = call['service']
                method_name = call['method']
                params = call.get('params', {})
                
                if service_name == primary_service:
                    service = primary
                else:
                    service = secondaries[service_name]
                
                method = getattr(service, method_name)
                call_result = await method(**params)
                self.operation_count += 1
                
                operation_result['calls'].append({
                    'service': service_name,
                    'method': method_name,
                    'success': isinstance(call_result, ServiceResponse) and call_result.success,
                    'result': call_result.__dict__ if hasattr(call_result, '__dict__') else call_result
                })
            
            results['operations'].append(operation_result)
        
        logger.info(f"Service integration test completed: {scenario_name}")
        return results
    
    async def _test_end_to_end_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test complete end-to-end workflow across all services"""
        workflow_name = workflow_config.get('name', 'e2e_workflow')
        logger.info(f"Starting end-to-end workflow test: {workflow_name}")
        
        # Create test data
        test_data = self.fixtures.create_integration_test_scenario(
            workflow_config.get('scenario', 'basic')
        )
        
        # Execute workflow phases
        phases = workflow_config.get('phases', [])
        results = {
            'workflow': workflow_name,
            'test_data': {
                'documents': len(test_data.get('documents', [])),
                'entities': len(test_data.get('entities', [])),
                'mentions': len(test_data.get('mentions', []))
            },
            'phases': []
        }
        
        for phase in phases:
            phase_name = phase['name']
            logger.debug(f"Executing workflow phase: {phase_name}")
            
            phase_result = await self._test_service_workflow(
                phase_name, phase['steps']
            )
            
            results['phases'].append(phase_result)
        
        logger.info(f"End-to-end workflow '{workflow_name}' completed")
        return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all integration tests"""
        successful_tests = [r for r in self.test_results if r.success]
        failed_tests = [r for r in self.test_results if not r.success]
        
        return {
            'total_tests': len(self.test_results),
            'successful': len(successful_tests),
            'failed': len(failed_tests),
            'success_rate': len(successful_tests) / len(self.test_results) if self.test_results else 0,
            'total_execution_time_ms': sum(r.execution_time_ms for r in self.test_results),
            'average_execution_time_ms': (
                sum(r.execution_time_ms for r in self.test_results) / len(self.test_results)
                if self.test_results else 0
            ),
            'total_operations': sum(r.operations_performed for r in self.test_results),
            'services_tested': list(set().union(*[r.services_used for r in self.test_results])),
            'integration_mode': self.integration_mode.value,
            'failed_tests': [{'name': r.test_name, 'error': r.error_message} for r in failed_tests]
        }


class WorkflowIntegrationTest(IntegrationTestBase):
    """Specialized integration test for workflow testing"""
    
    async def test_document_processing_workflow(self) -> Dict[str, Any]:
        """Test complete document processing workflow"""
        # Create test document
        document = self.fixtures.create_test_document(
            "Dr. Alice Johnson from MIT published research on quantum computing."
        )
        
        workflow_steps = [
            {
                'name': 'extract_entities',
                'service': 'identity_service',
                'method': 'create_mention',
                'params': {
                    'surface_form': 'Dr. Alice Johnson',
                    'context': document.content,
                    'confidence': 0.9
                }
            },
            {
                'name': 'resolve_entity',
                'service': 'identity_service', 
                'method': 'resolve_entity',
                'params': {'mention_id': 'mock_mention_123'}
            },
            {
                'name': 'record_provenance',
                'service': 'provenance_service',
                'method': 'record_operation',
                'params': {
                    'operation_type': 'entity_extraction',
                    'source_document': document.document_id
                }
            },
            {
                'name': 'assess_quality',
                'service': 'quality_service',
                'method': 'assess_quality',
                'params': {
                    'data_type': 'entity_mention',
                    'data_id': 'mock_mention_123'
                }
            }
        ]
        
        return await self._test_service_workflow(
            'document_processing_workflow',
            workflow_steps
        )
    
    async def test_graph_building_workflow(self) -> Dict[str, Any]:
        """Test graph building workflow across services"""
        # Create connected test data
        test_graph = self.fixtures.create_connected_graph(5, 7)
        
        integration_scenario = {
            'name': 'graph_building',
            'operations': [
                {
                    'name': 'create_entities',
                    'calls': [
                        {
                            'service': 'identity_service',
                            'method': 'create_mention',
                            'params': {'surface_form': 'Test Entity 1'}
                        },
                        {
                            'service': 'identity_service', 
                            'method': 'create_mention',
                            'params': {'surface_form': 'Test Entity 2'}
                        }
                    ]
                },
                {
                    'name': 'link_entities',
                    'calls': [
                        {
                            'service': 'identity_service',
                            'method': 'link_entities',
                            'params': {
                                'entity1_id': 'mock_entity_1',
                                'entity2_id': 'mock_entity_2',
                                'relationship_type': 'RELATED_TO'
                            }
                        }
                    ]
                },
                {
                    'name': 'record_and_assess',
                    'calls': [
                        {
                            'service': 'provenance_service',
                            'method': 'record_operation',
                            'params': {'operation_type': 'link_entities'}
                        },
                        {
                            'service': 'quality_service',
                            'method': 'assess_quality',
                            'params': {'data_type': 'relationship'}
                        }
                    ]
                }
            ]
        }
        
        return await self._test_service_integration(
            'identity_service',
            ['provenance_service', 'quality_service'],
            integration_scenario
        )