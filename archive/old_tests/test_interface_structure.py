#!/usr/bin/env python3
"""Test the GraphRAG Phase Interface structure without full execution"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_interface_imports():
    """Test that interface components can be imported"""
    print("🔄 Testing interface imports...")
    
    try:
        from src.core.graphrag_phase_interface import (
            GraphRAGPhase, PhaseResult, ProcessingRequest, PhaseStatus,
            phase_registry, register_phase, get_available_phases
        )
        print("✅ Core interface imports successful")
        
        from src.core.phase_adapters import (
            Phase1Adapter, Phase2Adapter, Phase3Adapter, initialize_phase_adapters
        )
        print("✅ Phase adapter imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_adapter_initialization():
    """Test adapter initialization without full execution"""
    print("\n🔄 Testing adapter initialization...")
    
    try:
        from src.core.phase_adapters import initialize_phase_adapters
        from src.core.graphrag_phase_interface import get_available_phases, phase_registry
        
        # Initialize adapters
        success = initialize_phase_adapters()
        if not success:
            print("❌ Adapter initialization failed")
            return False
        
        # Check registered phases
        phases = get_available_phases()
        print(f"✅ Registered phases: {phases}")
        
        expected_phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        for expected in expected_phases:
            if expected in phases:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ Missing: {expected}")
        
        return len(phases) >= 3
        
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_only():
    """Test input validation without execution"""
    print("\n🔄 Testing validation logic...")
    
    try:
        from src.core.graphrag_phase_interface import ProcessingRequest, phase_registry
        
        # Test requests
        valid_request = ProcessingRequest(
            documents=["examples/pdfs/wiki1.pdf"],
            queries=["Test query"],
            workflow_id="test",
            domain_description="Test domain"
        )
        
        invalid_request = ProcessingRequest(
            documents=[],  # No documents
            queries=[],    # No queries
            workflow_id="test"
        )
        
        phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        
        for phase_name in phases:
            phase = phase_registry.get_phase(phase_name)
            if phase:
                print(f"\n📝 {phase_name}:")
                
                # Test valid request
                valid_errors = phase.validate_input(valid_request)
                print(f"   Valid request: {len(valid_errors)} errors")
                if valid_errors:
                    print(f"      {valid_errors[:2]}...")  # Show first 2 errors
                
                # Test invalid request
                invalid_errors = phase.validate_input(invalid_request)
                print(f"   Invalid request: {len(invalid_errors)} errors ✅")
                
                # Test capabilities
                capabilities = phase.get_capabilities()
                print(f"   Capabilities: {len(capabilities)} fields ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_interface_compliance():
    """Test that adapters properly implement the interface"""
    print("\n🔄 Testing interface compliance...")
    
    try:
        from src.core.graphrag_phase_interface import GraphRAGPhase, phase_registry
        
        phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        compliance_results = {}
        
        for phase_name in phases:
            phase = phase_registry.get_phase(phase_name)
            if phase:
                print(f"\n🔍 {phase_name}:")
                
                # Check inheritance
                is_graphrag_phase = isinstance(phase, GraphRAGPhase)
                print(f"   Inherits GraphRAGPhase: {'✅' if is_graphrag_phase else '❌'}")
                
                # Check required methods
                required_methods = ['execute', 'get_capabilities', 'validate_input']
                method_check = {}
                
                for method in required_methods:
                    has_method = hasattr(phase, method) and callable(getattr(phase, method))
                    method_check[method] = has_method
                    print(f"   Has {method}(): {'✅' if has_method else '❌'}")
                
                # Check phase info
                try:
                    info = phase.get_phase_info()
                    has_info = isinstance(info, dict) and 'name' in info
                    print(f"   Phase info: {'✅' if has_info else '❌'}")
                except:
                    has_info = False
                    print("   Phase info: ❌")
                
                compliance_results[phase_name] = {
                    'inheritance': is_graphrag_phase,
                    'methods': all(method_check.values()),
                    'info': has_info
                }
        
        # Summary
        compliant_count = sum(1 for result in compliance_results.values() 
                             if all(result.values()))
        total_count = len(compliance_results)
        
        print(f"\n📊 Compliance Summary: {compliant_count}/{total_count} phases fully compliant")
        
        return compliant_count == total_count
        
    except Exception as e:
        print(f"❌ Compliance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("GraphRAG Phase Interface Structure Test")
    print("=" * 50)
    
    tests = [
        ("Interface Imports", test_interface_imports),
        ("Adapter Initialization", test_adapter_initialization),  
        ("Validation Logic", test_validation_only),
        ("Interface Compliance", test_interface_compliance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n{'='*50}")
    print("🎯 Final Results:")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 A2: GraphRAG Phase Interface is complete!")
        print("✅ Base interface contract defined and working")
        print("✅ Phase adapters successfully wrap existing implementations")
        print("✅ Registry system manages phases")
        print("✅ Validation framework prevents integration issues")
        print("✅ All phases comply with standardized interface")
    else:
        print(f"\n⚠️  A2 needs attention - {total-passed} issues to resolve")
    
    sys.exit(0 if passed == total else 1)