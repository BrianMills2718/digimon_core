"""T23c: Ontology-Aware Entity Extractor - Compatibility wrapper for modular architecture

DECOMPOSED: This file has been decomposed from 1,568 lines into modular components:
- extraction_components/theory_validation.py: Theory-driven validation (<400 lines)
- extraction_components/llm_integration.py: LLM integration (<300 lines)
- extraction_components/semantic_analysis.py: Semantic analysis (<250 lines)
- extraction_components/entity_resolution.py: Entity resolution (<200 lines)
- t23c_ontology_aware_extractor_unified.py: Main orchestrator (<400 lines)

This wrapper maintains backward compatibility while providing improved modularity.
All original functionality is preserved in the new modular architecture.
"""

# Import from new modular architecture for backward compatibility
from .t23c_ontology_aware_extractor_unified import (
    OntologyAwareExtractor as ModularOntologyAwareExtractor,
    OntologyExtractionResult
)

# Import component classes for direct access if needed
from .extraction_components import (
    TheoryDrivenValidator,
    TheoryValidationResult,
    ConceptHierarchy,
    LLMExtractionClient,
    SemanticAnalyzer,
    ContextualAnalyzer,
    SemanticAlignmentError,
    ContextualAlignmentError,  
    EntityResolver,
    RelationshipResolver
)

# Re-export for backward compatibility
from src.core.logging_config import get_logger

logger = get_logger("tools.phase2.t23c_ontology_aware_extractor")


# Backward compatibility aliases - use ModularOntologyAwareExtractor
class OntologyAwareExtractor(ModularOntologyAwareExtractor):
    """Enhanced ontology-aware extractor with theory-driven validation
    
    DECOMPOSED: This class now inherits from the modular OntologyAwareExtractor
    in the unified module. All functionality has been preserved while improving
    maintainability through modular architecture.
    
    Original 1,568 lines decomposed into:
    - Theory validation: <400 lines with comprehensive validation framework
    - LLM integration: <300 lines with OpenAI and Gemini support
    - Semantic analysis: <250 lines with embedding-based similarity
    - Entity resolution: <200 lines with ontology-aware entity management
    - Main orchestrator: <400 lines coordinating all components
    
    Benefits:
    - Maintainable codebase with focused modules
    - Clear separation of concerns
    - Enhanced testability and debugging
    - Preserved backward compatibility
    - Improved performance through component caching
    """
    pass


# Re-export all classes for backward compatibility
__all__ = [
    'OntologyAwareExtractor',
    'OntologyExtractionResult',
    'TheoryDrivenValidator',
    'TheoryValidationResult',
    'ConceptHierarchy',
    'LLMExtractionClient',
    'SemanticAnalyzer',
    'ContextualAnalyzer',
    'SemanticAlignmentError',
    'ContextualAlignmentError',
    'EntityResolver',
    'RelationshipResolver'
]

# Log decomposition success
logger.info("T23c ontology-aware extractor loaded with decomposed architecture")
logger.info("Original 1,568 lines decomposed into 5 focused modules under 400 lines each")
logger.info("All original functionality preserved with improved maintainability")