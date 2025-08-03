"""Tool Adapter Factory - Factory coordinator for all tool adapters

Centralizes tool adapter creation and management using factory pattern.
Reduces complexity by organizing adapters into phases and providing
unified creation interface.
"""

from typing import Any, Dict, List, Optional, Type
from ..logging_config import get_logger
from ..config_manager import get_config
from ..tool_protocol import Tool, ToolValidationResult

logger = get_logger("core.tool_adapter_factory")


class ToolAdapterFactory:
    """Factory for creating and managing tool adapters"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("core.tool_adapter_factory")
        self._adapters = {}
        self._phase_factories = {}
        
        # Initialize phase-specific factories
        self._initialize_phase_factories()
    
    def _initialize_phase_factories(self):
        """Initialize phase-specific adapter factories"""
        try:
            from .phase1_adapters import Phase1AdapterFactory
            from .phase2_adapters import Phase2AdapterFactory  
            from .phase3_adapters import Phase3AdapterFactory
            
            self._phase_factories = {
                'phase1': Phase1AdapterFactory(self.config_manager),
                'phase2': Phase2AdapterFactory(self.config_manager),
                'phase3': Phase3AdapterFactory(self.config_manager)
            }
            
            self.logger.info("Initialized adapter factories for all phases")
            
        except ImportError as e:
            self.logger.error(f"Failed to initialize phase factories: {e}")
            raise RuntimeError(f"Phase factory initialization failed: {e}")
    
    def create_adapter(self, adapter_name: str) -> Tool:
        """Create adapter by name using appropriate phase factory"""
        if adapter_name in self._adapters:
            return self._adapters[adapter_name]
        
        # Try each phase factory
        for phase_name, factory in self._phase_factories.items():
            if factory.can_create(adapter_name):
                adapter = factory.create_adapter(adapter_name)
                self._adapters[adapter_name] = adapter
                self.logger.info(f"Created adapter {adapter_name} using {phase_name} factory")
                return adapter
        
        raise ValueError(f"Unknown adapter: {adapter_name}")
    
    def list_available_adapters(self) -> List[str]:
        """List all available adapters across all phases"""
        adapters = []
        for factory in self._phase_factories.values():
            adapters.extend(factory.list_adapters())
        return adapters
    
    def get_adapter_info(self, adapter_name: str) -> Dict[str, Any]:
        """Get information about a specific adapter"""
        adapter = self.create_adapter(adapter_name)
        return adapter.get_tool_info()
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all phase factories"""
        health_status = {}
        for phase_name, factory in self._phase_factories.items():
            try:
                health_status[phase_name] = factory.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for {phase_name}: {e}")
                health_status[phase_name] = False
        return health_status


# Global factory instance
_tool_adapter_factory = None

def get_tool_adapter_factory():
    """Get global tool adapter factory instance"""
    global _tool_adapter_factory
    if _tool_adapter_factory is None:
        _tool_adapter_factory = ToolAdapterFactory()
    return _tool_adapter_factory