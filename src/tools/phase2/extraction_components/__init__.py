"""Extraction Components Package

Modular components for the ontology-aware entity extractor:

- theory_validation: Theory-driven validation of entities against ontological frameworks
- llm_integration: LLM-based entity extraction (OpenAI and Gemini)
- semantic_analysis: Semantic similarity calculations and alignment analysis
- entity_resolution: Entity creation, mention management, and ontology validation
"""

from .theory_validation import (
    TheoryDrivenValidator,
    TheoryValidationResult, 
    ConceptHierarchy,
    ValidationResultAnalyzer
)

from .llm_integration import (
    LLMExtractionClient
)

from .semantic_analysis import (
    SemanticAnalyzer,
    ContextualAnalyzer,
    SemanticAlignmentError,
    ContextualAlignmentError,
    SemanticCache
)

from .entity_resolution import (
    EntityResolver,
    RelationshipResolver
)

__all__ = [
    # Theory validation
    'TheoryDrivenValidator',
    'TheoryValidationResult',
    'ConceptHierarchy', 
    'ValidationResultAnalyzer',
    
    # LLM integration
    'LLMExtractionClient',
    
    # Semantic analysis
    'SemanticAnalyzer',
    'ContextualAnalyzer',
    'SemanticAlignmentError',
    'ContextualAlignmentError',
    'SemanticCache',
    
    # Entity resolution
    'EntityResolver',
    'RelationshipResolver'
]