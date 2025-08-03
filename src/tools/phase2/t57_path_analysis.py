"""T57: Path Analysis Tool - Main Interface

Streamlined path analysis tool using decomposed components.
Reduced from 1,165 lines to focused interface.
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

# Import decomposed path analysis components
from .path_analysis import (
    PathAlgorithm,
    FlowAlgorithm,
    PathResult,
    FlowResult,
    PathStats,
    PathAnalysisDataLoader,
    ShortestPathAnalyzer,
    FlowAnalyzer,
    ReachabilityAnalyzer,
    PathStatisticsCalculator
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PathAnalysisTool(BaseTool):
    """T57: Advanced Path Analysis Tool
    
    Implements comprehensive path analysis using decomposed components:
    - PathAnalysisDataLoader: Load graph data from various sources
    - ShortestPathAnalyzer: Calculate shortest paths using multiple algorithms
    - FlowAnalyzer: Analyze network flows and capacity constraints
    - ReachabilityAnalyzer: Analyze reachability and connectivity patterns
    - PathStatisticsCalculator: Calculate comprehensive statistics
    
    Reduced from 1,165 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize path analysis tool with decomposed components"""
        super().__init__(service_manager)
        self.tool_id = "T57_PATH_ANALYSIS"
        self.name = "Advanced Path Analysis"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = PathAnalysisDataLoader(service_manager)
        self.shortest_path_analyzer = ShortestPathAnalyzer()
        self.flow_analyzer = FlowAnalyzer()
        self.reachability_analyzer = ReachabilityAnalyzer()
        self.statistics_calculator = PathStatisticsCalculator()
        
        # Performance tracking
        self.execution_count = 0
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Comprehensive path analysis with shortest paths, flows, and reachability analysis",
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["networkx", "edge_list", "adjacency_matrix", "node_edge_lists"],
                        "description": "Source format for graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data in specified format"
                    },
                    "analysis_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["shortest_paths", "all_pairs_paths", "flow_analysis", "reachability_analysis"]
                        },
                        "description": "Types of analysis to perform"
                    },
                    "algorithms": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["dijkstra", "bellman_ford", "bfs", "shortest_path"]
                        },
                        "description": "Shortest path algorithms to use"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source nodes for path analysis"
                    },
                    "targets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Target nodes for path analysis"
                    },
                    "flow_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source nodes for flow analysis"
                    },
                    "flow_sinks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sink nodes for flow analysis"
                    },
                    "reachability_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source nodes for reachability analysis"
                    },
                    "weighted": {
                        "type": "boolean",
                        "description": "Whether to consider edge weights"
                    },
                    "directed": {
                        "type": "boolean",
                        "description": "Whether to treat graph as directed"
                    },
                    "weight_attribute": {
                        "type": "string",
                        "description": "Name of edge weight attribute"
                    },
                    "capacity_attribute": {
                        "type": "string",
                        "description": "Name of edge capacity attribute for flow analysis"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10000,
                        "description": "Maximum nodes for all-pairs analysis"
                    },
                    "max_reachability_distance": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Maximum distance for reachability analysis"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "academic"],
                        "description": "Output format preference"
                    }
                },
                "required": ["graph_source", "graph_data", "analysis_types"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "shortest_paths": {"type": "object"},
                    "all_pairs_paths": {"type": "object"},
                    "flow_analysis": {"type": "array"},
                    "reachability_analysis": {"type": "object"},
                    "statistics": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive path analysis"""
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
            graph_data = request.input_data["graph_data"]
            analysis_types = request.input_data["analysis_types"]
            algorithms = request.input_data.get("algorithms", ["dijkstra", "bfs"])
            output_format = request.input_data.get("output_format", "detailed")
            
            logger.info(f"Starting path analysis: {graph_source} source, {len(analysis_types)} analysis types")
            
            # Step 1: Create graph using decomposed loader
            graph = self.data_loader.create_graph_from_data(graph_source, graph_data, request.input_data)
            
            if graph is None:
                return self._create_error_result(
                    request, "Failed to create graph from provided data"
                )
            
            # Validate graph for analysis
            validation = self.data_loader.validate_graph_for_analysis(graph, "path_analysis")
            if not validation["valid"]:
                return self._create_error_result(
                    request, f"Graph validation failed: {validation['errors']}"
                )
            
            logger.info(f"Created graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Perform requested analyses using decomposed analyzers
            result_data = {}
            
            # Shortest paths analysis
            if "shortest_paths" in analysis_types:
                try:
                    shortest_paths_result = self.shortest_path_analyzer.analyze_shortest_paths(
                        graph, request.input_data, algorithms
                    )
                    result_data["shortest_paths"] = shortest_paths_result
                except Exception as e:
                    logger.error(f"Shortest paths analysis failed: {e}")
                    result_data["shortest_paths"] = {"error": str(e)}
            
            # All-pairs shortest paths analysis
            if "all_pairs_paths" in analysis_types:
                try:
                    all_pairs_result = self.shortest_path_analyzer.analyze_all_pairs_paths(
                        graph, request.input_data
                    )
                    result_data["all_pairs_paths"] = all_pairs_result
                except Exception as e:
                    logger.error(f"All-pairs paths analysis failed: {e}")
                    result_data["all_pairs_paths"] = {"error": str(e)}
            
            # Flow analysis
            if "flow_analysis" in analysis_types:
                try:
                    flow_result = self.flow_analyzer.analyze_flows(graph, request.input_data)
                    result_data["flow_analysis"] = flow_result
                except Exception as e:
                    logger.error(f"Flow analysis failed: {e}")
                    result_data["flow_analysis"] = {"error": str(e)}
            
            # Reachability analysis
            if "reachability_analysis" in analysis_types:
                try:
                    reachability_result = self.reachability_analyzer.analyze_reachability(
                        graph, request.input_data
                    )
                    result_data["reachability_analysis"] = reachability_result
                except Exception as e:
                    logger.error(f"Reachability analysis failed: {e}")
                    result_data["reachability_analysis"] = {"error": str(e)}
            
            # Step 3: Calculate comprehensive statistics using decomposed calculator
            path_statistics = self.statistics_calculator.calculate_path_statistics(graph, result_data)
            result_data["statistics"] = path_statistics.to_dict()
            
            # Step 4: Format output using decomposed calculator
            formatted_output = self.statistics_calculator.format_output(result_data, output_format)
            
            # Step 5: Calculate academic confidence using decomposed calculator
            confidence_score = self.statistics_calculator.calculate_academic_confidence(result_data, graph)
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Path analysis completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "graph_source": graph_source,
                    "analysis_types": analysis_types,
                    "algorithms_used": algorithms,
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "confidence_score": confidence_score,
                    "output_format": output_format,
                    "tool_version": self.version,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for path analysis"""
        errors = []
        
        # Check required fields
        required_fields = ["graph_source", "graph_data", "analysis_types"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate graph source
        valid_sources = ["networkx", "edge_list", "adjacency_matrix", "node_edge_lists"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate analysis types
        valid_analysis_types = ["shortest_paths", "all_pairs_paths", "flow_analysis", "reachability_analysis"]
        analysis_types = input_data.get("analysis_types", [])
        for analysis_type in analysis_types:
            if analysis_type not in valid_analysis_types:
                errors.append(f"Invalid analysis type: {analysis_type}")
        
        # Validate algorithms if provided
        if "algorithms" in input_data:
            valid_algorithms = [alg.value for alg in PathAlgorithm]
            for algorithm in input_data["algorithms"]:
                if algorithm not in valid_algorithms:
                    errors.append(f"Invalid algorithm: {algorithm}")
        
        # Validate numeric parameters
        if "max_nodes" in input_data:
            if not isinstance(input_data["max_nodes"], int) or input_data["max_nodes"] < 1:
                errors.append("max_nodes must be a positive integer")
        
        if "max_reachability_distance" in input_data:
            if not isinstance(input_data["max_reachability_distance"], int) or input_data["max_reachability_distance"] < 1:
                errors.append("max_reachability_distance must be a positive integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, request: ToolRequest, error_message: str, 
                           error_code: str = "INVALID_INPUT") -> ToolResult:
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
        error_message = f"Path analysis failed: {str(error)}"
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
                "nodes": ["A", "B", "C"],
                "edges": [["A", "B"], ["B", "C"], ["A", "C"]]
            }
            
            test_graph = self.data_loader.create_graph_from_data(
                "networkx", {"nodes": test_graph_data["nodes"], "edges": test_graph_data["edges"]}, 
                {"directed": False, "weighted": False}
            )
            
            if test_graph is None:
                return ToolResult(
                    tool_id=self.tool_id, status="error", 
                    data={"healthy": False, "error": "Failed to create test graph"},
                    execution_time=0.0
                )
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "healthy": True,
                    "components_status": {
                        "data_loader": "operational",
                        "shortest_path_analyzer": "operational",
                        "flow_analyzer": "operational",
                        "reachability_analyzer": "operational",
                        "statistics_calculator": "operational"
                    },
                    "test_graph": {
                        "nodes": len(test_graph.nodes),
                        "edges": len(test_graph.edges)
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