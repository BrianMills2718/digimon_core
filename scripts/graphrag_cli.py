#!/usr/bin/env python3
"""
GraphRAG Command Line Interface - Simple, reliable way to test the system
"""

import argparse
import sys
from pathlib import Path
import json

def run_phase1(file_path, query="What are the main entities and relationships?"):
    """Run Phase 1 processing"""
    print(f"🚀 Running Phase 1 on: {file_path}")
    print(f"📝 Query: {query}")
    
    try:
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        
        workflow = VerticalSliceWorkflow()
        result = workflow.execute_workflow(file_path, query, f"cli_{Path(file_path).stem}")
        
        status = result.get("status", "unknown")
        steps = result.get("steps", {})
        error = result.get("error")
        
        print(f"\n✅ Status: {status}")
        print(f"✅ Steps completed: {len(steps)}")
        
        if error:
            print(f"❌ Error: {error}")
            return False
        
        # Show results
        entity_step = steps.get("entity_extraction", {})
        rel_step = steps.get("relationship_extraction", {})
        query_step = steps.get("query_execution", {})
        
        entities = entity_step.get("total_entities", 0)
        relationships = rel_step.get("total_relationships", 0)
        
        print(f"📊 Results:")
        print(f"   Entities: {entities}")
        print(f"   Relationships: {relationships}")
        
        if query_step.get("results"):
            print(f"   Query Answer: {query_step['results']}")
        
        print(f"\n🎉 Phase 1 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        return False

def run_phase2(file_path, query="What are the main entities and relationships?"):
    """Run Phase 2 processing"""
    print(f"🚀 Running Phase 2 on: {file_path}")
    
    try:
        from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
        
        workflow = EnhancedVerticalSliceWorkflow()
        result = workflow.execute_enhanced_workflow(file_path, query, f"cli_enhanced_{Path(file_path).stem}")
        
        entities = len(result.get("entities", []))
        relationships = len(result.get("relationships", []))
        
        print(f"📊 Results:")
        print(f"   Enhanced Entities: {entities}")
        print(f"   Enhanced Relationships: {relationships}")
        
        print(f"🎉 Phase 2 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 failed: {e}")
        return False

def run_phase3(file_path, query="Extract and fuse entities"):
    """Run Phase 3 processing"""
    print(f"🚀 Running Phase 3 on: {file_path}")
    
    try:
        from src.core.phase_adapters import Phase3Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        phase3 = Phase3Adapter()
        request = ProcessingRequest(
            workflow_id=f"cli_phase3_{Path(file_path).stem}",
            documents=[file_path],
            queries=[query],
            domain_description="CLI test processing"
        )
        
        result = phase3.execute(request)
        
        if result.status.name == "SUCCESS":
            fusion_summary = result.results.get("processing_summary", {})
            print(f"📊 Results:")
            print(f"   Documents processed: {result.results.get('documents_processed', 1)}")
            print(f"   Total entities: {fusion_summary.get('total_entities_after_fusion', 0)}")
            print(f"   Fusion reduction: {fusion_summary.get('fusion_reduction', 0)}%")
            print(f"🎉 Phase 3 completed successfully!")
            return True
        else:
            print(f"❌ Phase 3 failed: {result.error_message}")
            return False
        
    except Exception as e:
        print(f"❌ Phase 3 failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Command Line Interface")
    parser.add_argument("file", help="PDF or text file to process")
    parser.add_argument("--phase", choices=["1", "2", "3"], default="1", help="Phase to run (default: 1)")
    parser.add_argument("--query", default="What are the main entities and relationships?", help="Query to run")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print("🔬 GraphRAG Command Line Interface")
    print("=" * 50)
    
    phase_funcs = {
        "1": run_phase1,
        "2": run_phase2,
        "3": run_phase3
    }
    
    success = phase_funcs[args.phase](str(file_path), args.query)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Processing completed successfully!")
        print(f"💡 Tip: Try different phases with --phase 2 or --phase 3")
    else:
        print("❌ Processing failed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()