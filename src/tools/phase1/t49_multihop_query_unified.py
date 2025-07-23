"""
T49 Multi-hop Query Unified Tool

Performs multi-hop queries on Neo4j graph to find research answers.
Implements unified BaseTool interface with comprehensive query capabilities.
"""

import uuid
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

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
        self.logger = logging.getLogger(__name__)
        
        # Query parameters
        self.max_hops = 3
        self.result_limit = 20
        self.min_path_weight = 0.01
        self.pagerank_boost_factor = 2.0
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Query execution stats
        self.queries_processed = 0
        self.paths_found = 0
        self.entities_extracted = 0
        self.neo4j_operations = 0

    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection"""
        if not NEO4J_AVAILABLE:
            self.logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            return
        
        try:
            # Use default Neo4j settings - in production these would come from config
            neo4j_uri = "bolt://localhost:7687"
            neo4j_user = "neo4j"
            neo4j_password = "password"
            
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
        """Execute multi-hop query with real Neo4j integration"""
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
            
            # Check Neo4j availability
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
            
            # Extract query parameters
            query_text = request.input_data.get("query", request.input_data.get("query_text", ""))
            max_hops = request.parameters.get("max_hops", self.max_hops)
            result_limit = request.parameters.get("result_limit", self.result_limit)
            min_path_weight = request.parameters.get("min_path_weight", self.min_path_weight)
            
            # Extract entities from query text
            query_entities = self._extract_query_entities(query_text)
            
            if not query_entities:
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="success",
                    data={
                        "query_results": [],
                        "result_count": 0,
                        "reason": "No recognizable entities found in query"
                    },
                    execution_time=execution_time,
                    memory_used=memory_used,
                    metadata={
                        "query_text": query_text,
                        "entities_extracted": 0
                    }
                )
            
            # Perform multi-hop query
            query_results = self._perform_multihop_query(
                query_entities, 
                query_text, 
                max_hops, 
                result_limit,
                min_path_weight
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(query_results)
            
            # Create service mentions for query results
            self._create_service_mentions(query_results[:5], request.input_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "query_results": query_results,
                    "result_count": len(query_results),
                    "confidence": overall_confidence,
                    "processing_method": "neo4j_multihop_query",
                    "query_stats": {
                        "queries_processed": self.queries_processed,
                        "paths_found": self.paths_found,
                        "entities_extracted": self.entities_extracted,
                        "neo4j_operations": self.neo4j_operations
                    },
                    "extracted_entities": query_entities,
                    "query_analysis": self._analyze_query_complexity(query_text, query_entities),
                    "path_distribution": self._analyze_path_distribution(query_results)
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "query_text": query_text,
                    "max_hops": max_hops,
                    "result_limit": result_limit,
                    "min_path_weight": min_path_weight,
                    "entities_found": len(query_entities),
                    "neo4j_available": True
                }
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            self.logger.error(f"Multi-hop query error: {str(e)}")
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
        
        return {"valid": True}

    def _extract_query_entities(self, query_text: str) -> List[Dict[str, Any]]:
        """Extract entities from query text using simple patterns and Neo4j lookup"""
        if not self.driver:
            return []
        
        try:
            # Extract potential entity names using simple patterns
            potential_entities = []
            
            # Pattern 1: Capitalized words/phrases (proper nouns)
            capitalized_patterns = re.findall(r'\b[A-Z][a-zA-Z\s]{1,30}(?=\s|$)', query_text)
            potential_entities.extend([p.strip() for p in capitalized_patterns if len(p.strip()) > 2])
            
            # Pattern 2: Quoted entities
            quoted_patterns = re.findall(r'"([^"]+)"', query_text)
            potential_entities.extend(quoted_patterns)
            
            # Pattern 3: Common entity indicators
            entity_indicators = [
                r'(?:company|corporation|inc|corp|ltd)\s+([A-Z][a-zA-Z\s]+)',
                r'(?:person|people|individual)\s+([A-Z][a-zA-Z\s]+)',
                r'(?:city|country|state)\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:company|corporation|inc|corp|ltd)',
            ]
            
            for pattern in entity_indicators:
                matches = re.findall(pattern, query_text, re.IGNORECASE)
                potential_entities.extend([m.strip() for m in matches])
            
            # Remove duplicates and clean up
            unique_entities = list(set([e.strip() for e in potential_entities if len(e.strip()) > 2]))
            
            # Look up entities in Neo4j
            found_entities = []
            
            with self.driver.session() as session:
                for entity_name in unique_entities:
                    # Search for entities with similar names
                    cypher = """
                    MATCH (e:Entity)
                    WHERE toLower(e.canonical_name) CONTAINS toLower($entity_name)
                       OR toLower(e.canonical_name) = toLower($entity_name)
                    RETURN e.entity_id as entity_id,
                           e.canonical_name as canonical_name,
                           e.entity_type as entity_type,
                           e.confidence as confidence,
                           e.pagerank_score as pagerank_score
                    ORDER BY e.pagerank_score DESC NULLS LAST
                    LIMIT 3
                    """
                    
                    result = session.run(cypher, entity_name=entity_name)
                    
                    for record in result:
                        found_entities.append({
                            "query_name": entity_name,
                            "entity_id": record["entity_id"],
                            "canonical_name": record["canonical_name"],
                            "entity_type": record["entity_type"],
                            "confidence": record["confidence"] or 0.5,
                            "pagerank_score": record["pagerank_score"] or 0.0001,
                            "match_type": "exact" if entity_name.lower() == record["canonical_name"].lower() else "partial"
                        })
            
            self.entities_extracted = len(found_entities)
            self.neo4j_operations += len(unique_entities)
            
            return found_entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            return []

    def _perform_multihop_query(
        self, 
        query_entities: List[Dict[str, Any]], 
        query_text: str,
        max_hops: int,
        result_limit: int,
        min_path_weight: float
    ) -> List[Dict[str, Any]]:
        """Perform multi-hop query to find relevant paths and answers"""
        if not self.driver or not query_entities:
            return []
        
        all_results = []
        
        try:
            with self.driver.session() as session:
                # If we have multiple entities, find paths between them
                if len(query_entities) >= 2:
                    # Find paths between entity pairs
                    for i, source_entity in enumerate(query_entities):
                        for target_entity in query_entities[i+1:]:
                            paths = self._find_paths_between_entities(
                                session, 
                                source_entity, 
                                target_entity, 
                                max_hops
                            )
                            all_results.extend(paths)
                
                # Also find high-ranking entities related to each query entity
                for entity in query_entities:
                    related_results = self._find_related_entities(
                        session,
                        entity,
                        max_hops,
                        result_limit // len(query_entities) if len(query_entities) > 0 else result_limit
                    )
                    all_results.extend(related_results)
            
            # Rank and filter results
            ranked_results = self._rank_query_results(all_results, query_text, min_path_weight)
            
            # Limit results
            final_results = ranked_results[:result_limit]
            
            self.queries_processed += 1
            self.paths_found = len(final_results)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Multi-hop query execution failed: {e}")
            return []

    def _find_paths_between_entities(
        self, 
        session, 
        source_entity: Dict[str, Any], 
        target_entity: Dict[str, Any], 
        max_hops: int
    ) -> List[Dict[str, Any]]:
        """Find paths between two entities"""
        paths = []
        
        try:
            # Query for paths of different lengths
            for hop_count in range(1, max_hops + 1):
                cypher = f"""
                MATCH path = (source:Entity)-[*{hop_count}]->(target:Entity)
                WHERE source.entity_id = $source_id 
                  AND target.entity_id = $target_id
                  AND ALL(r IN relationships(path) WHERE r.weight > 0.1)
                WITH path, 
                     reduce(weight = 1.0, r IN relationships(path) | weight * r.weight) as path_weight,
                     [n IN nodes(path) | n.canonical_name] as path_names,
                     [r IN relationships(path) | r.relationship_type] as relationship_types,
                     length(path) as path_length
                WHERE path_weight > 0.001
                RETURN path_weight, path_names, relationship_types, path_length
                ORDER BY path_weight DESC
                LIMIT 5
                """
                
                result = session.run(
                    cypher,
                    source_id=source_entity["entity_id"],
                    target_id=target_entity["entity_id"]
                )
                
                for record in result:
                    path_data = {
                        "result_type": "path",
                        "source_entity": source_entity["canonical_name"],
                        "target_entity": target_entity["canonical_name"],
                        "path": record["path_names"],
                        "relationship_types": record["relationship_types"],
                        "path_length": record["path_length"],
                        "path_weight": record["path_weight"],
                        "confidence": self._calculate_path_confidence(record["path_weight"], record["path_length"]),
                        "explanation": self._generate_path_explanation(
                            record["path_names"], 
                            record["relationship_types"]
                        )
                    }
                    paths.append(path_data)
            
            self.neo4j_operations += max_hops
            return paths
            
        except Exception as e:
            self.logger.error(f"Path finding failed: {e}")
            return []

    def _find_related_entities(
        self, 
        session, 
        entity: Dict[str, Any], 
        max_hops: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Find entities related to the query entity"""
        related_entities = []
        
        try:
            # Find highly connected entities within max_hops
            cypher = f"""
            MATCH (source:Entity)-[*1..{max_hops}]->(related:Entity)
            WHERE source.entity_id = $entity_id
              AND related.entity_id <> $entity_id
            WITH related, 
                 count(*) as connection_count,
                 avg(related.pagerank_score) as avg_pagerank
            WHERE connection_count >= 1
            RETURN related.entity_id as entity_id,
                   related.canonical_name as canonical_name,
                   related.entity_type as entity_type,
                   related.confidence as confidence,
                   related.pagerank_score as pagerank_score,
                   connection_count,
                   avg_pagerank
            ORDER BY pagerank_score DESC NULLS LAST, connection_count DESC
            LIMIT $limit
            """
            
            result = session.run(
                cypher,
                entity_id=entity["entity_id"],
                limit=limit
            )
            
            for record in result:
                related_data = {
                    "result_type": "related_entity",
                    "query_entity": entity["canonical_name"],
                    "related_entity": record["canonical_name"],
                    "entity_type": record["entity_type"],
                    "pagerank_score": record["pagerank_score"] or 0.0001,
                    "connection_count": record["connection_count"],
                    "confidence": self._calculate_related_confidence(
                        record["pagerank_score"] or 0.0001,
                        record["connection_count"],
                        record["confidence"] or 0.5
                    ),
                    "explanation": f"{record['canonical_name']} is connected to {entity['canonical_name']} through {record['connection_count']} path(s)"
                }
                related_entities.append(related_data)
            
            self.neo4j_operations += 1
            return related_entities
            
        except Exception as e:
            self.logger.error(f"Related entity search failed: {e}")
            return []

    def _rank_query_results(
        self, 
        results: List[Dict[str, Any]], 
        query_text: str,
        min_path_weight: float
    ) -> List[Dict[str, Any]]:
        """Rank query results by relevance and confidence"""
        if not results:
            return []
        
        # Calculate ranking scores
        for result in results:
            ranking_score = 0.0
            
            # Base score from confidence
            ranking_score += result.get("confidence", 0.5) * 0.4
            
            # PageRank boost
            if "pagerank_score" in result:
                ranking_score += result["pagerank_score"] * self.pagerank_boost_factor * 0.3
            
            # Path weight boost for path results
            if result.get("result_type") == "path":
                path_weight = result.get("path_weight", 0.0)
                if path_weight >= min_path_weight:
                    ranking_score += path_weight * 0.2
                else:
                    ranking_score *= 0.5  # Penalize low-weight paths
                
                # Prefer shorter paths (inverse length bonus)
                path_length = result.get("path_length", 1)
                ranking_score += (1.0 / path_length) * 0.1
            
            # Connection count boost for related entities
            if result.get("result_type") == "related_entity":
                connection_count = result.get("connection_count", 1)
                ranking_score += min(connection_count / 10.0, 0.1)
            
            result["ranking_score"] = ranking_score
        
        # Filter out very low scoring results
        filtered_results = [r for r in results if r.get("ranking_score", 0) > 0.1]
        
        # Sort by ranking score descending
        ranked_results = sorted(filtered_results, key=lambda x: x.get("ranking_score", 0), reverse=True)
        
        # Add final rankings
        for i, result in enumerate(ranked_results, 1):
            result["rank"] = i
        
        return ranked_results

    def _calculate_path_confidence(self, path_weight: float, path_length: int) -> float:
        """Calculate confidence for a path result"""
        # Base confidence from path weight
        weight_confidence = min(path_weight * 10.0, 1.0)  # Scale up small weights
        
        # Length penalty (longer paths are less confident)
        length_penalty = 1.0 / (1.0 + (path_length - 1) * 0.2)
        
        confidence = weight_confidence * length_penalty
        return max(0.1, min(1.0, confidence))

    def _calculate_related_confidence(
        self, 
        pagerank_score: float, 
        connection_count: int, 
        base_confidence: float
    ) -> float:
        """Calculate confidence for a related entity result"""
        # Combine PageRank, connection count, and base confidence
        pagerank_factor = min(pagerank_score * 1000, 1.0)  # Scale up small PageRank scores
        connection_factor = min(connection_count / 5.0, 1.0)  # Scale connection count
        
        confidence = (pagerank_factor * 0.4) + (connection_factor * 0.3) + (base_confidence * 0.3)
        return max(0.1, min(1.0, confidence))

    def _generate_path_explanation(self, path_names: List[str], relationship_types: List[str]) -> str:
        """Generate human-readable explanation for a path"""
        if not path_names or len(path_names) < 2:
            return "No path found"
        
        if not relationship_types or len(relationship_types) != len(path_names) - 1:
            return f"Path: {' -> '.join(path_names)}"
        
        explanation_parts = []
        for i in range(len(relationship_types)):
            source = path_names[i]
            target = path_names[i + 1]
            relation = relationship_types[i].replace("_", " ").lower()
            explanation_parts.append(f"{source} {relation} {target}")
        
        return "; ".join(explanation_parts)

    def _analyze_query_complexity(self, query_text: str, query_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query complexity and characteristics"""
        return {
            "query_length": len(query_text),
            "entity_count": len(query_entities),
            "complexity_score": min(len(query_entities) / 5.0, 1.0),
            "entity_types": list(set([e.get("entity_type", "UNKNOWN") for e in query_entities])),
            "has_multiple_entities": len(query_entities) > 1,
            "query_words": len(query_text.split())
        }

    def _analyze_path_distribution(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of path lengths and types"""
        if not query_results:
            return {}
        
        result_types = {}
        path_lengths = []
        confidence_ranges = {"high": 0, "medium": 0, "low": 0}
        
        for result in query_results:
            # Count result types
            result_type = result.get("result_type", "unknown")
            result_types[result_type] = result_types.get(result_type, 0) + 1
            
            # Collect path lengths
            if "path_length" in result:
                path_lengths.append(result["path_length"])
            
            # Count confidence ranges
            confidence = result.get("confidence", 0.5)
            if confidence >= 0.8:
                confidence_ranges["high"] += 1
            elif confidence >= 0.5:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["low"] += 1
        
        analysis = {
            "result_type_distribution": result_types,
            "confidence_distribution": confidence_ranges
        }
        
        if path_lengths:
            analysis["path_length_stats"] = {
                "min_length": min(path_lengths),
                "max_length": max(path_lengths),
                "avg_length": sum(path_lengths) / len(path_lengths)
            }
        
        return analysis

    def _calculate_overall_confidence(self, query_results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for query results"""
        if not query_results:
            return 0.0
        
        # Weight confidence by ranking
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for result in query_results:
            rank_weight = 1.0 / result.get("rank", 1)  # Higher rank = higher weight
            confidence = result.get("confidence", 0.5)
            weighted_confidence += confidence * rank_weight
            total_weight += rank_weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _create_service_mentions(self, top_results: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for top query results (placeholder for service integration)"""
        # This would integrate with the service manager to create mentions
        # For now, just log the top results
        if top_results:
            self.logger.info(f"Top {len(top_results)} query results processed")

    def get_query_stats(self) -> Dict[str, Any]:
        """Get query execution statistics"""
        return {
            "queries_processed": self.queries_processed,
            "paths_found": self.paths_found,
            "entities_extracted": self.entities_extracted,
            "neo4j_operations": self.neo4j_operations,
            "query_params": {
                "max_hops": self.max_hops,
                "result_limit": self.result_limit,
                "min_path_weight": self.min_path_weight,
                "pagerank_boost_factor": self.pagerank_boost_factor
            }
        }

    def search_entities_by_name(self, entity_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for entities by name similarity"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                cypher = """
                MATCH (e:Entity)
                WHERE toLower(e.canonical_name) CONTAINS toLower($entity_name)
                RETURN e.entity_id as entity_id,
                       e.canonical_name as canonical_name,
                       e.entity_type as entity_type,
                       e.confidence as confidence,
                       e.pagerank_score as pagerank_score
                ORDER BY e.pagerank_score DESC NULLS LAST
                LIMIT $limit
                """
                
                result = session.run(cypher, entity_name=entity_name, limit=limit)
                
                entities = []
                for record in result:
                    entities.append({
                        "entity_id": record["entity_id"],
                        "canonical_name": record["canonical_name"],
                        "entity_type": record["entity_type"],
                        "confidence": record["confidence"],
                        "pagerank_score": record["pagerank_score"]
                    })
                
                return entities
                
        except Exception as e:
            self.logger.error(f"Entity search failed: {e}")
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
            "description": "Perform multi-hop queries on Neo4j graph to find research answers",
            "input_specification": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 3,
                        "description": "Natural language query text"
                    },
                    "query_text": {
                        "type": "string",
                        "minLength": 3,
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
                    "confidence": {"type": "number"}
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
            "storage_backend": "neo4j"
        }