"""Base class for Phase 1 tools that use Neo4j

Implements performance optimization F2 from CLAUDE.md.
Provides shared Neo4j driver management to prevent connection duplication.
Target: 3x speedup by eliminating redundant connections.
"""

from typing import Optional
from neo4j import GraphDatabase, Driver

try:
    from src.core.identity_service import IdentityService
    from src.core.provenance_service import ProvenanceService
    from src.core.quality_service import QualityService
    from src.core.config_manager import ConfigurationManager, get_config
except ImportError:
    from core.identity_service import IdentityService
    from core.provenance_service import ProvenanceService
    from core.quality_service import QualityService
    from src.core.config_manager import ConfigurationManager, get_config


class BaseNeo4jTool:
    """Base class for tools that need Neo4j access."""
    
    def __init__(
        self,
        identity_service: IdentityService = None,
        provenance_service: ProvenanceService = None,
        quality_service: QualityService = None,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_password: str = None,
        shared_driver: Optional[Driver] = None,
        config_manager: ConfigurationManager = None
    ):
        # If services not provided, get them from service_manager
        if identity_service is None or provenance_service is None or quality_service is None:
            from src.core.service_manager import get_service_manager
            service_manager = get_service_manager()
            
            self.identity_service = identity_service or service_manager.identity_service
            self.provenance_service = provenance_service or service_manager.provenance_service
            self.quality_service = quality_service or service_manager.quality_service
        else:
            self.identity_service = identity_service
            self.provenance_service = provenance_service
            self.quality_service = quality_service
        
        # Get Neo4j config from ConfigurationManager if not provided
        if config_manager is None:
            config_manager = get_config()
        neo4j_config = config_manager.get_neo4j_config()
        
        final_neo4j_uri = neo4j_uri or neo4j_config['uri']
        final_neo4j_user = neo4j_user or neo4j_config['user']
        final_neo4j_password = neo4j_password or neo4j_config['password']
        
        # Use shared driver if provided, otherwise create own
        if shared_driver:
            self.driver = shared_driver
            self._owns_driver = False
        else:
            self._connect_neo4j(final_neo4j_uri, final_neo4j_user, final_neo4j_password)
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
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["connection", "network", "timeout", "unreachable", "refused"]):
                print(f"WARNING: Neo4j network connection failed: {e}")
                print("Network connectivity issue - check if Neo4j is running and accessible")
            elif any(keyword in error_msg for keyword in ["authentication", "auth", "credentials", "unauthorized"]):
                print(f"WARNING: Neo4j authentication failed: {e}")
                print("Authentication error - verify username and password are correct")
            else:
                print(f"WARNING: Failed to connect to Neo4j: {e}")
            print("Continuing without Neo4j - graph operations will be limited")
            self.driver = None
    
    def close(self):
        """Close the connection if we own it."""
        if self._owns_driver and self.driver:
            self.driver.close()
            self.driver = None