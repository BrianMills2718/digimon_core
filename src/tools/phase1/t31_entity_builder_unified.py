"""
T31 Entity Builder Unified Tool

Converts entity mentions into graph nodes and stores them in Neo4j.
Implements unified BaseTool interface with comprehensive entity building capabilities.
"""

import uuid
import logging
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

class T31EntityBuilderUnified(BaseTool):
    """
    Entity Builder tool for converting entity mentions into Neo4j graph nodes.
    
    Features:
    - Real Neo4j integration
    - Entity mention aggregation
    - Canonical name assignment
    - Quality assessment
    - Deduplication by entity ID
    - Comprehensive error handling
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T31"
        self.name = "Entity Builder"
        self.category = "graph_construction"
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Entity processing stats
        self.entities_created = 0
        self.mentions_processed = 0
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
        """Execute entity building with real Neo4j integration"""
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
            
            mentions = request.input_data.get("mentions", [])
            source_refs = request.input_data.get("source_refs", [])
            
            # Build entities from mentions
            entities = self._build_entities_from_mentions(mentions, source_refs)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(entities)
            
            # Create service mentions for created entities
            self._create_service_mentions(entities, request.input_data)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "entities": entities,
                    "entity_count": len(entities),
                    "confidence": overall_confidence,
                    "processing_method": "neo4j_entity_building",
                    "building_stats": {
                        "mentions_processed": self.mentions_processed,
                        "entities_created": self.entities_created,
                        "neo4j_operations": self.neo4j_operations
                    }
                },
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "neo4j_available": self.driver is not None,
                    "total_mentions": len(mentions),
                    "source_refs_count": len(source_refs),
                    "entity_types": self._get_entity_types_distribution(entities)
                }
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            self.logger.error(f"Entity building error: {str(e)}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"error": str(e)},
                error_message=f"Entity building failed: {str(e)}",
                error_code=ToolErrorCode.PROCESSING_ERROR,
                execution_time=execution_time,
                memory_used=memory_used
            )

    def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for entity building"""
        if not isinstance(input_data, dict):
            return {"valid": False, "error": "Input must be a dictionary"}
        
        if "mentions" not in input_data:
            return {"valid": False, "error": "Missing required field: mentions"}
        
        mentions = input_data["mentions"]
        if not isinstance(mentions, list):
            return {"valid": False, "error": "Mentions must be a list"}
        
        if len(mentions) == 0:
            return {"valid": False, "error": "At least one mention is required"}
        
        # Validate mention structure
        for i, mention in enumerate(mentions):
            if not isinstance(mention, dict):
                return {"valid": False, "error": f"Mention {i} must be a dictionary"}
            
            required_fields = ["text", "label"]
            for field in required_fields:
                if field not in mention:
                    return {"valid": False, "error": f"Mention {i} missing required field: {field}"}
        
        return {"valid": True}

    def _build_entities_from_mentions(
        self, 
        mentions: List[Dict[str, Any]], 
        source_refs: List[str]
    ) -> List[Dict[str, Any]]:
        """Build entities from mentions with real Neo4j storage"""
        entities = []
        
        # Group mentions by entity (for deduplication)
        entity_groups = self._group_mentions_by_entity(mentions)
        
        for entity_id, mention_group in entity_groups.items():
            # Build entity from mention group
            entity = self._build_single_entity(entity_id, mention_group, source_refs)
            
            if entity:
                entities.append(entity)
                self.entities_created += 1
        
        self.mentions_processed += len(mentions)
        return entities

    def _group_mentions_by_entity(self, mentions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group mentions by entity (using entity_id or creating new ones)"""
        entity_groups = {}
        
        for mention in mentions:
            # Use existing entity_id or create new one based on text and label
            entity_id = mention.get("entity_id")
            if not entity_id:
                # Create entity ID from text and label for grouping
                text = mention.get("text", "").strip().lower()
                label = mention.get("label", "UNKNOWN")
                entity_id = f"{label}_{hash(text) % 10000:04d}"
                mention["entity_id"] = entity_id
            
            if entity_id not in entity_groups:
                entity_groups[entity_id] = []
            entity_groups[entity_id].append(mention)
        
        return entity_groups

    def _build_single_entity(
        self, 
        entity_id: str, 
        mentions: List[Dict[str, Any]], 
        source_refs: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Build a single entity from mention group"""
        if not mentions:
            return None
        
        # Extract entity information from mentions
        entity_info = self._extract_entity_info(entity_id, mentions)
        
        # Create Neo4j node
        neo4j_result = self._create_neo4j_entity_node(entity_info, mentions)
        
        if neo4j_result["status"] == "success":
            entity_data = {
                "entity_id": entity_id,
                "neo4j_id": neo4j_result["neo4j_id"],
                "canonical_name": entity_info["canonical_name"],
                "entity_type": entity_info["entity_type"],
                "surface_forms": entity_info["surface_forms"],
                "mention_count": len(mentions),
                "confidence": entity_info["confidence"],
                "properties": neo4j_result.get("properties", {}),
                "source_mentions": [m.get("mention_id", f"mention_{i}") for i, m in enumerate(mentions)],
                "created_at": datetime.now().isoformat()
            }
            
            return entity_data
        
        return None

    def _extract_entity_info(self, entity_id: str, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract entity information from mention group"""
        # Get the most common entity type
        entity_types = [m.get("label", "UNKNOWN") for m in mentions]
        entity_type = max(set(entity_types), key=entity_types.count)
        
        # Get all surface forms
        surface_forms = list(set(m.get("text", "") for m in mentions if m.get("text")))
        
        # Choose canonical name (longest surface form)
        canonical_name = max(surface_forms, key=len) if surface_forms else "Unknown Entity"
        
        # Calculate confidence
        mention_confidences = [m.get("confidence", 0.8) for m in mentions]
        avg_confidence = sum(mention_confidences) / len(mention_confidences)
        
        # Boost confidence for multiple mentions
        mention_boost = min(0.2, len(mentions) * 0.05)
        confidence = min(1.0, avg_confidence + mention_boost)
        
        return {
            "entity_id": entity_id,
            "canonical_name": canonical_name,
            "entity_type": entity_type,
            "surface_forms": surface_forms,
            "confidence": confidence,
            "mention_count": len(mentions)
        }

    def _create_neo4j_entity_node(
        self, 
        entity_info: Dict[str, Any], 
        mentions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create entity node in Neo4j"""
        if not self.driver:
            return {"status": "error", "error": "Neo4j driver not available"}
        
        try:
            with self.driver.session() as session:
                # Prepare entity properties
                properties = {
                    "entity_id": entity_info["entity_id"],
                    "canonical_name": entity_info["canonical_name"],
                    "entity_type": entity_info["entity_type"],
                    "surface_forms": entity_info["surface_forms"],
                    "confidence": entity_info["confidence"],
                    "mention_count": entity_info["mention_count"],
                    "pagerank_score": 0.0,  # Initialize for PageRank
                    "created_at": datetime.now().isoformat(),
                    "tool_version": "T31_unified_v1.0"
                }
                
                # Create or merge entity node
                cypher = """
                MERGE (e:Entity {entity_id: $entity_id})
                SET e.canonical_name = $canonical_name,
                    e.entity_type = $entity_type,
                    e.surface_forms = $surface_forms,
                    e.confidence = $confidence,
                    e.mention_count = $mention_count,
                    e.pagerank_score = $pagerank_score,
                    e.created_at = $created_at,
                    e.tool_version = $tool_version
                RETURN elementId(e) as neo4j_id, e
                """
                
                result = session.run(cypher, **properties)
                record = result.single()
                
                if record:
                    self.neo4j_operations += 1
                    return {
                        "status": "success",
                        "neo4j_id": record["neo4j_id"],
                        "properties": dict(record["e"])
                    }
                else:
                    return {"status": "error", "error": "Failed to create Neo4j node"}
                    
        except Exception as e:
            self.logger.error(f"Neo4j entity creation failed: {e}")
            return {"status": "error", "error": f"Neo4j operation failed: {str(e)}"}

    def _calculate_overall_confidence(self, entities: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for all created entities"""
        if not entities:
            return 0.0
        
        total_confidence = sum(entity["confidence"] for entity in entities)
        return total_confidence / len(entities)

    def _get_entity_types_distribution(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of entity types"""
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts

    def _create_service_mentions(self, entities: List[Dict[str, Any]], input_data: Dict[str, Any]):
        """Create service mentions for created entities (placeholder for service integration)"""
        # This would integrate with the service manager to create mentions
        # For now, just log the creation
        if entities:
            self.logger.info(f"Created {len(entities)} entity nodes in Neo4j")

    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity from Neo4j by entity ID"""
        if not self.driver:
            return None
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (e:Entity {entity_id: $entity_id}) RETURN elementId(e) as neo4j_id, e",
                    entity_id=entity_id
                )
                record = result.single()
                
                if record:
                    entity_data = dict(record["e"])
                    entity_data["neo4j_id"] = record["neo4j_id"]
                    return entity_data
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve entity {entity_id}: {e}")
        
        return None

    def search_entities(
        self, 
        name_pattern: str = None, 
        entity_type: str = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search entities in Neo4j"""
        if not self.driver:
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
                ORDER BY e.confidence DESC
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
            self.logger.error(f"Entity search failed: {e}")
            return []

    def get_neo4j_stats(self) -> Dict[str, Any]:
        """Get Neo4j database statistics"""
        if not self.driver:
            return {"status": "error", "error": "Neo4j driver not available"}
        
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
            "description": "Convert entity mentions into Neo4j graph nodes with aggregation and deduplication",
            "input_specification": {
                "type": "object",
                "properties": {
                    "mentions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "label": {"type": "string"},
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                                "confidence": {"type": "number"},
                                "entity_id": {"type": "string"}
                            },
                            "required": ["text", "label"]
                        },
                        "minItems": 1
                    },
                    "source_refs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "References to source documents or chunks"
                    }
                },
                "required": ["mentions"]
            },
            "output_specification": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "neo4j_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "surface_forms": {"type": "array"},
                                "mention_count": {"type": "integer"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "entity_count": {"type": "integer"},
                    "confidence": {"type": "number"}
                }
            },
            "error_codes": [
                ToolErrorCode.INVALID_INPUT,
                ToolErrorCode.CONNECTION_ERROR,
                ToolErrorCode.PROCESSING_ERROR,
                ToolErrorCode.UNEXPECTED_ERROR
            ],
            "supported_entity_types": [
                "PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
                "WORK_OF_ART", "LAW", "LANGUAGE", "FACILITY", 
                "MONEY", "DATE", "TIME", "UNKNOWN"
            ],
            "dependencies": ["neo4j"],
            "storage_backend": "neo4j"
        }