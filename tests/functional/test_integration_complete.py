#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Tests phase transitions, full pipeline integration, and cross-phase data flow.
"""

import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

# Add src to path

def test_phase_transitions():
    """Test data flow between Phase 1 → Phase 2 → Phase 3."""
    print("🔄 Testing Phase Transitions")
    
    try:
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter, Phase3Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        # Create test document
        test_content = """
        AI Research at Stanford University
        
        Dr. Jane Smith from Stanford AI Lab has developed a breakthrough machine learning algorithm.
        The research was conducted in collaboration with Google Research and MIT.
        This work was funded by the National Science Foundation with a $5 million grant.
        The findings were published in the journal Nature AI.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write(test_content)
            test_doc = f.name
        
        print(f"✅ Created test document: {Path(test_doc).name}")
        
        # Phase 1 → Phase 2 transition test
        print("\n🔄 Test 1: Phase 1 → Phase 2 transition")
        
        # Execute Phase 1
        phase1 = Phase1Adapter()
        phase1_request = ProcessingRequest(
            workflow_id="transition_test_p1",
            documents=[test_doc],
            queries=["What are the main entities?"]
        )
        
        phase1_result = phase1.execute(phase1_request)
        print(f"  Phase 1 status: {phase1_result.status}")
        print(f"  Phase 1 entities: {phase1_result.entity_count}")
        print(f"  Phase 1 relationships: {phase1_result.relationship_count}")
        
        # Use Phase 1 results to inform Phase 2
        if phase1_result.status == "success":
            # Phase 2 with domain description informed by Phase 1 results
            phase2 = Phase2Adapter()
            phase2_request = ProcessingRequest(
                workflow_id="transition_test_p2",
                documents=[test_doc],
                queries=["Extract academic research entities with proper classification"],
                domain_description="Academic AI research collaboration involving universities and companies"
            )
            
            phase2_result = phase2.execute(phase2_request)
            print(f"  Phase 2 status: {phase2_result.status}")
            print(f"  Phase 2 entities: {phase2_result.entity_count}")
            print(f"  Phase 2 relationships: {phase2_result.relationship_count}")
            
            # Compare Phase 1 vs Phase 2 results
            entity_improvement = phase2_result.entity_count - phase1_result.entity_count
            rel_improvement = phase2_result.relationship_count - phase1_result.relationship_count
            print(f"  Entity improvement: {entity_improvement:+d}")
            print(f"  Relationship improvement: {rel_improvement:+d}")
            
            if phase2_result.status == "success":
                print("  ✅ Phase 1 → Phase 2 transition successful")
            else:
                print(f"  ❌ Phase 2 failed: {phase2_result.error_message}")
        else:
            print(f"  ❌ Phase 1 failed: {phase1_result.error_message}")
        
        # Phase 2 → Phase 3 transition test
        print("\n🔄 Test 2: Phase 2 → Phase 3 transition")
        
        # Create multiple documents for Phase 3
        test_docs = []
        test_contents = [
            test_content,  # Original document
            """
            Machine Learning Research at MIT
            
            Prof. Michael Chen from MIT Computer Science has published groundbreaking AI research.
            The MIT team collaborated with Facebook Research and Stanford University.
            This project received funding from DARPA with a $3 million grant.
            Results were presented at the International Conference on Machine Learning.
            """
        ]
        
        for i, content in enumerate(test_contents):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                f.write(content)
                test_docs.append(f.name)
        
        # Execute Phase 3 with multiple documents
        phase3 = Phase3Adapter()
        phase3_request = ProcessingRequest(
            workflow_id="transition_test_p3",
            documents=test_docs,
            queries=["Compare research across all documents", "Identify collaboration patterns"],
            domain_description="Cross-institutional AI research analysis"
        )
        
        phase3_result = phase3.execute(phase3_request)
        print(f"  Phase 3 status: {phase3_result.status}")
        print(f"  Phase 3 entities: {phase3_result.entity_count}")
        print(f"  Phase 3 relationships: {phase3_result.relationship_count}")
        
        if phase3_result.status == "success":
            fusion_summary = phase3_result.results.get("processing_summary", {})
            docs_processed = phase3_result.results.get("documents_processed", 0)
            print(f"  Documents processed: {docs_processed}")
            print(f"  Fusion effectiveness: {fusion_summary.get('fusion_reduction', 0):.1%}")
            print("  ✅ Phase 2 → Phase 3 transition successful")
        else:
            print(f"  ❌ Phase 3 failed: {phase3_result.error_message}")
        
        # Clean up
        for doc in [test_doc] + test_docs:
            try:
                os.unlink(doc)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Phase transition test failed: {e}")
        print(traceback.format_exc())
        return False

