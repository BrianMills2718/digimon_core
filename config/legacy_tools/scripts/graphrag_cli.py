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
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        workflow_config = create_unified_workflow_config(phase=Phase.PHASE1, optimization_level=OptimizationLevel.STANDARD)
        workflow = PipelineOrchestrator(workflow_config, config_manager)
        result = workflow.execute([file_path], [query])
        
        final_result = result.get("final_result", {})
        
        print(f"\n✅ Status: completed")
        
        # Show results using new orchestrator format
        entities = final_result.get("entities", [])
        relationships = final_result.get("relationships", [])
        query_results = final_result.get("query_results", [])
        
        print(f"📊 Results:")
        print(f"   Entities: {len(entities)}")
        print(f"   Relationships: {len(relationships)}")
        
        if query_results:
            print(f"   Query Results: {len(query_results)} found")
        
        print(f"\n🎉 Phase 1 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        return False

def run_phase2(file_path, query="What are the main entities and relationships?"):
    """Run Phase 2 processing"""
    print(f"🚀 Running Phase 2 on: {file_path}")
    
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        workflow_config = create_unified_workflow_config(phase=Phase.PHASE2, optimization_level=OptimizationLevel.ENHANCED)
        workflow = PipelineOrchestrator(workflow_config, config_manager)
        result = workflow.execute([file_path], [query])
        
        final_result = result.get("final_result", {})
        entities = len(final_result.get("entities", []))
        relationships = len(final_result.get("relationships", []))
        
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