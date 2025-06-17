"""Test core services integration."""

import pytest
import asyncio
from pathlib import Path

from src.utils.config import Config
from src.utils.database import DatabaseManager
from src.tools.phase8 import (
    T107_IdentityService,
    T110_ProvenanceService,
    T111_QualityService,
    T121_WorkflowStateService
)


@pytest.fixture
def test_config():
    """Create test configuration."""
    config = Config()
    # Use test databases
    config.sqlite_db_path = Path("./data/test_metadata.db")
    config.faiss_index_path = Path("./data/test_faiss_index")
    config.checkpoint_dir = Path("./data/test_checkpoints")
    config.ensure_directories()
    return config


@pytest.fixture
def db_manager(test_config):
    """Create database manager for tests."""
    db = DatabaseManager(test_config)
    db.initialize()
    yield db
    db.close()
    # Cleanup test files
    if test_config.sqlite_db_path.exists():
        test_config.sqlite_db_path.unlink()


@pytest.mark.asyncio
async def test_identity_service_workflow(db_manager):
    """Test identity service workflow."""
    identity_tool = T107_IdentityService(db_manager)
    
    # Create surface form
    surface_result = await identity_tool.execute({
        "operation": "create_surface_form",
        "surface_text": "Apple Inc.",
        "context": "Apple Inc. announced new products today.",
        "chunk_ref": "sqlite://chunk/test_chunk_1",
        "start_offset": 0,
        "end_offset": 10
    })
    
    assert "surface_form_ref" in surface_result
    assert surface_result["confidence"] == 1.0
    
    # Create mention
    mention_result = await identity_tool.execute({
        "operation": "create_mention",
        "surface_form_ref": surface_result["surface_form_ref"],
        "mention_type": "ORGANIZATION",
        "attributes": {"industry": "technology"}
    })
    
    assert "mention_ref" in mention_result
    assert mention_result["confidence"] == 1.0


@pytest.mark.asyncio
async def test_workflow_state_service(db_manager):
    """Test workflow state service."""
    workflow_tool = T121_WorkflowStateService(db_manager)
    
    # Start workflow
    start_result = await workflow_tool.execute({
        "operation": "start_workflow",
        "workflow_type": "test_workflow",
        "total_steps": 10,
        "metadata": {"test": True}
    })
    
    assert "workflow_id" in start_result
    workflow_id = start_result["workflow_id"]
    
    # Update progress
    update_result = await workflow_tool.execute({
        "operation": "update_progress",
        "workflow_id": workflow_id,
        "step_number": 5,
        "state_updates": {"processed": 50}
    })
    
    assert update_result["progress_percent"] == 50.0
    
    # Get status
    status_result = await workflow_tool.execute({
        "operation": "get_status",
        "workflow_id": workflow_id
    })
    
    assert status_result["status"] == "active"
    assert status_result["current_step"] == 5
    
    # Complete workflow
    complete_result = await workflow_tool.execute({
        "operation": "complete_workflow",
        "workflow_id": workflow_id,
        "final_state": {"success": True}
    })
    
    assert complete_result["status"] == "completed"


@pytest.mark.asyncio
async def test_quality_service(db_manager):
    """Test quality service."""
    quality_tool = T111_QualityService(db_manager)
    
    # Test quality propagation
    prop_result = await quality_tool.execute({
        "operation": "propagate_quality",
        "input_refs": ["neo4j://entity/1", "neo4j://entity/2"],
        "operation_type": "merge_operation",
        "parameters": {"partial_results": True}
    })
    
    assert "propagated_confidence" in prop_result
    assert prop_result["propagated_confidence"] < 1.0  # Degraded due to partial results
    assert "partial_data" in prop_result["degradation_factors"]


@pytest.mark.asyncio
async def test_provenance_tracking(db_manager):
    """Test provenance service."""
    provenance_tool = T110_ProvenanceService(db_manager)
    identity_tool = T107_IdentityService(db_manager)
    
    # Create some operations to track
    surface_result = await identity_tool.execute({
        "operation": "create_surface_form",
        "surface_text": "Test Entity",
        "context": "This is a test entity.",
        "chunk_ref": "sqlite://chunk/test_chunk_2",
        "start_offset": 0,
        "end_offset": 11
    })
    
    # Get statistics
    stats_result = await provenance_tool.execute({
        "operation": "get_statistics"
    })
    
    assert stats_result["total_operations"] > 0
    assert "T107" in stats_result["by_tool"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])