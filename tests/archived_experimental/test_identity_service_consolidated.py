#!/usr/bin/env python3
"""
Test Identity Service (Consolidated Implementation)

Verifies that the unified identity service:
1. Maintains backward compatibility with minimal implementation
2. Correctly implements optional features (embeddings, persistence)
3. Handles configuration properly
"""

import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports

from core.identity_service import IdentityService


def test_backward_compatibility():
    """Test that consolidated service works like minimal version by default."""
    print("🧪 Testing Backward Compatibility...")
    
    # Create service with no configuration (should work like minimal)
    service = IdentityService()
    
    # Test 1: Create mention
    result = service.create_mention(
        surface_form="Elon Musk",
        start_pos=0,
        end_pos=9,
        source_ref="test_doc_1",
        confidence=0.9
    )
    
    assert result["status"] == "success", "Failed to create mention"
    mention_id = result["mention_id"]
    entity_id = result["entity_id"]
    print(f"✅ Created mention: {mention_id} -> entity: {entity_id}")
    
    # Test 2: Create another mention of same entity
    result2 = service.create_mention(
        surface_form="elon musk",  # Different case
        start_pos=50,
        end_pos=59,
        source_ref="test_doc_2",
        confidence=0.8
    )
    
    assert result2["status"] == "success", "Failed to create second mention"
    assert result2["entity_id"] == entity_id, "Should link to same entity"
    print("✅ Second mention linked to same entity")
    
    # Test 3: Get entity by mention
    entity_info = service.get_entity_by_mention(mention_id)
    assert entity_info is not None, "Failed to get entity by mention"
    assert entity_info["entity_id"] == entity_id
    assert entity_info["mention_count"] == 2
    print("✅ Retrieved entity by mention")
    
    # Test 4: Get mentions for entity
    mentions = service.get_mentions_for_entity(entity_id)
    assert len(mentions) == 2, "Should have 2 mentions"
    print("✅ Retrieved mentions for entity")
    
    # Test 5: Create different entity
    result3 = service.create_mention(
        surface_form="SpaceX",
        start_pos=100,
        end_pos=106,
        source_ref="test_doc_1",
        confidence=0.95
    )
    
    assert result3["entity_id"] != entity_id, "Should create new entity"
    entity_id2 = result3["entity_id"]
    print("✅ Created different entity")
    
    # Test 6: Merge entities
    merge_result = service.merge_entities(entity_id, entity_id2)
    assert merge_result["status"] == "success", "Failed to merge entities"
    assert merge_result["total_mentions"] == 3
    print("✅ Merged entities successfully")
    
    # Test 7: Get stats
    stats = service.get_stats()
    assert stats["total_mentions"] == 3
    assert stats["total_entities"] == 1  # After merge
    assert stats["unique_surface_forms"] == 2  # "elon musk" and "spacex"
    print("✅ Stats correct after operations")
    
    print("\n✅ BACKWARD COMPATIBILITY: PASSED")
    return True


def test_persistence_feature():
    """Test persistence feature of consolidated service."""
    print("\n🧪 Testing Persistence Feature...")
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_identity.db")
        
        # Create service with persistence
        service1 = IdentityService(persistence_path=db_path)
        
        # Create some data
        result1 = service1.create_mention(
            surface_form="Tesla Motors",
            start_pos=0,
            end_pos=12,
            source_ref="doc1",
            confidence=0.9
        )
        entity_id = result1["entity_id"]
        
        result2 = service1.create_mention(
            surface_form="tesla motors",  # Same entity, different case
            start_pos=50,
            end_pos=62,
            source_ref="doc2",
            confidence=0.85
        )
        
        # Close the service
        service1.close()
        
        # Create new service instance with same database
        service2 = IdentityService(persistence_path=db_path)
        
        # Verify data was persisted
        stats = service2.get_stats()
        print(f"Stats after reload: {stats}")
        assert stats["total_mentions"] == 2, f"Mentions not persisted: {stats['total_mentions']} != 2"
        assert stats["total_entities"] == 1, f"Entities not persisted: {stats['total_entities']} != 1"
        print("✅ Data persisted correctly")
        
        # Verify we can still query the data
        entity_info = service2.get_entity_by_mention(result1["mention_id"])
        assert entity_info is not None, "Failed to retrieve persisted entity"
        assert entity_info["entity_id"] == entity_id
        print("✅ Can query persisted data")
        
        # Add more data to verify continuation works
        result3 = service2.create_mention(
            surface_form="Model S",
            start_pos=100,
            end_pos=107,
            source_ref="doc3",
            confidence=0.8
        )
        
        final_stats = service2.get_stats()
        assert final_stats["total_mentions"] == 3
        assert final_stats["persistence_enabled"] == True
        assert final_stats["database_path"] == db_path
        print("✅ Can add to persisted data")
        
        service2.close()
    
    print("\n✅ PERSISTENCE FEATURE: PASSED")
    return True


