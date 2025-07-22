# SQLite Data Model Specification

**Version**: 1.0
**Status**: Current Implementation  
**Last Updated**: 2025-07-22

## Overview

This document specifies the SQLite database schema used in KGAS for storing documents, chunks, mentions, and operational data.

## Table Definitions

### documents

Stores document metadata and processing status.

```sql
CREATE TABLE documents (
    -- Identity
    doc_id TEXT PRIMARY KEY,        -- Format: "doc_<uuid>"
    file_path TEXT NOT NULL,        -- Original file path
    file_name TEXT NOT NULL,        -- Original file name
    file_size INTEGER,              -- File size in bytes
    file_hash TEXT,                 -- SHA-256 hash of file
    
    -- Processing Status
    status TEXT NOT NULL,           -- 'pending', 'processing', 'completed', 'failed'
    processed_at TIMESTAMP,         -- When processing completed
    processing_time REAL,           -- Processing duration in seconds
    error_message TEXT,             -- Error details if failed
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- Document Properties
    page_count INTEGER,             -- Number of pages (for PDFs)
    word_count INTEGER,             -- Total word count
    confidence REAL,                -- Overall document confidence (0.0-1.0)
    
    CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_documents_hash ON documents(file_hash);
```

### chunks

Stores document chunks for processing.

```sql
CREATE TABLE chunks (
    -- Identity
    chunk_id TEXT PRIMARY KEY,      -- Format: "chunk_<uuid>"
    doc_id TEXT NOT NULL,           -- Foreign key to documents
    
    -- Content
    content TEXT NOT NULL,          -- Chunk text content
    tokens INTEGER,                 -- Number of tokens
    
    -- Position
    position INTEGER NOT NULL,      -- Order within document (0-based)
    start_char INTEGER,             -- Start character position in document
    end_char INTEGER,               -- End character position in document
    page_number INTEGER,            -- Page number (for PDFs)
    
    -- Quality
    confidence REAL,                -- Chunk confidence (0.0-1.0)
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CHECK (position >= 0),
    CHECK (end_char > start_char)
);

-- Indexes
CREATE INDEX idx_chunks_doc ON chunks(doc_id);
CREATE INDEX idx_chunks_position ON chunks(doc_id, position);
```

### mentions

Stores entity mentions found in text.

```sql
CREATE TABLE mentions (
    -- Identity
    mention_id TEXT PRIMARY KEY,    -- Format: "mention_<uuid>"
    entity_id TEXT NOT NULL,        -- Maps to Neo4j entity_id
    chunk_id TEXT NOT NULL,         -- Foreign key to chunks
    
    -- Mention Details
    surface_form TEXT NOT NULL,     -- Actual text of mention
    entity_type TEXT NOT NULL,      -- Entity type (PERSON, ORG, etc.)
    
    -- Position
    start_pos INTEGER NOT NULL,     -- Start position in chunk
    end_pos INTEGER NOT NULL,       -- End position in chunk
    
    -- Quality
    confidence REAL NOT NULL,       -- Mention confidence (0.0-1.0)
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                -- Tool ID that created this
    
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE,
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CHECK (end_pos > start_pos)
);

-- Indexes
CREATE INDEX idx_mentions_entity ON mentions(entity_id);
CREATE INDEX idx_mentions_chunk ON mentions(chunk_id);
CREATE INDEX idx_mentions_type ON mentions(entity_type);
```

### operations

Tracks all processing operations for provenance.

```sql
CREATE TABLE operations (
    -- Identity
    operation_id TEXT PRIMARY KEY,  -- Format: "op_<uuid>"
    
    -- Operation Details
    tool_id TEXT NOT NULL,          -- Tool that performed operation
    operation_type TEXT NOT NULL,   -- Type of operation
    
    -- Timing
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_ms INTEGER,            -- Duration in milliseconds
    
    -- Status
    status TEXT NOT NULL,           -- 'running', 'success', 'failed'
    error_message TEXT,             -- Error details if failed
    
    -- Lineage
    inputs TEXT,                    -- JSON array of input references
    outputs TEXT,                   -- JSON array of output references
    parameters TEXT,                -- JSON object of parameters
    
    -- Metadata
    metadata TEXT,                  -- JSON object of additional data
    
    CHECK (status IN ('running', 'success', 'failed'))
);

-- Indexes
CREATE INDEX idx_operations_tool ON operations(tool_id);
CREATE INDEX idx_operations_status ON operations(status);
CREATE INDEX idx_operations_started ON operations(started_at);
```

### workflows

Stores workflow definitions and executions.

```sql
CREATE TABLE workflows (
    -- Identity
    workflow_id TEXT PRIMARY KEY,   -- Format: "wf_<uuid>"
    workflow_name TEXT,             -- Human-readable name
    
    -- Status
    status TEXT NOT NULL,           -- 'created', 'running', 'completed', 'failed'
    current_step INTEGER DEFAULT 0, -- Current step number
    total_steps INTEGER,            -- Total number of steps
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Data
    input_data TEXT,                -- JSON input data
    output_data TEXT,               -- JSON output data
    state_data TEXT,                -- JSON workflow state
    
    -- Metadata
    created_by TEXT,                -- User or system that created
    tags TEXT,                      -- JSON array of tags
    
    CHECK (status IN ('created', 'running', 'completed', 'failed'))
);

-- Indexes
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created ON workflows(created_at);
```

