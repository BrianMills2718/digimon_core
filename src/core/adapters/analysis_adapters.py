"""
Analysis Tool Adapters

Extracted from tool_adapters.py - Adapters for graph analysis and query tools.
These adapters provide analysis capabilities like PageRank and multi-hop queries.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager
from ..tool_protocol import ToolExecutionError, ToolValidationError, ToolValidationResult
from .base_adapters import BaseToolAdapter

logger = get_logger("core.adapters.analysis")


class PageRankAdapter(BaseToolAdapter):
    """Adapter for PageRank calculation"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t68_pagerank_calculator_unified import PageRankCalculatorUnified as _PageRankCalculator
            self._tool = _PageRankCalculator(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import PageRankCalculatorUnified: {e}")
            self._tool = None
            
        self.tool_name = "PageRankAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to PageRank interface"""
        if self._tool is None:
            raise ToolExecutionError("PageRankAdapter", "PageRankCalculatorUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("PageRankAdapter", validation_result.validation_errors)
        
        try:
            graph_data = input_data.get("graph_data", {})
            
            # Call PageRank calculation
            result = self._tool.calculate_pagerank(graph_data)
            
            if result.get("status") == "success":
                return {
                    "pagerank_results": result.get("pagerank_scores", {}),
                    "pagerank_metadata": result.get("metadata", {}),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("PageRank calculation failed: %s", result.get("error"))
                return {
                    "pagerank_results": {},
                    "pagerank_metadata": {"error": result.get("error")},
                    **input_data
                }
                
        except Exception as e:
            raise ToolExecutionError("PageRankAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get PageRank tool information"""
        return {
            "name": "PageRank Calculator",
            "version": "1.0",
            "description": "Calculates PageRank scores for graph nodes",
            "contract_id": "T68_PageRankCalculator",
            "capabilities": ["pagerank_calculation", "graph_analysis", "centrality_analysis"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate PageRank input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "graph_data" not in input_data:
            errors.append("Missing required field: graph_data")
        elif not isinstance(input_data["graph_data"], dict):
            errors.append("graph_data must be a dictionary")
        else:
            graph_data = input_data["graph_data"]
            if "nodes" not in graph_data and "entities" not in graph_data:
                errors.append("graph_data must contain 'nodes' or 'entities'")
            if "edges" not in graph_data and "relationships" not in graph_data:
                errors.append("graph_data must contain 'edges' or 'relationships'")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class MultiHopQueryAdapter(BaseToolAdapter):
    """Adapter for Multi-Hop Query execution"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        
        try:
            from ...tools.phase1.t49_multihop_query_unified import MultiHopQueryUnified as _MultiHopQuery
            self._tool = _MultiHopQuery(self.identity_service, self.provenance_service, self.quality_service)
        except ImportError as e:
            logger.error(f"Failed to import MultiHopQueryUnified: {e}")
            self._tool = None
            
        self.tool_name = "MultiHopQueryAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Tool protocol to MultiHopQuery interface"""
        if self._tool is None:
            raise ToolExecutionError("MultiHopQueryAdapter", "MultiHopQueryUnified not available")
            
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("MultiHopQueryAdapter", validation_result.validation_errors)
        
        try:
            query_data = input_data.get("query_data", {})
            
            # Extract query parameters
            query = query_data.get("query", "")
            max_hops = query_data.get("max_hops", 3)
            start_nodes = query_data.get("start_nodes", [])
            
            # Execute multi-hop query
            result = self._tool.execute_query(query, max_hops, start_nodes)
            
            if result.get("status") == "success":
                return {
                    "query_results": result.get("results", []),
                    "query_metadata": result.get("metadata", {}),
                    "query_paths": result.get("paths", []),
                    **input_data  # Pass through other data
                }
            else:
                logger.error("Multi-hop query failed: %s", result.get("error"))
                return {
                    "query_results": [],
                    "query_metadata": {"error": result.get("error")},
                    "query_paths": [],
                    **input_data
                }
                
        except Exception as e:
            raise ToolExecutionError("MultiHopQueryAdapter", str(e), e)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get MultiHopQuery tool information"""
        return {
            "name": "Multi-Hop Query Engine",
            "version": "1.0",
            "description": "Executes multi-hop queries across graph database",
            "contract_id": "T49_MultiHopQuery",
            "capabilities": ["multi_hop_queries", "graph_traversal", "pattern_matching"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate MultiHopQuery input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "query_data" not in input_data:
            errors.append("Missing required field: query_data")
        elif not isinstance(input_data["query_data"], dict):
            errors.append("query_data must be a dictionary")
        else:
            query_data = input_data["query_data"]
            
            # Validate query
            if "query" not in query_data:
                errors.append("query_data must contain 'query' field")
            elif not isinstance(query_data["query"], str):
                errors.append("query must be a string")
            elif len(query_data["query"].strip()) == 0:
                errors.append("query cannot be empty")
            
            # Validate max_hops if present
            if "max_hops" in query_data:
                max_hops = query_data["max_hops"]
                if not isinstance(max_hops, int):
                    errors.append("max_hops must be an integer")
                elif max_hops < 1:
                    errors.append("max_hops must be at least 1")
                elif max_hops > 10:
                    errors.append("max_hops must be at most 10 for performance reasons")
            
            # Validate start_nodes if present
            if "start_nodes" in query_data:
                start_nodes = query_data["start_nodes"]
                if not isinstance(start_nodes, list):
                    errors.append("start_nodes must be a list")
                elif len(start_nodes) > 100:
                    errors.append("start_nodes list too large (>100) for performance reasons")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )


class GraphAnalysisAdapter(BaseToolAdapter):
    """Generic adapter for graph analysis operations"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        super().__init__(config_manager)
        self.tool_name = "GraphAnalysisAdapter"
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute graph analysis operation"""
        validation_result = self.validate_input(input_data)
        if not validation_result.is_valid:
            raise ToolValidationError("GraphAnalysisAdapter", validation_result.validation_errors)
        
        try:
            analysis_type = input_data.get("analysis_type", "basic")
            graph_data = input_data.get("graph_data", {})
            
            # Perform basic graph analysis
            analysis_results = self._perform_analysis(analysis_type, graph_data)
            
            return {
                "analysis_results": analysis_results,
                "analysis_type": analysis_type,
                **input_data  # Pass through other data
            }
            
        except Exception as e:
            raise ToolExecutionError("GraphAnalysisAdapter", str(e), e)
    
    def _perform_analysis(self, analysis_type: str, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform graph analysis based on type"""
        if analysis_type == "basic":
            return self._basic_graph_analysis(graph_data)
        elif analysis_type == "centrality":
            return self._centrality_analysis(graph_data)
        elif analysis_type == "connectivity":
            return self._connectivity_analysis(graph_data)
        else:
            logger.warning(f"Unknown analysis type: {analysis_type}")
            return {"error": f"Unknown analysis type: {analysis_type}"}
    
    def _basic_graph_analysis(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic graph statistics"""
        nodes = graph_data.get("nodes", graph_data.get("entities", []))
        edges = graph_data.get("edges", graph_data.get("relationships", []))
        
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0,
            "average_degree": (2 * len(edges)) / len(nodes) if len(nodes) > 0 else 0
        }
    
    def _centrality_analysis(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic centrality analysis"""
        # This would implement centrality calculations
        # For now, return placeholder results
        return {
            "degree_centrality": {},
            "betweenness_centrality": {},
            "closeness_centrality": {},
            "note": "Centrality analysis requires full graph processing implementation"
        }
    
    def _connectivity_analysis(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic connectivity analysis"""
        # This would implement connectivity analysis
        # For now, return placeholder results
        return {
            "connected_components": 1,
            "is_connected": True,
            "diameter": 0,
            "note": "Connectivity analysis requires full graph processing implementation"
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get GraphAnalysis tool information"""
        return {
            "name": "Graph Analysis Adapter",
            "version": "1.0",
            "description": "Generic graph analysis operations",
            "contract_id": "GraphAnalysis",
            "capabilities": ["graph_statistics", "centrality_analysis", "connectivity_analysis"]
        }

    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
        """Validate GraphAnalysis input"""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")
        elif "graph_data" not in input_data:
            errors.append("Missing required field: graph_data")
        elif not isinstance(input_data["graph_data"], dict):
            errors.append("graph_data must be a dictionary")
        
        # Validate analysis type if present
        if "analysis_type" in input_data:
            analysis_type = input_data["analysis_type"]
            valid_types = ["basic", "centrality", "connectivity"]
            if analysis_type not in valid_types:
                errors.append(f"analysis_type must be one of: {', '.join(valid_types)}")
        
        return ToolValidationResult(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            method_signatures={},
            execution_test_results={},
            input_schema_validation={"valid": len(errors) == 0, "errors": errors},
            security_validation={"valid": True, "errors": []},
            performance_validation={"valid": True, "errors": []}
        )