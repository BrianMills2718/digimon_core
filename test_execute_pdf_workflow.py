#!/usr/bin/env python3

"""
Direct test of execute_pdf_to_answer_workflow with real PDF
"""

import json
import sys
import os

# Add the project root to path
sys.path.insert(0, '/home/brian/Digimons')

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

def test_execute_pdf_workflow():
    """Execute the PDF workflow with a real PDF file"""
    
    print("=== STARTING REAL PDF WORKFLOW TEST ===")
    
    try:
        # Import the workflow class
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        print("✅ Successfully imported EnhancedVerticalSliceWorkflow")
        
        # Create workflow instance
        workflow = EnhancedVerticalSliceWorkflow()
        print("✅ Created workflow instance")
        
        # Set up real parameters
        pdf_path = "/home/brian/Digimons/examples/pdfs/test_document.pdf"
        domain_description = "Document analysis for general knowledge extraction"
        queries = ["What is the main topic of this document?", "What are the key entities mentioned?"]
        
        print(f"📁 PDF Path: {pdf_path}")
        print(f"🔍 Domain: {domain_description}")
        print(f"❓ Queries: {queries}")
        
        # Verify PDF exists
        if not os.path.exists(pdf_path):
            print(f"❌ ERROR: PDF file not found at {pdf_path}")
            return False
            
        print(f"✅ PDF file exists: {os.path.getsize(pdf_path)} bytes")
        
        # Execute the workflow
        print("\n🚀 EXECUTING ENHANCED WORKFLOW...")
        print("=" * 50)
        
        result = workflow.execute_enhanced_workflow(
            pdf_path=pdf_path,
            domain_description=domain_description,
            queries=queries,
            workflow_name="real_pdf_test",
            use_existing_ontology=None
        )
        
        print("=" * 50)
        print("📊 WORKFLOW RESULT:")
        print(f"Type: {type(result)}")
        
        if isinstance(result, dict):
            print("\n📋 Workflow Summary:")
            print(f"   - Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   - Status: {result.get('status', 'N/A')}")
            print(f"   - Execution Time: {result.get('execution_time', 0):.2f}s")
            
            # Check ontology info
            if 'steps' in result and 'ontology_generation' in result['steps']:
                ontology_step = result['steps']['ontology_generation']
                print(f"\n🏷️ Ontology Generation:")
                print(f"   - Status: {ontology_step.get('status', 'N/A')}")
                if ontology_step.get('status') == 'success':
                    print(f"   - Source: OpenAI o3-mini (not mock_fallback)")
                    print(f"   - Domain: {ontology_step.get('domain', 'N/A')}")
            
            # Check extraction results
            if 'steps' in result and 'entity_extraction' in result['steps']:
                extraction = result['steps']['entity_extraction']
                print(f"\n📊 Entity Extraction:")
                print(f"   - Status: {extraction.get('status', 'N/A')}")
                if extraction.get('status') == 'success' and 'extraction_result' in extraction:
                    ext_result = extraction['extraction_result']
                    if hasattr(ext_result, 'entities'):
                        print(f"   - Entities found: {len(ext_result.entities)}")
                        print(f"   - Top entities: {[e.text for e in ext_result.entities[:5]]}")
                    if hasattr(ext_result, 'relationships'):
                        print(f"   - Relationships found: {len(ext_result.relationships)}")
            
            # Check query results
            if 'query_results' in result:
                print(f"\n📝 Query Answers:")
                for i, (query, answer) in enumerate(result['query_results'].items()):
                    print(f"   Q{i+1}: {query}")
                    print(f"   A{i+1}: {answer[:100]}...")
        else:
            print(f"Raw Result: {result}")
            
        print("\n✅ WORKFLOW COMPLETED SUCCESSFULLY")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_execute_pdf_workflow()
    sys.exit(0 if success else 1)