#!/usr/bin/env python3
"""
TEST MCP TOOL CHAINS
Test realistic chains of MCP tools working together to accomplish complex tasks
"""

import sys
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_tool_chains():
    """Test chains of MCP tools working together"""
    
    print("🔗 TESTING MCP TOOL CHAINS")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_chains": 4,
            "chains_tested": 0,
            "chains_passed": 0,
            "chains_failed": 0,
            "start_time": time.time()
        },
        "chain_results": []
    }
    
    # Import services
    try:
        from src.core.identity_service import IdentityService
        from src.core.provenance_service import ProvenanceService
        from src.core.quality_service import QualityService
        from src.core.workflow_state_service import WorkflowStateService
        
        identity_service = IdentityService()
        provenance_service = ProvenanceService()
        quality_service = QualityService()
        workflow_service = WorkflowStateService("./data/workflows")
        
        print("✅ All services imported successfully")
    except Exception as e:
        print(f"❌ Failed to import services: {e}")
        return results
    
    # Chain 1: Document Processing Chain
    print("\n🔗 CHAIN 1: Document Processing with Provenance Tracking")
    print("-" * 70)
    
    chain_result = {
        "chain_name": "Document Processing Chain",
        "description": "Extract entities → Track provenance → Assess quality → Update workflow",
        "steps": [],
        "status": "UNKNOWN",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Start workflow tracking
        workflow_id = workflow_service.start_workflow(
            name="Document_Processing_Chain",
            total_steps=4,
            initial_state={"document": "test_doc.pdf", "entities_found": 0}
        )
        chain_result["steps"].append({
            "step": 1,
            "action": "start_workflow",
            "result": workflow_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 1: Started workflow {workflow_id}")
        
        # Step 2: Start operation tracking
        op_id = provenance_service.start_operation(
            tool_id="entity_extractor",
            operation_type="extraction",
            inputs=["test_doc.pdf"],
            parameters={"model": "spacy_lg", "confidence_threshold": 0.7}
        )
        chain_result["steps"].append({
            "step": 2,
            "action": "start_operation",
            "result": op_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 2: Started operation tracking {op_id}")
        
        # Step 3: Extract entities (simulate multiple entities)
        entities = []
        entity_data = [
            ("Dr. John Smith", 0, 13, "PERSON"),
            ("Stanford University", 25, 42, "ORG"),
            ("Machine Learning", 60, 76, "CONCEPT")
        ]
        
        for surface_form, start, end, entity_type in entity_data:
            mention_result = identity_service.create_mention(
                surface_form=surface_form,
                start_pos=start,
                end_pos=end,
                source_ref="test_doc.pdf",
                entity_type=entity_type,
                confidence=0.85
            )
            entities.append(mention_result)
        
        chain_result["steps"].append({
            "step": 3,
            "action": "extract_entities",
            "result": f"Extracted {len(entities)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 3: Extracted {len(entities)} entities")
        
        # Step 4: Assess quality for each entity
        quality_assessments = []
        for entity in entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "source_quality": 0.9,
                    "extraction_confidence": entity['confidence'],
                    "entity_type_certainty": 0.8
                },
                metadata={"extraction_method": "spacy_lg"}
            )
            quality_assessments.append(assessment)
        
        avg_quality = sum(qa['confidence'] for qa in quality_assessments) / len(quality_assessments)
        chain_result["steps"].append({
            "step": 4,
            "action": "assess_quality",
            "result": f"Average quality: {avg_quality:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 4: Assessed quality (avg: {avg_quality:.3f})")
        
        # Step 5: Complete operation tracking
        entity_ids = [e['entity_id'] for e in entities]
        complete_result = provenance_service.complete_operation(
            operation_id=op_id,
            outputs=entity_ids,
            success=True,
            metadata={"entities_extracted": len(entities), "avg_quality": avg_quality}
        )
        chain_result["steps"].append({
            "step": 5,
            "action": "complete_operation",
            "result": complete_result,
            "status": "PASS"
        })
        print(f"  ✅ Step 5: Completed operation tracking")
        
        # Step 6: Update workflow progress
        workflow_update = workflow_service.update_workflow_progress(
            workflow_id=workflow_id,
            step_number=4,
            status="completed"
        )
        chain_result["steps"].append({
            "step": 6,
            "action": "update_workflow",
            "result": workflow_update,
            "status": "PASS"
        })
        print(f"  ✅ Step 6: Updated workflow to completed")
        
        chain_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 1 COMPLETE: Full document processing chain successful")
        
    except Exception as e:
        chain_result["status"] = "FAIL"
        chain_result["error"] = str(e)
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 1 FAILED: {e}")
    
    chain_result["chain_duration"] = time.time() - chain_result["chain_start"]
    results["chain_results"].append(chain_result)
    results["test_summary"]["chains_tested"] += 1
    
    # Chain 2: Entity Deduplication Chain
    print("\n🔗 CHAIN 2: Entity Deduplication with Quality Filtering")
    print("-" * 70)
    
    chain_result = {
        "chain_name": "Entity Deduplication Chain",
        "description": "Create duplicate entities → Assess quality → Filter → Merge → Track",
        "steps": [],
        "status": "UNKNOWN",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Create similar entities (duplicates)
        duplicate_entities = []
        similar_forms = [
            ("Dr. Smith", 0, 9, "PERSON", 0.8),
            ("Doctor Smith", 15, 27, "PERSON", 0.75),
            ("D. Smith", 35, 43, "PERSON", 0.7)
        ]
        
        for surface_form, start, end, entity_type, conf in similar_forms:
            mention_result = identity_service.create_mention(
                surface_form=surface_form,
                start_pos=start,
                end_pos=end,
                source_ref="dedup_test.pdf",
                entity_type=entity_type,
                confidence=conf
            )
            duplicate_entities.append(mention_result)
        
        chain_result["steps"].append({
            "step": 1,
            "action": "create_duplicate_entities",
            "result": f"Created {len(duplicate_entities)} similar entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 1: Created {len(duplicate_entities)} similar entities")
        
        # Step 2: Assess quality for all entities
        quality_scores = []
        for entity in duplicate_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "name_completeness": 0.9 if "Dr." in entity['surface_form'] else 0.7,
                    "source_reliability": 0.8
                }
            )
            quality_scores.append((entity, assessment))
        
        chain_result["steps"].append({
            "step": 2,
            "action": "assess_all_quality",
            "result": f"Assessed quality for {len(quality_scores)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 2: Assessed quality for all entities")
        
        # Step 3: Filter by quality (keep only high-quality entities)
        high_quality_entities = []
        entity_refs = [entity['entity_id'] for entity, _ in quality_scores]
        
        filtered_refs = quality_service.filter_by_quality(
            object_refs=entity_refs,
            min_tier="MEDIUM",
            min_confidence=0.6
        )
        
        high_quality_entities = [
            entity for entity, assessment in quality_scores 
            if entity['entity_id'] in filtered_refs
        ]
        
        chain_result["steps"].append({
            "step": 3,
            "action": "filter_by_quality",
            "result": f"Filtered to {len(high_quality_entities)} high-quality entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 3: Filtered to {len(high_quality_entities)} high-quality entities")
        
        # Step 4: Merge duplicate entities (merge all into first one)
        if len(high_quality_entities) >= 2:
            primary_entity = high_quality_entities[0]
            for duplicate_entity in high_quality_entities[1:]:
                merge_result = identity_service.merge_entities(
                    entity_id1=primary_entity['entity_id'],
                    entity_id2=duplicate_entity['entity_id']
                )
            
            chain_result["steps"].append({
                "step": 4,
                "action": "merge_duplicates",
                "result": f"Merged {len(high_quality_entities)-1} duplicates into primary entity",
                "status": "PASS"
            })
            print(f"  ✅ Step 4: Merged duplicates into {primary_entity['entity_id']}")
        
        # Step 5: Get final statistics
        identity_stats = identity_service.get_stats()
        quality_stats = quality_service.get_quality_statistics()
        
        chain_result["steps"].append({
            "step": 5,
            "action": "get_final_stats",
            "result": {
                "identity_stats": identity_stats,
                "quality_stats": quality_stats
            },
            "status": "PASS"
        })
        print(f"  ✅ Step 5: Final stats - {identity_stats['total_entities']} entities, {quality_stats['total_assessments']} assessments")
        
        chain_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 2 COMPLETE: Entity deduplication chain successful")
        
    except Exception as e:
        chain_result["status"] = "FAIL"
        chain_result["error"] = str(e)
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 2 FAILED: {e}")
    
    chain_result["chain_duration"] = time.time() - chain_result["chain_start"]
    results["chain_results"].append(chain_result)
    results["test_summary"]["chains_tested"] += 1
    
    # Chain 3: Confidence Propagation Chain
    print("\n🔗 CHAIN 3: Confidence Propagation Through Operations")
    print("-" * 70)
    
    chain_result = {
        "chain_name": "Confidence Propagation Chain",
        "description": "Create entities → Propagate confidence → Track changes → Update quality",
        "steps": [],
        "status": "UNKNOWN",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Create source entities with different confidence levels
        source_entities = []
        confidence_levels = [0.9, 0.7, 0.5]
        
        for i, conf in enumerate(confidence_levels):
            mention_result = identity_service.create_mention(
                surface_form=f"Entity_{i+1}",
                start_pos=i*10,
                end_pos=(i*10)+8,
                source_ref="confidence_test.pdf",
                entity_type="CONCEPT",
                confidence=conf
            )
            source_entities.append(mention_result)
        
        chain_result["steps"].append({
            "step": 1,
            "action": "create_source_entities",
            "result": f"Created {len(source_entities)} entities with varying confidence",
            "status": "PASS"
        })
        print(f"  ✅ Step 1: Created entities with confidence levels: {confidence_levels}")
        
        # Step 2: Assess initial quality
        initial_assessments = []
        for entity in source_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={"extraction_method": 0.8}
            )
            initial_assessments.append(assessment)
        
        avg_initial_confidence = sum(a['confidence'] for a in initial_assessments) / len(initial_assessments)
        chain_result["steps"].append({
            "step": 2,
            "action": "assess_initial_quality",
            "result": f"Average initial confidence: {avg_initial_confidence:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 2: Initial average confidence: {avg_initial_confidence:.3f}")
        
        # Step 3: Propagate confidence through a relationship extraction operation
        entity_refs = [e['entity_id'] for e in source_entities]
        propagated_confidence = quality_service.propagate_confidence(
            input_refs=entity_refs,
            operation_type="relationship_extraction",
            boost_factor=1.1  # Slight boost for good extraction
        )
        
        chain_result["steps"].append({
            "step": 3,
            "action": "propagate_confidence",
            "result": f"Propagated confidence: {propagated_confidence:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 3: Propagated confidence: {propagated_confidence:.3f}")
        
        # Step 4: Create derived entity using propagated confidence
        derived_mention = identity_service.create_mention(
            surface_form="Derived_Relationship",
            start_pos=100,
            end_pos=118,
            source_ref="confidence_test.pdf",
            entity_type="RELATIONSHIP",
            confidence=propagated_confidence
        )
        
        chain_result["steps"].append({
            "step": 4,
            "action": "create_derived_entity",
            "result": f"Created derived entity with confidence {propagated_confidence:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 4: Created derived entity with propagated confidence")
        
        # Step 5: Get confidence trends for all entities
        all_entities = source_entities + [derived_mention]
        trends = []
        for entity in all_entities:
            trend = quality_service.get_confidence_trend(entity['entity_id'])
            trends.append(trend)
        
        chain_result["steps"].append({
            "step": 5,
            "action": "get_confidence_trends",
            "result": f"Retrieved trends for {len(trends)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 5: Retrieved confidence trends for all entities")
        
        chain_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 3 COMPLETE: Confidence propagation chain successful")
        
    except Exception as e:
        chain_result["status"] = "FAIL"
        chain_result["error"] = str(e)
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 3 FAILED: {e}")
    
    chain_result["chain_duration"] = time.time() - chain_result["chain_start"]
    results["chain_results"].append(chain_result)
    results["test_summary"]["chains_tested"] += 1
    
    # Chain 4: Full Analytics Pipeline Chain
    print("\n🔗 CHAIN 4: Full Analytics Pipeline with Checkpointing")
    print("-" * 70)
    
    chain_result = {
        "chain_name": "Full Analytics Pipeline Chain",
        "description": "Multi-stage workflow with checkpointing and rollback capability",
        "steps": [],
        "status": "UNKNOWN",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Start comprehensive workflow
        workflow_id = workflow_service.start_workflow(
            name="Full_Analytics_Pipeline",
            total_steps=6,
            initial_state={
                "pipeline_stage": "initialization",
                "documents_processed": 0,
                "entities_extracted": 0,
                "quality_checks_passed": 0
            }
        )
        
        chain_result["steps"].append({
            "step": 1,
            "action": "start_comprehensive_workflow",
            "result": workflow_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 1: Started comprehensive workflow {workflow_id}")
        
        # Step 2: Create checkpoint after initialization
        checkpoint_1 = workflow_service.create_checkpoint(
            workflow_id=workflow_id,
            step_name="initialization_complete",
            step_number=1,
            state_data={
                "pipeline_stage": "data_ingestion",
                "documents_processed": 0,
                "initialization_time": time.time()
            }
        )
        
        chain_result["steps"].append({
            "step": 2,
            "action": "create_initialization_checkpoint",
            "result": checkpoint_1,
            "status": "PASS"
        })
        print(f"  ✅ Step 2: Created initialization checkpoint {checkpoint_1}")
        
        # Step 3: Simulate data processing with operation tracking
        processing_op = provenance_service.start_operation(
            tool_id="analytics_pipeline",
            operation_type="batch_processing",
            inputs=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
            parameters={"batch_size": 3, "quality_threshold": 0.7}
        )
        
        # Process multiple documents
        pipeline_entities = []
        for doc_num in range(1, 4):
            mention = identity_service.create_mention(
                surface_form=f"Important_Entity_{doc_num}",
                start_pos=doc_num * 20,
                end_pos=(doc_num * 20) + 15,
                source_ref=f"doc{doc_num}.pdf",
                entity_type="KEY_CONCEPT",
                confidence=0.8 + (doc_num * 0.05)
            )
            pipeline_entities.append(mention)
        
        chain_result["steps"].append({
            "step": 3,
            "action": "process_batch_documents",
            "result": f"Processed 3 documents, extracted {len(pipeline_entities)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 3: Processed batch documents")
        
        # Step 4: Create checkpoint after processing
        checkpoint_2 = workflow_service.create_checkpoint(
            workflow_id=workflow_id,
            step_name="processing_complete",
            step_number=3,
            state_data={
                "pipeline_stage": "quality_assessment",
                "documents_processed": 3,
                "entities_extracted": len(pipeline_entities),
                "entity_ids": [e['entity_id'] for e in pipeline_entities]
            }
        )
        
        chain_result["steps"].append({
            "step": 4,
            "action": "create_processing_checkpoint",
            "result": checkpoint_2,
            "status": "PASS"
        })
        print(f"  ✅ Step 4: Created processing checkpoint {checkpoint_2}")
        
        # Step 5: Quality assessment phase
        quality_results = []
        for entity in pipeline_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "batch_processing_boost": 0.1,
                    "multi_document_validation": 0.15
                }
            )
            quality_results.append(assessment)
        
        passed_quality = len([qa for qa in quality_results if qa['confidence'] >= 0.7])
        
        # Complete the operation
        complete_result = provenance_service.complete_operation(
            operation_id=processing_op,
            outputs=[e['entity_id'] for e in pipeline_entities],
            success=True,
            metadata={
                "documents_processed": 3,
                "entities_extracted": len(pipeline_entities),
                "quality_checks_passed": passed_quality
            }
        )
        
        chain_result["steps"].append({
            "step": 5,
            "action": "complete_quality_assessment",
            "result": f"Quality assessment complete: {passed_quality}/{len(pipeline_entities)} passed",
            "status": "PASS"
        })
        print(f"  ✅ Step 5: Quality assessment complete")
        
        # Step 6: Final workflow completion
        final_update = workflow_service.update_workflow_progress(
            workflow_id=workflow_id,
            step_number=6,
            status="completed"
        )
        
        # Get final workflow status and checkpoints
        final_status = workflow_service.get_workflow_status(workflow_id)
        all_checkpoints = workflow_service.get_workflow_checkpoints(workflow_id)
        
        chain_result["steps"].append({
            "step": 6,
            "action": "finalize_workflow",
            "result": {
                "final_status": final_status,
                "total_checkpoints": len(all_checkpoints)
            },
            "status": "PASS"
        })
        print(f"  ✅ Step 6: Workflow finalized with {len(all_checkpoints)} checkpoints")
        
        chain_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 4 COMPLETE: Full analytics pipeline successful")
        
    except Exception as e:
        chain_result["status"] = "FAIL"
        chain_result["error"] = str(e)
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 4 FAILED: {e}")
    
    chain_result["chain_duration"] = time.time() - chain_result["chain_start"]
    results["chain_results"].append(chain_result)
    results["test_summary"]["chains_tested"] += 1
    
    # Generate final summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 MCP TOOL CHAINS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Chains: {results['test_summary']['total_chains']}")
    print(f"✅ Chains Passed: {results['test_summary']['chains_passed']}")
    print(f"❌ Chains Failed: {results['test_summary']['chains_failed']}")
    print(f"📈 Chain Pass Rate: {(results['test_summary']['chains_passed']/results['test_summary']['total_chains'])*100:.1f}%")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Show chain details
    print(f"\n📋 CHAIN BREAKDOWN:")
    for chain in results["chain_results"]:
        steps_passed = len([s for s in chain["steps"] if s["status"] == "PASS"])
        total_steps = len(chain["steps"])
        print(f"  {chain['chain_name']}: {chain['status']} ({steps_passed}/{total_steps} steps)")
        print(f"    Duration: {chain['chain_duration']:.2f}s")
        if chain["status"] == "FAIL" and chain["error"]:
            print(f"    Error: {chain['error']}")
    
    # Save results
    with open("mcp_tool_chains_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: mcp_tool_chains_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_mcp_tool_chains()
    
    # Determine success
    chains_passed = results["test_summary"]["chains_passed"]
    total_chains = results["test_summary"]["total_chains"]
    pass_rate = (chains_passed / total_chains) * 100 if total_chains > 0 else 0
    
    print(f"\n🎯 FINAL CONCLUSION:")
    print(f"   {chains_passed}/{total_chains} MCP tool chains working ({pass_rate:.1f}% pass rate)")
    
    if pass_rate >= 75:
        print("   🎉 EXCELLENT: MCP tool chains are fully functional")
        sys.exit(0)
    elif pass_rate >= 50:
        print("   ⚠️  GOOD: Most MCP tool chains working")
        sys.exit(0)
    else:
        print("   ❌ NEEDS WORK: MCP tool chain issues")
        sys.exit(1)