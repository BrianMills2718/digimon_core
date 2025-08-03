"""
Mock Service Factory for Testing

Provides intelligent mock creation for all service interfaces with realistic
behavior simulation and dependency injection integration.
"""

import logging
from typing import Dict, Any, Optional, Type, Callable, List
from unittest.mock import Mock, MagicMock, AsyncMock
import asyncio
import inspect
from dataclasses import dataclass, field
from enum import Enum

from ..core.interfaces.service_interfaces import (
    ServiceInterface, ServiceResponse, 
    IdentityServiceInterface,
    ProvenanceServiceInterface,
    QualityServiceInterface,
    Neo4jServiceInterface
)
from ..core.dependency_injection import ServiceContainer, ServiceLifecycle
from .config import get_testing_config

logger = logging.getLogger(__name__)


class MockBehavior(Enum):
    """Mock behavior patterns for different testing scenarios"""
    SUCCESS = "success"              # Always return successful responses
    FAILURE = "failure"              # Always return failure responses  
    REALISTIC = "realistic"          # Mix of success/failure with delays
    SLOW = "slow"                   # Simulate slow responses
    INTERMITTENT = "intermittent"   # Simulate intermittent failures
    CUSTOM = "custom"               # Custom behavior defined by user


@dataclass
class MockServiceConfig:
    """Configuration for mock service behavior"""
    behavior: MockBehavior = MockBehavior.SUCCESS
    success_rate: float = field(default_factory=lambda: get_testing_config().mock.success_rate)
    average_delay_ms: float = field(default_factory=lambda: get_testing_config().mock.default_delay_ms)
    failure_modes: Optional[List[str]] = None
    custom_responses: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.failure_modes is None:
            self.failure_modes = get_testing_config().mock.failure_modes
        if self.custom_responses is None:
            self.custom_responses = {}


