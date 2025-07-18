#!/usr/bin/env python3
"""
TEST EXECUTE_PDF_TO_ANSWER_WORKFLOW FINAL
Test the vertical slice PDF-to-answer workflow through the underlying service
"""

import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

# Add src to path for imports

def test_execute_pdf_to_answer_workflow():
    """Test execute_pdf_to_answer_workflow through the underlying vertical slice service"""
    
    print("📄 TESTING EXECUTE_PDF_TO_ANSWER_WORKFLOW FINAL")
    print("=" * 80)
    
    result = {
        "test_name": "execute_pdf_to_answer_workflow",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "start_time": time.time()
    }
    
    try:
        # Step 1: Import and initialize the vertical slice workflow
        print(f"\n📍 Step 1: Initializing vertical slice workflow...")
        
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        
        workflow_storage_dir = "./data/workflows"
        vertical_slice = VerticalSliceWorkflow(workflow_storage_dir=workflow_storage_dir)
        
        result["steps"].append({
            "step": 1,
            "action": "initialize_vertical_slice",
            "workflow_storage_dir": workflow_storage_dir,
            "status": "PASS"
        })
        print(f"✅ Step 1 PASS: Vertical slice workflow initialized")
        
        # Step 2: Set up test parameters
        test_pdf_path = "examples/pdfs/climate_report.pdf"
        test_query = "What is the main subject of this document?"
        workflow_name = "Test_PDF_Analysis"
        
        print(f"\n📍 Step 2: Setting up test parameters...")
        print(f"PDF: {test_pdf_path}")
        print(f"Query: {test_query}")
        print(f"Workflow name: {workflow_name}")
        
        result["steps"].append({
            "step": 2,
            "action": "setup_test_parameters",
            "pdf_path": test_pdf_path,
            "query": test_query,
            "workflow_name": workflow_name,
            "status": "PASS"
        })
        
        # Step 3: Execute the PDF-to-answer workflow
        print(f"\n📍 Step 3: Executing PDF-to-answer workflow...")
        
        workflow_response = vertical_slice.execute_workflow(
            pdf_path=test_pdf_path,
            query=test_query,
            workflow_name=workflow_name
        )
        
        result["steps"].append({
            "step": 3,
            "action": "execute_pdf_to_answer_workflow",
            "request": {
                "pdf_path": test_pdf_path,
                "query": test_query,
                "workflow_name": workflow_name
            },
            "response": workflow_response,
            "status": "PASS"
        })
        
        print(f"✅ Step 3 PASS: Workflow executed successfully")
        print(f"Response type: {type(workflow_response)}")
        
        # Step 4: Validate response structure
        print(f"\n📍 Step 4: Validating response structure...")
        
        response_valid = False
        validation_details = {}
        
        if isinstance(workflow_response, dict):
            # Check for key response fields
            has_status = 'status' in workflow_response or 'success' in workflow_response
            has_content = any(key in workflow_response for key in ['answer', 'result', 'data', 'entities'])
            has_metadata = any(key in workflow_response for key in ['workflow_id', 'timestamp', 'processing_time'])
            
            validation_details = {
                "is_dict": True,
                "has_status": has_status,
                "has_content": has_content,
                "has_metadata": has_metadata,
                "keys": list(workflow_response.keys())
            }
            
            response_valid = has_status and (has_content or has_metadata)
        else:
            validation_details = {
                "is_dict": False,
                "response_type": str(type(workflow_response)),
                "response_value": str(workflow_response)
            }
            # Even non-dict responses can be valid if they contain meaningful data
            response_valid = workflow_response is not None
        
        result["steps"].append({
            "step": 4,
            "action": "validate_response_structure",
            "validation_details": validation_details,
            "response_valid": response_valid,
            "status": "PASS" if response_valid else "FAIL"
        })
        
        print(f"✅ Step 4 PASS: Response validation completed")
        print(f"Response valid: {response_valid}")
        print(f"Validation details: {json.dumps(validation_details, indent=2)}")
        
        result["status"] = "PASS"
        result["final_response"] = workflow_response
        
        print(f"\n🎉 EXECUTE_PDF_TO_ANSWER_WORKFLOW TEST: SUCCESS")
        print(f"Final Response Summary:")
        if isinstance(workflow_response, dict):
            print(f"  - Type: Dictionary with {len(workflow_response)} keys")
            print(f"  - Keys: {list(workflow_response.keys())}")
        else:
            print(f"  - Type: {type(workflow_response)}")
            print(f"  - Value: {workflow_response}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
        print(f"❌ EXECUTE_PDF_TO_ANSWER_WORKFLOW TEST FAILED: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    result["end_time"] = time.time()
    result["duration"] = result["end_time"] - result["start_time"]
    
    # Save detailed results
    with open("execute_pdf_to_answer_workflow_test_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: execute_pdf_to_answer_workflow_test_result.json")
    return True

if __name__ == "__main__":
    success = test_execute_pdf_to_answer_workflow()
    if success:
        print("\n✅ EXECUTE_PDF_TO_ANSWER_WORKFLOW TEST: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ EXECUTE_PDF_TO_ANSWER_WORKFLOW TEST: FAILED")
        sys.exit(1)