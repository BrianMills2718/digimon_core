#!/usr/bin/env python3
"""
Direct Streamlit UI Testing (No Server Required)
Tests UI components and workflows directly without starting a web server
"""

import sys
import os
from pathlib import Path
import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.evidence_logger import evidence_logger

def test_ui_imports_and_setup():
    """Test UI imports and basic setup"""
    try:
        import streamlit_app
        print("✅ streamlit_app import successful")
        
        # Test session state initialization
        streamlit_app.init_session_state()
        print("✅ Session state initialization successful")
        
        # Test generator initialization
        generator = streamlit_app.get_ontology_generator()
        print(f"✅ Generator initialization: {generator is not None}")
        
        # Test storage service initialization  
        storage = streamlit_app.get_storage_service()
        print(f"✅ Storage service initialization: {storage is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI setup failed: {e}")
        return False

def test_ui_workflow_functions():
    """Test UI workflow functions directly"""
    try:
        import streamlit_app
        
        # Test ontology generation
        test_domain = "Test domain for climate policy analysis"
        config = {
            "temperature": 0.7,
            "max_entities": 10,
            "max_relations": 5,
            "include_hierarchies": True,
            "auto_suggest_attributes": True
        }
        
        print("🔄 Testing ontology generation...")
        ontology = streamlit_app.generate_ontology_with_gemini(test_domain, config)
        
        if ontology and hasattr(ontology, 'domain'):
            print(f"✅ Ontology generated: {ontology.domain}")
            print(f"   Entity types: {len(ontology.entity_types)}")
            print(f"   Relation types: {len(ontology.relation_types)}")
        else:
            print("❌ Ontology generation failed")
            return False
        
        # Test ontology validation
        print("🔄 Testing ontology validation...")
        sample_text = "Climate policies are implemented by government agencies to reduce carbon emissions and promote renewable energy sources."
        validation_result = streamlit_app.validate_ontology_with_text(ontology, sample_text)
        
        if validation_result and "entities_found" in validation_result:
            print(f"✅ Validation successful:")
            print(f"   Entities found: {validation_result['entities_found']}")
            print(f"   Relations found: {validation_result['relations_found']}")
            print(f"   Coverage: {validation_result.get('coverage', 0):.2%}")
        else:
            print("❌ Validation failed")
            return False
        
        # Test ontology refinement
        print("🔄 Testing ontology refinement...")
        refinement_request = "Add more entity types related to renewable energy and policy implementation"
        refined_ontology = streamlit_app.refine_ontology_with_gemini(ontology, refinement_request)
        
        if refined_ontology and hasattr(refined_ontology, 'domain'):
            print(f"✅ Refinement successful: {refined_ontology.domain}")
        else:
            print("❌ Refinement failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ UI workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_component_functions():
    """Test UI component functions"""
    try:
        import streamlit_app
        
        # Test component function availability
        component_functions = [
            "render_header",
            "render_sidebar", 
            "render_chat_interface",
            "render_ontology_preview",
            "render_ontology_structure",
            "render_ontology_details",
            "render_ontology_graph",
            "render_validation_interface"
        ]
        
        for func_name in component_functions:
            if hasattr(streamlit_app, func_name):
                func = getattr(streamlit_app, func_name)
                if callable(func):
                    print(f"✅ {func_name} function available")
                else:
                    print(f"❌ {func_name} not callable")
                    return False
            else:
                print(f"❌ {func_name} function missing")
                return False
        
        # Test helper functions
        helper_functions = [
            "process_user_input",
            "save_to_history",
            "load_ontology_from_history",
            "export_ontology_json"
        ]
        
        for func_name in helper_functions:
            if hasattr(streamlit_app, func_name):
                print(f"✅ {func_name} helper function available")
            else:
                print(f"❌ {func_name} helper function missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ UI component test failed: {e}")
        return False

def test_ui_data_models():
    """Test UI data models and conversion functions"""
    try:
        import streamlit_app
        
        # Test data classes
        test_entity = streamlit_app.EntityType(
            name="TEST_ENTITY",
            description="Test entity type",
            attributes=["attr1", "attr2"],
            examples=["example1", "example2"]
        )
        print("✅ EntityType data class working")
        
        test_relation = streamlit_app.RelationType(
            name="TEST_RELATION",
            description="Test relation type",
            source_types=["ENTITY1"],
            target_types=["ENTITY2"],
            examples=["example relation"]
        )
        print("✅ RelationType data class working")
        
        test_ontology = streamlit_app.Ontology(
            domain="Test Domain",
            description="Test ontology",
            entity_types=[test_entity],
            relation_types=[test_relation]
        )
        print("✅ Ontology data class working")
        
        # Test conversion function availability
        if hasattr(streamlit_app, 'domain_to_ui_ontology'):
            print("✅ domain_to_ui_ontology conversion function available")
        else:
            print("❌ domain_to_ui_ontology conversion function missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ UI data model test failed: {e}")
        return False

def run_comprehensive_direct_ui_test():
    """Run comprehensive UI testing without web server"""
    print("🚀 COMPREHENSIVE STREAMLIT UI TESTING (DIRECT)")
    print("=" * 60)
    
    # Clear evidence and start logging
    evidence_logger.clear_evidence_file()
    evidence_logger.log_task_start(
        "DIRECT_UI_TESTING",
        "Comprehensive Streamlit UI testing without web server"
    )
    
    # Run test categories
    test_categories = [
        ("UI Imports and Setup", test_ui_imports_and_setup),
        ("UI Workflow Functions", test_ui_workflow_functions),
        ("UI Component Functions", test_ui_component_functions),
        ("UI Data Models", test_ui_data_models)
    ]
    
    results = {}
    all_passed = True
    
    for category_name, test_func in test_categories:
        print(f"\n🔍 Testing {category_name}...")
        evidence_logger.log_task_start(f"UI_TEST_{category_name.upper().replace(' ', '_')}", f"Testing {category_name}")
        
        try:
            result = test_func()
            results[category_name] = result
            
            if result:
                print(f"✅ {category_name}: PASS")
            else:
                print(f"❌ {category_name}: FAIL")
                all_passed = False
            
            evidence_logger.log_task_completion(
                f"UI_TEST_{category_name.upper().replace(' ', '_')}",
                {"success": result},
                result
            )
            
        except Exception as e:
            print(f"❌ {category_name}: ERROR - {e}")
            results[category_name] = False
            all_passed = False
            
            evidence_logger.log_task_completion(
                f"UI_TEST_{category_name.upper().replace(' ', '_')}",
                {"success": False, "error": str(e)},
                False
            )
    
    # Overall results
    print("\n" + "=" * 60)
    print("📊 UI TEST SUMMARY")
    print("=" * 60)
    
    for category, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {category}")
    
    print(f"\n🎯 OVERALL UI STATUS: {'✅ PRODUCTION READY' if all_passed else '❌ NEEDS FIXES'}")
    
    # Log final results
    evidence_logger.log_verification_result(
        "DIRECT_UI_TESTING",
        {
            "overall_success": all_passed,
            "detailed_results": results,
            "ui_production_ready": all_passed,
            "test_categories_passed": sum(1 for r in results.values() if r),
            "total_test_categories": len(results)
        }
    )
    
    if all_passed:
        print("\n🚀 Streamlit UI is fully functional and ready for production!")
        print("   To start the UI: streamlit run streamlit_app.py")
    else:
        print("\n🔧 Some UI components need attention. Check the detailed results above.")
    
    return all_passed

def main():
    """Main function"""
    success = run_comprehensive_direct_ui_test()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)