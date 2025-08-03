"""SQLite Database Manager - Core Infrastructure

Provides centralized SQLite database management for the GraphRAG system,
including connection pooling, transaction management, and schema migrations.
"""

import sqlite3
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Iterator
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SQLiteManager:
    """Centralized SQLite database manager with connection pooling"""
    
    def __init__(self, database_path: str = None):
        """Initialize SQLite manager with database path"""
        if database_path is None:
            from .standard_config import get_file_path
            database_path = f"{get_file_path('data_dir')}/kgas.db"
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._connections = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            self._create_core_tables(conn)
    
    def _create_core_tables(self, conn: sqlite3.Connection):
        """Create core tables for the system"""
        # Identity service tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                entity_type TEXT,
                confidence REAL,
                mention_count INTEGER DEFAULT 0,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mentions (
                mention_id TEXT PRIMARY KEY,
                entity_id TEXT,
                surface_form TEXT NOT NULL,
                start_pos INTEGER,
                end_pos INTEGER,
                source_ref TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities (entity_id)
            )
        """)
        
        # Provenance service tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                tool_id TEXT,
                operation_type TEXT,
                inputs TEXT,
                outputs TEXT,
                parameters TEXT,
                success BOOLEAN,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Quality service tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quality_assessments (
                assessment_id TEXT PRIMARY KEY,
                target_ref TEXT,
                confidence REAL,
                quality_factors TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mentions_entity ON mentions(entity_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_operations_tool ON operations(tool_id)")
        
        conn.commit()
        logger.info("SQLite database initialized with core tables")
    
    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get database connection with proper cleanup"""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id not in self._connections:
                conn = sqlite3.connect(
                    str(self.database_path),
                    check_same_thread=False,
                    timeout=30.0
                )
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                self._connections[thread_id] = conn
            
            connection = self._connections[thread_id]
        
        try:
            yield connection
        except Exception as e:
            connection.rollback()
            raise
        finally:
            # Keep connection open for reuse within thread
            pass
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute multiple statements with parameter lists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in database"""
        rows = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row['name'] for row in rows]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table"""
        rows = self.execute_query(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in rows]
    
    def vacuum(self):
        """Vacuum database to reclaim space"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.commit()
        logger.info("Database vacuumed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        # Get table counts
        for table in self.get_tables():
            if not table.startswith('sqlite_'):
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = count_result[0]['count'] if count_result else 0
        
        # Get database size
        stats['database_size_bytes'] = self.database_path.stat().st_size
        stats['database_path'] = str(self.database_path)
        
        return stats
    
    def cleanup(self):
        """Clean up connections"""
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()
        logger.info("SQLite connections cleaned up")


# Global singleton
_sqlite_manager = None
_sqlite_lock = threading.Lock()


def get_sqlite_manager(database_path: str = None) -> SQLiteManager:
    """Get or create global SQLite manager instance"""
    global _sqlite_manager
    
    if _sqlite_manager is None:
        with _sqlite_lock:
            if _sqlite_manager is None:
                _sqlite_manager = SQLiteManager(database_path)
    
    return _sqlite_manager