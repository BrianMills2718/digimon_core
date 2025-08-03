#!/usr/bin/env python3
"""
Cross-Modal Service Registry - Central registration and discovery for cross-modal services

Provides unified access to all cross-modal analysis services with proper
dependency injection and lifecycle management.
"""

import threading
import logging
from typing import Dict, Any, Optional, Type
from datetime import datetime
from contextlib import contextmanager

# Import all cross-modal services
from .mode_selection_service import ModeSelectionService
from .cross_modal_converter import CrossModalConverter
from .cross_modal_orchestrator import CrossModalOrchestrator
from .cross_modal_validator import CrossModalValidator
from .real_llm_service import RealLLMService
from .real_embedding_service import RealEmbeddingService

logger = logging.getLogger(__name__)


class CrossModalServiceRegistry:
    """Central registry for all cross-modal analysis services.
    
    Provides:
    - Service registration and discovery
    - Dependency injection
    - Lifecycle management
    - Health monitoring
    - Thread-safe access
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'CrossModalServiceRegistry':
        """Singleton pattern for service registry"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize service registry"""
        if not self._initialized:
            self._services: Dict[str, Any] = {}
            self._service_configs: Dict[str, Dict[str, Any]] = {}
            self._initialization_order = []
            self._shutdown_handlers = {}
            self._health_checks = {}
            self._initialized = True
            
            logger.info("CrossModalServiceRegistry initialized")
    
    def initialize_all_services(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all cross-modal services with proper dependency order.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            True if all services initialized successfully
        """
        try:
            config = config or {}
            
            # 1. Initialize core dependencies first
            logger.info("Initializing core dependencies...")
            
            # Initialize LLM service
            llm_service = self._initialize_llm_service(config.get('llm', {}))
            if not llm_service:
                logger.error("Failed to initialize LLM service")
                return False
            
            # Initialize embedding service
            embedding_service = self._initialize_embedding_service(config.get('embedding', {}))
            if not embedding_service:
                logger.error("Failed to initialize embedding service")
                return False
            
            # 2. Initialize core services with dependencies
            logger.info("Initializing core cross-modal services...")
            
            # Mode Selection Service
            mode_selector = ModeSelectionService(
                service_manager=self,
                llm_client=llm_service
            )
            self.register_service('mode_selector', mode_selector)
            
            # Cross-Modal Converter
            converter = CrossModalConverter(
                service_manager=self,
                embedding_service=embedding_service
            )
            self.register_service('converter', converter)
            
            # Cross-Modal Validator
            validator = CrossModalValidator(
                converter=converter,
                service_manager=self
            )
            self.register_service('validator', validator)
            
            # Cross-Modal Orchestrator (depends on all others)
            orchestrator = CrossModalOrchestrator(
                service_manager=self
            )
            self.register_service('orchestrator', orchestrator)
            
            # 3. Initialize all registered services
            logger.info("Running service initialization...")
            for service_name in self._initialization_order:
                service = self._services[service_name]
                service_config = config.get(service_name, {})
                
                if hasattr(service, 'initialize'):
                    response = service.initialize(service_config)
                    if hasattr(response, 'success') and not response.success:
                        logger.error(f"Failed to initialize {service_name}")
                        return False
                
                logger.info(f"Initialized {service_name}")
            
            # 4. Verify all services are healthy
            health_status = self.check_all_health()
            if not all(health_status.values()):
                unhealthy = [k for k, v in health_status.items() if not v]
                logger.error(f"Unhealthy services: {unhealthy}")
                return False
            
            logger.info("All cross-modal services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            self.shutdown()
            return False
    
    def _initialize_llm_service(self, config: Dict[str, Any]) -> Optional[RealLLMService]:
        """Initialize LLM service with configuration"""
        try:
            provider = config.get('provider', 'openai')
            llm_service = RealLLMService(provider=provider)
            
            # Verify it's actually initialized
            if not llm_service.client:
                logger.error(f"LLM service client not initialized for {provider}")
                return None
                
            self.register_service('llm_service', llm_service)
            return llm_service
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            return None
    
    def _initialize_embedding_service(self, config: Dict[str, Any]) -> Optional[RealEmbeddingService]:
        """Initialize embedding service with configuration"""
        try:
            device = config.get('device', None)
            embedding_service = RealEmbeddingService(device=device)
            
            self.register_service('embedding_service', embedding_service)
            return embedding_service
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            return None
    
    def register_service(self, name: str, service: Any, config: Optional[Dict[str, Any]] = None) -> None:
        """Register a service with the registry.
        
        Args:
            name: Service name for discovery
            service: Service instance
            config: Optional service configuration
        """
        with self._lock:
            self._services[name] = service
            if config:
                self._service_configs[name] = config
            
            # Track initialization order
            if name not in self._initialization_order:
                self._initialization_order.append(name)
            
            # Register health check if available
            if hasattr(service, 'health_check'):
                self._health_checks[name] = service.health_check
            
            # Register shutdown handler if available
            if hasattr(service, 'cleanup') or hasattr(service, 'shutdown'):
                self._shutdown_handlers[name] = getattr(service, 'cleanup', getattr(service, 'shutdown', None))
            
            logger.info(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        return self._services.get(name)
    
    def list_services(self) -> Dict[str, str]:
        """List all registered services.
        
        Returns:
            Dictionary of service names to their class names
        """
        return {
            name: service.__class__.__name__
            for name, service in self._services.items()
        }
    
    def check_health(self, service_name: str) -> bool:
        """Check health of a specific service.
        
        Args:
            service_name: Name of service to check
            
        Returns:
            True if service is healthy
        """
        if service_name not in self._health_checks:
            return service_name in self._services
        
        try:
            health_check = self._health_checks[service_name]
            response = health_check()
            
            # Handle both sync and async responses
            if hasattr(response, 'success'):
                return response.success
            return bool(response)
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False
    
    def check_all_health(self) -> Dict[str, bool]:
        """Check health of all registered services.
        
        Returns:
            Dictionary of service names to health status
        """
        return {
            name: self.check_health(name)
            for name in self._services
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics from all services.
        
        Returns:
            Dictionary of service statistics
        """
        stats = {
            'registry': {
                'total_services': len(self._services),
                'healthy_services': sum(self.check_all_health().values()),
                'services': list(self._services.keys()),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Collect stats from each service
        for name, service in self._services.items():
            if hasattr(service, 'get_statistics'):
                try:
                    service_stats = service.get_statistics()
                    if hasattr(service_stats, 'data'):
                        stats[name] = service_stats.data
                    else:
                        stats[name] = service_stats
                except Exception as e:
                    logger.error(f"Failed to get stats from {name}: {e}")
                    stats[name] = {'error': str(e)}
        
        return stats
    
    def shutdown(self) -> None:
        """Shutdown all services in reverse initialization order."""
        logger.info("Shutting down cross-modal services...")
        
        # Shutdown in reverse order
        for service_name in reversed(self._initialization_order):
            if service_name in self._shutdown_handlers:
                try:
                    handler = self._shutdown_handlers[service_name]
                    handler()
                    logger.info(f"Shutdown {service_name}")
                except Exception as e:
                    logger.error(f"Error shutting down {service_name}: {e}")
        
        # Clear registry
        self._services.clear()
        self._service_configs.clear()
        self._initialization_order.clear()
        self._shutdown_handlers.clear()
        self._health_checks.clear()
        
        logger.info("All services shutdown complete")
    
    # Convenience methods for specific services
    @property
    def mode_selector(self) -> Optional[ModeSelectionService]:
        """Get mode selection service"""
        return self.get_service('mode_selector')
    
    @property
    def converter(self) -> Optional[CrossModalConverter]:
        """Get cross-modal converter"""
        return self.get_service('converter')
    
    @property
    def validator(self) -> Optional[CrossModalValidator]:
        """Get cross-modal validator"""
        return self.get_service('validator')
    
    @property
    def orchestrator(self) -> Optional[CrossModalOrchestrator]:
        """Get cross-modal orchestrator"""
        return self.get_service('orchestrator')
    
    @property
    def llm_service(self) -> Optional[RealLLMService]:
        """Get LLM service"""
        return self.get_service('llm_service')
    
    @property
    def embedding_service(self) -> Optional[RealEmbeddingService]:
        """Get embedding service"""
        return self.get_service('embedding_service')
    
    # Service manager compatibility methods
    def get_llm_client(self) -> Optional[RealLLMService]:
        """Get LLM client for compatibility with service manager interface"""
        return self.llm_service
    
    def get_embedding_client(self) -> Optional[RealEmbeddingService]:
        """Get embedding client for compatibility"""
        return self.embedding_service


# Global registry instance
_registry: Optional[CrossModalServiceRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> CrossModalServiceRegistry:
    """Get the global cross-modal service registry instance.
    
    Returns:
        The singleton registry instance
    """
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = CrossModalServiceRegistry()
    return _registry


def initialize_cross_modal_services(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize all cross-modal services.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        True if initialization successful
    """
    registry = get_registry()
    return registry.initialize_all_services(config)


def get_cross_modal_service(service_name: str) -> Optional[Any]:
    """Get a cross-modal service by name.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Service instance or None
    """
    registry = get_registry()
    return registry.get_service(service_name)


@contextmanager
def cross_modal_services(config: Optional[Dict[str, Any]] = None):
    """Context manager for cross-modal services.
    
    Usage:
        with cross_modal_services() as registry:
            orchestrator = registry.orchestrator
            result = orchestrator.orchestrate_analysis(...)
    """
    registry = get_registry()
    try:
        if not registry.list_services():  # Not initialized yet
            success = registry.initialize_all_services(config)
            if not success:
                raise RuntimeError("Failed to initialize cross-modal services")
        yield registry
    finally:
        # Note: We don't shutdown here to allow reuse
        pass


# Export key functions and classes
__all__ = [
    'CrossModalServiceRegistry',
    'get_registry',
    'initialize_cross_modal_services',
    'get_cross_modal_service',
    'cross_modal_services'
]