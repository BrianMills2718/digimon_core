"""
Advanced Graph Analytics Module

Implements sophisticated graph analytics capabilities for the KGAS Phase 2.1 system,
providing entity relationship analysis, community detection, cross-modal linking,
and research impact assessment on the bulletproof reliability foundation.
"""

# Import core analytics components with graceful handling of missing dependencies
try:
    from .graph_centrality_analyzer import GraphCentralityAnalyzer, AnalyticsError
except ImportError as e:
    GraphCentralityAnalyzer = None
    AnalyticsError = Exception

try:
    from .community_detector import CommunityDetector
except ImportError:
    CommunityDetector = None

try:
    from .cross_modal_linker import CrossModalEntityLinker  
except ImportError:
    CrossModalEntityLinker = None

try:
    from .knowledge_synthesizer import ConceptualKnowledgeSynthesizer
except ImportError:
    ConceptualKnowledgeSynthesizer = None

try:
    from .citation_impact_analyzer import CitationImpactAnalyzer
except ImportError:
    CitationImpactAnalyzer = None

try:
    from .scale_free_analyzer import ScaleFreeAnalyzer, ScaleFreeAnalysisError
except ImportError:
    ScaleFreeAnalyzer = None
    ScaleFreeAnalysisError = Exception

try:
    from .graph_export_tool import GraphExportTool, GraphExportError
except ImportError:
    GraphExportTool = None
    GraphExportError = Exception

# Import new cross-modal orchestration components
try:
    from .mode_selection_service import ModeSelectionService, AnalysisMode, DataContext
except ImportError:
    ModeSelectionService = None
    AnalysisMode = None
    DataContext = None

try:
    from .cross_modal_converter import CrossModalConverter, DataFormat
except ImportError:
    CrossModalConverter = None
    DataFormat = None

try:
    from .cross_modal_validator import CrossModalValidator, ValidationLevel
except ImportError:
    CrossModalValidator = None
    ValidationLevel = None

try:
    from .cross_modal_orchestrator import CrossModalOrchestrator, WorkflowOptimizationLevel
except ImportError:
    CrossModalOrchestrator = None
    WorkflowOptimizationLevel = None

try:
    from .cross_modal_service_registry import (
        CrossModalServiceRegistry, get_registry, initialize_cross_modal_services,
        get_cross_modal_service, cross_modal_services
    )
except ImportError:
    CrossModalServiceRegistry = None
    get_registry = None
    initialize_cross_modal_services = None
    get_cross_modal_service = None
    cross_modal_services = None

__all__ = [
    # Legacy analytics components
    'GraphCentralityAnalyzer',
    'CommunityDetector', 
    'CrossModalEntityLinker',
    'ConceptualKnowledgeSynthesizer',
    'CitationImpactAnalyzer',
    'ScaleFreeAnalyzer',
    'GraphExportTool',
    'AnalyticsError',
    'ScaleFreeAnalysisError',
    'GraphExportError',
    
    # New cross-modal orchestration components
    'ModeSelectionService',
    'AnalysisMode',
    'DataContext',
    'CrossModalConverter',
    'DataFormat',
    'CrossModalValidator',
    'ValidationLevel',
    'CrossModalOrchestrator',
    'WorkflowOptimizationLevel',
    
    # Service registry
    'CrossModalServiceRegistry',
    'get_registry',
    'initialize_cross_modal_services',
    'get_cross_modal_service',
    'cross_modal_services'
]