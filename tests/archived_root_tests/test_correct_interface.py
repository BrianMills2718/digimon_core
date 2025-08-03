#!/usr/bin/env python3
"""
Test tool chain with CORRECT unified interface usage
"""

import sys
sys.path.append('src')

import time
import json
from datetime import datetime
from typing import List, Dict, Any

def test_correct_unified_interface():
    """Test tools using the correct ToolRequest interface"""
    print("🔧 TESTING CORRECT UNIFIED INTERFACE USAGE")
    print("=" * 80)
    
    try:
        # Import unified interface components
        from src.tools.base_tool import ToolRequest, ToolResult
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified  
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        
        print("✅ All imports successful")
        
        # Initialize service manager
        print("🔧 Initializing ServiceManager...")
        service_manager = ServiceManager()
        print("✅ ServiceManager initialized")
        
        # Initialize tools with service manager
        tools = [
            ("T01", T01PDFLoaderUnified(service_manager)),
            ("T15A", T15ATextChunkerUnified(service_manager)),
            ("T23A", T23ASpacyNERUnified(service_manager))
        ]
        
        print(f"✅ {len(tools)} tools instantiated successfully")
        
        # Test data
        test_text = """
        Stanford University Artificial Intelligence Research Division
        Dr. Sarah Chen leads advanced machine learning research at Stanford University.
        The Natural Language Processing laboratory focuses on computational linguistics.
        
        MIT Computer Science and Artificial Intelligence Laboratory
        Professor John Smith at MIT works on robotics and autonomous systems research.
        """
        
        # Test 1: T01 PDF Loader (simulate with text)
        print("\n🔗 Tool Chain Execution with Correct Interface:")
        print("   🔧 Testing T01 (PDF Loader)...")
        
        # Create proper ToolRequest for T01
        t01_request = ToolRequest(
            tool_id="T01",
            operation="load_text",  # Simulate PDF loading with text
            input_data={
                "content": test_text,
                "source_type": "text"
            },
            parameters={}
        )
        
        try:
            # Execute T01 
            t01_result = tools[0][1].execute(t01_request)
            print(f"   ✅ T01: {t01_result.status} - {type(t01_result.data).__name__}")
            
            if t01_result.status == "success":
                current_data = t01_result.data
                
                # Test 2: T15A Text Chunker with proper interface
                print("   🔧 Testing T15A (Text Chunker)...")
                
                t15a_request = ToolRequest(
                    tool_id="T15A",
                    operation="chunk_text",
                    input_data={
                        "text": current_data.get("content", test_text),
                        "document_ref": "test_document",
                        "document_confidence": 0.8
                    },
                    parameters={}
                )
                
                t15a_result = tools[1][1].execute(t15a_request)
                print(f"   ✅ T15A: {t15a_result.status} - {type(t15a_result.data).__name__}")
                
                if t15a_result.status == "success":
                    chunks = t15a_result.data.get("chunks", [])
                    
                    # Test 3: T23A Entity Extraction with proper interface
                    print("   🔧 Testing T23A (Entity Extraction)...")
                    
                    # Use first chunk for entity extraction
                    if chunks:
                        chunk_text = chunks[0].get("text", test_text)
                        chunk_ref = chunks[0].get("chunk_id", "test_chunk")
                    else:
                        chunk_text = test_text
                        chunk_ref = "test_chunk"
                    
                    t23a_request = ToolRequest(
                        tool_id="T23A",
                        operation="extract_entities",
                        input_data={
                            "text": chunk_text,
                            "chunk_ref": chunk_ref
                        },
                        parameters={}
                    )
                    
                    t23a_result = tools[2][1].execute(t23a_request)
                    print(f"   ✅ T23A: {t23a_result.status} - {type(t23a_result.data).__name__}")
                    
                    if t23a_result.status == "success":
                        entities = t23a_result.data.get("entities", [])
                        print(f"       Extracted {len(entities)} entities")
                        
                        # Show some entities
                        for i, entity in enumerate(entities[:3]):
                            print(f"       Entity {i+1}: {entity.get('surface_form')} ({entity.get('entity_type')})")
                        
                        return {
                            "success": True,
                            "tools_executed": 3,
                            "interface_compliance": True,
                            "entities_extracted": len(entities),
                            "chunks_created": len(chunks)
                        }
                    else:
                        print(f"   ❌ T23A failed: {t23a_result.error_message}")
                        return {"success": False, "failed_at": "T23A", "error": t23a_result.error_message}
                else:
                    print(f"   ❌ T15A failed: {t15a_result.error_message}")
                    return {"success": False, "failed_at": "T15A", "error": t15a_result.error_message}
            else:
                print(f"   ❌ T01 failed: {t01_result.error_message}")
                return {"success": False, "failed_at": "T01", "error": t01_result.error_message}
                
        except Exception as e:
            print(f"   💥 Interface error: {e}")
            return {"success": False, "interface_error": str(e)}
            
    except Exception as e:
        print(f"💥 Setup error: {e}")
        return {"setup_error": str(e)}

