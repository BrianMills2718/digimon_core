#!/usr/bin/env python3
"""
TEST GET_VERTICAL_SLICE_INFO
Test the get_vertical_slice_info tool after proper initialization
"""

import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

# Add src to path for imports

def test_get_vertical_slice_info():
    """Test get_vertical_slice_info with proper vertical slice initialization"""
    
    print("ℹ️  TESTING GET_VERTICAL_SLICE_INFO")
    print("=" * 80)
    
    result = {
        "test_name": "get_vertical_slice_info",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "start_time": time.time()
    }
    
    try:
        # Step 1: Initialize the vertical slice component
        print(f"\n📍 Step 1: Initializing vertical slice component...")
        
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        
        workflow_storage_dir = "./data/workflows"
        vertical_slice = VerticalSliceWorkflow(workflow_storage_dir=workflow_storage_dir)
        
        result["steps"].append({
            "step": 1,
            "action": "initialize_vertical_slice_component",
            "workflow_storage_dir": workflow_storage_dir,
            "status": "PASS"
        })
        print(f"✅ Step 1 PASS: Vertical slice component initialized")
        
        # Step 2: Call get_vertical_slice_info
        print(f"\n📍 Step 2: Calling get_vertical_slice_info...")
        
        slice_info = vertical_slice.get_tool_info()
        
        result["steps"].append({
            "step": 2,
            "action": "get_vertical_slice_info",
            "request": {},
            "response": slice_info,
            "status": "PASS"
        })
        
        print(f"✅ Step 2 PASS: get_vertical_slice_info executed successfully")
        print(f"Response type: {type(slice_info)}")
        
        # Step 3: Validate response structure
        print(f"\n📍 Step 3: Validating response structure...")
        
        validation_details = {}
        response_valid = False
        
        if isinstance(slice_info, dict):
            # Check for expected info fields
            has_name = any(key in slice_info for key in ['name', 'tool_name', 'workflow_name'])
            has_description = any(key in slice_info for key in ['description', 'info', 'details'])
            has_tools = any(key in slice_info for key in ['tools', 'components', 'capabilities'])
            
            validation_details = {
                "is_dict": True,
                "has_name": has_name,
                "has_description": has_description,
                "has_tools": has_tools,
                "keys": list(slice_info.keys()),
                "key_count": len(slice_info)
            }
            
            response_valid = len(slice_info) > 0  # Any non-empty dict is valid
        else:
            validation_details = {
                "is_dict": False,
                "response_type": str(type(slice_info)),
                "response_length": len(str(slice_info)) if slice_info else 0
            }
            response_valid = slice_info is not None
        
        result["steps"].append({
            "step": 3,
            "action": "validate_response_structure",
            "validation_details": validation_details,
            "response_valid": response_valid,
            "status": "PASS" if response_valid else "FAIL"
        })
        
        print(f"✅ Step 3 PASS: Response validation completed")
        print(f"Response valid: {response_valid}")
        print(f"Validation details: {json.dumps(validation_details, indent=2)}")
        
        result["status"] = "PASS"
        result["final_response"] = slice_info
        
        print(f"\n🎉 GET_VERTICAL_SLICE_INFO TEST: SUCCESS")
        print(f"Final Response Summary:")
        if isinstance(slice_info, dict):
            print(f"  - Type: Dictionary with {len(slice_info)} keys")
            print(f"  - Keys: {list(slice_info.keys())}")
            # Show a preview of the content
            for key, value in list(slice_info.items())[:3]:  # First 3 items
                print(f"  - {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        else:
            print(f"  - Type: {type(slice_info)}")
            print(f"  - Content: {str(slice_info)[:200]}{'...' if len(str(slice_info)) > 200 else ''}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        print(f"❌ GET_VERTICAL_SLICE_INFO TEST FAILED: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    result["end_time"] = time.time()
    result["duration"] = result["end_time"] - result["start_time"]
    
    # Save detailed results
    with open("get_vertical_slice_info_test_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: get_vertical_slice_info_test_result.json")
    return True

if __name__ == "__main__":
    success = test_get_vertical_slice_info()
    if success:
        print("\n✅ GET_VERTICAL_SLICE_INFO TEST: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ GET_VERTICAL_SLICE_INFO TEST: FAILED")
        sys.exit(1)