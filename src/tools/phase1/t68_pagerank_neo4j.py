"""
T68: PageRank Calculator - Neo4j Version
Calculate PageRank scores for entities in Neo4j graph
REAL IMPLEMENTATION - NO MOCKS
"""

from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime
import numpy as np
from collections import defaultdict

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract

logger = logging.getLogger(__name__)


class T68PageRankNeo4j(BaseTool):
    """T68: PageRank Calculator - Uses real Neo4j for graph analysis"""
    
    def __init__(self, service_manager=None):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T68_PAGE_RANK"
        # Get Neo4j driver from service manager
        self.neo4j_driver = self.service_manager.get_neo4j_driver()
        if not self.neo4j_driver:
            raise RuntimeError("Neo4j driver required for T68 PageRank")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="PageRank Calculator",
            description="Calculate PageRank scores for entities in the knowledge graph",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "array",
                        "description": "Optional list of entity IDs to calculate PageRank for",
                        "items": {"type": "string"}
                    },
                    "damping_factor": {
                        "type": "number",
                        "description": "PageRank damping factor (default: 0.85)",
                        "default": 0.85,
                        "minimum": 0,
                        "maximum": 1
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Maximum iterations (default: 100)",
                        "default": 100,
                        "minimum": 1
                    },
                    "tolerance": {
                        "type": "number",
                        "description": "Convergence tolerance (default: 0.0001)",
                        "default": 0.0001,
                        "minimum": 0
                    },
                    "source_refs": {
                        "type": "array",
                        "description": "Source references for provenance"
                    }
                },
                "required": []
            },
            output_schema={
                "type": "object",
                "properties": {
                    "pagerank_scores": {
                        "type": "object",
                        "description": "Map of entity_id to PageRank score"
                    },
                    "top_entities": {
                        "type": "array",
                        "description": "Top entities by PageRank score",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "pagerank_score": {"type": "number"}
                            }
                        }
                    },
                    "iterations": {"type": "integer"},
                    "convergence_delta": {"type": "number"},
                    "entity_count": {"type": "integer"}
                }
            },
            dependencies=["neo4j", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 60.0,
                "max_memory_mb": 2000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES",
                "NEO4J_ERROR",
                "CONVERGENCE_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PageRank calculation on Neo4j graph"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result("INVALID_INPUT", "Input validation failed")
            
            # Extract parameters
            entity_ids = request.input_data.get("entity_ids", [])
            damping_factor = request.input_data.get("damping_factor", 0.85)
            max_iterations = request.input_data.get("max_iterations", 100)
            tolerance = request.input_data.get("tolerance", 0.0001)
            source_refs = request.input_data.get("source_refs", [])
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="calculate_pagerank",
                inputs=source_refs,
                parameters={
                    "entity_filter": len(entity_ids) if entity_ids else "all",
                    "damping_factor": damping_factor,
                    "max_iterations": max_iterations,
                    "tolerance": tolerance
                }
            )
            
            with self.neo4j_driver.session() as session:
                # Get graph structure from Neo4j
                if entity_ids:
                    # Calculate PageRank for specific entities
                    graph_data = self._get_subgraph(session, entity_ids)
                else:
                    # Calculate PageRank for entire graph
                    graph_data = self._get_full_graph(session)
                
                if not graph_data["nodes"]:
                    return self._create_error_result("NO_ENTITIES", "No entities found in graph")
                
                # Build adjacency structure
                adjacency = self._build_adjacency_list(
                    graph_data["nodes"], 
                    graph_data["edges"]
                )
                
                # Calculate PageRank
                pagerank_scores, iterations, delta = self._calculate_pagerank(
                    adjacency,
                    damping_factor,
                    max_iterations,
                    tolerance
                )
                
                # Store PageRank scores back to Neo4j
                self._store_pagerank_scores(session, pagerank_scores)
                
                # Get top entities with names
                top_entities = self._get_top_entities(session, pagerank_scores, limit=10)
                
                # Track quality for PageRank calculation
                self.quality_service.assess_confidence(
                    object_ref=f"pagerank_{operation_id}",
                    base_confidence=0.95,  # PageRank is deterministic
                    factors={
                        "algorithm": 1.0,
                        "convergence": 1.0 if delta < tolerance else 0.8,
                        "coverage": len(pagerank_scores) / len(graph_data["nodes"])
                    },
                    metadata={
                        "iterations": iterations,
                        "convergence_delta": delta,
                        "entity_count": len(pagerank_scores)
                    }
                )
            
            # Complete provenance tracking
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[f"pagerank_{entity_id}" for entity_id in pagerank_scores.keys()],
                success=True,
                metadata={
                    "iterations": iterations,
                    "convergence_delta": delta,
                    "scores_calculated": len(pagerank_scores)
                }
            )
            
            # Return success result
            return self._create_success_result(
                data={
                    "pagerank_scores": pagerank_scores,
                    "top_entities": top_entities,
                    "iterations": iterations,
                    "convergence_delta": delta,
                    "entity_count": len(pagerank_scores)
                },
                metadata={
                    "operation_id": operation_id,
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "damping_factor": damping_factor,
                        "tolerance": tolerance
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"PageRank calculation failed: {e}")
            return self._create_error_result("NEO4J_ERROR", str(e))
    
    def _get_full_graph(self, session) -> Dict[str, List]:
        """Get entire graph structure from Neo4j"""
        # Get all nodes
        nodes_result = session.run("""
            MATCH (e:Entity)
            RETURN e.entity_id as id, e.canonical_name as name
        """)
        nodes = [{"id": record["id"], "name": record["name"]} 
                 for record in nodes_result]
        
        # Get all edges
        edges_result = session.run("""
            MATCH (source:Entity)-[r:RELATES_TO]->(target:Entity)
            RETURN source.entity_id as source, target.entity_id as target, 
                   r.confidence as weight
        """)
        edges = [{"source": record["source"], 
                  "target": record["target"],
                  "weight": record["weight"] or 1.0} 
                 for record in edges_result]
        
        return {"nodes": nodes, "edges": edges}
    
    def _get_subgraph(self, session, entity_ids: List[str]) -> Dict[str, List]:
        """Get subgraph for specific entities"""
        # Get specified nodes and their neighbors
        nodes_result = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_id IN $entity_ids
            OPTIONAL MATCH (e)-[:RELATES_TO]-(neighbor:Entity)
            WITH DISTINCT e + collect(DISTINCT neighbor) as all_nodes
            UNWIND all_nodes as node
            RETURN DISTINCT node.entity_id as id, node.canonical_name as name
        """, entity_ids=entity_ids)
        nodes = [{"id": record["id"], "name": record["name"]} 
                 for record in nodes_result]
        
        node_ids = [node["id"] for node in nodes]
        
        # Get edges within this subgraph
        edges_result = session.run("""
            MATCH (source:Entity)-[r:RELATES_TO]->(target:Entity)
            WHERE source.entity_id IN $node_ids 
              AND target.entity_id IN $node_ids
            RETURN source.entity_id as source, target.entity_id as target,
                   r.confidence as weight
        """, node_ids=node_ids)
        edges = [{"source": record["source"], 
                  "target": record["target"],
                  "weight": record["weight"] or 1.0} 
                 for record in edges_result]
        
        return {"nodes": nodes, "edges": edges}
    
    def _build_adjacency_list(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, List[Tuple[str, float]]]:
        """Build adjacency list from nodes and edges"""
        adjacency = defaultdict(list)
        node_set = {node["id"] for node in nodes}
        
        # Initialize all nodes
        for node in nodes:
            adjacency[node["id"]] = []
        
        # Add edges
        for edge in edges:
            if edge["source"] in node_set and edge["target"] in node_set:
                weight = edge.get("weight", 1.0)
                adjacency[edge["source"]].append((edge["target"], weight))
        
        return dict(adjacency)
    
    def _calculate_pagerank(
        self, 
        adjacency: Dict[str, List[Tuple[str, float]]],
        damping_factor: float,
        max_iterations: int,
        tolerance: float
    ) -> Tuple[Dict[str, float], int, float]:
        """Calculate PageRank using power iteration method"""
        nodes = list(adjacency.keys())
        n = len(nodes)
        if n == 0:
            return {}, 0, 0.0
        
        # Initialize PageRank scores
        pr = {node: 1.0 / n for node in nodes}
        
        # Calculate out-degree for each node
        out_degree = {}
        for node in nodes:
            total_weight = sum(weight for _, weight in adjacency[node])
            out_degree[node] = total_weight if total_weight > 0 else 1.0
        
        # Power iteration
        for iteration in range(max_iterations):
            new_pr = {}
            
            # Calculate new PageRank for each node
            for node in nodes:
                # Random surfer component
                rank = (1 - damping_factor) / n
                
                # Incoming link component
                for source in nodes:
                    for target, weight in adjacency[source]:
                        if target == node:
                            rank += damping_factor * pr[source] * weight / out_degree[source]
                
                new_pr[node] = rank
            
            # Check convergence
            delta = sum(abs(new_pr[node] - pr[node]) for node in nodes)
            pr = new_pr
            
            if delta < tolerance:
                logger.info(f"PageRank converged after {iteration + 1} iterations")
                return pr, iteration + 1, delta
        
        logger.warning(f"PageRank did not converge after {max_iterations} iterations")
        return pr, max_iterations, delta
    
    def _store_pagerank_scores(self, session, pagerank_scores: Dict[str, float]):
        """Store PageRank scores back to Neo4j"""
        # Batch update PageRank scores
        session.run("""
            UNWIND $scores as score
            MATCH (e:Entity {entity_id: score.entity_id})
            SET e.pagerank_score = score.score,
                e.pagerank_updated = datetime()
        """, scores=[
            {"entity_id": entity_id, "score": score}
            for entity_id, score in pagerank_scores.items()
        ])
    
    def _get_top_entities(self, session, pagerank_scores: Dict[str, float], limit: int = 10) -> List[Dict]:
        """Get top entities by PageRank score with their names"""
        # Sort by PageRank score
        sorted_entities = sorted(
            pagerank_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        entity_ids = [entity_id for entity_id, _ in sorted_entities]
        
        # Get entity details from Neo4j
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_id IN $entity_ids
            RETURN e.entity_id as id, e.canonical_name as name
        """, entity_ids=entity_ids)
        
        entity_names = {record["id"]: record["name"] for record in result}
        
        # Build top entities list
        top_entities = []
        for entity_id, score in sorted_entities:
            top_entities.append({
                "entity_id": entity_id,
                "canonical_name": entity_names.get(entity_id, "Unknown"),
                "pagerank_score": score
            })
        
        return top_entities
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not isinstance(input_data, dict):
            return False
        
        # Optional entity_ids validation
        if "entity_ids" in input_data:
            if not isinstance(input_data["entity_ids"], list):
                return False
            for entity_id in input_data["entity_ids"]:
                if not isinstance(entity_id, str):
                    return False
        
        # Optional parameter validation
        if "damping_factor" in input_data:
            df = input_data["damping_factor"]
            if not isinstance(df, (int, float)) or df < 0 or df > 1:
                return False
        
        if "max_iterations" in input_data:
            mi = input_data["max_iterations"]
            if not isinstance(mi, int) or mi < 1:
                return False
        
        if "tolerance" in input_data:
            tol = input_data["tolerance"]
            if not isinstance(tol, (int, float)) or tol < 0:
                return False
        
        return True


