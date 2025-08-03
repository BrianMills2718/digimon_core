"""T56: Graph Metrics Tool - Main Interface

Streamlined graph metrics calculation tool using decomposed components.
Reduced from 1,215 lines to focused interface.
"""

import time
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore

# Import decomposed metrics components
from .metrics import (
    MetricCategory,
    GraphMetrics,
    MetricCalculationConfig,
    MetricsDataLoader,
    BasicMetricsCalculator,
    CentralityMetricsCalculator,
    ConnectivityMetricsCalculator,
    StructuralMetricsCalculator,
    MetricsAggregator
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class GraphMetricsTool(BaseTool):
    """T56: Advanced Graph Metrics Tool
    
    Implements comprehensive graph metrics calculation using decomposed components:
    - MetricsDataLoader: Load graph data from various sources
    - BasicMetricsCalculator: Calculate fundamental graph metrics
    - CentralityMetricsCalculator: Calculate centrality measures
    - ConnectivityMetricsCalculator: Calculate connectivity metrics
    - StructuralMetricsCalculator: Calculate structural properties
    - MetricsAggregator: Aggregate and analyze all metrics
    
    Reduced from 1,215 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize metrics tool with decomposed components"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T56_GRAPH_METRICS"
        self.name = "Advanced Graph Metrics"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = MetricsDataLoader(service_manager)
        self.basic_calculator = BasicMetricsCalculator()
        self.centrality_calculator = CentralityMetricsCalculator()
        self.connectivity_calculator = ConnectivityMetricsCalculator()
        self.structural_calculator = StructuralMetricsCalculator()
        self.aggregator = MetricsAggregator()
        
        # Performance tracking
        self.execution_count = 0
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Comprehensive graph metrics calculation with multiple categories and performance modes",
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["networkx", "edge_list", "adjacency_matrix"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data for analysis"
                    },
                    "metric_categories": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["basic", "centrality", "connectivity", "clustering", 
                                   "structural", "efficiency", "resilience", "all"]
                        },
                        "description": "Categories of metrics to calculate"
                    },
                    "performance_mode": {
                        "type": "string",
                        "enum": ["fast", "balanced", "comprehensive", "research"],
                        "description": "Performance vs completeness trade-off"
                    },
                    "weighted": {
                        "type": "boolean",
                        "description": "Consider edge weights in calculations"
                    },
                    "directed": {
                        "type": "boolean",
                        "description": "Treat graph as directed"
                    },
                    "normalize": {
                        "type": "boolean",
                        "description": "Normalize centrality measures"
                    },
                    "include_node_level": {
                        "type": "boolean",
                        "description": "Include node-level metrics"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100000,
                        "description": "Maximum number of nodes to process"
                    },
                    "calculation_timeout": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 3600,
                        "description": "Maximum calculation time in seconds"
                    }
                },
                "required": ["graph_source", "graph_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "metrics": {"type": "object"},
                    "summary": {"type": "object"},
                    "metadata": {"type": "object"}
                },
                "required": ["metrics", "summary", "metadata"]
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive graph metrics calculation"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    f"Input validation failed: {validation_result['errors']}",
                    execution_time=time.time() - start_time
                )
            
            # Extract parameters with defaults
            graph_source = request.input_data["graph_source"]
            graph_data = request.input_data["graph_data"]
            metric_categories = request.input_data.get("metric_categories", ["all"])
            performance_mode = request.input_data.get("performance_mode", "balanced")
            weighted = request.input_data.get("weighted", False)
            directed = request.input_data.get("directed", False)
            normalize = request.input_data.get("normalize", True)
            include_node_level = request.input_data.get("include_node_level", False)
            max_nodes = request.input_data.get("max_nodes", 
                                             self.data_loader.get_max_nodes_for_mode(performance_mode))
            calculation_timeout = request.input_data.get("calculation_timeout", 300)
            
            logger.info(f"Starting metrics calculation: {graph_source} source, {performance_mode} mode")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(graph_source, graph_data, directed, max_nodes)
            
            if graph is None or len(graph.nodes) == 0:
                return self._create_error_result(
                    "Failed to load graph data or graph is empty",
                    execution_time=time.time() - start_time
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Create calculation configuration
            config = MetricCalculationConfig(
                metric_categories=metric_categories,
                weighted=weighted,
                directed=directed,
                normalize=normalize,
                include_node_level=include_node_level,
                performance_mode=performance_mode,
                max_nodes=max_nodes,
                calculation_timeout=calculation_timeout
            )
            
            # Step 3: Calculate metrics by category using decomposed calculators
            metrics_results = self._calculate_comprehensive_metrics(graph, config)
            
            # Step 4: Create comprehensive metrics object using aggregator
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            comprehensive_metrics = self.aggregator.create_comprehensive_metrics(
                basic_metrics=metrics_results.get("basic", {}),
                centrality_metrics=metrics_results.get("centrality", {}),
                connectivity_metrics=metrics_results.get("connectivity", {}),
                clustering_metrics=metrics_results.get("clustering", {}),
                structural_metrics=metrics_results.get("structural", {}),
                efficiency_metrics=metrics_results.get("efficiency", {}),
                resilience_metrics=metrics_results.get("resilience", {}),
                execution_time=execution_time,
                memory_used=memory_used
            )
            
            # Step 5: Generate summaries using aggregator
            statistical_summary = self.aggregator.calculate_statistical_summary(graph, comprehensive_metrics)
            academic_summary = self.aggregator.generate_academic_summary(graph, comprehensive_metrics)
            confidence_score = self.aggregator.calculate_academic_confidence(comprehensive_metrics, graph)
            
            # Step 6: Format output using aggregator
            formatted_output = self.aggregator.format_output(
                comprehensive_metrics, statistical_summary, academic_summary, confidence_score
            )
            
            self.execution_count += 1
            logger.info(f"Metrics calculation completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "graph_source": graph_source,
                    "performance_mode": performance_mode,
                    "metric_categories": metric_categories,
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "confidence_score": confidence_score,
                    "tool_version": self.version,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _calculate_comprehensive_metrics(self, graph, config: MetricCalculationConfig) -> Dict[str, Any]:
        """Calculate comprehensive metrics using decomposed calculators"""
        results = {}
        categories = config.metric_categories
        
        # Expand "all" to specific categories
        if "all" in categories:
            categories = ["basic", "centrality", "connectivity", "clustering", 
                         "structural", "efficiency", "resilience"]
        
        # Basic metrics (always calculated)
        if "basic" in categories:
            results["basic"] = self.basic_calculator.calculate_basic_metrics(
                graph, config.weighted, config.performance_mode
            )
        
        # Centrality metrics
        if "centrality" in categories:
            results["centrality"] = self.centrality_calculator.calculate_centrality_metrics(
                graph, config.weighted, config.normalize, config.performance_mode
            )
        
        # Connectivity metrics
        if "connectivity" in categories:
            results["connectivity"] = self.connectivity_calculator.calculate_connectivity_metrics(
                graph, config.performance_mode
            )
        
        # Clustering metrics
        if "clustering" in categories:
            results["clustering"] = self.structural_calculator.calculate_clustering_metrics(
                graph, config.include_node_level, config.performance_mode
            )
        
        # Structural metrics
        if "structural" in categories:
            results["structural"] = self.structural_calculator.calculate_structural_properties(
                graph, config.weighted, config.performance_mode
            )
        
        # Efficiency metrics
        if "efficiency" in categories:
            results["efficiency"] = self.structural_calculator.calculate_efficiency_metrics(
                graph, config.weighted, config.performance_mode
            )
        
        # Resilience metrics
        if "resilience" in categories:
            results["resilience"] = self.structural_calculator.calculate_resilience_metrics(
                graph, config.performance_mode
            )
        
        return results
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metrics calculation input"""
        errors = []
        
        # Check required fields
        required_fields = ["graph_source", "graph_data"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate graph source
        valid_sources = ["networkx", "edge_list", "adjacency_matrix"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate metric categories
        if "metric_categories" in input_data:
            valid_categories = [cat.value for cat in MetricCategory]
            for category in input_data["metric_categories"]:
                if category not in valid_categories:
                    errors.append(f"Invalid metric category: {category}")
        
        # Validate performance mode
        if "performance_mode" in input_data:
            valid_modes = ["fast", "balanced", "comprehensive", "research"]
            if input_data["performance_mode"] not in valid_modes:
                errors.append(f"performance_mode must be one of: {valid_modes}")
        
        # Validate numeric parameters
        if "max_nodes" in input_data:
            if not isinstance(input_data["max_nodes"], int) or input_data["max_nodes"] < 1:
                errors.append("max_nodes must be a positive integer")
        
        if "calculation_timeout" in input_data:
            if not isinstance(input_data["calculation_timeout"], (int, float)) or input_data["calculation_timeout"] < 1:
                errors.append("calculation_timeout must be a positive number")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, error_message: str, execution_time: float) -> ToolResult:
        """Create error result"""
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "tool_version": self.version
            },
            execution_time=execution_time
        )
    
    def _handle_error(self, error: Exception, request: ToolRequest, execution_time: float) -> ToolResult:
        """Handle errors with detailed context"""
        error_message = f"Graph metrics calculation failed: {str(error)}"
        logger.error(error_message, exc_info=True)
        
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_type": type(error).__name__,
                "input_data": request.input_data,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "tool_version": self.version
            },
            execution_time=execution_time
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Simple input validation"""
        return self._validate_input(input_data)["valid"]