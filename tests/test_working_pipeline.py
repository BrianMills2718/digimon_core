#!/usr/bin/env python3
"""
End-to-End Working Pipeline Test
Tests that the system actually produces entities and relationships as required by CLAUDE.md
"""

import os
import sys
import tempfile
import uuid
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent

from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.core.service_manager import get_service_manager
from neo4j import GraphDatabase

def test_schema_initialization():
    """Test that schema initialization created proper constraints and indexes"""
    print("🔍 Testing schema initialization...")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    
    with driver.session() as session:
        # Test that sample data exists
        entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
        rel_count = session.run("MATCH ()-[r:RELATIONSHIP]-() RETURN count(r) as count").single()["count"]
        
        print(f"✅ Sample entities in database: {entity_count}")
        print(f"✅ Sample relationships in database: {rel_count}")
        
        # Test schema compliance
        schema_test = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_id IS NOT NULL 
            AND e.canonical_name IS NOT NULL
            AND e.entity_type IS NOT NULL
            RETURN count(e) as compliant_count
        """).single()["compliant_count"]
        
        print(f"✅ Schema compliant entities: {schema_test}")
        
        assert entity_count > 0, "No entities found in database"
        assert rel_count > 0, "No relationships found in database"
        assert schema_test == entity_count, "Not all entities are schema compliant"
    
    driver.close()
    print("✅ Schema initialization test passed!")

def test_entity_extraction():
    """Test that entity extraction actually works"""
    print("🔍 Testing entity extraction...")
    
    # Test text with known entities
    test_text = """
    Tesla Inc. is an American electric vehicle and clean energy company based in Austin, Texas. 
    The company was founded in 2003 by Elon Musk, Martin Eberhard, and Marc Tarpenning.
    Tesla designs and manufactures electric vehicles, battery energy storage systems, and solar panels.
    """
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Create NER extractor
    ner = SpacyNER(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service
    )
    
    # Extract entities using the working method
    entities = ner.extract_entities_working(test_text)
    
    print(f"✅ Extracted {len(entities)} entities")
    for entity in entities:
        print(f"  - {entity['name']} ({entity['type']})")
    
    assert len(entities) > 0, "No entities extracted from test text"
    assert any(e['type'] == 'ORG' for e in entities), "No organizations found"
    assert any(e['type'] == 'PERSON' for e in entities), "No persons found"
    
    print("✅ Entity extraction test passed!")
    return entities

def test_relationship_extraction():
    """Test that relationship extraction actually works"""
    print("🔍 Testing relationship extraction...")
    
    # Test text with known relationships
    test_text = """
    Tesla Inc. is an American electric vehicle company based in Austin, Texas. 
    Elon Musk founded Tesla in 2003.
    """
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Create extractors
    ner = SpacyNER(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service
    )
    
    rel_extractor = RelationshipExtractor(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service
    )
    
    # Extract entities first
    entities = ner.extract_entities_working(test_text)
    
    # Extract relationships
    relationships = rel_extractor.extract_relationships_working(test_text, entities)
    
    print(f"✅ Extracted {len(relationships)} relationships")
    for rel in relationships:
        print(f"  - {rel['source_id']} -> {rel['target_id']} ({rel['type']})")
    
    assert len(relationships) > 0, "No relationships extracted from test text"
    
    print("✅ Relationship extraction test passed!")
    return entities, relationships

def test_entity_persistence():
    """Test that entities are actually persisted to Neo4j"""
    print("🔍 Testing entity persistence...")
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Create entity builder
    entity_builder = EntityBuilder(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service,
        shared_driver=service_manager.get_neo4j_driver()
    )
    
    # Create test entity
    test_entity = {
        'id': f"test_entity_{uuid.uuid4()}",
        'name': 'Test Company',
        'type': 'ORG',
        'surface_forms': ['Test Company'],
        'confidence': 0.9
    }
    
    # Persist entity
    result = entity_builder.create_entity_with_schema(test_entity)
    
    print(f"✅ Entity creation result: {result['status']}")
    assert result['status'] == 'success', f"Entity creation failed: {result}"
    
    # Verify entity exists in Neo4j
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    
    with driver.session() as session:
        found_entity = session.run(
            "MATCH (e:Entity {entity_id: $id}) RETURN e",
            id=test_entity['id']
        ).single()
        
        assert found_entity is not None, "Entity not found in Neo4j"
        
        entity_data = dict(found_entity["e"])
        assert entity_data['canonical_name'] == test_entity['name'], "Entity name not persisted correctly"
        assert entity_data['entity_type'] == test_entity['type'], "Entity type not persisted correctly"
        
        print(f"✅ Entity persisted correctly: {entity_data['canonical_name']}")
    
    driver.close()
    print("✅ Entity persistence test passed!")

def test_relationship_persistence():
    """Test that relationships are actually persisted to Neo4j"""
    print("🔍 Testing relationship persistence...")
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Create builders
    entity_builder = EntityBuilder(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service,
        shared_driver=service_manager.get_neo4j_driver()
    )
    
    edge_builder = EdgeBuilder(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service,
        shared_driver=service_manager.get_neo4j_driver()
    )
    
    # Create test entities
    entity1 = {
        'id': f"test_entity_1_{uuid.uuid4()}",
        'name': 'Test Person',
        'type': 'PERSON',
        'surface_forms': ['Test Person'],
        'confidence': 0.9
    }
    
    entity2 = {
        'id': f"test_entity_2_{uuid.uuid4()}",
        'name': 'Test Company',
        'type': 'ORG',
        'surface_forms': ['Test Company'],
        'confidence': 0.9
    }
    
    # Persist entities
    result1 = entity_builder.create_entity_with_schema(entity1)
    result2 = entity_builder.create_entity_with_schema(entity2)
    
    assert result1['status'] == 'success', f"Entity 1 creation failed: {result1}"
    assert result2['status'] == 'success', f"Entity 2 creation failed: {result2}"
    
    # Create test relationship
    test_relationship = {
        'source_id': entity1['id'],
        'target_id': entity2['id'],
        'type': 'WORKS_FOR',
        'confidence': 0.8,
        'weight': 1.0
    }
    
    # Persist relationship
    result = edge_builder.create_relationship_with_schema(test_relationship)
    
    print(f"✅ Relationship creation result: {result['status']}")
    assert result['status'] == 'success', f"Relationship creation failed: {result}"
    
    # Verify relationship exists in Neo4j
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    
    with driver.session() as session:
        found_rel = session.run(
            """
            MATCH (a:Entity {entity_id: $source_id})-[r:RELATIONSHIP]->(b:Entity {entity_id: $target_id})
            RETURN r, a.canonical_name as source_name, b.canonical_name as target_name
            """,
            source_id=entity1['id'],
            target_id=entity2['id']
        ).single()
        
        assert found_rel is not None, "Relationship not found in Neo4j"
        
        rel_data = dict(found_rel["r"])
        assert rel_data['relation_type'] == test_relationship['type'], "Relationship type not persisted correctly"
        
        print(f"✅ Relationship persisted correctly: {found_rel['source_name']} -> {found_rel['target_name']}")
    
    driver.close()
    print("✅ Relationship persistence test passed!")

def test_ui_queries():
    """Test that UI queries return actual data"""
    print("🔍 Testing UI queries...")
    
    # Test entity query that UI uses
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    
    with driver.session() as session:
        # Query entities like the UI does
        entities = session.run(
            "MATCH (e:Entity) RETURN e.entity_id as id, e.canonical_name as name, e.entity_type as type LIMIT 10"
        ).data()
        
        print(f"✅ UI entity query returned {len(entities)} entities")
        for entity in entities:
            print(f"  - {entity['name']} ({entity['type']})")
        
        # Query relationships like the UI does
        relationships = session.run(
            "MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity) RETURN a.entity_id as source, b.entity_id as target, r.relation_type as type LIMIT 10"
        ).data()
        
        print(f"✅ UI relationship query returned {len(relationships)} relationships")
        for rel in relationships:
            print(f"  - {rel['source']} -> {rel['target']} ({rel['type']})")
        
        assert len(entities) > 0, "UI entity query returned no results"
        assert len(relationships) > 0, "UI relationship query returned no results"
    
    driver.close()
    print("✅ UI queries test passed!")

def test_end_to_end_pipeline():
    """Test the complete end-to-end pipeline"""
    print("🔍 Testing complete end-to-end pipeline...")
    
    # Test text
    test_text = """
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
    Tim Cook is the CEO of Apple Inc.
    The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    """
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Create all components
    ner = SpacyNER(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service
    )
    
    rel_extractor = RelationshipExtractor(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service
    )
    
    entity_builder = EntityBuilder(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service,
        shared_driver=service_manager.get_neo4j_driver()
    )
    
    edge_builder = EdgeBuilder(
        identity_service=service_manager.identity_service,
        provenance_service=service_manager.provenance_service,
        quality_service=service_manager.quality_service,
        shared_driver=service_manager.get_neo4j_driver()
    )
    
    # Step 1: Extract entities
    entities = ner.extract_entities_working(test_text)
    print(f"✅ Extracted {len(entities)} entities")
    
    # Step 2: Persist entities
    persisted_entities = []
    for entity in entities:
        result = entity_builder.create_entity_with_schema(entity)
        if result['status'] == 'success':
            persisted_entities.append(entity)
    
    print(f"✅ Persisted {len(persisted_entities)} entities")
    
    # Step 3: Extract relationships
    relationships = rel_extractor.extract_relationships_working(test_text, entities)
    print(f"✅ Extracted {len(relationships)} relationships")
    
    # Step 4: Persist relationships
    persisted_relationships = []
    for relationship in relationships:
        result = edge_builder.create_relationship_with_schema(relationship)
        if result['status'] == 'success':
            persisted_relationships.append(relationship)
    
    print(f"✅ Persisted {len(persisted_relationships)} relationships")
    
    # Step 5: Verify data in Neo4j
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password")
    )
    
    with driver.session() as session:
        # Count entities created by this test
        entity_count = session.run(
            "MATCH (e:Entity) WHERE e.entity_id IN $ids RETURN count(e) as count",
            ids=[e['id'] for e in entities]
        ).single()["count"]
        
        # Count relationships created by this test
        rel_count = session.run(
            "MATCH ()-[r:RELATIONSHIP]->() WHERE r.relation_type IN $types RETURN count(r) as count",
            types=[r['type'] for r in relationships]
        ).single()["count"]
        
        print(f"✅ Found {entity_count} entities in Neo4j")
        print(f"✅ Found {rel_count} relationships in Neo4j")
        
        # Test UI-style queries
        ui_entities = session.run(
            "MATCH (e:Entity) WHERE e.entity_id IN $ids RETURN e.entity_id as id, e.canonical_name as name, e.entity_type as type",
            ids=[e['id'] for e in entities]
        ).data()
        
        ui_relationships = session.run(
            "MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity) WHERE r.relation_type IN $types RETURN a.entity_id as source, b.entity_id as target, r.relation_type as type",
            types=[r['type'] for r in relationships]
        ).data()
        
        print(f"✅ UI queries returned {len(ui_entities)} entities and {len(ui_relationships)} relationships")
        
        assert entity_count > 0, "No entities found in Neo4j after pipeline"
        assert rel_count > 0, "No relationships found in Neo4j after pipeline"
        assert len(ui_entities) > 0, "UI entity query returned no results"
    
    driver.close()
    print("✅ End-to-end pipeline test passed!")

def main():
    """Run all tests"""
    print("🧪 Running GraphRAG Pipeline Tests")
    print("=" * 50)
    
    try:
        test_schema_initialization()
        test_entity_extraction()
        test_relationship_extraction()
        test_entity_persistence()
        test_relationship_persistence()
        test_ui_queries()
        test_end_to_end_pipeline()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ The GraphRAG system is working correctly")
        print("✅ UI should now display actual entities and relationships")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()