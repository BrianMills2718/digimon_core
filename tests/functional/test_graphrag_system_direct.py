#!/usr/bin/env python3
"""
Direct test of GraphRAG system - bypass UI completely
This shows if the core system actually works or not
"""

import tempfile
import os
from pathlib import Path

def test_phase1_real():
    """Test Phase 1 with real PDF"""
    print("🧪 Testing Phase 1 with Real Document")
    
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        
        # Use actual PDF from examples if it exists
        pdf_path = "examples/pdfs/wiki1.pdf"
        if not os.path.exists(pdf_path):
            # Create a text file as fallback
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("""
                Dr. John Smith is a professor at MIT who studies artificial intelligence.
                He collaborates with Dr. Jane Doe from Stanford University on machine learning research.
                Their research focuses on neural networks and deep learning algorithms.
                The MIT Computer Science Department has been working on this project since 2020.
                """)
                pdf_path = f.name
        
        config_manager = ConfigManager()
        workflow_config = create_unified_workflow_config(
            phase=Phase.PHASE1, 
            optimization_level=OptimizationLevel.STANDARD,
            workflow_storage_dir="./data"
        )
        orchestrator = PipelineOrchestrator(workflow_config, config_manager)
        result = orchestrator.execute(
            [pdf_path], 
            ["What are the main people and organizations mentioned?"]
        )
        
        final_result = result.get("final_result", {})
        entities = len(final_result.get("entities", []))
        relationships = len(final_result.get("relationships", []))
        query_results = final_result.get("query_results", [])
        
        print(f"✅ Phase 1 completed successfully")
        print(f"✅ Query results: {len(query_results)} results")
        
        print(f"✅ Entities Found: {entities}")
        print(f"✅ Relationships Found: {relationships}")
        
        if entities > 0 and relationships > 0:
            print("🎉 Phase 1: ACTUALLY WORKING!")
            return True
        else:
            print("⚠️ Phase 1: Completes but finds no entities/relationships")
            return False
            
    except Exception as e:
        print(f"❌ Phase 1 Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_real():
    """Test Phase 2 if available"""
    print("\n🧪 Testing Phase 2")
    
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Dr. Smith studies AI at MIT.")
            file_path = f.name
        
        config_manager = ConfigManager()
        config = create_unified_workflow_config(
            phase=Phase.PHASE2,
            optimization_level=OptimizationLevel.STANDARD,
            workflow_storage_dir="./data"
        )
        orchestrator = PipelineOrchestrator(config, config_manager)
        result = orchestrator.execute([file_path], ["What entities exist?"])
        
        final_result = result.get("final_result", {})
        entities = len(final_result.get("entities", []))
        print(f"✅ Phase 2: Found {entities} entities")
        return entities > 0
        
    except Exception as e:
        print(f"❌ Phase 2 Failed: {e}")
        return False

def test_phase3_real():
    """Test Phase 3 with proper PDF"""
    print("\n🧪 Testing Phase 3")
    
    try:
        from src.core.phase_adapters import Phase3Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        # Create a temporary PDF-like file (Phase 3 expects PDFs)
        # For real test, would need actual PDF
        
        # Check if we have real PDF
        pdf_path = "examples/pdfs/wiki1.pdf"
        if not os.path.exists(pdf_path):
            print("⚠️ Phase 3: No PDF available for testing (needs examples/pdfs/wiki1.pdf)")
            return False
        
        phase3 = Phase3Adapter()
        request = ProcessingRequest(
            workflow_id="test_phase3",
            documents=[pdf_path],
            queries=["Extract main entities"],
            domain_description="Test document"
        )
        
        result = phase3.execute(request)
        
        print(f"✅ Phase 3 Status: {result.status}")
        if result.error_message:
            print(f"❌ Phase 3 Error: {result.error_message}")
            return False
        
        print("🎉 Phase 3: ACTUALLY WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 3 Failed: {e}")
        return False

def main():
    """Test the entire GraphRAG system directly"""
    print("🔬 DIRECT GRAPHRAG SYSTEM TEST")
    print("=" * 50)
    print("This bypasses the UI to test if the core system works")
    print()
    
    results = []
    
    # Test each phase
    tests = [
        ("Phase 1 (Basic Pipeline)", test_phase1_real),
        ("Phase 2 (Enhanced)", test_phase2_real),
        ("Phase 3 (Multi-Document)", test_phase3_real)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "="*50)
    print("🏁 FINAL RESULTS")
    print("="*50)
    
    working_phases = []
    broken_phases = []
    
    for test_name, success in results:
        if success:
            working_phases.append(test_name)
            print(f"✅ {test_name}: WORKING")
        else:
            broken_phases.append(test_name)
            print(f"❌ {test_name}: BROKEN")
    
    print(f"\n📊 Summary:")
    print(f"   Working: {len(working_phases)}/{len(results)} phases")
    print(f"   Broken: {len(broken_phases)}/{len(results)} phases")
    
    if working_phases:
        print(f"\n🎉 GOOD NEWS: These phases actually work:")
        for phase in working_phases:
            print(f"   ✅ {phase}")
    
    if broken_phases:
        print(f"\n⚠️ PROBLEMS: These phases need fixing:")
        for phase in broken_phases:
            print(f"   ❌ {phase}")
    
    if len(working_phases) == len(results):
        print(f"\n🚀 SYSTEM STATUS: All phases working! UI is the only problem.")
    elif len(working_phases) > 0:
        print(f"\n🔧 SYSTEM STATUS: Partially working. {len(working_phases)} phases functional.")
    else:
        print(f"\n💥 SYSTEM STATUS: Core system broken. Weeks may indeed be wasted.")
    
    return len(working_phases) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)