#!/usr/bin/env python3
"""Test Phase 2 integration after fixing API compatibility issues"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow

def test_phase2_integration():
    """Test Phase 2 workflow execution after API fixes"""
    print("Testing Phase 2 Integration Fix...")
    
    # Initialize workflow
    workflow = EnhancedVerticalSliceWorkflow()
    print("✓ Phase 2 workflow initialized")
    
    # Test with simple example
    pdf_path = "examples/pdfs/wiki1.pdf"
    domain_description = "Technology and innovation domain focusing on companies, products, and technological developments"
    queries = ["What are the main entities and relationships?"]
    
    try:
        # Execute workflow
        print("\nExecuting Phase 2 workflow...")
        result = workflow.execute_enhanced_workflow(
            pdf_path=pdf_path,
            domain_description=domain_description,
            queries=queries,
            workflow_name="test_phase2_fix"
        )
        
        # Check results
        if result.get("status") == "success":
            print("\n✅ SUCCESS: Phase 2 workflow completed!")
            print(f"- Entities extracted: {result.get('entity_count', 0)}")
            print(f"- Relationships found: {result.get('relationship_count', 0)}")
            print(f"- Execution time: {result.get('execution_time', 0):.2f}s")
            
            # Test ontology generation
            if "ontology_generation" in result:
                ontology = result["ontology_generation"].get("ontology", {})
                print(f"\n📋 Domain Ontology Generated:")
                print(f"- Entity types: {len(ontology.get('entity_types', []))}")
                print(f"- Relationship types: {len(ontology.get('relationship_types', []))}")
            
            return True
            
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Check if we have API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set, embeddings will use mock values")
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set, using mock Gemini responses")
    
    success = test_phase2_integration()
    
    if success:
        print("\n🎉 Phase 2 integration fix verified!")
        print("The API compatibility issue has been resolved.")
    else:
        print("\n❌ Phase 2 integration still has issues")
        print("Further investigation needed")
    
    sys.exit(0 if success else 1)