"""Test Core Services Implementation

Basic tests to verify the four core services work correctly.
Tests are designed for minimal implementations.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService  
from src.core.quality_service import QualityService, QualityTier
from src.core.workflow_state_service import WorkflowStateService


class TestIdentityService:
    """Test T107: Identity Service."""
    
    def test_create_mention_basic(self):
        """Test basic mention creation."""
        service = IdentityService()
        
        result = service.create_mention(
            surface_form="Apple Inc",
            start_pos=0,
            end_pos=9,
            source_ref="storage://document/doc_123"
        )
        
        assert result["status"] == "success"
        assert "mention_id" in result
        assert "entity_id" in result
        assert result["normalized_form"] == "apple inc"
    
    def test_entity_linking(self):
        """Test that identical surface forms link to same entity."""
        service = IdentityService()
        
        # Create first mention
        result1 = service.create_mention(
            surface_form="Apple Inc",
            start_pos=0,
            end_pos=9,
            source_ref="storage://document/doc_123"
        )
        
        # Create second mention with same normalized form
        result2 = service.create_mention(
            surface_form="apple inc",
            start_pos=50,
            end_pos=59,
            source_ref="storage://document/doc_123"
        )
        
        # Should link to same entity
        assert result1["entity_id"] == result2["entity_id"]
    
    def test_input_validation(self):
        """Test input validation."""
        service = IdentityService()
        
        # Empty surface form
        result = service.create_mention("", 0, 5, "storage://doc/1")
        assert result["status"] == "error"
        
        # Invalid position range
        result = service.create_mention("test", 10, 5, "storage://doc/1")
        assert result["status"] == "error"
        
        # Invalid confidence
        result = service.create_mention("test", 0, 4, "storage://doc/1", confidence=1.5)
        assert result["status"] == "error"


class TestProvenanceService:
    """Test T110: Provenance Service."""
    
    def test_operation_lifecycle(self):
        """Test complete operation lifecycle."""
        service = ProvenanceService()
        
        # Start operation
        op_id = service.start_operation(
            tool_id="test_tool",
            operation_type="create",
            inputs=["storage://doc/input1"],
            parameters={"param1": "value1"}
        )
        
        assert op_id.startswith("op_")
        
        # Complete operation
        result = service.complete_operation(
            operation_id=op_id,
            outputs=["storage://entity/output1"],
            success=True
        )
        
        assert result["status"] == "success"
        assert result["operation_id"] == op_id
    
    def test_lineage_tracking(self):
        """Test lineage chain creation."""
        service = ProvenanceService()
        
        # Create chain of operations
        op1 = service.start_operation("loader", "create", [], {})
        service.complete_operation(op1, ["storage://doc/doc1"], True)
        
        op2 = service.start_operation("processor", "transform", ["storage://doc/doc1"], {})
        service.complete_operation(op2, ["storage://entity/ent1"], True)
        
        # Check lineage
        lineage = service.get_lineage("storage://entity/ent1")
        assert lineage["status"] == "success"
        assert lineage["depth"] == 2
        assert len(lineage["lineage"]) == 2
    
    def test_tool_statistics(self):
        """Test tool usage statistics."""
        service = ProvenanceService()
        
        # Complete some operations
        op1 = service.start_operation("tool1", "create", [], {})
        service.complete_operation(op1, ["storage://out1"], True)
        
        op2 = service.start_operation("tool1", "create", [], {})
        service.complete_operation(op2, ["storage://out2"], False, "Test error")
        
        stats = service.get_tool_statistics()
        assert stats["status"] == "success"
        assert stats["tool_statistics"]["tool1"]["total_calls"] == 2
        assert stats["tool_statistics"]["tool1"]["successes"] == 1
        assert stats["tool_statistics"]["tool1"]["failures"] == 1


class TestQualityService:
    """Test T111: Quality Service."""
    
    def test_confidence_assessment(self):
        """Test confidence assessment."""
        service = QualityService()
        
        result = service.assess_confidence(
            object_ref="storage://entity/ent1",
            base_confidence=0.85,
            factors={"frequency": 0.9, "context": 0.8}
        )
        
        assert result["status"] == "success"
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["quality_tier"] == "HIGH"
    
    def test_confidence_propagation(self):
        """Test confidence propagation through operations."""
        service = QualityService()
        
        # Assess some input objects
        service.assess_confidence("storage://input1", 0.9)
        service.assess_confidence("storage://input2", 0.8)
        
        # Propagate confidence
        propagated = service.propagate_confidence(
            input_refs=["storage://input1", "storage://input2"],
            operation_type="spacy_ner"
        )
        
        # Should be degraded from inputs
        assert 0.0 <= propagated <= 0.9  # Less than max input
    
    def test_quality_tiers(self):
        """Test quality tier assignment."""
        service = QualityService()
        
        # High confidence
        result = service.assess_confidence("storage://obj1", 0.85)
        assert result["quality_tier"] == "HIGH"
        
        # Medium confidence
        result = service.assess_confidence("storage://obj2", 0.65) 
        assert result["quality_tier"] == "MEDIUM"
        
        # Low confidence
        result = service.assess_confidence("storage://obj3", 0.35)
        assert result["quality_tier"] == "LOW"
    
    def test_quality_filtering(self):
        """Test filtering objects by quality."""
        service = QualityService()
        
        # Create objects with different qualities
        service.assess_confidence("storage://high1", 0.9)
        service.assess_confidence("storage://medium1", 0.6)
        service.assess_confidence("storage://low1", 0.3)
        
        objects = ["storage://high1", "storage://medium1", "storage://low1"]
        
        # Filter high quality only
        high_quality = service.filter_by_quality(
            objects, 
            min_tier=QualityTier.HIGH
        )
        assert len(high_quality) == 1
        assert "storage://high1" in high_quality


class TestWorkflowStateService:
    """Test T121: Workflow State Service."""
    
    def test_workflow_lifecycle(self):
        """Test complete workflow lifecycle."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            # Start workflow
            workflow_id = service.start_workflow(
                name="Test Workflow",
                total_steps=3,
                initial_state={"step": 0, "data": "initial"}
            )
            
            assert workflow_id.startswith("workflow_")
            
            # Create checkpoint
            checkpoint_id = service.create_checkpoint(
                workflow_id=workflow_id,
                step_name="step1",
                step_number=1,
                state_data={"step": 1, "data": "step1_done"}
            )
            
            assert checkpoint_id.startswith("checkpoint_")
    
    def test_checkpoint_restoration(self):
        """Test checkpoint restoration."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            workflow_id = service.start_workflow("Test", 2)
            
            # Create checkpoint with state
            test_state = {"key": "value", "step": 1}
            checkpoint_id = service.create_checkpoint(
                workflow_id=workflow_id,
                step_name="test_step",
                step_number=1,
                state_data=test_state
            )
            
            # Restore from checkpoint
            restored = service.restore_from_checkpoint(checkpoint_id)
            
            assert restored["status"] == "success"
            assert restored["state_data"] == test_state
            assert restored["step_number"] == 1
    
    def test_workflow_progress_tracking(self):
        """Test workflow progress updates."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            workflow_id = service.start_workflow("Progress Test", 5)
            
            # Update progress
            result = service.update_workflow_progress(
                workflow_id=workflow_id,
                step_number=3,
                status="running"
            )
            
            assert result["status"] == "success"
            assert result["current_step"] == 3
            
            # Check status
            status = service.get_workflow_status(workflow_id)
            assert status["current_step"] == 3
            assert status["status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])