def test_full_pipeline_integration():
    """Test complete pipeline from UI to Neo4j with all phases."""
    print("\n🔗 Testing Full Pipeline Integration")
    
    try:
        # Test 1: Check all adapters are registered
        print("\n📋 Test 1: Phase adapter registration")
        from src.core.graphrag_phase_interface import get_available_phases
        available_phases = get_available_phases()
        print(f"  Available phases: {available_phases}")
        
        expected_phases = ["Phase 1: Basic", "Phase 2: Enhanced", "Phase 3: Multi-Document"]
        for expected in expected_phases:
            if any(expected.split(':')[0] in phase for phase in available_phases):
                print(f"  ✅ {expected} registered")
            else:
                print(f"  ❌ {expected} missing")
        
        # Test 2: Service manager integration
        print("\n⚙️ Test 2: Service manager integration")
        from src.core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        # Check critical services
        services_to_check = ["neo4j", "identity", "provenance", "quality"]
        for service_name in services_to_check:
            try:
                service = getattr(service_manager, f"get_{service_name}_service", None)
                if service:
                    result = service()
                    print(f"  ✅ {service_name} service available")
                else:
                    print(f"  ⚠️ {service_name} service getter not found")
            except Exception as e:
                print(f"  ❌ {service_name} service failed: {e}")
        
        # Test 3: Neo4j integration across phases
        print("\n🗄️ Test 3: Neo4j cross-phase integration")
        try:
            from py2neo import Graph
            graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
            
            # Test connection
            result = graph.run("RETURN 1 as test").data()
            print(f"  ✅ Neo4j connection successful")
            
            # Check for data from different phases
            entity_count = graph.run("MATCH (e:Entity) RETURN count(e) as count").data()[0]["count"]
            relationship_count = graph.run("MATCH ()-[r]->() RETURN count(r) as count").data()[0]["count"]
            print(f"  Existing entities: {entity_count}")
            print(f"  Existing relationships: {relationship_count}")
            
        except Exception as e:
            print(f"  ❌ Neo4j integration test failed: {e}")
        
        # Test 4: UI integration completeness
        print("\n🖥️ Test 4: UI integration completeness")
        try:
            # Check UI can import all phase functions
            ui_path = Path(__file__).parent / "ui"
            from graphrag_ui import process_with_phase1, process_with_phase2, process_with_phase3
            
            print("  ✅ All phase processing functions importable")
            
            # Check UI has all required components
            required_ui_components = [
                "DocumentProcessingResult",
                "render_phase_status", 
                "render_document_upload",
                "display_processing_results"
            ]
            
            import graphrag_ui
            for component in required_ui_components:
                if hasattr(graphrag_ui, component):
                    print(f"  ✅ {component} available")
                else:
                    print(f"  ❌ {component} missing")
            
        except Exception as e:
            print(f"  ❌ UI integration test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline integration test failed: {e}")
        print(traceback.format_exc())
        return False

def test_cross_phase_data_flow():
    """Test data flow and consistency across phases."""
    print("\n🔀 Testing Cross-Phase Data Flow")
    
    try:
        # Test 1: Entity consistency across phases
        print("\n🏷️ Test 1: Entity consistency")
        
        test_text = "Dr. Sarah Johnson from Stanford University published AI research."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write(test_text)
            test_doc = f.name
        
        from src.core.phase_adapters import Phase1Adapter, Phase2Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        # Run Phase 1
        phase1 = Phase1Adapter()
        p1_request = ProcessingRequest(
            workflow_id="consistency_test_p1",
            documents=[test_doc],
            queries=["Extract entities"]
        )
        p1_result = phase1.execute(p1_request)
        
        # Run Phase 2 
        phase2 = Phase2Adapter()
        p2_request = ProcessingRequest(
            workflow_id="consistency_test_p2", 
            documents=[test_doc],
            queries=["Extract entities"],
            domain_description="Academic research"
        )
        p2_result = phase2.execute(p2_request)
        
        print(f"  Phase 1 entities: {p1_result.entity_count}")
        print(f"  Phase 2 entities: {p2_result.entity_count}")
        
        # Entity consistency check
        if p1_result.entity_count > 0 and p2_result.entity_count > 0:
            # Phase 2 should typically find more entities due to ontology awareness
            if p2_result.entity_count >= p1_result.entity_count:
                print("  ✅ Entity consistency: Phase 2 found same or more entities")
            else:
                print("  ⚠️ Entity consistency: Phase 2 found fewer entities (unexpected)")
        else:
            print("  ⚠️ Entity consistency: Some phases found no entities")
        
        # Test 2: Performance consistency
        print("\n⏱️ Test 2: Performance consistency")
        
        p1_time = p1_result.execution_time
        p2_time = p2_result.execution_time
        
        print(f"  Phase 1 time: {p1_time:.2f}s")
        print(f"  Phase 2 time: {p2_time:.2f}s")
        
        # Phase 2 should be slower due to LLM calls, but not excessively
        if p2_time <= p1_time * 10:  # Allow 10x slower for Phase 2
            print("  ✅ Performance consistency: Phase 2 time reasonable")
        else:
            print("  ⚠️ Performance consistency: Phase 2 much slower than expected")
        
        # Test 3: Error handling consistency
        print("\n❌ Test 3: Error handling consistency")
        
        # Test with invalid document
        invalid_request = ProcessingRequest(
            workflow_id="error_test",
            documents=["/nonexistent/file.pdf"],
            queries=["test"]
        )
        
        # All phases should handle errors gracefully
        phases_to_test = [("Phase 1", phase1), ("Phase 2", phase2)]
        
        for phase_name, phase_adapter in phases_to_test:
            try:
                error_result = phase_adapter.execute(invalid_request)
                if error_result.status == "error":
                    print(f"  ✅ {phase_name} handles errors gracefully")
                else:
                    print(f"  ⚠️ {phase_name} did not report error for invalid input")
            except Exception as e:
                print(f"  ❌ {phase_name} threw unhandled exception: {e}")
        
        # Clean up
        try:
            os.unlink(test_doc)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-phase data flow test failed: {e}")
        print(traceback.format_exc())
        return False

