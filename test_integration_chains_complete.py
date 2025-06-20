#!/usr/bin/env python3
"""
COMPLETE INTEGRATION CHAINS TESTING
Test all 4 integration chains with full error reporting
"""

import sys
import json
import time
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_all_integration_chains():
    """Test all 4 integration chains with detailed reporting"""
    
    print("🔗 TESTING ALL INTEGRATION CHAINS")
    print("=" * 80)
    
    results = {
        "test_summary": {
            "total_chains": 4,
            "chains_passed": 0,
            "chains_failed": 0,
            "start_time": time.time()
        },
        "chain_results": [],
        "raw_logs": []
    }
    
    # Import required services
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
        results["raw_logs"].append("All services imported successfully")
    except Exception as e:
        print(f"❌ Failed to import services: {e}")
        results["raw_logs"].append(f"Failed to import services: {str(e)}")
        return results
    
    # Chain 1: Document Processing Chain
    print("\n🔗 CHAIN 1: Document Processing with Provenance Tracking")
    print("-" * 70)
    
    chain1_result = {
        "chain_name": "Document Processing Chain",
        "description": "Extract entities → Track provenance → Assess quality → Update workflow",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Start workflow tracking
        print("  📍 Step 1: Starting workflow...")
        workflow_id = workflow_service.start_workflow(
            name="Document_Processing_Chain_Test",
            total_steps=6,
            initial_state={"document": "test_doc.pdf", "entities_found": 0}
        )
        chain1_result["steps"].append({
            "step": 1,
            "action": "start_workflow",
            "result": workflow_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 1 PASS: Started workflow {workflow_id}")
        results["raw_logs"].append(f"Chain 1 Step 1 PASS: workflow_id={workflow_id}")
        
        # Step 2: Start operation tracking
        print("  📍 Step 2: Starting operation tracking...")
        op_id = provenance_service.start_operation(
            tool_id="entity_extractor",
            operation_type="extraction",
            inputs=["test_doc.pdf"],
            parameters={"model": "spacy_lg", "confidence_threshold": 0.7}
        )
        chain1_result["steps"].append({
            "step": 2,
            "action": "start_operation",
            "result": op_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 2 PASS: Started operation {op_id}")
        results["raw_logs"].append(f"Chain 1 Step 2 PASS: operation_id={op_id}")
        
        # Step 3: Extract entities
        print("  📍 Step 3: Extracting entities...")
        entities = []
        entity_data = [
            ("Dr. John Smith", 0, 13, "PERSON"),
            ("Stanford University", 25, 42, "ORG"),
            ("Machine Learning", 60, 76, "CONCEPT"),
            ("Natural Language Processing", 100, 127, "CONCEPT")
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
        
        chain1_result["steps"].append({
            "step": 3,
            "action": "extract_entities",
            "result": f"Extracted {len(entities)} entities",
            "entities": entities,
            "status": "PASS"
        })
        print(f"  ✅ Step 3 PASS: Extracted {len(entities)} entities")
        results["raw_logs"].append(f"Chain 1 Step 3 PASS: Extracted {len(entities)} entities: {[e['entity_id'] for e in entities]}")
        
        # Step 4: Assess quality for each entity
        print("  📍 Step 4: Assessing quality...")
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
        chain1_result["steps"].append({
            "step": 4,
            "action": "assess_quality",
            "result": f"Average quality: {avg_quality:.3f}",
            "assessments": quality_assessments,
            "status": "PASS"
        })
        print(f"  ✅ Step 4 PASS: Assessed quality (avg: {avg_quality:.3f})")
        results["raw_logs"].append(f"Chain 1 Step 4 PASS: Average quality={avg_quality:.3f}")
        
        # Step 5: Complete operation tracking
        print("  📍 Step 5: Completing operation...")
        entity_ids = [e['entity_id'] for e in entities]
        complete_result = provenance_service.complete_operation(
            operation_id=op_id,
            outputs=entity_ids,
            success=True,
            metadata={"entities_extracted": len(entities), "avg_quality": avg_quality}
        )
        chain1_result["steps"].append({
            "step": 5,
            "action": "complete_operation",
            "result": complete_result,
            "status": "PASS"
        })
        print(f"  ✅ Step 5 PASS: Completed operation")
        results["raw_logs"].append(f"Chain 1 Step 5 PASS: Operation completed with {complete_result}")
        
        # Step 6: Update workflow progress
        print("  📍 Step 6: Updating workflow...")
        workflow_update = workflow_service.update_workflow_progress(
            workflow_id=workflow_id,
            step_number=6,
            status="completed"
        )
        chain1_result["steps"].append({
            "step": 6,
            "action": "update_workflow",
            "result": workflow_update,
            "status": "PASS"
        })
        print(f"  ✅ Step 6 PASS: Updated workflow to completed")
        results["raw_logs"].append(f"Chain 1 Step 6 PASS: Workflow updated to completed")
        
        chain1_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 1 COMPLETE: All 6 steps passed")
        
    except Exception as e:
        chain1_result["status"] = "FAIL"
        chain1_result["error"] = str(e)
        chain1_result["traceback"] = traceback.format_exc()
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 1 FAILED: {str(e)}")
        results["raw_logs"].append(f"Chain 1 FAILED: {str(e)}\n{traceback.format_exc()}")
    
    chain1_result["chain_duration"] = time.time() - chain1_result["chain_start"]
    results["chain_results"].append(chain1_result)
    
    # Chain 2: Entity Deduplication Chain
    print("\n🔗 CHAIN 2: Entity Deduplication with Quality Filtering")
    print("-" * 70)
    
    chain2_result = {
        "chain_name": "Entity Deduplication Chain",
        "description": "Create duplicate entities → Assess quality → Filter → Merge → Track",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Create similar entities (duplicates)
        print("  📍 Step 1: Creating duplicate entities...")
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
        
        chain2_result["steps"].append({
            "step": 1,
            "action": "create_duplicate_entities",
            "result": f"Created {len(duplicate_entities)} similar entities",
            "entities": duplicate_entities,
            "status": "PASS"
        })
        print(f"  ✅ Step 1 PASS: Created {len(duplicate_entities)} similar entities")
        results["raw_logs"].append(f"Chain 2 Step 1 PASS: Created {len(duplicate_entities)} entities")
        
        # Step 2: Assess quality for all entities
        print("  📍 Step 2: Assessing quality...")
        quality_scores = []
        for entity in duplicate_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "name_completeness": 0.9 if "Dr." in entity.get('normalized_form', '') else 0.7,
                    "source_reliability": 0.8
                }
            )
            quality_scores.append((entity, assessment))
        
        chain2_result["steps"].append({
            "step": 2,
            "action": "assess_all_quality",
            "result": f"Assessed quality for {len(quality_scores)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 2 PASS: Assessed quality for all entities")
        results["raw_logs"].append(f"Chain 2 Step 2 PASS: Assessed {len(quality_scores)} entities")
        
        # Step 3: Filter by quality
        print("  📍 Step 3: Filtering by quality...")
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
        
        chain2_result["steps"].append({
            "step": 3,
            "action": "filter_by_quality",
            "result": f"Filtered to {len(high_quality_entities)} high-quality entities",
            "filtered_count": len(high_quality_entities),
            "status": "PASS"
        })
        print(f"  ✅ Step 3 PASS: Filtered to {len(high_quality_entities)} high-quality entities")
        results["raw_logs"].append(f"Chain 2 Step 3 PASS: Filtered to {len(high_quality_entities)} entities")
        
        # Step 4: Merge duplicate entities
        print("  📍 Step 4: Merging duplicates...")
        if len(high_quality_entities) >= 2:
            primary_entity = high_quality_entities[0]
            merge_count = 0
            for duplicate_entity in high_quality_entities[1:]:
                merge_result = identity_service.merge_entities(
                    entity_id1=primary_entity['entity_id'],
                    entity_id2=duplicate_entity['entity_id']
                )
                merge_count += 1
            
            chain2_result["steps"].append({
                "step": 4,
                "action": "merge_duplicates",
                "result": f"Merged {merge_count} duplicates into primary entity",
                "primary_entity": primary_entity['entity_id'],
                "status": "PASS"
            })
            print(f"  ✅ Step 4 PASS: Merged {merge_count} duplicates")
            results["raw_logs"].append(f"Chain 2 Step 4 PASS: Merged {merge_count} duplicates")
        else:
            chain2_result["steps"].append({
                "step": 4,
                "action": "merge_duplicates",
                "result": "No duplicates to merge",
                "status": "PASS"
            })
            print(f"  ✅ Step 4 PASS: No duplicates to merge")
        
        # Step 5: Get final statistics
        print("  📍 Step 5: Getting final statistics...")
        identity_stats = identity_service.get_stats()
        quality_stats = quality_service.get_quality_statistics()
        
        chain2_result["steps"].append({
            "step": 5,
            "action": "get_final_stats",
            "result": {
                "identity_stats": identity_stats,
                "quality_stats": quality_stats
            },
            "status": "PASS"
        })
        print(f"  ✅ Step 5 PASS: Final stats retrieved")
        results["raw_logs"].append(f"Chain 2 Step 5 PASS: {identity_stats['total_entities']} entities, {quality_stats['total_assessments']} assessments")
        
        chain2_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 2 COMPLETE: All 5 steps passed")
        
    except Exception as e:
        chain2_result["status"] = "FAIL"
        chain2_result["error"] = str(e)
        chain2_result["traceback"] = traceback.format_exc()
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 2 FAILED: {str(e)}")
        results["raw_logs"].append(f"Chain 2 FAILED: {str(e)}\n{traceback.format_exc()}")
    
    chain2_result["chain_duration"] = time.time() - chain2_result["chain_start"]
    results["chain_results"].append(chain2_result)
    
    # Chain 3: Confidence Propagation Chain
    print("\n🔗 CHAIN 3: Confidence Propagation Through Operations")
    print("-" * 70)
    
    chain3_result = {
        "chain_name": "Confidence Propagation Chain",
        "description": "Create entities → Propagate confidence → Track changes → Update quality",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Create source entities with different confidence levels
        print("  📍 Step 1: Creating source entities...")
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
        
        chain3_result["steps"].append({
            "step": 1,
            "action": "create_source_entities",
            "result": f"Created {len(source_entities)} entities with varying confidence",
            "confidence_levels": confidence_levels,
            "status": "PASS"
        })
        print(f"  ✅ Step 1 PASS: Created entities with confidence levels: {confidence_levels}")
        results["raw_logs"].append(f"Chain 3 Step 1 PASS: Created {len(source_entities)} entities")
        
        # Step 2: Assess initial quality
        print("  📍 Step 2: Assessing initial quality...")
        initial_assessments = []
        for entity in source_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={"extraction_method": 0.8}
            )
            initial_assessments.append(assessment)
        
        avg_initial_confidence = sum(a['confidence'] for a in initial_assessments) / len(initial_assessments)
        chain3_result["steps"].append({
            "step": 2,
            "action": "assess_initial_quality",
            "result": f"Average initial confidence: {avg_initial_confidence:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 2 PASS: Initial average confidence: {avg_initial_confidence:.3f}")
        results["raw_logs"].append(f"Chain 3 Step 2 PASS: Initial confidence={avg_initial_confidence:.3f}")
        
        # Step 3: Propagate confidence through a relationship extraction operation
        print("  📍 Step 3: Propagating confidence...")
        entity_refs = [e['entity_id'] for e in source_entities]
        propagated_confidence = quality_service.propagate_confidence(
            input_refs=entity_refs,
            operation_type="relationship_extraction",
            boost_factor=1.1
        )
        
        chain3_result["steps"].append({
            "step": 3,
            "action": "propagate_confidence",
            "result": f"Propagated confidence: {propagated_confidence:.3f}",
            "status": "PASS"
        })
        print(f"  ✅ Step 3 PASS: Propagated confidence: {propagated_confidence:.3f}")
        results["raw_logs"].append(f"Chain 3 Step 3 PASS: Propagated confidence={propagated_confidence:.3f}")
        
        # Step 4: Create derived entity using propagated confidence
        print("  📍 Step 4: Creating derived entity...")
        derived_mention = identity_service.create_mention(
            surface_form="Derived_Relationship",
            start_pos=100,
            end_pos=118,
            source_ref="confidence_test.pdf",
            entity_type="RELATIONSHIP",
            confidence=propagated_confidence
        )
        
        chain3_result["steps"].append({
            "step": 4,
            "action": "create_derived_entity",
            "result": f"Created derived entity with confidence {propagated_confidence:.3f}",
            "entity_id": derived_mention['entity_id'],
            "status": "PASS"
        })
        print(f"  ✅ Step 4 PASS: Created derived entity with propagated confidence")
        results["raw_logs"].append(f"Chain 3 Step 4 PASS: Created derived entity {derived_mention['entity_id']}")
        
        # Step 5: Get confidence trends
        print("  📍 Step 5: Getting confidence trends...")
        all_entities = source_entities + [derived_mention]
        trends = []
        for entity in all_entities:
            trend = quality_service.get_confidence_trend(entity['entity_id'])
            trends.append(trend)
        
        chain3_result["steps"].append({
            "step": 5,
            "action": "get_confidence_trends",
            "result": f"Retrieved trends for {len(trends)} entities",
            "status": "PASS"
        })
        print(f"  ✅ Step 5 PASS: Retrieved confidence trends for all entities")
        results["raw_logs"].append(f"Chain 3 Step 5 PASS: Retrieved {len(trends)} trends")
        
        chain3_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 3 COMPLETE: All 5 steps passed")
        
    except Exception as e:
        chain3_result["status"] = "FAIL"
        chain3_result["error"] = str(e)
        chain3_result["traceback"] = traceback.format_exc()
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 3 FAILED: {str(e)}")
        results["raw_logs"].append(f"Chain 3 FAILED: {str(e)}\n{traceback.format_exc()}")
    
    chain3_result["chain_duration"] = time.time() - chain3_result["chain_start"]
    results["chain_results"].append(chain3_result)
    
    # Chain 4: Full Analytics Pipeline Chain
    print("\n🔗 CHAIN 4: Full Analytics Pipeline with Checkpointing")
    print("-" * 70)
    
    chain4_result = {
        "chain_name": "Full Analytics Pipeline Chain",
        "description": "Multi-stage workflow with checkpointing and rollback capability",
        "steps": [],
        "status": "RUNNING",
        "error": None,
        "chain_start": time.time()
    }
    
    try:
        # Step 1: Start comprehensive workflow
        print("  📍 Step 1: Starting comprehensive workflow...")
        workflow_id = workflow_service.start_workflow(
            name="Full_Analytics_Pipeline_Test",
            total_steps=6,
            initial_state={
                "pipeline_stage": "initialization",
                "documents_processed": 0,
                "entities_extracted": 0,
                "quality_checks_passed": 0
            }
        )
        
        chain4_result["steps"].append({
            "step": 1,
            "action": "start_comprehensive_workflow",
            "result": workflow_id,
            "status": "PASS"
        })
        print(f"  ✅ Step 1 PASS: Started workflow {workflow_id}")
        results["raw_logs"].append(f"Chain 4 Step 1 PASS: workflow_id={workflow_id}")
        
        # Step 2: Create checkpoint after initialization
        print("  📍 Step 2: Creating initialization checkpoint...")
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
        
        chain4_result["steps"].append({
            "step": 2,
            "action": "create_initialization_checkpoint",
            "result": checkpoint_1,
            "status": "PASS"
        })
        print(f"  ✅ Step 2 PASS: Created checkpoint {checkpoint_1}")
        results["raw_logs"].append(f"Chain 4 Step 2 PASS: checkpoint_id={checkpoint_1}")
        
        # Step 3: Simulate data processing with operation tracking
        print("  📍 Step 3: Processing batch documents...")
        processing_op = provenance_service.start_operation(
            tool_id="analytics_pipeline",
            operation_type="batch_processing",
            inputs=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
            parameters={"batch_size": 3, "quality_threshold": 0.7}
        )
        
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
        
        chain4_result["steps"].append({
            "step": 3,
            "action": "process_batch_documents",
            "result": f"Processed 3 documents, extracted {len(pipeline_entities)} entities",
            "entity_count": len(pipeline_entities),
            "status": "PASS"
        })
        print(f"  ✅ Step 3 PASS: Processed batch documents")
        results["raw_logs"].append(f"Chain 4 Step 3 PASS: Processed 3 docs, {len(pipeline_entities)} entities")
        
        # Step 4: Create checkpoint after processing
        print("  📍 Step 4: Creating processing checkpoint...")
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
        
        chain4_result["steps"].append({
            "step": 4,
            "action": "create_processing_checkpoint",
            "result": checkpoint_2,
            "status": "PASS"
        })
        print(f"  ✅ Step 4 PASS: Created checkpoint {checkpoint_2}")
        results["raw_logs"].append(f"Chain 4 Step 4 PASS: checkpoint_id={checkpoint_2}")
        
        # Step 5: Quality assessment phase
        print("  📍 Step 5: Performing quality assessment...")
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
        
        chain4_result["steps"].append({
            "step": 5,
            "action": "complete_quality_assessment",
            "result": f"Quality assessment complete: {passed_quality}/{len(pipeline_entities)} passed",
            "passed": passed_quality,
            "total": len(pipeline_entities),
            "status": "PASS"
        })
        print(f"  ✅ Step 5 PASS: Quality assessment complete")
        results["raw_logs"].append(f"Chain 4 Step 5 PASS: {passed_quality}/{len(pipeline_entities)} passed quality")
        
        # Step 6: Final workflow completion
        print("  📍 Step 6: Finalizing workflow...")
        final_update = workflow_service.update_workflow_progress(
            workflow_id=workflow_id,
            step_number=6,
            status="completed"
        )
        
        final_status = workflow_service.get_workflow_status(workflow_id)
        all_checkpoints = workflow_service.get_workflow_checkpoints(workflow_id)
        
        chain4_result["steps"].append({
            "step": 6,
            "action": "finalize_workflow",
            "result": {
                "final_status": final_status,
                "total_checkpoints": len(all_checkpoints)
            },
            "status": "PASS"
        })
        print(f"  ✅ Step 6 PASS: Workflow finalized with {len(all_checkpoints)} checkpoints")
        results["raw_logs"].append(f"Chain 4 Step 6 PASS: Workflow completed with {len(all_checkpoints)} checkpoints")
        
        chain4_result["status"] = "PASS"
        results["test_summary"]["chains_passed"] += 1
        print(f"  🎉 CHAIN 4 COMPLETE: All 6 steps passed")
        
    except Exception as e:
        chain4_result["status"] = "FAIL"
        chain4_result["error"] = str(e)
        chain4_result["traceback"] = traceback.format_exc()
        results["test_summary"]["chains_failed"] += 1
        print(f"  ❌ CHAIN 4 FAILED: {str(e)}")
        results["raw_logs"].append(f"Chain 4 FAILED: {str(e)}\n{traceback.format_exc()}")
    
    chain4_result["chain_duration"] = time.time() - chain4_result["chain_start"]
    results["chain_results"].append(chain4_result)
    
    # Generate final summary
    results["test_summary"]["end_time"] = time.time()
    results["test_summary"]["total_execution_time"] = results["test_summary"]["end_time"] - results["test_summary"]["start_time"]
    
    print("\n" + "=" * 80)
    print("📊 INTEGRATION CHAINS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Chains: {results['test_summary']['total_chains']}")
    print(f"✅ Chains Passed: {results['test_summary']['chains_passed']}")
    print(f"❌ Chains Failed: {results['test_summary']['chains_failed']}")
    
    pass_rate = (results['test_summary']['chains_passed'] / results['test_summary']['total_chains']) * 100
    print(f"📈 Chain Pass Rate: {pass_rate:.1f}%")
    print(f"⏱️  Total Time: {results['test_summary']['total_execution_time']:.2f}s")
    
    # Show detailed breakdown
    print(f"\n📋 CHAIN BREAKDOWN:")
    for chain in results["chain_results"]:
        steps_passed = len([s for s in chain["steps"] if s["status"] == "PASS"])
        total_steps = len(chain["steps"])
        print(f"  {chain['chain_name']}: {chain['status']} ({steps_passed}/{total_steps} steps)")
        if chain["status"] == "FAIL":
            print(f"    Error: {chain['error']}")
    
    # Save results
    with open("integration_chains_complete_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: integration_chains_complete_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_all_integration_chains()
    
    # Exit code based on results
    if results["test_summary"]["chains_failed"] > 0:
        print(f"\n❌ FAILURE: {results['test_summary']['chains_failed']} chains failed")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: All {results['test_summary']['total_chains']} chains passed")
        sys.exit(0)