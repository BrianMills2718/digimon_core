#!/usr/bin/env python3

"""
Test workflow with a simpler PDF to isolate Gemini safety filter issues
"""

import json
import sys
import os

# Add the project root to path

def test_simple_pdf_workflow():
    """Execute the PDF workflow with a simpler PDF file"""
    
    print("=== TESTING WITH SIMPLE PDF ===")
    
    try:
        # Import the workflow class
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        print("✅ Successfully imported PipelineOrchestrator")
        
        # Create workflow instance
        config_manager = ConfigManager()
        config = create_unified_workflow_config(phase=Phase.PHASE2, optimization_level=OptimizationLevel.ENHANCED)
        workflow = PipelineOrchestrator(config, config_manager)
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
        
        result = workflow.execute([pdf_path], queries)
        
        print("=" * 50)
        print("📊 WORKFLOW RESULT:")
        final_result = result.get('final_result', {})
        
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY WITH SIMPLE PDF!")
        
        # Print summary of results
        entities = final_result.get('entities', [])
        relationships = final_result.get('relationships', [])
        query_results = final_result.get('query_results', [])
        
        print(f"  - Entities extracted: {len(entities)}")
        print(f"  - Relationships found: {len(relationships)}")
        print(f"  - Query results: {len(query_results)}")
        
        return True
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_pdf_workflow()
    sys.exit(0 if success else 1)