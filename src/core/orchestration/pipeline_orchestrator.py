"""Pipeline Orchestrator - Main coordinator (<200 lines)

Coordinates workflow execution across different engines and monitors.
Provides unified interface for all pipeline operations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager, get_config
from ..tool_protocol import Tool
from .workflow_engines import SequentialEngine, ParallelEngine, AnyIOEngine
from .execution_monitors import ProgressMonitor, ErrorMonitor, PerformanceMonitor
from .result_aggregators import SimpleAggregator, GraphAggregator

logger = get_logger("core.orchestration.pipeline_orchestrator")


class OptimizationLevel(Enum):
    """Different optimization levels for pipeline execution"""
    STANDARD = "standard"
    OPTIMIZED = "optimized" 
    ENHANCED = "enhanced"


class Phase(Enum):
    """Supported pipeline phases"""
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution"""
    tools: List[Tool]
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    phase: Phase = Phase.PHASE1
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    confidence_threshold: float = 0.7
    workflow_storage_dir: Optional[str] = None


@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    status: str
    entities: List[Any]
    relationships: List[Any]
    graph_created: bool
    query_enabled: bool
    text_chunks: List[str]
    error: Optional[str] = None


class PipelineOrchestrator:
    """Main pipeline orchestrator with modular architecture
    
    Coordinates execution across specialized engines and monitors.
    Provides single interface for all pipeline operations.
    """
    
    def __init__(self, config: PipelineConfig = None, config_manager: ConfigurationManager = None):
        """Initialize orchestrator with configuration"""
        self.config = config
        self.logger = get_logger("core.orchestration.pipeline_orchestrator")
        self.config_manager = config_manager or get_config()
        
        # Initialize pipeline validator
        from ..pipeline_validator import PipelineValidator
        self.pipeline_validator = PipelineValidator()
        
        # Initialize workflow engines
        self._initialize_engines()
        
        # Initialize execution monitors
        self._initialize_monitors()
        
        # Initialize result aggregators
        self._initialize_aggregators()
        
        # Select engine based on optimization level
        self._select_execution_engine()
        
        # Validate pipeline if config provided
        if self.config and self.config.tools:
            self._validate_pipeline()
        
    def _initialize_engines(self):
        """Initialize workflow execution engines"""
        self.sequential_engine = SequentialEngine(self.config_manager)
        self.parallel_engine = ParallelEngine(self.config_manager)
        self.anyio_engine = AnyIOEngine(self.config_manager)
        
    def _initialize_monitors(self):
        """Initialize execution monitoring components"""
        self.progress_monitor = ProgressMonitor()
        self.error_monitor = ErrorMonitor()
        self.performance_monitor = PerformanceMonitor()
        
    def _initialize_aggregators(self):
        """Initialize result aggregation components"""
        self.simple_aggregator = SimpleAggregator()
        self.graph_aggregator = GraphAggregator()
        
    def _select_execution_engine(self):
        """Select execution engine based on optimization level"""
        if not self.config:
            self.execution_engine = self.sequential_engine
            return
            
        if self.config.optimization_level == OptimizationLevel.STANDARD:
            self.execution_engine = self.sequential_engine
        elif self.config.optimization_level == OptimizationLevel.OPTIMIZED:
            self.execution_engine = self.parallel_engine
        else:  # ENHANCED
            self.execution_engine = self.anyio_engine
    
    def _validate_pipeline(self):
        """Validate pipeline configuration before execution"""
        is_valid, errors = self.pipeline_validator.validate_pipeline(self.config.tools)
        
        if not is_valid:
            error_msg = "Pipeline validation failed:\n"
            for error in errors:
                error_msg += f"  - {error}\n"
            
            # Get suggestions
            suggestions = self.pipeline_validator.suggest_fixes(errors)
            if suggestions:
                error_msg += "\nSuggestions:\n"
                for suggestion in suggestions:
                    error_msg += f"  - {suggestion}\n"
            
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Pipeline validated successfully with {len(self.config.tools)} tools")
            
    def execute(self, document_paths: List[str], queries: List[str] = None) -> Dict[str, Any]:
        """Execute pipeline with configured tools
        
        Args:
            document_paths: List of document paths to process
            queries: Optional list of queries to execute
            
        Returns:
            Complete pipeline execution result with metadata
        """
        # Input validation
        if not document_paths:
            raise ValueError("document_paths cannot be empty")
            
        start_time = time.time()
        
        # Setup execution context
        execution_context = {
            "document_paths": document_paths,
            "queries": queries or [],
            "workflow_id": f"{self.config.phase.value}_{int(start_time)}",
            "start_time": start_time
        }
        
        try:
            # Start monitoring
            self.progress_monitor.start_execution(execution_context)
            self.performance_monitor.start_monitoring()
            
            # Execute pipeline using selected engine
            results = self.execution_engine.execute_pipeline(
                tools=self.config.tools,
                input_data=execution_context,
                monitors=[self.progress_monitor, self.error_monitor, self.performance_monitor]
            )
            
            # Aggregate results
            if self.config.phase == Phase.PHASE1:
                final_results = self.simple_aggregator.aggregate(results)
            else:
                final_results = self.graph_aggregator.aggregate(results)
            
            # Finalize execution
            execution_time = time.time() - start_time
            final_results.update({
                "execution_metadata": {
                    "total_time": execution_time,
                    "success": True,
                    "phase": self.config.phase.value,
                    "optimization_level": self.config.optimization_level.value
                }
            })
            
            return final_results
            
        except Exception as e:
            self.error_monitor.record_error(e)
            execution_time = time.time() - start_time
            
            return {
                "status": "error",
                "error": str(e),
                "execution_metadata": {
                    "total_time": execution_time,
                    "success": False,
                    "phase": self.config.phase.value if self.config else "unknown",
                    "optimization_level": self.config.optimization_level.value if self.config else "unknown"
                }
            }
        finally:
            self.progress_monitor.complete_execution()
            self.performance_monitor.stop_monitoring()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        return {
            "progress": self.progress_monitor.get_progress(),
            "errors": self.error_monitor.get_error_summary(),
            "performance": self.performance_monitor.get_metrics()
        }
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all orchestrator components"""
        return {
            "sequential_engine": self.sequential_engine.health_check(),
            "parallel_engine": self.parallel_engine.health_check(),
            "anyio_engine": self.anyio_engine.health_check(),
            "progress_monitor": self.progress_monitor.health_check(),
            "error_monitor": self.error_monitor.health_check(),
            "performance_monitor": self.performance_monitor.health_check()
        }