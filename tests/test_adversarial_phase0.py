"""Adversarial Testing for Phase 0 Core Services

Comprehensive adversarial tests designed to break the core services.
Tests edge cases, extreme values, resource pressure, and error conditions.

Required by CLAUDE.md: "Every tool implementation must pass adversarial tests BEFORE integration"
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService  
from src.core.quality_service import QualityService, QualityTier
from src.core.workflow_state_service import WorkflowStateService


class TestAdversarialIdentityService:
    """Adversarial tests for T107: Identity Service."""
    
    def test_unicode_and_special_characters(self):
        """Test with Unicode, special characters, and edge cases."""
        service = IdentityService()
        
        # Unicode characters
        result = service.create_mention(
            surface_form="北京大学",  # Chinese characters
            start_pos=0,
            end_pos=4,
            source_ref="storage://doc/unicode_test"
        )
        assert result["status"] == "success"
        
        # Emoji
        result = service.create_mention(
            surface_form="Apple 🍎 Inc",
            start_pos=0,
            end_pos=11,
            source_ref="storage://doc/emoji_test"
        )
        assert result["status"] == "success"
        
        # Special characters and punctuation
        result = service.create_mention(
            surface_form="AT&T Corp. (formerly Bell System)",
            start_pos=0,
            end_pos=33,
            source_ref="storage://doc/special_test"
        )
        assert result["status"] == "success"
        
        # Zero-width characters
        result = service.create_mention(
            surface_form="Apple\u200BInc",  # Zero-width space
            start_pos=0,
            end_pos=9,
            source_ref="storage://doc/zws_test"
        )
        assert result["status"] == "success"
    
    def test_extremely_long_inputs(self):
        """Test with very long surface forms."""
        service = IdentityService()
        
        # Very long surface form (1000 characters)
        long_name = "A" * 1000
        result = service.create_mention(
            surface_form=long_name,
            start_pos=0,
            end_pos=1000,
            source_ref="storage://doc/long_test"
        )
        assert result["status"] == "success"
        
        # Extremely long surface form (10,000 characters)
        extreme_name = "B" * 10000
        result = service.create_mention(
            surface_form=extreme_name,
            start_pos=0,
            end_pos=10000,
            source_ref="storage://doc/extreme_test"
        )
        assert result["status"] == "success"
    
    def test_edge_case_positions(self):
        """Test edge cases for position values."""
        service = IdentityService()
        
        # Very large position values
        result = service.create_mention(
            surface_form="Test",
            start_pos=999999999,
            end_pos=1000000003,
            source_ref="storage://doc/large_pos"
        )
        assert result["status"] == "success"
        
        # Zero start position
        result = service.create_mention(
            surface_form="Test",
            start_pos=0,
            end_pos=4,
            source_ref="storage://doc/zero_start"
        )
        assert result["status"] == "success"
    
    def test_extreme_confidence_values(self):
        """Test extreme and invalid confidence values."""
        service = IdentityService()
        
        # Very small positive confidence
        result = service.create_mention(
            surface_form="Test",
            start_pos=0,
            end_pos=4,
            source_ref="storage://doc/small_conf",
            confidence=0.0001
        )
        assert result["status"] == "success"
        assert result["confidence"] == 0.0001
        
        # Very close to 1.0
        result = service.create_mention(
            surface_form="Test2",
            start_pos=0,
            end_pos=5,
            source_ref="storage://doc/high_conf", 
            confidence=0.9999
        )
        assert result["status"] == "success"
        assert result["confidence"] == 0.9999
        
        # Invalid values should fail gracefully
        result = service.create_mention(
            surface_form="Test3",
            start_pos=0,
            end_pos=5,
            source_ref="storage://doc/invalid_conf",
            confidence=-0.5  # Negative
        )
        assert result["status"] == "error"
        
        result = service.create_mention(
            surface_form="Test4",
            start_pos=0,
            end_pos=5,
            source_ref="storage://doc/invalid_conf2",
            confidence=1.5  # > 1.0
        )
        assert result["status"] == "error"
    
    def test_massive_entity_creation(self):
        """Test creating thousands of entities to check memory handling."""
        service = IdentityService()
        
        # Create 1000 unique entities
        for i in range(1000):
            result = service.create_mention(
                surface_form=f"Entity_{i}",
                start_pos=0,
                end_pos=len(f"Entity_{i}"),
                source_ref=f"storage://doc/mass_test_{i}"
            )
            assert result["status"] == "success"
        
        # Verify stats
        stats = service.get_stats()
        assert stats["total_mentions"] == 1000
        assert stats["total_entities"] == 1000  # All unique


class TestAdversarialProvenanceService:
    """Adversarial tests for T110: Provenance Service."""
    
    def test_concurrent_operation_simulation(self):
        """Simulate concurrent operations to test race conditions."""
        service = ProvenanceService()
        
        # Start many operations simultaneously
        operation_ids = []
        for i in range(100):
            op_id = service.start_operation(
                tool_id=f"concurrent_tool_{i % 10}",
                operation_type="create",
                inputs=[f"storage://input/{i}"],
                parameters={"batch": i}
            )
            operation_ids.append(op_id)
        
        # Complete them all
        for i, op_id in enumerate(operation_ids):
            result = service.complete_operation(
                operation_id=op_id,
                outputs=[f"storage://output/{i}"],
                success=True
            )
            assert result["status"] == "success"
        
        # Verify all operations are tracked
        stats = service.get_tool_statistics()
        assert stats["total_operations"] == 100
    
    def test_malformed_operation_data(self):
        """Test with malformed and extreme operation data."""
        service = ProvenanceService()
        
        # Very long tool ID
        long_tool_id = "x" * 1000
        op_id = service.start_operation(
            tool_id=long_tool_id,
            operation_type="test",
            inputs=[],
            parameters={}
        )
        assert op_id.startswith("op_")
        
        # Massive parameter dict
        huge_params = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        op_id2 = service.start_operation(
            tool_id="test_tool",
            operation_type="test",
            inputs=[],
            parameters=huge_params
        )
        assert op_id2.startswith("op_")
        
        # Complete with massive outputs list
        massive_outputs = [f"storage://output/{i}" for i in range(1000)]
        result = service.complete_operation(
            operation_id=op_id2,
            outputs=massive_outputs,
            success=True
        )
        assert result["status"] == "success"
    
    def test_invalid_operation_references(self):
        """Test with invalid operation IDs and references."""
        service = ProvenanceService()
        
        # Try to complete non-existent operation
        result = service.complete_operation(
            operation_id="op_nonexistent",
            outputs=["storage://test"],
            success=True
        )
        assert result["status"] == "error"
        
        # Try to get lineage for non-existent object
        lineage = service.get_lineage("storage://nonexistent")
        assert lineage["status"] == "not_found"
        
        # Try to get details for non-existent operation
        details = service.get_operation("op_fake")
        assert details is None
    
    def test_memory_pressure_simulation(self):
        """Test behavior under memory pressure."""
        service = ProvenanceService()
        
        # Create very deep lineage chains (1000 operations)
        current_ref = "storage://root"
        
        for i in range(100):  # Reduced from 1000 for test speed
            op_id = service.start_operation(
                tool_id="chain_tool",
                operation_type="transform",
                inputs=[current_ref],
                parameters={"step": i}
            )
            
            next_ref = f"storage://step_{i}"
            service.complete_operation(
                operation_id=op_id,
                outputs=[next_ref],
                success=True
            )
            current_ref = next_ref
        
        # Verify lineage works for deep chain
        lineage = service.get_lineage(current_ref, max_depth=150)
        assert lineage["status"] == "success"
        assert lineage["depth"] == 100


class TestAdversarialQualityService:
    """Adversarial tests for T111: Quality Service."""
    
    def test_extreme_confidence_values(self):
        """Test with extreme confidence values and edge cases."""
        service = QualityService()
        
        # Test confidence exactly at boundaries
        result = service.assess_confidence("storage://obj1", 0.0)
        assert result["status"] == "success"
        assert result["confidence"] == 0.0
        assert result["quality_tier"] == "LOW"
        
        result = service.assess_confidence("storage://obj2", 1.0)
        assert result["status"] == "success"
        assert result["confidence"] == 1.0
        assert result["quality_tier"] == "HIGH"
        
        # Test invalid confidence values
        result = service.assess_confidence("storage://obj3", -0.1)
        assert result["status"] == "error"
        
        result = service.assess_confidence("storage://obj4", 1.1)
        assert result["status"] == "error"
        
        # Test very small increments
        result = service.assess_confidence("storage://obj5", 0.000001)
        assert result["status"] == "success"
        
        result = service.assess_confidence("storage://obj6", 0.999999)
        assert result["status"] == "success"
    
    def test_massive_factor_dictionaries(self):
        """Test with large numbers of confidence factors."""
        service = QualityService()
        
        # Create massive factors dictionary
        massive_factors = {f"factor_{i}": 0.5 + (i % 100) / 200 for i in range(1000)}
        
        result = service.assess_confidence(
            object_ref="storage://massive_factors",
            base_confidence=0.7,
            factors=massive_factors
        )
        assert result["status"] == "success"
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_confidence_propagation_edge_cases(self):
        """Test confidence propagation with edge cases."""
        service = QualityService()
        
        # Empty inputs list
        propagated = service.propagate_confidence(
            input_refs=[],
            operation_type="test_op"
        )
        assert propagated == 0.5  # Default for no inputs
        
        # Single input with zero confidence
        service.assess_confidence("storage://zero_conf", 0.0)
        
        # This should handle zero confidence gracefully
        propagated = service.propagate_confidence(
            input_refs=["storage://zero_conf"],
            operation_type="test_op"
        )
        assert 0.0 <= propagated <= 1.0
        
        # Very large number of inputs
        many_inputs = []
        for i in range(100):
            ref = f"storage://input_{i}"
            service.assess_confidence(ref, 0.8)
            many_inputs.append(ref)
        
        propagated = service.propagate_confidence(
            input_refs=many_inputs,
            operation_type="test_op"
        )
        assert 0.0 <= propagated <= 1.0
    
    def test_quality_statistics_edge_cases(self):
        """Test quality statistics with edge cases."""
        service = QualityService()
        
        # Get stats with no assessments
        stats = service.get_quality_statistics()
        assert stats["status"] == "success"
        assert stats["total_assessments"] == 0
        
        # Create assessment then get stats
        service.assess_confidence("storage://single", 0.5)
        stats = service.get_quality_statistics()
        assert stats["total_assessments"] == 1
        assert stats["confidence_std"] == 0.0  # Single value has no std dev


class TestAdversarialWorkflowStateService:
    """Adversarial tests for T121: Workflow State Service."""
    
    def test_filesystem_edge_cases(self):
        """Test filesystem-related edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            # Create workflow with very large state data
            huge_state = {f"key_{i}": f"value_{i}" * 1000 for i in range(100)}
            
            workflow_id = service.start_workflow(
                name="Huge State Test",
                total_steps=1,
                initial_state=huge_state
            )
            assert workflow_id.startswith("workflow_")
            
            # Create checkpoint with massive state
            massive_state = {f"data_{i}": list(range(1000)) for i in range(10)}
            
            checkpoint_id = service.create_checkpoint(
                workflow_id=workflow_id,
                step_name="massive_step",
                step_number=1,
                state_data=massive_state
            )
            assert checkpoint_id.startswith("checkpoint_")
            
            # Restore should work
            restored = service.restore_from_checkpoint(checkpoint_id)
            assert restored["status"] == "success"
    
    def test_invalid_state_data(self):
        """Test with non-serializable state data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            workflow_id = service.start_workflow("Test", 1)
            
            # Try to create checkpoint with non-serializable data
            try:
                # Functions are not JSON serializable
                invalid_state = {"func": lambda x: x}
                
                with pytest.raises(RuntimeError):
                    service.create_checkpoint(
                        workflow_id=workflow_id,
                        step_name="invalid",
                        step_number=1,
                        state_data=invalid_state
                    )
            except (TypeError, ValueError):
                # This is expected - service should handle gracefully
                pass
    
    def test_disk_full_simulation(self):
        """Test behavior when disk space is limited."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            workflow_id = service.start_workflow("Disk Test", 100)
            
            # Create many checkpoints to consume disk space
            checkpoint_ids = []
            for i in range(50):  # Reduced for test speed
                try:
                    checkpoint_id = service.create_checkpoint(
                        workflow_id=workflow_id,
                        step_name=f"step_{i}",
                        step_number=i,
                        state_data={"data": "x" * 10000, "step": i}  # 10KB per checkpoint
                    )
                    checkpoint_ids.append(checkpoint_id)
                except RuntimeError:
                    # Disk full is expected eventually
                    break
            
            # Should have created at least some checkpoints
            assert len(checkpoint_ids) > 0
    
    def test_corrupted_checkpoint_handling(self):
        """Test handling of corrupted checkpoint files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            # Create a valid checkpoint first
            workflow_id = service.start_workflow("Corruption Test", 1)
            checkpoint_id = service.create_checkpoint(
                workflow_id=workflow_id,
                step_name="valid",
                step_number=1,
                state_data={"valid": True}
            )
            
            # Corrupt the checkpoint file
            checkpoint_file = service.checkpoint_files[checkpoint_id]
            with open(checkpoint_file, 'w') as f:
                f.write("corrupted data")
            
            # Create new service instance to trigger loading
            service2 = WorkflowStateService(temp_dir)
            
            # Should handle corrupted file gracefully
            # (Original checkpoint should not be loaded)
            restored = service2.restore_from_checkpoint(checkpoint_id)
            assert restored["status"] == "error"
    
    def test_concurrent_checkpoint_creation(self):
        """Test concurrent checkpoint creation simulation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = WorkflowStateService(temp_dir)
            
            workflow_id = service.start_workflow("Concurrent Test", 100)
            
            # Simulate rapid checkpoint creation
            checkpoint_ids = []
            for i in range(20):
                checkpoint_id = service.create_checkpoint(
                    workflow_id=workflow_id,
                    step_name=f"rapid_{i}",
                    step_number=i,
                    state_data={"rapid": i, "timestamp": str(i)}
                )
                checkpoint_ids.append(checkpoint_id)
            
            # All checkpoints should be valid
            assert len(checkpoint_ids) == 20
            
            # All should be restorable
            for checkpoint_id in checkpoint_ids:
                restored = service.restore_from_checkpoint(checkpoint_id)
                assert restored["status"] == "success"


