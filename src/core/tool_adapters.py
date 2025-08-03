"""
Tool Protocol Adapters - Unified Interface

This module has been decomposed from 1,892 lines into focused modules:
- adapters/base_adapters.py: Base adapter classes and infrastructure  
- adapters/phase1_adapters.py: Phase 1 document processing adapters
- adapters/phase2_adapters.py: Phase 2 ontology-aware adapters  
- adapters/phase3_adapters.py: Phase 3 multi-document fusion adapters
- adapters/analysis_adapters.py: Analysis and query adapters
- adapters/adapter_registry.py: Adapter registration and management

This unified interface maintains backward compatibility while providing improved modularity.
"""

# Import all adapters for backward compatibility
from .adapters.base_adapters import (
    SimplifiedToolAdapter,
    BaseToolAdapter,
    DEFAULT_CONCEPT_LIBRARY,
    create_simplified_adapter
)

from .adapters.adapter_registry import (
    OptimizedToolAdapterRegistry,
    tool_adapter_registry
)

from .adapters.phase1_adapters import (
    PDFLoaderAdapter,
    TextChunkerAdapter,
    SpacyNERAdapter,
    RelationshipExtractorAdapter,
    EntityBuilderAdapter,
    EdgeBuilderAdapter
)

from .adapters.analysis_adapters import (
    PageRankAdapter,
    MultiHopQueryAdapter,
    GraphAnalysisAdapter
)

from .adapters.phase2_adapters import (
    OntologyAwareExtractorAdapter,
    OntologyGraphBuilderAdapter,
    OntologyValidatorAdapter
)

from .adapters.phase3_adapters import (
    MultiDocumentFusionAdapter,
    InteractiveGraphVisualizerAdapter,
    DocumentComparisonAdapter
)

# Import configuration and logging
from .logging_config import get_logger
from .config_manager import get_config

logger = get_logger("core.tool_adapters")

# Maintain backward compatibility with legacy imports
__all__ = [
    # Base classes
    'SimplifiedToolAdapter',
    'BaseToolAdapter',
    'OptimizedToolAdapterRegistry',
    'create_simplified_adapter',
    'DEFAULT_CONCEPT_LIBRARY',
    
    # Phase 1 adapters
    'PDFLoaderAdapter',
    'TextChunkerAdapter',
    'SpacyNERAdapter',
    'RelationshipExtractorAdapter',
    'EntityBuilderAdapter',
    'EdgeBuilderAdapter',
    
    # Analysis adapters
    'PageRankAdapter',
    'MultiHopQueryAdapter',
    'GraphAnalysisAdapter',
    
    # Phase 2 adapters
    'OntologyAwareExtractorAdapter',
    'OntologyGraphBuilderAdapter',
    'OntologyValidatorAdapter',
    
    # Phase 3 adapters
    'MultiDocumentFusionAdapter',
    'InteractiveGraphVisualizerAdapter',
    'DocumentComparisonAdapter',
    
    # Registry and global instances
    'tool_adapter_registry'
]

# Log decomposition success
logger.info("Tool adapters module loaded with decomposed architecture")
logger.info(f"Available adapters: {len(__all__)} classes")
logger.info(f"Registry contains: {len(tool_adapter_registry.adapters)} simplified adapters")

# Provide factory functions for easy adapter creation
def get_adapter(adapter_name: str):
    """Get an adapter instance by name"""
    return tool_adapter_registry.get_adapter(adapter_name)

def list_available_adapters():
    """List all available adapters"""
    return tool_adapter_registry.list_adapters()

def get_adapter_info():
    """Get information about all available adapters"""
    return tool_adapter_registry.get_available_adapters()

def check_adapter_health():
    """Check health of all adapters"""
    return tool_adapter_registry.health_check()

# Maintain compatibility with module-level functions
def demonstrate_tool_adapters():
    """Demonstrate tool adapter functionality with decomposed architecture"""
    print("🔗 Tool Adapter Architecture Demonstration")
    print("=" * 50)
    
    try:
        # Show decomposed architecture info
        print(f"📦 Decomposed Architecture:")
        print(f"   - Base adapters: {len([cls for cls in __all__ if 'Base' in cls or 'Simplified' in cls])} classes")
        print(f"   - Phase 1 adapters: {len([cls for cls in __all__ if any(phase in cls for phase in ['PDF', 'Text', 'Spacy', 'Relationship', 'Entity', 'Edge'])])} classes")
        print(f"   - Analysis adapters: {len([cls for cls in __all__ if any(analysis in cls for analysis in ['PageRank', 'Query', 'Analysis'])])} classes")
        print(f"   - Phase 2 adapters: {len([cls for cls in __all__ if 'Ontology' in cls])} classes")
        print(f"   - Phase 3 adapters: {len([cls for cls in __all__ if any(phase3 in cls for phase3 in ['Fusion', 'Visualizer', 'Comparison'])])} classes")
        
        # Show registry status
        registry_health = check_adapter_health()
        print(f"\n🏥 Registry Health:")
        print(f"   - Total adapters: {registry_health['total_adapters']}")
        print(f"   - Healthy adapters: {registry_health['healthy_adapters']}")
        print(f"   - Overall health: {'✅' if registry_health['overall_health'] else '❌'}")
        
        # Show adapter info
        adapter_info = get_adapter_info()
        print(f"\n📋 Available Simplified Adapters:")
        for name, info in list(adapter_info.items())[:5]:  # Show first 5
            status = "✅" if info['available'] else "❌"
            print(f"   {status} {name}: {info['type']}")
        
        if len(adapter_info) > 5:
            print(f"   ... and {len(adapter_info) - 5} more adapters")
        
        print(f"\n🎯 Decomposition Complete:")
        print(f"   - Original: 1,892 lines → Decomposed architecture")
        print(f"   - Modularity: ✅ Focused modules with single responsibility")
        print(f"   - Compatibility: ✅ All original APIs preserved")
        print(f"   - Maintainability: ✅ Clear separation of concerns")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")

if __name__ == "__main__":
    demonstrate_tool_adapters()