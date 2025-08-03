"""
T49 Multi-hop Query Unified Tool - Main Implementation

Main tool class implementing the BaseTool interface for multi-hop graph queries.
Uses decomposed components for entity extraction, path finding, and result ranking.
"""

import logging
import time
import psutil
from datetime import datetime
from typing import Dict, Any, List

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

from .connection_manager import Neo4jConnectionManager
from .query_entity_extractor import QueryEntityExtractor
from .path_finder import PathFinder
from .result_ranker import ResultRanker
from .query_analyzer import QueryAnalyzer

logger = logging.getLogger(__name__)


class T49MultiHopQueryUnified(BaseTool):
    """
    Multi-hop Query tool for answering research questions from graph data.
    
    Features:
    - Real Neo4j multi-hop path finding
    - Query entity extraction from natural language
    - PageRank-weighted result ranking
    - Path explanation and evidence tracking
    - 1-hop, 2-hop, and 3-hop query support
    - Quality assessment and confidence scoring
    - Comprehensive error handling
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T49"
        self.name = "Multi-hop Query"
        self.category = "graph_querying"
        self.service_manager = service_manager
        self.logger = logging.getLogger("multihop_query.main_tool")
        
        # Tool configuration
        self.config = {
            "max_hops": 3,
            "result_limit": 20,
            "min_path_weight": 0.01,
            "pagerank_boost_factor": 2.0,
            "min_confidence": 0.1
        }
        
        # Initialize components
        self._initialize_components()
        
        # Execution statistics
        self.execution_stats = {
            "queries_processed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0
        }

    def _initialize_components(self):
        """Initialize all decomposed components"""
        try:
            # Connection manager for Neo4j operations
            self.connection_manager = Neo4jConnectionManager()
            
            # Entity extractor for query processing
            self.entity_extractor = QueryEntityExtractor(self.connection_manager)
            
            # Path finder for multi-hop queries
            self.path_finder = PathFinder(self.connection_manager)
            
            # Result ranker for scoring and ranking
            self.result_ranker = ResultRanker(self.config["pagerank_boost_factor"])
            
            # Query analyzer for complexity analysis
            self.query_analyzer = QueryAnalyzer()
            
            self.logger.info("Multi-hop query tool components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            # Set components to None for graceful failure handling
            self.connection_manager = None
            self.entity_extractor = None
            self.path_finder = None
            self.result_ranker = None
            self.query_analyzer = None

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute multi-hop query with real Neo4j integration"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            self.execution_stats["queries_processed"] += 1
            
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    request, ToolErrorCode.INVALID_INPUT, validation_result["error"], start_time, start_memory
                )
            
            # Check component availability
            if not self._check_components_available():
                return self._create_error_result(
                    request, ToolErrorCode.CONNECTION_ERROR, "Tool components not available", start_time, start_memory
                )
            
            # Extract query parameters
            query_text = request.input_data.get("query", request.input_data.get("query_text", ""))
            max_hops = request.parameters.get("max_hops", self.config["max_hops"])
            result_limit = request.parameters.get("result_limit", self.config["result_limit"])
            min_path_weight = request.parameters.get("min_path_weight", self.config["min_path_weight"])
            
            # Extract entities from query text
            query_entities = self.entity_extractor.extract_query_entities(query_text)
            
            # Analyze query complexity
            query_analysis = self.query_analyzer.analyze_query(query_text, query_entities)
            
            if not query_entities:
                execution_time = time.time() - start_time
                memory_used = psutil.Process().memory_info().rss - start_memory
                
                return ToolResult(
                    tool_id=self.tool_id,
                    status="success",
                    data={
                        "query_results": [],
                        "result_count": 0,
                        "confidence": 0.0,
                        "reason": "No recognizable entities found in query",
                        "query_analysis": query_analysis,
                        "suggestions": self._generate_improvement_suggestions(query_text, query_entities)
                    },
                    execution_time=execution_time,
                    memory_used=memory_used,
                    metadata={
                        "query_text": query_text,
                        "entities_extracted": 0,
                        "processing_method": "entity_extraction_only"
                    }
                )
            
            # Perform multi-hop query
            raw_results = self.path_finder.find_multihop_paths(
                query_entities, max_hops, result_limit * 2  # Get more results for better ranking
            )
            
            # Rank and filter results
            ranked_results = self.result_ranker.rank_query_results(
                raw_results, query_text, min_path_weight, self.config["min_confidence"]
            )
            
            # Limit final results
            final_results = ranked_results[:result_limit]
            
            # Calculate overall confidence
            overall_confidence = self.result_ranker.calculate_overall_confidence(final_results)
            
            # Create service mentions for top results (integration with service manager)
            self._create_service_mentions(final_results[:5], request.input_data)
            
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            # Update statistics
            self.execution_stats["successful_queries"] += 1
            self.execution_stats["total_execution_time"] += execution_time
            self.execution_stats["avg_execution_time"] = (
                self.execution_stats["total_execution_time"] / self.execution_stats["queries_processed"]
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "query_results": final_results,
                    "result_count": len(final_results),
                    "confidence": overall_confidence,
                    "processing_method": "neo4j_multihop_query",
                    "query_stats": self._get_comprehensive_stats(),
                    "extracted_entities": query_entities,
                    "query_analysis": query_analysis,
                    "path_distribution": self.path_finder.analyze_path_distribution(final_results),
                    "ranking_analysis": self.result_ranker.analyze_ranking_distribution(final_results),
                    "insights": self.query_analyzer.get_query_insights(query_analysis)
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "query_text": query_text,
                    "max_hops": max_hops,
                    "result_limit": result_limit,
                    "min_path_weight": min_path_weight,
                    "entities_found": len(query_entities),
                    "neo4j_available": True,
                    "component_status": self._get_component_status()
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            self.execution_stats["failed_queries"] += 1
            self.logger.error(f"Multi-hop query error: {str(e)}", exc_info=True)
            
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"Multi-hop query failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for multi-hop query"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        # Query text is required
        query = input_data.get("query", input_data.get("query_text", ""))
        if not query or not isinstance(query, str):
            return {"valid": False, "error": "Query text is required and must be a string"}
        
        if len(query.strip()) < 3:
            return {"valid": False, "error": "Query text must be at least 3 characters long"}
        
        if len(query) > 1000:
            return {"valid": False, "error": "Query text must be less than 1000 characters"}
        
        return {"valid": True}

    def _check_components_available(self) -> bool:
        """Check if all required components are available"""
        required_components = [
            self.connection_manager,
            self.entity_extractor,
            self.path_finder,
            self.result_ranker,
            self.query_analyzer
        ]
        
        return all(component is not None for component in required_components)

    def _create_error_result(
        self, 
        request: ToolRequest, 
        error_code: ToolErrorCode, 
        error_message: str,
        start_time: float,
        start_memory: int
    ) -> ToolResult:
        """Create standardized error result"""
        execution_time = time.time() - start_time
        memory_used = psutil.Process().memory_info().rss - start_memory
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data={},
            error_message=error_message,
            error_code=error_code,
            execution_time=execution_time,
            memory_used=memory_used
        )

    def _get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components"""
        stats = {
            "execution_stats": self.execution_stats,
            "connection_stats": {},
            "extraction_stats": {},
            "path_finding_stats": {},
            "ranking_stats": {},
            "analysis_stats": {}
        }
        
        if self.connection_manager:
            stats["connection_stats"] = self.connection_manager.get_connection_stats()
        
        if self.entity_extractor:
            stats["extraction_stats"] = self.entity_extractor.get_extraction_stats()
        
        if self.path_finder:
            stats["path_finding_stats"] = self.path_finder.get_path_finding_stats()
        
        if self.result_ranker:
            stats["ranking_stats"] = self.result_ranker.get_ranking_stats()
        
        if self.query_analyzer:
            stats["analysis_stats"] = self.query_analyzer.get_analysis_stats()
        
        return stats

    def _get_component_status(self) -> Dict[str, bool]:
        """Get status of all components"""
        return {
            "connection_manager": self.connection_manager is not None,
            "entity_extractor": self.entity_extractor is not None,
            "path_finder": self.path_finder is not None,
            "result_ranker": self.result_ranker is not None,
            "query_analyzer": self.query_analyzer is not None,
            "neo4j_connected": (
                self.connection_manager.driver is not None 
                if self.connection_manager else False
            )
        }

    def _generate_improvement_suggestions(
        self, 
        query_text: str, 
        entities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggestions for improving query results"""
        suggestions = []
        
        if not entities:
            suggestions.append("Try using specific names of people, organizations, or places")
            suggestions.append("Use proper capitalization for entity names (e.g., 'John Smith', 'Microsoft')")
            suggestions.append("Put entity names in quotes if they contain common words")
        
        if len(query_text.split()) < 5:
            suggestions.append("Try adding more context to your query")
        
        if "?" not in query_text:
            suggestions.append("Consider phrasing your query as a question")
        
        return suggestions

    def _create_service_mentions(self, top_results: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for top query results"""
        # This would integrate with the service manager to create mentions
        # For now, just log the top results
        if top_results:
            self.logger.info(f"Top {len(top_results)} query results processed for service integration")

    def get_tool_info(self) -> Dict[str, Any]:
        """Get comprehensive tool information"""
        base_info = super().get_tool_info()
        
        # Add component-specific information
        component_info = {
            "decomposed_architecture": True,
            "components": {
                "connection_manager": "Neo4j connection and session management",
                "entity_extractor": "Natural language entity extraction from queries",
                "path_finder": "Multi-hop path discovery between entities",
                "result_ranker": "PageRank-weighted result ranking and scoring",
                "query_analyzer": "Query complexity analysis and insights"
            },
            "component_status": self._get_component_status(),
            "configuration": self.config,
            "capabilities": [
                "natural_language_entity_extraction",
                "multi_hop_path_finding",
                "pagerank_weighted_ranking",
                "path_explanation_generation",
                "neo4j_graph_querying",
                "confidence_scoring",
                "query_complexity_analysis",
                "performance_monitoring"
            ]
        }
        
        return {**base_info, **component_info}

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components"""
        health_status = {
            "overall_healthy": True,
            "component_health": {},
            "issues": []
        }
        
        # Check connection manager
        if self.connection_manager:
            connection_healthy = self.connection_manager.test_connection()
            health_status["component_health"]["connection_manager"] = connection_healthy
            if not connection_healthy:
                health_status["overall_healthy"] = False
                health_status["issues"].append("Neo4j connection not available")
        else:
            health_status["overall_healthy"] = False
            health_status["issues"].append("Connection manager not initialized")
        
        # Check other components
        components = {
            "entity_extractor": self.entity_extractor,
            "path_finder": self.path_finder,
            "result_ranker": self.result_ranker,
            "query_analyzer": self.query_analyzer
        }
        
        for component_name, component in components.items():
            component_healthy = component is not None
            health_status["component_health"][component_name] = component_healthy
            if not component_healthy:
                health_status["overall_healthy"] = False
                health_status["issues"].append(f"{component_name} not initialized")
        
        return health_status

    def cleanup(self) -> bool:
        """Clean up all components and resources"""
        cleanup_success = True
        
        if self.connection_manager:
            try:
                if not self.connection_manager.cleanup():
                    cleanup_success = False
            except Exception as e:
                self.logger.error(f"Connection manager cleanup failed: {e}")
                cleanup_success = False
        
        # Reset components
        self.connection_manager = None
        self.entity_extractor = None
        self.path_finder = None
        self.result_ranker = None
        self.query_analyzer = None
        
        return cleanup_success

    def get_contract(self):
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "description": "Perform multi-hop queries on Neo4j graph to find research answers",
            "input_specification": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 1000,
                        "description": "Natural language query text"
                    },
                    "query_text": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 1000,
                        "description": "Alternative field name for query text"
                    }
                },
                "anyOf": [
                    {"required": ["query"]},
                    {"required": ["query_text"]}
                ]
            },
            "parameters": {
                "max_hops": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 3,
                    "description": "Maximum number of hops in graph traversal"
                },
                "result_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "Maximum number of results to return"
                },
                "min_path_weight": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.01,
                    "description": "Minimum path weight threshold"
                }
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "query_results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rank": {"type": "integer"},
                                "result_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "ranking_score": {"type": "number"},
                                "explanation": {"type": "string"}
                            }
                        }
                    },
                    "result_count": {"type": "integer"},
                    "confidence": {"type": "number"},
                    "query_analysis": {"type": "object"},
                    "insights": {"type": "array"}
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ],
            "query_types": [
                "path_finding",
                "entity_relationships",
                "multi_hop_traversal",
                "research_questions"
            ],
            "supported_hops": [1, 2, 3],
            "dependencies": ["neo4j"],
            "storage_backend": "neo4j",
            "version": "2.0.0",
            "architecture": "decomposed_components"
        }