"""
Tool Adapter Registry

Extracted from tool_adapters.py - Registry for managing and accessing tool adapters.
This module provides centralized adapter registration and lookup functionality.
"""

from typing import List, Dict, Any, Optional
from ..logging_config import get_logger
from ..config_manager import get_config
from ..tool_protocol import Tool
from .base_adapters import SimplifiedToolAdapter

logger = get_logger("core.adapters.registry")


class OptimizedToolAdapterRegistry:
    """Optimized registry using simplified adapters to reduce complexity"""
    
    def __init__(self):
        self.logger = get_logger("core.tool_adapters_registry")
        self.config_manager = get_config()
        self.adapters = {}
        
        try:
            from ..tool_adapter_bridge import ToolAdapterBridge
            self.validation_bridge = ToolAdapterBridge()
            self.validation_enabled = True
            self.logger.info("Tool validation bridge initialized")
        except Exception as e:
            self.logger.warning(f"Validation bridge failed: {e}")
            self.validation_enabled = False
            
        # Register simplified adapters
        self._register_simplified_adapters()
        
    def _register_simplified_adapters(self):
        """Register all simplified adapters to reduce complexity"""
        # Import tool classes with error handling
        tool_imports = []
        
        try:
            from ...tools.phase1.t01_pdf_loader_unified import PDFLoaderUnified as _PDFLoader
            tool_imports.append((_PDFLoader, "load_pdf", "document_paths", "documents"))
        except ImportError as e:
            self.logger.warning(f"PDFLoaderUnified not available: {e}")
        
        try:
            from ...tools.phase1.t15a_text_chunker_unified import TextChunkerUnified as _TextChunker
            tool_imports.append((_TextChunker, "chunk_text", "documents", "chunks"))
        except ImportError as e:
            self.logger.warning(f"TextChunkerUnified not available: {e}")
        
        try:
            from ...tools.phase1.t23a_spacy_ner_unified import SpacyNERUnified as _SpacyNER
            tool_imports.append((_SpacyNER, "extract_entities", "chunks", "entities"))
        except ImportError as e:
            self.logger.warning(f"SpacyNERUnified not available: {e}")
        
        try:
            from ...tools.phase1.t27_relationship_extractor_unified import RelationshipExtractorUnified as _RelationshipExtractor
            tool_imports.append((_RelationshipExtractor, "extract_relationships", "entities", "relationships"))
        except ImportError as e:
            self.logger.warning(f"RelationshipExtractorUnified not available: {e}")
        
        try:
            from ...tools.phase1.t31_entity_builder_unified import EntityBuilderUnified as _EntityBuilder
            tool_imports.append((_EntityBuilder, "build_entities", "entities", "entity_results"))
        except ImportError as e:
            self.logger.warning(f"EntityBuilderUnified not available: {e}")
        
        try:
            from ...tools.phase1.t34_edge_builder_unified import EdgeBuilderUnified as _EdgeBuilder
            tool_imports.append((_EdgeBuilder, "build_edges", "relationships", "edge_results"))
        except ImportError as e:
            self.logger.warning(f"EdgeBuilderUnified not available: {e}")
        
        try:
            from ...tools.phase1.t68_pagerank_calculator_unified import PageRankCalculatorUnified as _PageRankCalculator
            tool_imports.append((_PageRankCalculator, "calculate_pagerank", "graph_data", "pagerank_results"))
        except ImportError as e:
            self.logger.warning(f"PageRankCalculatorUnified not available: {e}")
        
        try:
            from ...tools.phase1.t49_multihop_query_unified import MultiHopQueryUnified as _MultiHopQuery
            tool_imports.append((_MultiHopQuery, "execute_query", "query_data", "query_results"))
        except ImportError as e:
            self.logger.warning(f"MultiHopQueryUnified not available: {e}")
        
        # Create and register simplified adapters for available tools
        for tool_class, method, input_key, output_key in tool_imports:
            try:
                adapter_name = f"{tool_class.__name__}Adapter"
                adapter = SimplifiedToolAdapter(tool_class, method, input_key, output_key, self.config_manager)
                self.adapters[adapter_name] = adapter
                self.logger.debug(f"Registered adapter: {adapter_name}")
            except Exception as e:
                self.logger.error(f"Failed to create adapter for {tool_class.__name__}: {e}")
                
        self.logger.info(f"Registered {len(self.adapters)} simplified adapters")
        
    def register_adapter(self, name: str, adapter: Tool):
        """Register an adapter with the registry"""
        if not isinstance(adapter, Tool):
            raise ValueError(f"Adapter {name} must implement Tool protocol")
        
        self.adapters[name] = adapter
        self.logger.info(f"Registered custom adapter: {name}")
        
    def get_adapter(self, name: str) -> Optional[Tool]:
        """Get an adapter by name"""
        adapter = self.adapters.get(name)
        if adapter is None:
            self.logger.warning(f"Adapter '{name}' not found")
        return adapter
        
    def list_adapters(self) -> List[str]:
        """List all registered adapter names"""
        return list(self.adapters.keys())
    
    def get_available_adapters(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available adapters"""
        adapter_info = {}
        for name, adapter in self.adapters.items():
            try:
                info = adapter.get_tool_info() if hasattr(adapter, 'get_tool_info') else {}
                adapter_info[name] = {
                    'name': name,
                    'type': type(adapter).__name__,
                    'available': True,
                    'info': info
                }
            except Exception as e:
                adapter_info[name] = {
                    'name': name,
                    'type': type(adapter).__name__,
                    'available': False,
                    'error': str(e)
                }
        return adapter_info
    
    def unregister_adapter(self, name: str) -> bool:
        """Unregister an adapter"""
        if name in self.adapters:
            del self.adapters[name]
            self.logger.info(f"Unregistered adapter: {name}")
            return True
        else:
            self.logger.warning(f"Cannot unregister non-existent adapter: {name}")
            return False
    
    def clear_adapters(self):
        """Clear all registered adapters"""
        count = len(self.adapters)
        self.adapters.clear()
        self.logger.info(f"Cleared {count} adapters from registry")
    
    def reload_adapters(self):
        """Reload all simplified adapters"""
        self.logger.info("Reloading adapters...")
        self.clear_adapters()
        self._register_simplified_adapters()
        self.logger.info("Adapter reload complete")
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all registered adapters"""
        health_status = {
            'total_adapters': len(self.adapters),
            'healthy_adapters': 0,
            'unhealthy_adapters': 0,
            'adapter_status': {}
        }
        
        for name, adapter in self.adapters.items():
            try:
                # Try to call get_tool_info as a basic health check
                if hasattr(adapter, 'get_tool_info'):
                    adapter.get_tool_info()
                health_status['adapter_status'][name] = 'healthy'
                health_status['healthy_adapters'] += 1
            except Exception as e:
                health_status['adapter_status'][name] = f'unhealthy: {str(e)}'
                health_status['unhealthy_adapters'] += 1
        
        health_status['overall_health'] = health_status['unhealthy_adapters'] == 0
        return health_status


# Global registry instance
tool_adapter_registry = OptimizedToolAdapterRegistry()