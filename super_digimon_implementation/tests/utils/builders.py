"""Test data builders for consistent test entity creation."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from neo4j import Session


class TestEntityBuilder:
    """Builder for creating test entities with all required fields."""
    
    @staticmethod
    def create_entity(
        session: Session,
        id: Optional[str] = None,
        name: str = "Test Entity",
        entity_type: str = "TEST",
        canonical_name: Optional[str] = None,
        confidence: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None,
        surface_forms: Optional[List[str]] = None,
        mention_refs: Optional[List[str]] = None,
        embedding_ref: Optional[str] = None,
        quality_tier: str = "high",
        warnings: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None
    ) -> str:
        """Create a test entity with ALL required fields.
        
        Args:
            session: Neo4j session
            id: Entity ID (generated if not provided)
            name: Entity name
            entity_type: Type of entity
            canonical_name: Canonical form (defaults to name)
            confidence: Confidence score
            attributes: Additional attributes
            surface_forms: Alternative names
            mention_refs: References to mentions
            embedding_ref: Reference to embedding
            quality_tier: Quality tier (high/medium/low)
            warnings: List of warnings
            evidence: List of evidence
            
        Returns:
            Entity ID
        """
        if id is None:
            id = f"test_ent_{uuid4().hex[:8]}"
        
        if canonical_name is None:
            canonical_name = name
            
        if attributes is None:
            attributes = {}
            
        if surface_forms is None:
            surface_forms = [name]
            
        if mention_refs is None:
            mention_refs = []
            
        if warnings is None:
            warnings = []
            
        if evidence is None:
            evidence = []
        
        # Serialize complex fields
        import json
        attributes_json = json.dumps(attributes)
        
        query = """
        CREATE (e:Entity {
            id: $id,
            name: $name,
            entity_type: $entity_type,
            canonical_name: $canonical_name,
            confidence: $confidence,
            attributes: $attributes,
            surface_forms: $surface_forms,
            mention_refs: $mention_refs,
            embedding_ref: $embedding_ref,
            quality_tier: $quality_tier,
            warnings: $warnings,
            evidence: $evidence,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN e.id as id
        """
        
        result = session.run(
            query,
            id=id,
            name=name,
            entity_type=entity_type,
            canonical_name=canonical_name,
            confidence=confidence,
            attributes=attributes_json,
            surface_forms=surface_forms,
            mention_refs=mention_refs,
            embedding_ref=embedding_ref,
            quality_tier=quality_tier,
            warnings=warnings,
            evidence=evidence
        )
        
        return result.single()["id"]
    
    @staticmethod
    def create_entities_with_relationships(
        session: Session,
        entities_data: List[Dict[str, Any]],
        relationships_data: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Create multiple entities with relationships.
        
        Args:
            session: Neo4j session
            entities_data: List of entity data dicts
            relationships_data: List of relationship data dicts
                Each should have: source_name, target_name, relationship_type
                
        Returns:
            Dict mapping entity names to IDs
        """
        entity_ids = {}
        
        # Create entities
        for entity_data in entities_data:
            entity_id = TestEntityBuilder.create_entity(session, **entity_data)
            entity_ids[entity_data.get("name", "Test Entity")] = entity_id
        
        # Create relationships
        for rel_data in relationships_data:
            source_name = rel_data["source_name"]
            target_name = rel_data["target_name"]
            rel_type = rel_data.get("relationship_type", "RELATES")
            
            if source_name not in entity_ids or target_name not in entity_ids:
                raise ValueError(f"Entity not found for relationship: {source_name} -> {target_name}")
            
            rel_id = f"test_rel_{uuid4().hex[:8]}"
            
            query = f"""
            MATCH (s:Entity {{id: $source_id}})
            MATCH (t:Entity {{id: $target_id}})
            CREATE (s)-[r:RELATES {{
                id: $rel_id,
                relationship_type: $rel_type,
                confidence: $confidence,
                created_at: datetime(),
                updated_at: datetime()
            }}]->(t)
            """
            
            session.run(
                query,
                source_id=entity_ids[source_name],
                target_id=entity_ids[target_name],
                rel_id=rel_id,
                rel_type=rel_type,
                confidence=rel_data.get("confidence", 1.0)
            )
        
        return entity_ids


class TestGraphBuilder:
    """Builder for creating test graph structures."""
    
    @staticmethod
    def create_simple_chain(
        session: Session,
        length: int = 3,
        entity_prefix: str = "Entity"
    ) -> List[str]:
        """Create a simple chain of entities: A -> B -> C.
        
        Args:
            session: Neo4j session
            length: Number of entities in chain
            entity_prefix: Prefix for entity names
            
        Returns:
            List of entity IDs
        """
        entities = []
        entity_ids = []
        
        for i in range(length):
            entity_data = {
                "name": f"{entity_prefix}_{i}",
                "entity_type": "TEST_CHAIN"
            }
            entities.append(entity_data)
        
        # Create relationships
        relationships = []
        for i in range(length - 1):
            relationships.append({
                "source_name": f"{entity_prefix}_{i}",
                "target_name": f"{entity_prefix}_{i+1}",
                "relationship_type": "NEXT"
            })
        
        id_map = TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
        
        return [id_map[f"{entity_prefix}_{i}"] for i in range(length)]
    
    @staticmethod
    def create_hub_spoke(
        session: Session,
        hub_name: str = "Hub",
        spoke_count: int = 5
    ) -> Dict[str, str]:
        """Create a hub-and-spoke pattern.
        
        Args:
            session: Neo4j session
            hub_name: Name of central hub entity
            spoke_count: Number of spoke entities
            
        Returns:
            Dict mapping entity names to IDs
        """
        entities = [{"name": hub_name, "entity_type": "HUB"}]
        relationships = []
        
        for i in range(spoke_count):
            spoke_name = f"Spoke_{i}"
            entities.append({
                "name": spoke_name,
                "entity_type": "SPOKE"
            })
            relationships.append({
                "source_name": hub_name,
                "target_name": spoke_name,
                "relationship_type": "CONNECTS"
            })
        
        return TestEntityBuilder.create_entities_with_relationships(
            session, entities, relationships
        )
    
    @staticmethod
    def create_disconnected_components(
        session: Session,
        component_count: int = 3,
        size_per_component: int = 2
    ) -> List[List[str]]:
        """Create disconnected graph components.
        
        Args:
            session: Neo4j session
            component_count: Number of disconnected components
            size_per_component: Entities per component
            
        Returns:
            List of lists, each containing entity IDs for a component
        """
        components = []
        
        for c in range(component_count):
            component_ids = TestGraphBuilder.create_simple_chain(
                session,
                length=size_per_component,
                entity_prefix=f"Component{c}_Entity"
            )
            components.append(component_ids)
        
        return components


class TestDataCleaner:
    """Utility for cleaning up test data."""
    
    @staticmethod
    def cleanup_test_entities(session: Session, prefix: str = "test_"):
        """Delete all test entities and relationships.
        
        Args:
            session: Neo4j session
            prefix: Prefix for test entity IDs to delete
        """
        query = """
        MATCH (e:Entity)
        WHERE e.id STARTS WITH $prefix
        DETACH DELETE e
        """
        session.run(query, prefix=prefix)
        
    @staticmethod
    def cleanup_all(session: Session):
        """Delete ALL entities and relationships. Use with caution!"""
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        session.run(query)