#!/usr/bin/env python3
"""
TASK 2.1: Neo4j Connection and Operations Testing
Implementation per CLAUDE.md requirements - database integration verification
"""

import unittest
import sys
import os
from datetime import datetime
import uuid
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.service_manager import get_service_manager

class TestNeo4jIntegration(unittest.TestCase):
    """Test Neo4j database connectivity and operations per CLAUDE.md spec"""
    
    def setUp(self):
        """Set up test environment for each test"""
        self.service_manager = get_service_manager()
        self.test_entities = []
        self.test_relationships = []
    
    def tearDown(self):
        """Clean up test data after each test"""
        # Clean up any test entities created
        if hasattr(self, 'service_manager') and self.service_manager:
            driver = self.service_manager.get_neo4j_driver()
            if driver:
                try:
                    with driver.session() as session:
                        # Delete test entities
                        for entity_id in self.test_entities:
                            session.run(
                                "MATCH (e) WHERE e.test_id = $test_id DETACH DELETE e",
                                test_id=entity_id
                            )
                        # Delete test relationships
                        for rel_id in self.test_relationships:
                            session.run(
                                "MATCH ()-[r]-() WHERE r.test_id = $test_id DELETE r",
                                test_id=rel_id
                            )
                except Exception as e:
                    print(f"Warning: Cleanup failed: {e}")
    
    def test_neo4j_connection(self):
        """Test Neo4j database connectivity"""
        print("\n🧪 Testing Neo4j database connectivity...")
        
        # Test driver access
        driver = self.service_manager.get_neo4j_driver()
        self.assertIsNotNone(driver, "Should get Neo4j driver from service manager")
        
        # Test session creation
        try:
            with driver.session() as session:
                self.assertIsNotNone(session, "Should create database session")
                
                # Test basic query
                result = session.run("RETURN 1 as test_value")
                record = result.single()
                self.assertIsNotNone(record, "Should execute basic query")
                self.assertEqual(record["test_value"], 1, "Should return correct value")
                
                print("✅ Neo4j connection test passed")
                
        except Exception as e:
            self.fail(f"Neo4j connection test failed: {e}")
    
    def test_create_entity_operation(self):
        """Test creating entities in Neo4j"""
        print("\n🧪 Testing entity creation operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        self.assertIsNotNone(driver, "Driver should be available")
        
        test_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        self.test_entities.append(test_entity_id)
        
        try:
            with driver.session() as session:
                # Create test entity
                result = session.run(
                    """
                    CREATE (e:TestEntity {
                        test_id: $test_id,
                        name: $name,
                        type: $type,
                        created_at: datetime(),
                        test_flag: $test_flag,
                        source: $source
                    })
                    RETURN e
                    """,
                    test_id=test_entity_id,
                    name="Test Company",
                    type="ORGANIZATION",
                    test_flag=True,
                    source="test_suite"
                )
                
                record = result.single()
                self.assertIsNotNone(record, "Should create entity successfully")
                
                created_entity = record["e"]
                self.assertEqual(created_entity["test_id"], test_entity_id)
                self.assertEqual(created_entity["name"], "Test Company")
                self.assertEqual(created_entity["type"], "ORGANIZATION")
                
                print(f"✅ Entity creation test passed - Created entity with ID: {test_entity_id}")
                
        except Exception as e:
            self.fail(f"Entity creation test failed: {e}")
    
    def test_read_entity_operation(self):
        """Test reading entities from Neo4j"""
        print("\n🧪 Testing entity read operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        # First create an entity to read
        test_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        self.test_entities.append(test_entity_id)
        
        try:
            with driver.session() as session:
                # Create entity
                session.run(
                    """
                    CREATE (e:TestEntity {
                        test_id: $test_id,
                        name: $name,
                        type: $type,
                        created_at: datetime()
                    })
                    """,
                    test_id=test_entity_id,
                    name="Test Person",
                    type="PERSON"
                )
                
                # Read entity back
                result = session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) RETURN e",
                    test_id=test_entity_id
                )
                
                record = result.single()
                self.assertIsNotNone(record, "Should find created entity")
                
                retrieved_entity = record["e"]
                self.assertEqual(retrieved_entity["test_id"], test_entity_id)
                self.assertEqual(retrieved_entity["name"], "Test Person")
                self.assertEqual(retrieved_entity["type"], "PERSON")
                
                print(f"✅ Entity read test passed - Retrieved entity: {retrieved_entity['name']}")
                
        except Exception as e:
            self.fail(f"Entity read test failed: {e}")
    
    def test_create_relationship_operation(self):
        """Test creating relationships in Neo4j"""
        print("\n🧪 Testing relationship creation operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        # Create two entities to relate
        entity1_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        entity2_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        rel_id = f"test_rel_{uuid.uuid4().hex[:8]}"
        
        self.test_entities.extend([entity1_id, entity2_id])
        self.test_relationships.append(rel_id)
        
        try:
            with driver.session() as session:
                # Create entities
                session.run(
                    """
                    CREATE (e1:TestEntity {test_id: $e1_id, name: $e1_name, type: 'PERSON'})
                    CREATE (e2:TestEntity {test_id: $e2_id, name: $e2_name, type: 'ORGANIZATION'})
                    """,
                    e1_id=entity1_id,
                    e1_name="John Doe",
                    e2_id=entity2_id,
                    e2_name="Acme Corp"
                )
                
                # Create relationship
                result = session.run(
                    """
                    MATCH (e1:TestEntity {test_id: $e1_id})
                    MATCH (e2:TestEntity {test_id: $e2_id})
                    CREATE (e1)-[r:WORKS_FOR {
                        test_id: $rel_id,
                        relationship_type: 'employment',
                        created_at: datetime()
                    }]->(e2)
                    RETURN r
                    """,
                    e1_id=entity1_id,
                    e2_id=entity2_id,
                    rel_id=rel_id
                )
                
                record = result.single()
                self.assertIsNotNone(record, "Should create relationship successfully")
                
                relationship = record["r"]
                self.assertEqual(relationship["test_id"], rel_id)
                self.assertEqual(relationship["relationship_type"], "employment")
                
                print(f"✅ Relationship creation test passed - Created WORKS_FOR relationship")
                
        except Exception as e:
            self.fail(f"Relationship creation test failed: {e}")
    
    def test_update_entity_operation(self):
        """Test updating entities in Neo4j"""
        print("\n🧪 Testing entity update operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        test_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        self.test_entities.append(test_entity_id)
        
        try:
            with driver.session() as session:
                # Create entity
                session.run(
                    """
                    CREATE (e:TestEntity {
                        test_id: $test_id,
                        name: $name,
                        type: $type,
                        status: 'initial'
                    })
                    """,
                    test_id=test_entity_id,
                    name="Test Entity",
                    type="GENERIC"
                )
                
                # Update entity
                result = session.run(
                    """
                    MATCH (e:TestEntity {test_id: $test_id})
                    SET e.status = 'updated',
                        e.updated_at = datetime(),
                        e.version = 2
                    RETURN e
                    """,
                    test_id=test_entity_id
                )
                
                record = result.single()
                self.assertIsNotNone(record, "Should update entity successfully")
                
                updated_entity = record["e"]
                self.assertEqual(updated_entity["status"], "updated")
                self.assertEqual(updated_entity["version"], 2)
                
                print(f"✅ Entity update test passed - Updated entity status to: {updated_entity['status']}")
                
        except Exception as e:
            self.fail(f"Entity update test failed: {e}")
    
    def test_delete_entity_operation(self):
        """Test deleting entities from Neo4j"""
        print("\n🧪 Testing entity deletion operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        test_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        
        try:
            with driver.session() as session:
                # Create entity
                session.run(
                    """
                    CREATE (e:TestEntity {
                        test_id: $test_id,
                        name: $name,
                        type: $type
                    })
                    """,
                    test_id=test_entity_id,
                    name="Entity To Delete",
                    type="TEMPORARY"
                )
                
                # Verify entity exists
                result = session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) RETURN count(e) as count",
                    test_id=test_entity_id
                )
                count_before = result.single()["count"]
                self.assertEqual(count_before, 1, "Entity should exist before deletion")
                
                # Delete entity
                session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) DETACH DELETE e",
                    test_id=test_entity_id
                )
                
                # Verify entity is deleted
                result = session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) RETURN count(e) as count",
                    test_id=test_entity_id
                )
                count_after = result.single()["count"]
                self.assertEqual(count_after, 0, "Entity should be deleted")
                
                print(f"✅ Entity deletion test passed - Entity successfully deleted")
                
        except Exception as e:
            self.fail(f"Entity deletion test failed: {e}")
    
    def test_schema_operations(self):
        """Test database schema operations"""
        print("\n🧪 Testing schema operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        try:
            with driver.session() as session:
                # Test creating index
                try:
                    session.run("CREATE INDEX test_entity_index IF NOT EXISTS FOR (e:TestEntity) ON (e.test_id)")
                    print("✅ Index creation successful")
                except Exception as e:
                    print(f"⚠️  Index creation warning: {e}")
                
                # Test showing indexes
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                self.assertIsInstance(indexes, list, "Should return list of indexes")
                
                print(f"✅ Schema query test passed - Found {len(indexes)} indexes")
                
                # Test showing constraints
                result = session.run("SHOW CONSTRAINTS")
                constraints = list(result)
                self.assertIsInstance(constraints, list, "Should return list of constraints")
                
                print(f"✅ Constraints query test passed - Found {len(constraints)} constraints")
                
        except Exception as e:
            self.fail(f"Schema operations test failed: {e}")
    
    def test_transaction_operations(self):
        """Test database transaction handling"""
        print("\n🧪 Testing transaction operations...")
        
        driver = self.service_manager.get_neo4j_driver()
        
        test_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
        self.test_entities.append(test_entity_id)
        
        try:
            # Test successful transaction
            with driver.session() as session:
                with session.begin_transaction() as tx:
                    tx.run(
                        """
                        CREATE (e:TestEntity {
                            test_id: $test_id,
                            name: $name,
                            transaction_test: true
                        })
                        """,
                        test_id=test_entity_id,
                        name="Transaction Test Entity"
                    )
                    # Transaction commits automatically
                
                # Verify entity was created
                result = session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) RETURN e",
                    test_id=test_entity_id
                )
                record = result.single()
                self.assertIsNotNone(record, "Entity should exist after successful transaction")
                
                print("✅ Transaction commit test passed")
                
                # Test transaction rollback
                failed_entity_id = f"test_entity_{uuid.uuid4().hex[:8]}"
                try:
                    with session.begin_transaction() as tx:
                        tx.run(
                            """
                            CREATE (e:TestEntity {
                                test_id: $test_id,
                                name: $name
                            })
                            """,
                            test_id=failed_entity_id,
                            name="Should Not Exist"
                        )
                        # Force rollback by raising exception
                        raise Exception("Intentional rollback test")
                except Exception:
                    pass  # Expected exception
                
                # Verify entity was not created due to rollback
                result = session.run(
                    "MATCH (e:TestEntity {test_id: $test_id}) RETURN count(e) as count",
                    test_id=failed_entity_id
                )
                count = result.single()["count"]
                self.assertEqual(count, 0, "Entity should not exist after rollback")
                
                print("✅ Transaction rollback test passed")
                
        except Exception as e:
            self.fail(f"Transaction operations test failed: {e}")


def run_neo4j_tests():
    """Run all Neo4j integration tests and return results"""
    print("🚀 Running Neo4j Integration Tests...")
    print("=" * 60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNeo4jIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Document results
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "=" * 60)
    print("🏁 Neo4j Integration Test Summary:")
    print(f"Timestamp: {timestamp}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  {test}")
    
    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"  {test}")
    
    print(f"\n{'✅ All Neo4j tests passed!' if success else '❌ Some Neo4j tests failed!'}")
    
    return {
        'success': success,
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'timestamp': timestamp
    }


if __name__ == "__main__":
    results = run_neo4j_tests()
    sys.exit(0 if results['success'] else 1)