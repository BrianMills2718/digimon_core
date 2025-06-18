#\!/usr/bin/env python3
"""Direct Phase 1 Test - Check what workflow actually returns"""

import os
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_phase1_workflow_direct():
    """Test Phase 1 workflow directly to see what it returns"""
    print("🔍 Direct Phase 1 Workflow Test")
    print("=" * 50)
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        
        # Create workflow
        workflow = VerticalSliceWorkflow()
        
        # Execute with real data
        result = workflow.execute_workflow(
            pdf_path="examples/pdfs/wiki1.pdf",
            query="What are the main entities?",
            workflow_name="direct_test"
        )
        
        print(f"Result status: {result.get('status')}")
        print(f"Result keys: {list(result.keys())}")
        
        # Check workflow_summary specifically
        workflow_summary = result.get("workflow_summary", {})
        print(f"\n📊 Workflow Summary:")
        print(f"  Keys: {list(workflow_summary.keys())}")
        print(f"  Entities extracted: {workflow_summary.get('entities_extracted', 'NOT FOUND')}")
        print(f"  Relationships found: {workflow_summary.get('relationships_found', 'NOT FOUND')}")
        print(f"  Chunks created: {workflow_summary.get('chunks_created', 'NOT FOUND')}")
        print(f"  Graph entities: {workflow_summary.get('graph_entities', 'NOT FOUND')}")
        print(f"  Graph edges: {workflow_summary.get('graph_edges', 'NOT FOUND')}")
        
        # Check individual steps
        steps = result.get("steps", {})
        print(f"\n📋 Individual Steps:")
        for step_name, step_data in steps.items():
            if isinstance(step_data, dict):
                print(f"  {step_name}:")
                if "total_entities" in step_data:
                    print(f"    Total entities: {step_data['total_entities']}")
                if "total_relationships" in step_data:
                    print(f"    Total relationships: {step_data['total_relationships']}")
                if "entities_created" in step_data:
                    print(f"    Entities created: {step_data['entities_created']}")
                if "edges_created" in step_data:
                    print(f"    Edges created: {step_data['edges_created']}")
        
        # Test adapter translation
        print(f"\n🔄 Testing Phase1Adapter translation...")
        from src.core.phase_adapters import Phase1Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        adapter = Phase1Adapter()
        request = ProcessingRequest(
            documents=["examples/pdfs/wiki1.pdf"],
            queries=["What are the main entities?"],
            workflow_id="adapter_test"
        )
        
        adapter_result = adapter.execute(request)
        print(f"Adapter status: {adapter_result.status.value}")
        print(f"Adapter entity count: {adapter_result.entity_count}")
        print(f"Adapter relationship count: {adapter_result.relationship_count}")
        
        workflow.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_phase1_workflow_direct()
