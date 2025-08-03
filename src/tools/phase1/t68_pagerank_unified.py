from src.core.standard_config import get_database_uri
"""
T68 PageRank Calculator Unified Tool

Calculates PageRank centrality scores for entities in Neo4j graph using NetworkX.
Implements unified BaseTool interface with comprehensive PageRank analysis capabilities.
"""

import os
import uuid
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

class T68PageRankCalculatorUnified(BaseTool):
    """
    PageRank Calculator tool for ranking entities by centrality.
    
    Features:
    - Real NetworkX PageRank algorithm implementation
    - Neo4j graph loading and result storage
    - Centrality score calculation with confidence metrics
    - Graph metrics analysis and ranking
    - Quality assessment and performance tracking
    - Comprehensive error handling
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T68_PAGERANK"
        self.name = "PageRank Calculator"
        self.category = "graph_analysis"
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
        # PageRank algorithm parameters
        self.damping_factor = 0.85
        self.max_iterations = 100
        self.tolerance = 1e-6
        self.min_score = 0.0001
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # PageRank computation stats
        self.entities_processed = 0
        self.iterations_used = 0
        self.convergence_achieved = False
        self.neo4j_operations = 0

    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection"""
        if not NEO4J_AVAILABLE:
            self.logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            return
        
        try:
            # Load environment variables 
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).parent.parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Get Neo4j settings from environment or config
            neo4j_uri = get_database_uri()
            neo4j_user = os.getenv('NEO4J_USER', "neo4j")
            neo4j_password = os.getenv('NEO4J_PASSWORD')
            
            # Allow empty password for Neo4j instances without authentication
            if neo4j_password is None:
                self.logger.warning("NEO4J_PASSWORD not set, attempting connection without authentication")
                neo4j_password = ""
            
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            self.logger.info("Neo4j connection established successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PageRank calculation with real NetworkX integration"""
        self._start_execution()
        
        try:
            # Validate input
            validation_result = self._validate_input(request.input_data)
            if not validation_result["valid"]:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message=validation_result["error"],
                    error_code=ToolErrorCode.INVALID_INPUT,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            # Check dependencies
            if not NETWORKX_AVAILABLE:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message="NetworkX not available. Install with: pip install networkx",
                    error_code=ToolErrorCode.PROCESSING_ERROR,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            if not self.driver:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_message="Neo4j connection not available",
                    error_code=ToolErrorCode.CONNECTION_ERROR,
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            # Extract parameters
            graph_ref = request.input_data.get("graph_ref", "neo4j://graph/main")
            entity_types = request.parameters.get("entity_types", None)
            min_degree = request.parameters.get("min_degree", 1)
            result_limit = request.parameters.get("result_limit", 100)
            
            # Load graph from Neo4j
            graph_data = self._load_graph_from_neo4j(entity_types, min_degree)
            
            if graph_data["node_count"] < 2:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="success",
                    data={
                        "ranked_entities": [],
                        "pagerank_scores": {},
                        "entity_count": 0,
                        "reason": f"Graph too small for PageRank (only {graph_data['node_count']} nodes)"
                    },
                    execution_time=execution_time,
                    memory_used=memory_used,
                    metadata={
                        "graph_ref": graph_ref,
                        "node_count": graph_data["node_count"],
                        "edge_count": graph_data["edge_count"]
                    }
                )
            
            # Build NetworkX graph
            nx_graph = self._build_networkx_graph(graph_data)
            
            # Calculate PageRank scores
            pagerank_scores = self._calculate_pagerank_scores(nx_graph)
            
            # Rank and format results
            ranked_entities = self._rank_entities(pagerank_scores, graph_data, result_limit)
            
            # Store results back to Neo4j
            storage_result = self._store_pagerank_scores(pagerank_scores)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(ranked_entities)
            
            # Create service mentions for top-ranked entities
            self._create_service_mentions(ranked_entities[:10], request.input_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "ranked_entities": ranked_entities,
                    "pagerank_scores": pagerank_scores,
                    "entity_count": len(ranked_entities),
                    "node_count": graph_data["node_count"],  # FIX: Add node_count for consistency
                    "top_entities": ranked_entities[:10],  # FIX: Add top_entities for easier access
                    "confidence": overall_confidence,
                    "processing_method": "networkx_pagerank",
                    "computation_stats": {
                        "entities_processed": self.entities_processed,
                        "iterations_used": self.iterations_used,
                        "convergence_achieved": self.convergence_achieved,
                        "neo4j_operations": self.neo4j_operations
                    },
                    "graph_metrics": self._analyze_graph_metrics(nx_graph),
                    "score_distribution": self._analyze_score_distribution(pagerank_scores),
                    "storage_result": storage_result
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "graph_ref": graph_ref,
                    "algorithm_params": {
                        "damping_factor": self.damping_factor,
                        "max_iterations": self.max_iterations,
                        "tolerance": self.tolerance
                    },
                    "node_count": graph_data["node_count"],
                    "edge_count": graph_data["edge_count"],
                    "networkx_available": True,
                    "neo4j_available": self.driver is not None
                }
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            self.logger.error(f"PageRank calculation error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"PageRank calculation failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for PageRank calculation"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        # Graph reference is optional - defaults to main graph
        graph_ref = input_data.get("graph_ref", "neo4j://graph/main")
        if not isinstance(graph_ref, str):
            return {"valid": False, "error": "Graph reference must be a string"}
        
        return {"valid": True}

    def _load_graph_from_neo4j(
        self, 
        entity_types: Optional[List[str]] = None, 
        min_degree: int = 1
    ) -> Dict[str, Any]:
        """Load graph data from Neo4j"""
        if not self.driver:
            return {"nodes": {}, "edges": [], "node_count": 0, "edge_count": 0}
        
        try:
            with self.driver.session() as session:
                # Build entity type filter
                type_filter = ""
                params = {"min_degree": min_degree}
                
                if entity_types:
                    type_filter = "WHERE n.entity_type IN $entity_types"
                    params["entity_types"] = entity_types
                
                # Load nodes and edges in a single query
                cypher = f"""
                MATCH (n:Entity)-[r:RELATED_TO]->(m:Entity)
                {type_filter}
                WITH n, m, r, 
                     count{{(n)-[:RELATED_TO]-()}} as n_degree,
                     count{{(m)-[:RELATED_TO]-()}} as m_degree
                WHERE n_degree >= $min_degree AND m_degree >= $min_degree
                RETURN 
                    n.entity_id as source_id,
                    n.canonical_name as source_name,
                    n.entity_type as source_type,
                    n.confidence as source_confidence,
                    m.entity_id as target_id,
                    m.canonical_name as target_name,
                    m.entity_type as target_type,
                    m.confidence as target_confidence,
                    r.weight as edge_weight,
                    r.confidence as edge_confidence
                """
                
                result = session.run(cypher, **params)
                
                nodes = {}
                edges = []
                
                for record in result:
                    # Add source node
                    source_id = record["source_id"]
                    if source_id not in nodes:
                        nodes[source_id] = {
                            "entity_id": source_id,
                            "name": record["source_name"],
                            "entity_type": record["source_type"],
                            "confidence": record["source_confidence"] or 0.5
                        }
                    
                    # Add target node
                    target_id = record["target_id"]
                    if target_id not in nodes:
                        nodes[target_id] = {
                            "entity_id": target_id,
                            "name": record["target_name"],
                            "entity_type": record["target_type"],
                            "confidence": record["target_confidence"] or 0.5
                        }
                    
                    # Add edge
                    edges.append({
                        "source": source_id,
                        "target": target_id,
                        "weight": record["edge_weight"] or 1.0,
                        "confidence": record["edge_confidence"] or 0.5
                    })
                
                self.neo4j_operations += 1
                
                return {
                    "nodes": nodes,
                    "edges": edges,
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to load graph from Neo4j: {e}")
            return {"nodes": {}, "edges": [], "node_count": 0, "edge_count": 0}

    def _build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.DiGraph:
        """Build NetworkX graph from graph data"""
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node_id, node_data in graph_data["nodes"].items():
            G.add_node(node_id, **node_data)
        
        # Add edges with weights
        for edge in graph_data["edges"]:
            G.add_edge(
                edge["source"], 
                edge["target"], 
                weight=edge["weight"],
                confidence=edge["confidence"]
            )
        
        self.logger.info(f"Built NetworkX graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G

    def _calculate_pagerank_scores(self, nx_graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate PageRank scores using NetworkX"""
        try:
            pagerank_scores = nx.pagerank(
                nx_graph,
                alpha=self.damping_factor,
                max_iter=self.max_iterations,
                tol=self.tolerance,
                weight='weight'
            )
            
            # Track computation stats
            self.entities_processed = len(pagerank_scores)
            self.convergence_achieved = True  # NetworkX handles convergence
            
            # Filter out very low scores
            filtered_scores = {
                entity_id: score for entity_id, score in pagerank_scores.items()
                if score >= self.min_score
            }
            
            self.logger.info(f"Calculated PageRank for {len(filtered_scores)} entities")
            return filtered_scores
            
        except Exception as e:
            self.logger.error(f"PageRank calculation failed: {e}")
            return {}

    def _rank_entities(
        self, 
        pagerank_scores: Dict[str, float], 
        graph_data: Dict[str, Any], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Rank entities by PageRank scores"""
        ranked_entities = []
        
        # Sort by PageRank score descending
        sorted_entities = sorted(
            pagerank_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        for rank, (entity_id, pagerank_score) in enumerate(sorted_entities, 1):
            node_data = graph_data["nodes"].get(entity_id, {})
            
            # Calculate confidence based on PageRank score and entity confidence
            confidence = self._calculate_pagerank_confidence(
                pagerank_score, 
                node_data.get("confidence", 0.5)
            )
            
            entity_data = {
                "rank": rank,
                "entity_id": entity_id,
                "canonical_name": node_data.get("name", "Unknown"),
                "entity_type": node_data.get("entity_type", "UNKNOWN"),
                "pagerank_score": round(pagerank_score, 6),
                "confidence": confidence,
                "base_confidence": node_data.get("confidence", 0.5),
                "percentile": self._calculate_percentile(pagerank_score, pagerank_scores),
                "created_at": datetime.now().isoformat()
            }
            
            ranked_entities.append(entity_data)
        
        return ranked_entities

    def _calculate_pagerank_confidence(self, pagerank_score: float, base_confidence: float) -> float:
        """Calculate confidence score for PageRank results"""
        # Combine PageRank score with base entity confidence
        pagerank_weight = 0.7
        base_weight = 0.3
        
        # Normalize PageRank score (typical range is 0.0001 to 0.01+ for large graphs)
        normalized_pagerank = min(1.0, pagerank_score * 1000)  # Scale up small scores
        
        confidence = (pagerank_weight * normalized_pagerank) + (base_weight * base_confidence)
        return min(1.0, max(0.1, confidence))

    def _calculate_percentile(self, score: float, all_scores: Dict[str, float]) -> float:
        """Calculate percentile rank for a score"""
        if not all_scores:
            return 0.0
        
        scores_list = list(all_scores.values())
        scores_list.sort()
        
        rank = sum(1 for s in scores_list if s <= score)
        percentile = (rank / len(scores_list)) * 100
        return round(percentile, 2)

    def _store_pagerank_scores(self, pagerank_scores: Dict[str, float]) -> Dict[str, Any]:
        """Store PageRank scores back to Neo4j"""
        if not self.driver or not pagerank_scores:
            return {"status": "skipped", "reason": "No driver or scores"}
        
        try:
            with self.driver.session() as session:
                # Update entity nodes with PageRank scores
                cypher = """
                UNWIND $scores AS score_data
                MATCH (e:Entity {entity_id: score_data.entity_id})
                SET e.pagerank_score = score_data.score,
                    e.pagerank_updated = $timestamp
                RETURN count(e) as updated_count
                """
                
                score_data = [
                    {"entity_id": entity_id, "score": score}
                    for entity_id, score in pagerank_scores.items()
                ]
                
                result = session.run(
                    cypher, 
                    scores=score_data, 
                    timestamp=datetime.now().isoformat()
                )
                
                updated_count = result.single()["updated_count"]
                self.neo4j_operations += 1
                
                return {
                    "status": "success",
                    "updated_count": updated_count,
                    "total_scores": len(pagerank_scores)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to store PageRank scores: {e}")
            return {"status": "error", "error": str(e)}

    def _analyze_graph_metrics(self, nx_graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze graph metrics"""
        try:
            metrics = {
                "node_count": nx_graph.number_of_nodes(),
                "edge_count": nx_graph.number_of_edges(),
                "density": nx.density(nx_graph),
                "is_connected": nx.is_weakly_connected(nx_graph),
                "average_degree": sum(dict(nx_graph.degree()).values()) / nx_graph.number_of_nodes() if nx_graph.number_of_nodes() > 0 else 0
            }
            
            # Calculate additional metrics if graph is not too large
            if nx_graph.number_of_nodes() < 1000:
                try:
                    metrics["average_clustering"] = nx.average_clustering(nx_graph.to_undirected())
                except:
                    metrics["average_clustering"] = 0.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Graph metrics calculation failed: {e}")
            return {}

    def _analyze_score_distribution(self, pagerank_scores: Dict[str, float]) -> Dict[str, Any]:
        """Analyze PageRank score distribution"""
        if not pagerank_scores:
            return {}
        
        scores = list(pagerank_scores.values())
        scores.sort(reverse=True)
        
        return {
            "min_score": min(scores),
            "max_score": max(scores),
            "mean_score": sum(scores) / len(scores),
            "median_score": scores[len(scores) // 2],
            "score_ranges": {
                "top_10_percent": len([s for s in scores if s >= scores[len(scores) // 10]]),
                "top_25_percent": len([s for s in scores if s >= scores[len(scores) // 4]]),
                "bottom_50_percent": len([s for s in scores if s <= scores[len(scores) // 2]])
            }
        }

    def _calculate_overall_confidence(self, ranked_entities: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for PageRank results"""
        if not ranked_entities:
            return 0.0
        
        # Weight confidence by rank (higher ranked entities have more impact)
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for entity in ranked_entities:
            rank_weight = 1.0 / entity["rank"]  # Higher rank = higher weight
            weighted_confidence += entity["confidence"] * rank_weight
            total_weight += rank_weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _create_service_mentions(self, top_entities: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for top-ranked entities (placeholder for service integration)"""
        # This would integrate with the service manager to create mentions
        # For now, just log the top entities
        if top_entities:
            self.logger.info(f"Top {len(top_entities)} entities by PageRank calculated")

    def get_pagerank_stats(self) -> Dict[str, Any]:
        """Get PageRank computation statistics"""
        return {
            "entities_processed": self.entities_processed,
            "iterations_used": self.iterations_used,
            "convergence_achieved": self.convergence_achieved,
            "neo4j_operations": self.neo4j_operations,
            "algorithm_params": {
                "damping_factor": self.damping_factor,
                "max_iterations": self.max_iterations,
                "tolerance": self.tolerance,
                "min_score": self.min_score
            }
        }

    def get_top_entities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top entities by PageRank from Neo4j"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                cypher = """
                MATCH (e:Entity)
                WHERE e.pagerank_score IS NOT NULL
                RETURN e.entity_id as entity_id,
                       e.canonical_name as name,
                       e.entity_type as entity_type,
                       e.pagerank_score as pagerank_score,
                       e.confidence as confidence
                ORDER BY e.pagerank_score DESC
                LIMIT $limit
                """
                
                result = session.run(cypher, limit=limit)
                
                entities = []
                for rank, record in enumerate(result, 1):
                    entities.append({
                        "rank": rank,
                        "entity_id": record["entity_id"],
                        "canonical_name": record["name"],
                        "entity_type": record["entity_type"],
                        "pagerank_score": record["pagerank_score"],
                        "confidence": record["confidence"]
                    })
                
                return entities
                
        except Exception as e:
            self.logger.error(f"Failed to get top entities: {e}")
            return []

    def cleanup(self) -> bool:
        """Clean up Neo4j connection"""
        if self.driver:
            try:
                self.driver.close()
                self.driver = None
                return True
            except Exception as e:
                self.logger.error(f"Failed to close Neo4j driver: {e}")
                return False
        return True

    def get_contract(self):
        """Return tool contract specification"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "description": "Calculate PageRank centrality scores for entities in Neo4j graph",
            "input_specification": {
                "type": "object",
                "properties": {
                    "graph_ref": {
                        "type": "string",
                        "description": "Reference to the graph to analyze",
                        "default": "neo4j://graph/main"
                    }
                },
                "required": []
            },
            "parameters": {
                "entity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter entities by type (optional)"
                },
                "min_degree": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "Minimum degree for entities to include"
                },
                "result_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 100,
                    "description": "Maximum number of results to return"
                }
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "ranked_entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rank": {"type": "integer"},
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "pagerank_score": {"type": "number"},
                                "confidence": {"type": "number"},
                                "percentile": {"type": "number"}
                            }
                        }
                    },
                    "entity_count": {"type": "integer"},
                    "confidence": {"type": "number"}
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ],
            "algorithm_info": {
                "algorithm": "PageRank",
                "implementation": "NetworkX",
                "damping_factor": self.damping_factor,
                "max_iterations": self.max_iterations,
                "tolerance": self.tolerance
            },
            "dependencies": ["networkx", "neo4j"],
            "storage_backend": "neo4j"
        }

    def calculate_pagerank(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, Any]:
        """MCP-compatible method for calculating PageRank"""
        from src.tools.base_tool import ToolRequest
        
        request = ToolRequest(
            tool_id=self.tool_id,
            operation="calculate_pagerank",
            input_data={},
            parameters={
                "damping_factor": damping_factor,
                "max_iterations": max_iterations,
                "tolerance": tolerance
            }
        )
        
        result = self.execute(request)
        if result.status == "success":
            return result.data
        else:
            return {"error": result.error_message, "error_code": result.error_code}