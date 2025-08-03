from src.core.standard_config import get_database_uri
"""
T34 Edge Builder Unified Tool

Creates weighted relationship edges in Neo4j from extracted relationships.
Implements unified BaseTool interface with comprehensive edge building capabilities.
"""

import uuid
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolErrorCode
from src.core.service_manager import ServiceManager

class T34EdgeBuilderUnified(BaseTool):
    """
    Edge Builder tool for creating weighted relationship edges in Neo4j.
    
    Features:
    - Real Neo4j integration
    - Entity verification before edge creation
    - Confidence-based weight calculation
    - Multiple relationship types support
    - Quality assessment
    - Comprehensive error handling
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T34_EDGE_BUILDER"
        self.name = "Edge Builder"
        self.category = "graph_construction"
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
        # Weight calculation parameters
        self.min_weight = 0.1
        self.max_weight = 1.0
        self.confidence_weight_factor = 0.8
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Edge building stats
        self.edges_created = 0
        self.relationships_processed = 0
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
            
            # Get Neo4j settings from environment
            neo4j_uri = get_database_uri()
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', '')
            
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
        """Execute edge building with real Neo4j integration"""
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
            
            relationships = request.input_data.get("relationships", [])
            source_refs = request.input_data.get("source_refs", [])
            verify_entities = request.parameters.get("verify_entities", True)
            
            # Verify entities exist if requested
            if verify_entities:
                verification_result = self._verify_entities_exist(relationships)
                if not verification_result["all_entities_found"]:
                    execution_time, memory_used = self._end_execution()
                    return ToolResult(
                        tool_id=self.tool_id,
                        status="error",
                        data={
                            "missing_entities": verification_result.get("missing_entities", []),
                            "found_count": verification_result.get("found_count", 0),
                            "total_count": verification_result.get("total_count", 0)
                        },
                        error_message=f"Cannot create edges - missing entities: {verification_result.get('missing_entities', [])}",
                        error_code=ToolErrorCode.VALIDATION_FAILED,
                        execution_time=execution_time,
                        memory_used=memory_used
                    )
            
            # Build edges from relationships
            edges = self._build_edges_from_relationships(relationships, source_refs)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(edges)
            
            # Create service mentions for created edges
            self._create_service_mentions(edges, request.input_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "edges": edges,
                    "edge_count": len(edges),
                    "confidence": overall_confidence,
                    "processing_method": "neo4j_edge_building",
                    "building_stats": {
                        "relationships_processed": self.relationships_processed,
                        "edges_created": self.edges_created,
                        "neo4j_operations": self.neo4j_operations
                    },
                    "weight_distribution": self._analyze_weight_distribution(edges),
                    "relationship_types": self._count_relationship_types(edges)
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "neo4j_available": self.driver is not None,
                    "total_relationships": len(relationships),
                    "source_refs_count": len(source_refs),
                    "entity_verification": verify_entities
                }
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            self.logger.error(f"Edge building error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"Edge building failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for edge building"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        if "relationships" not in input_data:
            return {"valid": False, "error": "Missing required field: relationships"}
        
        relationships = input_data["relationships"]
        if not isinstance(relationships, list):
            return {"valid": False, "error": "Relationships must be a list"}
        
        if len(relationships) == 0:
            return {"valid": False, "error": "At least one relationship is required"}
        
        # Validate relationship structure
        for i, relationship in enumerate(relationships):
            if not isinstance(relationship, dict):
                return {"valid": False, "error": f"Relationship {i} must be a dictionary"}
            
            required_fields = ["subject", "object", "relationship_type"]
            for field in required_fields:
                if field not in relationship:
                    return {"valid": False, "error": f"Relationship {i} missing required field: {field}"}
            
            # Validate subject and object structure
            for entity_field in ["subject", "object"]:
                entity = relationship[entity_field]
                if not isinstance(entity, dict):
                    return {"valid": False, "error": f"Relationship {i} {entity_field} must be a dictionary"}
                
                if "text" not in entity:
                    return {"valid": False, "error": f"Relationship {i} {entity_field} missing 'text' field"}
        
        return {"valid": True}

    def _verify_entities_exist(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify all required entities exist in Neo4j"""
        if not self.driver:
            return {"all_entities_found": False, "reason": "Neo4j driver not available"}
        
        try:
            # Extract all unique entity identifiers
            required_entities = set()
            for rel in relationships:
                subject_id = self._get_entity_identifier(rel["subject"])
                object_id = self._get_entity_identifier(rel["object"])
                required_entities.add(subject_id)
                required_entities.add(object_id)
            
            if not required_entities:
                return {"all_entities_found": True, "missing_entities": []}
            
            # Check which entities exist in Neo4j
            with self.driver.session() as session:
                entity_check_cypher = """
                UNWIND $entity_ids AS entity_id
                OPTIONAL MATCH (e:Entity)
                WHERE e.canonical_name = entity_id OR e.entity_id = entity_id
                RETURN entity_id, count(e) > 0 as exists
                """
                
                result = session.run(entity_check_cypher, entity_ids=list(required_entities))
                
                found_entities = set()
                missing_entities = set()
                
                for record in result:
                    entity_id = record["entity_id"]
                    if record["exists"]:
                        found_entities.add(entity_id)
                    else:
                        missing_entities.add(entity_id)
                
                return {
                    "all_entities_found": len(missing_entities) == 0,
                    "missing_entities": list(missing_entities),
                    "found_count": len(found_entities),
                    "total_count": len(required_entities)
                }
                
        except Exception as e:
            self.logger.error(f"Entity verification failed: {e}")
            return {"all_entities_found": False, "reason": f"Verification error: {e}"}

    def _get_entity_identifier(self, entity: Dict[str, Any]) -> str:
        """Get entity identifier for lookup"""
        # Try different identifier fields
        for field in ["entity_id", "text", "canonical_name"]:
            if field in entity and entity[field]:
                return str(entity[field])
        
        return str(entity.get("text", "unknown_entity"))

    def _build_edges_from_relationships(
        self, 
        relationships: List[Dict[str, Any]], 
        source_refs: List[str]
    ) -> List[Dict[str, Any]]:
        """Build edges from relationships with real Neo4j storage"""
        edges = []
        
        for relationship in relationships:
            # Build edge from relationship
            edge = self._build_single_edge(relationship, source_refs)
            
            if edge:
                edges.append(edge)
                self.edges_created += 1
        
        self.relationships_processed += len(relationships)
        return edges

    def _build_single_edge(
        self, 
        relationship: Dict[str, Any], 
        source_refs: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Build a single edge from relationship"""
        if not self.driver:
            return None
        
        try:
            # Calculate edge weight
            weight = self._calculate_edge_weight(relationship)
            
            # Create Neo4j relationship edge
            neo4j_result = self._create_neo4j_relationship_edge(relationship, weight)
            
            if neo4j_result["status"] == "success":
                edge_data = {
                    "relationship_id": relationship.get("relationship_id", f"rel_{uuid.uuid4().hex[:8]}"),
                    "neo4j_rel_id": neo4j_result["neo4j_rel_id"],
                    "relationship_type": relationship["relationship_type"],
                    "subject": relationship["subject"],
                    "object": relationship["object"],
                    "weight": weight,
                    "confidence": relationship.get("confidence", 0.5),
                    "extraction_method": relationship.get("extraction_method", "unknown"),
                    "evidence_text": relationship.get("evidence_text", relationship.get("connecting_text", "")),
                    "properties": neo4j_result.get("properties", {}),
                    "created_at": datetime.now().isoformat()
                }
                
                return edge_data
        
        except Exception as e:
            self.logger.error(f"Failed to build edge: {e}")
        
        return None

    def _create_neo4j_relationship_edge(
        self, 
        relationship: Dict[str, Any], 
        weight: float
    ) -> Dict[str, Any]:
        """Create relationship edge in Neo4j"""
        if not self.driver:
            return {"status": "error", "error": "Neo4j driver not available"}
        
        try:
            with self.driver.session() as session:
                # Get entity identifiers
                subject_id = self._get_entity_identifier(relationship["subject"])
                object_id = self._get_entity_identifier(relationship["object"])
                
                # Prepare relationship properties
                properties = {
                    "relationship_id": relationship.get("relationship_id", f"rel_{uuid.uuid4().hex[:8]}"),
                    "relationship_type": relationship["relationship_type"],
                    "weight": weight,
                    "confidence": relationship.get("confidence", 0.5),
                    "extraction_method": relationship.get("extraction_method", "unknown"),
                    "evidence_text": str(relationship.get("evidence_text", relationship.get("connecting_text", "")))[:500],
                    "created_at": datetime.now().isoformat(),
                    "tool_version": "T34_unified_v1.0"
                }
                
                # Create relationship with flexible entity matching
                cypher = """
                MATCH (subject:Entity)
                WHERE subject.canonical_name = $subject_id OR subject.entity_id = $subject_id
                MATCH (object:Entity)
                WHERE object.canonical_name = $object_id OR object.entity_id = $object_id
                CREATE (subject)-[r:RELATED_TO $properties]->(object)
                RETURN elementId(r) as neo4j_rel_id, r
                """
                
                result = session.run(
                    cypher,
                    subject_id=subject_id,
                    object_id=object_id,
                    properties=properties
                )
                record = result.single()
                
                if record:
                    self.neo4j_operations += 1
                    return {
                        "status": "success",
                        "neo4j_rel_id": record["neo4j_rel_id"],
                        "properties": dict(record["r"])
                    }
                else:
                    return {"status": "error", "error": "Failed to create Neo4j relationship - entities may not exist"}
                    
        except Exception as e:
            self.logger.error(f"Neo4j relationship creation failed: {e}")
            return {"status": "error", "error": f"Neo4j operation failed: {str(e)}"}

    def _calculate_edge_weight(self, relationship: Dict[str, Any]) -> float:
        """Calculate edge weight from relationship confidence and other factors"""
        base_confidence = relationship.get("confidence", 0.5)
        
        # Weight factors
        factors = []
        
        # Primary factor: relationship confidence
        factors.append(base_confidence * self.confidence_weight_factor)
        
        # Secondary factor: extraction method confidence
        method_confidence = {
            "pattern_based": 0.8,
            "dependency_parsing": 0.75,
            "proximity_based": 0.4
        }
        extraction_method = relationship.get("extraction_method", "unknown")
        factors.append(method_confidence.get(extraction_method, 0.5))
        
        # Tertiary factor: evidence quality
        evidence_text = relationship.get("evidence_text", relationship.get("connecting_text", ""))
        evidence_quality = self._assess_evidence_quality(evidence_text)
        factors.append(evidence_quality)
        
        # Distance penalty for proximity-based relationships
        if relationship.get("entity_distance"):
            distance = relationship["entity_distance"]
            distance_factor = max(0.2, 1.0 - (distance / 100.0))
            factors.append(distance_factor)
        
        # Calculate weighted average
        if factors:
            weight = sum(factors) / len(factors)
        else:
            weight = base_confidence
        
        # Ensure weight is within bounds
        weight = max(self.min_weight, min(self.max_weight, weight))
        
        return round(weight, 3)

    def _assess_evidence_quality(self, evidence_text: str) -> float:
        """Assess quality of evidence text"""
        if not evidence_text:
            return 0.3
        
        # Simple heuristics for evidence quality
        quality_score = 0.5  # Base score
        
        # Length factor
        if len(evidence_text) > 50:
            quality_score += 0.2
        elif len(evidence_text) > 20:
            quality_score += 0.1
        
        # Word count factor
        word_count = len(evidence_text.split())
        if word_count >= 5:
            quality_score += 0.1
        
        # Presence of connecting words
        connecting_words = ["and", "with", "of", "in", "at", "for", "by", "owns", "works", "leads"]
        if any(word in evidence_text.lower() for word in connecting_words):
            quality_score += 0.1
        
        return min(1.0, quality_score)

    def _calculate_overall_confidence(self, edges: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for all created edges"""
        if not edges:
            return 0.0
        
        total_confidence = sum(edge["confidence"] for edge in edges)
        return total_confidence / len(edges)

    def _analyze_weight_distribution(self, edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weight distribution of created edges"""
        if not edges:
            return {}
        
        weights = [edge["weight"] for edge in edges]
        
        return {
            "min_weight": min(weights),
            "max_weight": max(weights),
            "average_weight": round(sum(weights) / len(weights), 3),
            "weight_ranges": {
                "high_confidence": len([w for w in weights if w >= 0.8]),
                "medium_confidence": len([w for w in weights if 0.5 <= w < 0.8]),
                "low_confidence": len([w for w in weights if w < 0.5])
            }
        }

    def _count_relationship_types(self, edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count edges by relationship type"""
        type_counts = {}
        for edge in edges:
            rel_type = edge["relationship_type"]
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts

    def _create_service_mentions(self, edges: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for created edges (placeholder for service integration)"""
        # This would integrate with the service manager to create mentions
        # For now, just log the creation
        if edges:
            self.logger.info(f"Created {len(edges)} relationship edges in Neo4j")

    def get_relationship_by_id(self, neo4j_rel_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve relationship from Neo4j by ID"""
        if not self.driver:
            return None
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (a)-[r]->(b) 
                    WHERE elementId(r) = $rel_id 
                    RETURN r, type(r) as rel_type, a.entity_id as subject_id, b.entity_id as object_id
                    """,
                    rel_id=neo4j_rel_id
                )
                record = result.single()
                
                if record:
                    rel_data = dict(record["r"])
                    rel_data.update({
                        "neo4j_rel_id": neo4j_rel_id,
                        "relationship_type": record["rel_type"],
                        "subject_entity_id": record["subject_id"],
                        "object_entity_id": record["object_id"]
                    })
                    return rel_data
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve relationship {neo4j_rel_id}: {e}")
        
        return None

    def search_relationships(
        self, 
        relationship_type: str = None, 
        min_weight: float = None, 
        max_weight: float = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search relationships in Neo4j"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                conditions = []
                params = {"limit": limit}
                
                if relationship_type:
                    conditions.append("r.relationship_type = $rel_type")
                    params["rel_type"] = relationship_type
                
                if min_weight is not None:
                    conditions.append("r.weight >= $min_weight")
                    params["min_weight"] = min_weight
                
                if max_weight is not None:
                    conditions.append("r.weight <= $max_weight")
                    params["max_weight"] = max_weight
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                cypher = f"""
                MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
                {where_clause}
                RETURN elementId(r) as neo4j_rel_id, r, 
                       a.entity_id as subject_id, b.entity_id as object_id
                ORDER BY r.weight DESC
                LIMIT $limit
                """
                
                result = session.run(cypher, **params)
                
                relationships = []
                for record in result:
                    rel_data = dict(record["r"])
                    rel_data.update({
                        "neo4j_rel_id": record["neo4j_rel_id"],
                        "subject_entity_id": record["subject_id"],
                        "object_entity_id": record["object_id"]
                    })
                    relationships.append(rel_data)
                
                return relationships
                
        except Exception as e:
            self.logger.error(f"Relationship search failed: {e}")
            return []

    def get_neo4j_stats(self) -> Dict[str, Any]:
        """Get Neo4j database statistics"""
        if not self.driver:
            return {"status": "error", "error": "Neo4j driver not available"}
        
        try:
            with self.driver.session() as session:
                # Count entities and relationships
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                # Count relationship types
                rel_types = session.run("""
                MATCH ()-[r:RELATED_TO]->()
                RETURN r.relationship_type as type, count(r) as count, avg(r.weight) as avg_weight
                ORDER BY count DESC
                """).data()
                
                # Calculate graph density
                max_possible_edges = entity_count * (entity_count - 1) if entity_count > 1 else 0
                density = rel_count / max_possible_edges if max_possible_edges > 0 else 0
                
                return {
                    "status": "success",
                    "total_entities": entity_count,
                    "total_relationships": rel_count,
                    "graph_density": round(density, 4),
                    "relationship_type_distribution": {
                        r["type"] or "UNKNOWN": {
                            "count": r["count"],
                            "average_weight": round(r["avg_weight"] or 0, 3)
                        } for r in rel_types
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get Neo4j stats: {e}")
            return {"status": "error", "error": f"Neo4j operation failed: {str(e)}"}

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
            "description": "Create weighted relationship edges in Neo4j from extracted relationships",
            "input_specification": {
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "relationship_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "subject": {"type": "object"},
                                "object": {"type": "object"},
                                "confidence": {"type": "number"},
                                "extraction_method": {"type": "string"},
                                "evidence_text": {"type": "string"}
                            },
                            "required": ["subject", "object", "relationship_type"]
                        },
                        "minItems": 1
                    },
                    "source_refs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "References to source documents or chunks"
                    }
                },
                "required": ["relationships"]
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "relationship_id": {"type": "string"},
                                "neo4j_rel_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "subject": {"type": "object"},
                                "object": {"type": "object"},
                                "weight": {"type": "number"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "edge_count": {"type": "integer"},
                    "confidence": {"type": "number"}
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.VALIDATION_FAILED,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ],
            "supported_relationship_types": [
                "OWNS", "WORKS_FOR", "LOCATED_IN", "PARTNERS_WITH",
                "CREATED", "LEADS", "MEMBER_OF", "RELATED_TO"
            ],
            "weight_range": [self.min_weight, self.max_weight],
            "dependencies": ["neo4j"],
            "storage_backend": "neo4j"
        }

    def build_edges(self, relationships: List[Dict[str, Any]], source_refs: List[str]) -> Dict[str, Any]:
        """MCP-compatible method for building edges from relationships"""
        from src.tools.base_tool import ToolRequest
        
        request = ToolRequest(
            tool_id=self.tool_id,
            operation="build_edges",
            input_data={
                "relationships": relationships,
                "source_refs": source_refs
            },
            parameters={}
        )
        
        result = self.execute(request)
        if result.status == "success":
            return result.data
        else:
            return {"error": result.error_message, "error_code": result.error_code}