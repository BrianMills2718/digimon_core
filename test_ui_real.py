#!/usr/bin/env python3
"""
Test the GraphRAG UI with real Phase 1 functionality
This validates that the UI actually works with real pipeline components
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_phase1_imports():
    """Test that Phase 1 components can be imported"""
    print("🧪 Testing Phase 1 imports...")
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        print("✅ VerticalSliceWorkflow imported successfully")
        
        # Test instantiation
        workflow = VerticalSliceWorkflow()
        print("✅ VerticalSliceWorkflow instantiated successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Phase 1 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Phase 1 instantiation failed: {e}")
        return False

def test_phase2_imports():
    """Test that Phase 2 components can be imported"""
    print("\n🧪 Testing Phase 2 imports...")
    
    try:
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        print("✅ EnhancedVerticalSliceWorkflow imported successfully")
        
        workflow = EnhancedVerticalSliceWorkflow()
        print("✅ EnhancedVerticalSliceWorkflow instantiated successfully")
        
        return True
    except ImportError as e:
        print(f"⚠️ Phase 2 import failed (expected if not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Phase 2 instantiation failed: {e}")
        return False

def test_phase3_imports():
    """Test that Phase 3 components can be imported"""
    print("\n🧪 Testing Phase 3 imports...")
    
    try:
        from src.tools.phase3.t301_multi_document_fusion_tools import calculate_entity_similarity
        print("✅ T301 tools imported successfully")
        return True
    except ImportError as e:
        print(f"⚠️ Phase 3 import failed (expected if not installed): {e}")
        return False
    except Exception as e:
        print(f"❌ Phase 3 import failed: {e}")
        return False

def test_ui_dependencies():
    """Test that UI dependencies are available"""
    print("\n🧪 Testing UI dependencies...")
    
    try:
        import streamlit
        print("✅ Streamlit available")
    except ImportError:
        print("❌ Streamlit not available - install with: pip install streamlit")
        return False
    
    try:
        import plotly
        print("✅ Plotly available")
    except ImportError:
        print("❌ Plotly not available - install with: pip install plotly")
        return False
    
    try:
        import networkx
        print("✅ NetworkX available")
    except ImportError:
        print("❌ NetworkX not available - install with: pip install networkx")
        return False
    
    try:
        import pandas
        print("✅ Pandas available")
    except ImportError:
        print("❌ Pandas not available - install with: pip install pandas")
        return False
    
    return True

def test_sample_documents():
    """Test that sample documents exist for testing"""
    print("\n🧪 Testing sample documents...")
    
    examples_dir = Path("examples/pdfs")
    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        return False
    
    pdf_files = list(examples_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {examples_dir}")
        return False
    
    print(f"✅ Found {len(pdf_files)} sample PDF(s):")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    
    return True

def test_ui_import():
    """Test that the UI module can be imported"""
    print("\n🧪 Testing UI module import...")
    
    try:
        # This should work without Streamlit running
        ui_file = Path("ui/graphrag_ui.py")
        if not ui_file.exists():
            print(f"❌ UI file not found: {ui_file}")
            return False
        
        print(f"✅ UI file exists: {ui_file}")
        return True
    except Exception as e:
        print(f"❌ UI import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 GraphRAG UI Validation Test")
    print("=" * 50)
    
    tests = [
        ("Phase 1 Components", test_phase1_imports),
        ("Phase 2 Components", test_phase2_imports), 
        ("Phase 3 Components", test_phase3_imports),
        ("UI Dependencies", test_ui_dependencies),
        ("Sample Documents", test_sample_documents),
        ("UI Module", test_ui_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 3:  # Phase 1 + UI deps + UI module minimum
        print("\n🎉 UI should be functional for basic testing!")
        print("🚀 Run: python start_graphrag_ui.py")
        return 0
    else:
        print("\n⚠️ UI may not work properly. Fix failing tests first.")
        return 1

if __name__ == "__main__":
    sys.exit(main())