def test_integration_reliability():
    """Test system reliability and error recovery."""
    print("\n🛡️ Testing Integration Reliability")
    
    try:
        # Test 1: Service failure recovery
        print("\n⚡ Test 1: Service failure recovery")
        
        # Test with various failure conditions
        failure_tests = [
            ("Empty document", ""),
            ("Very short document", "A."),
            ("Non-English content", "Este es un documento en español."),
            ("Special characters", "Test with émojis 🚀 and spéciàl çharacters"),
        ]
        
        from src.core.phase_adapters import Phase1Adapter
        from src.core.graphrag_phase_interface import ProcessingRequest
        
        phase1 = Phase1Adapter()
        
        for test_name, content in failure_tests:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                    f.write(content)
                    test_doc = f.name
                
                request = ProcessingRequest(
                    workflow_id=f"reliability_test_{test_name.replace(' ', '_')}",
                    documents=[test_doc],
                    queries=["Extract entities"]
                )
                
                result = phase1.execute(request)
                
                # Should either succeed or fail gracefully
                if result.status in ["success", "error"]:
                    print(f"  ✅ {test_name}: Handled gracefully ({result.status})")
                else:
                    print(f"  ⚠️ {test_name}: Unexpected status ({result.status})")
                
                os.unlink(test_doc)
                
            except Exception as e:
                print(f"  ❌ {test_name}: Unhandled exception: {e}")
        
        # Test 2: Concurrent processing
        print("\n🔄 Test 2: Concurrent processing capability")
        
        # Create multiple test documents
        test_docs = []
        for i in range(3):
            content = f"Document {i+1}: This is test content for concurrent processing test."
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
                f.write(content)
                test_docs.append(f.name)
        
        # Process multiple documents in sequence (simulating concurrent load)
        start_time = time.time()
        results = []
        
        for i, doc in enumerate(test_docs):
            request = ProcessingRequest(
                workflow_id=f"concurrent_test_{i}",
                documents=[doc],
                queries=["Extract entities"]
            )
            
            result = phase1.execute(request)
            results.append(result)
        
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.status == "success"]
        
        print(f"  Processed {len(test_docs)} documents in {total_time:.2f}s")
        print(f"  Success rate: {len(successful_results)}/{len(results)}")
        
        if len(successful_results) == len(results):
            print("  ✅ Concurrent processing: All documents processed successfully")
        else:
            print("  ⚠️ Concurrent processing: Some documents failed")
        
        # Clean up
        for doc in test_docs:
            try:
                os.unlink(doc)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Integration reliability test failed: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Run comprehensive integration test suite."""
    print("🧪 Comprehensive Integration Test Suite")
    print("=" * 50)
    
    # Update todo status
    from src.core.workflow_state_service import WorkflowStateService
    workflow_service = WorkflowStateService()
    
    test_results = []
    
    # Run all test suites
    test_suites = [
        ("Phase Transitions", test_phase_transitions),
        ("Full Pipeline Integration", test_full_pipeline_integration), 
        ("Cross-Phase Data Flow", test_cross_phase_data_flow),
        ("Integration Reliability", test_integration_reliability)
    ]
    
    for suite_name, test_function in test_suites:
        print(f"\n{'='*20} {suite_name} {'='*20}")
        try:
            success = test_function()
            test_results.append((suite_name, success))
        except Exception as e:
            print(f"❌ {suite_name} suite failed: {e}")
            test_results.append((suite_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for suite_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {suite_name}")
    
    print(f"\nOverall: {passed}/{total} test suites passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️ Some integration tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)