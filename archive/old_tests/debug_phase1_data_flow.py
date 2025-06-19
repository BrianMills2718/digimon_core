#!/usr/bin/env python3
"""Debug Phase 1 Data Flow - Check entity extraction pipeline"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_workflow_results():
    """Debug what the workflow actually returns vs what adapter expects"""
    print("🔍 Debug Phase 1 Data Flow")
    print("=" * 50)
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        from src.core.phase_adapters import Phase1Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        # Test workflow directly
        print("📋 Testing workflow directly...")
        workflow = VerticalSliceWorkflow()
        
        result = workflow.execute_workflow(
            pdf_path="examples/pdfs/wiki1.pdf",
            query="What are the main entities?",
            workflow_name="debug_test"
        )
        
        print(f"Status: {result.get('status')}")
        
        # Check workflow_summary
        workflow_summary = result.get("workflow_summary", {})
        print(f"\n📊 Workflow Summary Contents:")
        for key, value in workflow_summary.items():
            print(f"  {key}: {value}")
        
        # Check steps for entity counts
        steps = result.get("steps", {})
        print(f"\n📋 Step-by-step entity counts:")
        if "entity_extraction" in steps:
            entity_step = steps["entity_extraction"]
            print(f"  Entity extraction step: {entity_step}")
        
        if "entity_building" in steps:
            building_step = steps["entity_building"] 
            print(f"  Entity building step: {building_step}")
        
        # Now test adapter
        print(f"\n🔄 Testing adapter with same data...")
        adapter = Phase1Adapter()
        request = ProcessingRequest(
            documents=["examples/pdfs/wiki1.pdf"],
            queries=["What are the main entities?"],
            workflow_id="debug_adapter_test"
        )
        
        adapter_result = adapter.execute(request)
        print(f"Adapter result status: {adapter_result.status.value}")
        print(f"Adapter entity count: {adapter_result.entity_count}")
        print(f"Adapter relationship count: {adapter_result.relationship_count}")
        
        # Check what adapter got from workflow
        if hasattr(adapter_result, 'results') and adapter_result.results:
            raw_result = adapter_result.results.get("phase1_raw", {})
            raw_summary = raw_result.get("workflow_summary", {})
            print(f"\n🔍 Raw workflow summary in adapter:")
            for key, value in raw_summary.items():
                print(f"  {key}: {value}")
        
        workflow.close()
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_workflow_results()