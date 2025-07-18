"""T68: PageRank Calculator - Minimal Implementation

Calculates PageRank centrality scores for entities in the Neo4j graph.
Key component for ranking entities by importance in the vertical slice.

Minimal implementation focusing on:
- Standard PageRank algorithm using NetworkX
- Confidence-weighted edges from Neo4j
- Entity importance scoring
- Integration with core services

Deferred features:
- Personalized PageRank variants
- Custom damping factors
- Topic-specific PageRank
- Advanced centrality measures
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import networkx as nx
import neo4j
from neo4j import GraphDatabase, Driver

# Import core services
try:
    from src.core.identity_service import IdentityService
    from src.core.provenance_service import ProvenanceService
    from src.core.quality_service import QualityService
    from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
    from src.tools.phase1.neo4j_error_handler import Neo4jErrorHandler
    from src.core.config import get_config
except ImportError:
    from core.identity_service import IdentityService
    from core.provenance_service import ProvenanceService
    from core.quality_service import QualityService
    from tools.phase1.base_neo4j_tool import BaseNeo4jTool
    from tools.phase1.neo4j_error_handler import Neo4jErrorHandler
    from core.config import get_config


class PageRankCalculator(BaseNeo4jTool):
    """T68: PageRank Calculator."""
    
    def __init__(
        self,
        identity_service: Optional[IdentityService] = None,
        provenance_service: Optional[ProvenanceService] = None,
        quality_service: Optional[QualityService] = None,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_password: str = None,
        shared_driver: Optional[Driver] = None
    ):
        # Allow tools to work standalone for testing
        if identity_service is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
            identity_service = service_manager.get_identity_service()
            provenance_service = service_manager.get_provenance_service()
            quality_service = service_manager.get_quality_service()
        
        # Initialize base class with shared driver
        super().__init__(
            identity_service=identity_service,
            provenance_service=provenance_service,
            quality_service=quality_service,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            shared_driver=shared_driver
        )
        
        self.tool_id = "T68_PAGERANK"
        
        # Load configuration for PageRank parameters
        config = get_config()
        gc = config.graph_construction
        
        # PageRank parameters from configuration
        self.damping_factor = gc.pagerank_damping_factor
        self.max_iterations = gc.pagerank_iterations
        self.tolerance = gc.pagerank_tolerance
        self.min_score = gc.pagerank_min_score
    
    
    def calculate_pagerank(
        self,
        graph_ref: str = "neo4j://graph/main",
        entity_filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate PageRank scores for entities in the graph.
        
        Args:
            graph_ref: Reference to the graph (for provenance)
            entity_filter: Optional filter for entities (e.g., entity_type)
            
        Returns:
            PageRank scores for all entities with rankings
        """
        # Start operation tracking
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="calculate_pagerank",
            inputs=[graph_ref],
            parameters={
                "damping_factor": self.damping_factor,
                "max_iterations": self.max_iterations,
                "entity_filter": entity_filter or {}
            }
        )
        
        try:
            # Input validation
            # Check Neo4j availability
            driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
            if driver_error:
                return self._complete_with_neo4j_error(operation_id, driver_error)
            
            # Load graph from Neo4j
            graph_data = self._load_graph_from_neo4j(entity_filter)
            
            if graph_data["status"] != "success":
                return self._complete_with_error(
                    operation_id,
                    f"Failed to load graph: {graph_data.get('error')}"
                )
            
            # Check if graph has enough nodes
            if graph_data["node_count"] < 2:
                return self._complete_success(
                    operation_id,
                    [],
                    f"Graph too small for PageRank (only {graph_data['node_count']} nodes)"
                )
            
            # Create NetworkX graph
            nx_graph = self._create_networkx_graph(graph_data)
            
            if nx_graph.number_of_nodes() == 0:
                return self._complete_success(
                    operation_id,
                    [],
                    "No valid nodes found for PageRank calculation"
                )
            
            # Calculate PageRank
            pagerank_scores = self._calculate_networkx_pagerank(nx_graph)
            
            # Process and rank results
            ranked_entities = self._process_pagerank_results(
                pagerank_scores, 
                graph_data["node_mapping"]
            )
            
            # Store results back to Neo4j
            storage_result = self._store_pagerank_scores(ranked_entities)
            
            # Create result references
            result_refs = []
            for entity in ranked_entities:
                pagerank_ref = f"storage://pagerank/{entity['entity_id']}"
                entity["pagerank_ref"] = pagerank_ref
                result_refs.append(pagerank_ref)
                
                # Assess PageRank quality
                quality_result = self.quality_service.assess_confidence(
                    object_ref=pagerank_ref,
                    base_confidence=0.9,  # High confidence for PageRank calculation
                    factors={
                        "score_magnitude": min(1.0, entity["pagerank_score"] * 10),  # Higher scores = higher confidence
                        "graph_connectivity": min(1.0, graph_data["edge_count"] / graph_data["node_count"]),
                        "iteration_convergence": 1.0 if pagerank_scores else 0.8
                    },
                    metadata={
                        "algorithm": "pagerank",
                        "damping_factor": self.damping_factor,
                        "graph_size": graph_data["node_count"]
                    }
                )
                
                if quality_result["status"] == "success":
                    entity["quality_confidence"] = quality_result["confidence"]
                    entity["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=result_refs,
                success=True,
                metadata={
                    "entities_ranked": len(ranked_entities),
                    "graph_nodes": graph_data["node_count"],
                    "graph_edges": graph_data["edge_count"],
                    "top_score": ranked_entities[0]["pagerank_score"] if ranked_entities else 0,
                    "algorithm_converged": bool(pagerank_scores)
                }
            )
            
            return {
                "status": "success",
                "ranked_entities": ranked_entities,
                "total_entities": len(ranked_entities),
                "graph_stats": {
                    "node_count": graph_data["node_count"],
                    "edge_count": graph_data["edge_count"],
                    "connected_components": nx.number_connected_components(nx_graph.to_undirected())
                },
                "pagerank_stats": self._calculate_pagerank_stats(ranked_entities),
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during PageRank calculation: {str(e)}"
            )
    
    def _load_graph_from_neo4j(self, entity_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Load graph structure from Neo4j."""
        try:
            with self.driver.session() as session:
                # Build entity filter conditions
                entity_conditions = []
                params = {}
                
                if entity_filter:
                    if "entity_type" in entity_filter:
                        entity_conditions.append("a.entity_type = $entity_type AND b.entity_type = $entity_type")
                        params["entity_type"] = entity_filter["entity_type"]
                    
                    if "min_confidence" in entity_filter:
                        entity_conditions.append("a.confidence >= $min_confidence AND b.confidence >= $min_confidence")
                        params["min_confidence"] = entity_filter["min_confidence"]
                
                where_clause = "WHERE " + " AND ".join(entity_conditions) if entity_conditions else ""
                
                # Optimized single query to load entire graph
                # This reduces round trips and is more efficient
                additional_conditions = " AND a.entity_id IS NOT NULL AND b.entity_id IS NOT NULL"
                where_clause_with_null_check = where_clause + additional_conditions if where_clause else "WHERE a.entity_id IS NOT NULL AND b.entity_id IS NOT NULL"
                
                # Single query that gets both nodes and relationships
                graph_query = f"""
                MATCH (a:Entity)-[r]->(b:Entity)
                {where_clause_with_null_check}
                WITH collect(DISTINCT {{
                    entity_id: a.entity_id,
                    name: a.canonical_name,
                    confidence: a.confidence,
                    entity_type: a.entity_type
                }}) + collect(DISTINCT {{
                    entity_id: b.entity_id,
                    name: b.canonical_name,
                    confidence: b.confidence,
                    entity_type: b.entity_type
                }}) as all_nodes,
                collect({{
                    source: a.entity_id,
                    target: b.entity_id,
                    weight: r.weight,
                    confidence: r.confidence,
                    relationship_type: type(r)
                }}) as all_edges
                UNWIND all_nodes as node
                WITH collect(DISTINCT node) as nodes, all_edges[0..size(all_edges)] as edges
                RETURN nodes, edges
                """
                
                result = session.run(graph_query, **params).single()
                
                if result:
                    nodes = result["nodes"]
                    edges = result["edges"]
                else:
                    nodes = []
                    edges = []
                
                # Create node mapping
                node_mapping = {}
                for i, node in enumerate(nodes):
                    node_mapping[node["entity_id"]] = {
                        "index": i,
                        "entity_id": node["entity_id"],
                        "name": node["name"],
                        "confidence": node["confidence"],
                        "entity_type": node.get("entity_type")
                    }
                
                return {
                    "status": "success",
                    "nodes": nodes,
                    "edges": edges,
                    "node_mapping": node_mapping,
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                }
                
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["connection", "network", "timeout", "unreachable", "refused"]):
                return {
                    "status": "error",
                    "error": f"Neo4j network connection error: {str(e)}. Check database connectivity and network settings."
                }
            elif any(keyword in error_msg for keyword in ["authentication", "auth", "credentials", "unauthorized"]):
                return {
                    "status": "error", 
                    "error": f"Neo4j authentication failed: {str(e)}. Verify username and password are correct."
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to load graph from Neo4j: {str(e)}"
                }
    
    def _create_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.DiGraph:
        """Create NetworkX directed graph from Neo4j data."""
        G = nx.DiGraph()
        
        # Add nodes - skip nodes with None entity_id
        for node in graph_data["nodes"]:
            entity_id = node["entity_id"]
            if entity_id is not None:
                G.add_node(
                    entity_id,
                    name=node["name"],
                    confidence=node["confidence"],
                    entity_type=node.get("entity_type")
                )
            else:
                print(f"Warning: Skipping node with None entity_id: {node.get('name', 'unknown')}")
        
        # Add edges with weights - skip edges with None source/target
        for edge in graph_data["edges"]:
            source = edge["source"]
            target = edge["target"]
            
            # Skip edges with None source or target
            if source is None or target is None:
                print(f"Warning: Skipping edge with None source/target: {source} -> {target}")
                continue
                
            # Skip edges where source or target nodes don't exist in graph
            if not G.has_node(source) or not G.has_node(target):
                print(f"Warning: Skipping edge with missing nodes: {source} -> {target}")
                continue
            
            weight = edge.get("weight", 1.0)
            # Ensure weight is positive and reasonable
            weight = max(0.01, min(1.0, weight))
            
            G.add_edge(
                source,
                target,
                weight=weight,
                confidence=edge.get("confidence", 0.5),
                relationship_type=edge.get("relationship_type", "RELATED_TO")
            )
        
        return G
    
    def _calculate_networkx_pagerank(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate PageRank using NetworkX."""
        try:
            # Use edge weights for PageRank calculation
            pagerank_scores = nx.pagerank(
                graph,
                alpha=self.damping_factor,
                max_iter=self.max_iterations,
                tol=self.tolerance,
                weight='weight'
            )
            
            return pagerank_scores
            
        except Exception as e:
            print(f"NetworkX PageRank failed: {e}")
            # Fallback: try without weights
            try:
                pagerank_scores = nx.pagerank(
                    graph,
                    alpha=self.damping_factor,
                    max_iter=self.max_iterations,
                    tol=self.tolerance
                )
                return pagerank_scores
            except Exception as e2:
                print(f"Fallback PageRank also failed: {e2}")
                return {}
    
    def _process_pagerank_results(
        self, 
        pagerank_scores: Dict[str, float], 
        node_mapping: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """Process PageRank results and create ranked entity list."""
        ranked_entities = []
        
        for entity_id, score in pagerank_scores.items():
            if entity_id in node_mapping:
                node_info = node_mapping[entity_id]
                
                entity_data = {
                    "entity_id": entity_id,
                    "canonical_name": node_info["name"],
                    "entity_type": node_info.get("entity_type"),
                    "pagerank_score": round(score, 6),
                    "entity_confidence": node_info["confidence"],
                    "calculated_at": datetime.now().isoformat()
                }
                
                ranked_entities.append(entity_data)
        
        # Sort by PageRank score (descending)
        ranked_entities.sort(key=lambda x: x["pagerank_score"], reverse=True)
        
        # Add rank information
        for i, entity in enumerate(ranked_entities):
            entity["rank"] = i + 1
            entity["percentile"] = round((len(ranked_entities) - i) / len(ranked_entities) * 100, 1)
        
        return ranked_entities
    
    def _store_pagerank_scores(self, ranked_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Store PageRank scores back to Neo4j entities."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            # Prepare batch updates
            updates = [{
                "id": entity["entity_id"],
                "score": entity["pagerank_score"],
                "rank": entity["rank"],
                "percentile": entity["percentile"],
                "calculated_at": entity["calculated_at"]
            } for entity in ranked_entities]
            
            with self.driver.session() as session:
                # Use UNWIND for batch update - much faster than individual queries
                result = session.run("""
                    UNWIND $updates as update
                    MATCH (e:Entity {entity_id: update.id})
                    SET e.pagerank_score = update.score,
                        e.pagerank_rank = update.rank,
                        e.pagerank_percentile = update.percentile,
                        e.pagerank_calculated_at = update.calculated_at
                    RETURN count(e) as updated_count
                """, updates=updates)
                
                record = result.single()
                updated_count = record["updated_count"] if record else 0
                
                return {
                    "status": "success", 
                    "entities_updated": updated_count,
                    "entities_submitted": len(ranked_entities)
                }
                
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("store_pagerank_scores", e)
    
    def _calculate_pagerank_stats(self, ranked_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics about PageRank scores."""
        if not ranked_entities:
            return {}
        
        scores = [e["pagerank_score"] for e in ranked_entities]
        
        return {
            "min_score": min(scores),
            "max_score": max(scores),
            "average_score": sum(scores) / len(scores),
            "median_score": sorted(scores)[len(scores) // 2],
            "score_distribution": {
                "high_importance": len([s for s in scores if s > 0.01]),
                "medium_importance": len([s for s in scores if 0.001 <= s <= 0.01]),
                "low_importance": len([s for s in scores if s < 0.001])
            }
        }
    
    def get_top_entities(
        self, 
        limit: int = 10,
        entity_type: str = None,
        min_score: float = None
    ) -> List[Dict[str, Any]]:
        """Get top-ranked entities from Neo4j."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable: {driver_error['message']}")
            return []
        
        try:
            with self.driver.session() as session:
                conditions = ["e.pagerank_score IS NOT NULL"]
                params = {"limit": limit}
                
                if entity_type:
                    conditions.append("e.entity_type = $entity_type")
                    params["entity_type"] = entity_type
                
                if min_score is not None:
                    conditions.append("e.pagerank_score >= $min_score")
                    params["min_score"] = min_score
                
                where_clause = "WHERE " + " AND ".join(conditions)
                
                result = session.run(f"""
                MATCH (e:Entity)
                {where_clause}
                RETURN e.entity_id as entity_id, e.canonical_name as name,
                       e.entity_type as entity_type, e.pagerank_score as score,
                       e.pagerank_rank as rank, e.pagerank_percentile as percentile
                ORDER BY e.pagerank_score DESC
                LIMIT $limit
                """, **params)
                
                return result.data()
                
        except Exception as e:
            error_result = Neo4jErrorHandler.create_operation_error("get_top_entities", e)
            print(f"Neo4j operation failed: {error_result['message']}")
            return []
    
    def _complete_with_error(self, operation_id: str, error_message: str) -> Dict[str, Any]:
        """Complete operation with error."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=[],
            success=False,
            error_message=error_message
        )
        
        return {
            "status": "error",
            "error": error_message,
            "operation_id": operation_id
        }
    
    def _complete_with_neo4j_error(self, operation_id: str, error_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Complete operation with Neo4j error following NO MOCKS policy."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=[],
            success=False,
            error_message=error_dict.get("error", "Neo4j operation failed")
        )
        
        # Return the full error dictionary from Neo4jErrorHandler
        error_dict["operation_id"] = operation_id
        return error_dict
    
    def _complete_success(self, operation_id: str, outputs: List[str], message: str) -> Dict[str, Any]:
        """Complete operation successfully with message."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=outputs,
            success=True,
            metadata={"message": message}
        )
        
        return {
            "status": "success",
            "ranked_entities": [],
            "total_entities": 0,
            "graph_stats": {},
            "pagerank_stats": {},
            "operation_id": operation_id,
            "message": message
        }
    
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the PageRank calculator - standardized interface required by tool factory"""
        if isinstance(input_data, dict):
            # Extract parameters
            entity_filter = input_data.get("entity_filter", {})
            workflow_id = input_data.get("workflow_id", "default")
        elif input_data is None:
            # Default execution
            entity_filter = {}
            workflow_id = "default"
        else:
            return {
                "status": "error",
                "error": "Input must be dict with optional 'entity_filter' key, or None for default execution"
            }
            
        return self.calculate_pagerank(entity_filter, workflow_id)

    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "PageRank Calculator",
            "version": "1.0.0",
            "description": "Calculates PageRank centrality scores for entities in Neo4j graph",
            "algorithm": "PageRank",
            "damping_factor": self.damping_factor,
            "max_iterations": self.max_iterations,
            "requires_graph": True,
            "neo4j_connected": self.driver is not None,
            "input_type": "neo4j_graph",
            "output_type": "entity_rankings"
        }

# Removed brittle alias as per CLAUDE.md CRITICAL FIX 3
# Use proper class name PageRankCalculator directly