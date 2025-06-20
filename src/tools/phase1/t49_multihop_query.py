"""T49: Multi-hop Graph Query - Minimal Implementation

Performs multi-hop queries on the Neo4j graph to find answers.
Final component of the PDF → PageRank → Answer vertical slice workflow.

Minimal implementation focusing on:
- Basic 2-hop and 3-hop graph traversal
- PageRank-weighted result ranking
- Simple path finding between entities
- Integration with core services

Deferred features:
- Complex query planning
- Advanced path ranking algorithms
- Semantic query understanding
- Query result caching
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import uuid
from datetime import datetime
import neo4j
from neo4j import GraphDatabase, Driver

# Import core services
try:
    from src.core.identity_service import IdentityService
    from src.core.provenance_service import ProvenanceService
    from src.core.quality_service import QualityService
    from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
    from src.tools.phase1.neo4j_error_handler import Neo4jErrorHandler
except ImportError:
    from core.identity_service import IdentityService
    from core.provenance_service import ProvenanceService
    from core.quality_service import QualityService
    from tools.phase1.base_neo4j_tool import BaseNeo4jTool
    from tools.phase1.neo4j_error_handler import Neo4jErrorHandler


class MultiHopQueryEngine(BaseNeo4jTool):
    """Multi-hop Query Engine - Main interface for query functionality."""
    
    def __init__(
        self,
        identity_service: IdentityService,
        provenance_service: ProvenanceService,
        quality_service: QualityService,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        shared_driver: Optional[Driver] = None
    ):
        super().__init__(
            identity_service=identity_service,
            provenance_service=provenance_service,
            quality_service=quality_service,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            shared_driver=shared_driver
        )
        
        # Initialize the actual query engine
        self.query_engine = MultiHopQuery(
            identity_service=identity_service,
            provenance_service=provenance_service,
            quality_service=quality_service,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            shared_driver=shared_driver
        )
    
    def query_graph(self, query_text: str, **kwargs) -> Dict[str, Any]:
        """Execute multi-hop query."""
        return self.query_engine.query_graph(query_text, **kwargs)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return self.query_engine.get_tool_info()

class MultiHopQuery(BaseNeo4jTool):
    """T49: Multi-hop Graph Query."""
    
    def __init__(
        self,
        identity_service: IdentityService,
        provenance_service: ProvenanceService,
        quality_service: QualityService,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        shared_driver: Optional[Driver] = None
    ):
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
        
        self.tool_id = "T49_MULTIHOP_QUERY"
        
        # Query parameters
        self.max_hops = 3               # Maximum number of hops
        self.max_results = 100          # Maximum results per query
        self.min_path_weight = 0.01     # Minimum path weight threshold
        self.pagerank_boost = 2.0       # Boost factor for PageRank scores
    
    
    def query_graph(
        self,
        query_text: str,
        query_entities: List[str] = None,
        max_hops: int = 2,
        result_limit: int = 20
    ) -> Dict[str, Any]:
        """Execute multi-hop query on the graph.
        
        Args:
            query_text: Natural language query text
            query_entities: List of entity names to start search from
            max_hops: Maximum number of hops (1-3)
            result_limit: Maximum number of results to return
            
        Returns:
            Query results with paths, entities, and confidence scores
        """
        # Start operation tracking
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="multihop_query",
            inputs=["storage://query/user_input"],
            parameters={
                "query_text": query_text[:200],  # Truncate for storage
                "query_entities": query_entities or [],
                "max_hops": max_hops,
                "result_limit": result_limit
            }
        )
        
        try:
            # Input validation
            if not query_text or not query_text.strip():
                return self._complete_with_error(
                    operation_id,
                    "Query text cannot be empty"
                )
            
            # Check Neo4j availability
            driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
            if driver_error:
                return self._complete_with_neo4j_error(operation_id, driver_error)
            
            max_hops = max(1, min(self.max_hops, max_hops))  # Clamp to valid range
            result_limit = max(1, min(self.max_results, result_limit))
            
            # Find or extract query entities
            if not query_entities:
                query_entities = self._extract_query_entities(query_text)
            
            if not query_entities:
                return self._complete_success(
                    operation_id,
                    [],
                    "No entities found in query for graph traversal"
                )
            
            # Execute multi-hop search
            search_results = self._execute_multihop_search(
                query_entities, max_hops, result_limit
            )
            
            if search_results["status"] != "success":
                return self._complete_with_error(
                    operation_id,
                    f"Multi-hop search failed: {search_results.get('error')}"
                )
            
            # Rank and process results
            ranked_results = self._rank_query_results(
                search_results["paths"],
                query_text,
                query_entities
            )
            
            # Create result references and assess quality
            result_refs = []
            for i, result in enumerate(ranked_results):
                result_ref = f"storage://query_result/{uuid.uuid4().hex[:8]}"
                result["result_ref"] = result_ref
                result_refs.append(result_ref)
                
                # Assess result quality
                quality_result = self.quality_service.assess_confidence(
                    object_ref=result_ref,
                    base_confidence=result["confidence"],
                    factors={
                        "path_weight": result["path_weight"],
                        "pagerank_relevance": result.get("pagerank_score", 0.0),
                        "hop_distance": 1.0 - (result["hop_count"] / max_hops),  # Shorter paths better
                        "entity_match": result.get("entity_match_score", 0.5)
                    },
                    metadata={
                        "query_method": "multihop_graph_traversal",
                        "hop_count": result["hop_count"],
                        "path_type": result.get("path_type", "unknown")
                    }
                )
                
                if quality_result["status"] == "success":
                    result["quality_confidence"] = quality_result["confidence"]
                    result["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=result_refs,
                success=True,
                metadata={
                    "results_found": len(ranked_results),
                    "query_entities": query_entities,
                    "max_hops_used": max_hops,
                    "paths_explored": search_results.get("total_paths", 0)
                }
            )
            
            return {
                "status": "success",
                "query": {
                    "text": query_text,
                    "entities": query_entities,
                    "max_hops": max_hops
                },
                "results": ranked_results,
                "total_results": len(ranked_results),
                "search_stats": {
                    "paths_explored": search_results.get("total_paths", 0),
                    "entities_visited": search_results.get("entities_visited", 0),
                    "average_confidence": sum(r["confidence"] for r in ranked_results) / len(ranked_results) if ranked_results else 0
                },
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during multi-hop query: {str(e)}"
            )
    
    def _extract_query_entities(self, query_text: str) -> List[str]:
        """Extract potential entity names from query text."""
        # Improved entity extraction - search for all meaningful terms
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable for entity extraction: {driver_error['message']}")
            return []
        
        try:
            # Extract potential search terms from query
            import re
            
            # Remove question words and punctuation
            question_words = {'who', 'what', 'where', 'when', 'which', 'how', 'why', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'at', 'on', 'for', 'and', 'or', 'but', 'about', 'mentioned'}
            
            # Clean and split the query
            clean_query = re.sub(r'[?.,!;:]', '', query_text)
            words = clean_query.split()
            
            # Get all potential search terms
            search_terms = []
            
            # Add individual words
            for word in words:
                if word.lower() not in question_words:
                    search_terms.append(word)
            
            # Add multi-word phrases (2-3 words)
            for i in range(len(words)):
                for length in [2, 3]:
                    if i + length <= len(words):
                        phrase = ' '.join(words[i:i+length])
                        # Only add if not all words are question words
                        if not all(w.lower() in question_words for w in words[i:i+length]):
                            search_terms.append(phrase)
            
            # Search for matching entities in Neo4j using case-insensitive search
            found_entities = []
            seen_names = set()
            
            with self.driver.session() as session:
                for term in search_terms:
                    # Use case-insensitive search
                    result = session.run("""
                        MATCH (e:Entity)
                        WHERE toLower(e.canonical_name) CONTAINS toLower($term)
                           OR ANY(form IN e.surface_forms WHERE toLower(form) CONTAINS toLower($term))
                        RETURN DISTINCT e.canonical_name as name, e.pagerank_score as score
                        ORDER BY coalesce(e.pagerank_score, 0) DESC
                        LIMIT 5
                        """, term=term)
                    
                    for record in result:
                        name = record["name"]
                        if name not in seen_names:
                            found_entities.append(name)
                            seen_names.add(name)
            
            # Log what we found
            print(f"\nQuery: '{query_text}'")
            print(f"Search terms: {search_terms[:10]}..." if len(search_terms) > 10 else f"Search terms: {search_terms}")
            print(f"Found {len(found_entities)} entities: {found_entities[:5]}..." if len(found_entities) > 5 else f"Found entities: {found_entities}")
            
            return found_entities
            
        except Exception as e:
            print(f"Error extracting query entities: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _execute_multihop_search(
        self, 
        start_entities: List[str], 
        max_hops: int, 
        limit: int
    ) -> Dict[str, Any]:
        """Execute multi-hop search starting from given entities."""
        try:
            with self.driver.session() as session:
                all_paths = []
                entities_visited = set()
                
                # For each starting entity, find paths
                for entity_name in start_entities:
                    # Find the entity node
                    entity_result = session.run("""
                    MATCH (e:Entity)
                    WHERE e.canonical_name = $name
                    RETURN e.entity_id as id, e.canonical_name as name, e.pagerank_score as score
                    """, name=entity_name)
                    
                    entity_record = entity_result.single()
                    if not entity_record:
                        continue
                    
                    entities_visited.add(entity_record["id"])
                    
                    # Execute multi-hop traversal
                    if max_hops == 1:
                        paths = self._find_1hop_paths(session, entity_record["id"], limit)
                    elif max_hops == 2:
                        paths = self._find_2hop_paths(session, entity_record["id"], limit)
                    else:  # max_hops >= 3
                        paths = self._find_3hop_paths(session, entity_record["id"], limit)
                    
                    all_paths.extend(paths)
                
                return {
                    "status": "success",
                    "paths": all_paths,
                    "total_paths": len(all_paths),
                    "entities_visited": len(entities_visited)
                }
                
        except Exception as e:
            error_result = Neo4jErrorHandler.create_operation_error("multihop_search", e)
            return error_result
    
    def _find_1hop_paths(self, session, start_entity_id: str, limit: int) -> List[Dict[str, Any]]:
        """Find 1-hop paths from start entity."""
        result = session.run("""
        MATCH (start:Entity {entity_id: $start_id})-[r]->(end:Entity)
        RETURN start.canonical_name as start_name, start.pagerank_score as start_score,
               type(r) as rel_type, r.weight as weight, r.confidence as rel_confidence,
               end.canonical_name as end_name, end.pagerank_score as end_score,
               end.entity_id as end_id
        ORDER BY coalesce(r.weight, 0) DESC, coalesce(end.pagerank_score, 0) DESC
        LIMIT $limit
        """, start_id=start_entity_id, limit=limit)
        
        paths = []
        for record in result:
            path = {
                "hop_count": 1,
                "path_type": "direct",
                "start_entity": record["start_name"],
                "end_entity": record["end_name"],
                "end_entity_id": record["end_id"],
                "relationship_path": [record["rel_type"]],
                "path_weight": record["weight"] or 0.5,
                "path_confidence": record["rel_confidence"] or 0.5,
                "pagerank_score": record["end_score"] or 0.0,
                "entities": [record["start_name"], record["end_name"]]
            }
            paths.append(path)
        
        return paths
    
    def _find_2hop_paths(self, session, start_entity_id: str, limit: int) -> List[Dict[str, Any]]:
        """Find 2-hop paths from start entity."""
        result = session.run("""
        MATCH (start:Entity {entity_id: $start_id})-[r1]->(middle:Entity)-[r2]->(end:Entity)
        WHERE start <> end
        RETURN start.canonical_name as start_name, start.pagerank_score as start_score,
               type(r1) as rel1_type, r1.weight as weight1, r1.confidence as conf1,
               middle.canonical_name as middle_name, middle.pagerank_score as middle_score,
               type(r2) as rel2_type, r2.weight as weight2, r2.confidence as conf2,
               end.canonical_name as end_name, end.pagerank_score as end_score,
               end.entity_id as end_id
        ORDER BY (coalesce(r1.weight, 0.5) * coalesce(r2.weight, 0.5)) DESC, coalesce(end.pagerank_score, 0) DESC
        LIMIT $limit
        """, start_id=start_entity_id, limit=limit)
        
        paths = []
        for record in result:
            # Calculate combined path weight
            weight1 = record["weight1"] or 0.5
            weight2 = record["weight2"] or 0.5
            path_weight = (weight1 * weight2) ** 0.5  # Geometric mean
            
            # Calculate combined confidence
            conf1 = record["conf1"] or 0.5
            conf2 = record["conf2"] or 0.5
            path_confidence = (conf1 * conf2) ** 0.5
            
            path = {
                "hop_count": 2,
                "path_type": "indirect",
                "start_entity": record["start_name"],
                "middle_entity": record["middle_name"],
                "end_entity": record["end_name"],
                "end_entity_id": record["end_id"],
                "relationship_path": [record["rel1_type"], record["rel2_type"]],
                "path_weight": path_weight,
                "path_confidence": path_confidence,
                "pagerank_score": record["end_score"] or 0.0,
                "entities": [record["start_name"], record["middle_name"], record["end_name"]]
            }
            paths.append(path)
        
        return paths
    
    def _find_3hop_paths(self, session, start_entity_id: str, limit: int) -> List[Dict[str, Any]]:
        """Find 3-hop paths from start entity."""
        result = session.run("""
        MATCH (start:Entity {entity_id: $start_id})-[r1]->(e1:Entity)-[r2]->(e2:Entity)-[r3]->(end:Entity)
        WHERE start <> end AND e1 <> end AND e2 <> start
        RETURN start.canonical_name as start_name,
               type(r1) as rel1_type, r1.weight as weight1, r1.confidence as conf1,
               e1.canonical_name as e1_name,
               type(r2) as rel2_type, r2.weight as weight2, r2.confidence as conf2,
               e2.canonical_name as e2_name,
               type(r3) as rel3_type, r3.weight as weight3, r3.confidence as conf3,
               end.canonical_name as end_name, end.pagerank_score as end_score,
               end.entity_id as end_id
        ORDER BY (coalesce(r1.weight, 0.5) * coalesce(r2.weight, 0.5) * coalesce(r3.weight, 0.5)) DESC, coalesce(end.pagerank_score, 0) DESC
        LIMIT $limit
        """, start_id=start_entity_id, limit=limit // 2)  # Fewer 3-hop paths due to complexity
        
        paths = []
        for record in result:
            # Calculate combined path weight
            weights = [record["weight1"] or 0.5, record["weight2"] or 0.5, record["weight3"] or 0.5]
            path_weight = (weights[0] * weights[1] * weights[2]) ** (1/3)  # Cubic mean
            
            # Calculate combined confidence
            confs = [record["conf1"] or 0.5, record["conf2"] or 0.5, record["conf3"] or 0.5]
            path_confidence = (confs[0] * confs[1] * confs[2]) ** (1/3)
            
            path = {
                "hop_count": 3,
                "path_type": "complex",
                "start_entity": record["start_name"],
                "intermediate_entities": [record["e1_name"], record["e2_name"]],
                "end_entity": record["end_name"],
                "end_entity_id": record["end_id"],
                "relationship_path": [record["rel1_type"], record["rel2_type"], record["rel3_type"]],
                "path_weight": path_weight,
                "path_confidence": path_confidence,
                "pagerank_score": record["end_score"] or 0.0,
                "entities": [record["start_name"], record["e1_name"], record["e2_name"], record["end_name"]]
            }
            paths.append(path)
        
        return paths
    
    def _rank_query_results(
        self, 
        paths: List[Dict[str, Any]], 
        query_text: str, 
        query_entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Rank query results by relevance and quality."""
        ranked_results = []
        
        for path in paths:
            # Calculate overall confidence score
            base_confidence = path["path_confidence"]
            
            # Boost based on PageRank score
            pagerank_boost = min(0.2, path["pagerank_score"] * self.pagerank_boost)
            
            # Penalty for longer paths
            hop_penalty = 0.1 * (path["hop_count"] - 1)
            
            # Boost for path weight
            weight_boost = path["path_weight"] * 0.3
            
            # Calculate final confidence
            final_confidence = base_confidence + pagerank_boost + weight_boost - hop_penalty
            final_confidence = max(0.1, min(1.0, final_confidence))
            
            # Create result entry
            result = {
                "answer_entity": path["end_entity"],
                "answer_entity_id": path["end_entity_id"],
                "confidence": round(final_confidence, 3),
                "path_weight": round(path["path_weight"], 3),
                "pagerank_score": path["pagerank_score"],
                "hop_count": path["hop_count"],
                "path_type": path["path_type"],
                "relationship_path": " → ".join(path["relationship_path"]),
                "full_path": " → ".join(path["entities"]),
                "explanation": self._generate_path_explanation(path),
                "source_entities": query_entities
            }
            
            ranked_results.append(result)
        
        # Sort by confidence (descending)
        ranked_results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Remove duplicates (same end entity)
        seen_entities = set()
        unique_results = []
        for result in ranked_results:
            if result["answer_entity_id"] not in seen_entities:
                seen_entities.add(result["answer_entity_id"])
                unique_results.append(result)
        
        return unique_results
    
    def _generate_path_explanation(self, path: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the path."""
        if path["hop_count"] == 1:
            return f"Directly connected via {path['relationship_path'][0]}"
        elif path["hop_count"] == 2:
            return f"Connected through {path.get('middle_entity', 'intermediate entity')} via {' → '.join(path['relationship_path'])}"
        else:
            intermediates = path.get("intermediate_entities", ["entity"])
            return f"Connected through {', '.join(intermediates)} via multi-step relationships"
    
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
            "query": {},
            "results": [],
            "total_results": 0,
            "search_stats": {},
            "operation_id": operation_id,
            "message": message
        }
    
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "Multi-hop Graph Query",
            "version": "1.0.0",
            "description": "Performs multi-hop queries on Neo4j graph with PageRank-weighted ranking",
            "max_hops": self.max_hops,
            "max_results": self.max_results,
            "requires_graph": True,
            "uses_pagerank": True,
            "neo4j_connected": self.driver is not None,
            "input_type": "natural_language_query",
            "output_type": "ranked_answers"
        }