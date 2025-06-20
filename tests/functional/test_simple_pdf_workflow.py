#!/usr/bin/env python3

"""
Test workflow with a simpler PDF to isolate Gemini safety filter issues
"""

import json
import sys
import os

# Add the project root to path
sys.path.insert(0, '/home/brian/Digimons')

def test_simple_pdf_workflow():
    """Execute the PDF workflow with a simpler PDF file"""
    
    print("=== TESTING WITH SIMPLE PDF ===")
    
    try:
        # Import the workflow class
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        print("✅ Successfully imported EnhancedVerticalSliceWorkflow")
        
        # Create workflow instance
        workflow = EnhancedVerticalSliceWorkflow()
        print("✅ Created workflow instance")
        
        # Use simple PDF instead of wiki1.pdf
        pdf_path = "/home/brian/Digimons/examples/pdfs/test_document.pdf"
        domain_description = "Simple document analysis for testing"
        queries = ["What is this document about?"]
        
        print(f"📁 PDF Path: {pdf_path}")
        print(f"🔍 Domain: {domain_description}")
        print(f"❓ Queries: {queries}")
        
        # Verify PDF exists
        if not os.path.exists(pdf_path):
            print(f"❌ ERROR: PDF file not found at {pdf_path}")
            return False
            
        print(f"✅ PDF file exists: {os.path.getsize(pdf_path)} bytes")
        
        # Execute the workflow
        print("\n🚀 EXECUTING ENHANCED WORKFLOW WITH SIMPLE PDF...")
        print("=" * 50)
        
        result = workflow.execute_enhanced_workflow(
            pdf_path=pdf_path,
            domain_description=domain_description,
            queries=queries,
            workflow_name="simple_pdf_test"
        )
        
        print("=" * 50)
        print("📊 WORKFLOW RESULT:")
        print(f"Status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY WITH SIMPLE PDF!")
            print(f"Execution time: {result.get('execution_time', 0):.2f}s")
            
            # Print summary of results
            steps = result.get('steps', {})
            for step_name, step_result in steps.items():
                status = step_result.get('status', 'unknown')
                print(f"  - {step_name}: {status}")
                
            return True
        else:
            print(f"❌ WORKFLOW FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_pdf_workflow()
    sys.exit(0 if success else 1)