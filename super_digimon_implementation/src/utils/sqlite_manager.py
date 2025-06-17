"""SQLite database manager."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..models import Document, Chunk, SurfaceForm, Mention, ProvenanceRecord, WorkflowCheckpoint


logger = logging.getLogger(__name__)


class SQLiteManager:
    """Manager for SQLite metadata database operations."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    @property
    def conn(self):
        """Lazy-load database connection."""
        if not self._conn:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn
    
    def initialize_schema(self) -> None:
        """Create database tables."""
        cursor = self.conn.cursor()
        
        # Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source_path TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            metadata TEXT,
            chunk_count INTEGER DEFAULT 0,
            entity_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            warnings TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        
        # Chunks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            text TEXT NOT NULL,
            position INTEGER NOT NULL,
            start_char INTEGER NOT NULL,
            end_char INTEGER NOT NULL,
            embedding_ref TEXT,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            warnings TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
        """)
        
        # Surface forms table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS surface_forms (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            context TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        )
        """)
        
        # Mentions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentions (
            id TEXT PRIMARY KEY,
            surface_form_id TEXT NOT NULL,
            entity_id TEXT,
            mention_type TEXT NOT NULL,
            attributes TEXT,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            warnings TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (surface_form_id) REFERENCES surface_forms(id)
        )
        """)
        
        # Provenance table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provenance (
            id TEXT PRIMARY KEY,
            operation_type TEXT NOT NULL,
            tool_id TEXT NOT NULL,
            input_refs TEXT,
            output_refs TEXT,
            parameters TEXT,
            metrics TEXT,
            parent_id TEXT,
            status TEXT NOT NULL,
            error_message TEXT,
            duration_ms INTEGER,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            warnings TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        
        # Workflow checkpoints table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_checkpoints (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            workflow_type TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            total_steps INTEGER NOT NULL,
            state_data TEXT,
            completed_operations TEXT,
            pending_operations TEXT,
            failed_operations TEXT,
            metadata TEXT,
            confidence REAL DEFAULT 1.0,
            quality_tier TEXT DEFAULT 'high',
            warnings TEXT,
            evidence TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_surface_forms_chunk ON surface_forms(chunk_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_surface_form ON mentions(surface_form_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_entity ON mentions(entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_provenance_outputs ON provenance(output_refs)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_workflow ON workflow_checkpoints(workflow_id)")
        
        self.conn.commit()
        logger.info("SQLite schema initialized")
    
    def health_check(self) -> bool:
        """Check if SQLite is accessible."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            return False
    
    # Document operations
    def save_document(self, document: Document) -> None:
        """Save a document."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO documents 
        (id, title, source_path, content_hash, metadata, chunk_count, entity_count,
         confidence, quality_tier, warnings, evidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document.id,
            document.title,
            document.source_path,
            document.content_hash,
            json.dumps(document.metadata),
            document.chunk_count,
            document.entity_count,
            document.confidence,
            document.quality_tier,
            json.dumps(document.warnings),
            json.dumps(document.evidence),
            document.created_at.isoformat(),
            document.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        
        if row:
            return self._document_from_row(row)
        return None
    
    def update_document(self, document: Document) -> None:
        """Update a document."""
        document.updated_at = datetime.utcnow()
        self.save_document(document)
    
    # Chunk operations
    def save_chunk(self, chunk: Chunk) -> None:
        """Save a chunk."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO chunks
        (id, document_id, text, position, start_char, end_char, embedding_ref,
         confidence, quality_tier, warnings, evidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk.id,
            chunk.document_id,
            chunk.text,
            chunk.position,
            chunk.start_char,
            chunk.end_char,
            chunk.embedding_ref,
            chunk.confidence,
            chunk.quality_tier,
            json.dumps(chunk.warnings),
            json.dumps(chunk.evidence),
            chunk.created_at.isoformat(),
            chunk.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        """Get a chunk by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,))
        row = cursor.fetchone()
        
        if row:
            return self._chunk_from_row(row)
        return None
    
    def get_document_chunks(self, document_id: str) -> List[Chunk]:
        """Get all chunks for a document."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY position",
            (document_id,)
        )
        
        chunks = []
        for row in cursor.fetchall():
            chunks.append(self._chunk_from_row(row))
        return chunks
    
    def update_chunk(self, chunk: Chunk) -> None:
        """Update a chunk."""
        chunk.updated_at = datetime.utcnow()
        self.save_chunk(chunk)
    
    # Surface form operations
    def save_surface_form(self, surface_form: SurfaceForm) -> None:
        """Save a surface form."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO surface_forms
        (id, text, context, chunk_id, start_offset, end_offset,
         confidence, quality_tier, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            surface_form.id,
            surface_form.text,
            surface_form.context,
            surface_form.chunk_id,
            surface_form.start_offset,
            surface_form.end_offset,
            surface_form.confidence,
            surface_form.quality_tier,
            surface_form.created_at.isoformat(),
            surface_form.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_surface_form(self, surface_form_id: str) -> Optional[SurfaceForm]:
        """Get a surface form by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM surface_forms WHERE id = ?", (surface_form_id,))
        row = cursor.fetchone()
        
        if row:
            return self._surface_form_from_row(row)
        return None
    
    # Mention operations
    def save_mention(self, mention: Mention) -> None:
        """Save a mention."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO mentions
        (id, surface_form_id, entity_id, mention_type, attributes,
         confidence, quality_tier, warnings, evidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mention.id,
            mention.surface_form_id,
            mention.entity_id,
            mention.mention_type,
            json.dumps(mention.attributes),
            mention.confidence,
            mention.quality_tier,
            json.dumps(mention.warnings),
            json.dumps(mention.evidence),
            mention.created_at.isoformat(),
            mention.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_mention(self, mention_id: str) -> Optional[Mention]:
        """Get a mention by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mentions WHERE id = ?", (mention_id,))
        row = cursor.fetchone()
        
        if row:
            return self._mention_from_row(row)
        return None
    
    def get_mentions_by_surface_form(self, surface_form_id: str) -> List[Mention]:
        """Get all mentions for a surface form."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mentions WHERE surface_form_id = ?",
            (surface_form_id,)
        )
        
        mentions = []
        for row in cursor.fetchall():
            mentions.append(self._mention_from_row(row))
        return mentions
    
    def update_mention(self, mention: Mention) -> None:
        """Update a mention."""
        mention.updated_at = datetime.utcnow()
        self.save_mention(mention)
    
    # Provenance operations
    def save_provenance(self, record: ProvenanceRecord) -> None:
        """Save a provenance record."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO provenance
        (id, operation_type, tool_id, input_refs, output_refs, parameters, metrics,
         parent_id, status, error_message, duration_ms, confidence, quality_tier,
         warnings, evidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.operation_type,
            record.tool_id,
            json.dumps(record.input_refs),
            json.dumps(record.output_refs),
            json.dumps(record.parameters),
            json.dumps(record.metrics),
            record.parent_id,
            record.status,
            record.error_message,
            record.duration_ms,
            record.confidence,
            record.quality_tier,
            json.dumps(record.warnings),
            json.dumps(record.evidence),
            record.created_at.isoformat(),
            record.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_provenance(self, record_id: str) -> Optional[ProvenanceRecord]:
        """Get a provenance record by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM provenance WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        
        if row:
            return self._provenance_from_row(row)
        return None
    
    def get_provenance_by_output(self, output_ref: str) -> List[ProvenanceRecord]:
        """Get provenance records that produced an output."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM provenance WHERE output_refs LIKE ?",
            (f'%"{output_ref}"%',)
        )
        
        records = []
        for row in cursor.fetchall():
            records.append(self._provenance_from_row(row))
        return records
    
    def get_provenance_by_input(self, input_ref: str) -> List[ProvenanceRecord]:
        """Get provenance records that used an input."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM provenance WHERE input_refs LIKE ?",
            (f'%"{input_ref}"%',)
        )
        
        records = []
        for row in cursor.fetchall():
            records.append(self._provenance_from_row(row))
        return records
    
    def update_provenance(self, record: ProvenanceRecord) -> None:
        """Update a provenance record."""
        record.updated_at = datetime.utcnow()
        self.save_provenance(record)
    
    def get_provenance_records(
        self,
        tool_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ProvenanceRecord]:
        """Get provenance records with optional filters."""
        query = "SELECT * FROM provenance WHERE 1=1"
        params = []
        
        if tool_id:
            query += " AND tool_id = ?"
            params.append(tool_id)
        
        if start_time:
            query += " AND created_at >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND created_at <= ?"
            params.append(end_time.isoformat())
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        records = []
        for row in cursor.fetchall():
            records.append(self._provenance_from_row(row))
        return records
    
    # Workflow checkpoint operations
    def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> None:
        """Save a workflow checkpoint."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO workflow_checkpoints
        (id, workflow_id, workflow_type, step_number, total_steps, state_data,
         completed_operations, pending_operations, failed_operations, metadata,
         confidence, quality_tier, warnings, evidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint.id,
            checkpoint.workflow_id,
            checkpoint.workflow_type,
            checkpoint.step_number,
            checkpoint.total_steps,
            json.dumps(checkpoint.state_data),
            json.dumps(checkpoint.completed_operations),
            json.dumps(checkpoint.pending_operations),
            json.dumps(checkpoint.failed_operations),
            json.dumps(checkpoint.metadata),
            checkpoint.confidence,
            checkpoint.quality_tier,
            json.dumps(checkpoint.warnings),
            json.dumps(checkpoint.evidence),
            checkpoint.created_at.isoformat(),
            checkpoint.updated_at.isoformat()
        ))
        self.conn.commit()
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Get a checkpoint by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workflow_checkpoints WHERE id = ?", (checkpoint_id,))
        row = cursor.fetchone()
        
        if row:
            return self._checkpoint_from_row(row)
        return None
    
    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """Get the latest checkpoint for a workflow."""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM workflow_checkpoints 
        WHERE workflow_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
        """, (workflow_id,))
        row = cursor.fetchone()
        
        if row:
            return self._checkpoint_from_row(row)
        return None
    
    def list_checkpoints(
        self,
        workflow_id: Optional[str] = None,
        workflow_type: Optional[str] = None
    ) -> List[WorkflowCheckpoint]:
        """List checkpoints with optional filters."""
        query = "SELECT * FROM workflow_checkpoints WHERE 1=1"
        params = []
        
        if workflow_id:
            query += " AND workflow_id = ?"
            params.append(workflow_id)
        
        if workflow_type:
            query += " AND workflow_type = ?"
            params.append(workflow_type)
        
        query += " ORDER BY created_at DESC"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        checkpoints = []
        for row in cursor.fetchall():
            checkpoints.append(self._checkpoint_from_row(row))
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Delete a checkpoint."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM workflow_checkpoints WHERE id = ?", (checkpoint_id,))
        self.conn.commit()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    # Helper methods to convert rows to objects
    def _document_from_row(self, row) -> Document:
        """Convert a database row to Document object."""
        return Document(
            id=row["id"],
            title=row["title"],
            source_path=row["source_path"],
            content_hash=row["content_hash"],
            metadata=json.loads(row["metadata"] or "{}"),
            chunk_count=row["chunk_count"],
            entity_count=row["entity_count"],
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            warnings=json.loads(row["warnings"] or "[]"),
            evidence=json.loads(row["evidence"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _chunk_from_row(self, row) -> Chunk:
        """Convert a database row to Chunk object."""
        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            text=row["text"],
            position=row["position"],
            start_char=row["start_char"],
            end_char=row["end_char"],
            embedding_ref=row["embedding_ref"],
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            warnings=json.loads(row["warnings"] or "[]"),
            evidence=json.loads(row["evidence"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _surface_form_from_row(self, row) -> SurfaceForm:
        """Convert a database row to SurfaceForm object."""
        return SurfaceForm(
            id=row["id"],
            text=row["text"],
            context=row["context"],
            chunk_id=row["chunk_id"],
            start_offset=row["start_offset"],
            end_offset=row["end_offset"],
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _mention_from_row(self, row) -> Mention:
        """Convert a database row to Mention object."""
        return Mention(
            id=row["id"],
            surface_form_id=row["surface_form_id"],
            entity_id=row["entity_id"],
            mention_type=row["mention_type"],
            attributes=json.loads(row["attributes"] or "{}"),
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            warnings=json.loads(row["warnings"] or "[]"),
            evidence=json.loads(row["evidence"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _provenance_from_row(self, row) -> ProvenanceRecord:
        """Convert a database row to ProvenanceRecord object."""
        return ProvenanceRecord(
            id=row["id"],
            operation_type=row["operation_type"],
            tool_id=row["tool_id"],
            input_refs=json.loads(row["input_refs"] or "[]"),
            output_refs=json.loads(row["output_refs"] or "[]"),
            parameters=json.loads(row["parameters"] or "{}"),
            metrics=json.loads(row["metrics"] or "{}"),
            parent_id=row["parent_id"],
            status=row["status"],
            error_message=row["error_message"],
            duration_ms=row["duration_ms"] or 0,
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            warnings=json.loads(row["warnings"] or "[]"),
            evidence=json.loads(row["evidence"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _checkpoint_from_row(self, row) -> WorkflowCheckpoint:
        """Convert a database row to WorkflowCheckpoint object."""
        return WorkflowCheckpoint(
            id=row["id"],
            workflow_id=row["workflow_id"],
            workflow_type=row["workflow_type"],
            step_number=row["step_number"],
            total_steps=row["total_steps"],
            state_data=json.loads(row["state_data"] or "{}"),
            completed_operations=json.loads(row["completed_operations"] or "[]"),
            pending_operations=json.loads(row["pending_operations"] or "[]"),
            failed_operations=json.loads(row["failed_operations"] or "[]"),
            metadata=json.loads(row["metadata"] or "{}"),
            confidence=row["confidence"],
            quality_tier=row["quality_tier"],
            warnings=json.loads(row["warnings"] or "[]"),
            evidence=json.loads(row["evidence"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )