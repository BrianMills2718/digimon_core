"""
Phase Adapters - Main Interface

Streamlined phase adapters interface using decomposed components.
Reduced from 901 lines to focused interface.

Bridge existing phase implementations to the standard interface
with theory-aware processing and contracts support.
"""

import logging

# Import main adapters from decomposed module
from .phase_adapters import (
    Phase1Adapter,
    Phase2Adapter, 
    Phase3Adapter,
    IntegratedPipelineOrchestrator,
    initialize_phase_adapters
)

logger = logging.getLogger(__name__)

# Export for backward compatibility
__all__ = [
    "Phase1Adapter",
    "Phase2Adapter",
    "Phase3Adapter", 
    "IntegratedPipelineOrchestrator",
    "initialize_phase_adapters"
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
        "total_lines": 75   # This main file line count
    }


if __name__ == "__main__":
    # Test adapter initialization
    success = initialize_phase_adapters()
    if success:
        from .graphrag_phase_interface import get_available_phases
        
        logger.info("\nAvailable phases: %s", get_available_phases())
        
        # Test integrated pipeline
        orchestrator = IntegratedPipelineOrchestrator()
        logger.info("\n🧪 Testing integrated pipeline...")
    else:
        logger.error("❌ Adapter initialization failed")