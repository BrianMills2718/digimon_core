"""
Real Provenance Service using SQLite
NO MOCKS - Real database operations only
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProvenanceService:
    """Real provenance tracking using SQLite database"""
    
    def __init__(self, connection=None):
        """Initialize with SQLite connection"""
        if connection:
            self.conn = connection
            self.owns_connection = False
        else:
            # Create new connection if not provided
            db_path = Path("provenance.db")
            self.conn = sqlite3.connect(str(db_path))
            self.owns_connection = True
            logger.info(f"ProvenanceService connected to {db_path}")
        
        # Create tables
        self._create_tables()
    
    def _create_tables(self):
        """Create provenance tables if they don't exist"""
        try:
            # Operations table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    operation_id TEXT PRIMARY KEY,
                    tool_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    inputs TEXT,
                    parameters TEXT,
                    outputs TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    metadata TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_ms INTEGER
                )
            """)
            
            # Lineage table for tracking dependencies
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_operation_id TEXT NOT NULL,
                    target_operation_id TEXT NOT NULL,
                    relationship_type TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (source_operation_id) REFERENCES operations(operation_id),
                    FOREIGN KEY (target_operation_id) REFERENCES operations(operation_id)
                )
            """)
            
            # Create indexes for performance
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_operations_tool 
                ON operations(tool_id)
            """)
            
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_operations_time 
                ON operations(started_at)
            """)
            
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lineage_source 
                ON lineage(source_operation_id)
            """)
            
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_lineage_target 
                ON lineage(target_operation_id)
            """)
            
            self.conn.commit()
            logger.info("Provenance tables and indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating provenance tables: {e}")
            raise
    
    def start_operation(self, tool_id: str, operation_type: str,
                       inputs: List[Any] = None, parameters: Dict[str, Any] = None) -> str:
        """
        Start tracking an operation
        
        Args:
            tool_id: ID of the tool performing the operation
            operation_type: Type of operation being performed
            inputs: Input data/references
            parameters: Operation parameters
            
        Returns:
            Operation ID for tracking
        """
        try:
            operation_id = f"op_{uuid.uuid4().hex[:16]}"
            started_at = datetime.now().isoformat()
            
            self.conn.execute("""
                INSERT INTO operations 
                (operation_id, tool_id, operation_type, inputs, parameters, started_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                operation_id,
                tool_id,
                operation_type,
                json.dumps(inputs) if inputs else "[]",
                json.dumps(parameters) if parameters else "{}",
                started_at
            ))
            self.conn.commit()
            
            logger.debug(f"Started operation {operation_id} for tool {tool_id}")
            return operation_id
            
        except Exception as e:
            logger.error(f"Error starting operation: {e}")
            raise
    
    def complete_operation(self, operation_id: str, outputs: List[Any] = None,
                          success: bool = True, metadata: Dict[str, Any] = None,
                          error_message: str = None) -> Dict[str, Any]:
        """
        Complete tracking an operation
        
        Args:
            operation_id: Operation ID to complete
            outputs: Output data/references
            success: Whether operation succeeded
            metadata: Additional metadata
            error_message: Error message if failed
            
        Returns:
            Completion status
        """
        try:
            completed_at = datetime.now().isoformat()
            
            # Get start time to calculate duration
            cursor = self.conn.execute("""
                SELECT started_at FROM operations WHERE operation_id = ?
            """, (operation_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.error(f"Operation {operation_id} not found")
                return {"success": False, "error": "Operation not found"}
            
            started_at = datetime.fromisoformat(row[0])
            completed = datetime.fromisoformat(completed_at)
            duration_ms = int((completed - started_at).total_seconds() * 1000)
            
            # Update operation
            self.conn.execute("""
                UPDATE operations
                SET outputs = ?, success = ?, metadata = ?, error_message = ?,
                    completed_at = ?, duration_ms = ?
                WHERE operation_id = ?
            """, (
                json.dumps(outputs) if outputs else "[]",
                success,
                json.dumps(metadata) if metadata else "{}",
                error_message,
                completed_at,
                duration_ms,
                operation_id
            ))
            self.conn.commit()
            
            logger.debug(f"Completed operation {operation_id} (success={success}, duration={duration_ms}ms)")
            
            return {
                "success": True,
                "operation_id": operation_id,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"Error completing operation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_lineage(self, source_operation_id: str, target_operation_id: str,
                    relationship_type: str = "DERIVED_FROM") -> bool:
        """
        Add lineage relationship between operations
        
        Args:
            source_operation_id: Source operation
            target_operation_id: Target operation  
            relationship_type: Type of relationship
            
        Returns:
            Success status
        """
        try:
            self.conn.execute("""
                INSERT INTO lineage 
                (source_operation_id, target_operation_id, relationship_type, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                source_operation_id,
                target_operation_id,
                relationship_type,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            
            logger.debug(f"Added lineage: {source_operation_id} -> {target_operation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding lineage: {e}")
            return False
    
    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific operation"""
        try:
            cursor = self.conn.execute("""
                SELECT * FROM operations WHERE operation_id = ?
            """, (operation_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                operation = dict(zip(columns, row))
                
                # Parse JSON fields
                operation["inputs"] = json.loads(operation.get("inputs", "[]"))
                operation["outputs"] = json.loads(operation.get("outputs", "[]"))
                operation["parameters"] = json.loads(operation.get("parameters", "{}"))
                operation["metadata"] = json.loads(operation.get("metadata", "{}"))
                
                return operation
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting operation: {e}")
            return None
    
    def get_lineage(self, operation_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get lineage for an operation
        
        Args:
            operation_id: Operation to get lineage for
            direction: "upstream", "downstream", or "both"
            
        Returns:
            List of related operations
        """
        try:
            lineage = []
            
            if direction in ["upstream", "both"]:
                # Get upstream operations (what this operation depends on)
                cursor = self.conn.execute("""
                    SELECT o.*, l.relationship_type
                    FROM operations o
                    JOIN lineage l ON o.operation_id = l.source_operation_id
                    WHERE l.target_operation_id = ?
                """, (operation_id,))
                
                for row in cursor:
                    columns = [desc[0] for desc in cursor.description]
                    op = dict(zip(columns, row))
                    op["direction"] = "upstream"
                    lineage.append(op)
            
            if direction in ["downstream", "both"]:
                # Get downstream operations (what depends on this operation)
                cursor = self.conn.execute("""
                    SELECT o.*, l.relationship_type
                    FROM operations o
                    JOIN lineage l ON o.operation_id = l.target_operation_id
                    WHERE l.source_operation_id = ?
                """, (operation_id,))
                
                for row in cursor:
                    columns = [desc[0] for desc in cursor.description]
                    op = dict(zip(columns, row))
                    op["direction"] = "downstream"
                    lineage.append(op)
            
            return lineage
            
        except Exception as e:
            logger.error(f"Error getting lineage: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get provenance statistics"""
        try:
            stats = {}
            
            # Total operations
            cursor = self.conn.execute("SELECT COUNT(*) FROM operations")
            stats["total_operations"] = cursor.fetchone()[0]
            
            # Successful operations
            cursor = self.conn.execute("SELECT COUNT(*) FROM operations WHERE success = 1")
            stats["successful_operations"] = cursor.fetchone()[0]
            
            # Failed operations
            cursor = self.conn.execute("SELECT COUNT(*) FROM operations WHERE success = 0")
            stats["failed_operations"] = cursor.fetchone()[0]
            
            # Operations by tool
            cursor = self.conn.execute("""
                SELECT tool_id, COUNT(*) as count 
                FROM operations 
                GROUP BY tool_id
            """)
            stats["operations_by_tool"] = {row[0]: row[1] for row in cursor}
            
            # Average duration
            cursor = self.conn.execute("""
                SELECT AVG(duration_ms) 
                FROM operations 
                WHERE duration_ms IS NOT NULL
            """)
            avg_duration = cursor.fetchone()[0]
            stats["average_duration_ms"] = avg_duration if avg_duration else 0
            
            # Lineage relationships
            cursor = self.conn.execute("SELECT COUNT(*) FROM lineage")
            stats["lineage_relationships"] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        if self.owns_connection and self.conn:
            self.conn.close()
            logger.info("ProvenanceService connection closed")


# Test function
def test_provenance_service():
    """Test the provenance service with real SQLite"""
    service = ProvenanceService()
    
    # Test starting an operation
    op_id = service.start_operation(
        tool_id="T01_PDF_LOADER",
        operation_type="load_document",
        inputs=["test.pdf"],
        parameters={"format": "pdf", "confidence_threshold": 0.8}
    )
    print(f"✅ Started operation: {op_id}")
    
    # Test completing an operation
    result = service.complete_operation(
        operation_id=op_id,
        outputs=["doc_123"],
        success=True,
        metadata={"pages": 10, "text_length": 5000}
    )
    print(f"✅ Completed operation: {result}")
    
    # Test getting operation
    operation = service.get_operation(op_id)
    print(f"📄 Operation details: {operation}")
    
    # Test statistics
    stats = service.get_statistics()
    print(f"📊 Statistics: {stats}")
    
    return service


if __name__ == "__main__":
    test_provenance_service()