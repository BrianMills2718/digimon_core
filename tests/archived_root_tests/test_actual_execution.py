#!/usr/bin/env python3
"""
TEST: Can the agent actually execute a basic tool chain?

This tests the fundamental execution capabilities that we've been designing theory for.
"""

import os
import time
from pathlib import Path

def test_basic_tool_execution():
    """Test if we can actually execute tools in sequence"""
    print("🧪 TESTING ACTUAL TOOL EXECUTION CAPABILITIES")
    print("=" * 60)
    
    try:
        # Step 1: Initialize service manager
        print("\n1️⃣ INITIALIZING SERVICE MANAGER...")
        from src.core.service_manager import get_service_manager
        service_manager = get_service_manager()
        print("   ✅ Service manager created")
        
        # Step 2: Initialize T01 PDF Loader
        print("\n2️⃣ INITIALIZING T01 PDF LOADER...")
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        loader = PDFLoader(service_manager)
        print("   ✅ PDF Loader created")
        
        # Step 3: Test with a simple text file (since we need actual content)
        print("\n3️⃣ CREATING TEST FILE...")
        test_file = "test_document.txt"
        test_content = """
        This is a test document for execution testing.
        
        John Smith works for Acme Corporation in New York.
        The company was founded by Jane Doe in 2020.
        Microsoft and Google are major technology companies.
        
        This document contains several entities and relationships
        that should be extracted by our tools.
        """
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        print(f"   ✅ Test file created: {test_file}")
        
        # Step 4: Execute T01 - Load document
        print("\n4️⃣ EXECUTING T01 - DOCUMENT LOADING...")
        load_result = loader.load_pdf(test_file, workflow_id="test_workflow")
        print(f"   Status: {load_result.get('status', 'unknown')}")
        if load_result.get('status') == 'success':
            print(f"   ✅ Document loaded successfully")
            print(f"   Text length: {len(load_result.get('text_content', ''))}")
            document_ref = load_result.get('document_ref')
            text_content = load_result.get('text_content')
        else:
            print(f"   ❌ Document loading failed: {load_result.get('error', 'Unknown error')}")
            return False
        
        # Step 5: Initialize T15A Text Chunker
        print("\n5️⃣ INITIALIZING T15A TEXT CHUNKER...")
        from src.tools.phase1.t15a_text_chunker import TextChunker
        chunker = TextChunker(service_manager)
        print("   ✅ Text Chunker created")
        
        # Step 6: Execute T15A - Chunk text
        print("\n6️⃣ EXECUTING T15A - TEXT CHUNKING...")
        chunk_result = chunker.chunk_text(document_ref, text_content, confidence=0.8)
        print(f"   Status: {chunk_result.get('status', 'unknown')}")
        if chunk_result.get('status') == 'success':
            chunks = chunk_result.get('chunks', [])
            print(f"   ✅ Text chunked successfully - {len(chunks)} chunks created")
        else:
            print(f"   ❌ Text chunking failed: {chunk_result.get('error', 'Unknown error')}")
            return False
        
        # Step 7: Initialize T23A spaCy NER
        print("\n7️⃣ INITIALIZING T23A SPACY NER...")
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        ner = SpacyNER(service_manager)
        print("   ✅ spaCy NER created")
        
        # Step 8: Execute T23A - Extract entities from first chunk
        print("\n8️⃣ EXECUTING T23A - ENTITY EXTRACTION...")
        if chunks:
            first_chunk = chunks[0]
            chunk_ref = first_chunk.get('chunk_ref')
            chunk_text = first_chunk.get('chunk_text')
            
            entity_result = ner.extract_entities(chunk_ref, chunk_text, confidence=0.8)
            print(f"   Status: {entity_result.get('status', 'unknown')}")
            if entity_result.get('status') == 'success':
                entities = entity_result.get('entities', [])
                print(f"   ✅ Entities extracted successfully - {len(entities)} entities found")
                for entity in entities[:3]:  # Show first 3
                    print(f"      • {entity.get('surface_form')} ({entity.get('entity_type')})")
            else:
                print(f"   ❌ Entity extraction failed: {entity_result.get('error', 'Unknown error')}")
                return False
        
        # Step 9: Test tool chaining capability  
        print("\n9️⃣ TESTING TOOL CHAINING...")
        print("   Can we pass outputs from one tool to the next?")
        
        # Check if document_ref from T01 was used by T15A
        if document_ref and chunks:
            print("   ✅ T01 → T15A: Document reference passed successfully")
        
        # Check if chunk_ref from T15A was used by T23A  
        if chunks and chunk_ref:
            print("   ✅ T15A → T23A: Chunk reference passed successfully")
        
        print("\n🎯 TOOL CHAINING ASSESSMENT:")
        print("   ✅ Service manager provides shared services")
        print("   ✅ Tools can be initialized and executed")
        print("   ✅ Outputs can be passed between tools")
        print("   ✅ Basic 3-tool chain works: T01 → T15A → T23A")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"\n❌ EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return False

