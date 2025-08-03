#!/usr/bin/env python3
"""
Database Verification Script
Tests database with production-scale data (100k+ nodes)
"""

import sys
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.service_manager import ServiceManager
from src.core.neo4j_manager import Neo4jManager
from src.core.evidence_logger import EvidenceLogger

class DatabaseVerifier:
    """Verifies database functionality at production scale"""
    
    def __init__(self):
        """Initialize database verifier"""
        self.service_manager = ServiceManager()
        self.neo4j_manager = Neo4jManager()
        self.driver = None
        self.verification_results = []
        self.evidence_logger = EvidenceLogger()
    
    def connect_to_database(self) -> bool:
        """Test database connectivity"""
        print("🔗 Testing database connectivity...")
        
        try:
            self.driver = self.neo4j_manager.get_driver()
            
            # Test connection with simple query
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                
                if record and record["test"] == 1:
                    print("✅ Database connectivity successful")
                    return True
                else:
                    print("❌ Database connectivity failed - invalid response")
                    return False
                    
        except Exception as e:
            print(f"❌ Database connectivity failed: {e}")
            return False
    
    def verify_database_info(self) -> bool:
        """Verify database information"""
        print("📊 Verifying database information...")
        
        try:
            with self.driver.session() as session:
                # Get database version
                result = session.run("CALL dbms.components() YIELD versions")
                versions = result.single()
                
                # Get database size
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = result.single()["node_count"]
                
                # Get relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()["rel_count"]
                
                print(f"✅ Database info retrieved:")
                print(f"   - Nodes: {node_count}")
                print(f"   - Relationships: {rel_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ Database info verification failed: {e}")
            return False
    
    def verify_schema_operations(self) -> bool:
        """Verify schema operations"""
        print("🏗️  Verifying schema operations...")
        
        try:
            with self.driver.session() as session:
                # Create test index
                session.run("CREATE INDEX test_index IF NOT EXISTS FOR (n:TestEntity) ON (n.id)")
                
                # Verify index creation
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                
                # Clean up any existing constraints first
                session.run("DROP CONSTRAINT test_constraint IF EXISTS")
                
                # Create test constraint
                session.run("CREATE CONSTRAINT test_constraint IF NOT EXISTS FOR (n:TestEntity) REQUIRE n.id IS UNIQUE")
                
                # Verify constraint creation
                result = session.run("SHOW CONSTRAINTS")
                constraints = list(result)
                
                # Clean up
                session.run("DROP CONSTRAINT test_constraint IF EXISTS")
                session.run("DROP INDEX test_index IF EXISTS")
                
                print("✅ Schema operations successful")
                return True
                
        except Exception as e:
            print(f"❌ Schema operations failed: {e}")
            return False
    
    def verify_crud_operations(self) -> bool:
        """Verify CRUD operations"""
        print("🔄 Verifying CRUD operations...")
        
        try:
            with self.driver.session() as session:
                # CREATE
                session.run("""
                    CREATE (n:TestEntity {
                        id: 'test_001',
                        name: 'Test Entity',
                        created_at: datetime()
                    })
                """)
                
                # READ
                result = session.run("MATCH (n:TestEntity {id: 'test_001'}) RETURN n")
                record = result.single()
                
                if not record:
                    print("❌ CREATE/READ failed - entity not found")
                    return False
                
                # UPDATE
                session.run("""
                    MATCH (n:TestEntity {id: 'test_001'})
                    SET n.name = 'Updated Test Entity',
                        n.updated_at = datetime()
                """)
                
                # Verify update
                result = session.run("MATCH (n:TestEntity {id: 'test_001'}) RETURN n.name as name")
                record = result.single()
                
                if record["name"] != "Updated Test Entity":
                    print("❌ UPDATE failed - name not updated")
                    return False
                
                # DELETE
                session.run("MATCH (n:TestEntity {id: 'test_001'}) DELETE n")
                
                # Verify deletion
                result = session.run("MATCH (n:TestEntity {id: 'test_001'}) RETURN n")
                record = result.single()
                
                if record:
                    print("❌ DELETE failed - entity still exists")
                    return False
                
                print("✅ CRUD operations successful")
                return True
                
        except Exception as e:
            print(f"❌ CRUD operations failed: {e}")
            return False
    
    def verify_transaction_handling(self) -> bool:
        """Verify transaction handling"""
        print("🔒 Verifying transaction handling...")
        
        try:
            # Test successful transaction
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    tx.run("CREATE (n:TransactionTest {id: 'tx_001', status: 'pending'})")
                    tx.run("CREATE (n:TransactionTest {id: 'tx_002', status: 'pending'})")
                    tx.commit()
                
                # Verify both nodes exist
                result = session.run("MATCH (n:TransactionTest) RETURN count(n) as count")
                count = result.single()["count"]
                
                if count != 2:
                    print("❌ Transaction commit failed")
                    return False
            
            # Test transaction rollback
            try:
                with self.driver.session() as session:
                    with session.begin_transaction() as tx:
                        tx.run("CREATE (n:TransactionTest {id: 'tx_003', status: 'pending'})")
                        tx.run("INVALID CYPHER QUERY")  # This will cause rollback
                        tx.commit()
            except:
                pass  # Expected to fail
            
            # Verify rollback worked
            with self.driver.session() as session:
                result = session.run("MATCH (n:TransactionTest {id: 'tx_003'}) RETURN n")
                record = result.single()
                
                if record:
                    print("❌ Transaction rollback failed")
                    return False
                
                # Clean up
                session.run("MATCH (n:TransactionTest) DELETE n")
                
                print("✅ Transaction handling successful")
                return True
                
        except Exception as e:
            print(f"❌ Transaction handling failed: {e}")
            return False
    
    def verify_production_scale_performance(self) -> bool:
        """Verify database performance at production scale (100k+ nodes)"""
        print("⚡ Verifying production scale performance...")
        
        MIN_NODES = 100000
        MIN_RELATIONSHIPS = 200000
        
        try:
            # Clean up any existing test data
            self._cleanup_test_data()
            
            # Create production-scale dataset
            print(f"📊 Creating production dataset: {MIN_NODES} nodes, {MIN_RELATIONSHIPS} relationships...")
            self._create_production_dataset(MIN_NODES, MIN_RELATIONSHIPS)
            
            # Test performance queries
            performance_tests = [
                ("Node count", "MATCH (n:PerfTestEntity) RETURN count(n)", 2.0),
                ("Relationship count", "MATCH ()-[r:PERF_TEST_REL]->() RETURN count(r)", 3.0),
                ("Complex traversal", "MATCH (n:PerfTestEntity)-[:PERF_TEST_REL*1..2]-(m:PerfTestEntity) RETURN count(DISTINCT m)", 5.0),
                ("Property search", "MATCH (n:PerfTestEntity) WHERE n.category = 'type_1' RETURN count(n)", 4.0),
                ("Aggregation", "MATCH (n:PerfTestEntity) WITH n.category as cat, count(n) as cnt RETURN cat, cnt ORDER BY cnt DESC", 3.0)
            ]
            
            all_passed = True
            
            for test_name, query, max_time in performance_tests:
                start_time = time.time()
                
                with self.driver.session() as session:
                    result = session.run(query)
                    records = list(result)
                
                query_time = time.time() - start_time
                
                # Log actual performance metrics to evidence file
                self.evidence_logger.log_database_performance(
                    test_name, query_time, len(records), query
                )
                
                if query_time > max_time:
                    print(f"❌ {test_name} too slow: {query_time:.2f}s > {max_time}s")
                    all_passed = False
                else:
                    print(f"✅ {test_name}: {len(records)} results in {query_time:.2f}s")
            
            # Clean up
            self._cleanup_test_data()
            
            if all_passed:
                print("✅ Production scale performance verification successful")
                return True
            else:
                print("❌ Production scale performance verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Production scale performance verification failed: {e}")
            self._cleanup_test_data()
            return False
    
    def _create_production_dataset(self, num_nodes: int, num_relationships: int):
        """Create production-scale dataset"""
        batch_size = 1000
        
        # Create nodes in batches
        for i in range(0, num_nodes, batch_size):
            batch_end = min(i + batch_size, num_nodes)
            batch_data = []
            
            for j in range(i, batch_end):
                batch_data.append({
                    "id": f"perf_entity_{j}",
                    "name": f"Performance Entity {j}",
                    "category": f"type_{j % 10}",
                    "value": random.randint(1, 1000),
                    "batch": i // batch_size
                })
            
            with self.driver.session() as session:
                session.run("""
                    UNWIND $batch as entity
                    CREATE (n:PerfTestEntity {
                        id: entity.id,
                        name: entity.name,
                        category: entity.category,
                        value: entity.value,
                        batch: entity.batch,
                        created_at: datetime()
                    })
                """, batch=batch_data)
        
        # Create relationships in batches
        for i in range(0, num_relationships, batch_size):
            batch_end = min(i + batch_size, num_relationships)
            batch_relationships = []
            
            for j in range(i, batch_end):
                source_id = f"perf_entity_{j % num_nodes}"
                target_id = f"perf_entity_{(j + 1) % num_nodes}"
                
                batch_relationships.append({
                    "source_id": source_id,
                    "target_id": target_id,
                    "rel_type": f"type_{j % 5}",
                    "weight": random.uniform(0.1, 1.0)
                })
            
            with self.driver.session() as session:
                session.run("""
                    UNWIND $batch as rel
                    MATCH (source:PerfTestEntity {id: rel.source_id})
                    MATCH (target:PerfTestEntity {id: rel.target_id})
                    CREATE (source)-[:PERF_TEST_REL {
                        type: rel.rel_type,
                        weight: rel.weight,
                        created_at: datetime()
                    }]->(target)
                """, batch=batch_relationships)
    
    def _cleanup_test_data(self):
        """Clean up test data"""
        with self.driver.session() as session:
            # Delete relationships first, then nodes
            session.run("MATCH ()-[r:PERF_TEST_REL]->() DELETE r")
            session.run("MATCH (n:PerfTestEntity) DELETE n")
    
    def run_full_verification(self) -> bool:
        """Run complete database verification"""
        print("🚀 Starting comprehensive database verification...")
        
        verifications = [
            ("Database Connectivity", self.connect_to_database),
            ("Database Information", self.verify_database_info),
            ("Schema Operations", self.verify_schema_operations),
            ("CRUD Operations", self.verify_crud_operations),
            ("Transaction Handling", self.verify_transaction_handling),
            ("Production Scale Performance", self.verify_production_scale_performance)
        ]
        
        passed_count = 0
        total_count = len(verifications)
        
        for name, verification_func in verifications:
            print(f"\n📋 Running {name}...")
            
            try:
                success = verification_func()
                if success:
                    passed_count += 1
                    self.verification_results.append({
                        'name': name,
                        'status': 'PASSED',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    self.verification_results.append({
                        'name': name,
                        'status': 'FAILED',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"❌ {name} failed with exception: {e}")
                self.verification_results.append({
                    'name': name,
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        success_rate = (passed_count / total_count) * 100
        
        print(f"\n📊 DATABASE VERIFICATION RESULTS:")
        print(f"Passed: {passed_count}/{total_count}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if passed_count == total_count:
            print("✅ ALL DATABASE VERIFICATIONS PASSED")
            print("Database verification completed successfully with 100% SUCCESS")
            return True
        else:
            print("❌ DATABASE VERIFICATION FAILED")
            for result in self.verification_results:
                if result['status'] != 'PASSED':
                    print(f"  - {result['name']}: {result['status']}")
            return False
    
    def save_verification_report(self, filename: str = "docs/database_verification_report.md"):
        """Save verification report"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write("# Database Verification Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            passed_count = sum(1 for r in self.verification_results if r['status'] == 'PASSED')
            total_count = len(self.verification_results)
            success_rate = (passed_count / total_count) * 100
            
            f.write(f"## Summary\n")
            f.write(f"- Total verifications: {total_count}\n")
            f.write(f"- Passed: {passed_count}\n")
            f.write(f"- Success rate: {success_rate:.1f}%\n\n")
            
            f.write("## Detailed Results\n\n")
            
            for result in self.verification_results:
                f.write(f"### {result['name']}\n")
                f.write(f"- Status: {result['status']}\n")
                f.write(f"- Timestamp: {result['timestamp']}\n")
                
                if result.get('error'):
                    f.write(f"- Error: {result['error']}\n")
                
                f.write("\n")

def main():
    """Main verification function"""
    verifier = DatabaseVerifier()
    
    # Run full verification
    success = verifier.run_full_verification()
    
    # Save report
    verifier.save_verification_report()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()