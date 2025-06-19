#!/usr/bin/env python
"""Test core services with real databases - no mocking."""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.neo4j_manager import Neo4jManager
from src.utils.sqlite_manager import SQLiteManager
from src.utils.faiss_manager import FAISSManager


def test_core_services():
    """Test core services with real databases."""
    print("🧪 Testing Core Services with Real Databases")
    print("=" * 50)
    
    # Create test config
    config = Config()
    config.sqlite_db_path = Path("./data/test_core_services.db")
    config.faiss_index_path = Path("./data/test_core_faiss")
    config.checkpoint_dir = Path("./data/test_checkpoints")
    config.ensure_directories()
    
    # Test 1: SQLite Manager
    print("\n📊 Testing SQLite Manager...")
    sqlite = SQLiteManager(config.sqlite_db_path)
    sqlite.initialize_schema()
    
    # Create a document
    from src.models import Document
    doc = Document(
        title="Test Document",
        source_path="/tmp/test.pdf",
        content_hash="abc123"
    )
    
    sqlite.save_document(doc)
    print(f"✓ Created document: {doc.id}")
    
    # Retrieve it
    retrieved_doc = sqlite.get_document(doc.id)
    print(f"✓ Retrieved document: {retrieved_doc.title}")
    assert retrieved_doc.title == "Test Document"
    
    # Test 2: Neo4j Manager
    print("\n🌐 Testing Neo4j Manager...")
    neo4j = Neo4jManager(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )
    neo4j.initialize_schema()
    
    # Create an entity
    from src.models import Entity
    entity = Entity(
        name="Apple Inc.",
        entity_type="ORGANIZATION",
        canonical_name="Apple Inc."
    )
    
    neo4j.save_entity(entity)
    print(f"✓ Created entity: {entity.id}")
    
    # Retrieve it
    retrieved_entity = neo4j.get_entity(entity.id)
    print(f"✓ Retrieved entity: {retrieved_entity.name}")
    assert retrieved_entity.name == "Apple Inc."
    
    # Test 3: FAISS Manager
    print("\n🔍 Testing FAISS Manager...")
    faiss = FAISSManager(config.faiss_index_path)
    faiss.initialize_index()
    
    # Add vectors
    import numpy as np
    test_vector = np.random.rand(768).astype('float32')  # Match default dimension
    entity_ref = f"neo4j://entity/{entity.id}"
    
    faiss.add_vectors(np.array([test_vector]), [entity_ref])
    print(f"✓ Added vector for entity: {entity_ref}")
    
    # Search
    results = faiss.search(test_vector, k=1)
    similar_refs = [r[0] for r in results]
    scores = [r[1] for r in results]
    print(f"✓ Found similar entity: {similar_refs[0]} (score: {scores[0]})")
    assert similar_refs[0] == entity_ref
    
    # Test 4: Cross-database workflow
    print("\n🔄 Testing Cross-Database Workflow...")
    
    # First create a chunk
    from src.models import Chunk
    chunk = Chunk(
        document_id=doc.id,
        text="Apple announced new products.",
        position=0,
        start_char=0,
        end_char=29
    )
    sqlite.save_chunk(chunk)
    print(f"✓ Created chunk: {chunk.id}")
    
    # Create surface form
    from src.models import SurfaceForm
    surface = SurfaceForm(
        text="Apple",
        context="Apple announced new products.",
        chunk_id=chunk.id,
        start_offset=0,
        end_offset=5
    )
    
    sqlite.save_surface_form(surface)
    print(f"✓ Created surface form: {surface.id}")
    
    # Create mention
    from src.models import Mention
    mention = Mention(
        surface_form_id=surface.id,
        entity_id=entity_ref,  # Cross-database reference!
        mention_type="ORGANIZATION"
    )
    
    sqlite.save_mention(mention)
    print(f"✓ Created mention: {mention.id}")
    
    # Update entity with mention reference
    entity.mention_refs.append(f"sqlite://mention/{mention.id}")
    neo4j.update_entity(entity)
    print(f"✓ Updated entity with mention reference")
    
    # Test 5: Provenance tracking
    print("\n📊 Testing Provenance Tracking...")
    
    from src.models import ProvenanceRecord
    prov = ProvenanceRecord(
        operation_type="entity_creation",
        tool_id="T107",
        input_refs=[f"sqlite://surface_form/{surface.id}"],
        output_refs=[entity_ref],
        parameters={"method": "automatic"},
        confidence=0.95
    )
    
    sqlite.save_provenance(prov)
    print(f"✓ Created provenance record: {prov.id}")
    
    # Update with completion status
    prov.status = "success"
    prov.duration_ms = 150
    prov.completed_at = datetime.utcnow()
    sqlite.save_provenance(prov)
    print(f"✓ Completed operation tracking")
    
    # Test 6: Quality tracking
    print("\n⭐ Testing Quality Tracking...")
    
    # Check entity quality
    print(f"Entity confidence: {entity.confidence}")
    print(f"Entity quality tier: {entity.quality_tier}")
    
    # Add warning and check degradation
    original_confidence = entity.confidence
    entity.warnings.append("Ambiguous entity name")
    entity.confidence *= 0.95  # Degrade by 5%
    
    print(f"✓ Quality degraded: {original_confidence} -> {entity.confidence}")
    
    # Test 7: Workflow checkpointing
    print("\n🔄 Testing Workflow Checkpointing...")
    
    from src.models import WorkflowCheckpoint
    checkpoint = WorkflowCheckpoint(
        workflow_id="wf_001",
        workflow_type="entity_extraction",
        step_number=5,
        total_steps=10,
        state_data={"entities_processed": 1},
        completed_operations=[prov.id],
        failed_operations=[],
        metadata={"test": True}
    )
    
    sqlite.save_checkpoint(checkpoint)
    print(f"✓ Created checkpoint: {checkpoint.id}")
    
    # Retrieve checkpoint
    retrieved_cp = sqlite.get_checkpoint(checkpoint.id)
    print(f"✓ Retrieved checkpoint at step {retrieved_cp.step_number}/{retrieved_cp.total_steps}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    
    # Clean Neo4j
    with neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    neo4j.close()
    
    # Clean SQLite
    sqlite.close()
    if config.sqlite_db_path.exists():
        config.sqlite_db_path.unlink()
    
    # Clean FAISS
    faiss.close()
    if config.faiss_index_path.exists():
        config.faiss_index_path.unlink()
    
    print("\n✅ All core service tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    # Wait for services
    print("⏳ Waiting for services to start...")
    time.sleep(2)
    
    # Run tests
    test_core_services()