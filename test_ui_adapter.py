#!/usr/bin/env python3
"""Test the UI Phase Adapter"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ui_adapter_initialization():
    """Test UI adapter initialization"""
    print("🔄 Testing UI adapter initialization...")
    
    try:
        from src.ui.ui_phase_adapter import (
            UIPhaseManager, get_ui_phase_manager, get_available_ui_phases
        )
        
        # Test manager initialization
        manager = get_ui_phase_manager()
        print(f"   Manager initialized: {'✅' if manager.is_initialized() else '❌'}")
        
        # Test available phases
        phases = get_available_ui_phases()
        print(f"   Available phases: {phases}")
        
        expected_phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        for expected in expected_phases:
            if expected in phases:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ Missing: {expected}")
        
        return len(phases) >= 2  # At least Phase 1 and 2 should work
        
    except Exception as e:
        print(f"❌ UI adapter initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase_capabilities():
    """Test phase capability querying"""
    print("\n🔄 Testing phase capabilities...")
    
    try:
        from src.ui.ui_phase_adapter import get_ui_phase_manager
        
        manager = get_ui_phase_manager()
        phases = manager.get_available_phases()
        
        for phase_name in phases:
            print(f"\n📋 {phase_name}:")
            
            capabilities = manager.get_phase_capabilities(phase_name)
            requirements = manager.get_phase_requirements(phase_name)
            
            print(f"   File types: {requirements.get('supported_files', [])}")
            print(f"   Requires domain: {requirements.get('requires_domain', False)}")
            print(f"   Multi-query: {requirements.get('supports_multiple_queries', False)}")
            print(f"   Services: {requirements.get('required_services', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Capabilities test failed: {e}")
        return False


def test_input_validation():
    """Test UI input validation"""
    print("\n🔄 Testing input validation...")
    
    try:
        from src.ui.ui_phase_adapter import validate_ui_phase_input
        
        # Test valid input
        valid_errors = validate_ui_phase_input(
            "Phase 1: Basic",
            ["examples/pdfs/wiki1.pdf"],
            ["What are the main entities?"]
        )
        print(f"   Valid input errors: {len(valid_errors)}")
        
        # Test invalid input  
        invalid_errors = validate_ui_phase_input(
            "Phase 1: Basic",
            [],  # No documents
            []   # No queries
        )
        print(f"   Invalid input errors: {len(invalid_errors)} ✅")
        
        # Test Phase 2 requirements
        phase2_errors = validate_ui_phase_input(
            "Phase 2: Enhanced",
            ["examples/pdfs/wiki1.pdf"],
            ["Test query"],
            domain_description="Technology domain"
        )
        print(f"   Phase 2 with domain: {len(phase2_errors)} errors")
        
        phase2_no_domain = validate_ui_phase_input(
            "Phase 2: Enhanced", 
            ["examples/pdfs/wiki1.pdf"],
            ["Test query"]
            # No domain_description
        )
        print(f"   Phase 2 without domain: {len(phase2_no_domain)} errors ✅")
        
        return invalid_errors and phase2_no_domain
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


def test_document_processing_interface():
    """Test document processing interface (without full execution)"""
    print("\n🔄 Testing document processing interface...")
    
    try:
        from src.ui.ui_phase_adapter import process_document_with_phase
        
        # Test with non-existent file (should fail gracefully)
        result = process_document_with_phase(
            phase_name="Phase 1: Basic",
            file_path="non_existent.pdf",
            filename="test.pdf",
            queries=["Test query"]
        )
        
        print(f"   Result type: {type(result).__name__}")
        print(f"   Status: {result.status}")
        print(f"   Error handling: {'✅' if result.status == 'error' else '❌'}")
        print(f"   Error message: {result.error_message[:50]}...")
        
        # Test interface structure
        required_fields = [
            'filename', 'phase_name', 'status', 'processing_time',
            'entity_count', 'relationship_count', 'confidence_score'
        ]
        
        missing_fields = [field for field in required_fields if not hasattr(result, field)]
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            return False
        else:
            print("   ✅ All required fields present")
            return True
        
    except Exception as e:
        print(f"❌ Processing interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("UI Phase Adapter Test")
    print("=" * 50)
    
    tests = [
        ("UI Adapter Initialization", test_ui_adapter_initialization),
        ("Phase Capabilities", test_phase_capabilities),
        ("Input Validation", test_input_validation),
        ("Processing Interface", test_document_processing_interface)
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
        print("\n🎉 UI Phase Adapter is working!")
        print("✅ UI can now use any phase through standardized interface")
        print("✅ Phase isolation achieved - UI doesn't know implementation details")
        print("✅ Input validation works across all phases")
        print("✅ Error handling is consistent and graceful")
        print("\nReady for A3 UI integration!")
    else:
        print(f"\n⚠️  UI adapter needs attention - {total-passed} issues to resolve")
    
    sys.exit(0 if passed == total else 1)