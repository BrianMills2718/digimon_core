"""
Adapter Registry - Phase Adapter Registration and Discovery

Handles registration and initialization of all phase adapters
with the global registry system.
"""

import logging
from typing import Dict, Any, List

from ..logging_config import get_logger
from ..graphrag_phase_interface import register_phase

logger = logging.getLogger(__name__)


def initialize_phase_adapters() -> bool:
    """Register all phase adapters with the global registry"""
    try:
        logger = get_logger("core.phase_adapters")
        
        # Import adapters
        from .phase1_adapter import Phase1Adapter
        from .phase2_adapter import Phase2Adapter  
        from .phase3_adapter import Phase3Adapter
        
        # Register Phase 1
        phase1 = Phase1Adapter()  # type: ignore[abstract]
        register_phase(phase1)
        logger.info("✓ Phase 1 adapter registered")
        
        # Register Phase 2
        phase2 = Phase2Adapter()  # type: ignore[abstract]
        register_phase(phase2)
        logger.info("✓ Phase 2 adapter registered")
        
        # Register Phase 3
        phase3 = Phase3Adapter()  # type: ignore[abstract]
        register_phase(phase3)
        logger.info("✓ Phase 3 adapter registered")
        
        return True
        
    except Exception as e:
        logger.error("❌ Failed to initialize phase adapters: %s", str(e))
        return False


def get_registered_adapters() -> Dict[str, Any]:
    """Get information about all registered adapters"""
    try:
        from ..graphrag_phase_interface import get_available_phases
        return {
            "available_phases": get_available_phases(),
            "registration_successful": True
        }
    except Exception as e:
        logger.error(f"Failed to get registered adapters: {e}")
        return {
            "available_phases": [],
            "registration_successful": False,
            "error": str(e)
        }


def health_check_all_adapters() -> Dict[str, Any]:
    """Perform health check on all registered adapters"""
    health_results: Dict[str, Any] = {
        "overall_healthy": True,
        "adapter_health": {},
        "issues": []
    }
    
    try:
        from .phase1_adapter import Phase1Adapter
        from .phase2_adapter import Phase2Adapter
        from .phase3_adapter import Phase3Adapter
        
        adapters = [
            ("Phase1", Phase1Adapter()),  # type: ignore[abstract]
            ("Phase2", Phase2Adapter()),  # type: ignore[abstract]
            ("Phase3", Phase3Adapter())   # type: ignore[abstract]
        ]
        
        for adapter_name, adapter in adapters:
            try:
                # Check if adapter has health_check method
                if hasattr(adapter, 'health_check'):
                    health = adapter.health_check()
                else:
                    health = {"adapter_healthy": True, "message": "health_check not implemented"}
                    
                adapter_health_dict: Dict[str, Any] = health_results["adapter_health"]
                adapter_health_dict[adapter_name] = health
                
                if not health.get("adapter_healthy", False):
                    health_results["overall_healthy"] = False
                    issues_list: List[str] = health_results["issues"]
                    issues_list.extend(health.get("issues", []))
                    
            except Exception as e:
                health_results["overall_healthy"] = False
                error_adapter_health_dict: Dict[str, Any] = health_results["adapter_health"]
                error_adapter_health_dict[adapter_name] = {
                    "adapter_healthy": False,
                    "error": str(e)
                }
                error_issues_list: List[str] = health_results["issues"]
                error_issues_list.append(f"{adapter_name} health check failed: {str(e)}")
        
    except Exception as e:
        health_results["overall_healthy"] = False
        final_issues_list: List[str] = health_results["issues"]
        final_issues_list.append(f"Health check process failed: {str(e)}")
    
    return health_results


def cleanup_all_adapters() -> bool:
    """Clean up all adapter resources"""
    cleanup_success = True
    
    try:
        from .phase1_adapter import Phase1Adapter
        from .phase2_adapter import Phase2Adapter
        from .phase3_adapter import Phase3Adapter
        
        adapters = [
            ("Phase1", Phase1Adapter()),  # type: ignore[abstract]
            ("Phase2", Phase2Adapter()),  # type: ignore[abstract]
            ("Phase3", Phase3Adapter())   # type: ignore[abstract]
        ]
        
        for adapter_name, adapter in adapters:
            try:
                # Check if adapter has cleanup method
                if hasattr(adapter, 'cleanup'):
                    cleanup_result = adapter.cleanup()
                else:
                    cleanup_result = True  # No cleanup needed
                    
                if not cleanup_result:
                    cleanup_success = False
                    logger.warning(f"{adapter_name} cleanup reported failure")
                    
            except Exception as e:
                cleanup_success = False
                logger.error(f"{adapter_name} cleanup failed: {e}")
        
    except Exception as e:
        cleanup_success = False
        logger.error(f"Adapter cleanup process failed: {e}")
    
    return cleanup_success