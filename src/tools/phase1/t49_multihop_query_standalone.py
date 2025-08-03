"""
T49: Multi-hop Query - Standalone Version
Perform multi-hop queries on the graph to answer questions
"""

from typing import Dict, Any, List, Optional, Tuple
import uuid
from datetime import datetime
import logging
import re

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T49MultiHopQueryStandalone(BaseTool):
    """T49: Multi-hop Query - works standalone without service_manager"""
    
    def __init__(self, service_manager=None):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T49_MULTIHOP_QUERY"
        # In-memory graph storage
        self.entities = {}
        self.edges = {}
        self.pagerank_scores = {}
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Multi-hop Query Engine",
            description="Perform multi-hop queries on the graph to answer questions",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "entities": {
                        "type": "array",
                        "description": "Graph entities"
                    },
                    "edges": {
                        "type": "array",
                        "description": "Graph edges"
                    },
                    "pagerank_scores": {
                        "type": "array",
                        "description": "PageRank scores for ranking"
                    },
                    "max_hops": {
                        "type": "integer",
                        "description": "Maximum number of hops",
                        "default": 2
                    },
                    "result_limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "Natural language answer"
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity": {"type": "string"},
                                "path": {"type": "array"},
                                "score": {"type": "number"},
                                "evidence": {"type": "string"}
                            }
                        }
                    },
                    "query_entities": {
                        "type": "array",
                        "description": "Entities extracted from query"
                    },
                    "paths_explored": {
                        "type": "integer",
                        "description": "Number of paths explored"
                    }
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 20.0,
                "max_memory_mb": 500
            },
            error_conditions=[
                "INVALID_QUERY",
                "NO_GRAPH_DATA",
                "QUERY_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute multi-hop query"""
        self._start_execution()
        
        try:
            # Extract parameters
            query = request.input_data.get("query", "")
            entities = request.input_data.get("entities", [])
            edges = request.input_data.get("edges", [])
            pagerank_scores = request.input_data.get("pagerank_scores", [])
            max_hops = request.input_data.get("max_hops", 2)
            result_limit = request.input_data.get("result_limit", 10)
            
            # Validate input
            if not query:
                return self._create_error_result(
                    "INVALID_QUERY",
                    "Query cannot be empty"
                )
            
            # Load graph data
            self._load_graph_data(entities, edges, pagerank_scores)
            
            if not self.entities:
                return self._create_error_result(
                    "NO_GRAPH_DATA",
                    "No graph data available for querying"
                )
            
            # Extract query entities
            query_entities = self._extract_query_entities(query)
            
            # Find matching entities in graph
            matched_entities = self._match_query_entities(query_entities)
            
            # Perform multi-hop traversal
            results = []
            paths_explored = 0
            
            for start_entity in matched_entities:
                paths = self._find_paths(start_entity, max_hops, query)
                paths_explored += len(paths)
                
                for path in paths:
                    score = self._score_path(path)
                    evidence = self._generate_evidence(path)
                    
                    results.append({
                        "entity": path[-1]["name"],
                        "path": [p["name"] for p in path],
                        "score": score,
                        "evidence": evidence
                    })
            
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:result_limit]
            
            # Generate natural language answer
            answer = self._generate_answer(query, results)
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="multi_hop_query",
                inputs=[query],
                parameters={
                    "max_hops": max_hops,
                    "result_limit": result_limit
                }
            )
            
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[r["entity"] for r in results],
                success=True,
                metadata={
                    "result_count": len(results),
                    "paths_explored": paths_explored
                }
            )
            
            return self._create_success_result(
                data={
                    "answer": answer,
                    "results": results,
                    "query_entities": query_entities,
                    "paths_explored": paths_explored
                },
                metadata={
                    "operation_id": operation_id,
                    "max_hops": max_hops,
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in multi-hop query: {e}", exc_info=True)
            return self._create_error_result(
                "QUERY_FAILED",
                f"Query execution failed: {str(e)}"
            )
    
    def _load_graph_data(self, entities, edges, pagerank_scores):
        """Load graph data into memory"""
        # Load entities
        self.entities = {}
        for entity in entities:
            entity_id = entity.get("entity_id", entity.get("id"))
            self.entities[entity_id] = {
                "id": entity_id,
                "name": entity.get("canonical_name", entity.get("name", entity_id)),
                "type": entity.get("entity_type", "UNKNOWN")
            }
        
        # Load edges
        self.edges = {}
        for edge in edges:
            edge_id = edge.get("edge_id", f"edge_{len(self.edges)}")
            self.edges[edge_id] = {
                "id": edge_id,
                "source": edge.get("source_id", edge.get("source")),
                "target": edge.get("target_id", edge.get("target")),
                "type": edge.get("relationship_type", edge.get("type", "RELATED_TO")),
                "weight": edge.get("weight", 1.0)
            }
        
        # Load PageRank scores
        self.pagerank_scores = {}
        for score_entry in pagerank_scores:
            entity_id = score_entry.get("entity_id")
            self.pagerank_scores[entity_id] = score_entry.get("pagerank_score", 0.0)
    
    def _extract_query_entities(self, query: str) -> List[str]:
        """Extract potential entity names from query"""
        entities = []
        
        # Simple entity extraction using capitalized words
        words = query.split()
        current_entity = []
        
        for word in words:
            if word[0].isupper() and word not in ['What', 'Who', 'Where', 'When', 'How', 'Which', 'The']:
                current_entity.append(word)
            elif current_entity:
                entities.append(' '.join(current_entity))
                current_entity = []
        
        if current_entity:
            entities.append(' '.join(current_entity))
        
        # Also look for quoted strings
        quoted = re.findall(r'"([^"]*)"', query)
        entities.extend(quoted)
        
        return entities
    
    def _match_query_entities(self, query_entities: List[str]) -> List[Dict]:
        """Match query entities to graph entities"""
        matched = []
        
        for query_entity in query_entities:
            query_lower = query_entity.lower()
            
            for entity_id, entity in self.entities.items():
                entity_name_lower = entity["name"].lower()
                
                # Exact match or contains
                if query_lower == entity_name_lower or query_lower in entity_name_lower:
                    matched.append({
                        "id": entity_id,
                        "name": entity["name"],
                        "type": entity["type"],
                        "match_score": 1.0 if query_lower == entity_name_lower else 0.8
                    })
        
        return matched
    
    def _find_paths(self, start_entity: Dict, max_hops: int, query: str) -> List[List[Dict]]:
        """Find paths from start entity up to max_hops"""
        paths = []
        visited = set()
        
        def dfs(current_id, current_path, hops):
            if hops > max_hops:
                return
            
            if hops > 0:  # Don't add the starting point as a result
                paths.append(list(current_path))
            
            if hops == max_hops:
                return
            
            visited.add(current_id)
            
            # Find outgoing edges
            for edge in self.edges.values():
                if edge["source"] == current_id and edge["target"] not in visited:
                    target_entity = self.entities.get(edge["target"])
                    if target_entity:
                        next_entity = {
                            "id": edge["target"],
                            "name": target_entity["name"],
                            "type": target_entity["type"],
                            "relationship": edge["type"]
                        }
                        current_path.append(next_entity)
                        dfs(edge["target"], current_path, hops + 1)
                        current_path.pop()
            
            visited.remove(current_id)
        
        # Start DFS
        initial_path = [start_entity]
        dfs(start_entity["id"], initial_path, 0)
        
        return paths
    
    def _score_path(self, path: List[Dict]) -> float:
        """Score a path based on PageRank and path length"""
        score = 0.0
        
        # Factor in PageRank scores
        for entity in path:
            pr_score = self.pagerank_scores.get(entity["id"], 0.0)
            score += pr_score
        
        # Normalize by path length (shorter paths are better)
        if len(path) > 0:
            score = score / len(path)
        
        # Boost score for certain relationship types
        for entity in path[1:]:  # Skip the first entity
            if entity.get("relationship") in ["WORKS_FOR", "LEADS", "CREATED"]:
                score *= 1.2
        
        return score
    
    def _generate_evidence(self, path: List[Dict]) -> str:
        """Generate evidence text for a path"""
        if len(path) == 1:
            return f"{path[0]['name']} is a {path[0]['type']}"
        
        evidence_parts = []
        for i in range(len(path) - 1):
            if i + 1 < len(path):
                rel = path[i + 1].get("relationship", "related to")
                evidence_parts.append(f"{path[i]['name']} {rel} {path[i + 1]['name']}")
        
        return " → ".join(evidence_parts)
    
    def _generate_answer(self, query: str, results: List[Dict]) -> str:
        """Generate natural language answer from results"""
        if not results:
            return "I couldn't find any relevant information to answer your question."
        
        query_lower = query.lower()
        
        # Determine query type
        if "who" in query_lower:
            if len(results) == 1:
                return f"{results[0]['entity']} ({results[0]['evidence']})"
            else:
                entities = [r['entity'] for r in results[:3]]
                return f"The following entities are relevant: {', '.join(entities)}"
        
        elif "what" in query_lower:
            if "relationship" in query_lower or "relation" in query_lower:
                if results:
                    return f"The relationship is: {results[0]['evidence']}"
            else:
                return f"{results[0]['entity']} - {results[0]['evidence']}"
        
        elif "where" in query_lower:
            locations = [r['entity'] for r in results if r.get('type') == 'GPE']
            if locations:
                return f"Located in: {', '.join(locations[:3])}"
            else:
                return f"Location information: {results[0]['evidence']}"
        
        elif "how many" in query_lower:
            return f"Found {len(results)} relevant results"
        
        else:
            # Default: return top result with evidence
            top_result = results[0]
            return f"{top_result['entity']}: {top_result['evidence']}"


# Test function
def test_standalone_multihop_query():
    """Test the standalone multi-hop query engine"""
    query_engine = T49MultiHopQueryStandalone()
    print(f"✅ Multi-hop Query Engine initialized: {query_engine.tool_id}")
    
    # Test graph data
    test_entities = [
        {"entity_id": "e1", "canonical_name": "Joe Biden", "entity_type": "PERSON"},
        {"entity_id": "e2", "canonical_name": "United States", "entity_type": "GPE"},
        {"entity_id": "e3", "canonical_name": "Washington D.C.", "entity_type": "GPE"},
        {"entity_id": "e4", "canonical_name": "Bill Gates", "entity_type": "PERSON"},
        {"entity_id": "e5", "canonical_name": "Microsoft", "entity_type": "ORG"}
    ]
    
    test_edges = [
        {"source_id": "e1", "target_id": "e2", "relationship_type": "WORKS_FOR", "weight": 0.9},
        {"source_id": "e1", "target_id": "e3", "relationship_type": "LOCATED_IN", "weight": 0.8},
        {"source_id": "e4", "target_id": "e5", "relationship_type": "CREATED", "weight": 0.95}
    ]
    
    test_pagerank = [
        {"entity_id": "e1", "pagerank_score": 0.15},
        {"entity_id": "e2", "pagerank_score": 0.25},
        {"entity_id": "e3", "pagerank_score": 0.20},
        {"entity_id": "e4", "pagerank_score": 0.30},
        {"entity_id": "e5", "pagerank_score": 0.35}
    ]
    
    # Test queries
    test_queries = [
        "Who is Joe Biden?",
        "Where is Joe Biden located?",
        "What did Bill Gates create?",
        "What is the relationship between Joe Biden and United States?"
    ]
    
    for test_query in test_queries:
        print(f"\n📝 Query: {test_query}")
        
        request = ToolRequest(
            tool_id="T49",
            operation="query",
            input_data={
                "query": test_query,
                "entities": test_entities,
                "edges": test_edges,
                "pagerank_scores": test_pagerank,
                "max_hops": 2,
                "result_limit": 5
            }
        )
        
        result = query_engine.execute(request)
        
        if result.status == "success":
            data = result.data
            print(f"✅ Answer: {data['answer']}")
            print(f"   Query entities: {data['query_entities']}")
            print(f"   Paths explored: {data['paths_explored']}")
            
            if data['results']:
                print("   Top results:")
                for r in data['results'][:3]:
                    print(f"     - {r['entity']} (score: {r['score']:.3f})")
                    print(f"       Path: {' → '.join(r['path'])}")
        else:
            print(f"❌ Error: {result.error_message}")
    
    return query_engine


if __name__ == "__main__":
    test_standalone_multihop_query()