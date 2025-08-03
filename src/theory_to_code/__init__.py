"""
Theory-to-Code System

A complete system for converting social science theory schemas into
executable code using LLMs, extracting parameters from text, and
performing computational analysis.

Main components:
- LLMCodeGenerator: Generates Python code from theory formulas
- LLMParameterExtractor: Extracts theory parameters from text
- DynamicTheoryExecutor: Safely executes generated code
- IntegratedTheorySystem: Complete pipeline orchestration
"""

from .llm_code_generator import (
    LLMCodeGenerator,
    SchemaToCodeBridge,
    GeneratedFunction
)

from .llm_parameter_extractor import (
    LLMParameterExtractor,
    TextToParameterPipeline,
    ExtractedParameters,
    ProspectTheoryParameters
)

from .structured_extractor import (
    StructuredParameterExtractor,
    TextSchema,
    TextProspect,
    TextOutcome,
    TextProbability,
    ResolvedParameters
)

from .dynamic_executor import (
    SafeExecutor,
    DynamicTheoryExecutor,
    ExecutionResult
)

from .simple_executor import (
    SimpleExecutor
)

from .integrated_system import (
    IntegratedTheorySystem,
    TheoryAnalysis
)

__all__ = [
    # Code generation
    'LLMCodeGenerator',
    'SchemaToCodeBridge',
    'GeneratedFunction',
    
    # Parameter extraction
    'LLMParameterExtractor',
    'TextToParameterPipeline',
    'ExtractedParameters',
    'ProspectTheoryParameters',
    
    # Dynamic execution
    'SafeExecutor',
    'DynamicTheoryExecutor',
    'ExecutionResult',
    
    # Integrated system
    'IntegratedTheorySystem',
    'TheoryAnalysis'
]

__version__ = '1.0.0'