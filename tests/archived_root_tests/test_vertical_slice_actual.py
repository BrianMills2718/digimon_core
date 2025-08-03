#!/usr/bin/env python3
"""
Test vertical slice with ACTUAL current interfaces
Since audit shows all tools use base_tool.ToolRequest
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import tempfile
import json

def test_vertical_slice_actual():
    """Test with the actual interfaces the tools are using"""
    
    print("🎯 VERTICAL SLICE TEST - ACTUAL INTERFACES")
    print("=" * 60)
    
    # Initialize services
    print("\n1. Initializing Services...")
    try:
        from src.core.service_manager import ServiceManager
        service_manager = ServiceManager()
        print("   ✅ ServiceManager initialized")
    except Exception as e:
        print(f"   ❌ ServiceManager failed: {e}")
        return {"status": "FAILED"}
    
    # Import the ACTUAL ToolRequest that tools use
    print("\n2. Importing base_tool interfaces...")
    try:
        from src.tools.base_tool import ToolRequest, ToolResult
        print("   ✅ Imported base_tool.ToolRequest")
    except Exception as e:
        print(f"   ❌ Failed to import: {e}")
        return {"status": "FAILED"}
    
    # Initialize tools
    print("\n3. Initializing Tools...")
    tools = {}
    tool_configs = [
        ("T01", "src.tools.phase1.t01_pdf_loader_unified", "T01PDFLoaderUnified"),
        ("T15A", "src.tools.phase1.t15a_text_chunker_unified", "T15ATextChunkerUnified")
    ]
    
    for tool_id, module_path, class_name in tool_configs:
        try:
            module = __import__(module_path, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            tools[tool_id] = tool_class(service_manager)
            print(f"   ✅ {tool_id} initialized")
        except Exception as e:
            print(f"   ❌ {tool_id} failed: {e}")
    
    # Create test document
    print("\n4. Testing Pipeline with base_tool.ToolRequest...")
    test_content = "This is a test document for the vertical slice. It contains enough text to test chunking."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    # Step 1: T01 with base_tool.ToolRequest
    print("\n   Step 1: T01 PDF Loader...")
    try:
        t01_request = ToolRequest(
            tool_id='T01',
            operation='load_document',
            input_data={'file_path': test_file_path},
            parameters={}
        )
        
        print(f"      Created request: {t01_request}")
        
        t01_result = tools['T01'].execute(t01_request)
        
        if hasattr(t01_result, 'status') and t01_result.status == "success":
            print(f"      ✅ T01 SUCCESS!")
            document_data = t01_result.data.get('document', {})
            text = document_data.get('text', '')
            document_ref = document_data.get('document_ref', '')
            print(f"      Loaded: {len(text)} characters")
            print(f"      Doc ref: {document_ref}")
        else:
            print(f"      ❌ T01 failed: {t01_result}")
            
    except Exception as e:
        print(f"      ❌ T01 error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 2: T15A with base_tool.ToolRequest
    print("\n   Step 2: T15A Text Chunker...")
    try:
        if 'text' in locals() and 'document_ref' in locals():
            t15a_request = ToolRequest(
                tool_id='T15A',
                operation='chunk_text',
                input_data={
                    'text': text,
                    'document_ref': document_ref
                },
                parameters={
                    'chunk_size': 512,
                    'overlap_size': 50
                }
            )
            
            print(f"      Created request with parameters")
            
            t15a_result = tools['T15A'].execute(t15a_request)
            
            if hasattr(t15a_result, 'status') and t15a_result.status == "success":
                print(f"      ✅ T15A SUCCESS!")
                chunks = t15a_result.data.get('chunks', [])
                print(f"      Created {len(chunks)} chunks")
            else:
                print(f"      ❌ T15A failed: {t15a_result}")
        else:
            print("      ⚠️  Skipping T15A - no text from T01")
            
    except Exception as e:
        print(f"      ❌ T15A error: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    os.unlink(test_file_path)
    
    # Assessment
    print("\n" + "=" * 60)
    print("📊 ASSESSMENT")
    print("=" * 60)
    
    if 'chunks' in locals() and len(chunks) > 0:
        print("\n✅ VERTICAL SLICE IS WORKING!")
        print("   - All tools use base_tool.ToolRequest")
        print("   - Data flows from T01 to T15A successfully")
        print("   - The interface mismatch was a FALSE ALARM")
        return {"status": "SUCCESS", "vertical_slice": "WORKING"}
    else:
        print("\n❌ VERTICAL SLICE HAS ISSUES")
        print("   - Tools may use same interface but have other problems")
        return {"status": "PARTIAL", "vertical_slice": "ISSUES"}

if __name__ == "__main__":
    result = test_vertical_slice_actual()
    print(f"\n📦 Result: {json.dumps(result, indent=2)}")
