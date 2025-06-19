#!/usr/bin/env python3
"""
Quick Adversarial Test - Assume everything is broken, document when wrong
"""

import tempfile
import time
import os

def assume_imports_fail():
    """Assume all core imports will fail"""
    print("🔥 ASSUMING ALL IMPORTS WILL FAIL")
    
    evidence_wrong = []
    confirmed_broken = []
    
    test_imports = [
        "src.tools.phase1.vertical_slice_workflow",
        "src.tools.phase1.t01_pdf_loader", 
        "src.tools.phase1.t23a_spacy_ner",
        "src.tools.phase2.enhanced_vertical_slice_workflow",
        "src.core.phase_adapters"
    ]
    
    for module in test_imports:
        try:
            exec(f"import {module}")
            evidence_wrong.append(f"❌ WRONG: {module} imported successfully (expected failure)")
        except Exception as e:
            confirmed_broken.append(f"✅ CORRECT: {module} failed as expected: {e}")
    
    return evidence_wrong, confirmed_broken

def assume_phase1_workflow_fails():
    """Assume Phase 1 workflow will fail"""
    print("🔥 ASSUMING PHASE 1 WORKFLOW WILL FAIL")
    
    # Create simple test
    test_text = "Dr. Smith works at MIT."
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_text)
            test_file = f.name
        
        from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        workflow = VerticalSliceWorkflow()
        
        start_time = time.time()
        result = workflow.execute_workflow(test_file, "What entities?", "quick_test")
        duration = time.time() - start_time
        
        os.unlink(test_file)
        
        # Check if assumption was wrong
        if isinstance(result, dict) and result.get("status") == "success":
            steps = result.get("steps", {})
            entities = steps.get("entity_extraction", {}).get("total_entities", 0)
            relationships = steps.get("relationship_extraction", {}).get("total_relationships", 0)
            
            if entities > 0 or relationships > 0:
                return [f"❌ WRONG: Phase 1 worked - {entities} entities, {relationships} relationships in {duration:.2f}s"], []
            else:
                return [], [f"✅ CORRECT: Phase 1 failed - no extraction despite success status"]
        else:
            return [], [f"✅ CORRECT: Phase 1 failed - {result.get('error', 'unknown error')}"]
            
    except Exception as e:
        return [], [f"✅ CORRECT: Phase 1 failed with exception - {e}"]

def assume_cli_interface_fails():
    """Assume CLI interface will fail"""
    print("🔥 ASSUMING CLI INTERFACE WILL FAIL")
    
    try:
        # Test that graphrag_cli.py exists and can be imported
        import graphrag_cli
        
        # If we get here, our assumption was wrong
        return [f"❌ WRONG: CLI interface imported successfully"], []
        
    except Exception as e:
        return [], [f"✅ CORRECT: CLI interface failed - {e}"]

def assume_neo4j_fails():
    """Assume Neo4j connection will fail"""
    print("🔥 ASSUMING NEO4J CONNECTION WILL FAIL")
    
    try:
        from src.tools.base_neo4j_tool import BaseNeo4jTool
        tool = BaseNeo4jTool()
        
        # Try basic query
        result = tool._execute_read_query("MATCH (n) RETURN count(n) LIMIT 1")
        
        if result is not None:
            return [f"❌ WRONG: Neo4j connected and returned: {result}"], []
        else:
            return [], [f"✅ CORRECT: Neo4j returned null/empty"]
            
    except Exception as e:
        return [], [f"✅ CORRECT: Neo4j failed - {e}"]

def main():
    print("🔥 QUICK ADVERSARIAL VERIFICATION")
    print("ASSUMPTION: Everything is broken")
    print("=" * 50)
    
    all_evidence_wrong = []
    all_confirmed_broken = []
    
    # Test imports
    wrong, broken = assume_imports_fail()
    all_evidence_wrong.extend(wrong)
    all_confirmed_broken.extend(broken)
    
    # Test Phase 1 workflow  
    wrong, broken = assume_phase1_workflow_fails()
    all_evidence_wrong.extend(wrong)
    all_confirmed_broken.extend(broken)
    
    # Test CLI
    wrong, broken = assume_cli_interface_fails()
    all_evidence_wrong.extend(wrong)
    all_confirmed_broken.extend(broken)
    
    # Test Neo4j
    wrong, broken = assume_neo4j_fails()
    all_evidence_wrong.extend(wrong)
    all_confirmed_broken.extend(broken)
    
    print("\n" + "=" * 50)
    print("📊 ADVERSARIAL RESULTS")
    print("=" * 50)
    
    print(f"\n❌ EVIDENCE MY ASSUMPTIONS WERE WRONG ({len(all_evidence_wrong)}):")
    for evidence in all_evidence_wrong:
        print(f"   {evidence}")
    
    print(f"\n✅ CONFIRMED BROKEN AS EXPECTED ({len(all_confirmed_broken)}):")
    for broken in all_confirmed_broken:
        print(f"   {broken}")
    
    if len(all_evidence_wrong) > len(all_confirmed_broken):
        print(f"\n🎉 SURPRISING: More capabilities work than expected!")
        print(f"   {len(all_evidence_wrong)} assumptions proven wrong")
    else:
        print(f"\n⚠️ EXPECTED: Most capabilities broken as assumed")
    
    return 0

if __name__ == "__main__":
    exit(main())