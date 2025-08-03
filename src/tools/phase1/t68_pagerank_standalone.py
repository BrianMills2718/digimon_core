"""
T68: PageRank Calculator - Standalone Version
Calculate PageRank scores for graph entities
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not available - PageRank will use simple implementation")


class T68PageRankStandalone(BaseTool):
    """T68: PageRank Calculator - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T68_PAGERANK"
        self.damping_factor = 0.85
        self.max_iterations = 100
        self.tolerance = 1e-6
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="PageRank Calculator",
            description="Calculate PageRank scores for graph entities",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "description": "List of entities (nodes)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"}
                            }
                        }
                    },
                    "edges": {
                        "type": "array",
                        "description": "List of edges (relationships)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_id": {"type": "string"},
                                "target_id": {"type": "string"},
                                "weight": {"type": "number"}
                            }
                        }
                    },
                    "damping_factor": {
                        "type": "number",
                        "description": "PageRank damping factor",
                        "default": 0.85
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Maximum iterations",
                        "default": 100
                    }
                },
                "required": ["entities", "edges"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "pagerank_scores": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "pagerank_score": {"type": "number"},
                                "rank": {"type": "integer"}
                            }
                        }
                    },
                    "top_entities": {
                        "type": "array",
                        "description": "Top 10 entities by PageRank"
                    },
                    "convergence_info": {
                        "type": "object",
                        "properties": {
                            "iterations": {"type": "integer"},
                            "converged": {"type": "boolean"}
                        }
                    }
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_GRAPH_DATA",
                "CALCULATION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PageRank calculation"""
        self._start_execution()
        
        try:
            # Extract parameters
            entities = request.input_data.get("entities", [])
            edges = request.input_data.get("edges", [])
            damping_factor = request.input_data.get("damping_factor", self.damping_factor)
            max_iterations = request.input_data.get("max_iterations", self.max_iterations)
            
            # Validate input
            if not entities:
                return self._create_error_result(
                    "NO_GRAPH_DATA",
                    "No entities provided for PageRank calculation"
                )
            
            # Calculate PageRank
            if NETWORKX_AVAILABLE:
                scores, convergence_info = self._calculate_pagerank_networkx(
                    entities, edges, damping_factor, max_iterations
                )
            else:
                scores, convergence_info = self._calculate_pagerank_simple(
                    entities, edges, damping_factor, max_iterations
                )
            
            # Sort by PageRank score
            sorted_scores = sorted(scores, key=lambda x: x["pagerank_score"], reverse=True)
            
            # Add rank
            for i, score_entry in enumerate(sorted_scores):
                score_entry["rank"] = i + 1
            
            # Get top entities
            top_entities = sorted_scores[:10]
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="calculate_pagerank",
                inputs=[e["entity_id"] for e in entities],
                parameters={
                    "entity_count": len(entities),
                    "edge_count": len(edges),
                    "damping_factor": damping_factor
                }
            )
            
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[s["entity_id"] for s in sorted_scores],
                success=True,
                metadata={
                    "top_entity": top_entities[0]["canonical_name"] if top_entities else None,
                    "iterations": convergence_info["iterations"],
                    "converged": convergence_info["converged"]
                }
            )
            
            return self._create_success_result(
                data={
                    "pagerank_scores": sorted_scores,
                    "top_entities": top_entities,
                    "convergence_info": convergence_info
                },
                metadata={
                    "operation_id": operation_id,
                    "calculation_method": "networkx" if NETWORKX_AVAILABLE else "simple",
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in PageRank calculation: {e}", exc_info=True)
            return self._create_error_result(
                "CALCULATION_FAILED",
                f"PageRank calculation failed: {str(e)}"
            )
    
    def _calculate_pagerank_networkx(self, entities, edges, damping_factor, max_iterations):
        """Calculate PageRank using NetworkX"""
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes
        for entity in entities:
            G.add_node(entity["entity_id"], name=entity.get("canonical_name", entity["entity_id"]))
        
        # Add edges
        for edge in edges:
            G.add_edge(edge["source_id"], edge["target_id"], weight=edge.get("weight", 1.0))
        
        # Calculate PageRank
        try:
            pagerank = nx.pagerank(
                G,
                alpha=damping_factor,
                max_iter=max_iterations,
                tol=self.tolerance,
                weight='weight'
            )
            converged = True
            iterations = max_iterations  # NetworkX doesn't expose actual iterations
        except nx.PowerIterationFailedConvergence as e:
            pagerank = e.pagerank
            converged = False
            iterations = max_iterations
        
        # Format results
        scores = []
        for entity in entities:
            entity_id = entity["entity_id"]
            scores.append({
                "entity_id": entity_id,
                "canonical_name": entity.get("canonical_name", entity_id),
                "pagerank_score": pagerank.get(entity_id, 0.0)
            })
        
        return scores, {"iterations": iterations, "converged": converged}
    
    def _calculate_pagerank_simple(self, entities, edges, damping_factor, max_iterations):
        """Simple PageRank implementation without NetworkX"""
        # Create adjacency lists
        outgoing = {}
        incoming = {}
        entity_map = {}
        
        for entity in entities:
            entity_id = entity["entity_id"]
            entity_map[entity_id] = entity
            outgoing[entity_id] = []
            incoming[entity_id] = []
        
        for edge in edges:
            source = edge["source_id"]
            target = edge["target_id"]
            if source in outgoing and target in incoming:
                outgoing[source].append(target)
                incoming[target].append(source)
        
        # Initialize PageRank scores
        n = len(entities)
        scores = {e["entity_id"]: 1.0 / n for e in entities}
        
        # Power iteration
        converged = False
        for iteration in range(max_iterations):
            new_scores = {}
            
            for entity_id in scores:
                # Calculate sum of incoming PageRank
                rank_sum = 0.0
                for source in incoming[entity_id]:
                    out_count = len(outgoing[source])
                    if out_count > 0:
                        rank_sum += scores[source] / out_count
                
                # Apply damping factor
                new_scores[entity_id] = (1 - damping_factor) / n + damping_factor * rank_sum
            
            # Check convergence
            diff = sum(abs(new_scores[e] - scores[e]) for e in scores)
            if diff < self.tolerance:
                converged = True
                break
            
            scores = new_scores
        
        # Format results
        score_list = []
        for entity_id, score in scores.items():
            entity = entity_map[entity_id]
            score_list.append({
                "entity_id": entity_id,
                "canonical_name": entity.get("canonical_name", entity_id),
                "pagerank_score": score
            })
        
        return score_list, {"iterations": iteration + 1, "converged": converged}


# Test function
def test_standalone_pagerank():
    """Test the standalone PageRank calculator"""
    calculator = T68PageRankStandalone()
    print(f"✅ PageRank Calculator initialized: {calculator.tool_id}")
    print(f"NetworkX available: {NETWORKX_AVAILABLE}")
    
    # Test graph data
    test_entities = [
        {"entity_id": "e1", "canonical_name": "Joe Biden"},
        {"entity_id": "e2", "canonical_name": "United States"},
        {"entity_id": "e3", "canonical_name": "Washington D.C."},
        {"entity_id": "e4", "canonical_name": "Bill Gates"},
        {"entity_id": "e5", "canonical_name": "Microsoft"}
    ]
    
    test_edges = [
        {"source_id": "e1", "target_id": "e2", "weight": 0.9},
        {"source_id": "e1", "target_id": "e3", "weight": 0.8},
        {"source_id": "e2", "target_id": "e3", "weight": 0.7},
        {"source_id": "e4", "target_id": "e5", "weight": 0.95},
        {"source_id": "e5", "target_id": "e4", "weight": 0.6},  # Bidirectional
        {"source_id": "e2", "target_id": "e1", "weight": 0.5}   # Bidirectional
    ]
    
    request = ToolRequest(
        tool_id="T68",
        operation="calculate",
        input_data={
            "entities": test_entities,
            "edges": test_edges,
            "damping_factor": 0.85,
            "max_iterations": 100
        }
    )
    
    result = calculator.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"\nConvergence: {data['convergence_info']}")
        print(f"\nTop entities by PageRank:")
        
        for entity in data['top_entities'][:5]:
            print(f"  {entity['rank']}. {entity['canonical_name']}: {entity['pagerank_score']:.4f}")
    else:
        print(f"Error: {result.error_message}")
    
    return calculator


if __name__ == "__main__":
    test_standalone_pagerank()