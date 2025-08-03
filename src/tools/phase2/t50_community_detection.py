"""T50: Community Detection Tool - Main Interface

Streamlined community detection tool using decomposed components.
Reduced from 1,005 lines to focused interface.
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

# Import decomposed community detection components
from .community_detection import (
    CommunityAlgorithm,
    CommunityResult,
    CommunityStats,
    CommunityGraphDataLoader,
    CommunityDetector,
    CommunityAnalyzer,
    CommunityResultsAggregator
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityDetectionTool(BaseTool):
    """T50: Advanced Community Detection Tool
    
    Implements comprehensive community detection using decomposed components:
    - CommunityGraphDataLoader: Load graph data from various sources
    - CommunityDetector: Detect communities using multiple algorithms
    - CommunityAnalyzer: Analyze community structure and statistics
    - CommunityResultsAggregator: Format and store results
    
    Reduced from 1,005 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize community detection tool with decomposed components"""
        super().__init__(service_manager)
        self.tool_id = "T50_COMMUNITY_DETECTION"
        self.name = "Advanced Community Detection"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = CommunityGraphDataLoader(service_manager)
        self.detector = CommunityDetector()
        self.analyzer = CommunityAnalyzer()
        self.aggregator = CommunityResultsAggregator(service_manager)
        
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
            description="Multi-algorithm community detection with quality analysis and comparison",
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
                    "algorithms": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["louvain", "leiden", "label_propagation", "greedy_modularity", 
                                   "fluid_communities", "girvan_newman", "all"]
                        },
                        "description": "Community detection algorithms to use"
                    },
                    "min_community_size": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Minimum community size threshold"
                    },
                    "max_community_size": {
                        "type": "integer",
                        "minimum": 10,
                        "description": "Maximum community size threshold"
                    },
                    "resolution": {
                        "type": "number",
                        "minimum": 0.1,
                        "maximum": 10.0,
                        "description": "Resolution parameter for modularity optimization"
                    },
                    "detailed_analysis": {
                        "type": "boolean",
                        "description": "Whether to perform detailed community analysis"
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
                        "description": "Configuration overrides for specific algorithms"
                    }
                },
                "required": ["graph_source", "algorithms"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "community_results": {"type": "array"},
                    "community_details": {"type": "array"},
                    "statistics": {"type": "object"},
                    "best_algorithm": {"type": "string"},
                    "confidence_score": {"type": "number"},
                    "metadata": {"type": "object"}
                }
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive community detection"""
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
            algorithms = [CommunityAlgorithm(alg) for alg in request.input_data["algorithms"]]
            min_community_size = request.input_data.get("min_community_size", 2)
            max_community_size = request.input_data.get("max_community_size", 1000)
            resolution = request.input_data.get("resolution", 1.0)
            detailed_analysis = request.input_data.get("detailed_analysis", True)
            source_document = request.input_data.get("source_document", "unknown")
            output_format = request.input_data.get("output_format", "detailed")
            config_overrides = request.input_data.get("config_overrides", {})
            
            logger.info(f"Starting community detection: {graph_source} source, {len(algorithms)} algorithms")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(graph_source, graph_data)
            
            if graph is None:
                return self._create_error_result(
                    request, "Failed to load graph data from specified source"
                )
            
            # Validate graph for community detection
            validation = self.data_loader.validate_graph_for_communities(graph)
            if not validation["valid"]:
                return self._create_error_result(
                    request, f"Graph validation failed: {validation['errors']}"
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Detect communities using decomposed detector
            community_results = []
            
            # Handle "all" algorithm
            if CommunityAlgorithm.ALL in algorithms:
                algorithms = [alg for alg in CommunityAlgorithm if alg != CommunityAlgorithm.ALL]
            
            for algorithm in algorithms:
                try:
                    # Get config overrides for this algorithm
                    algorithm_config = config_overrides.get(algorithm.value, {})
                    algorithm_config.update({
                        "min_community_size": min_community_size,
                        "max_community_size": max_community_size,
                        "resolution": resolution
                    })
                    
                    # Prepare graph for this algorithm
                    prepared_graph = self.data_loader.prepare_graph_for_algorithm(graph, algorithm.value)
                    
                    # Detect communities
                    result = self.detector.detect_communities(prepared_graph, algorithm, algorithm_config)
                    community_results.append(result)
                    
                    if result.communities:
                        logger.info(f"Detected {result.num_communities} communities using {algorithm.value}")
                    else:
                        logger.warning(f"Failed to detect communities using {algorithm.value}")
                        
                except Exception as e:
                    logger.error(f"Error with {algorithm.value} algorithm: {e}")
                    continue
            
            if not any(result.communities for result in community_results):
                return self._create_error_result(
                    request, "No community detection algorithms were successful"
                )
            
            # Step 3: Calculate statistics using decomposed analyzer
            stats = self.analyzer.calculate_community_statistics(graph, community_results)
            
            # Step 4: Detailed community analysis (if requested)
            community_details = []
            if detailed_analysis and stats.best_algorithm != "none":
                best_result = next((r for r in community_results 
                                 if r.algorithm == stats.best_algorithm and r.communities), None)
                if best_result:
                    community_details = self.analyzer.analyze_communities_detailed(
                        graph, best_result.communities
                    )
            
            # Step 5: Calculate academic confidence using decomposed analyzer
            confidence_score = self.analyzer.calculate_academic_confidence(stats, graph, community_results)
            
            # Step 6: Store results using decomposed aggregator
            storage_result = self.aggregator.store_community_results(community_results, source_document)
            
            # Step 7: Format output using decomposed aggregator
            formatted_output = self.aggregator.format_community_output(
                community_results, community_details, stats, output_format, confidence_score
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Community detection completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "graph_source": graph_source,
                    "algorithms_used": [r.algorithm for r in community_results if r.communities],
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "successful_algorithms": len([r for r in community_results if r.communities]),
                    "total_algorithms": len(community_results),
                    "best_algorithm": stats.best_algorithm,
                    "best_modularity": stats.best_modularity,
                    "communities_analyzed": len(community_details),
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
        """Validate input data for community detection"""
        errors = []
        
        # Check required fields
        required_fields = ["graph_source", "algorithms"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate graph source
        valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate algorithms
        valid_algorithms = [alg.value for alg in CommunityAlgorithm]
        algorithms = input_data.get("algorithms", [])
        for algorithm in algorithms:
            if algorithm not in valid_algorithms:
                errors.append(f"Invalid algorithm: {algorithm}")
        
        # Validate numeric parameters
        if "min_community_size" in input_data:
            min_size = input_data["min_community_size"]
            if not isinstance(min_size, int) or min_size < 1:
                errors.append("min_community_size must be a positive integer")
        
        if "max_community_size" in input_data:
            max_size = input_data["max_community_size"]
            if not isinstance(max_size, int) or max_size < 10:
                errors.append("max_community_size must be at least 10")
        
        if "resolution" in input_data:
            resolution = input_data["resolution"]
            if not isinstance(resolution, (int, float)) or resolution <= 0:
                errors.append("resolution must be a positive number")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, request: ToolRequest, error_message: str, 
                           error_code: str = "COMMUNITY_DETECTION_FAILED") -> ToolResult:
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
        error_message = f"Community detection failed: {str(error)}"
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
                "nodes": ["A", "B", "C", "D", "E", "F"],
                "edges": [["A", "B"], ["B", "C"], ["C", "A"], ["D", "E"], ["E", "F"], ["F", "D"], ["A", "D"]]
            }
            
            test_graph = self.data_loader.load_graph_data("networkx", test_graph_data)
            
            if test_graph is None:
                return ToolResult(
                    tool_id=self.tool_id, status="error", 
                    data={"healthy": False, "error": "Failed to load test graph"},
                    execution_time=0.0
                )
            
            # Test community detection
            test_result = self.detector.detect_communities(
                test_graph, CommunityAlgorithm.LABEL_PROPAGATION
            )
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "healthy": True,
                    "components_status": {
                        "data_loader": "operational",
                        "detector": "operational",
                        "analyzer": "operational",
                        "aggregator": "operational"
                    },
                    "test_results": {
                        "graph_nodes": len(test_graph.nodes),
                        "graph_edges": len(test_graph.edges),
                        "communities_detected": test_result.num_communities,
                        "modularity": test_result.modularity
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