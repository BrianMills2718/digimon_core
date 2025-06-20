#!/usr/bin/env python3
"""
DEBUG ENTITY DEDUPLICATION CHAIN
Isolate and fix the 'surface_form' error with detailed logging
"""

import sys
import json
import time
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def debug_entity_deduplication_chain():
    """Debug the Entity Deduplication Chain with detailed logging"""
    
    print("🔍 DEBUGGING ENTITY DEDUPLICATION CHAIN")
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
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    # Step 1: Create similar entities (duplicates)
    print("\n📍 Step 1: Creating duplicate entities...")
    duplicate_entities = []
    similar_forms = [
        ("Dr. Smith", 0, 9, "PERSON", 0.8),
        ("Doctor Smith", 15, 27, "PERSON", 0.75),
        ("D. Smith", 35, 43, "PERSON", 0.7)
    ]
    
    try:
        for i, (surface_form, start, end, entity_type, conf) in enumerate(similar_forms):
            print(f"  Creating entity {i+1}: surface_form='{surface_form}', start={start}, end={end}, type={entity_type}, conf={conf}")
            
            mention_result = identity_service.create_mention(
                surface_form=surface_form,
                start_pos=start,
                end_pos=end,
                source_ref="dedup_test.pdf",
                entity_type=entity_type,
                confidence=conf
            )
            
            print(f"  ✅ Entity {i+1} created: {mention_result}")
            duplicate_entities.append(mention_result)
        
        print(f"✅ Step 1 SUCCESS: Created {len(duplicate_entities)} entities")
        
    except Exception as e:
        print(f"❌ Step 1 FAILED: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    # Step 2: Assess quality for all entities
    print("\n📍 Step 2: Assessing quality...")
    quality_scores = []
    
    try:
        for i, entity in enumerate(duplicate_entities):
            print(f"  Assessing entity {i+1}: entity_id={entity.get('entity_id')}")
            print(f"  Entity data: {entity}")
            
            # Check if entity has surface_form attribute
            if 'surface_form' in entity:
                surface_form = entity['surface_form']
                print(f"  Using surface_form from entity: '{surface_form}'")
            elif hasattr(entity, 'surface_form'):
                surface_form = entity.surface_form
                print(f"  Using surface_form attribute: '{surface_form}'")
            else:
                print(f"  ⚠️  Entity missing surface_form, using default")
                surface_form = "Unknown"
            
            assessment = quality_service.assess_confidence(
                object_ref=entity['entity_id'],
                base_confidence=entity['confidence'],
                factors={
                    "name_completeness": 0.9 if "Dr." in surface_form else 0.7,
                    "source_reliability": 0.8
                }
            )
            
            print(f"  ✅ Assessment {i+1} complete: {assessment}")
            quality_scores.append((entity, assessment))
        
        print(f"✅ Step 2 SUCCESS: Assessed {len(quality_scores)} entities")
        
    except Exception as e:
        print(f"❌ Step 2 FAILED: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        
        # Print detailed debugging info
        print("\n🔍 DEBUGGING INFO:")
        print(f"Current entity being processed: {entity if 'entity' in locals() else 'None'}")
        print(f"Entity keys: {list(entity.keys()) if 'entity' in locals() and hasattr(entity, 'keys') else 'N/A'}")
        print(f"Entity type: {type(entity) if 'entity' in locals() else 'N/A'}")
        
        return False
    
    # Step 3: Filter by quality
    print("\n📍 Step 3: Filtering by quality...")
    
    try:
        entity_refs = [entity['entity_id'] for entity, _ in quality_scores]
        print(f"  Entity refs to filter: {entity_refs}")
        
        filtered_refs = quality_service.filter_by_quality(
            object_refs=entity_refs,
            min_tier="MEDIUM",
            min_confidence=0.6
        )
        
        print(f"  Filtered refs: {filtered_refs}")
        
        high_quality_entities = [
            entity for entity, assessment in quality_scores 
            if entity['entity_id'] in filtered_refs
        ]
        
        print(f"✅ Step 3 SUCCESS: Filtered to {len(high_quality_entities)} high-quality entities")
        
    except Exception as e:
        print(f"❌ Step 3 FAILED: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    # Step 4: Merge duplicate entities
    print("\n📍 Step 4: Merging duplicates...")
    
    try:
        if len(high_quality_entities) >= 2:
            primary_entity = high_quality_entities[0]
            merge_count = 0
            for duplicate_entity in high_quality_entities[1:]:
                print(f"  Merging {duplicate_entity['entity_id']} into {primary_entity['entity_id']}")
                
                merge_result = identity_service.merge_entities(
                    entity_id1=primary_entity['entity_id'],
                    entity_id2=duplicate_entity['entity_id']
                )
                print(f"  Merge result: {merge_result}")
                merge_count += 1
            
            print(f"✅ Step 4 SUCCESS: Merged {merge_count} duplicates")
        else:
            print(f"✅ Step 4 SUCCESS: No duplicates to merge (only {len(high_quality_entities)} high-quality entities)")
        
    except Exception as e:
        print(f"❌ Step 4 FAILED: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    # Step 5: Get final statistics
    print("\n📍 Step 5: Getting final statistics...")
    
    try:
        identity_stats = identity_service.get_stats()
        quality_stats = quality_service.get_quality_statistics()
        
        print(f"  Identity stats: {identity_stats}")
        print(f"  Quality stats: {quality_stats}")
        
        print("✅ Step 5 SUCCESS: Final stats retrieved")
        
    except Exception as e:
        print(f"❌ Step 5 FAILED: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    print("\n🎉 ENTITY DEDUPLICATION CHAIN: ALL STEPS COMPLETED SUCCESSFULLY")
    return True

if __name__ == "__main__":
    success = debug_entity_deduplication_chain()
    if success:
        print("\n✅ DEBUG SUCCESS: Chain completed without errors")
        sys.exit(0)
    else:
        print("\n❌ DEBUG FAILED: Chain encountered errors")
        sys.exit(1)