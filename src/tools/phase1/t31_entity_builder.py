"""T31: Entity Node Builder - Minimal Implementation

Converts entity mentions into graph nodes and stores them in Neo4j.
Critical component for building the graph structure in the vertical slice.

Minimal implementation focusing on:
- Mention aggregation to entities via T107
- Canonical name assignment
- Basic Neo4j node creation
- Simple deduplication by name

Deferred features:
- Complex entity merging algorithms
- Advanced property assignment
- Entity type hierarchies
- Cross-document entity resolution
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
except ImportError:
    from core.identity_service import IdentityService
    from core.provenance_service import ProvenanceService
    from core.quality_service import QualityService
from .base_neo4j_tool import BaseNeo4jTool
from .neo4j_error_handler import Neo4jErrorHandler


class EntityBuilder(BaseNeo4jTool):
    """T31: Entity Node Builder."""
    
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
            identity_service, provenance_service, quality_service,
            neo4j_uri, neo4j_user, neo4j_password, shared_driver
        )
        self.tool_id = "T31_ENTITY_BUILDER"
    
    def build_entities(
        self,
        mentions: List[Dict[str, Any]],
        source_refs: List[str]
    ) -> Dict[str, Any]:
        """Build entity nodes from mentions and store in Neo4j.
        
        Args:
            mentions: List of entity mentions from NER
            source_refs: List of source references (chunks, documents)
            
        Returns:
            List of created entity nodes with Neo4j references
        """
        # Start operation tracking
        mention_refs = [m.get("mention_ref", "") for m in mentions]
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="build_entities",
            inputs=source_refs + mention_refs,
            parameters={
                "mention_count": len(mentions),
                "storage_backend": "neo4j"
            }
        )
        
        try:
            # Input validation
            if not mentions:
                return self._complete_success(
                    operation_id,
                    [],
                    "No mentions provided for entity building"
                )
            
            # Check Neo4j availability
            driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
            if driver_error:
                return self._complete_with_neo4j_error(operation_id, driver_error)
            
            # Group mentions by entity (using T107 entity linking)
            entity_groups = self._group_mentions_by_entity(mentions)
            
            # Build entity nodes
            created_entities = []
            entity_refs = []
            
            for entity_id, mention_group in entity_groups.items():
                # Get entity info from identity service
                entity_info = self._get_entity_info(entity_id, mention_group)
                
                if entity_info:
                    # Create Neo4j node
                    neo4j_result = self._create_neo4j_entity_node(entity_info, mention_group)
                    
                    if neo4j_result["status"] == "success":
                        entity_data = {
                            "entity_id": entity_id,
                            "neo4j_id": neo4j_result["neo4j_id"],
                            "entity_ref": f"storage://neo4j_entity/{neo4j_result['neo4j_id']}",
                            "canonical_name": entity_info["canonical_name"],
                            "entity_type": entity_info.get("entity_type"),
                            "mention_count": len(mention_group),
                            "mention_ids": [m["mention_id"] for m in mention_group],
                            "confidence": entity_info["confidence"],
                            "properties": neo4j_result.get("properties", {}),
                            "created_at": datetime.now().isoformat(),
                            "source_mentions": mention_refs
                        }
                        
                        created_entities.append(entity_data)
                        entity_refs.append(entity_data["entity_ref"])
                        
                        # Assess entity quality
                        quality_result = self.quality_service.assess_confidence(
                            object_ref=entity_data["entity_ref"],
                            base_confidence=entity_info["confidence"],
                            factors={
                                "mention_count": min(1.0, len(mention_group) / 5),  # More mentions = higher confidence
                                "name_length": min(1.0, len(entity_info["canonical_name"]) / 20),
                                "entity_type_confidence": self._get_type_confidence(entity_info.get("entity_type"))
                            },
                            metadata={
                                "storage_backend": "neo4j",
                                "entity_type": entity_info.get("entity_type"),
                                "mention_count": len(mention_group)
                            }
                        )
                        
                        if quality_result["status"] == "success":
                            entity_data["quality_confidence"] = quality_result["confidence"]
                            entity_data["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=entity_refs,
                success=True,
                metadata={
                    "entities_created": len(created_entities),
                    "total_mentions_processed": len(mentions),
                    "entity_types": list(set(e.get("entity_type") for e in created_entities if e.get("entity_type")))
                }
            )
            
            return {
                "status": "success",
                "entities": created_entities,
                "total_entities": len(created_entities),
                "entity_types": self._count_entity_types(created_entities),
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during entity building: {str(e)}"
            )
    
    def _group_mentions_by_entity(self, mentions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group mentions by their linked entity."""
        entity_groups = {}
        
        for mention in mentions:
            entity_id = mention.get("entity_id")
            if entity_id:
                if entity_id not in entity_groups:
                    entity_groups[entity_id] = []
                entity_groups[entity_id].append(mention)
        
        return entity_groups
    
    def _get_entity_info(self, entity_id: str, mentions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get entity information from identity service."""
        try:
            # Get entity from first mention
            first_mention = mentions[0]
            entity_info = self.identity_service.get_entity_by_mention(first_mention["mention_id"])
            
            if entity_info:
                # Calculate aggregated confidence from all mentions
                mention_confidences = [m.get("confidence", 0.5) for m in mentions]
                aggregated_confidence = sum(mention_confidences) / len(mention_confidences)
                
                # Boost confidence based on mention count
                mention_boost = min(0.1, len(mentions) * 0.02)  # Up to 10% boost
                final_confidence = min(1.0, aggregated_confidence + mention_boost)
                
                entity_info["confidence"] = final_confidence
                return entity_info
            
        except Exception as e:
            print(f"Error getting entity info for {entity_id}: {e}")
        
        return None
    
    def _create_neo4j_entity_node(
        self, 
        entity_info: Dict[str, Any], 
        mentions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create entity node in Neo4j."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            with self.driver.session() as session:
                # Prepare entity properties
                properties = {
                    "entity_id": entity_info["entity_id"],
                    "canonical_name": entity_info["canonical_name"],
                    "confidence": entity_info["confidence"],
                    "mention_count": len(mentions),
                    "created_at": datetime.now().isoformat(),
                    "tool_version": "T31_v1.0"
                }
                
                # Add entity type if available
                if entity_info.get("entity_type"):
                    properties["entity_type"] = entity_info["entity_type"]
                
                # Add mention surface forms
                surface_forms = list(set(m["surface_form"] for m in mentions))
                properties["surface_forms"] = surface_forms
                
                # Create Cypher query
                label = "Entity"
                if entity_info.get("entity_type"):
                    # Add specific type label
                    label = f"Entity:{entity_info['entity_type']}"
                
                cypher = f"""
                CREATE (e:{label} $properties)
                RETURN elementId(e) as neo4j_id, e
                """
                
                result = session.run(cypher, properties=properties)
                record = result.single()
                
                if record:
                    return {
                        "status": "success",
                        "neo4j_id": record["neo4j_id"],
                        "properties": dict(record["e"])
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Failed to create Neo4j node"
                    }
                    
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("create_entity_node", e)
    
    def _get_type_confidence(self, entity_type: Optional[str]) -> float:
        """Get confidence modifier for entity type."""
        if not entity_type:
            return 0.5
        
        # Some entity types are more reliable
        type_confidences = {
            "PERSON": 0.9,
            "ORG": 0.85,
            "GPE": 0.9,
            "PRODUCT": 0.7,
            "EVENT": 0.75,
            "WORK_OF_ART": 0.7,
            "LAW": 0.85,
            "LANGUAGE": 0.9,
            "FACILITY": 0.8,
            "MONEY": 0.95,
            "DATE": 0.8,
            "TIME": 0.8
        }
        
        return type_confidences.get(entity_type, 0.75)
    
    def _count_entity_types(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type."""
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def get_entity_by_neo4j_id(self, neo4j_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve entity from Neo4j by ID."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable: {driver_error['message']}")
            return None
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (e:Entity) WHERE id(e) = $id RETURN e",
                    id=neo4j_id
                )
                record = result.single()
                
                if record:
                    return dict(record["e"])
                
        except Exception as e:
            error_result = Neo4jErrorHandler.create_operation_error("get_entity_by_neo4j_id", e)
            print(f"Neo4j operation failed: {error_result['message']}")
        
        return None
    
    def search_entities(
        self, 
        name_pattern: str = None, 
        entity_type: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search entities in Neo4j."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            print(f"Neo4j unavailable: {driver_error['message']}")
            return []
        
        try:
            with self.driver.session() as session:
                conditions = []
                params = {"limit": limit}
                
                if name_pattern:
                    conditions.append("e.canonical_name CONTAINS $name_pattern")
                    params["name_pattern"] = name_pattern
                
                if entity_type:
                    conditions.append("e.entity_type = $entity_type")
                    params["entity_type"] = entity_type
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                cypher = f"""
                MATCH (e:Entity)
                {where_clause}
                RETURN elementId(e) as neo4j_id, e
                LIMIT $limit
                """
                
                result = session.run(cypher, **params)
                
                entities = []
                for record in result:
                    entity_data = dict(record["e"])
                    entity_data["neo4j_id"] = record["neo4j_id"]
                    entities.append(entity_data)
                
                return entities
                
        except Exception as e:
            error_result = Neo4jErrorHandler.create_operation_error("search_entities", e)
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
            "entities": [],
            "total_entities": 0,
            "entity_types": {},
            "operation_id": operation_id,
            "message": message
        }
    
    def get_neo4j_stats(self) -> Dict[str, Any]:
        """Get Neo4j database statistics."""
        # Check Neo4j availability
        driver_error = Neo4jErrorHandler.check_driver_available(self.driver)
        if driver_error:
            return driver_error
        
        try:
            with self.driver.session() as session:
                # Count entities
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                
                # Count by type
                type_counts = session.run("""
                MATCH (e:Entity)
                RETURN e.entity_type as type, count(e) as count
                ORDER BY count DESC
                """).data()
                
                return {
                    "status": "success",
                    "total_entities": entity_count,
                    "entity_type_distribution": {r["type"] or "UNKNOWN": r["count"] for r in type_counts}
                }
                
        except Exception as e:
            return Neo4jErrorHandler.create_operation_error("get_neo4j_stats", e)
    
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "Entity Node Builder",
            "version": "1.0.0",
            "description": "Converts entity mentions into graph nodes in Neo4j",
            "storage_backend": "neo4j",
            "requires_mentions": True,
            "neo4j_connected": self.driver is not None,
            "input_type": "mentions",
            "output_type": "neo4j_entities"
        }