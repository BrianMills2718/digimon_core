"""T52: Graph Clustering Tool - Main Interface

Streamlined graph clustering tool using decomposed components.
Reduced from 1,356 lines to focused interface.
"""

import time
import psutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
except ImportError:
    from core.service_manager import ServiceManager

# Import decomposed clustering components
from .clustering import (
    ClusteringAlgorithm,
    GraphDataLoader,
    ClusteringAlgorithms
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class GraphClusteringTool(BaseTool):
    """T52: Advanced Graph Clustering Tool
    
    Implements comprehensive graph clustering using decomposed components:
    - GraphDataLoader: Load graph data from various sources
    - ClusteringAlgorithms: Multiple clustering algorithm implementations
    
    Reduced from 1,356 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize clustering tool with decomposed components"""
        super().__init__(service_manager)
        self.tool_id = "T52_GRAPH_CLUSTERING"
        self.tool_name = "Graph Clustering Tool"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = GraphDataLoader(service_manager)
        self.clustering_algorithms = ClusteringAlgorithms()
        
        # Performance tracking
        self.execution_count = 0
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract for graph clustering"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.tool_name,
            description="Advanced graph clustering with multiple algorithms and quality metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "string",
                        "enum": ["neo4j", "networkx", "edge_list", "adjacency_matrix", "mock"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data for non-Neo4j sources"
                    },
                    "neo4j_config": {
                        "type": "object",
                        "description": "Neo4j configuration"
                    },
                    "clustering_algorithm": {
                        "type": "string",
                        "enum": ["spectral", "kmeans", "louvain", "leiden", "hierarchical", 
                                "dbscan", "label_propagation", "greedy_modularity", "all"],
                        "description": "Clustering algorithm to use"
                    },
                    "num_clusters": {
                        "type": "integer",
                        "minimum": 2,
                        "description": "Number of clusters (if applicable)"
                    },
                    "algorithm_params": {
                        "type": "object",
                        "description": "Algorithm-specific parameters"
                    }
                },
                "required": ["data_source", "clustering_algorithm"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "clustering_results": {"type": "array"},
                    "best_result": {"type": "object"},
                    "quality_comparison": {"type": "object"},
                    "execution_summary": {"type": "object"}
                },
                "required": ["clustering_results", "execution_summary"]
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph clustering with decomposed components"""
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
            
            # Extract parameters
            data_source = request.input_data["data_source"]
            algorithm_name = request.input_data["clustering_algorithm"]
            num_clusters = request.input_data.get("num_clusters")
            algorithm_params = request.input_data.get("algorithm_params", {})
            
            logger.info(f"Starting clustering: {data_source} source, {algorithm_name} algorithm")
            
            # Step 1: Load graph data using decomposed loader
            graph = self.data_loader.load_graph_data(request.input_data)
            
            if graph is None or len(graph.nodes) == 0:
                return self._create_error_result(
                    "Failed to load graph data or graph is empty",
                    execution_time=time.time() - start_time
                )
            
            logger.info(f"Loaded graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # Step 2: Parse clustering configuration
            clustering_config = self._parse_clustering_config(request.input_data)
            
            # Step 3: Perform clustering using decomposed algorithms
            clustering_results = self._perform_clustering(graph, algorithm_name, clustering_config)
            
            if not clustering_results:
                return self._create_error_result(
                    "No clustering results generated",
                    execution_time=time.time() - start_time
                )
            
            # Step 4: Find best result and create comparison
            best_result = self._find_best_result(clustering_results)
            quality_comparison = self._create_quality_comparison(clustering_results)
            
            # Step 5: Create execution summary
            execution_summary = self._create_execution_summary(graph, clustering_results, start_time)
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_count += 1
            logger.info(f"Clustering completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data={
                    "clustering_results": [self._result_to_dict(result) for result in clustering_results],
                    "best_result": self._result_to_dict(best_result) if best_result else None,
                    "quality_comparison": quality_comparison,
                    "execution_summary": execution_summary
                },
                metadata={
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "algorithms_run": [result.algorithm for result in clustering_results],
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "data_source": data_source,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_error(e, request, time.time() - start_time)
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate clustering input"""
        errors = []
        
        # Check required fields
        required_fields = ["data_source", "clustering_algorithm"]
        for field in required_fields:
            if field not in input_data:
                errors.append(f"{field} is required")
        
        # Validate data source
        valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix", "mock"]
        if input_data.get("data_source") not in valid_sources:
            errors.append(f"data_source must be one of: {valid_sources}")
        
        # Validate algorithm
        valid_algorithms = [alg.value for alg in ClusteringAlgorithm]
        if input_data.get("clustering_algorithm") not in valid_algorithms:
            errors.append(f"clustering_algorithm must be one of: {valid_algorithms}")
        
        # Validate num_clusters if provided
        if "num_clusters" in input_data:
            if not isinstance(input_data["num_clusters"], int) or input_data["num_clusters"] < 2:
                errors.append("num_clusters must be an integer >= 2")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _parse_clustering_config(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse clustering configuration"""
        config = input_data.get("algorithm_params", {}).copy()
        
        # Add global parameters
        if "num_clusters" in input_data:
            config["num_clusters"] = input_data["num_clusters"]
        
        # Set algorithm-specific defaults
        algorithm = input_data["clustering_algorithm"]
        
        if algorithm == "spectral":
            config.setdefault("laplacian_type", "normalized")
            config.setdefault("eigen_solver", "arpack")
            config.setdefault("max_clusters", 10)
        elif algorithm == "dbscan":
            config.setdefault("eps", 0.5)
            config.setdefault("min_samples", 5)
        elif algorithm in ["louvain", "leiden"]:
            config.setdefault("resolution", 1.0)
        
        return config
    
    def _perform_clustering(self, graph, algorithm_name: str, config: Dict[str, Any]) -> List:
        """Perform clustering using decomposed algorithms"""
        results = []
        
        if algorithm_name == "all":
            # Run all available algorithms
            algorithms_to_run = [
                ClusteringAlgorithm.LOUVAIN,
                ClusteringAlgorithm.SPECTRAL,
                ClusteringAlgorithm.LABEL_PROPAGATION,
                ClusteringAlgorithm.GREEDY_MODULARITY
            ]
        else:
            # Run specific algorithm
            try:
                algorithms_to_run = [ClusteringAlgorithm(algorithm_name)]
            except ValueError:
                logger.error(f"Unknown algorithm: {algorithm_name}")
                return []
        
        for algorithm in algorithms_to_run:
            try:
                result = self.clustering_algorithms.run_clustering(graph, algorithm, config)
                results.append(result)
                logger.info(f"Completed {algorithm.value}: {result.num_clusters} clusters, modularity={result.modularity:.3f}")
            except Exception as e:
                logger.error(f"Failed {algorithm.value}: {e}")
        
        return results
    
    def _find_best_result(self, results: List) -> Optional[Any]:
        """Find best clustering result based on modularity"""
        if not results:
            return None
        
        # Sort by modularity (higher is better)
        valid_results = [r for r in results if r.num_clusters > 0]
        if not valid_results:
            return None
        
        return max(valid_results, key=lambda x: x.modularity)
    
    def _create_quality_comparison(self, results: List) -> Dict[str, Any]:
        """Create comparison of clustering quality"""
        if not results:
            return {}
        
        comparison = {
            "algorithms_compared": len(results),
            "metrics": {},
            "rankings": {}
        }
        
        # Collect metrics
        for result in results:
            comparison["metrics"][result.algorithm] = {
                "num_clusters": result.num_clusters,
                "modularity": result.modularity,
                "execution_time": result.execution_time
            }
        
        # Create rankings
        valid_results = [r for r in results if r.num_clusters > 0]
        if valid_results:
            # Rank by modularity
            by_modularity = sorted(valid_results, key=lambda x: x.modularity, reverse=True)
            comparison["rankings"]["by_modularity"] = [r.algorithm for r in by_modularity]
            
            # Rank by speed
            by_speed = sorted(valid_results, key=lambda x: x.execution_time)
            comparison["rankings"]["by_speed"] = [r.algorithm for r in by_speed]
        
        return comparison
    
    def _create_execution_summary(self, graph, results: List, start_time: float) -> Dict[str, Any]:
        """Create execution summary"""
        return {
            "graph_stats": {
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "density": len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1) / 2) if len(graph.nodes) > 1 else 0,
                "is_connected": len(list(graph.subgraph(c) for c in nx.connected_components(graph))) == 1
            },
            "clustering_stats": {
                "algorithms_run": len(results),
                "successful_results": len([r for r in results if r.num_clusters > 0]),
                "total_execution_time": time.time() - start_time,
                "best_modularity": max([r.modularity for r in results]) if results else 0
            },
            "tool_stats": {
                "version": self.version,
                "execution_count": self.execution_count,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _result_to_dict(self, result) -> Dict[str, Any]:
        """Convert clustering result to dictionary"""
        if result is None:
            return {}
        
        return {
            "algorithm": result.algorithm,
            "num_clusters": result.num_clusters,
            "modularity": result.modularity,
            "silhouette_score": result.silhouette_score,
            "execution_time": result.execution_time,
            "clusters": [list(cluster) for cluster in result.clusters],
            "quality_metrics": result.quality_metrics,
            "metadata": result.metadata
        }
    
    def _create_error_result(self, error_message: str, execution_time: float) -> ToolResult:
        """Create error result"""
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time
            },
            execution_time=execution_time
        )
    
    def _handle_error(self, error: Exception, request: ToolRequest, execution_time: float) -> ToolResult:
        """Handle errors with detailed context"""
        error_message = f"Graph clustering failed: {str(error)}"
        logger.error(error_message, exc_info=True)
        
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_type": type(error).__name__,
                "input_data": request.input_data,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time
            },
            execution_time=execution_time
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Simple input validation"""
        return self._validate_input(input_data)["valid"]