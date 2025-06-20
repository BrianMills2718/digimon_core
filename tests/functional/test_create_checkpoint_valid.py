#!/usr/bin/env python3
"""
TEST CREATE_CHECKPOINT WITH VALID WORKFLOW_ID
Prove that create_checkpoint works correctly with a valid workflow ID
"""

import sys
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_create_checkpoint_with_valid_workflow():
    """Test create_checkpoint with a valid workflow_id"""
    
    print("🔧 TESTING CREATE_CHECKPOINT WITH VALID WORKFLOW_ID")
    print("=" * 80)
    
    # Import required services
    try:
        from src.core.workflow_state_service import WorkflowStateService
        
        workflow_service = WorkflowStateService("./data/workflows")
        print("✅ Workflow service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import workflow service: {e}")
        return False
    
    result = {
        "test_name": "create_checkpoint_with_valid_workflow",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "start_time": time.time()
    }
    
    try:
        # Step 1: Create a new workflow and capture the valid workflow_id
        print("\n📍 Step 1: Creating new workflow...")
        workflow_id = workflow_service.start_workflow(
            name="Create_Checkpoint_Test_Workflow",
            total_steps=5,
            initial_state={"test_phase": "checkpoint_validation", "progress": 0}
        )
        
        result["steps"].append({
            "step": 1,
            "action": "start_workflow",
            "request": {
                "name": "Create_Checkpoint_Test_Workflow",
                "total_steps": 5,
                "initial_state": {"test_phase": "checkpoint_validation", "progress": 0}
            },
            "response": workflow_id,
            "status": "PASS"
        })
        print(f"✅ Step 1 PASS: Created workflow with valid ID: {workflow_id}")
        
        # Step 2: Immediately call create_checkpoint with the valid workflow_id
        print("\n📍 Step 2: Creating checkpoint with valid workflow_id...")
        checkpoint_result = workflow_service.create_checkpoint(
            workflow_id=workflow_id,
            step_name="validation_checkpoint",
            step_number=2,
            state_data={"checkpoint_phase": "mid_process", "validated": True},
            metadata={"test_reason": "valid_workflow_id_verification"}
        )
        
        result["steps"].append({
            "step": 2,
            "action": "create_checkpoint",
            "request": {
                "workflow_id": workflow_id,
                "step_name": "validation_checkpoint",
                "step_number": 2,
                "state_data": {"checkpoint_phase": "mid_process", "validated": True},
                "metadata": {"test_reason": "valid_workflow_id_verification"}
            },
            "response": checkpoint_result,
            "status": "PASS"
        })
        print(f"✅ Step 2 PASS: Created checkpoint: {checkpoint_result}")
        
        result["status"] = "PASS"
        print(f"\n🎉 CREATE_CHECKPOINT TEST: SUCCESS")
        print(f"Valid workflow_id: {workflow_id}")
        print(f"Checkpoint created: {checkpoint_result}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
        print(f"❌ CREATE_CHECKPOINT TEST FAILED: {str(e)}")
        return False
    
    result["end_time"] = time.time()
    result["duration"] = result["end_time"] - result["start_time"]
    
    # Save detailed results
    with open("create_checkpoint_valid_test_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Test results saved to: create_checkpoint_valid_test_result.json")
    return True

if __name__ == "__main__":
    success = test_create_checkpoint_with_valid_workflow()
    if success:
        print("\n✅ CREATE_CHECKPOINT VALIDATION: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ CREATE_CHECKPOINT VALIDATION: FAILED")
        sys.exit(1)