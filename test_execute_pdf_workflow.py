#!/usr/bin/env python3

"""
Direct test of execute_pdf_to_answer_workflow with real PDF
"""

import json
import sys
import os

# Add the project root to path
sys.path.insert(0, '/home/brian/Digimons')

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
            workflow_name="real_pdf_test"
        )
        
        print("=" * 50)
        print("📊 WORKFLOW RESULT:")
        print(f"Type: {type(result)}")
        
        if isinstance(result, dict):
            print("JSON Result:")
            print(json.dumps(result, indent=2))
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