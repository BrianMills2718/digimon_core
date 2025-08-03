"""Integration Tests: Dependency Injection with Real Services

These tests exercise the dependency injection container with actual service
implementations to verify ServiceProtocol compatibility and real functionality.
"""

import pytest
import logging
from typing import Dict, Any

from src.core.dependency_injection import (
    DependencyContainer, 
    get_container, 
    configure_services,
    ServiceProtocol
)
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService  
from src.core.quality_service import QualityService


class TestRealServiceIntegration:
    """Integration tests using actual service implementations."""
    
    def setup_method(self):
        """Set up fresh container for each test."""
        # Clear any existing container state
        if hasattr(DependencyContainer, '_instance'):
            DependencyContainer._instance = None
        self.container = DependencyContainer()
    
    def teardown_method(self):
        """Clean up after each test."""
        try:
            self.container.cleanup()
        except:
            pass
    
    def test_real_service_protocol_compliance(self):
        """Test that all real services implement ServiceProtocol methods."""
        # Test IdentityService
        identity = IdentityService()
        assert hasattr(identity, 'initialize'), "IdentityService missing initialize method"
        assert hasattr(identity, 'health_check'), "IdentityService missing health_check method"  
        assert hasattr(identity, 'cleanup'), "IdentityService missing cleanup method"
        
        # Test ProvenanceService
        provenance = ProvenanceService()
        assert hasattr(provenance, 'initialize'), "ProvenanceService missing initialize method"
        assert hasattr(provenance, 'health_check'), "ProvenanceService missing health_check method"
        assert hasattr(provenance, 'cleanup'), "ProvenanceService missing cleanup method"
        
        # Test QualityService
        quality = QualityService()
        assert hasattr(quality, 'initialize'), "QualityService missing initialize method"
        assert hasattr(quality, 'health_check'), "QualityService missing health_check method"
        assert hasattr(quality, 'cleanup'), "QualityService missing cleanup method"
    
    def test_real_service_initialization(self):
        """Test initialization of real services through DI container."""
        # Register real services
        self.container.register_singleton(IdentityService, lambda: IdentityService())
        self.container.register_singleton(ProvenanceService, lambda: ProvenanceService())
        self.container.register_singleton(QualityService, lambda: QualityService())
        
        # Resolve services
        identity = self.container.resolve(IdentityService)
        provenance = self.container.resolve(ProvenanceService)
        quality = self.container.resolve(QualityService)
        
        # Test initialization with actual configurations
        identity_config = {'test_config': 'identity_value', 'embedding_enabled': False}
        provenance_config = {'test_config': 'provenance_value', 'auto_cleanup_days': 30}
        quality_config = {'test_config': 'quality_value', 'default_confidence': 0.8}
        
        # These should now work with ServiceProtocol implementations
        assert identity.initialize(identity_config) == True, "IdentityService initialization failed"
        assert provenance.initialize(provenance_config) == True, "ProvenanceService initialization failed"
        assert quality.initialize(quality_config) == True, "QualityService initialization failed"
    
    def test_real_service_health_checks(self):
        """Test health check functionality of real services."""
        # Register and resolve services
        self.container.register_singleton(IdentityService, lambda: IdentityService())
        self.container.register_singleton(ProvenanceService, lambda: ProvenanceService())
        self.container.register_singleton(QualityService, lambda: QualityService())
        
        identity = self.container.resolve(IdentityService)
        provenance = self.container.resolve(ProvenanceService)
        quality = self.container.resolve(QualityService)
        
        # Initialize services first
        assert identity.initialize({}) == True
        assert provenance.initialize({}) == True
        assert quality.initialize({}) == True
        
        # Test health checks
        assert identity.health_check() == True, "IdentityService health check failed"
        assert provenance.health_check() == True, "ProvenanceService health check failed"
        assert quality.health_check() == True, "QualityService health check failed"
    
    def test_real_service_functionality_integration(self):
        """Test actual functionality of services working together through DI."""
        # Register services
        self.container.register_singleton(IdentityService, lambda: IdentityService())
        self.container.register_singleton(ProvenanceService, lambda: ProvenanceService())
        self.container.register_singleton(QualityService, lambda: QualityService())
        
        # Resolve services
        identity = self.container.resolve(IdentityService)
        provenance = self.container.resolve(ProvenanceService)
        quality = self.container.resolve(QualityService)
        
        # Initialize services
        identity.initialize({'embedding_enabled': False})
        provenance.initialize({'auto_cleanup_days': 7})
        quality.initialize({'default_confidence': 0.7})
        
        # Test actual functionality - create a mention using identity service
        mention = identity.create_mention(
            surface_form="test_entity",
            start_pos=0,
            end_pos=11,
            source_ref="integration_test",
            entity_type="PERSON",
            confidence=0.9
        )
        
        assert mention is not None, "Identity service failed to create mention"
        assert 'mention_id' in mention, "Mention missing mention_id"
        assert mention['normalized_form'] == "test_entity", "Mention normalized form incorrect"
        
        # Track the operation using provenance service
        op_id = provenance.start_operation(
            tool_id="identity_service",
            operation_type="create_mention",
            used={"input_text": "integration_test"},
            agent_details={"name": "identity_service", "version": "2.0"}
        )
        
        assert op_id is not None, "Provenance service failed to start operation"
        
        # Complete the operation
        provenance.complete_operation(op_id, [mention['mention_id']], success=True)
        
        # Assess quality using quality service
        confidence_result = quality.assess_confidence(mention['mention_id'], 0.8)
        if isinstance(confidence_result, dict):
            # Handle error response format
            assert confidence_result.get('status') != 'error', f"Quality service error: {confidence_result.get('error')}"
            confidence_score = confidence_result.get('confidence', 0.0)
            quality_tier = confidence_result.get('quality_tier', None)
        else:
            confidence_score = confidence_result
            quality_tier = None
            
        assert isinstance(confidence_score, float), "Quality service failed to return float confidence"
        assert 0.0 <= confidence_score <= 1.0, "Confidence score out of valid range"
        
        # Verify quality tier was returned
        assert quality_tier is not None, "Quality service failed to assign tier"
        assert quality_tier in ['HIGH', 'MEDIUM', 'LOW'], f"Invalid quality tier: {quality_tier}"
    
    def test_configure_services_with_real_implementations(self):
        """Test configure_services function with real service implementations."""
        # Configuration that will trigger real service imports and registration
        config = {
            'identity_service': {
                'type': 'singleton',
                'config': {'embedding_enabled': False, 'persistence_enabled': False}
            },
            'provenance_service': {
                'type': 'singleton', 
                'config': {'auto_cleanup_days': 30, 'max_operations': 1000}
            },
            'quality_service': {
                'type': 'singleton',
                'config': {'default_confidence': 0.8, 'quality_tiers': {'high': 0.8, 'medium': 0.5}}
            }
        }
        
        # This should now work without errors
        configure_services(config)
        
        # Verify services are registered and functional
        container = get_container()
        
        # Test service resolution
        identity = container.resolve(IdentityService)
        provenance = container.resolve(ProvenanceService) 
        quality = container.resolve(QualityService)
        
        # Verify they are actual service instances
        assert isinstance(identity, IdentityService), "Identity service not properly registered"
        assert isinstance(provenance, ProvenanceService), "Provenance service not properly registered"
        assert isinstance(quality, QualityService), "Quality service not properly registered"
        
        # Test that they have been initialized (should return True, not fail)
        assert identity.initialize(config['identity_service']['config']) == True
        assert provenance.initialize(config['provenance_service']['config']) == True
        assert quality.initialize(config['quality_service']['config']) == True
    
    def test_service_cleanup_integration(self):
        """Test cleanup functionality across all real services."""
        # Register and initialize services
        self.container.register_singleton(IdentityService, lambda: IdentityService())
        self.container.register_singleton(ProvenanceService, lambda: ProvenanceService())
        self.container.register_singleton(QualityService, lambda: QualityService())
        
        identity = self.container.resolve(IdentityService)
        provenance = self.container.resolve(ProvenanceService)
        quality = self.container.resolve(QualityService)
        
        # Initialize and use services to create some state
        identity.initialize({})
        provenance.initialize({})
        quality.initialize({})
        
        # Create some data
        mention = identity.create_mention("test", 0, 4, "cleanup_test")
        op_id = provenance.start_operation("test", "create", {"input": "test"})
        quality.assess_confidence("test_entity", 0.8)
        
        # Test cleanup - should not raise exceptions
        identity.cleanup()
        provenance.cleanup()
        quality.cleanup()
        
        # Services should still be functional after cleanup
        assert identity.health_check() == True, "Identity service unhealthy after cleanup"
        assert provenance.health_check() == True, "Provenance service unhealthy after cleanup"  
        assert quality.health_check() == True, "Quality service unhealthy after cleanup"
    
    def test_container_health_check_integration(self):
        """Test container-wide health checking with real services."""
        # Register services
        self.container.register_singleton(IdentityService, lambda: IdentityService())
        self.container.register_singleton(ProvenanceService, lambda: ProvenanceService())
        self.container.register_singleton(QualityService, lambda: QualityService())
        
        # Resolve services to trigger singleton creation
        identity = self.container.resolve(IdentityService)
        provenance = self.container.resolve(ProvenanceService)
        quality = self.container.resolve(QualityService)
        
        # Test container health check
        health_status = self.container.health_check()
        
        # Should include all registered services
        assert 'IdentityService' in health_status, "IdentityService missing from health check"
        assert 'ProvenanceService' in health_status, "ProvenanceService missing from health check"
        assert 'QualityService' in health_status, "QualityService missing from health check"
        
        # All should be healthy
        assert health_status['IdentityService'] == True, "IdentityService unhealthy"
        assert health_status['ProvenanceService'] == True, "ProvenanceService unhealthy"
        assert health_status['QualityService'] == True, "QualityService unhealthy"


