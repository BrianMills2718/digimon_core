"""Test Reliability - Find and Fix All Failure Points - HISTORICAL TEST ⚠️

⚠️ MISLEADING TITLE: "100% Reliability" is impossible - no system can be 100% reliable
Current reality: System achieves high reliability (90%+) but not perfect reliability

According to CLAUDE.md guidelines:
- Success = System completes without crashing
- Failure = Unhandled exceptions or processing stops
- Accuracy issues (entity resolution) are NOT failures
"""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from src.tools.phase1.vertical_slice_workflow_optimized import OptimizedVerticalSliceWorkflow
from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow
from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
from src.core.graphrag_phase_interface import ProcessingRequest


def test_phase1_reliability():
    """Test Phase 1 for all failure scenarios"""
    print("\n🔍 Testing Phase 1 Reliability")
    print("="*50)
    
    failures = []
    
    # Test scenarios
    test_cases = [
        {
            "name": "Valid PDF",
            "pdf": "./examples/pdfs/wiki1.pdf",
            "query": "What are the main entities?",
            "should_succeed": True
        },
        {
            "name": "Non-existent PDF",
            "pdf": "./does_not_exist.pdf",
            "query": "Test query",
            "should_succeed": True  # Should handle gracefully
        },
        {
            "name": "Empty query",
            "pdf": "./examples/pdfs/wiki1.pdf", 
            "query": "",
            "should_succeed": True  # Should handle gracefully
        },
        {
            "name": "Invalid PDF path",
            "pdf": None,
            "query": "Test query",
            "should_succeed": True  # Should handle gracefully
        },
        {
            "name": "Corrupt PDF",
            "pdf": "./test_corrupt.pdf",
            "query": "Test query",
            "should_succeed": True  # Should handle gracefully
        }
    ]
    
    # Create a corrupt PDF for testing
    with open("./test_corrupt.pdf", "wb") as f:
        f.write(b"This is not a valid PDF file")
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        try:
            workflow = OptimizedVerticalSliceWorkflow()
            
            if test['pdf'] is None:
                # Test handling of None input
                try:
                    result = workflow.execute_workflow("", test['query'], test['name'])
                except Exception as e:
                    result = {"status": "error", "error": str(e)}
            else:
                result = workflow.execute_workflow(
                    test['pdf'], 
                    test['query'],
                    test['name'],
                    skip_pagerank=True  # Speed up tests
                )
            
            workflow.close()
            
            # Check if it completed (success or handled error)
            if result.get('status') in ['success', 'failed', 'error']:
                print(f"   ✅ Completed with status: {result['status']}")
                if result['status'] != 'success':
                    print(f"   ℹ️  Error handled: {result.get('error', 'No error message')}")
            else:
                print(f"   ❌ Unexpected status: {result.get('status')}")
                failures.append(f"Phase 1 - {test['name']}: Unexpected status")
                
        except Exception as e:
            print(f"   ❌ UNHANDLED EXCEPTION: {e}")
            failures.append(f"Phase 1 - {test['name']}: {str(e)}")
            traceback.print_exc()
    
    # Cleanup
    if os.path.exists("./test_corrupt.pdf"):
        os.remove("./test_corrupt.pdf")
    
    return failures


