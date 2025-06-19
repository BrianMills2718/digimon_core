"""Neo4j database manager."""

import logging
from typing import Optional, List, Dict, Any

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from ..models import Entity, Relationship


logger = logging.getLogger(__name__)


class Neo4jManager:
    """Manager for Neo4j graph database operations."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
    
    @property
    def driver(self):
        """Lazy-load driver connection."""
        if not self._driver:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
        return self._driver
    
    def initialize_schema(self) -> None:
        """Create indexes and constraints."""
        with self.driver.session() as session:
            # Create indexes
            queries = [
                "CREATE INDEX entity_id IF NOT EXISTS FOR (e:Entity) ON (e.id)",
                "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
                "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.entity_type)",
                "CREATE INDEX rel_id IF NOT EXISTS FOR ()-[r:RELATES]-() ON (r.id)",
                "CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:RELATES]-() ON (r.relationship_type)"
            ]
            
            for query in queries:
                try:
                    session.run(query)
                    logger.debug(f"Created index: {query}")
                except Exception as e:
                    logger.warning(f"Index creation skipped (may already exist): {e}")
    
    def health_check(self) -> bool:
        """Check if Neo4j is accessible."""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except ServiceUnavailable:
            return False
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False
    
    def save_entity(self, entity: Entity) -> None:
        """Save an entity to Neo4j."""
        with self.driver.session() as session:
            query = """
            MERGE (e:Entity {id: $id})
            SET e += $properties
            """
            session.run(query, id=entity.id, properties=entity.to_cypher_props())
            logger.debug(f"Saved entity: {entity.id}")
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {id: $id})
            RETURN e
            """
            result = session.run(query, id=entity_id)
            record = result.single()
            
            if record:
                props = dict(record["e"])
                return self._entity_from_props(props)
            return None
    
    def update_entity(self, entity: Entity) -> None:
        """Update an existing entity."""
        self.save_entity(entity)  # MERGE handles both create and update
    
    def delete_entity(self, entity_id: str) -> None:
        """Delete an entity and its relationships."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {id: $id})
            DETACH DELETE e
            """
            session.run(query, id=entity_id)
            logger.debug(f"Deleted entity: {entity_id}")
    
    def save_relationship(self, relationship: Relationship) -> None:
        """Save a relationship between entities."""
        with self.driver.session() as session:
            query = """
            MATCH (s:Entity {id: $source_id})
            MATCH (t:Entity {id: $target_id})
            MERGE (s)-[r:RELATES {id: $id}]->(t)
            SET r += $properties
            """
            session.run(
                query,
                source_id=relationship.source_id,
                target_id=relationship.target_id,
                id=relationship.id,
                properties=relationship.to_cypher_props()
            )
            logger.debug(f"Saved relationship: {relationship.id}")
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Retrieve a relationship by ID."""
        with self.driver.session() as session:
            query = """
            MATCH (s:Entity)-[r:RELATES {id: $id}]->(t:Entity)
            RETURN r, s.id as source_id, t.id as target_id
            """
            result = session.run(query, id=relationship_id)
            record = result.single()
            
            if record:
                props = dict(record["r"])
                props["source_id"] = record["source_id"]
                props["target_id"] = record["target_id"]
                return self._relationship_from_props(props)
            return None
    
    def update_relationship(self, relationship: Relationship) -> None:
        """Update an existing relationship."""
        self.save_relationship(relationship)  # MERGE handles both create and update
    
    def get_entity_relationships(
        self,
        entity_id: str,
        direction: str = "both",
        relationship_type: Optional[str] = None
    ) -> List[Relationship]:
        """Get all relationships for an entity."""
        with self.driver.session() as session:
            if direction == "outgoing":
                match_clause = "(e:Entity {id: $id})-[r:RELATES]->(t:Entity)"
            elif direction == "incoming":
                match_clause = "(s:Entity)-[r:RELATES]->(e:Entity {id: $id})"
            else:  # both
                match_clause = "(s:Entity)-[r:RELATES]-(e:Entity {id: $id})"
            
            query = f"""
            MATCH {match_clause}
            {'WHERE r.relationship_type = $rel_type' if relationship_type else ''}
            RETURN r, s.id as source_id, 
                   CASE WHEN s.id = $id THEN t.id ELSE e.id END as target_id
            """
            
            params = {"id": entity_id}
            if relationship_type:
                params["rel_type"] = relationship_type
            
            result = session.run(query, **params)
            
            relationships = []
            for record in result:
                props = dict(record["r"])
                props["source_id"] = record["source_id"]
                props["target_id"] = record["target_id"]
                relationships.append(self._relationship_from_props(props))
            
            return relationships
    
    def search_entities(
        self,
        entity_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        limit: int = 100
    ) -> List[Entity]:
        """Search for entities by type and/or name pattern."""
        with self.driver.session() as session:
            where_clauses = []
            params = {"limit": limit}
            
            if entity_type:
                where_clauses.append("e.entity_type = $entity_type")
                params["entity_type"] = entity_type
            
            if name_pattern:
                where_clauses.append("e.name =~ $pattern")
                params["pattern"] = f".*{name_pattern}.*"
            
            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            query = f"""
            MATCH (e:Entity)
            {where_clause}
            RETURN e
            ORDER BY e.confidence DESC
            LIMIT $limit
            """
            
            result = session.run(query, **params)
            
            entities = []
            for record in result:
                props = dict(record["e"])
                entities.append(self._entity_from_props(props))
            
            return entities
    
    def close(self) -> None:
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def _entity_from_props(self, props: Dict[str, Any]) -> Entity:
        """Create Entity object from Neo4j properties."""
        import json
        from datetime import datetime
        
        # Parse datetime strings
        # Handle optional timestamps
        if "created_at" in props:
            if isinstance(props["created_at"], str):
                props["created_at"] = datetime.fromisoformat(props["created_at"])
        else:
            props["created_at"] = datetime.utcnow()
            
        if "updated_at" in props:
            if isinstance(props["updated_at"], str):
                props["updated_at"] = datetime.fromisoformat(props["updated_at"])
        else:
            props["updated_at"] = datetime.utcnow()
        
        # Deserialize attributes
        if isinstance(props.get("attributes"), str):
            props["attributes"] = json.loads(props["attributes"])
        
        # Handle missing canonical_name
        if "canonical_name" not in props:
            props["canonical_name"] = props.get("name", "Unknown")
        
        # Handle missing surface_forms
        if "surface_forms" not in props:
            props["surface_forms"] = []
            
        # Handle missing mention_refs
        if "mention_refs" not in props:
            props["mention_refs"] = []
        
        return Entity(**props)
    
    def _relationship_from_props(self, props: Dict[str, Any]) -> Relationship:
        """Create Relationship object from Neo4j properties."""
        import json
        from datetime import datetime
        
        # Parse datetime strings
        # Handle optional timestamps
        if "created_at" in props:
            if isinstance(props["created_at"], str):
                props["created_at"] = datetime.fromisoformat(props["created_at"])
        else:
            props["created_at"] = datetime.utcnow()
            
        if "updated_at" in props:
            if isinstance(props["updated_at"], str):
                props["updated_at"] = datetime.fromisoformat(props["updated_at"])
        else:
            props["updated_at"] = datetime.utcnow()
        
        # Deserialize attributes
        if isinstance(props.get("attributes"), str):
            props["attributes"] = json.loads(props["attributes"])
        
        return Relationship(**props)