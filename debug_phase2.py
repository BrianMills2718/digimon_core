#!/usr/bin/env python3
"""Debug Phase 2 workflow execution"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow

def debug_workflow():
    """Debug Phase 2 workflow execution"""
    print("Debugging Phase 2 workflow...")
    
    workflow = EnhancedVerticalSliceWorkflow()
    
    pdf_path = 'examples/pdfs/wiki1.pdf'
    domain_description = 'Technology and innovation domain'
    queries = ['What are the main entities?']
    
    try:
        result = workflow.execute_enhanced_workflow(
            pdf_path=pdf_path,
            domain_description=domain_description,
            queries=queries,
            workflow_name='test_debug'
        )
        
        print(f"\nWorkflow Status: {result.get('status')}")
        
        if result.get('status') != 'success':
            print(f"Overall Error: {result.get('error')}")
            
            # Check each step's results
            print("\nStep Results:")
            for key, value in result.items():
                if isinstance(value, dict):
                    status = value.get('status', 'N/A')
                    error = value.get('error', '')
                    if error:
                        print(f"- {key}: {status} - {error}")
                    else:
                        print(f"- {key}: {status}")
        else:
            print("✅ Workflow completed successfully!")
            print(f"- Entities: {result.get('entity_count', 0)}")
            print(f"- Relationships: {result.get('relationship_count', 0)}")
            
    except Exception as e:
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflow()