"""Orchestration Module - Modular pipeline execution components

Decomposes the original pipeline_orchestrator.py into focused modules:

Main Components:
- pipeline_orchestrator.py: Main coordinator (<200 lines)
- workflow_engines/: Different execution strategies (sequential, parallel, AnyIO)
- execution_monitors/: Progress, error, and performance monitoring
- result_aggregators/: Simple and graph-based result aggregation

This modular architecture provides:
- Clear separation of concerns
- Configurable execution strategies
- Comprehensive monitoring
- Flexible result aggregation
- Maintainable codebase with files under 200 lines each
"""

from .pipeline_orchestrator import (
    PipelineOrchestrator,
    PipelineConfig, 
    PipelineResult,
    OptimizationLevel,
    Phase
)

from .workflow_engines import (
    SequentialEngine,
    ParallelEngine, 
    AnyIOEngine
)

from .execution_monitors import (
    ProgressMonitor,
    ErrorMonitor,
    PerformanceMonitor
)

from .result_aggregators import (
    SimpleAggregator,
    GraphAggregator
)

__all__ = [
    # Main orchestrator
    'PipelineOrchestrator',
    'PipelineConfig',
    'PipelineResult', 
    'OptimizationLevel',
    'Phase',
    
    # Workflow engines
    'SequentialEngine',
    'ParallelEngine',
    'AnyIOEngine',
    
    # Execution monitors
    'ProgressMonitor', 
    'ErrorMonitor',
    'PerformanceMonitor',
    
    # Result aggregators
    'SimpleAggregator',
    'GraphAggregator'
]