# Test function
def test_pagerank():
    """Test the PageRank calculator with sample data"""
    from src.core.service_manager import get_service_manager
    
    service_manager = get_service_manager()
    calculator = T68PageRankNeo4j(service_manager)
    
    # First, ensure we have some test entities and relationships in Neo4j
    with service_manager.get_neo4j_driver().session() as session:
        # Create test entities if they don't exist
        session.run("""
            MERGE (a:Entity {entity_id: 'test_entity_a', canonical_name: 'Entity A'})
            MERGE (b:Entity {entity_id: 'test_entity_b', canonical_name: 'Entity B'})
            MERGE (c:Entity {entity_id: 'test_entity_c', canonical_name: 'Entity C'})
            MERGE (d:Entity {entity_id: 'test_entity_d', canonical_name: 'Entity D'})
            
            MERGE (a)-[:RELATES_TO {confidence: 0.9}]->(b)
            MERGE (b)-[:RELATES_TO {confidence: 0.8}]->(c)
            MERGE (c)-[:RELATES_TO {confidence: 0.7}]->(d)
            MERGE (d)-[:RELATES_TO {confidence: 0.6}]->(a)
            MERGE (b)-[:RELATES_TO {confidence: 0.85}]->(d)
        """)
    
    # Calculate PageRank for all entities
    request = ToolRequest(
        tool_id="T68",
        operation="calculate_pagerank",
        input_data={
            "damping_factor": 0.85,
            "max_iterations": 100,
            "tolerance": 0.0001,
            "source_refs": ["test_graph"]
        },
        parameters={}
    )
    
    result = calculator.execute(request)
    
    if result.status == "success":
        print(f"✅ PageRank calculated successfully")
        print(f"   Iterations: {result.data['iterations']}")
        print(f"   Convergence delta: {result.data['convergence_delta']:.6f}")
        print(f"   Entities processed: {result.data['entity_count']}")
        print(f"\n   Top entities by PageRank:")
        for entity in result.data['top_entities'][:5]:
            print(f"   - {entity['canonical_name']}: {entity['pagerank_score']:.4f}")
    else:
        print(f"❌ Error: {result.error_message}")
    
    # Test PageRank for specific entities
    specific_request = ToolRequest(
        tool_id="T68",
        operation="calculate_pagerank",
        input_data={
            "entity_ids": ["test_entity_a", "test_entity_b"],
            "source_refs": ["test_subgraph"]
        },
        parameters={}
    )
    
    specific_result = calculator.execute(specific_request)
    
    if specific_result.status == "success":
        print(f"\n✅ Subgraph PageRank calculated")
        print(f"   Entities in subgraph: {specific_result.data['entity_count']}")
    
    return result, specific_result


if __name__ == "__main__":
    test_pagerank()