"""
Real Identity Service using Neo4j
NO MOCKS - Real database operations only
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IdentityService:
    """Real identity service using Neo4j for entity management"""
    
    def __init__(self, neo4j_driver):
        """Initialize with real Neo4j driver"""
        if not neo4j_driver:
            raise ValueError("Neo4j driver is required for IdentityService")
        
        self.driver = neo4j_driver
        logger.info("IdentityService initialized with real Neo4j connection")
        
        # Create indexes for performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create Neo4j indexes for better performance"""
        try:
            with self.driver.session() as session:
                # Create index on mention_id
                session.run("""
                    CREATE INDEX mention_id_index IF NOT EXISTS
                    FOR (m:Mention) ON (m.mention_id)
                """)
                
                # Create index on entity_id  
                session.run("""
                    CREATE INDEX entity_id_index IF NOT EXISTS
                    FOR (e:Entity) ON (e.entity_id)
                """)
                
                # Create index on canonical_name
                session.run("""
                    CREATE INDEX canonical_name_index IF NOT EXISTS
                    FOR (e:Entity) ON (e.canonical_name)
                """)
                
                logger.info("Neo4j indexes created successfully")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def create_mention(self, surface_form: str, start_pos: int, end_pos: int,
                      source_ref: str, entity_type: str = None, 
                      confidence: float = 0.8) -> Dict[str, Any]:
        """
        Create entity mention in Neo4j
        
        Args:
            surface_form: The text of the mention
            start_pos: Start position in source text
            end_pos: End position in source text
            source_ref: Reference to source (chunk_id, doc_id, etc)
            entity_type: Type of entity (PERSON, ORG, GPE, etc)
            confidence: Confidence score (0-1)
            
        Returns:
            Dict with success status, mention_id, and entity_id
        """
        try:
            mention_id = f"mention_{uuid.uuid4().hex[:12]}"
            entity_id = f"entity_{uuid.uuid4().hex[:12]}"
            
            with self.driver.session() as session:
                # Create mention node
                result = session.run("""
                    CREATE (m:Mention {
                        mention_id: $mention_id,
                        surface_form: $surface_form,
                        start_pos: $start_pos,
                        end_pos: $end_pos,
                        source_ref: $source_ref,
                        entity_type: $entity_type,
                        confidence: $confidence,
                        created_at: datetime()
                    })
                    RETURN m.mention_id as mention_id
                """,
                mention_id=mention_id,
                surface_form=surface_form,
                start_pos=start_pos,
                end_pos=end_pos,
                source_ref=source_ref,
                entity_type=entity_type,
                confidence=confidence)
                
                record = result.single()
                
                if record:
                    logger.debug(f"Created mention {mention_id} for '{surface_form}'")
                    return {
                        "success": True,
                        "data": {
                            "mention_id": mention_id,
                            "entity_id": entity_id
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create mention in Neo4j"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating mention: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict[str, Any]]:
        """
        Get entity associated with a mention
        
        Args:
            mention_id: The mention ID
            
        Returns:
            Entity data or None if not found
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (m:Mention {mention_id: $mention_id})-[:REFERS_TO]->(e:Entity)
                    RETURN e
                """, mention_id=mention_id)
                
                record = result.single()
                if record:
                    return dict(record["e"])
                    
                # If no entity linked, check if mention exists
                mention_result = session.run("""
                    MATCH (m:Mention {mention_id: $mention_id})
                    RETURN m
                """, mention_id=mention_id)
                
                if mention_result.single():
                    logger.warning(f"Mention {mention_id} exists but has no linked entity")
                else:
                    logger.warning(f"Mention {mention_id} not found")
                    
                return None
                
        except Exception as e:
            logger.error(f"Error getting entity by mention: {e}")
            return None
    
    def merge_entities(self, entity_ids: List[str]) -> Optional[str]:
        """
        Merge multiple entities into one canonical entity
        
        Args:
            entity_ids: List of entity IDs to merge
            
        Returns:
            The canonical entity ID or None if failed
        """
        if len(entity_ids) < 2:
            logger.warning("Need at least 2 entities to merge")
            return None
            
        try:
            canonical_id = entity_ids[0]  # Use first as canonical
            
            with self.driver.session() as session:
                # Get all mentions pointing to entities to be merged
                result = session.run("""
                    MATCH (m:Mention)-[:REFERS_TO]->(e:Entity)
                    WHERE e.entity_id IN $entity_ids
                    RETURN m.mention_id as mention_id
                """, entity_ids=entity_ids[1:])  # Skip canonical
                
                mention_ids = [record["mention_id"] for record in result]
                
                # Update mentions to point to canonical entity
                if mention_ids:
                    session.run("""
                        MATCH (m:Mention)-[r:REFERS_TO]->(e:Entity)
                        WHERE m.mention_id IN $mention_ids
                        DELETE r
                        WITH m
                        MATCH (canonical:Entity {entity_id: $canonical_id})
                        CREATE (m)-[:REFERS_TO]->(canonical)
                    """, mention_ids=mention_ids, canonical_id=canonical_id)
                
                # Delete non-canonical entities
                session.run("""
                    MATCH (e:Entity)
                    WHERE e.entity_id IN $entity_ids
                    DELETE e
                """, entity_ids=entity_ids[1:])
                
                logger.info(f"Merged {len(entity_ids)} entities into {canonical_id}")
                return canonical_id
                
        except Exception as e:
            logger.error(f"Error merging entities: {e}")
            return None
    
    def find_similar_entities(self, surface_form: str, entity_type: str = None,
                            threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find entities similar to the given surface form
        
        Args:
            surface_form: Text to match
            entity_type: Optional entity type filter
            threshold: Similarity threshold (not used in simple implementation)
            
        Returns:
            List of similar entities
        """
        try:
            with self.driver.session() as session:
                # Simple implementation - exact and substring matching
                # For production, use embedding-based similarity
                
                if entity_type:
                    result = session.run("""
                        MATCH (e:Entity)
                        WHERE toLower(e.canonical_name) CONTAINS toLower($surface_form)
                        AND e.entity_type = $entity_type
                        RETURN e
                        LIMIT 10
                    """, surface_form=surface_form, entity_type=entity_type)
                else:
                    result = session.run("""
                        MATCH (e:Entity)
                        WHERE toLower(e.canonical_name) CONTAINS toLower($surface_form)
                        RETURN e
                        LIMIT 10
                    """, surface_form=surface_form)
                
                entities = []
                for record in result:
                    entity = dict(record["e"])
                    # Add simple similarity score based on string matching
                    if entity.get("canonical_name", "").lower() == surface_form.lower():
                        entity["similarity"] = 1.0
                    else:
                        entity["similarity"] = 0.8  # Substring match
                    entities.append(entity)
                
                return entities
                
        except Exception as e:
            logger.error(f"Error finding similar entities: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about entities and mentions"""
        try:
            with self.driver.session() as session:
                # Count mentions
                mention_result = session.run("MATCH (m:Mention) RETURN count(m) as count")
                mention_count = mention_result.single()["count"]
                
                # Count entities
                entity_result = session.run("MATCH (e:Entity) RETURN count(e) as count")
                entity_count = entity_result.single()["count"]
                
                # Count relationships
                rel_result = session.run("MATCH ()-[r:REFERS_TO]->() RETURN count(r) as count")
                rel_count = rel_result.single()["count"]
                
                return {
                    "mentions": mention_count,
                    "entities": entity_count,
                    "relationships": rel_count
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "mentions": 0,
                "entities": 0,
                "relationships": 0
            }


# Test function
def test_identity_service(driver):
    """Test the identity service with real Neo4j"""
    service = IdentityService(driver)
    
    # Test creating mention
    result = service.create_mention(
        surface_form="Barack Obama",
        start_pos=0,
        end_pos=12,
        source_ref="test_doc",
        entity_type="PERSON",
        confidence=0.95
    )
    
    if result["success"]:
        print(f"✅ Created mention: {result['data']['mention_id']}")
    else:
        print(f"❌ Failed to create mention: {result.get('error')}")
    
    # Test statistics
    stats = service.get_statistics()
    print(f"📊 Statistics: {stats}")
    
    return service