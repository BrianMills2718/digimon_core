"""T34: Relationship Edge Builder - Minimal Implementation

Creates weighted relationship edges in Neo4j from extracted relationships.
Essential for building the graph structure needed for PageRank analysis.

Minimal implementation focusing on:
- Basic edge creation between entity nodes
- Confidence-based edge weights
- Simple relationship type mapping
- Provenance linking to source extractions

Deferred features:
- Complex weight calculations
- Edge property enrichment
- Relationship hierarchies
- Advanced graph constraints
"""

from typing import Dict, List, Optional, Any
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


class EdgeBuilder(BaseNeo4jTool):
    """T34: Relationship Edge Builder."""
    
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
        
        self.tool_id = "T34_EDGE_BUILDER"
        
        # Weight calculation parameters
        self.min_weight = 0.1
        self.max_weight = 1.0
        self.confidence_weight_factor = 0.8  # How much confidence affects weight
    
    
    def build_edges(
        self,
        relationships: List[Dict[str, Any]],
        source_refs: List[str],
        entity_verification_required: bool = True
    ) -> Dict[str, Any]:
        """Build relationship edges in Neo4j from extracted relationships.
        
        Args:
            relationships: List of relationships from T27
            source_refs: List of source references (chunks, documents)
            entity_verification_required: Whether to verify all entities exist before creating relationships
            
        Returns:
            List of created edges with Neo4j references
        """
        # Start operation tracking
        relationship_refs = [r.get("relationship_ref", "") for r in relationships]
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="build_edges",
            inputs=source_refs + relationship_refs,
            parameters={
                "relationship_count": len(relationships),
                "storage_backend": "neo4j"
            }
        )
        
        try:
            # Input validation
            if not relationships:
                return self._complete_success(
                    operation_id,
                    [],
                    "No relationships provided for edge building"
                )
            
            # Check Neo4j availability
            driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
            if driver_error:
                return self._complete_with_neo4j_error(operation_id, driver_error)
            
            # Verify all required entities exist before creating any relationships
            if entity_verification_required:
                verification_result = self._verify_entities_exist(relationships)
                if not verification_result["all_entities_found"]:
                    return self._complete_with_error(
                        operation_id,
                        f"Cannot create relationships - missing entities: {verification_result['missing_entities']}"
                    )
            
            # Build edges
            created_edges = []
            edge_refs = []
            
            for relationship in relationships:
                # Create Neo4j relationship edge
                edge_result = self._create_neo4j_relationship_edge(relationship)
                
                if edge_result["status"] == "success":
                    edge_data = {
                        "relationship_id": relationship["relationship_id"],
                        "neo4j_rel_id": edge_result["neo4j_rel_id"],
                        "edge_ref": f"storage://neo4j_relationship/{edge_result['neo4j_rel_id']}",
                        "relationship_type": relationship["relationship_type"],
                        "subject_entity_id": relationship["subject_entity_id"],
                        "object_entity_id": relationship["object_entity_id"],
                        "weight": edge_result["weight"],
                        "confidence": relationship["confidence"],
                        "source_relationship": relationship.get("relationship_ref", ""),
                        "extraction_method": relationship.get("extraction_method", "unknown"),
                        "evidence_text": relationship.get("evidence_text", ""),
                        "properties": edge_result.get("properties", {}),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    created_edges.append(edge_data)
                    edge_refs.append(edge_data["edge_ref"])
                    
                    # Assess edge quality
                    quality_result = self.quality_service.assess_confidence(
                        object_ref=edge_data["edge_ref"],
                        base_confidence=relationship["confidence"],
                        factors={
                            "extraction_confidence": relationship.get("pattern_confidence", 0.5),
                            "weight_strength": edge_result["weight"],
                            "evidence_quality": self._assess_evidence_quality(relationship.get("evidence_text", ""))
                        },
                        metadata={
                            "storage_backend": "neo4j",
                            "relationship_type": relationship["relationship_type"],
                            "extraction_method": relationship.get("extraction_method")
                        }
                    )
                    
                    if quality_result["status"] == "success":
                        edge_data["quality_confidence"] = quality_result["confidence"]
                        edge_data["quality_tier"] = quality_result["quality_tier"]
                else:
                    print(f"Failed to create edge for relationship {relationship['relationship_id']}: {edge_result.get('error')}")
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=edge_refs,
                success=True,
                metadata={
                    "edges_created": len(created_edges),
                    "total_relationships_processed": len(relationships),
                    "relationship_types": list(set(e["relationship_type"] for e in created_edges)),
                    "average_weight": sum(e["weight"] for e in created_edges) / len(created_edges) if created_edges else 0
                }
            )
            
            return {
                "status": "success",
                "edges": created_edges,
                "total_edges": len(created_edges),
                "relationship_types": self._count_relationship_types(created_edges),
                "weight_distribution": self._analyze_weight_distribution(created_edges),
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during edge building: {str(e)}"
            )
    
    def _create_neo4j_relationship_edge(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Create relationship edge in Neo4j."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            with self.driver.session() as session:
                # Calculate edge weight
                weight = self._calculate_edge_weight(relationship)
                
                # Prepare relationship properties with schema-compliant naming
                properties = {
                    "relationship_id": relationship["relationship_id"],
                    "relationship_type": relationship["relationship_type"],  # Schema expects this property
                    "weight": weight,
                    "confidence": relationship["confidence"],
                    "extraction_method": relationship.get("extraction_method", "unknown"),
                    "evidence_text": relationship.get("evidence_text", "")[:500],  # Truncate long evidence
                    "created_at": datetime.now().isoformat(),
                    "tool_version": "T34_v1.0"
                }
                
                # Add method-specific properties
                if relationship.get("pattern_confidence"):
                    properties["pattern_confidence"] = relationship["pattern_confidence"]
                
                if relationship.get("entity_distance"):
                    properties["entity_distance"] = relationship["entity_distance"]
                
                # First, verify both entities exist
                entity_check_cypher = """
                MATCH (subject:Entity {entity_id: $subject_id})
                MATCH (object:Entity {entity_id: $object_id})
                RETURN count(subject) > 0 AND count(object) > 0 as entities_exist
                """
                
                entity_check_result = session.run(
                    entity_check_cypher,
                    subject_id=relationship["subject_entity_id"],
                    object_id=relationship["object_entity_id"]
                )
                entity_check_record = entity_check_result.single()
                
                if not entity_check_record or not entity_check_record["entities_exist"]:
                    return {
                        "status": "error",
                        "error": f"Required entities not found: subject={relationship['subject_entity_id']}, object={relationship['object_entity_id']}"
                    }
                
                # Create Cypher query to link entities with standardized relationship type
                # Schema expects all relationships to be of type RELATED_TO with relationship_type property
                cypher = """
                MATCH (subject:Entity {entity_id: $subject_id})
                MATCH (object:Entity {entity_id: $object_id})
                CREATE (subject)-[r:RELATED_TO $properties]->(object)
                RETURN elementId(r) as neo4j_rel_id, r
                """
                
                result = session.run(
                    cypher,
                    subject_id=relationship["subject_entity_id"],
                    object_id=relationship["object_entity_id"],
                    properties=properties
                )
                record = result.single()
                
                if record:
                    return {
                        "status": "success",
                        "neo4j_rel_id": record["neo4j_rel_id"],
                        "weight": weight,
                        "properties": dict(record["r"])
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Failed to create Neo4j relationship - entities exist but relationship creation failed"
                    }
                    
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("create_relationship_edge", e)
    
    def _verify_entities_exist(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify all required entities exist in Neo4j before proceeding with relationships
        
        Args:
            relationships: List of relationships to verify entities for
            
        Returns:
            Dictionary with verification results
        """
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return {"all_entities_found": False, "reason": "Neo4j unavailable"}
        
        try:
            # Collect all unique entity IDs from relationships
            required_entities = set()
            for rel in relationships:
                subject_id = rel.get("subject_entity_id")
                object_id = rel.get("object_entity_id")
                if subject_id:
                    required_entities.add(subject_id)
                if object_id:
                    required_entities.add(object_id)
            
            if not required_entities:
                return {"all_entities_found": True, "missing_entities": []}
            
            # Check which entities exist in Neo4j
            with self.driver.session() as session:
                # Use parameterized query to check all entities at once
                entity_check_cypher = """
                UNWIND $entity_ids AS entity_id
                MATCH (e:Entity {entity_id: entity_id})
                RETURN entity_id
                """
                
                result = session.run(entity_check_cypher, entity_ids=list(required_entities))
                found_entities = set(record["entity_id"] for record in result)
                
                missing_entities = required_entities - found_entities
                
                return {
                    "all_entities_found": len(missing_entities) == 0,
                    "missing_entities": list(missing_entities),
                    "found_count": len(found_entities),
                    "total_count": len(required_entities)
                }
                
        except Exception as e:
            return {"all_entities_found": False, "reason": f"Verification error: {e}"}
    
    def _calculate_edge_weight(self, relationship: Dict[str, Any]) -> float:
        """Calculate edge weight from relationship confidence and other factors."""
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
        
        # Tertiary factor: pattern-specific confidence
        if relationship.get("pattern_confidence"):
            factors.append(relationship["pattern_confidence"])
        
        # Distance penalty for proximity-based relationships
        if relationship.get("entity_distance"):
            distance = relationship["entity_distance"]
            distance_factor = max(0.2, 1.0 - (distance / 100.0))  # Penalty for distance
            factors.append(distance_factor)
        
        # Calculate weighted average
        if factors:
            weight = sum(factors) / len(factors)
        else:
            weight = base_confidence
        
        # Ensure weight is within bounds
        weight = max(self.min_weight, min(self.max_weight, weight))
        
        return round(weight, 3)
    
    def _sanitize_relationship_type(self, rel_type: str) -> str:
        """Sanitize relationship type for use as Neo4j relationship label."""
        # Replace spaces and special characters with underscores
        import re
        sanitized = re.sub(r'[^A-Za-z0-9_]', '_', rel_type)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "REL_" + sanitized
        return sanitized or "RELATED_TO"
    
    def _assess_evidence_quality(self, evidence_text: str) -> float:
        """Assess quality of evidence text."""
        if not evidence_text:
            return 0.3
        
        # Simple heuristics for evidence quality
        quality_score = 0.5  # Base score
        
        # Length factor (longer evidence usually better)
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
    
    def _count_relationship_types(self, edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count edges by relationship type."""
        type_counts = {}
        for edge in edges:
            rel_type = edge["relationship_type"]
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts
    
    def _analyze_weight_distribution(self, edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weight distribution of created edges."""
        if not edges:
            return {}
        
        weights = [edge["weight"] for edge in edges]
        
        return {
            "min_weight": min(weights),
            "max_weight": max(weights),
            "average_weight": sum(weights) / len(weights),
            "weight_ranges": {
                "high_confidence": len([w for w in weights if w >= 0.8]),
                "medium_confidence": len([w for w in weights if 0.5 <= w < 0.8]),
                "low_confidence": len([w for w in weights if w < 0.5])
            }
        }
    
    def get_relationship_by_neo4j_id(self, neo4j_rel_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve relationship from Neo4j by ID."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable: {driver_error['message']}")
            return None
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (a)-[r]->(b) 
                    WHERE id(r) = $id 
                    RETURN r, type(r) as rel_type, a.entity_id as subject_id, b.entity_id as object_id
                    """,
                    id=neo4j_rel_id
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
            error_result = Neo4jErrorHandler.create_operation_error("get_relationship_by_neo4j_id", e)
            print(f"Neo4j operation failed: {error_result['message']}")
        
        return None
    
    def search_relationships(
        self,
        relationship_type: str = None,
        min_weight: float = None,
        max_weight: float = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search relationships in Neo4j."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable: {driver_error['message']}")
            return []
        
        try:
            with self.driver.session() as session:
                conditions = []
                params = {"limit": limit}
                
                if relationship_type:
                    # Note: This is simplified - in practice you'd need to handle the dynamic relationship type
                    conditions.append("type(r) = $rel_type")
                    params["rel_type"] = relationship_type
                
                if min_weight is not None:
                    conditions.append("r.weight >= $min_weight")
                    params["min_weight"] = min_weight
                
                if max_weight is not None:
                    conditions.append("r.weight <= $max_weight")
                    params["max_weight"] = max_weight
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                cypher = f"""
                MATCH (a:Entity)-[r]->(b:Entity)
                {where_clause}
                RETURN elementId(r) as neo4j_rel_id, r, type(r) as rel_type, 
                       a.entity_id as subject_id, b.entity_id as object_id
                LIMIT $limit
                """
                
                result = session.run(cypher, **params)
                
                relationships = []
                for record in result:
                    rel_data = dict(record["r"])
                    rel_data.update({
                        "neo4j_rel_id": record["neo4j_rel_id"],
                        "relationship_type": record["rel_type"],
                        "subject_entity_id": record["subject_id"],
                        "object_entity_id": record["object_id"]
                    })
                    relationships.append(rel_data)
                
                return relationships
                
        except Exception as e:
            error_result = Neo4jErrorHandler.create_operation_error("search_relationships", e)
            print(f"Neo4j operation failed: {error_result['message']}")
            return []
    
    def get_neo4j_graph_stats(self) -> Dict[str, Any]:
        """Get Neo4j graph statistics."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            with self.driver.session() as session:
                # Count entities and relationships
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                # Count relationship types
                rel_types = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count, avg(r.weight) as avg_weight
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
                        r["type"]: {
                            "count": r["count"],
                            "average_weight": round(r["avg_weight"] or 0, 3)
                        } for r in rel_types
                    }
                }
                
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("get_neo4j_graph_stats", e)
    
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
            "edges": [],
            "total_edges": 0,
            "relationship_types": {},
            "weight_distribution": {},
            "operation_id": operation_id,
            "message": message
        }
    
    
    def create_relationship_with_schema(self, rel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create relationship with proper schema compliance - simplified interface for workflow."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            with self.driver.session() as session:
                # Prepare relationship properties with UI-expected schema
                properties = {
                    "relation_type": rel_data.get('type', 'RELATED'),  # UI expects this property
                    "weight": rel_data.get('weight', 1.0),
                    "confidence": rel_data.get('confidence', 0.0),
                    "created_at": datetime.now().isoformat()
                }
                
                # Create Cypher query with proper schema compliance
                cypher = """
                MATCH (subject:Entity {entity_id: $subject_id})
                MATCH (object:Entity {entity_id: $object_id})
                CREATE (subject)-[r:RELATIONSHIP $properties]->(object)
                RETURN elementId(r) as neo4j_rel_id, r
                """
                
                result = session.run(
                    cypher,
                    subject_id=rel_data.get('source_id'),
                    object_id=rel_data.get('target_id'),
                    properties=properties
                )
                record = result.single()
                
                if record:
                    return {
                        "status": "success",
                        "neo4j_rel_id": record["neo4j_rel_id"],
                        "properties": dict(record["r"])
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Failed to create Neo4j relationship - entities may not exist"
                    }
                    
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("create_relationship_with_schema", e)

    def execute(self, input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the edge builder tool - standardized interface required by tool factory"""
        if isinstance(input_data, dict):
            # Extract required parameters
            relationship_refs = input_data.get("relationship_refs", [])
            relationships = input_data.get("relationships", [])
            workflow_id = input_data.get("workflow_id", "default")
        elif isinstance(input_data, list):
            # Input is list of relationships
            relationships = input_data
            relationship_refs = []
            workflow_id = "default"
        else:
            return {
                "status": "error",
                "error": "Input must be list of relationships or dict with 'relationships' key"
            }
            
        if not relationships:
            return {
                "status": "error",
                "error": "No relationships provided for edge building"
            }
            
        return self.build_edges(relationship_refs, relationships, workflow_id)

    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "Relationship Edge Builder",
            "version": "1.0.0",
            "description": "Creates weighted relationship edges in Neo4j from extracted relationships",
            "storage_backend": "neo4j",
            "requires_relationships": True,
            "weight_range": [self.min_weight, self.max_weight],
            "neo4j_connected": self.driver is not None,
            "input_type": "relationships",
            "output_type": "neo4j_edges"
        }