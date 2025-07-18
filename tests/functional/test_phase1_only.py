#!/usr/bin/env python3
"""
Phase 1 only functional integration test
"""
import tempfile
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent.parent.parent  # Go up from tests/functional/

def test_phase1_functional():
    """Test Phase 1 end-to-end functionality"""
    print("🔍 Testing Phase 1 functional integration...")
    
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        
        # Create test document
        test_content = """
        Research Report on Machine Learning
        
        This research was conducted by Dr. Jennifer Martinez at Stanford University 
        in collaboration with Prof. David Lee at University of California, Berkeley.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        # Test workflow
        workflow_config = create_unified_workflow_config(phase=Phase.PHASE1, optimization_level=OptimizationLevel.STANDARD)
workflow = PipelineOrchestrator(workflow_config)
        result = workflow.execute_workflow(
            pdf_path=test_file,
            query="Who conducted the research?"
        )
        
        # Verify results
        passed = (
            result.get("status") == "success" and
            result.get("steps", {}).get("entity_extraction", {}).get("total_entities", 0) > 0
        )
        
        print(f"Status: {result.get('status')}")
        print(f"Entities found: {result.get('steps', {}).get('entity_extraction', {}).get('total_entities', 0)}")
        print(f"Relationships found: {result.get('steps', {}).get('relationship_extraction', {}).get('total_relationships', 0)}")
        
        return passed
        
    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        return False
    finally:
        import os
        try:
            os.unlink(test_file)
        except:
            pass

if __name__ == "__main__":
    print("🔴 PHASE 1 FUNCTIONAL INTEGRATION TEST")
    print("=" * 50)
    
    result = test_phase1_functional()
    
    if result:
        print("✅ PASSED Phase 1 Functional")
        print("✅ REORGANIZATION VALIDATION: SUCCESS")
    else:
        print("❌ FAILED Phase 1 Functional")
        print("❌ REORGANIZATION VALIDATION: FAILED")