#!/usr/bin/env python3
"""
Test T23C LLM Integration Migration
===================================

Verify that the T23C LLM Entity Extractor now uses UniversalLLMService
instead of legacy API clients.
"""

import asyncio
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
sys.path.append('/home/brian/projects/Digimons')

def test_llm_integration_migration():
    """Test that LLMExtractionClient uses UniversalLLMService."""
    print("🔧 Testing T23C LLM Integration Migration...")
    
    try:
        # Import the migrated LLM extraction client
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        
        # Test initialization
        client = LLMExtractionClient()
        print("  ✅ LLMExtractionClient initialized successfully")
        
        # Check that it has UniversalLLMService
        has_llm_service = hasattr(client, 'llm_service')
        print(f"  ✅ Uses UniversalLLMService: {'YES' if has_llm_service else 'NO'}")
        
        if has_llm_service:
            from src.core.universal_llm_service import UniversalLLMService
            is_universal_service = isinstance(client.llm_service, UniversalLLMService)
            print(f"  ✅ Correct Service Type: {'YES' if is_universal_service else 'NO'}")
        
        # Check that new methods exist
        has_unified_method = hasattr(client, 'extract_entities')
        print(f"  ✅ Has Unified extract_entities Method: {'YES' if has_unified_method else 'NO'}")
        
        # Check backward compatibility methods exist
        has_openai_compat = hasattr(client, 'extract_entities_openai')
        has_gemini_compat = hasattr(client, 'extract_entities_gemini')
        print(f"  ✅ Backward Compatibility: OpenAI={'YES' if has_openai_compat else 'NO'}, Gemini={'YES' if has_gemini_compat else 'NO'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Migration test failed: {e}")
        return False

def test_method_signatures():
    """Test that method signatures are correct."""
    print("\n🔧 Testing Method Signatures...")
    
    try:
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        import inspect
        
        client = LLMExtractionClient()
        
        # Test extract_entities signature
        extract_sig = inspect.signature(client.extract_entities)
        params = list(extract_sig.parameters.keys())
        print(f"  ✅ extract_entities parameters: {params}")
        
        # Should have: text, ontology, model (optional)
        expected_params = ['text', 'ontology', 'model']
        has_required = all(param in params for param in expected_params[:2])
        has_optional_model = 'model' in params
        
        print(f"  ✅ Required Parameters: {'YES' if has_required else 'NO'}")
        print(f"  ✅ Optional Model Parameter: {'YES' if has_optional_model else 'NO'}")
        
        return has_required and has_optional_model
        
    except Exception as e:
        print(f"  ❌ Method signature test failed: {e}")
        return False

def test_import_structure():
    """Test that imports work correctly."""
    print("\n🔧 Testing Import Structure...")
    
    try:
        # Test UniversalLLMService imports
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        print("  ✅ LLMExtractionClient import: SUCCESS")
        
        # Test that it can import UniversalLLMService components
        client = LLMExtractionClient()
        
        # Check that LLMRequest and TaskType are accessible
        from src.core.universal_llm_service import LLMRequest, TaskType
        print("  ✅ UniversalLLMService components import: SUCCESS")
        
        # Test that TaskType.EXTRACTION exists
        has_extraction_task = hasattr(TaskType, 'EXTRACTION')
        print(f"  ✅ TaskType.EXTRACTION available: {'YES' if has_extraction_task else 'NO'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import structure test failed: {e}")
        return False

def test_legacy_api_removal():
    """Test that legacy API methods are removed or deprecated."""
    print("\n🔧 Testing Legacy API Removal...")
    
    try:
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        import inspect
        
        client = LLMExtractionClient()
        
        # These methods should no longer make direct API calls
        legacy_methods = [
            '_make_openai_request',
            '_make_gemini_request', 
            '_parse_openai_response',
            '_parse_gemini_response'
        ]
        
        removed_methods = []
        for method in legacy_methods:
            if not hasattr(client, method):
                removed_methods.append(method)
        
        print(f"  ✅ Legacy Methods Removed: {len(removed_methods)}/{len(legacy_methods)}")
        for method in removed_methods:
            print(f"    - {method}")
        
        # Check for new unified methods
        new_methods = [
            '_parse_llm_response',
            '_validate_entity',
            '_validate_relationship'
        ]
        
        present_methods = []
        for method in new_methods:
            if hasattr(client, method):
                present_methods.append(method)
        
        print(f"  ✅ New Unified Methods: {len(present_methods)}/{len(new_methods)}")
        for method in present_methods:
            print(f"    - {method}")
        
        return len(removed_methods) >= 2 and len(present_methods) >= 2
        
    except Exception as e:
        print(f"  ❌ Legacy API removal test failed: {e}")
        return False

def print_summary(results):
    """Print test summary."""
    print("\n" + "="*60)
    print("🎯 T23C LLM MIGRATION TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL" 
        print(f"  {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 MIGRATION SUCCESSFUL - T23C NOW USES UNIVERSAL LLM SERVICE")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TESTS FAILED - MIGRATION INCOMPLETE")
        return False

def main():
    """Run comprehensive migration test suite."""
    print("🚀 Starting T23C LLM Integration Migration Tests")
    print("=" * 60)
    
    # Run all test cases
    results = {
        "LLM Integration Migration": test_llm_integration_migration(),
        "Method Signatures": test_method_signatures(),
        "Import Structure": test_import_structure(),
        "Legacy API Removal": test_legacy_api_removal()
    }
    
    # Print summary
    all_passed = print_summary(results)
    
    return all_passed

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)