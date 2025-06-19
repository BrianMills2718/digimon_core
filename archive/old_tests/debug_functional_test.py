#!/usr/bin/env python3
"""
Debug functional integration test issues
"""
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_phase1_simple():
    """Test Phase 1 workflow in isolation"""
    print("Testing Phase 1 workflow...")
    
    # Create test text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test document with Apple Inc and Google LLC entities.")
        test_file = f.name
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        
        workflow = VerticalSliceWorkflow()
        result = workflow.execute_workflow(
            pdf_path=test_file,
            query="What companies are mentioned?"
        )
        
        print(f"Status: {result.get('status')}")
        print(f"Steps completed: {len(result.get('steps', {}))}")
        
        if result.get('status') == 'success':
            print("✅ Phase 1 working")
            return True
        else:
            print(f"❌ Phase 1 failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 1 exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import os
        try:
            os.unlink(test_file)
        except:
            pass

def test_phase2_simple():
    """Test Phase 2 workflow in isolation"""
    print("\nTesting Phase 2 workflow...")
    
    try:
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        
        # Create test text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Research by Dr. Smith at Stanford University on artificial intelligence.")
            test_file = f.name
        
        workflow = EnhancedVerticalSliceWorkflow()
        result = workflow.execute_enhanced_workflow(
            test_file,
            "Who conducted the research?",
            "test_phase2"
        )
        
        print(f"Status: {result.get('status', 'no_status')}")
        
        if result and result.get('status') == 'success':
            print("✅ Phase 2 working") 
            return True
        else:
            print(f"❌ Phase 2 failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 2 exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import os
        try:
            os.unlink(test_file)
        except:
            pass

if __name__ == "__main__":
    print("🔧 DEBUG: Testing individual components\n")
    
    results = []
    results.append(test_phase1_simple())
    results.append(test_phase2_simple())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} components working")
    if all(results):
        print("✅ All basic components functional")
    else:
        print("❌ Some components have issues")