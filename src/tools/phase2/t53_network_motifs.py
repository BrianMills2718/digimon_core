"""T53: Network Motifs Detection Tool - Main Interface

Streamlined network motifs detection tool using decomposed components.
Reduced from 1,157 lines to focused interface.
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

# Import decomposed network motifs components
from .network_motifs import (
    MotifType,
    MotifInstance,
    MotifStats,
    NetworkMotifsDataLoader,
    MotifDetector,
    StatisticalAnalyzer,
    MotifResultsAggregator
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class NetworkMotifsDetectionTool(BaseTool):
    """T53: Advanced Network Motifs Detection Tool
    
    Implements comprehensive motif detection using decomposed components:
    - NetworkMotifsDataLoader: Load graph data from various sources
    - MotifDetector: Detect various types of network motifs
    - StatisticalAnalyzer: Calculate statistical significance
    - MotifResultsAggregator: Format and store results
    
    Reduced from 1,157 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize network motifs detection tool with decomposed components"""
        super().__init__(service_manager)
        self.tool_id = "T53_NETWORK_MOTIFS"
        self.name = "Advanced Network Motifs Detection"
        self.category = "advanced_analytics"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = NetworkMotifsDataLoader(service_manager)
        self.motif_detector = MotifDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.results_aggregator = MotifResultsAggregator(service_manager)
        
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
            description="Advanced network motif detection with statistical significance testing",
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
                    "motif_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["triangles", "squares", "wedges", "feed_forward_loops", 
                                   "bi_fans", "three_chains", "four_chains", "cliques", "all"]
                        },
                        "description": "Types of motifs to detect"
                    },
                    "min_frequency": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Minimum frequency threshold for motifs"
                    },
                    "max_instances": {
                        "type": "integer",
                        "minimum": 100,
                        "maximum": 50000,
                        "description": "Maximum number of motif instances to detect"
                    },
                    "directed": {
                        "type": "boolean",
                        "description": "Whether to treat graph as directed"
                    },
                    "statistical_testing": {
                        "type": "boolean",
                        "description": "Whether to perform statistical significance testing"
                    },
                    "random_iterations": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 1000,
                        "description": "Number of random iterations for significance testing"
                    },
                    "source_document": {
                        "type": "string",
                        "description": "Source document identifier for storing results"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "academic"],
                        "description": "Output format preference"
                    }
                },
                "required": ["graph_source", "motif_types"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "motif_instances": {"type": "array"},
                    "statistics": {"type": "object"},
                    "pattern_catalog": {"type": "object"},
                    "confidence_score": {"type": "number"},
                    "metadata": {"type": "object"}
                }
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute comprehensive network motifs detection"""
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
            motif_types = [MotifType(mt) for mt in request.input_data["motif_types"]]
            min_frequency = request.input_data.get("min_frequency", 1)
            max_instances = request.input_data.get("max_instances", 10000)
            directed = request.input_data.get("directed", False)
            statistical_testing = request.input_data.get("statistical_testing", True)
            random_iterations = request.input_data.get("random_iterations", 100)
            source_document = request.input_data.get("source_document", "unknown")
            output_format = request.input_data.get("output_format", "detailed")
            
            logger.info(f"Starting motif detection: {graph_source} source, {len(motif_types)} motif types")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(graph_source, graph_data, directed)
            
            if graph is None:
                return self._create_error_result(
                    request, "Failed to load graph data from specified source"
                )
            
            # Validate graph for motif detection
            validation = self.data_loader.validate_graph_for_motifs(graph)
            if not validation["valid"]:
                return self._create_error_result(
                    request, f"Graph validation failed: {validation['errors']}"
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Detect motifs using decomposed detector
            motif_instances = self.motif_detector.detect_motifs(
                graph, motif_types, min_frequency, max_instances
            )
            
            if not motif_instances:
                return self._create_error_result(
                    request, "No motifs detected in the graph"
                )
            
            logger.info(f"Detected {len(motif_instances)} motif instances")
            
            # Step 3: Calculate statistical significance using decomposed analyzer
            if statistical_testing:
                stats = self.statistical_analyzer.calculate_motif_significance(
                    graph, motif_instances, random_iterations
                )
            else:
                stats = self.statistical_analyzer._calculate_basic_motif_stats(motif_instances)
            
            # Step 4: Generate pattern catalog using decomposed aggregator
            pattern_catalog = self.results_aggregator.generate_pattern_catalog(motif_instances)
            
            # Step 5: Calculate academic confidence using decomposed analyzer
            confidence_score = self.statistical_analyzer.calculate_academic_confidence(
                stats, graph, motif_instances
            )
            
            # Step 6: Store results in Neo4j using decomposed aggregator
            storage_success = self.results_aggregator.store_motif_results(
                motif_instances, stats, source_document
            )
            
            # Step 7: Format output using decomposed aggregator
            formatted_output = self.results_aggregator.format_output(
                motif_instances, stats, output_format, confidence_score
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Motif detection completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "graph_source": graph_source,
                    "motif_types": [mt.value for mt in motif_types],
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "motifs_detected": len(motif_instances),
                    "statistical_testing": statistical_testing,
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "confidence_score": confidence_score,
                    "storage_success": storage_success,
                    "output_format": output_format,
                    "tool_version": self.version,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for motif detection"""
        errors = []
        
        # Check required fields
        required_fields = ["graph_source", "motif_types"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate graph source
        valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
        if input_data.get("graph_source") not in valid_sources:
            errors.append(f"graph_source must be one of: {valid_sources}")
        
        # Validate motif types
        valid_motif_types = [mt.value for mt in MotifType]
        motif_types = input_data.get("motif_types", [])
        for motif_type in motif_types:
            if motif_type not in valid_motif_types:
                errors.append(f"Invalid motif type: {motif_type}")
        
        # Validate numeric parameters
        if "min_frequency" in input_data:
            if not isinstance(input_data["min_frequency"], int) or input_data["min_frequency"] < 1:
                errors.append("min_frequency must be a positive integer")
        
        if "max_instances" in input_data:
            max_inst = input_data["max_instances"]
            if not isinstance(max_inst, int) or max_inst < 100 or max_inst > 50000:
                errors.append("max_instances must be between 100 and 50000")
        
        if "random_iterations" in input_data:
            rand_iter = input_data["random_iterations"]
            if not isinstance(rand_iter, int) or rand_iter < 10 or rand_iter > 1000:
                errors.append("random_iterations must be between 10 and 1000")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_error_result(self, request: ToolRequest, error_message: str, 
                           error_code: str = "MOTIF_DETECTION_FAILED") -> ToolResult:
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
        error_message = f"Network motifs detection failed: {str(error)}"
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
            
            test_graph = self.data_loader.load_graph_data(
                "networkx", test_graph_data, False
            )
            
            if test_graph is None:
                return ToolResult(
                    tool_id=self.tool_id, status="error", 
                    data={"healthy": False, "error": "Failed to load test graph"},
                    execution_time=0.0
                )
            
            # Test motif detection
            test_motifs = self.motif_detector.detect_motifs(
                test_graph, [MotifType.TRIANGLES], 1, 100
            )
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "healthy": True,
                    "components_status": {
                        "data_loader": "operational",
                        "motif_detector": "operational", 
                        "statistical_analyzer": "operational",
                        "results_aggregator": "operational"
                    },
                    "test_results": {
                        "graph_nodes": len(test_graph.nodes),
                        "graph_edges": len(test_graph.edges),
                        "motifs_detected": len(test_motifs)
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