"""Service Manager - Singleton pattern for shared services

Implements performance optimization F1 from CLAUDE.md.
Provides shared service instances across all tools to prevent duplication.
Target: 10x speedup by eliminating redundant service creation.
"""

from typing import Optional, Dict, Any
import threading
from neo4j import GraphDatabase
import sqlite3
from pathlib import Path

from src.services.identity_service import IdentityService as RealIdentityService
from src.services.provenance_service import ProvenanceService as RealProvenanceService
from src.services.quality_service import QualityService as RealQualityService
from .config_manager import get_config
from .logging_config import get_logger


class ServiceManager:
    """Singleton service manager for shared services."""
    
    _instance = None
    _lock = threading.Lock()
    _init_lock = threading.Lock()  # Additional lock for thread-safe initialization
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        with self._init_lock:  # Protect initialization
            if not hasattr(self, "_initialized"):
                self._initialized = True
                self._identity_service = None
                self._provenance_service = None
                self._quality_service = None
                self._neo4j_driver = None
                self._neo4j_config = None
                self._identity_config = None  # Store identity service configuration
                self.logger = get_logger("core.service_manager")
    
    @property
    def identity_service(self) -> RealIdentityService:
        """Get shared identity service instance."""
        if not self._identity_service:
            # Get Neo4j driver first
            neo4j_driver = self.get_neo4j_driver()
            if neo4j_driver:
                self._identity_service = RealIdentityService(neo4j_driver)
                self.logger.info("Initialized real IdentityService with Neo4j")
            else:
                self.logger.error("Cannot create IdentityService without Neo4j connection")
                raise RuntimeError("Neo4j connection required for IdentityService")
        return self._identity_service
    
    def configure_identity_service(self, **config):
        """Configure identity service before first use.
        
        Args:
            use_embeddings: Enable semantic similarity
            persistence_path: Path to SQLite database
            similarity_threshold: Threshold for entity matching
            etc.
        """
        if self._identity_service:
            raise RuntimeError("Cannot configure identity service after it's been created")
        self._identity_config = config
    
    @property
    def provenance_service(self) -> RealProvenanceService:
        """Get shared provenance service instance."""
        if not self._provenance_service:
            # Create SQLite connection for provenance
            db_path = Path("data/provenance.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            self._provenance_service = RealProvenanceService(connection=conn)
            self.logger.info(f"Initialized real ProvenanceService with SQLite at {db_path}")
        return self._provenance_service
    
    @property
    def quality_service(self) -> RealQualityService:
        """Get shared quality service instance."""
        if not self._quality_service:
            # Get Neo4j driver first
            neo4j_driver = self.get_neo4j_driver()
            if neo4j_driver:
                self._quality_service = RealQualityService(neo4j_driver)
                self.logger.info("Initialized real QualityService with Neo4j")
            else:
                self.logger.error("Cannot create QualityService without Neo4j connection")
                raise RuntimeError("Neo4j connection required for QualityService")
        return self._quality_service
    
    def get_neo4j_driver(
        self,
        uri: str = None,
        user: str = None,
        password: str = None
    ):
        """Get shared Neo4j driver instance with connection pooling using configuration."""
        # Load configuration if parameters not provided
        config = get_config()
        database_config = config.database  # Changed from neo4j to database
        
        # Use provided parameters or fall back to configuration
        uri = uri or database_config.uri
        user = user or database_config.username  # Changed from user to username
        password = password or database_config.password
        
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
                        max_connection_pool_size=database_config.max_connection_pool_size,
                        connection_acquisition_timeout=database_config.connection_acquisition_timeout,
                        keep_alive=database_config.keep_alive
                    )
                    self._neo4j_config = config_key
                    
                    # Test connection with proper single record handling
                    with self._neo4j_driver.session() as session:
                        result = session.run("RETURN 1 as test")
                        result.single()  # Consume single record properly
                    self.logger.info(f"Shared Neo4j connection established to {uri}")
                except Exception as e:
                    self.logger.info(f"WARNING: Neo4j connection failed: {e}")
                    self.logger.info("Continuing without Neo4j - some features may be limited")
                    self._neo4j_driver = None
                    self._neo4j_config = None
        
        return self._neo4j_driver
    
    def close_all(self):
        """Close all managed resources."""
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
        self._neo4j_config = None
    
    def get_identity_service(self) -> RealIdentityService:
        """Get shared identity service instance."""
        return self.identity_service
    
    def get_provenance_service(self) -> RealProvenanceService:
        """Get shared provenance service instance."""
        return self.provenance_service
    
    def get_quality_service(self) -> RealQualityService:
        """Get shared quality service instance."""
        return self.quality_service
    
    def get_neo4j_manager(self):
        """Get Neo4j manager instance for compatibility."""
        from .neo4j_manager import Neo4jManager
        from src.core.config_manager import get_config

        return Neo4jManager()
    
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