#!/usr/bin/env python3
"""
Provenance Persistence Layer
Stores provenance data in SQLite for persistent tracking and querying
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class ProvenancePersistence:
    """Persistent storage for provenance tracking data"""
    
    def __init__(self, db_path: str = "data/provenance.db"):
        """Initialize persistence layer
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database schema
        self._init_database()
        
        logger.info(f"Provenance persistence initialized at {self.db_path}")
    
    @property
    def connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _init_database(self):
        """Initialize database schema"""
        with self.connection as conn:
            # Operations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    operation_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    tool_id TEXT,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    agent_data TEXT,  -- JSON
                    parameters TEXT,  -- JSON
                    metadata TEXT,    -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Operation inputs table (used relationship)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operation_inputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL,
                    input_ref TEXT NOT NULL,
                    input_type TEXT,
                    input_metadata TEXT,  -- JSON
                    FOREIGN KEY (operation_id) REFERENCES operations(operation_id),
                    UNIQUE(operation_id, input_ref)
                )
            """)
            
            # Operation outputs table (generated relationship)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operation_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL,
                    output_ref TEXT NOT NULL,
                    output_type TEXT,
                    output_metadata TEXT,  -- JSON
                    FOREIGN KEY (operation_id) REFERENCES operations(operation_id),
                    UNIQUE(operation_id, output_ref)
                )
            """)
            
            # Tool statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_stats (
                    tool_id TEXT PRIMARY KEY,
                    total_calls INTEGER DEFAULT 0,
                    successful_calls INTEGER DEFAULT 0,
                    failed_calls INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Lineage chains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage_chains (
                    object_ref TEXT PRIMARY KEY,
                    chain_data TEXT NOT NULL,  -- JSON
                    depth INTEGER NOT NULL,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_operations_tool ON operations(tool_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_operations_status ON operations(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_operations_started ON operations(started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_inputs_ref ON operation_inputs(input_ref)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outputs_ref ON operation_outputs(output_ref)")
            
            conn.commit()
    
    def save_operation(self, operation_id: str, operation_data: Dict[str, Any]) -> bool:
        """Save operation to database
        
        Args:
            operation_id: Unique operation identifier
            operation_data: Operation data including type, agent, status, etc.
            
        Returns:
            Success status
        """
        try:
            with self.connection as conn:
                # Extract core fields
                tool_id = operation_data.get('agent', {}).get('tool_id')
                
                # Insert operation
                conn.execute("""
                    INSERT OR REPLACE INTO operations 
                    (operation_id, operation_type, tool_id, status, 
                     started_at, completed_at, error_message,
                     agent_data, parameters, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    operation_id,
                    operation_data.get('operation_type', 'unknown'),
                    tool_id,
                    operation_data.get('status', 'unknown'),
                    operation_data.get('started_at', datetime.now()),
                    operation_data.get('completed_at'),
                    operation_data.get('error_message'),
                    json.dumps(operation_data.get('agent', {})),
                    json.dumps(operation_data.get('parameters', {})),
                    json.dumps(operation_data.get('metadata', {}))
                ))
                
                # Save inputs
                for input_ref, input_data in operation_data.get('used', {}).items():
                    conn.execute("""
                        INSERT OR REPLACE INTO operation_inputs
                        (operation_id, input_ref, input_type, input_metadata)
                        VALUES (?, ?, ?, ?)
                    """, (
                        operation_id,
                        input_ref,
                        input_data.get('type') if isinstance(input_data, dict) else None,
                        json.dumps(input_data) if isinstance(input_data, dict) else None
                    ))
                
                # Save outputs
                for output_ref in operation_data.get('generated', []):
                    conn.execute("""
                        INSERT OR REPLACE INTO operation_outputs
                        (operation_id, output_ref, output_type, output_metadata)
                        VALUES (?, ?, ?, ?)
                    """, (
                        operation_id,
                        output_ref,
                        None,  # Type can be added later
                        None   # Metadata can be added later
                    ))
                
                # Update tool statistics
                if tool_id:
                    self._update_tool_stats(conn, tool_id, operation_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to save operation {operation_id}: {e}")
            return False
    
    def _update_tool_stats(self, conn: sqlite3.Connection, tool_id: str, operation_data: Dict[str, Any]):
        """Update tool statistics"""
        # Calculate duration
        duration = 0
        if operation_data.get('completed_at') and operation_data.get('started_at'):
            duration = (operation_data['completed_at'] - operation_data['started_at']).total_seconds()
        
        # Increment counters based on status
        if operation_data.get('status') == 'completed':
            conn.execute("""
                INSERT INTO tool_stats (tool_id, total_calls, successful_calls, total_duration, last_used)
                VALUES (?, 1, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(tool_id) DO UPDATE SET
                    total_calls = total_calls + 1,
                    successful_calls = successful_calls + 1,
                    total_duration = total_duration + ?,
                    last_used = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (tool_id, duration, duration))
        else:
            conn.execute("""
                INSERT INTO tool_stats (tool_id, total_calls, failed_calls, last_used)
                VALUES (?, 1, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(tool_id) DO UPDATE SET
                    total_calls = total_calls + 1,
                    failed_calls = failed_calls + 1,
                    last_used = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (tool_id,))
    
    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve operation by ID"""
        try:
            with self.connection as conn:
                # Get operation
                row = conn.execute(
                    "SELECT * FROM operations WHERE operation_id = ?",
                    (operation_id,)
                ).fetchone()
                
                if not row:
                    return None
                
                # Convert to dict
                operation = dict(row)
                operation['agent'] = json.loads(operation['agent_data']) if operation['agent_data'] else {}
                operation['parameters'] = json.loads(operation['parameters']) if operation['parameters'] else {}
                operation['metadata'] = json.loads(operation['metadata']) if operation['metadata'] else {}
                
                # Get inputs
                inputs = conn.execute(
                    "SELECT * FROM operation_inputs WHERE operation_id = ?",
                    (operation_id,)
                ).fetchall()
                operation['used'] = {
                    row['input_ref']: json.loads(row['input_metadata']) if row['input_metadata'] else {}
                    for row in inputs
                }
                
                # Get outputs
                outputs = conn.execute(
                    "SELECT output_ref FROM operation_outputs WHERE operation_id = ?",
                    (operation_id,)
                ).fetchall()
                operation['generated'] = [row['output_ref'] for row in outputs]
                
                return operation
                
        except Exception as e:
            logger.error(f"Failed to get operation {operation_id}: {e}")
            return None
    
    def get_object_lineage(self, object_ref: str) -> List[Dict[str, Any]]:
        """Get all operations that created or used an object"""
        try:
            with self.connection as conn:
                # Find operations that generated this object
                generated_ops = conn.execute("""
                    SELECT o.* FROM operations o
                    JOIN operation_outputs oo ON o.operation_id = oo.operation_id
                    WHERE oo.output_ref = ?
                    ORDER BY o.started_at
                """, (object_ref,)).fetchall()
                
                # Find operations that used this object
                used_ops = conn.execute("""
                    SELECT o.* FROM operations o
                    JOIN operation_inputs oi ON o.operation_id = oi.operation_id
                    WHERE oi.input_ref = ?
                    ORDER BY o.started_at
                """, (object_ref,)).fetchall()
                
                # Combine and convert to dicts
                all_ops = []
                for row in generated_ops:
                    op = dict(row)
                    op['relationship'] = 'generated'
                    all_ops.append(op)
                
                for row in used_ops:
                    op = dict(row)
                    op['relationship'] = 'used'
                    all_ops.append(op)
                
                return all_ops
                
        except Exception as e:
            logger.error(f"Failed to get lineage for {object_ref}: {e}")
            return []
    
    def get_tool_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all tools"""
        try:
            with self.connection as conn:
                rows = conn.execute("SELECT * FROM tool_stats ORDER BY tool_id").fetchall()
                
                stats = {}
                for row in rows:
                    stats[row['tool_id']] = {
                        'calls': row['total_calls'],
                        'successes': row['successful_calls'],
                        'failures': row['failed_calls'],
                        'total_duration': row['total_duration'],
                        'avg_duration': row['total_duration'] / row['total_calls'] if row['total_calls'] > 0 else 0,
                        'success_rate': row['successful_calls'] / row['total_calls'] if row['total_calls'] > 0 else 0,
                        'last_used': row['last_used']
                    }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get tool statistics: {e}")
            return {}
    
    def query_operations(self, 
                        tool_id: Optional[str] = None,
                        status: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Query operations with filters"""
        try:
            with self.connection as conn:
                query = "SELECT * FROM operations WHERE 1=1"
                params = []
                
                if tool_id:
                    query += " AND tool_id = ?"
                    params.append(tool_id)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if start_time:
                    query += " AND started_at >= ?"
                    params.append(start_time)
                
                if end_time:
                    query += " AND started_at <= ?"
                    params.append(end_time)
                
                query += " ORDER BY started_at DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to query operations: {e}")
            return []
    
    def save_lineage_chain(self, object_ref: str, chain_data: Dict[str, Any]) -> bool:
        """Save lineage chain for an object
        
        Args:
            object_ref: Object reference
            chain_data: Lineage chain data including operations, depth, confidence
            
        Returns:
            Success status
        """
        try:
            with self.connection as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO lineage_chains
                    (object_ref, chain_data, depth, confidence)
                    VALUES (?, ?, ?, ?)
                """, (
                    object_ref,
                    json.dumps(chain_data),
                    chain_data.get('depth', 0),
                    chain_data.get('confidence', 1.0)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save lineage chain for {object_ref}: {e}")
            return False
    
    def get_lineage_chain(self, object_ref: str) -> Optional[Dict[str, Any]]:
        """Retrieve lineage chain for an object"""
        try:
            with self.connection as conn:
                row = conn.execute(
                    "SELECT * FROM lineage_chains WHERE object_ref = ?",
                    (object_ref,)
                ).fetchone()
                
                if not row:
                    return None
                
                chain = dict(row)
                chain['chain_data'] = json.loads(chain['chain_data'])
                return chain
                
        except Exception as e:
            logger.error(f"Failed to get lineage chain for {object_ref}: {e}")
            return None
    
    def export_to_json(self, output_path: str) -> bool:
        """Export all provenance data to JSON file
        
        Args:
            output_path: Path to output JSON file
            
        Returns:
            Success status
        """
        try:
            data = {
                'operations': [],
                'lineage_chains': [],
                'tool_stats': [],
                'export_timestamp': datetime.now().isoformat()
            }
            
            with self.connection as conn:
                # Export operations
                ops = conn.execute("SELECT * FROM operations ORDER BY started_at").fetchall()
                for op in ops:
                    op_dict = dict(op)
                    op_dict['agent_data'] = json.loads(op_dict['agent_data']) if op_dict['agent_data'] else {}
                    op_dict['parameters'] = json.loads(op_dict['parameters']) if op_dict['parameters'] else {}
                    op_dict['metadata'] = json.loads(op_dict['metadata']) if op_dict['metadata'] else {}
                    
                    # Get inputs and outputs
                    inputs = conn.execute(
                        "SELECT * FROM operation_inputs WHERE operation_id = ?",
                        (op['operation_id'],)
                    ).fetchall()
                    outputs = conn.execute(
                        "SELECT * FROM operation_outputs WHERE operation_id = ?",
                        (op['operation_id'],)
                    ).fetchall()
                    
                    op_dict['inputs'] = [dict(i) for i in inputs]
                    op_dict['outputs'] = [dict(o) for o in outputs]
                    
                    data['operations'].append(op_dict)
                
                # Export lineage chains
                chains = conn.execute("SELECT * FROM lineage_chains").fetchall()
                for chain in chains:
                    chain_dict = dict(chain)
                    chain_dict['chain_data'] = json.loads(chain_dict['chain_data'])
                    data['lineage_chains'].append(chain_dict)
                
                # Export tool stats
                stats = conn.execute("SELECT * FROM tool_stats").fetchall()
                data['tool_stats'] = [dict(s) for s in stats]
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported provenance data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export provenance data: {e}")
            return False
    
    def import_from_json(self, input_path: str) -> bool:
        """Import provenance data from JSON file
        
        Args:
            input_path: Path to input JSON file
            
        Returns:
            Success status
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            with self.connection as conn:
                # Import operations
                for op in data.get('operations', []):
                    # Save operation
                    self.save_operation(op['operation_id'], op)
                
                # Import lineage chains
                for chain in data.get('lineage_chains', []):
                    self.save_lineage_chain(chain['object_ref'], chain['chain_data'])
                
                conn.commit()
            
            logger.info(f"Imported provenance data from {input_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import provenance data: {e}")
            return False
    
    def get_workflow_operations(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all operations for a specific workflow
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of operations in the workflow
        """
        try:
            with self.connection as conn:
                # Find operations with workflow_id in metadata
                query = """
                    SELECT * FROM operations 
                    WHERE json_extract(metadata, '$.workflow_id') = ?
                    ORDER BY started_at
                """
                rows = conn.execute(query, (workflow_id,)).fetchall()
                
                operations = []
                for row in rows:
                    op = dict(row)
                    op['agent'] = json.loads(op['agent_data']) if op['agent_data'] else {}
                    op['parameters'] = json.loads(op['parameters']) if op['parameters'] else {}
                    op['metadata'] = json.loads(op['metadata']) if op['metadata'] else {}
                    operations.append(op)
                
                return operations
                
        except Exception as e:
            logger.error(f"Failed to get workflow operations: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
