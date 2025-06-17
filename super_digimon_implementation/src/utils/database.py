"""Database management utilities."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Core services imported lazily to avoid circular import
from .config import Config
from .neo4j_manager import Neo4jManager
from .sqlite_manager import SQLiteManager
from .faiss_manager import FAISSManager


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Central database management for all three databases."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.ensure_directories()
        
        # Initialize database managers
        self.neo4j = Neo4jManager(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password
        )
        
        self.sqlite = SQLiteManager(
            db_path=self.config.sqlite_db_path
        )
        
        self.faiss = FAISSManager(
            index_path=self.config.faiss_index_path
        )
        
        # Initialize core services
        self._identity_service = None
        self._provenance_service = None
        self._quality_service = None
        self._workflow_state_service = None
        
        logger.info("DatabaseManager initialized")
    
    def initialize(self) -> None:
        """Initialize all databases and create schemas."""
        logger.info("Initializing databases...")
        
        # Initialize Neo4j
        self.neo4j.initialize_schema()
        
        # Initialize SQLite
        self.sqlite.initialize_schema()
        
        # Initialize FAISS
        self.faiss.initialize_index()
        
        logger.info("All databases initialized successfully")
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all databases."""
        return {
            "neo4j": self.neo4j.health_check(),
            "sqlite": self.sqlite.health_check(),
            "faiss": self.faiss.health_check()
        }
    
    def close(self) -> None:
        """Close all database connections."""
        self.neo4j.close()
        self.sqlite.close()
        self.faiss.close()
        logger.info("All database connections closed")
    
    # Core service accessors
    def get_identity_service(self):
        """Get or create identity service."""
        if not self._identity_service:
            from ..core import IdentityService
            self._identity_service = IdentityService(self)
        return self._identity_service
    
    def get_provenance_service(self):
        """Get or create provenance service."""
        if not self._provenance_service:
            from ..core import ProvenanceService
            self._provenance_service = ProvenanceService(self)
        return self._provenance_service
    
    def get_quality_service(self):
        """Get or create quality service."""
        if not self._quality_service:
            from ..core import QualityService
            self._quality_service = QualityService(self)
        return self._quality_service
    
    def get_workflow_state_service(self):
        """Get or create workflow state service."""
        if not self._workflow_state_service:
            from ..core import WorkflowStateService
            self._workflow_state_service = WorkflowStateService(
                self,
                checkpoint_dir=self.config.checkpoint_dir
            )
        return self._workflow_state_service
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()