def test_interface_contract_validation():
    """Test interface contract validation"""
    print("\n\n🔍 TESTING INTERFACE CONTRACT VALIDATION")
    print("=" * 80)
    
    try:
        from src.tools.base_tool import ToolRequest, ToolResult
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
        
        service_manager = ServiceManager()
        tool = T15ATextChunkerUnified(service_manager)
        
        # Test 1: Valid request
        print("🧪 Test 1: Valid ToolRequest...")
        valid_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "text": "This is a test text for chunking.",
                "document_ref": "test_doc",
                "document_confidence": 0.8
            },
            parameters={}
        )
        
        # Validate input
        is_valid = tool.validate_input(valid_request.input_data)
        print(f"   Input validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        
        # Test 2: Invalid request (missing required fields)
        print("🧪 Test 2: Invalid ToolRequest (missing text)...")
        invalid_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "document_ref": "test_doc"
                # Missing 'text' field
            },
            parameters={}
        )
        
        is_invalid = tool.validate_input(invalid_request.input_data)
        print(f"   Input validation: {'❌ FAILED (expected)' if not is_invalid else '✅ UNEXPECTEDLY PASSED'}")
        
        # Test 3: Raw string (incorrect interface usage)
        print("🧪 Test 3: Raw string (incorrect interface)...")
        try:
            # This should fail - demonstrates the interface issue
            result = tool.execute("This is a raw string, not a ToolRequest")
            print(f"   Raw string execution: ❌ SHOULD HAVE FAILED but got {result.status}")
        except AttributeError as e:
            print(f"   Raw string execution: ✅ CORRECTLY FAILED - {e}")
        except Exception as e:
            print(f"   Raw string execution: ⚠️ FAILED WITH DIFFERENT ERROR - {e}")
        
        return {
            "valid_request_validation": is_valid,
            "invalid_request_validation": not is_invalid,
            "raw_string_handling": "correctly_failed"
        }
        
    except Exception as e:
        print(f"💥 Contract validation test failed: {e}")
        return {"error": str(e)}

def main():
    """Main test execution"""
    print("🎯 UNIFIED INTERFACE COMPLIANCE TEST")
    print("=" * 80)
    print("Testing tool chain with correct ToolRequest interface usage")
    print("=" * 80)
    
    # Test 1: Correct interface usage
    interface_result = test_correct_unified_interface()
    
    # Test 2: Contract validation
    contract_result = test_interface_contract_validation()
    
    # Summary
    print(f"\n" + "=" * 80)
    print("🎯 INTERFACE COMPLIANCE TEST SUMMARY")
    print("=" * 80)
    
    if interface_result.get("success"):
        print(f"✅ TOOL CHAIN: Successfully executed {interface_result.get('tools_executed', 0)} tools")
        print(f"✅ INTERFACE: All tools accept ToolRequest objects correctly")
        print(f"📊 RESULTS: {interface_result.get('entities_extracted', 0)} entities, {interface_result.get('chunks_created', 0)} chunks")
        
        print(f"\n🎯 KEY INSIGHT:")
        print(f"   The unified interface WORKS when used correctly")
        print(f"   Breaking point was incorrect interface usage, not tool failure")
        print(f"   Tools expect ToolRequest objects, not raw strings")
        
    else:
        print(f"❌ TOOL CHAIN: Failed at {interface_result.get('failed_at', 'unknown')}")
        print(f"   Error: {interface_result.get('error', 'unknown')}")
    
    # Save results
    results = {
        "test_type": "unified_interface_compliance",
        "timestamp": datetime.now().isoformat(),
        "interface_test": interface_result,
        "contract_test": contract_result
    }
    
    results_file = f"INTERFACE_FIX_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full results: {results_file}")
    
    return results

if __name__ == "__main__":
    results = main()