## Example Data

### Document Record
```sql
INSERT INTO documents (doc_id, file_path, file_name, status, confidence) VALUES
('doc_123e4567-e89b-12d3-a456-426614174000', 
 '/data/papers/research.pdf',
 'research.pdf',
 'completed',
 0.92);
```

### Chunk Record
```sql
INSERT INTO chunks (chunk_id, doc_id, content, position, confidence) VALUES
('chunk_456a7890-123b-45c6-789d-012345678901',
 'doc_123e4567-e89b-12d3-a456-426614174000',
 'This research explores the application of knowledge graphs...',
 0,
 0.95);
```

### Mention Record
```sql
INSERT INTO mentions (mention_id, entity_id, chunk_id, surface_form, entity_type, start_pos, end_pos, confidence) VALUES
('mention_789b0123-456c-789d-012e-345678901234',
 'entity_123e4567-e89b-12d3-a456-426614174000',
 'chunk_456a7890-123b-45c6-789d-012345678901',
 'John Smith',
 'PERSON',
 15,
 25,
 0.88);
```

## Common Queries

### Get Document Status
```sql
SELECT doc_id, file_name, status, processed_at
FROM documents
WHERE status = 'completed'
ORDER BY processed_at DESC;
```

### Get Chunks for Document
```sql
SELECT chunk_id, position, content
FROM chunks
WHERE doc_id = ?
ORDER BY position;
```

### Get Mentions in Chunk
```sql
SELECT m.*, c.content
FROM mentions m
JOIN chunks c ON m.chunk_id = c.chunk_id
WHERE c.chunk_id = ?
ORDER BY m.start_pos;
```

### Track Operation Lineage
```sql
SELECT *
FROM operations
WHERE json_extract(outputs, '$[0]') = ?
ORDER BY started_at DESC;
```

## Data Integrity Rules

1. **Referential Integrity**: All foreign keys must reference existing records
2. **Position Consistency**: Chunk positions must be sequential
3. **Confidence Bounds**: All confidence scores between 0.0 and 1.0
4. **Status Values**: Only allowed status values per table
5. **Timestamp Order**: completed_at must be after started_at

## Performance Considerations

### Current Scale
- Documents: ~100s
- Chunks per document: ~10-100
- Mentions per chunk: ~5-20
- Operations: ~1000s per workflow

### Optimization Strategies
1. Use indexes for common query patterns
2. Batch inserts for chunks and mentions
3. Periodic cleanup of old operations
4. JSON indexing for metadata queries

## Consistency with Neo4j

### Entity ID Synchronization
```sql
-- Mentions table entity_id maps to Neo4j Entity.entity_id
-- Ensures traceability between systems
```

### Transaction Boundaries
- SQLite operations are atomic within SQLite
- No distributed transactions with Neo4j
- Eventual consistency model

### Data Flow
1. Document → SQLite documents table
2. Chunks → SQLite chunks table  
3. Mentions → SQLite mentions table + Neo4j Entity nodes
4. Relationships → Neo4j only (no SQLite storage)

## Error Scenarios

### Common Issues
1. **Foreign Key Violation**: Referencing non-existent document/chunk
2. **Unique Constraint**: Duplicate primary keys
3. **Check Constraint**: Invalid status or confidence values
4. **Storage Full**: SQLite database size limits

### Error Handling
```sql
-- Use transactions for multi-table operations
BEGIN TRANSACTION;
INSERT INTO documents ...;
INSERT INTO chunks ...;
COMMIT;

-- Rollback on error
ROLLBACK;
```

## Migration and Evolution

### Schema Version
Current: 1.0

### Future Additions (Planned)
```sql
-- Version 2.0 Additions

-- Add embedding storage
CREATE TABLE embeddings (
    embedding_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    vector BLOB NOT NULL,
    dimension INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id)
);

-- Add quality metrics
ALTER TABLE documents ADD COLUMN quality_score REAL;
ALTER TABLE chunks ADD COLUMN embedding_id TEXT;
```

### Backward Compatibility
- New columns will be nullable
- Existing queries will continue to work
- Migration scripts will handle schema updates

## Backup and Recovery

### Backup Strategy
```bash
# Regular backups
sqlite3 kgas.db ".backup kgas_backup.db"

# Export to SQL
sqlite3 kgas.db .dump > kgas_dump.sql
```

### Recovery Procedures
1. Stop all operations
2. Restore from backup
3. Verify integrity
4. Resume operations

## Database Configuration

### Recommended Settings
```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Set journal mode for better concurrency
PRAGMA journal_mode = WAL;

-- Optimize for performance
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -2000;  -- 2MB cache
```