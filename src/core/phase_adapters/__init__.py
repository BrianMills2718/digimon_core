"""
Phase Adapters - Decomposed Components

Modular architecture for phase adapters that bridge existing phase implementations 
to the standard interface. Decomposed from 901-line monolithic file into focused components.
"""

# Export main adapter classes
from .phase1_adapter import Phase1Adapter
from .phase2_adapter import Phase2Adapter  
from .phase3_adapter import Phase3Adapter
from .integrated_orchestrator import IntegratedPipelineOrchestrator
from .adapter_registry import initialize_phase_adapters

# Export supporting classes for extension
from .theory_aware_base import TheoryAwareAdapterBase
from .adapter_utils import AdapterUtils

__all__ = [
    "Phase1Adapter",
    "Phase2Adapter",
    "Phase3Adapter", 
    "IntegratedPipelineOrchestrator",
    "initialize_phase_adapters",
    "TheoryAwareAdapterBase",
    "AdapterUtils"
]

def get_phase_adapters_info():
    """Get information about the phase adapters implementation"""
    return {
        "module": "phase_adapters",
        "version": "2.0.0",
        "architecture": "decomposed_components",
        "description": "Phase adapters with modular architecture and theory-aware support",
        "capabilities": [
            "phase1_basic_graphrag_adapter",
            "phase2_enhanced_ontology_adapter", 
            "phase3_multidocument_fusion_adapter",
            "theory_aware_processing",
            "integrated_pipeline_orchestration",
            "contract_based_validation",
            "performance_monitoring"
        ],
        "components": {
            "phase1_adapter": "Basic GraphRAG workflow adapter with theory support",
            "phase2_adapter": "Enhanced GraphRAG with ontology integration adapter",
            "phase3_adapter": "Multi-document fusion workflow adapter",
            "integrated_orchestrator": "Full pipeline orchestration with data flow",
            "adapter_registry": "Phase adapter registration and discovery",
            "theory_aware_base": "Base class for theory-aware processing",
            "adapter_utils": "Common utilities for adapter implementations"
        },
        "decomposed": True,
        "file_count": 8,  # Main file + 7 component files
        "total_lines": 95   # This main file line count
    }