class TestServiceProtocolCompliance:
    """Tests specifically for ServiceProtocol compliance."""
    
    def test_all_services_implement_protocol_methods(self):
        """Verify all services have required protocol methods with correct signatures."""
        services = [IdentityService(), ProvenanceService(), QualityService()]
        
        for service in services:
            service_name = service.__class__.__name__
            
            # Check method existence
            assert hasattr(service, 'initialize'), f"{service_name} missing initialize method"
            assert hasattr(service, 'health_check'), f"{service_name} missing health_check method"
            assert hasattr(service, 'cleanup'), f"{service_name} missing cleanup method"
            
            # Check method signatures by calling them
            try:
                # initialize should accept Dict[str, Any] and return bool
                result = service.initialize({})
                assert isinstance(result, bool), f"{service_name}.initialize should return bool"
                
                # health_check should return bool
                result = service.health_check()
                assert isinstance(result, bool), f"{service_name}.health_check should return bool"
                
                # cleanup should not raise exceptions
                service.cleanup()
                
            except Exception as e:
                pytest.fail(f"{service_name} ServiceProtocol method failed: {e}")
    
    def test_services_work_with_di_container_lifecycle(self):
        """Test that services work properly with DI container lifecycle management."""
        container = DependencyContainer()
        
        # Register services
        container.register_singleton(IdentityService, lambda: IdentityService())
        container.register_singleton(ProvenanceService, lambda: ProvenanceService()) 
        container.register_singleton(QualityService, lambda: QualityService())
        
        # Container should be able to initialize all services
        services = [
            container.resolve(IdentityService),
            container.resolve(ProvenanceService),
            container.resolve(QualityService)
        ]
        
        # Test initialization phase
        for service in services:
            result = service.initialize({'test': True})
            assert result == True, f"Service {service.__class__.__name__} initialization failed"
        
        # Test health check phase
        health_results = container.health_check()
        for service_name, is_healthy in health_results.items():
            assert is_healthy == True, f"Service {service_name} reported unhealthy"
        
        # Test cleanup phase
        container.cleanup()  # Should not raise exceptions