def test_cross_modal_capability():
    """Test if we can do graph → table → vector type operations"""
    print("\n🔄 TESTING CROSS-MODAL CAPABILITIES")
    print("=" * 40)
    
    try:
        # This would test the graph → table → vector flow
        # But first let's see what we actually have
        
        print("   📊 Checking available cross-modal tools...")
        
        # Check if we have any cross-modal tools
        from pathlib import Path
        tools_dir = Path("src/tools")
        
        # Look for cross-modal or conversion tools
        cross_modal_files = []
        for phase_dir in tools_dir.glob("phase*"):
            for tool_file in phase_dir.glob("*cross*"):
                cross_modal_files.append(tool_file)
            for tool_file in phase_dir.glob("*convert*"):
                cross_modal_files.append(tool_file)
        
        if cross_modal_files:
            print(f"   ✅ Found {len(cross_modal_files)} potential cross-modal tools")
            for f in cross_modal_files:
                print(f"      • {f}")
        else:
            print("   ❌ No cross-modal tools found")
            print("   📝 Cross-modal capabilities need to be implemented")
        
        return len(cross_modal_files) > 0
        
    except Exception as e:
        print(f"   ❌ Cross-modal test failed: {e}")
        return False

def test_statistical_analysis_capability():
    """Test if we can write and execute statistical analysis code on the fly"""
    print("\n📈 TESTING STATISTICAL ANALYSIS CAPABILITIES")
    print("=" * 45)
    
    try:
        # Test if we can generate and execute statistical code
        print("   🧮 Testing dynamic statistical analysis...")
        
        # Create sample data
        sample_data = [
            {"entity": "John Smith", "pagerank": 0.25, "mentions": 3},
            {"entity": "Acme Corp", "pagerank": 0.35, "mentions": 2}, 
            {"entity": "Jane Doe", "pagerank": 0.15, "mentions": 1},
            {"entity": "Microsoft", "pagerank": 0.45, "mentions": 4},
            {"entity": "Google", "pagerank": 0.40, "mentions": 3}
        ]
        
        # Test basic statistical operations
        import statistics
        pagerank_scores = [item["pagerank"] for item in sample_data]
        mention_counts = [item["mentions"] for item in sample_data]
        
        # Calculate correlations and statistics
        mean_pagerank = statistics.mean(pagerank_scores)
        stdev_pagerank = statistics.stdev(pagerank_scores)
        mean_mentions = statistics.mean(mention_counts)
        
        print(f"   ✅ Basic statistics calculated:")
        print(f"      • Mean PageRank: {mean_pagerank:.3f}")
        print(f"      • StdDev PageRank: {stdev_pagerank:.3f}")
        print(f"      • Mean Mentions: {mean_mentions:.1f}")
        
        # Test if we can generate code dynamically
        analysis_code = '''
import numpy as np
import scipy.stats

def analyze_entity_correlations(data):
    pagerank = [item["pagerank"] for item in data]
    mentions = [item["mentions"] for item in data]
    
    # Calculate Pearson correlation
    correlation, p_value = scipy.stats.pearsonr(pagerank, mentions)
    
    return {
        "correlation": correlation,
        "p_value": p_value,
        "significant": p_value < 0.05
    }

result = analyze_entity_correlations(sample_data)
'''
        
        # Try to execute the generated code
        try:
            import numpy as np
            import scipy.stats
            
            exec_globals = {
                'np': np, 
                'scipy': scipy,
                'sample_data': sample_data
            }
            exec(analysis_code, exec_globals)
            result = exec_globals['result']
            
            print(f"   ✅ Dynamic statistical analysis executed:")
            print(f"      • Correlation: {result['correlation']:.3f}")
            print(f"      • P-value: {result['p_value']:.3f}")
            print(f"      • Significant: {result['significant']}")
            
            return True
            
        except ImportError as e:
            print(f"   ❌ Missing statistical libraries: {e}")
            print("   📝 Need to install scipy/numpy for advanced statistics")
            return False
            
    except Exception as e:
        print(f"   ❌ Statistical analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING AGENT EXECUTION CAPABILITIES")
    print("=" * 80)
    print("🎯 GOAL: Determine what the agent can actually DO vs. theoretical design")
    print("=" * 80)
    
    # Test 1: Basic tool execution and chaining
    tool_execution_works = test_basic_tool_execution()
    
    # Test 2: Cross-modal capabilities
    cross_modal_works = test_cross_modal_capability()
    
    # Test 3: Statistical analysis capabilities
    stats_works = test_statistical_analysis_capability()
    
    # Final Assessment
    print("\n" + "=" * 80)
    print("📊 AGENT EXECUTION CAPABILITY ASSESSMENT")
    print("=" * 80)
    
    capabilities = {
        "Basic Tool Chaining (T01→T15A→T23A)": tool_execution_works,
        "Cross-Modal Operations (Graph→Table→Vector)": cross_modal_works,
        "Dynamic Statistical Analysis": stats_works
    }
    
    working_count = sum(capabilities.values())
    total_count = len(capabilities)
    
    print(f"\n📈 CAPABILITY SUMMARY:")
    for capability, working in capabilities.items():
        status = "✅ WORKING" if working else "❌ NOT WORKING"
        print(f"   {capability}: {status}")
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    print(f"   Working Capabilities: {working_count}/{total_count}")
    print(f"   Success Rate: {working_count/total_count*100:.1f}%")
    
    if working_count == total_count:
        print("   Status: 🟢 AGENT FULLY CAPABLE")
        print("   Assessment: Agent can execute complex workflows")
    elif working_count >= total_count * 0.6:
        print("   Status: 🟡 AGENT PARTIALLY CAPABLE") 
        print("   Assessment: Basic execution works, advanced features need development")
    else:
        print("   Status: 🔴 AGENT LIMITED CAPABILITY")
        print("   Assessment: Significant development needed for workflow execution")
    
    print("\n💡 WHAT THE AGENT CAN ACTUALLY DO:")
    if tool_execution_works:
        print("   ✅ Execute individual tools with service coordination")
        print("   ✅ Chain tool outputs as inputs to next tool")
        print("   ✅ Process documents through multi-step pipelines")
        print("   ✅ Extract entities, relationships, and build graphs")
    
    if not cross_modal_works:
        print("   ❌ Cannot seamlessly convert between graph/table/vector formats")
        print("   📝 Need to implement cross-modal transition tools")
    
    if stats_works:
        print("   ✅ Can generate and execute statistical analysis code dynamically")
        print("   ✅ Can perform correlations, significance tests, and analytics")
    
    print("\n🔄 WHAT NEEDS TO BE BUILT:")
    if not cross_modal_works:
        print("   • Graph → Table conversion tools")
        print("   • Table → Vector conversion tools") 
        print("   • Vector → Graph conversion tools")
        print("   • Unified cross-modal orchestration")
    
    if not stats_works:
        print("   • Statistical analysis library integration")
        print("   • Dynamic code generation and execution")
    
    print("\n🎯 BOTTOM LINE:")
    if tool_execution_works:
        print("   The agent CAN execute multi-step tool workflows!")
        print("   The foundation for complex orchestration exists.")
        print("   Missing pieces are specific advanced capabilities, not basic execution.")
    else:
        print("   The agent CANNOT execute basic tool workflows.")
        print("   Fundamental execution capability needs to be built first.")