"""
Phase C Tool Wrappers

Provides BaseTool-compatible wrappers for all Phase C advanced capabilities.
"""

from .multi_document_tool import MultiDocumentTool
from .cross_modal_tool import CrossModalTool
from .clustering_tool import ClusteringTool
from .temporal_tool import TemporalTool
from .collaborative_tool import CollaborativeTool

__all__ = [
    "MultiDocumentTool",
    "CrossModalTool",
    "ClusteringTool",
    "TemporalTool",
    "CollaborativeTool"
]

# Tool registry for easy access
PHASE_C_TOOLS = {
    "MULTI_DOCUMENT_PROCESSOR": MultiDocumentTool,
    "CROSS_MODAL_ANALYZER": CrossModalTool,
    "INTELLIGENT_CLUSTERER": ClusteringTool,
    "TEMPORAL_ANALYZER": TemporalTool,
    "COLLABORATIVE_INTELLIGENCE": CollaborativeTool
}

def get_phase_c_tool(tool_id: str, service_manager=None):
    """
    Factory function to get Phase C tool by ID.
    
    Args:
        tool_id: Tool identifier
        service_manager: Optional service manager
        
    Returns:
        Initialized tool instance
    """
    if tool_id not in PHASE_C_TOOLS:
        raise ValueError(f"Unknown Phase C tool: {tool_id}")
    
    tool_class = PHASE_C_TOOLS[tool_id]
    return tool_class(service_manager)