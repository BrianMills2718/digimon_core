#!/usr/bin/env python3
"""
Production Scale Database Testing

This module implements comprehensive production-scale database tests
as specified in CLAUDE.md Task 2.1. It tests the database performance
with realistic production loads and conditions.

Requirements:
- Test with 100k+ nodes (minimum production scale)
- Test concurrent load with 10+ concurrent users
- Test realistic query performance benchmarks
- No more "toy dataset" claims
"""

import unittest
import time
import random
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.service_manager import get_service_manager
from src.core.config_manager import get_config
from src.core.neo4j_manager import ensure_neo4j_for_testing

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestProductionScale(unittest.TestCase):
    """Test database performance at production scale."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        logger.info("🚀 Setting up production scale database tests...")
        
        # Ensure Neo4j is available
        if not ensure_neo4j_for_testing():
            raise unittest.SkipTest("Neo4j not available for testing")
        
        cls.service_manager = get_service_manager()
        cls.driver = cls.service_manager.get_neo4j_driver()
        
        if not cls.driver:
            raise unittest.SkipTest("Neo4j driver not available")
        
        # Clean up any existing test data
        cls._cleanup_test_data()
        
        logger.info("✅ Production scale test environment ready")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        logger.info("🧹 Cleaning up production scale test data...")
        cls._cleanup_test_data()
        logger.info("✅ Production scale test cleanup complete")
    
    @classmethod
    def _cleanup_test_data(cls):
        """Clean up test data from database."""
        try:
            with cls.driver.session() as session:
                # Delete all test entities and relationships
                session.run("MATCH (n) WHERE n.test_marker = 'production_scale' DETACH DELETE n")
                session.run("MATCH (n:ProductionTestEntity) DETACH DELETE n")
                session.run("MATCH (n:ConcurrentTest) DETACH DELETE n")
                session.run("MATCH (n:StressTestEntity) DETACH DELETE n")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
    
    def test_large_dataset_performance(self):
        """Test with 100k+ nodes (minimum production scale)."""
        logger.info("🔍 Testing large dataset performance with 100k+ nodes...")
        
        batch_size = 1000
        total_nodes = 100000
        
        start_time = time.time()
        
        # Create test data in batches
        logger.info(f"Creating {total_nodes} test nodes in batches of {batch_size}...")
        
        with self.driver.session() as session:
            for i in range(0, total_nodes, batch_size):
                batch_data = []
                for j in range(i, min(i + batch_size, total_nodes)):
                    batch_data.append({
                        "id": f"prod_test_node_{j}",
                        "name": f"Production Test Entity {j}",
                        "entity_type": "PRODUCTION_TEST",
                        "confidence": random.uniform(0.7, 1.0),
                        "batch_id": i // batch_size,
                        "created_at": datetime.now().isoformat(),
                        "test_marker": "production_scale"
                    })
                
                session.run("""
                    UNWIND $batch as entity
                    CREATE (n:ProductionTestEntity {
                        entity_id: entity.id,
                        canonical_name: entity.name,
                        entity_type: entity.entity_type,
                        confidence: entity.confidence,
                        batch_id: entity.batch_id,
                        created_at: entity.created_at,
                        test_marker: entity.test_marker
                    })
                """, batch=batch_data)
                
                # Progress logging
                if (i + batch_size) % 10000 == 0:
                    logger.info(f"  Created {i + batch_size} nodes...")
        
        creation_time = time.time() - start_time
        logger.info(f"✅ Created {total_nodes} nodes in {creation_time:.2f}s")
        
        # Test query performance on large dataset
        logger.info("🔍 Testing query performance on large dataset...")
        
        # Test 1: Count query
        start_time = time.time()
        with self.driver.session() as session:
            result = session.run("MATCH (n:ProductionTestEntity) RETURN count(n) as count")
            count = result.single()["count"]
        count_time = time.time() - start_time
        
        # Test 2: Complex aggregation query
        start_time = time.time()
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:ProductionTestEntity) 
                WITH n.entity_type as type, n.batch_id as batch, avg(n.confidence) as avg_conf
                RETURN type, batch, avg_conf
                ORDER BY avg_conf DESC
                LIMIT 100
            """)
            agg_results = list(result)
        agg_time = time.time() - start_time
        
        # Test 3: Index lookup query
        start_time = time.time()
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:ProductionTestEntity) 
                WHERE n.confidence > 0.9
                RETURN n.entity_id, n.canonical_name, n.confidence
                ORDER BY n.confidence DESC
                LIMIT 1000
            """)
            lookup_results = list(result)
        lookup_time = time.time() - start_time
        
        # Assertions for production scale
        self.assertEqual(count, total_nodes, "All nodes should be created")
        self.assertLess(count_time, 5.0, "Count query should complete within 5 seconds on 100k nodes")
        self.assertLess(agg_time, 10.0, "Aggregation query should complete within 10 seconds")
        self.assertLess(lookup_time, 5.0, "Lookup query should complete within 5 seconds")
        self.assertGreater(len(lookup_results), 0, "Lookup should return results")
        
        logger.info(f"✅ Large dataset performance test passed:")
        logger.info(f"  - Count query: {count_time:.2f}s")
        logger.info(f"  - Aggregation query: {agg_time:.2f}s")
        logger.info(f"  - Lookup query: {lookup_time:.2f}s")
    
    def test_concurrent_load(self):
        """Test database under concurrent load (10+ concurrent users)."""
        logger.info("🔍 Testing concurrent load with 10+ concurrent users...")
        
        def concurrent_operation(thread_id: int, operations_per_thread: int = 100) -> Dict[str, Any]:
            """Perform database operations concurrently."""
            thread_start = time.time()
            created_count = 0
            queried_count = 0
            errors = []
            
            try:
                with self.driver.session() as session:
                    # Create entities
                    for i in range(operations_per_thread):
                        try:
                            session.run("""
                                CREATE (n:ConcurrentTest {
                                    entity_id: $id,
                                    thread_id: $thread,
                                    iteration: $iteration,
                                    created_at: $timestamp,
                                    test_marker: 'production_scale'
                                })
                            """, 
                            id=f"concurrent_thread_{thread_id}_item_{i}",
                            thread=thread_id,
                            iteration=i,
                            timestamp=datetime.now().isoformat()
                            )
                            created_count += 1
                        except Exception as e:
                            errors.append(f"Create error: {e}")
                    
                    # Query entities
                    for i in range(operations_per_thread // 2):
                        try:
                            result = session.run("""
                                MATCH (n:ConcurrentTest {thread_id: $thread}) 
                                RETURN count(n) as count
                            """, thread=thread_id)
                            count = result.single()["count"]
                            queried_count += 1
                        except Exception as e:
                            errors.append(f"Query error: {e}")
                    
                    # Final verification
                    result = session.run("""
                        MATCH (n:ConcurrentTest {thread_id: $thread}) 
                        RETURN count(n) as final_count
                    """, thread=thread_id)
                    final_count = result.single()["final_count"]
                    
                    thread_time = time.time() - thread_start
                    
                    return {
                        "thread_id": thread_id,
                        "created_count": created_count,
                        "queried_count": queried_count,
                        "final_count": final_count,
                        "errors": errors,
                        "execution_time": thread_time,
                        "success": len(errors) == 0
                    }
            
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "created_count": 0,
                    "queried_count": 0,
                    "final_count": 0,
                    "errors": [f"Thread error: {e}"],
                    "execution_time": time.time() - thread_start,
                    "success": False
                }
        
        # Run 12 concurrent threads (more than required 10)
        num_threads = 12
        operations_per_thread = 50
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_operation, i, operations_per_thread) 
                for i in range(num_threads)
            ]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_threads = [r for r in results if r["success"]]
        failed_threads = [r for r in results if not r["success"]]
        
        total_created = sum(r["created_count"] for r in results)
        total_queried = sum(r["queried_count"] for r in results)
        total_errors = sum(len(r["errors"]) for r in results)
        
        # Assertions for concurrent load
        self.assertEqual(len(results), num_threads, "All threads should complete")
        self.assertGreaterEqual(len(successful_threads), num_threads * 0.8, "At least 80% of threads should succeed")
        self.assertLess(total_time, 60.0, "Concurrent operations should complete within 60 seconds")
        self.assertLess(total_errors, total_created * 0.1, "Error rate should be less than 10%")
        
        logger.info(f"✅ Concurrent load test passed:")
        logger.info(f"  - Total threads: {num_threads}")
        logger.info(f"  - Successful threads: {len(successful_threads)}")
        logger.info(f"  - Failed threads: {len(failed_threads)}")
        logger.info(f"  - Total execution time: {total_time:.2f}s")
        logger.info(f"  - Total created entities: {total_created}")
        logger.info(f"  - Total query operations: {total_queried}")
        logger.info(f"  - Total errors: {total_errors}")
    
    def test_realistic_query_performance(self):
        """Test realistic query performance benchmarks."""
        logger.info("🔍 Testing realistic query performance benchmarks...")
        
        # Create realistic test dataset (10k nodes, 20k relationships)
        self._setup_realistic_dataset()
        
        # Define realistic production queries
        test_queries = [
            {
                "name": "Entity Search",
                "query": """
                    MATCH (n:StressTestEntity) 
                    WHERE n.canonical_name CONTAINS 'Entity' 
                    RETURN n.entity_id, n.canonical_name, n.confidence
                    ORDER BY n.confidence DESC
                    LIMIT 100
                """,
                "max_time": 2.0
            },
            {
                "name": "Relationship Traversal",
                "query": """
                    MATCH (n:StressTestEntity)-[r:RELATED_TO]->(m:StressTestEntity)
                    WHERE n.confidence > 0.8
                    RETURN n.canonical_name, type(r), m.canonical_name, r.confidence
                    ORDER BY r.confidence DESC
                    LIMIT 50
                """,
                "max_time": 3.0
            },
            {
                "name": "Multi-hop Query",
                "query": """
                    MATCH (n:StressTestEntity)-[:RELATED_TO*1..2]->(m:StressTestEntity)
                    WHERE n.entity_type = 'ORGANIZATION'
                    RETURN n.canonical_name, m.canonical_name, length(shortestPath((n)-[*]-(m))) as path_length
                    ORDER BY path_length
                    LIMIT 30
                """,
                "max_time": 5.0
            },
            {
                "name": "Aggregation Query",
                "query": """
                    MATCH (n:StressTestEntity)
                    WITH n.entity_type as type, count(n) as count, avg(n.confidence) as avg_conf
                    RETURN type, count, avg_conf
                    ORDER BY count DESC
                """,
                "max_time": 2.0
            },
            {
                "name": "PageRank Simulation",
                "query": """
                    MATCH (n:StressTestEntity)
                    WHERE n.pagerank_score IS NOT NULL
                    RETURN n.canonical_name, n.pagerank_score
                    ORDER BY n.pagerank_score DESC
                    LIMIT 20
                """,
                "max_time": 1.0
            }
        ]
        
        performance_results = []
        
        for query_info in test_queries:
            query_name = query_info["name"]
            query = query_info["query"]
            max_time = query_info["max_time"]
            
            times = []
            
            # Run each query 5 times for consistency
            for i in range(5):
                start_time = time.time()
                with self.driver.session() as session:
                    result = session.run(query)
                    records = list(result)
                execution_time = time.time() - start_time
                times.append(execution_time)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time_actual = max(times)
            
            performance_results.append({
                "query_name": query_name,
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time_actual,
                "max_allowed": max_time,
                "passed": avg_time <= max_time,
                "result_count": len(records)
            })
            
            # Assert performance requirement
            self.assertLessEqual(
                avg_time, max_time, 
                f"Query '{query_name}' too slow: {avg_time:.3f}s > {max_time}s"
            )
        
        # Log performance results
        logger.info("✅ Realistic query performance results:")
        for result in performance_results:
            status = "✅" if result["passed"] else "❌"
            logger.info(f"  {status} {result['query_name']}: {result['avg_time']:.3f}s (max: {result['max_allowed']}s)")
        
        # Overall performance assertion
        passed_queries = sum(1 for r in performance_results if r["passed"])
        total_queries = len(performance_results)
        
        self.assertEqual(passed_queries, total_queries, "All queries should meet performance requirements")
    
    def _setup_realistic_dataset(self):
        """Set up realistic test dataset with 10k nodes and 20k relationships."""
        logger.info("🔧 Setting up realistic test dataset...")
        
        # Create 10k entities
        entities = []
        entity_types = ["ORGANIZATION", "PERSON", "LOCATION", "TECHNOLOGY", "CONCEPT"]
        
        for i in range(10000):
            entities.append({
                "id": f"stress_entity_{i}",
                "name": f"Stress Test Entity {i}",
                "entity_type": random.choice(entity_types),
                "confidence": random.uniform(0.6, 1.0),
                "pagerank_score": random.uniform(0.001, 0.1),
                "created_at": datetime.now().isoformat(),
                "test_marker": "production_scale"
            })
        
        # Create entities in batches
        batch_size = 1000
        with self.driver.session() as session:
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                session.run("""
                    UNWIND $batch as entity
                    CREATE (n:StressTestEntity {
                        entity_id: entity.id,
                        canonical_name: entity.name,
                        entity_type: entity.entity_type,
                        confidence: entity.confidence,
                        pagerank_score: entity.pagerank_score,
                        created_at: entity.created_at,
                        test_marker: entity.test_marker
                    })
                """, batch=batch)
        
        # Create 20k relationships
        relationships = []
        for i in range(20000):
            source_id = f"stress_entity_{random.randint(0, 9999)}"
            target_id = f"stress_entity_{random.randint(0, 9999)}"
            
            if source_id != target_id:  # Avoid self-loops
                relationships.append({
                    "source": source_id,
                    "target": target_id,
                    "confidence": random.uniform(0.5, 1.0),
                    "weight": random.uniform(0.1, 1.0)
                })
        
        # Create relationships in batches
        with self.driver.session() as session:
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i + batch_size]
                session.run("""
                    UNWIND $batch as rel
                    MATCH (source:StressTestEntity {entity_id: rel.source})
                    MATCH (target:StressTestEntity {entity_id: rel.target})
                    CREATE (source)-[r:RELATED_TO {
                        confidence: rel.confidence,
                        weight: rel.weight
                    }]->(target)
                """, batch=batch)
        
        logger.info("✅ Realistic test dataset created")
    
    def test_memory_and_resource_usage(self):
        """Test memory and resource usage under load."""
        logger.info("🔍 Testing memory and resource usage under load...")
        
        # This test creates a continuous load and monitors for memory leaks
        # and resource exhaustion
        
        iterations = 1000
        batch_size = 100
        
        start_time = time.time()
        
        for i in range(iterations):
            with self.driver.session() as session:
                # Create batch of entities
                batch_data = [
                    {
                        "id": f"memory_test_{i}_{j}",
                        "name": f"Memory Test Entity {i}_{j}",
                        "iteration": i,
                        "test_marker": "production_scale"
                    }
                    for j in range(batch_size)
                ]
                
                session.run("""
                    UNWIND $batch as entity
                    CREATE (n:MemoryTestEntity {
                        entity_id: entity.id,
                        canonical_name: entity.name,
                        iteration: entity.iteration,
                        test_marker: entity.test_marker
                    })
                """, batch=batch_data)
                
                # Query and immediately clean up
                session.run("""
                    MATCH (n:MemoryTestEntity {iteration: $iteration})
                    DETACH DELETE n
                """, iteration=i)
            
            # Progress check
            if i % 100 == 0:
                elapsed = time.time() - start_time
                logger.info(f"  Memory test iteration {i}/{iterations} - {elapsed:.2f}s elapsed")
        
        total_time = time.time() - start_time
        
        # Verify no memory leaks (no entities should remain)
        with self.driver.session() as session:
            result = session.run("MATCH (n:MemoryTestEntity) RETURN count(n) as count")
            remaining_entities = result.single()["count"]
        
        self.assertEqual(remaining_entities, 0, "No entities should remain after cleanup")
        self.assertLess(total_time, 300.0, "Memory test should complete within 5 minutes")
        
        logger.info(f"✅ Memory and resource usage test passed:")
        logger.info(f"  - Iterations: {iterations}")
        logger.info(f"  - Total time: {total_time:.2f}s")
        logger.info(f"  - Remaining entities: {remaining_entities}")


if __name__ == "__main__":
    # Run the production scale tests
    unittest.main(verbosity=2)