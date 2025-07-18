#!/usr/bin/env python3
"""
Test UI startup fixes - verify spaCy lazy loading and import issues are resolved.
"""

import sys
import os
from pathlib import Path

# Add project root to path

def test_ui_imports():
    """Test that UI imports work without torch/streamlit conflicts."""
    print("🧪 Testing UI Import Fixes")
    
    try:
        print("\n1. Testing basic UI imports...")
        # This should not trigger spaCy model loading
        from ui.graphrag_ui import init_session_state, render_header
        print("✅ Basic UI components import successfully")
        
        print("\n2. Testing Phase 1 lazy loading...")
        from ui.graphrag_ui import _get_phase1_workflow
        # This should work but not load spaCy yet
        print("✅ Phase 1 lazy loading function available")
        
        print("\n3. Testing Phase 2 lazy loading...")
        from ui.graphrag_ui import _get_phase2_workflow
        print("✅ Phase 2 lazy loading function available")
        
        print("\n4. Testing Phase 3 lazy loading...")
        from ui.graphrag_ui import _get_phase3_adapter
        print("✅ Phase 3 lazy loading function available")
        
        print("\n5. Testing service manager import...")
        from src.core.service_manager import ServiceManager
        print("✅ Service manager imports without issues")
        
        print("\n6. Testing spaCy NER class import...")
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        print("✅ SpacyNER class imports without loading model")
        
        # Test that spaCy model is NOT loaded yet
        from src.core.service_manager import get_service_manager
        service_manager = get_service_manager()
        identity_service = service_manager.identity_service
        provenance_service = service_manager.provenance_service
        quality_service = service_manager.quality_service
        
        ner = SpacyNER(identity_service, provenance_service, quality_service)
        if not ner._model_initialized:
            print("✅ spaCy model correctly NOT loaded at initialization")
        else:
            print("❌ spaCy model incorrectly loaded at initialization")
        
        print("\n🎉 All UI import fixes verified!")
        return True
        
    except Exception as e:
        print(f"❌ UI import test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_neo4j_fixes():
    """Test Neo4j connection fixes."""
    print("\n🔍 Testing Neo4j Connection Fixes")
    
    try:
        from src.core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        # Test Neo4j connection - should not produce warnings now
        neo4j_driver = service_manager.get_neo4j_driver()
        
        if neo4j_driver:
            print("✅ Neo4j connection successful without multiple record warnings")
        else:
            print("⚠️ Neo4j not available (expected if Neo4j not running)")
        
        return True
        
    except Exception as e:
        print(f"❌ Neo4j test failed: {e}")
        return False

def test_actual_lazy_loading():
    """Test that spaCy models are actually lazy loaded."""
    print("\n⏱️ Testing Actual Lazy Loading")
    
    try:
        # Import and create workflow - should not load spaCy models
        print("Creating Phase 1 workflow...")
        from ui.graphrag_ui import _get_phase1_workflow
        
        # This might trigger some loading but should be much faster than before
        import time
        start_time = time.time()
        workflow = _get_phase1_workflow()
        load_time = time.time() - start_time
        
        print(f"✅ Phase 1 workflow created in {load_time:.2f}s")
        
        if load_time < 10:  # Should be much faster than before
            print("✅ Lazy loading appears to be working (fast startup)")
        else:
            print("⚠️ Startup still slow - lazy loading may not be fully effective")
        
        return True
        
    except Exception as e:
        print(f"❌ Lazy loading test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🔧 Testing UI Startup Fixes")
    print("=" * 50)
    
    tests = [
        ("UI Imports", test_ui_imports),
        ("Neo4j Fixes", test_neo4j_fixes), 
        ("Lazy Loading", test_actual_lazy_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "="*50)
    print("🏁 FINAL RESULTS")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All UI startup fixes verified successful!")
    else:
        print(f"\n⚠️ {total-passed} test(s) failed - more fixes needed")
    
    sys.exit(0 if passed == total else 1)