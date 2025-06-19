"""Service Manager - Singleton pattern for shared services

Implements performance optimization F1 from CLAUDE.md.
Provides shared service instances across all tools to prevent duplication.
Target: 10x speedup by eliminating redundant service creation.
"""

from typing import Optional, Dict, Any
import threading
from neo4j import GraphDatabase

from .identity_service import IdentityService
from .provenance_service import ProvenanceService
from .quality_service import QualityService


class ServiceManager:
    """Singleton service manager for shared services."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._identity_service = None
            self._provenance_service = None
            self._quality_service = None
            self._neo4j_driver = None
            self._neo4j_config = None
    
    @property
    def identity_service(self) -> IdentityService:
        """Get shared identity service instance."""
        if not self._identity_service:
            self._identity_service = IdentityService()
        return self._identity_service
    
    @property
    def provenance_service(self) -> ProvenanceService:
        """Get shared provenance service instance."""
        if not self._provenance_service:
            self._provenance_service = ProvenanceService()
        return self._provenance_service
    
    @property
    def quality_service(self) -> QualityService:
        """Get shared quality service instance."""
        if not self._quality_service:
            self._quality_service = QualityService()
        return self._quality_service
    
    def get_neo4j_driver(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password"
    ):
        """Get shared Neo4j driver instance with connection pooling."""
        config_key = f"{uri}:{user}"
        
        if self._neo4j_driver and self._neo4j_config == config_key:
            return self._neo4j_driver
        
        with self._lock:
            if self._neo4j_driver and self._neo4j_config != config_key:
                self._neo4j_driver.close()
                self._neo4j_driver = None
            
            if not self._neo4j_driver:
                try:
                    self._neo4j_driver = GraphDatabase.driver(
                        uri,
                        auth=(user, password),
                        max_connection_pool_size=50,
                        connection_acquisition_timeout=30.0,
                        keep_alive=True
                    )
                    self._neo4j_config = config_key
                    
                    # Test connection
                    with self._neo4j_driver.session() as session:
                        session.run("RETURN 1")
                    print(f"Shared Neo4j connection established to {uri}")
                except Exception as e:
                    print(f"WARNING: Neo4j connection failed: {e}")
                    print("Continuing without Neo4j - some features may be limited")
                    self._neo4j_driver = None
                    self._neo4j_config = None
        
        return self._neo4j_driver
    
    def close_all(self):
        """Close all managed resources."""
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
        self._neo4j_config = None
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about shared services."""
        return {
            "identity_service_active": self._identity_service is not None,
            "provenance_service_active": self._provenance_service is not None,
            "quality_service_active": self._quality_service is not None,
            "neo4j_driver_active": self._neo4j_driver is not None,
            "neo4j_config": self._neo4j_config
        }


# Global instance getter
def get_service_manager() -> ServiceManager:
    """Get the global service manager instance."""
    return ServiceManager()