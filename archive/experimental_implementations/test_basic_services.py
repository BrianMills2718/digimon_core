#!/usr/bin/env python
"""Test basic services without NLP models."""

import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.database import DatabaseManager
from src.models import Document, Chunk


def test_basic():
    """Test basic database operations."""
    print("Testing basic services...")
    
    # Setup
    config = Config()
    config.sqlite_db_path = Path("./data/test_basic.db")
    config.ensure_directories()
    
    # Initialize database
    print("1. Initializing database...")
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    print("✓ Database initialized")
    
    # Test document creation
    print("\n2. Creating document...")
    doc = Document(
        title="Test Document",
        source_path="test.txt",
        content_hash="test123"
    )
    db_manager.sqlite.save_document(doc)
    print(f"✓ Created document: {doc.id}")
    
    # Test chunk creation
    print("\n3. Creating chunk...")
    chunk = Chunk(
        document_id=doc.id,
        text="This is a test chunk.",
        position=0,
        start_char=0,
        end_char=20
    )
    db_manager.sqlite.save_chunk(chunk)
    print(f"✓ Created chunk: {chunk.id}")
    
    # Test provenance
    print("\n4. Testing provenance...")
    prov_service = db_manager.get_provenance_service()
    record = prov_service.track_operation(
        operation_type="test",
        tool_id="T00",
        input_refs=[],
        output_refs=[f"sqlite://document/{doc.id}"],
        parameters={"test": True},
        confidence=1.0
    )
    print(f"✓ Created provenance: {record.id}")
    
    print("\n✅ Basic services test completed!")
    
    # Cleanup
    db_manager.close()
    if config.sqlite_db_path.exists():
        config.sqlite_db_path.unlink()


if __name__ == "__main__":
    test_basic()