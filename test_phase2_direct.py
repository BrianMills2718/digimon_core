#!/usr/bin/env python3
"""Direct Phase 2 Test - Identify specific Phase 2 failures"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_phase2_adapter():
    """Test Phase 2 adapter directly to identify issues"""
    print("🔍 Direct Phase 2 Test")
    print("=" * 50)
    
    try:
        from src.core.phase_adapters import Phase2Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        # Test Phase 2 adapter creation
        print("1. Creating Phase 2 adapter...")
        adapter = Phase2Adapter()
        print("✅ Phase 2 adapter created successfully")
        
        # Test capabilities
        print("\n2. Getting Phase 2 capabilities...")
        capabilities = adapter.get_capabilities()
        print(f"✅ Capabilities: {capabilities}")
        
        # Test validation with minimal request
        print("\n3. Testing input validation...")
        request = ProcessingRequest(
            documents=["examples/pdfs/wiki1.pdf"],
            queries=["What are the main entities?"],
            workflow_id="phase2_test",
            domain_description="Test domain for entity extraction"
        )
        
        validation_errors = adapter.validate_input(request)
        if validation_errors:
            print(f"❌ Validation errors: {validation_errors}")
            return False
        else:
            print("✅ Input validation passed")
        
        # Test actual execution
        print("\n4. Testing Phase 2 execution...")
        print("   Note: This may fail due to known issues")
        
        try:
            result = adapter.execute(request)
            print(f"📊 Result status: {result.status.value}")
            
            if result.status.value == "success":
                print(f"✅ Phase 2 execution successful!")
                print(f"   Entities: {result.entity_count}")
                print(f"   Relationships: {result.relationship_count}")
                print(f"   Execution time: {result.execution_time:.2f}s")
                return True
            else:
                print(f"❌ Phase 2 execution failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Phase 2 execution exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This suggests Phase 2 dependencies are missing or broken")
        return False
    except Exception as e:
        print(f"❌ Phase 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_dependencies():
    """Test Phase 2 dependencies individually"""
    print(f"\n🔧 Testing Phase 2 Dependencies")
    print("-" * 40)
    
    dependencies = [
        ("Enhanced Vertical Slice Workflow", "src.tools.phase2.enhanced_vertical_slice_workflow", "EnhancedVerticalSliceWorkflow"),
        ("Ontology Aware Extractor", "src.tools.phase2.t23c_ontology_aware_extractor", "OntologyAwareExtractor"),
        ("Gemini Ontology Generator", "src.ontology.gemini_ontology_generator", "GeminiOntologyGenerator"),
        ("Enhanced Identity Service", "src.core.enhanced_identity_service", "EnhancedIdentityService"),
    ]
    
    results = {}
    
    for name, module_path, class_name in dependencies:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {name}: Available")
            results[name] = True
        except ImportError as e:
            print(f"❌ {name}: Import error - {e}")
            results[name] = False
        except AttributeError as e:
            print(f"❌ {name}: Class not found - {e}")
            results[name] = False
        except Exception as e:
            print(f"❌ {name}: Other error - {e}")
            results[name] = False
    
    working = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nDependency Status: {working}/{total} working")
    
    return working >= total // 2  # At least half should work

if __name__ == "__main__":
    print("🧪 PHASE 2 DIRECT TESTING")
    print("=" * 60)
    
    tests = [
        ("Phase 2 Dependencies", test_phase2_dependencies),
        ("Phase 2 Adapter", test_phase2_adapter)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 PHASE 2 TEST RESULTS:")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\nOverall: {passed}/{total} working")
    
    if passed >= 1:
        print(f"\n📋 PHASE 2 DIAGNOSIS:")
        if results.get("Phase 2 Dependencies", False):
            print("✅ Dependencies available - issue likely in execution logic")
        else:
            print("❌ Missing dependencies - need to fix imports/implementations")
            
        if results.get("Phase 2 Adapter", False):
            print("✅ Adapter working - Phase 2 functional")
        else:
            print("❌ Adapter failing - core Phase 2 workflow broken")
    else:
        print(f"\n🚨 PHASE 2 COMPLETELY BROKEN")
        print("All core components failing - needs complete investigation")
    
    sys.exit(0 if passed >= 1 else 1)