"""Base class for Phase 1 tools that use Neo4j

Implements performance optimization F2 from CLAUDE.md.
Provides shared Neo4j driver management to prevent connection duplication.
Target: 3x speedup by eliminating redundant connections.
"""

from typing import Optional
from neo4j import GraphDatabase, Driver

from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService


class BaseNeo4jTool:
    """Base class for tools that need Neo4j access."""
    
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
        self.identity_service = identity_service
        self.provenance_service = provenance_service
        self.quality_service = quality_service
        
        # Use shared driver if provided, otherwise create own
        if shared_driver:
            self.driver = shared_driver
            self._owns_driver = False
        else:
            self._connect_neo4j(neo4j_uri, neo4j_user, neo4j_password)
            self._owns_driver = True
    
    def _connect_neo4j(self, uri: str, user: str, password: str):
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30.0,
                keep_alive=True
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"WARNING: Failed to connect to Neo4j: {e}")
            print("Continuing without Neo4j - graph operations will be limited")
            self.driver = None
    
    def close(self):
        """Close the connection if we own it."""
        if self._owns_driver and self.driver:
            self.driver.close()
            self.driver = None