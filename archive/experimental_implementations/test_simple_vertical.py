#!/usr/bin/env python
"""Simple vertical slice test - step by step."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.database import DatabaseManager
from src.tools.phase1 import PDFDocumentLoader
from src.tools.phase2 import TextChunker


def test_simple():
    """Test just PDF loading and chunking."""
    print("Testing simple vertical slice...")
    
    # Setup
    config = Config()
    config.sqlite_db_path = Path("./data/test_simple.db")
    config.ensure_directories()
    
    # Initialize database
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    
    # Create simple test content
    test_text = """
    Apple Inc. is a technology company.
    Microsoft is another tech giant.
    Google is part of Alphabet.
    """
    
    # Test chunking directly without PDF
    print("\n1. Testing text chunker...")
    chunker = TextChunker(db_manager)
    
    # First create a dummy document
    from src.models import Document
    doc = Document(
        title="Test Document",
        source_path="test.txt",
        content_hash="test123"
    )
    db_manager.sqlite.save_document(doc)
    doc_ref = f"sqlite://document/{doc.id}"
    print(f"Created document: {doc_ref}")
    
    # Chunk it
    result = chunker.chunk_document(
        doc_ref,
        chunk_size=50,
        overlap=10,
        text_content=test_text
    )
    
    print(f"Created {result['chunk_count']} chunks")
    for i, chunk_ref in enumerate(result['chunk_refs'][:3]):
        print(f"  Chunk {i}: {chunk_ref}")
    
    # Test entity extraction
    print("\n2. Testing entity extraction...")
    from src.tools.phase2 import EntityExtractorSpacy
    
    extractor = EntityExtractorSpacy(db_manager)
    
    # Extract from first chunk
    if result['chunk_refs']:
        chunk_ref = result['chunk_refs'][0]
        print(f"Extracting from: {chunk_ref}")
        
        entity_result = extractor.extract_entities(chunk_ref)
        print(f"Found {entity_result['entity_count']} entities")
        for entity_ref in entity_result['entity_refs']:
            print(f"  Entity: {entity_ref}")
    
    print("\nSimple test completed!")
    
    # Cleanup
    db_manager.close()
    if config.sqlite_db_path.exists():
        config.sqlite_db_path.unlink()


if __name__ == "__main__":
    test_simple()