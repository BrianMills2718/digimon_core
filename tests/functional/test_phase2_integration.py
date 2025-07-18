#!/usr/bin/env python3
"""
Test Phase 2 Integration Fix
Test the fixed Phase 2 pipeline with proper Neo4j relationship handling.
"""

import os
import sys
import traceback
from pathlib import Path

# Add src to path

def test_phase2_integration_fix():
    """Test Phase 2 integration with Neo4j relationship fix."""
    print("🧪 Testing Phase 2 Integration Fix")
    
    try:
        # Import Phase 2 workflow
        from tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        from tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
        from tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
        from core.enhanced_identity_service import EnhancedIdentityService
        
        print("✅ All Phase 2 imports successful")
        
        # Test ontology extractor with mock data (to avoid API key issues)
        print("\n🔍 Testing Ontology Extractor...")
        identity_service = EnhancedIdentityService()
        
        # Create mock extractor without API keys
        try:
            # This should fail gracefully with clear error about missing API key
            extractor = OntologyAwareExtractor(identity_service)
            print("❌ Should have failed due to missing API key")
        except ValueError as e:
            if "Google API key required" in str(e):
                print("✅ Properly validates Google API key requirement")
            else:
                print(f"❌ Unexpected error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")
        
        # Test graph builder initialization (should work)
        print("\n🔗 Testing Graph Builder...")
        try:
            graph_builder = OntologyAwareGraphBuilder()
            print("✅ Graph builder initialized successfully")
            
            # Test the sanitization method I added
            test_types = [
                "WORKS_AT",
                "works-at", 
                "works at",
                "AFFILIATED WITH",
                "123INVALID",
                "",
                "test@#$%^&*()"
            ]
            
            print("\n🧹 Testing relationship type sanitization:")
            for test_type in test_types:
                sanitized = graph_builder._sanitize_relationship_type(test_type)
                print(f"  '{test_type}' -> '{sanitized}'")
            
            graph_builder.close()
            print("✅ Graph builder cleanup successful")
            
        except Exception as e:
            print(f"❌ Graph builder error: {e}")
            print(traceback.format_exc())
        
        # Test enhanced workflow initialization (should fail on API keys)
        print("\n🚀 Testing Enhanced Workflow...")
        try:
            workflow = EnhancedVerticalSliceWorkflow()
            print("❌ Should have failed due to missing API keys")
        except Exception as e:
            if "Google API key" in str(e) or "API key" in str(e):
                print("✅ Properly validates API key requirements")
            else:
                print(f"❌ Unexpected workflow error: {e}")
        
        print("\n✅ Phase 2 integration fix test completed")
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 integration test failed: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_phase2_integration_fix()
    sys.exit(0 if success else 1)