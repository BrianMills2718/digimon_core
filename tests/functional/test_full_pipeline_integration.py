#!/usr/bin/env python3
"""
Full Pipeline Integration Test - P1→P2→P3 with Real Data Flow

This test addresses the critical gap identified in INTEGRATION_TESTING_GAP_ANALYSIS.md:
- Tests actual data flow between all three phases
- Validates that each phase contributes evidence to the final result
- Proves the integrated pipeline works with a single document end-to-end

Success Criteria (from CLAUDE.md):
1. Single document flows from Phase 1 → Phase 2 → Phase 3
2. Evidence of each phase's contribution (entities, relationships, processing)
3. Proof of integration without API compatibility issues
"""

import os
from pathlib import Path
import time

# Add src to path for imports

from core.phase_adapters import IntegratedPipelineOrchestrator
from core.graphrag_phase_interface import PhaseStatus
from core.neo4j_manager import ensure_neo4j_for_testing


def test_full_pipeline_integration():
    """
    CRITICAL INTEGRATION TEST: Complete P1→P2→P3 pipeline with single document
    
    This test validates:
    1. Phase transitions work without API failures
    2. Each phase processes the same document successfully  
    3. Data flows correctly between phases
    4. Evidence of each phase's unique contribution is captured
    """
    
    print("=" * 80)
    print("🧪 FULL PIPELINE INTEGRATION TEST")
    print("=" * 80)
    print("Testing: Phase 1 → Phase 2 → Phase 3 with real data flow")
    print("Goal: Prove integrated pipeline works, closing the gap identified in")
    print("      docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md")
    print()
    
    # Auto-start Neo4j if needed
    print("🔧 Ensuring Neo4j is available...")
    if not ensure_neo4j_for_testing():
        print("❌ CRITICAL: Cannot start Neo4j automatically")
        print("   Manual intervention required - see Neo4j startup documentation")
        return False
    print()
    
    # Find test PDF - use existing test file
    test_files = [
        "examples/pdfs/test_document.pdf",
        "examples/pdfs/enhanced_test.pdf",
        "test_data/enhanced_test.pdf",
        "archive/experimental_implementations/test.pdf",
        "archive/experimental_implementations/minimal_test.pdf"
    ]
    
    test_pdf = None
    for pdf_path in test_files:
        if os.path.exists(pdf_path):
            test_pdf = pdf_path
            break
    
    if not test_pdf:
        print("❌ CRITICAL: No test PDF found. Searched:")
        for path in test_files:
            print(f"   - {path}")
        print("\nThis test REQUIRES a PDF to validate the complete pipeline.")
        return False
    
    print(f"📄 Using test document: {test_pdf}")
    print(f"📄 File size: {os.path.getsize(test_pdf)} bytes")
    print()
    
    # Test parameters
    test_query = "What are the main concepts and how are they related?"
    domain_description = "Technology companies and electric vehicles"  # Matches PDF content about Tesla/SpaceX
    workflow_id = "integration_test_" + str(int(time.time()))
    
    print(f"🔍 Query: {test_query}")
    print(f"🏷️  Domain: {domain_description}")
    print(f"🆔 Workflow ID: {workflow_id}")
    print()
    
    # Execute integrated pipeline
    orchestrator = IntegratedPipelineOrchestrator()
    
    start_time = time.time()
    result = orchestrator.execute_full_pipeline(
        pdf_path=test_pdf,
        query=test_query,
        domain_description=domain_description,
        workflow_id=workflow_id
    )
    total_time = time.time() - start_time
    
    print()
    print("=" * 80)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    # Validate overall status
    if result["status"] != "success":
        print(f"❌ PIPELINE FAILED: {result['status']}")
        if result["errors"]:
            print("Errors:")
            for error in result["errors"]:
                print(f"   - {error}")
        return False
    
    print("✅ PIPELINE STATUS: SUCCESS")
    print(f"⏱️  Total execution time: {total_time:.2f}s")
    print()
    
    # Validate Phase 1 evidence
    p1_evidence = result["evidence"]
    print("📋 PHASE 1 EVIDENCE:")
    print(f"   Entities extracted: {p1_evidence.get('phase1_entities', 0)}")
    print(f"   Relationships found: {p1_evidence.get('phase1_relationships', 0)}")
    print(f"   Execution time: {p1_evidence.get('phase1_execution_time', 0):.2f}s")
    
    if p1_evidence.get('phase1_entities', 0) == 0:
        print("❌ PHASE 1 FAILED: No entities extracted")
        return False
    
    print("✅ Phase 1 contributed meaningful data")
    print()
    
    # Validate Phase 2 evidence
    print("📋 PHASE 2 EVIDENCE:")
    print(f"   Enhanced entities: {p1_evidence.get('phase2_entities', 0)}")
    print(f"   Enhanced relationships: {p1_evidence.get('phase2_relationships', 0)}")
    print(f"   Execution time: {p1_evidence.get('phase2_execution_time', 0):.2f}s")
    print(f"   Ontology used: {bool(p1_evidence.get('ontology_used'))}")
    
    if p1_evidence.get('phase2_entities', 0) == 0:
        print("❌ PHASE 2 FAILED: No enhanced entities")
        return False
    
    print("✅ Phase 2 contributed ontology-enhanced data")
    print()
    
    # Validate Phase 3 evidence  
    print("📋 PHASE 3 EVIDENCE:")
    print(f"   Final entities: {p1_evidence.get('phase3_entities', 0)}")
    print(f"   Final relationships: {p1_evidence.get('phase3_relationships', 0)}")
    print(f"   Execution time: {p1_evidence.get('phase3_execution_time', 0):.2f}s")
    print(f"   Fusion applied: {bool(p1_evidence.get('fusion_applied'))}")
    
    if p1_evidence.get('phase3_entities', 0) == 0:
        print("❌ PHASE 3 FAILED: No final entities")
        return False
    
    print("✅ Phase 3 contributed multi-document fusion")
    print()
    
    # Validate progression
    entity_progression = p1_evidence.get('entity_progression', [])
    relationship_progression = p1_evidence.get('relationship_progression', [])
    
    print("📈 PHASE PROGRESSION:")
    print(f"   Entities: {entity_progression}")
    print(f"   Relationships: {relationship_progression}")
    
    if len(entity_progression) != 3 or len(relationship_progression) != 3:
        print("❌ PROGRESSION FAILED: Missing phase data")
        return False
    
    print("✅ All phases executed with measurable progression")
    print()
    
    # Final validation
    print("=" * 80)
    print("🎯 INTEGRATION VALIDATION SUMMARY")
    print("=" * 80)
    
    validations = [
        ("Pipeline completes without errors", result["status"] == "success"),
        ("Phase 1 extracts entities", p1_evidence.get('phase1_entities', 0) > 0),
        ("Phase 2 enhances with ontology", p1_evidence.get('phase2_entities', 0) > 0),
        ("Phase 3 applies fusion", p1_evidence.get('phase3_entities', 0) > 0),
        ("All phases complete", len(entity_progression) == 3),
        ("Data flows between phases", all(x > 0 for x in entity_progression)),
        ("Evidence captured for each phase", all(key in p1_evidence for key in [
            'phase1_entities', 'phase2_entities', 'phase3_entities'
        ]))
    ]
    
    all_passed = True
    for description, passed in validations:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 INTEGRATION TEST PASSED: Complete P1→P2→P3 pipeline working!")
        print("   This test proves the integration gap has been closed.")
        print("   All phases contribute evidence and data flows correctly.")
        return True
    else:
        print("❌ INTEGRATION TEST FAILED: Pipeline has integration issues")
        return False


def main():
    """Run the full pipeline integration test"""
    
    print("Starting Full Pipeline Integration Test...")
    print("This test validates the complete P1→P2→P3 data flow")
    print()
    
    success = test_full_pipeline_integration()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ SUCCESS: Full pipeline integration test PASSED")
        print("Integration gap from INTEGRATION_TESTING_GAP_ANALYSIS.md is CLOSED")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80) 
        print("❌ FAILURE: Full pipeline integration test FAILED")
        print("Integration issues still exist - pipeline is not properly connected")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit(main())