def test_phase2_reliability():
    """Test Phase 2 for all failure scenarios"""
    print("\n\n🔍 Testing Phase 2 Reliability")
    print("="*50)
    
    failures = []
    
    test_cases = [
        {
            "name": "Valid inputs",
            "pdf": "./examples/pdfs/wiki1.pdf",
            "query": "What are the main entities?",
            "domain": "Technology companies",
            "should_succeed": True
        },
        {
            "name": "Missing domain description",
            "pdf": "./examples/pdfs/wiki1.pdf",
            "query": "Test query",
            "domain": None,
            "should_succeed": True  # Should handle gracefully
        },
        {
            "name": "Multiple documents (unsupported)",
            "pdfs": ["./examples/pdfs/wiki1.pdf", "./examples/pdfs/wiki1.pdf"],
            "query": "Test query",
            "domain": "Test domain",
            "should_succeed": True  # Should reject gracefully
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        try:
            adapter = Phase2Adapter()
            
            # Create request
            if 'pdfs' in test:
                request = ProcessingRequest(
                    documents=test['pdfs'],
                    queries=[test['query']],
                    domain_description=test['domain'],
                    workflow_id=f"test_phase2_{test['name']}"
                )
            else:
                request = ProcessingRequest(
                    documents=[test['pdf']] if test['pdf'] else [],
                    queries=[test['query']] if test['query'] else [],
                    domain_description=test['domain'],
                    workflow_id=f"test_phase2_{test['name']}"
                )
            
            result = adapter.execute(request)
            
            # Check completion (handle both string and enum statuses)
            status_str = str(result.status).lower()
            if 'success' in status_str or 'error' in status_str:
                print(f"   ✅ Completed with status: {result.status}")
                if 'error' in status_str:
                    print(f"   ℹ️  Error handled: {result.error_message}")
            else:
                print(f"   ❌ Unexpected status: {result.status}")
                failures.append(f"Phase 2 - {test['name']}: Unexpected status")
                
        except Exception as e:
            print(f"   ❌ UNHANDLED EXCEPTION: {e}")
            failures.append(f"Phase 2 - {test['name']}: {str(e)}")
            traceback.print_exc()
    
    return failures


def test_phase3_reliability():
    """Test Phase 3 placeholder behavior"""
    print("\n\n🔍 Testing Phase 3 Reliability")
    print("="*50)
    
    failures = []
    
    try:
        adapter = Phase3Adapter()
        request = ProcessingRequest(
            documents=["test1.pdf", "test2.pdf"],
            queries=["Test multi-doc query"],
            workflow_id="test_phase3"
        )
        
        result = adapter.execute(request)
        
        status_str = str(result.status).lower()
        # Phase 3 now works and returns validation errors for missing files
        if 'error' in status_str and result.error_message and "Document not found" in result.error_message:
            print("   ✅ Phase 3 returns expected validation error for missing documents")
        elif 'error' in status_str:
            print(f"   ✅ Phase 3 handled error gracefully: {result.error_message}")
        else:
            print(f"   ❌ Unexpected Phase 3 behavior: {result.status}")
            failures.append(f"Phase 3: Unexpected behavior")
            
    except Exception as e:
        print(f"   ❌ UNHANDLED EXCEPTION in Phase 3: {e}")
        failures.append(f"Phase 3: {str(e)}")
        traceback.print_exc()
    
    return failures


def test_neo4j_failure_recovery():
    """Test Neo4j connection failure recovery"""
    print("\n\n🔍 Testing Neo4j Failure Recovery")
    print("="*50)
    
    failures = []
    
    # Test with wrong credentials
    try:
        workflow = OptimizedVerticalSliceWorkflow(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="wrong_user",
            neo4j_password="wrong_password"
        )
        
        # This should handle the connection failure gracefully
        result = workflow.execute_workflow(
            "./examples/pdfs/wiki1.pdf",
            "Test query",
            "neo4j_failure_test",
            skip_pagerank=True
        )
        
        if 'error' in result or result['status'] in ['failed', 'error']:
            print("   ✅ Neo4j connection failure handled gracefully")
        else:
            print("   ❌ Neo4j failure not properly handled")
            failures.append("Neo4j connection failure not handled")
            
    except Exception as e:
        print(f"   ❌ UNHANDLED EXCEPTION with Neo4j failure: {e}")
        failures.append(f"Neo4j failure: {str(e)}")
    
    return failures


def main():
    """Run all reliability tests"""
    print("="*60)
    print("100% RELIABILITY TEST SUITE")
    print("Goal: Zero unhandled exceptions, 100% graceful error handling")
    print("="*60)
    
    all_failures = []
    
    # Run all test suites
    all_failures.extend(test_phase1_reliability())
    all_failures.extend(test_phase2_reliability())
    all_failures.extend(test_phase3_reliability())
    all_failures.extend(test_neo4j_failure_recovery())
    
    # Summary
    print("\n\n" + "="*60)
    print("RELIABILITY TEST SUMMARY")
    print("="*60)
    
    if not all_failures:
        print("✅ HIGH RELIABILITY ACHIEVED!")
        print("All test scenarios completed without unhandled exceptions")
        print("Note: 100% reliability is impossible - this tests specific scenarios only")
    else:
        print(f"❌ Found {len(all_failures)} reliability issues:\n")
        for i, failure in enumerate(all_failures, 1):
            print(f"{i}. {failure}")
        print(f"\nReliability Score: {(1 - len(all_failures)/15) * 100:.1f}%")
    
    return len(all_failures) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)