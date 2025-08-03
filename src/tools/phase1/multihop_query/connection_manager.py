from src.core.standard_config import get_database_uri
"""
Neo4j Connection Manager for Multi-hop Query Tool

Handles Neo4j connection management, session pooling, and database operations
for the multi-hop query tool.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

logger = logging.getLogger(__name__)


class Neo4jConnectionManager:
    """Manages Neo4j connections and sessions for multi-hop queries"""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self.connection_stats = {
            "connections_created": 0,
            "sessions_created": 0,
            "queries_executed": 0,
            "errors_encountered": 0
        }
        self.logger = logging.getLogger("multihop_query.connection_manager")
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Neo4j connection with environment variables"""
        if not NEO4J_AVAILABLE:
            self.logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            return
        
        try:
            # Load environment variables 
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Get Neo4j settings from environment or config
            neo4j_uri = get_database_uri()
            neo4j_user = os.getenv('NEO4J_USER', "neo4j")
            neo4j_password = os.getenv('NEO4J_PASSWORD')
            
            if not neo4j_password:
                raise ValueError("Neo4j password must be provided via NEO4J_PASSWORD environment variable")
            
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            self.connection_stats["connections_created"] += 1
            self.logger.info("Neo4j connection established successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to connect to Neo4j: {e}")
            self.connection_stats["errors_encountered"] += 1
            self.driver = None
    
    @contextmanager
    def get_session(self):
        """Get a Neo4j session with proper error handling"""
        if not self.driver:
            raise ConnectionError("Neo4j connection not available")
        
        session = None
        try:
            session = self.driver.session()
            self.connection_stats["sessions_created"] += 1
            yield session
        except Exception as e:
            self.connection_stats["errors_encountered"] += 1
            self.logger.error(f"Neo4j session error: {e}")
            raise
        finally:
            if session:
                session.close()
    
    def execute_query(self, cypher: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        if not self.driver:
            raise ConnectionError("Neo4j connection not available")
        
        try:
            with self.get_session() as session:
                result = session.run(cypher, parameters or {})
                records = [record.data() for record in result]
                self.connection_stats["queries_executed"] += 1
                return records
        except Exception as e:
            self.connection_stats["errors_encountered"] += 1
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if Neo4j connection is working"""
        try:
            if not self.driver:
                return False
            
            with self.get_session() as session:
                session.run("RETURN 1 as test")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get basic graph statistics"""
        if not self.driver:
            return {"error": "No Neo4j connection"}
        
        try:
            with self.get_session() as session:
                # Count entities
                entity_result = session.run("MATCH (e:Entity) RETURN count(e) as entity_count")
                entity_count = entity_result.single()["entity_count"]
                
                # Count relationships
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = rel_result.single()["rel_count"]
                
                # Count unique entity types
                type_result = session.run("""
                    MATCH (e:Entity) 
                    WHERE e.entity_type IS NOT NULL
                    RETURN count(DISTINCT e.entity_type) as type_count
                """)
                type_count = type_result.single()["type_count"]
                
                return {
                    "entity_count": entity_count,
                    "relationship_count": rel_count,
                    "entity_type_count": type_count,
                    "connection_healthy": True
                }
        except Exception as e:
            self.logger.error(f"Failed to get graph stats: {e}")
            return {"error": str(e), "connection_healthy": False}
    
    def find_entities_by_name(self, entity_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find entities by name similarity"""
        cypher = """
        MATCH (e:Entity)
        WHERE toLower(e.canonical_name) CONTAINS toLower($entity_name)
           OR toLower(e.canonical_name) = toLower($entity_name)
        RETURN e.entity_id as entity_id,
               e.canonical_name as canonical_name,
               e.entity_type as entity_type,
               e.confidence as confidence,
               e.pagerank_score as pagerank_score
        ORDER BY CASE WHEN e.pagerank_score IS NULL THEN 0 ELSE e.pagerank_score END DESC
        LIMIT $limit
        """
        
        return self.execute_query(cypher, {
            "entity_name": entity_name,
            "limit": limit
        })
    
    def find_paths_between_entities(
        self, 
        source_id: str, 
        target_id: str, 
        max_hops: int,
        limit_per_hop: int = 5
    ) -> List[Dict[str, Any]]:
        """Find paths between two entities with specified hop count"""
        all_paths = []
        
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
            LIMIT $limit_per_hop
            """
            
            try:
                results = self.execute_query(cypher, {
                    "source_id": source_id,
                    "target_id": target_id,
                    "limit_per_hop": limit_per_hop
                })
                
                for record in results:
                    all_paths.append({
                        "path_weight": record["path_weight"],
                        "path_names": record["path_names"],
                        "relationship_types": record["relationship_types"],
                        "path_length": record["path_length"],
                        "hop_count": hop_count
                    })
            except Exception as e:
                self.logger.error(f"Path finding failed for {hop_count} hops: {e}")
                continue
        
        return all_paths
    
    def find_related_entities(
        self, 
        entity_id: str, 
        max_hops: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find entities related to a given entity within max_hops"""
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
        ORDER BY CASE WHEN pagerank_score IS NULL THEN 0 ELSE pagerank_score END DESC, connection_count DESC
        LIMIT $limit
        """
        
        return self.execute_query(cypher, {
            "entity_id": entity_id,
            "limit": limit
        })
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection and query statistics"""
        return {
            **self.connection_stats,
            "driver_available": self.driver is not None,
            "neo4j_driver_installed": NEO4J_AVAILABLE
        }
    
    def cleanup(self) -> bool:
        """Clean up Neo4j connection"""
        if self.driver:
            try:
                self.driver.close()
                self.driver = None
                self.logger.info("Neo4j connection closed successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to close Neo4j driver: {e}")
                return False
        return True
    
    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.cleanup()