class MockServiceFactory:
    """Factory for creating intelligent mock services with realistic behavior"""
    
    def __init__(self) -> None:
        self.mock_configs: Dict[str, MockServiceConfig] = {}
        self.created_mocks: Dict[str, Mock] = {}
        
        # Default mock responses for common operations
        self.default_responses = {
            'health_check': ServiceResponse(
                success=True,
                data={"status": "healthy", "service": "mock"},
                metadata={"mock": True}
            ),
            'create_mention': ServiceResponse(
                success=True,
                data={"mention_id": "mock_mention_123", "created": True},
                metadata={"mock": True}
            ),
            'resolve_entity': ServiceResponse(
                success=True,
                data={"entity_id": "mock_entity_456", "resolved": True},
                metadata={"mock": True}
            )
        }
    
    def create_mock_service(self, interface_class: Type[ServiceInterface],
                          config: Optional[MockServiceConfig] = None,
                          **method_overrides: Any) -> Mock:
        """Create a mock service implementing the given interface"""
        
        config = config or MockServiceConfig()
        service_name = interface_class.__name__
        
        # Store config for this service type
        self.mock_configs[service_name] = config
        
        # Create mock based on interface type
        if interface_class == IdentityServiceInterface:
            mock_service = self._create_identity_mock(config, **method_overrides)
        elif interface_class == ProvenanceServiceInterface:
            mock_service = self._create_provenance_mock(config, **method_overrides)
        elif interface_class == QualityServiceInterface:
            mock_service = self._create_quality_mock(config, **method_overrides)
        elif interface_class == Neo4jServiceInterface:
            mock_service = self._create_neo4j_mock(config, **method_overrides)
        else:
            mock_service = self._create_generic_mock(interface_class, config, **method_overrides)
        
        # Add lifecycle methods
        mock_service.startup = AsyncMock(return_value=None)
        mock_service.shutdown = AsyncMock(return_value=None)
        
        # Mark as mock for DI container detection
        mock_service._mock_name = f"mock_{service_name}"
        
        self.created_mocks[service_name] = mock_service
        logger.debug(f"Created mock service for {service_name} with behavior {config.behavior}")
        
        return mock_service
    
    def _create_identity_mock(self, config: MockServiceConfig, **overrides: Any) -> Mock:
        """Create mock for IdentityServiceInterface"""
        mock = AsyncMock(spec=IdentityServiceInterface)
        
        # Health check
        mock.health_check = AsyncMock(
            return_value=self._get_response('health_check', config, overrides)
        )
        
        # Create mention
        mock.create_mention = AsyncMock(
            side_effect=self._create_side_effect(
                'create_mention', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "mention_id": "mock_mention_123",
                        "surface_form": "Mock Entity",
                        "confidence": 0.9,
                        "created_at": "2025-07-26T12:00:00Z"
                    },
                    metadata={"mock": True, "service": "identity"}
                )
            )
        )
        
        # Resolve entity
        mock.resolve_entity = AsyncMock(
            side_effect=self._create_side_effect(
                'resolve_entity', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "entity_id": "mock_entity_456",
                        "canonical_name": "Mock Entity", 
                        "entity_type": "PERSON",
                        "confidence": 0.85
                    },
                    metadata={"mock": True, "service": "identity"}
                )
            )
        )
        
        # Get entity by ID
        mock.get_entity_by_id = AsyncMock(
            side_effect=self._create_side_effect(
                'get_entity_by_id', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "entity_id": "mock_entity_456",
                        "canonical_name": "Mock Entity",
                        "mentions": ["mock_mention_123"]
                    },
                    metadata={"mock": True, "service": "identity"}
                )
            )
        )
        
        # Search entities
        mock.search_entities = AsyncMock(
            side_effect=self._create_side_effect(
                'search_entities', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data=[
                        {"entity_id": "mock_entity_1", "name": "Entity One", "score": 0.9},
                        {"entity_id": "mock_entity_2", "name": "Entity Two", "score": 0.8}
                    ],
                    metadata={"mock": True, "service": "identity", "query": "mock"}
                )
            )
        )
        
        # Link entities
        mock.link_entities = AsyncMock(
            side_effect=self._create_side_effect(
                'link_entities', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "relationship_id": "mock_rel_789",
                        "source_id": "entity_1",
                        "target_id": "entity_2",
                        "relationship_type": "RELATED_TO"
                    },
                    metadata={"mock": True, "service": "identity"}
                )
            )
        )
        
        return mock
    
    def _create_provenance_mock(self, config: MockServiceConfig, **overrides: Any) -> Mock:
        """Create mock for ProvenanceServiceInterface"""
        mock = AsyncMock(spec=ProvenanceServiceInterface)
        
        mock.health_check = AsyncMock(
            return_value=self._get_response('health_check', config, overrides)
        )
        
        mock.record_operation = AsyncMock(
            side_effect=self._create_side_effect(
                'record_operation', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "operation_id": "mock_op_123",
                        "timestamp": "2025-07-26T12:00:00Z",
                        "recorded": True
                    },
                    metadata={"mock": True, "service": "provenance"}
                )
            )
        )
        
        mock.get_operation_history = AsyncMock(
            side_effect=self._create_side_effect(
                'get_operation_history', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data=[
                        {"operation_id": "op_1", "type": "create_mention", "timestamp": "2025-07-26T11:00:00Z"},
                        {"operation_id": "op_2", "type": "resolve_entity", "timestamp": "2025-07-26T11:30:00Z"}
                    ],
                    metadata={"mock": True, "service": "provenance"}
                )
            )
        )
        
        return mock
    
    def _create_quality_mock(self, config: MockServiceConfig, **overrides: Any) -> Mock:
        """Create mock for QualityServiceInterface"""
        mock = AsyncMock(spec=QualityServiceInterface)
        
        mock.health_check = AsyncMock(
            return_value=self._get_response('health_check', config, overrides)
        )
        
        mock.assess_quality = AsyncMock(
            side_effect=self._create_side_effect(
                'assess_quality', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "quality_score": 0.85,
                        "dimensions": {
                            "accuracy": 0.9,
                            "completeness": 0.8,
                            "consistency": 0.85
                        },
                        "assessment_id": "mock_assess_123"
                    },
                    metadata={"mock": True, "service": "quality"}
                )
            )
        )
        
        mock.validate_data = AsyncMock(
            side_effect=self._create_side_effect(
                'validate_data', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "valid": True,
                        "validation_errors": [],
                        "validation_id": "mock_valid_456"
                    },
                    metadata={"mock": True, "service": "quality"}
                )
            )
        )
        
        return mock
    
    def _create_neo4j_mock(self, config: MockServiceConfig, **overrides: Any) -> Mock:
        """Create mock for Neo4jServiceInterface"""
        mock = AsyncMock(spec=Neo4jServiceInterface)
        
        mock.health_check = AsyncMock(
            return_value=self._get_response('health_check', config, overrides)
        )
        
        mock.execute_query = AsyncMock(
            side_effect=self._create_side_effect(
                'execute_query', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "results": [
                            {"node": {"id": "123", "name": "Mock Node"}},
                            {"node": {"id": "456", "name": "Another Node"}}
                        ],
                        "summary": {"nodes_created": 0, "relationships_created": 0}
                    },
                    metadata={"mock": True, "service": "neo4j", "query": "MATCH (n) RETURN n"}
                )
            )
        )
        
        mock.create_node = AsyncMock(
            side_effect=self._create_side_effect(
                'create_node', config, overrides,
                default_response=ServiceResponse(
                    success=True,
                    data={
                        "node_id": "mock_node_789",
                        "labels": ["Entity"],
                        "properties": {"name": "Mock Entity"}
                    },
                    metadata={"mock": True, "service": "neo4j"}
                )
            )
        )
        
        return mock
    
    def _create_generic_mock(self, interface_class: Type[ServiceInterface], config: MockServiceConfig, **overrides: Any) -> Mock:
        """Create a generic mock for any service interface"""
        mock = AsyncMock(spec=interface_class)
        
        # Add common methods
        mock.health_check = AsyncMock(
            return_value=self._get_response('health_check', config, overrides)
        )
        
        # Inspect interface for other methods and add default mocks
        for method_name in dir(interface_class):
            if not method_name.startswith('_') and callable(getattr(interface_class, method_name, None)):
                if not hasattr(mock, method_name):
                    setattr(mock, method_name, AsyncMock(
                        return_value=ServiceResponse(
                            success=True,
                            data={"result": f"mock_{method_name}_result"},
                            metadata={"mock": True, "method": method_name}
                        )
                    ))
        
        return mock
    
    def _create_side_effect(self, method_name: str, config: MockServiceConfig, 
                          overrides: Dict[str, Any], default_response: ServiceResponse) -> Callable:
        """Create a side effect function for mock methods"""
        
        # Check for method override
        if method_name in overrides:
            override = overrides[method_name]
            if callable(override):
                return override
            else:
                # Direct return value
                async def override_side_effect(*args, **kwargs):
                    return override
                return override_side_effect
        
        # Use configured behavior
        async def side_effect(*args, **kwargs):
            # Simulate delay if configured
            if config.average_delay_ms > 0:
                await asyncio.sleep(config.average_delay_ms / 1000.0)
            
            # Determine response based on behavior
            if config.behavior == MockBehavior.SUCCESS:
                return default_response
            elif config.behavior == MockBehavior.FAILURE:
                return ServiceResponse(
                    success=False,
                    data=None,
                    error=f"Mock {method_name} failure",
                    metadata={"mock": True, "failure_mode": "configured"}
                )
            elif config.behavior == MockBehavior.REALISTIC:
                import random
                if random.random() < config.success_rate:
                    return default_response
                else:
                    failure_mode = random.choice(config.failure_modes if config.failure_modes else ["generic_error"])
                    return ServiceResponse(
                        success=False,
                        data=None,
                        error=f"Mock {method_name} failed: {failure_mode}",
                        metadata={"mock": True, "failure_mode": failure_mode}
                    )
            else:
                return default_response
        
        return side_effect
    
    def _get_response(self, method_name: str, config: MockServiceConfig, 
                     overrides: Dict[str, Any]) -> ServiceResponse:
        """Get response for simple (non-side-effect) methods"""
        if method_name in overrides:
            return overrides[method_name]
        
        if method_name in self.default_responses:
            return self.default_responses[method_name]
        
        return ServiceResponse(
            success=True,
            data={"result": f"mock_{method_name}_result"},
            metadata={"mock": True}
        )
    
    def configure_service_behavior(self, service_name: str, config: MockServiceConfig) -> None:
        """Configure behavior for a specific service type"""
        self.mock_configs[service_name] = config
        logger.debug(f"Configured behavior for {service_name}: {config.behavior}")
    
    def get_mock_statistics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about mock service usage"""
        if service_name and service_name in self.created_mocks:
            mock = self.created_mocks[service_name]
            return {
                "service": service_name,
                "call_count": len(mock.method_calls),
                "methods_called": list(set(call[0] for call in mock.method_calls))
            }
        
        return {
            "total_mocks_created": len(self.created_mocks),
            "service_types": list(self.created_mocks.keys()),
            "total_configurations": len(self.mock_configs)
        }
    
    def reset_all_mocks(self) -> None:
        """Reset all created mocks"""
        for mock in self.created_mocks.values():
            mock.reset_mock()
        logger.debug("All mocks reset")
    
    def register_mocks_with_container(self, container: ServiceContainer, 
                                    services: Optional[List[str]] = None) -> None:
        """Register all created mocks with a service container"""
        services_to_register = services or list(self.created_mocks.keys())
        
        for service_name in services_to_register:
            if service_name in self.created_mocks:
                mock = self.created_mocks[service_name]
                container.register(
                    service_name.lower().replace('interface', '_service'),
                    mock,
                    lifecycle=ServiceLifecycle.SINGLETON
                )
                logger.debug(f"Registered mock {service_name} with container")


# Pre-configured mock factories for common scenarios
def create_success_factory() -> MockServiceFactory:
    """Create factory configured for all-success responses"""
    factory = MockServiceFactory()
    factory.configure_service_behavior("default", MockServiceConfig(
        behavior=MockBehavior.SUCCESS
    ))
    return factory


def create_realistic_factory() -> MockServiceFactory:
    """Create factory configured for realistic responses with occasional failures"""
    factory = MockServiceFactory()
    factory.configure_service_behavior("default", MockServiceConfig(
        behavior=MockBehavior.REALISTIC,
        success_rate=0.9,
        average_delay_ms=25.0
    ))
    return factory


def create_failure_factory() -> MockServiceFactory:
    """Create factory configured to test failure scenarios"""
    factory = MockServiceFactory()
    factory.configure_service_behavior("default", MockServiceConfig(
        behavior=MockBehavior.FAILURE
    ))
    return factory