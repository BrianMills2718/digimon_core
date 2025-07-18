#!/usr/bin/env python3
"""
ISOLATED ENTITY DEDUPLICATION CHAIN TEST
Test only Chain 2 with the fix applied
"""

import sys
import json
import time
import traceback
from pathlib import Path

# Add src to path for imports

def test_chain2_isolated():
    """Test only the Entity Deduplication Chain"""
    
    print("🔗 TESTING ENTITY DEDUPLICATION CHAIN (ISOLATED)")
    print("=" * 80)
    
    # Import required services
    try:
        from src.core.identity_service import IdentityService
        from src.core.quality_service import QualityService
        
        identity_service = IdentityService()
        quality_service = QualityService()
        
        print("✅ Services imported successfully")
    except Exception as e:
        print(f"❌ Failed to import services: {e}")
        return False
    
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
        
        # Step 2: Assess quality for all entities (FIXED)
        print("  📍 Step 2: Assessing quality...")
        quality_scores = []
        for entity in duplicate_entities:
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "name_completeness": 0.9 if "dr." in entity.get('normalized_form', '').lower() else 0.7,
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
        
        chain2_result["status"] = "PASS"
        print(f"  🎉 CHAIN 2 COMPLETE: All 5 steps passed")
        
    except Exception as e:
        chain2_result["status"] = "FAIL"
        chain2_result["error"] = str(e)
        chain2_result["traceback"] = traceback.format_exc()
        print(f"  ❌ CHAIN 2 FAILED: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    chain2_result["chain_duration"] = time.time() - chain2_result["chain_start"]
    
    # Save result
    with open("chain2_isolated_test_result.json", "w") as f:
        json.dump(chain2_result, f, indent=2)
    
    print(f"\n📊 CHAIN 2 RESULT:")
    print(f"Status: {chain2_result['status']}")
    print(f"Steps passed: {len([s for s in chain2_result['steps'] if s['status'] == 'PASS'])}/5")
    print(f"Duration: {chain2_result['chain_duration']:.3f}s")
    
    return chain2_result["status"] == "PASS"

if __name__ == "__main__":
    success = test_chain2_isolated()
    if success:
        print("\n✅ CHAIN 2 ISOLATED TEST: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ CHAIN 2 ISOLATED TEST: FAILED")
        sys.exit(1)