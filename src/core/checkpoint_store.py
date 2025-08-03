import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .workflow_models import WorkflowCheckpoint
from .exceptions import CheckpointRestoreError
import logging

logger = logging.getLogger(__name__)


class PersistentCheckpointStore:
    """File-based persistent storage for workflow checkpoints"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            from .standard_config import get_file_path
            storage_path = f"{get_file_path('data_dir')}/checkpoints"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
    
    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> None:
        """Save checkpoint to persistent storage"""
        async with self._lock:
            checkpoint_file = self.storage_path / f"{checkpoint.workflow_id}_checkpoints.json"
            
            # Load existing checkpoints
            checkpoints = []
            if checkpoint_file.exists():
                async with aiofiles.open(checkpoint_file, 'r') as f:
                    content = await f.read()
                    checkpoints = json.loads(content)
            
            # Append new checkpoint
            checkpoint_data = {
                'checkpoint_id': checkpoint.checkpoint_id,
                'workflow_id': checkpoint.workflow_id,
                'timestamp': checkpoint.timestamp.isoformat(),
                'processed_documents': checkpoint.processed_documents,
                'state_data': checkpoint.state_data,
                'service_states': checkpoint.service_states,
                'metadata': checkpoint.metadata
            }
            checkpoints.append(checkpoint_data)
            
            # Save back to file
            async with aiofiles.open(checkpoint_file, 'w') as f:
                await f.write(json.dumps(checkpoints, indent=2))
            
            logger.info(f"Saved checkpoint {checkpoint.checkpoint_id} for workflow {checkpoint.workflow_id}")
    
    async def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Retrieve latest checkpoint for workflow"""
        async with self._lock:
            checkpoint_file = self.storage_path / f"{workflow_id}_checkpoints.json"
            
            if not checkpoint_file.exists():
                return None
            
            async with aiofiles.open(checkpoint_file, 'r') as f:
                content = await f.read()
                checkpoints = json.loads(content)
            
            if not checkpoints:
                return None
            
            # Get latest checkpoint
            latest = checkpoints[-1]
            return WorkflowCheckpoint(
                checkpoint_id=latest['checkpoint_id'],
                workflow_id=latest['workflow_id'],
                timestamp=datetime.fromisoformat(latest['timestamp']),
                processed_documents=latest['processed_documents'],
                state_data=latest['state_data'],
                service_states=latest['service_states'],
                metadata=latest['metadata']
            )
    
    async def get_all_checkpoints(self, workflow_id: str) -> List[WorkflowCheckpoint]:
        """Get all checkpoints for a workflow"""
        async with self._lock:
            checkpoint_file = self.storage_path / f"{workflow_id}_checkpoints.json"
            
            if not checkpoint_file.exists():
                return []
            
            async with aiofiles.open(checkpoint_file, 'r') as f:
                content = await f.read()
                checkpoints_data = json.loads(content)
            
            checkpoints = []
            for data in checkpoints_data:
                checkpoints.append(WorkflowCheckpoint(
                    checkpoint_id=data['checkpoint_id'],
                    workflow_id=data['workflow_id'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    processed_documents=data['processed_documents'],
                    state_data=data['state_data'],
                    service_states=data['service_states'],
                    metadata=data['metadata']
                ))
            
            return checkpoints
    
    async def delete_workflow_checkpoints(self, workflow_id: str) -> None:
        """Delete all checkpoints for a workflow"""
        async with self._lock:
            checkpoint_file = self.storage_path / f"{workflow_id}_checkpoints.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                logger.info(f"Deleted checkpoints for workflow {workflow_id}")


class PostgresCheckpointStore:
    """PostgreSQL-based persistent storage for workflow checkpoints"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection and schema"""
        import asyncpg
        self.pool = await asyncpg.create_pool(self.connection_string)
        
        # Create schema if not exists
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    processed_documents INTEGER NOT NULL,
                    state_data JSONB NOT NULL,
                    service_states JSONB NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_workflow_id ON workflow_checkpoints(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON workflow_checkpoints(workflow_id, timestamp DESC);
            ''')
        
        logger.info("PostgreSQL checkpoint store initialized")
    
    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> None:
        """Save checkpoint to database"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO workflow_checkpoints 
                (checkpoint_id, workflow_id, timestamp, processed_documents, 
                 state_data, service_states, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (checkpoint_id) DO UPDATE SET
                    timestamp = EXCLUDED.timestamp,
                    processed_documents = EXCLUDED.processed_documents,
                    state_data = EXCLUDED.state_data,
                    service_states = EXCLUDED.service_states,
                    metadata = EXCLUDED.metadata
            ''', 
            checkpoint.checkpoint_id,
            checkpoint.workflow_id,
            checkpoint.timestamp,
            checkpoint.processed_documents,
            json.dumps(checkpoint.state_data),
            json.dumps(checkpoint.service_states),
            json.dumps(checkpoint.metadata)
            )
        
        logger.info(f"Saved checkpoint {checkpoint.checkpoint_id} for workflow {checkpoint.workflow_id}")
    
    async def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Retrieve latest checkpoint for workflow"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM workflow_checkpoints
                WHERE workflow_id = $1
                ORDER BY timestamp DESC
                LIMIT 1
            ''', workflow_id)
            
            if not row:
                return None
            
            return WorkflowCheckpoint(
                checkpoint_id=row['checkpoint_id'],
                workflow_id=row['workflow_id'],
                timestamp=row['timestamp'],
                processed_documents=row['processed_documents'],
                state_data=json.loads(row['state_data']),
                service_states=json.loads(row['service_states']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
    
    async def get_all_checkpoints(self, workflow_id: str) -> List[WorkflowCheckpoint]:
        """Get all checkpoints for a workflow"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM workflow_checkpoints
                WHERE workflow_id = $1
                ORDER BY timestamp ASC
            ''', workflow_id)
            
            checkpoints = []
            for row in rows:
                checkpoints.append(WorkflowCheckpoint(
                    checkpoint_id=row['checkpoint_id'],
                    workflow_id=row['workflow_id'],
                    timestamp=row['timestamp'],
                    processed_documents=row['processed_documents'],
                    state_data=json.loads(row['state_data']),
                    service_states=json.loads(row['service_states']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                ))
            
            return checkpoints
    
    async def delete_workflow_checkpoints(self, workflow_id: str) -> None:
        """Delete all checkpoints for a workflow"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM workflow_checkpoints
                WHERE workflow_id = $1
            ''', workflow_id)
        
        logger.info(f"Deleted checkpoints for workflow {workflow_id}")
    
    async def cleanup(self) -> None:
        """Clean up database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL checkpoint store closed")