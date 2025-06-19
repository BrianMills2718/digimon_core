#!/usr/bin/env python3
"""Quick test to verify if core system components work"""

def test_imports():
    """Test if core components can be imported"""
    print("🔍 Testing Core System Imports")
    
    results = []
    
    # Test Phase 1
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        print("✅ Phase 1: Can import")
        results.append(("Phase 1", True))
    except Exception as e:
        print(f"❌ Phase 1: Import failed - {e}")
        results.append(("Phase 1", False))
    
    # Test Phase 2  
    try:
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        print("✅ Phase 2: Can import")
        results.append(("Phase 2", True))
    except Exception as e:
        print(f"❌ Phase 2: Import failed - {e}")
        results.append(("Phase 2", False))
    
    # Test Phase 3
    try:
        from src.core.phase_adapters import Phase3Adapter
        print("✅ Phase 3: Can import")
        results.append(("Phase 3", True))
    except Exception as e:
        print(f"❌ Phase 3: Import failed - {e}")
        results.append(("Phase 3", False))
    
    return results

def test_quick_phase1():
    """Quick Phase 1 test"""
    print("\n🧪 Testing Phase 1 Functionality")
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        import tempfile
        
        # Create simple test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Dr. John Smith works at MIT.")
            test_file = f.name
        
        workflow = VerticalSliceWorkflow()
        
        # Test just the workflow creation
        print("✅ Phase 1: Workflow created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Phase 1: Failed - {e}")
        return False

if __name__ == "__main__":
    print("⚡ QUICK SYSTEM CHECK")
    print("=" * 30)
    
    import_results = test_imports()
    phase1_works = test_quick_phase1()
    
    print(f"\n📊 RESULTS:")
    working = sum(1 for _, success in import_results if success)
    total = len(import_results)
    
    print(f"Imports: {working}/{total} phases can import")
    print(f"Phase 1 Basic Test: {'✅ PASS' if phase1_works else '❌ FAIL'}")
    
    if working == total and phase1_works:
        print("\n🎉 CORE SYSTEM APPEARS FUNCTIONAL")
        print("Problem is likely just UI integration, not core system")
    else:
        print(f"\n⚠️ CORE SYSTEM HAS ISSUES")
        print("Need to fix core components before UI")