def test_embeddings_simulation():
    """Test embedding feature configuration (without actual OpenAI calls)."""
    print("\n🧪 Testing Embeddings Configuration...")
    
    # Create service with embeddings enabled
    # Note: This won't actually call OpenAI without API key
    service = IdentityService(
        use_embeddings=True,
        similarity_threshold=0.85,
        related_threshold=0.70
    )
    
    # Verify configuration
    assert service.use_embeddings == True
    assert service.similarity_threshold == 0.85
    assert service.related_threshold == 0.70
    print("✅ Embeddings configuration set correctly")
    
    # Create mentions (will fall back to exact matching without API key)
    result = service.create_mention(
        surface_form="Artificial Intelligence",
        start_pos=0,
        end_pos=23,
        source_ref="doc1"
    )
    
    assert result["status"] == "success"
    print("✅ Service works even without OpenAI API key")
    
    # Test find_related_entities method exists
    related = service.find_related_entities("Machine Learning", limit=5)
    assert isinstance(related, list), "find_related_entities should return list"
    print("✅ Enhanced methods available")
    
    print("\n✅ EMBEDDINGS CONFIGURATION: PASSED")
    return True


def test_service_manager_integration():
    """Test integration with ServiceManager."""
    print("\n🧪 Testing ServiceManager Integration...")
    
    from core.service_manager import ServiceManager
    
    # Get service manager instance
    manager = ServiceManager()
    
    # Ensure we get the identity service
    identity = manager.identity_service
    assert identity is not None, "Failed to get identity service"
    print("✅ ServiceManager provides identity service")
    
    # Verify it works
    result = identity.create_mention(
        surface_form="Test Entity",
        start_pos=0,
        end_pos=11,
        source_ref="test"
    )
    
    assert result["status"] == "success"
    print("✅ Identity service from ServiceManager works")
    
    print("\n✅ SERVICE MANAGER INTEGRATION: PASSED")
    return True


def test_error_handling():
    """Test error handling in consolidated service."""
    print("\n🧪 Testing Error Handling...")
    
    service = IdentityService()
    
    # Test 1: Empty surface form
    result = service.create_mention(
        surface_form="",
        start_pos=0,
        end_pos=0,
        source_ref="test"
    )
    assert result["status"] == "error"
    assert "empty" in result["error"]
    print("✅ Handles empty surface form")
    
    # Test 2: Invalid position range
    result = service.create_mention(
        surface_form="Test",
        start_pos=10,
        end_pos=5,  # End before start
        source_ref="test"
    )
    assert result["status"] == "error"
    assert "position" in result["error"].lower()
    print("✅ Handles invalid position range")
    
    # Test 3: Invalid confidence
    result = service.create_mention(
        surface_form="Test",
        start_pos=0,
        end_pos=4,
        source_ref="test",
        confidence=1.5  # > 1.0
    )
    assert result["status"] == "error"
    assert "confidence" in result["error"].lower()
    print("✅ Handles invalid confidence")
    
    # Test 4: Merge non-existent entities
    result = service.merge_entities("fake_id_1", "fake_id_2")
    assert result["status"] == "error"
    assert "not found" in result["error"]
    print("✅ Handles merge of non-existent entities")
    
    print("\n✅ ERROR HANDLING: PASSED")
    return True


def main():
    """Run all tests for consolidated identity service."""
    print("=" * 80)
    print("🧪 CONSOLIDATED IDENTITY SERVICE TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Backward Compatibility", test_backward_compatibility),
        ("Persistence Feature", test_persistence_feature),
        ("Embeddings Configuration", test_embeddings_simulation),
        ("ServiceManager Integration", test_service_manager_integration),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: EXCEPTION - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Consolidated identity service is ready!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review and fix issues")
        return 1


if __name__ == "__main__":
    exit(main())