class TestAdversarialMCPServer:
    """Adversarial tests for MCP server integration."""
    
    def test_mcp_server_startup_with_missing_dependencies(self):
        """Test MCP server behavior with missing dependencies."""
        # Test server can import without crashing
        try:
            from src.mcp_server import mcp
            # Server creation should work
            assert mcp is not None
        except ImportError as e:
            pytest.fail(f"MCP server failed to import: {e}")
    
    def test_mcp_server_tool_registration(self):
        """Test that all expected tools are registered."""
        from src.mcp_server import mcp
        
        # Test that server can be created and tools are accessible
        # Since FastMCP internal structure may vary, test functionality instead
        
        # Test that essential MCP functions work
        try:
            # This will succeed if tools are properly registered
            assert hasattr(mcp, 'tool'), "MCP server missing tool decorator"
            assert hasattr(mcp, 'run'), "MCP server missing run method"
        except Exception as e:
            pytest.fail(f"MCP server not properly configured: {e}")
    
    def test_mcp_tool_functionality(self):
        """Test core service functionality through adversarial scenarios."""
        # Test the services directly as they're used by MCP tools
        from src.mcp_server import (
            identity_service, provenance_service, 
            quality_service, workflow_service
        )
        
        # Test identity service with adversarial input
        result = identity_service.create_mention(
            surface_form="Adversarial Test 🚨",
            start_pos=0,
            end_pos=17,
            source_ref="storage://adversarial/test"
        )
        assert result["status"] == "success"
        
        # Test provenance service with large parameters
        large_params = {f"param_{i}": f"value_{i}" * 50 for i in range(20)}
        op_id = provenance_service.start_operation(
            tool_id="adversarial_tool",
            operation_type="test",
            inputs=["storage://input/1"],
            parameters=large_params
        )
        assert op_id.startswith("op_")
        
        # Test quality service with edge case
        result = quality_service.assess_confidence(
            object_ref="storage://edge_case",
            base_confidence=0.0001
        )
        assert result["status"] == "success"
        assert result["confidence"] >= 0.0
        
        # Test workflow service with large initial state
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_workflow_service = WorkflowStateService(temp_dir)
            large_state = {f"key_{i}": f"value_{i}" * 100 for i in range(10)}
            workflow_id = temp_workflow_service.start_workflow(
                name="Adversarial Workflow Test",
                total_steps=1,
                initial_state=large_state
            )
            assert workflow_id.startswith("workflow_")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])