#!/usr/bin/env python
"""Real integration test to verify all components work without mocking."""

import asyncio
import time
from pathlib import Path

from src.utils.config import Config
from src.utils.database import DatabaseManager
from src.models.base import UniversalReference


async def test_real_integration():
    """Test real integration with all databases."""
    print("🧪 Starting Real Integration Test")
    print("=" * 50)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Create config
    config = Config()
    config.redis_url = "redis://localhost:6380"  # Updated port
    config.sqlite_db_path = Path("./data/test_integration.db")
    config.faiss_index_path = Path("./data/test_faiss_index")
    config.checkpoint_dir = Path("./data/test_checkpoints")
    config.ensure_directories()
    
    # Initialize database manager
    print("\n🗄️ Initializing databases...")
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    
    # Check health
    health = db_manager.health_check()
    print(f"Health check: {health}")
    assert health["neo4j"]["status"] == "healthy", "Neo4j is not healthy"
    assert health["sqlite"]["status"] == "healthy", "SQLite is not healthy"
    assert health["faiss"]["status"] == "healthy", "FAISS is not healthy"
    
    # Test 1: Identity Service
    print("\n📋 Testing Identity Service (T107)...")
    identity = db_manager.get_identity_service()
    
    # Create surface form
    surface_ref = identity.create_surface_form(
        surface_text="Apple Inc.",
        context="Apple Inc. announced new products today.",
        chunk_ref="sqlite://chunk/test_chunk_1",
        start_offset=0,
        end_offset=10
    )
    print(f"Created surface form: {surface_ref}")
    assert surface_ref.startswith("sqlite://surface_form/"), "Invalid surface form reference"
    
    # Create mention
    mention_ref = identity.create_mention(
        surface_form_ref=surface_ref,
        mention_type="ORGANIZATION",
        attributes={"industry": "technology", "ticker": "AAPL"}
    )
    print(f"Created mention: {mention_ref}")
    assert mention_ref.startswith("sqlite://mention/"), "Invalid mention reference"
    
    # Resolve entity
    entity_ref = identity.resolve_entity(
        mention_ref=mention_ref,
        candidate_refs=[],
        create_if_missing=True
    )
    print(f"Resolved entity: {entity_ref}")
    assert entity_ref.startswith("neo4j://entity/"), "Invalid entity reference"
    
    # Test 2: Provenance Service
    print("\n📊 Testing Provenance Service (T110)...")
    provenance = db_manager.get_provenance_service()
    
    # Start tracking an operation
    operation_id = provenance.start_operation(
        operation_type="entity_resolution",
        tool_id="T107",
        input_refs=[surface_ref, mention_ref],
        parameters={"method": "automatic"}
    )
    print(f"Started operation: {operation_id}")
    
    # Complete operation
    provenance.complete_operation(
        operation_id=operation_id,
        output_refs=[entity_ref],
        status="success",
        confidence=0.95,
        metadata={"resolved": True}
    )
    print(f"Completed operation: {operation_id}")
    
    # Get lineage
    lineage = provenance.get_lineage(entity_ref, direction="backward", max_depth=10)
    print(f"Entity lineage: {len(lineage)} operations")
    assert len(lineage) > 0, "No lineage found"
    
    # Test 3: Quality Service
    print("\n⭐ Testing Quality Service (T111)...")
    quality = db_manager.get_quality_service()
    
    # Assess quality
    assessment = quality.assess_quality(entity_ref, method="automatic")
    print(f"Quality assessment: confidence={assessment.confidence}, tier={assessment.quality_tier}")
    assert 0 <= assessment.confidence <= 1, "Invalid confidence score"
    
    # Test quality propagation
    propagated_conf, warnings = quality.propagate_quality(
        input_refs=[entity_ref],
        operation_type="merge_operation",
        parameters={"partial_results": True}
    )
    print(f"Propagated confidence: {propagated_conf}")
    assert propagated_conf < assessment.confidence, "Quality should degrade with partial results"
    
    # Test 4: Workflow State Service
    print("\n🔄 Testing Workflow State Service (T121)...")
    workflow = db_manager.get_workflow_state_service()
    
    # Start workflow
    workflow_id = workflow.start_workflow(
        workflow_type="test_workflow",
        total_steps=10,
        metadata={"test": True}
    )
    print(f"Started workflow: {workflow_id}")
    
    # Update progress
    workflow.update_progress(
        workflow_id=workflow_id,
        step_number=5,
        operation_id=operation_id,
        state_updates={"entities_processed": 1}
    )
    
    # Get status
    status = workflow.get_workflow_status(workflow_id)
    print(f"Workflow status: {status['status']}, progress: {status['progress_percent']}%")
    assert status["progress_percent"] == 50.0, "Progress calculation error"
    
    # Complete workflow
    checkpoint = workflow.complete_workflow(
        workflow_id=workflow_id,
        final_state={"success": True}
    )
    print(f"Completed workflow with checkpoint: {checkpoint.id}")
    
    # Test 5: Cross-database references
    print("\n🔗 Testing Cross-Database References...")
    
    # Test FAISS integration
    faiss_manager = db_manager.faiss
    
    # Add a vector
    import numpy as np
    test_vector = np.random.rand(384).astype('float32')
    faiss_manager.add_vectors([test_vector], [entity_ref])
    print(f"Added vector for entity: {entity_ref}")
    
    # Search similar
    similar_refs, scores = faiss_manager.search_similar(test_vector, k=1)
    print(f"Found similar entities: {similar_refs} with scores: {scores}")
    assert len(similar_refs) == 1, "Vector search failed"
    assert similar_refs[0] == entity_ref, "Wrong entity returned"
    
    # Test 6: Reference resolution
    print("\n🔍 Testing Reference Resolution...")
    
    # Resolve different reference types
    ref_types = [
        ("neo4j://entity/test_123", "neo4j", "entity", "test_123"),
        ("sqlite://mention/ment_456", "sqlite", "mention", "ment_456"),
        ("faiss://vector/789", "faiss", "vector", "789")
    ]
    
    for ref_str, expected_storage, expected_type, expected_id in ref_types:
        ref = UniversalReference.from_string(ref_str)
        assert ref.storage == expected_storage, f"Wrong storage for {ref_str}"
        assert ref.type == expected_type, f"Wrong type for {ref_str}"
        assert ref.id == expected_id, f"Wrong ID for {ref_str}"
        print(f"✓ Resolved {ref_str} correctly")
    
    # Test 7: Database statistics
    print("\n📈 Testing Database Statistics...")
    
    # Get Neo4j stats
    neo4j_stats = db_manager.neo4j.get_statistics()
    print(f"Neo4j: {neo4j_stats}")
    
    # Get SQLite stats
    sqlite_stats = db_manager.sqlite.get_statistics()
    print(f"SQLite: {sqlite_stats}")
    
    # Get FAISS stats
    faiss_stats = {"total_vectors": db_manager.faiss.index.ntotal}
    print(f"FAISS: {faiss_stats}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    db_manager.close()
    
    # Clean test files
    if config.sqlite_db_path.exists():
        config.sqlite_db_path.unlink()
    if config.faiss_index_path.exists():
        config.faiss_index_path.unlink()
    
    print("\n✅ All tests passed! System is working correctly.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_real_integration())