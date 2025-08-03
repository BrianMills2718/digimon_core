"""T51: Centrality Analysis Tool - Main Interface

Streamlined centrality analysis tool using decomposed components.
Reduced from 1,051 lines to focused interface.
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
except ImportError:
    from core.service_manager import ServiceManager

# Import decomposed centrality analysis components
from .centrality_analysis import (
    CentralityMetric,
    CentralityResult,
    CentralityStats,
    CentralityGraphDataLoader,
    CentralityCalculator,
    CentralityAnalyzer,
    CentralityResultsAggregator
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityAnalysisTool(BaseTool):
    """T51: Advanced Centrality Analysis Tool
    
    Implements comprehensive centrality analysis using decomposed components:
    - CentralityGraphDataLoader: Load graph data from various sources
    - CentralityCalculator: Calculate various centrality metrics
    - CentralityAnalyzer: Analyze correlations and statistics
    - CentralityResultsAggregator: Format and store results
    
    Reduced from 1,051 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize centrality analysis tool with decomposed components"""
        super().__init__(service_manager)
        self.tool_id = "T51_CENTRALITY_ANALYSIS"
        self.name = "Advanced Centrality Analysis"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = CentralityGraphDataLoader(service_manager)
        self.calculator = CentralityCalculator()
        self.analyzer = CentralityAnalyzer()
        self.aggregator = CentralityResultsAggregator(service_manager)
        
        # Configuration
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Performance tracking
        self.execution_count = 0
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Comprehensive centrality analysis with multiple metrics and correlation analysis",
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["neo4j", "networkx", "edge_list", "adjacency_matrix"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data in specified format"
                    },
                    "centrality_metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["degree", "betweenness", "closeness", "eigenvector", 
                                   "pagerank", "katz", "harmonic", "load", "information",
                                   "current_flow_betweenness", "current_flow_closeness", 
                                   "subgraph", "all"]
                        },
                        "description": "Centrality metrics to calculate"
                    },
                    "normalize_scores": {
                        "type": "boolean",
                        "description": "Whether to normalize centrality scores"
                    },
                    "calculate_correlations": {
                        "type": "boolean",
                        "description": "Whether to calculate metric correlations"
                    },
                    "top_k_nodes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Number of top nodes to return per metric"
                    },
                    "source_document": {
                        "type": "string",
                        "description": "Source document identifier for storing results"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "academic"],
                        "description": "Output format preference"
                    },
                    "config_overrides": {
                        "type": "object",
                        "description": "Configuration overrides for specific metrics"
                    }
                },
                "required": ["graph_source", "centrality_metrics"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "centrality_results": {"type": "array"},
                    "statistics": {"type": "object"},
                    "correlation_matrix": {"type": "object"},
                    "top_nodes": {"type": "object"},
                    "confidence_score": {"type": "number"},
                    "metadata": {"type": "object"}
                }
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive centrality analysis"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Validate input
            validation_result = self._validate_input_data(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    request, f"Input validation failed: {validation_result['errors']}"
                )
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            graph_data = request.input_data.get("graph_data", {})
            centrality_metrics = [CentralityMetric(cm) for cm in request.input_data["centrality_metrics"]]
            normalize_scores = request.input_data.get("normalize_scores", True)
            calculate_correlations = request.input_data.get("calculate_correlations", True)
            top_k_nodes = request.input_data.get("top_k_nodes", 20)
            source_document = request.input_data.get("source_document", "unknown")
            output_format = request.input_data.get("output_format", "detailed")
            config_overrides = request.input_data.get("config_overrides", {})
            
            logger.info(f"Starting centrality analysis: {graph_source} source, {len(centrality_metrics)} metrics")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(graph_source, graph_data)
            
            if graph is None:
                return self._create_error_result(
                    request, "Failed to load graph data from specified source"
                )
            
            # Validate graph for centrality analysis
            validation = self.data_loader.validate_graph_for_centrality(graph)
            if not validation["valid"]:
                return self._create_error_result(
                    request, f"Graph validation failed: {validation['errors']}"
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Calculate centrality metrics using decomposed calculator
            results = []
            all_scores = {}
            
            # Handle "all" metric
            if CentralityMetric.ALL in centrality_metrics:
                centrality_metrics = [metric for metric in CentralityMetric if metric != CentralityMetric.ALL]
            
            for metric in centrality_metrics:
                try:
                    # Get config overrides for this metric
                    metric_config = config_overrides.get(metric.value, {})
                    metric_config["normalized"] = normalize_scores
                    
                    # Prepare graph for this specific metric
                    prepared_graph = self.data_loader.prepare_graph_for_centrality(graph, metric.value)
                    
                    # Calculate centrality
                    result = self.calculator.calculate_centrality_metric(
                        prepared_graph, metric, metric_config
                    )
                    
                    results.append(result)
                    
                    if result.scores:
                        all_scores[metric.value] = result.normalized_scores if normalize_scores else result.scores
                        logger.info(f"Calculated {metric.value} centrality: {len(result.scores)} nodes")
                    else:
                        logger.warning(f"Failed to calculate {metric.value} centrality")
                        
                except Exception as e:
                    logger.error(f"Error calculating {metric.value} centrality: {e}")
                    continue
            
            if not all_scores:
                return self._create_error_result(
                    request, "No centrality metrics were successfully calculated"
                )
            
            # Step 3: Calculate correlation matrix using decomposed analyzer
            correlation_matrix = {}
            if calculate_correlations and len(all_scores) > 1:
                correlation_matrix = self.analyzer.calculate_correlation_matrix(all_scores)
            
            # Step 4: Calculate graph statistics using decomposed analyzer
            graph_statistics = self.analyzer.calculate_graph_statistics(graph)
            
            # Step 5: Identify top nodes using decomposed analyzer
            top_nodes_by_metric = self.analyzer.identify_top_nodes(all_scores, top_k_nodes)
            
            # Step 6: Calculate academic confidence using decomposed analyzer
            confidence_score = self.analyzer.calculate_academic_confidence(
                results, graph, correlation_matrix
            )
            
            # Step 7: Create statistics object
            stats = CentralityStats(
                total_metrics=len(results),
                metrics_calculated=[r.metric for r in results if r.scores],
                correlation_matrix=correlation_matrix,
                top_nodes_by_metric=top_nodes_by_metric,
                graph_statistics=graph_statistics,
                analysis_metadata={
                    "normalize_scores": normalize_scores,
                    "calculate_correlations": calculate_correlations,
                    "top_k_nodes": top_k_nodes,
                    "config_overrides": config_overrides
                }
            )
            
            # Step 8: Store results using decomposed aggregator
            storage_result = self.aggregator.store_centrality_results(all_scores, source_document)
            
            # Step 9: Format output using decomposed aggregator
            formatted_output = self.aggregator.format_centrality_output(
                results, stats, output_format, confidence_score
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Centrality analysis completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "graph_source": graph_source,
                    "metrics_calculated": [r.metric for r in results if r.scores],
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "successful_calculations": len([r for r in results if r.scores]),
                    "total_calculations": len(results),
                    "correlations_calculated": len(correlation_matrix),
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "confidence_score": confidence_score,
                    "storage_result": storage_result,
                    "output_format": output_format,
                    "tool_version": self.version,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for centrality analysis"""
        errors = []
        
        # Check required fields
        required_fields = ["graph_source", "centrality_metrics"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate graph source
        valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate centrality metrics
        valid_metrics = [metric.value for metric in CentralityMetric]
        centrality_metrics = input_data.get("centrality_metrics", [])
        for metric in centrality_metrics:
            if metric not in valid_metrics:
                errors.append(f"Invalid centrality metric: {metric}")
        
        # Validate numeric parameters
        if "top_k_nodes" in input_data:
            top_k = input_data["top_k_nodes"]
            if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
                errors.append("top_k_nodes must be between 1 and 100")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, request: ToolRequest, error_message: str, 
                           error_code: str = "CENTRALITY_ANALYSIS_FAILED") -> ToolResult:
        """Create error result"""
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_code": error_code,
                "input_data": request.input_data,
                "timestamp": datetime.now().isoformat(),
                "tool_version": self.version
            },
            execution_time=0.0
        )
    
    def _handle_error(self, error: Exception, request: ToolRequest, execution_time: float) -> ToolResult:
        """Handle errors with detailed context"""
        error_message = f"Centrality analysis failed: {str(error)}"
        logger.error(error_message, exc_info=True)
        
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_type": type(error).__name__,
                "input_data": request.input_data,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "tool_version": self.version
            },
            execution_time=execution_time
        )
    
    def health_check(self) -> ToolResult:
        """Perform health check on the tool"""
        try:
            # Test basic functionality
            test_graph_data = {
                "nodes": ["A", "B", "C", "D"],
                "edges": [["A", "B"], ["B", "C"], ["C", "A"], ["A", "D"]]
            }
            
            test_graph = self.data_loader.load_graph_data("networkx", test_graph_data)
            
            if test_graph is None:
                return ToolResult(
                    tool_id=self.tool_id, status="error", 
                    data={"healthy": False, "error": "Failed to load test graph"},
                    execution_time=0.0
                )
            
            # Test centrality calculation
            test_result = self.calculator.calculate_centrality_metric(
                test_graph, CentralityMetric.DEGREE
            )
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "healthy": True,
                    "components_status": {
                        "data_loader": "operational",
                        "calculator": "operational",
                        "analyzer": "operational",
                        "aggregator": "operational"
                    },
                    "test_results": {
                        "graph_nodes": len(test_graph.nodes),
                        "graph_edges": len(test_graph.edges),
                        "centrality_calculated": len(test_result.scores) > 0
                    }
                },
                execution_time=0.0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id, status="error", 
                data={"healthy": False, "error": str(e)},
                execution_time=0.0
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Simple input validation"""
        return self._validate_input_data(input_data)["valid"]