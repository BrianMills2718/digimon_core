"""
T49: Multi-hop Query Engine - Neo4j Version
Perform multi-hop queries on Neo4j graph
REAL IMPLEMENTATION - NO MOCKS
FIXED: Entity extraction strips punctuation
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime
import re
from collections import defaultdict

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract

logger = logging.getLogger(__name__)


class T49MultiHopQueryNeo4j(BaseTool):
    """T49: Multi-hop Query Engine - Uses real Neo4j for graph queries"""
    
    def __init__(self, service_manager=None):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T49_MULTI_HOP_QUERY"
        # Get Neo4j driver from service manager
        self.neo4j_driver = self.service_manager.get_neo4j_driver()
        if not self.neo4j_driver:
            raise RuntimeError("Neo4j driver required for T49 Query Engine")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Multi-hop Query Engine",
            description="Perform multi-hop queries on the knowledge graph",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query",
                        "minLength": 1
                    },
                    "max_hops": {
                        "type": "integer",
                        "description": "Maximum number of hops (default: 2)",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 3
                    },
                    "result_limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "entity_types": {
                        "type": "array",
                        "description": "Filter results by entity types",
                        "items": {"type": "string"}
                    },
                    "source_refs": {
                        "type": "array",
                        "description": "Source references for provenance"
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "description": "Query results with paths and scores",
                        "items": {
                            "type": "object",
                            "properties": {
                                "answer": {"type": "string"},
                                "confidence": {"type": "number"},
                                "path": {"type": "array"},
                                "evidence": {"type": "string"},
                                "hops": {"type": "integer"}
                            }
                        }
                    },
                    "query_entities": {
                        "type": "array",
                        "description": "Entities extracted from query"
                    },
                    "total_paths_found": {"type": "integer"},
                    "execution_time": {"type": "number"}
                }
            },
            dependencies=["neo4j", "identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_INPUT",
                "NO_ENTITIES_IN_QUERY",
                "NO_RESULTS_FOUND",
                "NEO4J_ERROR",
                "QUERY_TIMEOUT"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute multi-hop query on Neo4j graph"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result("INVALID_INPUT", "Input validation failed")
            
            # Extract parameters
            query = request.input_data.get("query", "").strip()
            max_hops = request.input_data.get("max_hops", 2)
            result_limit = request.input_data.get("result_limit", 10)
            entity_types = request.input_data.get("entity_types", [])
            source_refs = request.input_data.get("source_refs", [])
            
            if not query:
                return self._create_error_result("INVALID_INPUT", "Query cannot be empty")
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="multi_hop_query",
                inputs=source_refs,
                parameters={
                    "query": query,
                    "max_hops": max_hops,
                    "result_limit": result_limit,
                    "entity_types": entity_types
                }
            )
            
            # Extract entities from query - FIXED: Remove punctuation
            query_entities = self._extract_query_entities(query)
            
            if not query_entities:
                return self._create_error_result(
                    "NO_ENTITIES_IN_QUERY", 
                    "No recognizable entities found in query"
                )
            
            # Perform multi-hop query
            results = []
            total_paths = 0
            
            with self.neo4j_driver.session() as session:
                # Try different hop counts
                for hop_count in range(1, max_hops + 1):
                    hop_results = self._query_with_hops(
                        session, 
                        query_entities, 
                        hop_count,
                        entity_types,
                        result_limit
                    )
                    
                    for result in hop_results:
                        # Calculate confidence based on path and PageRank
                        confidence = self._calculate_result_confidence(
                            result["path"],
                            result.get("pagerank_scores", [])
                        )
                        
                        # Format result
                        formatted_result = {
                            "answer": result["answer"],
                            "confidence": confidence,
                            "path": self._format_path(result["path"]),
                            "evidence": result.get("evidence", "Direct relationship"),
                            "hops": hop_count
                        }
                        
                        results.append(formatted_result)
                        total_paths += 1
                    
                    # Stop if we have enough results
                    if len(results) >= result_limit:
                        break
            
            # Sort results by confidence
            results = sorted(results, key=lambda x: x["confidence"], reverse=True)
            results = results[:result_limit]
            
            # Track quality for query
            self.quality_service.assess_confidence(
                object_ref=f"query_{operation_id}",
                base_confidence=0.85,
                factors={
                    "entity_recognition": 0.9 if query_entities else 0.0,
                    "path_quality": 0.8 if results else 0.0,
                    "result_diversity": min(1.0, len(results) / 5.0)
                },
                metadata={
                    "query": query,
                    "entities_found": len(query_entities),
                    "results_count": len(results)
                }
            )
            
            # Complete provenance tracking
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[f"result_{i}" for i in range(len(results))],
                success=True,
                metadata={
                    "query_entities": query_entities,
                    "total_results": len(results),
                    "total_paths": total_paths
                }
            )
            
            # Return results
            return self._create_success_result(
                data={
                    "results": results,
                    "query_entities": query_entities,
                    "total_paths_found": total_paths,
                    "execution_time": 0.0
                },
                metadata={
                    "operation_id": operation_id,
                    "timestamp": datetime.now().isoformat(),
                    "query_parameters": {
                        "max_hops": max_hops,
                        "result_limit": result_limit
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return self._create_error_result("NEO4J_ERROR", str(e))
    
    def _extract_query_entities(self, query: str) -> List[str]:
        """Extract entities from natural language query
        FIXED: Strips punctuation from extracted entities
        """
        entities = []
        
        # Simple entity extraction - find capitalized words
        # This is where LLM extraction would improve accuracy
        words = query.split()
        
        # Pattern to match capitalized words/phrases
        i = 0
        while i < len(words):
            # Check if word starts with capital letter
            word = words[i]
            # Remove trailing punctuation (?, !, ., ,, etc.)
            clean_word = re.sub(r'[^\w\s-]', '', word)
            
            if clean_word and clean_word[0].isupper():
                # Start of potential entity
                entity_parts = [clean_word]
                
                # Check if next words are also capitalized (multi-word entity)
                j = i + 1
                while j < len(words):
                    next_word = words[j]
                    clean_next = re.sub(r'[^\w\s-]', '', next_word)
                    
                    if clean_next and clean_next[0].isupper():
                        entity_parts.append(clean_next)
                        j += 1
                    else:
                        break
                
                # Join multi-word entity
                entity = " ".join(entity_parts)
                if entity and entity not in ["What", "Who", "Where", "When", "How", "Why", "Which"]:
                    entities.append(entity)
                
                i = j
            else:
                i += 1
        
        # Also check for entities in quotes
        quoted_entities = re.findall(r'"([^"]*)"', query)
        for entity in quoted_entities:
            if entity.strip():
                entities.append(entity.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        
        logger.info(f"Extracted entities from query: {unique_entities}")
        return unique_entities
    
    def _query_with_hops(
        self, 
        session, 
        query_entities: List[str],
        hop_count: int,
        entity_types: List[str],
        limit: int
    ) -> List[Dict]:
        """Perform multi-hop query with specified hop count"""
        results = []
        
        # Build entity filter
        entity_filter = ""
        if entity_types:
            entity_filter = f"AND target.entity_type IN {entity_types}"
        
        # Perform query based on hop count
        if hop_count == 1:
            # Direct relationships (with fuzzy matching)
            query = f"""
            MATCH (source:Entity)-[r:RELATES_TO]->(target:Entity)
            WHERE ANY(entity IN $entities WHERE 
                      toLower(source.canonical_name) CONTAINS toLower(entity) OR
                      toLower(entity) CONTAINS toLower(source.canonical_name))
            {entity_filter}
            RETURN source.canonical_name as source,
                   target.canonical_name as answer,
                   target.entity_id as target_id,
                   r.confidence as confidence,
                   r.evidence as evidence,
                   target.pagerank_score as pagerank,
                   [source.canonical_name, target.canonical_name] as path
            ORDER BY r.confidence DESC, target.pagerank_score DESC
            LIMIT $limit
            """
            
            result = session.run(
                query,
                entities=query_entities,
                limit=limit
            )
            
            for record in result:
                results.append({
                    "answer": record["answer"],
                    "path": record["path"],
                    "confidence": record["confidence"] or 0.5,
                    "evidence": record["evidence"] or "Direct relationship",
                    "pagerank_scores": [0.0, record["pagerank"] or 0.0]
                })
        
        elif hop_count == 2:
            # Two-hop relationships (with fuzzy matching)
            query = f"""
            MATCH (source:Entity)-[r1:RELATES_TO]->(middle:Entity)-[r2:RELATES_TO]->(target:Entity)
            WHERE ANY(entity IN $entities WHERE 
                      toLower(source.canonical_name) CONTAINS toLower(entity) OR
                      toLower(entity) CONTAINS toLower(source.canonical_name))
            {entity_filter}
            WITH source, middle, target, r1, r2,
                 (r1.confidence + r2.confidence) / 2 as avg_confidence,
                 target.pagerank_score as pagerank
            RETURN source.canonical_name as source,
                   target.canonical_name as answer,
                   target.entity_id as target_id,
                   avg_confidence as confidence,
                   middle.canonical_name as middle,
                   pagerank,
                   [source.canonical_name, middle.canonical_name, target.canonical_name] as path
            ORDER BY avg_confidence DESC, pagerank DESC
            LIMIT $limit
            """
            
            result = session.run(
                query,
                entities=query_entities,
                limit=limit
            )
            
            for record in result:
                results.append({
                    "answer": record["answer"],
                    "path": record["path"],
                    "confidence": record["confidence"] or 0.5,
                    "evidence": f"Connected via {record['middle']}",
                    "pagerank_scores": [0.0, 0.0, record["pagerank"] or 0.0]
                })
        
        elif hop_count == 3:
            # Three-hop relationships (with fuzzy matching)
            query = f"""
            MATCH (source:Entity)-[r1:RELATES_TO]->(m1:Entity)-[r2:RELATES_TO]->(m2:Entity)-[r3:RELATES_TO]->(target:Entity)
            WHERE ANY(entity IN $entities WHERE 
                      toLower(source.canonical_name) CONTAINS toLower(entity) OR
                      toLower(entity) CONTAINS toLower(source.canonical_name))
            {entity_filter}
            WITH source, m1, m2, target, r1, r2, r3,
                 (r1.confidence + r2.confidence + r3.confidence) / 3 as avg_confidence,
                 target.pagerank_score as pagerank
            RETURN source.canonical_name as source,
                   target.canonical_name as answer,
                   target.entity_id as target_id,
                   avg_confidence as confidence,
                   m1.canonical_name as middle1,
                   m2.canonical_name as middle2,
                   pagerank,
                   [source.canonical_name, m1.canonical_name, m2.canonical_name, target.canonical_name] as path
            ORDER BY avg_confidence DESC, pagerank DESC
            LIMIT $limit
            """
            
            result = session.run(
                query,
                entities=query_entities,
                limit=limit
            )
            
            for record in result:
                results.append({
                    "answer": record["answer"],
                    "path": record["path"],
                    "confidence": record["confidence"] or 0.5,
                    "evidence": f"Connected via {record['middle1']} and {record['middle2']}",
                    "pagerank_scores": [0.0, 0.0, 0.0, record["pagerank"] or 0.0]
                })
        
        return results
    
    def _calculate_result_confidence(
        self, 
        path: List[str], 
        pagerank_scores: List[float]
    ) -> float:
        """Calculate confidence score for a result"""
        # Base confidence from path length (shorter paths are more confident)
        path_confidence = 1.0 / len(path)
        
        # Boost from PageRank scores
        pagerank_boost = 0.0
        if pagerank_scores:
            # Weight PageRank of final node more heavily
            pagerank_boost = sum(pagerank_scores) * 0.5
            if len(pagerank_scores) > 0:
                pagerank_boost += pagerank_scores[-1] * 0.5  # Extra weight for target
        
        # Combine factors
        confidence = (path_confidence * 0.7) + (pagerank_boost * 0.3)
        
        # Normalize to [0, 1]
        return min(1.0, max(0.0, confidence))
    
    def _format_path(self, path: List[str]) -> List[Dict[str, str]]:
        """Format path for output"""
        formatted_path = []
        
        for i, node in enumerate(path):
            formatted_path.append({
                "position": i,
                "entity": node,
                "role": "source" if i == 0 else ("target" if i == len(path) - 1 else "intermediate")
            })
        
        return formatted_path
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not isinstance(input_data, dict):
            return False
        
        # Query is required
        if "query" not in input_data:
            return False
        
        query = input_data["query"]
        if not isinstance(query, str) or not query.strip():
            return False
        
        # Optional parameters
        if "max_hops" in input_data:
            max_hops = input_data["max_hops"]
            if not isinstance(max_hops, int) or max_hops < 1 or max_hops > 3:
                return False
        
        if "result_limit" in input_data:
            limit = input_data["result_limit"]
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                return False
        
        if "entity_types" in input_data:
            types = input_data["entity_types"]
            if not isinstance(types, list):
                return False
            for t in types:
                if not isinstance(t, str):
                    return False
        
        return True


# Test function
def test_query_engine():
    """Test the query engine with sample queries"""
    from src.core.service_manager import get_service_manager
    
    service_manager = get_service_manager()
    engine = T49MultiHopQueryNeo4j(service_manager)
    
    # First, ensure we have some test data in Neo4j
    with service_manager.get_neo4j_driver().session() as session:
        # Create test entities and relationships
        session.run("""
            // Create test entities
            MERGE (carter:Entity {entity_id: 'carter_1', canonical_name: 'Carter', entity_type: 'PERSON'})
            MERGE (annapolis:Entity {entity_id: 'annapolis_1', canonical_name: 'Annapolis', entity_type: 'GPE'})
            MERGE (academy:Entity {entity_id: 'academy_1', canonical_name: 'Naval Academy', entity_type: 'ORG'})
            MERGE (navy:Entity {entity_id: 'navy_1', canonical_name: 'U.S. Navy', entity_type: 'ORG'})
            
            // Create relationships
            MERGE (carter)-[:RELATES_TO {confidence: 0.9, evidence: 'graduated from'}]->(academy)
            MERGE (academy)-[:RELATES_TO {confidence: 0.85, evidence: 'located in'}]->(annapolis)
            MERGE (carter)-[:RELATES_TO {confidence: 0.8, evidence: 'served in'}]->(navy)
            
            // Set PageRank scores
            SET carter.pagerank_score = 0.25
            SET annapolis.pagerank_score = 0.15
            SET academy.pagerank_score = 0.20
            SET navy.pagerank_score = 0.30
        """)
    
    # Test queries
    test_queries = [
        "Where did Carter go to school?",
        "What is in Annapolis?",
        "Who is Carter?",
        "What organizations are related to Carter?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        request = ToolRequest(
            tool_id="T49",
            operation="query",
            input_data={
                "query": query,
                "max_hops": 2,
                "result_limit": 5,
                "source_refs": ["test"]
            },
            parameters={}
        )
        
        result = engine.execute(request)
        
        if result.status == "success":
            print(f"✅ Found {len(result.data['results'])} results")
            print(f"   Query entities: {result.data['query_entities']}")
            
            for i, res in enumerate(result.data['results'][:3]):
                print(f"\n   Result {i+1}:")
                print(f"   - Answer: {res['answer']}")
                print(f"   - Confidence: {res['confidence']:.3f}")
                print(f"   - Hops: {res['hops']}")
                print(f"   - Evidence: {res['evidence']}")
                print(f"   - Path: {' -> '.join([p['entity'] for p in res['path']])}")
        else:
            print(f"❌ Error: {result.error_message}")
    
    return True


if __name__ == "__main__":
    test_query_engine()