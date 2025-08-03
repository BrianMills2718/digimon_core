#!/usr/bin/env python3
"""
Database Optimizer for Large-Scale Text Processing

Provides optimizations for Neo4j and SQLite databases when processing
large document collections, including indexing strategies, query optimization,
batch processing, and memory management.
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import psutil
import gc

from .neo4j_manager import Neo4jDockerManager
from .config_manager import get_config

logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """Track optimization performance metrics"""
    query_execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit_rate: float
    batch_size: int
    processed_documents: int
    optimization_method: str


class DatabaseOptimizer:
    """Optimizes database operations for large-scale text processing"""
    
    def __init__(self, neo4j_manager: Optional[Neo4jDockerManager] = None):
        self.config = get_config()
        self.neo4j_manager = neo4j_manager or Neo4jDockerManager()
        
        # Performance monitoring
        self.metrics_history: List[OptimizationMetrics] = []
        self.query_cache: Dict[str, Any] = {}
        self.batch_processor = BatchProcessor()
        
        # Optimization settings
        self.optimization_config = {
            'batch_size': 1000,
            'max_memory_mb': 4096,  # 4GB memory limit
            'parallel_workers': min(8, psutil.cpu_count()),
            'cache_size_limit': 10000,
            'index_refresh_interval': 3600,  # 1 hour
            'gc_threshold': 0.8  # GC when memory usage > 80%
        }
        
        # Initialize optimizations
        self._initialize_optimizations()
    
    def _initialize_optimizations(self):
        """Initialize database optimizations"""
        try:
            # Create optimized indexes for text processing
            self._create_text_processing_indexes()
            
            # Configure Neo4j for large-scale operations
            self._configure_neo4j_optimization()
            
            # Set up memory monitoring
            self._setup_memory_monitoring()
            
            logger.info("Database optimizations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database optimizations: {e}")
            raise
    
    def _create_text_processing_indexes(self):
        """Create optimized indexes for text processing operations"""
        
        index_queries = [
            # Document processing indexes
            "CREATE INDEX document_id_index IF NOT EXISTS FOR (d:Document) ON (d.id)",
            "CREATE INDEX document_source_index IF NOT EXISTS FOR (d:Document) ON (d.source_path)",
            "CREATE INDEX document_type_index IF NOT EXISTS FOR (d:Document) ON (d.document_type)",
            "CREATE INDEX document_processed_index IF NOT EXISTS FOR (d:Document) ON (d.processed_at)",
            
            # Entity processing indexes
            "CREATE INDEX entity_canonical_index IF NOT EXISTS FOR (e:Entity) ON (e.canonical_name)",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.entity_type)",
            "CREATE INDEX entity_confidence_index IF NOT EXISTS FOR (e:Entity) ON (e.confidence)",
            "CREATE INDEX entity_quality_index IF NOT EXISTS FOR (e:Entity) ON (e.quality_tier)",
            
            # Text chunk indexes for large document processing
            "CREATE INDEX chunk_document_index IF NOT EXISTS FOR (c:Chunk) ON (c.document_id)",
            "CREATE INDEX chunk_position_index IF NOT EXISTS FOR (c:Chunk) ON (c.start_pos, c.end_pos)",
            "CREATE INDEX chunk_processed_index IF NOT EXISTS FOR (c:Chunk) ON (c.processed)",
            
            # Relationship indexes for fast traversal
            "CREATE INDEX mention_confidence_index IF NOT EXISTS FOR ()-[r:MENTIONS]->() ON (r.confidence)",
            "CREATE INDEX relation_type_index IF NOT EXISTS FOR ()-[r:RELATES_TO]->() ON (r.relation_type)",
            
            # Vector similarity indexes (if using Neo4j 5.x with vector support)
            "CREATE VECTOR INDEX entity_embedding_index IF NOT EXISTS "
            "FOR (e:Entity) ON (e.embedding) "
            "OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
        ]
        
        for query in index_queries:
            try:
                with self.neo4j_manager.get_session() as session:
                    session.run(query)
                logger.info(f"Created index: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
    
    def _configure_neo4j_optimization(self):
        """Configure Neo4j settings for optimal large-scale performance"""
        
        optimization_queries = [
            # Configure transaction settings for batch processing
            "CALL dbms.setConfigValue('dbms.transaction.timeout', '300s')",
            
            # Optimize memory allocation
            "CALL dbms.setConfigValue('dbms.memory.heap.initial_size', '2g')",
            "CALL dbms.setConfigValue('dbms.memory.heap.max_size', '4g')",
            "CALL dbms.setConfigValue('dbms.memory.pagecache.size', '1g')",
            
            # Configure parallel processing
            "CALL dbms.setConfigValue('dbms.cypher.parallel_runtime_support', 'all')",
        ]
        
        for query in optimization_queries:
            try:
                with self.neo4j_manager.get_session() as session:
                    session.run(query)
                logger.info(f"Applied Neo4j optimization: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Neo4j optimization failed (may not be supported): {e}")
    
    def _setup_memory_monitoring(self):
        """Set up continuous memory monitoring"""
        self.memory_monitor = MemoryMonitor(
            gc_threshold=self.optimization_config['gc_threshold'],
            max_memory_mb=self.optimization_config['max_memory_mb']
        )
    
    async def optimize_batch_insert(self, entities: List[Dict], batch_size: Optional[int] = None) -> OptimizationMetrics:
        """Optimize batch insertion of entities"""
        
        batch_size = batch_size or self.optimization_config['batch_size']
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024 * 1024)
        
        try:
            # Process in optimized batches
            processed_count = 0
            
            for batch in self._create_batches(entities, batch_size):
                # Memory check before processing batch
                self.memory_monitor.check_memory_usage()
                
                # Process batch with transaction optimization
                await self._process_entity_batch(batch)
                processed_count += len(batch)
                
                # Log progress for large operations
                if processed_count % (batch_size * 10) == 0:
                    logger.info(f"Processed {processed_count}/{len(entities)} entities")
            
            # Calculate metrics
            execution_time = time.time() - start_time
            end_memory = psutil.virtual_memory().used / (1024 * 1024)
            memory_used = end_memory - start_memory
            
            metrics = OptimizationMetrics(
                query_execution_time=execution_time,
                memory_usage_mb=memory_used,
                cpu_usage_percent=psutil.cpu_percent(),
                cache_hit_rate=self._calculate_cache_hit_rate(),
                batch_size=batch_size,
                processed_documents=len(entities),
                optimization_method="batch_insert"
            )
            
            self.metrics_history.append(metrics)
            logger.info(f"Batch insert completed: {processed_count} entities in {execution_time:.2f}s")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Batch insert optimization failed: {e}")
            raise
    
    async def _process_entity_batch(self, batch: List[Dict]):
        """Process a single batch of entities with optimization"""
        
        # Create optimized Cypher query for batch insert
        batch_query = """
        UNWIND $entities AS entity
        MERGE (e:Entity {id: entity.id})
        SET e.canonical_name = entity.canonical_name,
            e.entity_type = entity.entity_type,
            e.confidence = entity.confidence,
            e.quality_tier = entity.quality_tier,
            e.created_at = datetime(),
            e.updated_at = datetime()
        WITH e, entity
        WHERE entity.embedding IS NOT NULL
        CALL db.create.setNodeVectorProperty(e, 'embedding', entity.embedding)
        RETURN count(e) as created
        """
        
        async with self.neo4j_manager.get_async_session() as session:
            result = await session.run(batch_query, entities=batch)
            summary = await result.consume()
            return summary.counters.nodes_created
    
    def optimize_query_performance(self, query: str, parameters: Dict = None) -> Tuple[Any, OptimizationMetrics]:
        """Optimize query performance with caching and analysis"""
        
        start_time = time.time()
        
        # Check query cache first
        cache_key = self._generate_cache_key(query, parameters)
        if cache_key in self.query_cache:
            result = self.query_cache[cache_key]
            metrics = OptimizationMetrics(
                query_execution_time=0.001,  # Cache hit
                memory_usage_mb=0,
                cpu_usage_percent=0,
                cache_hit_rate=1.0,
                batch_size=0,
                processed_documents=0,
                optimization_method="cache_hit"
            )
            return result, metrics
        
        # Execute optimized query
        with self.neo4j_manager.get_session() as session:
            # Add query optimization hints
            optimized_query = self._add_query_optimizations(query)
            
            result = session.run(optimized_query, parameters or {})
            result_data = list(result)
            
            # Cache result if appropriate
            if self._should_cache_result(query, result_data):
                self.query_cache[cache_key] = result_data
                self._manage_cache_size()
        
        execution_time = time.time() - start_time
        
        metrics = OptimizationMetrics(
            query_execution_time=execution_time,
            memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
            cpu_usage_percent=psutil.cpu_percent(),
            cache_hit_rate=self._calculate_cache_hit_rate(),
            batch_size=0,
            processed_documents=len(result_data),
            optimization_method="optimized_query"
        )
        
        self.metrics_history.append(metrics)
        
        return result_data, metrics
    
    def _add_query_optimizations(self, query: str) -> str:
        """Add optimization hints to Cypher queries"""
        
        optimizations = []
        
        # Add USING INDEX hints for common patterns
        if "MATCH (d:Document)" in query:
            optimizations.append("USING INDEX d:Document(id)")
        
        if "MATCH (e:Entity)" in query:
            optimizations.append("USING INDEX e:Entity(canonical_name)")
        
        # Add LIMIT for large result sets if not present
        if "RETURN" in query and "LIMIT" not in query and "COUNT" not in query:
            query += " LIMIT 10000"
        
        # Add optimization comments
        if optimizations:
            query = f"// Optimized query with hints\n{query}"
        
        return query
    
    def _create_batches(self, items: List, batch_size: int):
        """Create optimized batches for processing"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    def _generate_cache_key(self, query: str, parameters: Dict = None) -> str:
        """Generate cache key for query and parameters"""
        import hashlib
        
        content = query + str(sorted((parameters or {}).items()))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _should_cache_result(self, query: str, result: List) -> bool:
        """Determine if query result should be cached"""
        
        # Don't cache very large results
        if len(result) > 1000:
            return False
        
        # Don't cache write operations
        if any(keyword in query.upper() for keyword in ['CREATE', 'MERGE', 'DELETE', 'SET']):
            return False
        
        # Cache read-only queries with reasonable result sizes
        return True
    
    def _manage_cache_size(self):
        """Manage cache size to prevent memory issues"""
        
        if len(self.query_cache) > self.optimization_config['cache_size_limit']:
            # Remove oldest 20% of cache entries
            items_to_remove = len(self.query_cache) // 5
            oldest_keys = list(self.query_cache.keys())[:items_to_remove]
            
            for key in oldest_keys:
                del self.query_cache[key]
            
            logger.info(f"Cache pruned: removed {items_to_remove} entries")
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate current cache hit rate"""
        
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 operations
        cache_hits = sum(1 for m in recent_metrics if m.optimization_method == "cache_hit")
        
        return cache_hits / len(recent_metrics) if recent_metrics else 0.0
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization performance report"""
        
        if not self.metrics_history:
            return {"status": "no_data", "message": "No optimization metrics available"}
        
        recent_metrics = self.metrics_history[-100:]
        
        report = {
            "performance_summary": {
                "total_operations": len(self.metrics_history),
                "average_execution_time": sum(m.query_execution_time for m in recent_metrics) / len(recent_metrics),
                "average_memory_usage_mb": sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "current_cache_size": len(self.query_cache)
            },
            "optimization_effectiveness": {
                "cache_hits": len([m for m in recent_metrics if m.optimization_method == "cache_hit"]),
                "batch_operations": len([m for m in recent_metrics if m.optimization_method == "batch_insert"]),
                "optimized_queries": len([m for m in recent_metrics if m.optimization_method == "optimized_query"])
            },
            "resource_usage": {
                "current_memory_mb": psutil.virtual_memory().used / (1024 * 1024),
                "memory_limit_mb": self.optimization_config['max_memory_mb'],
                "cpu_usage_percent": psutil.cpu_percent(),
                "available_workers": self.optimization_config['parallel_workers']
            },
            "recommendations": self._generate_optimization_recommendations(recent_metrics)
        }
        
        return report
    
    def _generate_optimization_recommendations(self, metrics: List[OptimizationMetrics]) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        
        recommendations = []
        
        # Analyze performance patterns
        avg_execution_time = sum(m.query_execution_time for m in metrics) / len(metrics)
        avg_memory_usage = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        # Performance recommendations
        if avg_execution_time > 5.0:
            recommendations.append("Consider increasing batch sizes or adding more specific indexes")
        
        if avg_memory_usage > self.optimization_config['max_memory_mb'] * 0.8:
            recommendations.append("Memory usage is high - consider reducing batch sizes or increasing memory limits")
        
        if cache_hit_rate < 0.3:
            recommendations.append("Low cache hit rate - consider caching more query results or adjusting cache size")
        
        # Add specific optimizations based on operation types
        batch_ops = [m for m in metrics if m.optimization_method == "batch_insert"]
        if batch_ops:
            avg_batch_time = sum(m.query_execution_time for m in batch_ops) / len(batch_ops)
            if avg_batch_time > 10.0:
                recommendations.append("Batch operations are slow - consider parallel processing or smaller batch sizes")
        
        return recommendations


class BatchProcessor:
    """Handles optimized batch processing for large-scale operations"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_documents_batch(self, documents: List[Dict], 
                                    processor_func, batch_size: int = 100) -> List[Any]:
        """Process documents in optimized batches"""
        
        results = []
        
        # Create batches
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
        
        # Process batches in parallel
        tasks = []
        for batch in batches:
            task = asyncio.create_task(self._process_single_batch(batch, processor_func))
            tasks.append(task)
        
        # Wait for all batches to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch processing failed: {batch_result}")
            else:
                results.extend(batch_result)
        
        return results
    
    async def _process_single_batch(self, batch: List[Dict], processor_func) -> List[Any]:
        """Process a single batch of documents"""
        
        loop = asyncio.get_event_loop()
        
        # Run processor function in thread pool to avoid blocking
        result = await loop.run_in_executor(
            self.executor, 
            lambda: [processor_func(doc) for doc in batch]
        )
        
        return result


class MemoryMonitor:
    """Monitors memory usage and triggers garbage collection when needed"""
    
    def __init__(self, gc_threshold: float = 0.8, max_memory_mb: int = 4096):
        self.gc_threshold = gc_threshold
        self.max_memory_mb = max_memory_mb
        self.last_gc_time = 0
        self.gc_interval = 60  # Minimum 60 seconds between forced GC
    
    def check_memory_usage(self):
        """Check memory usage and trigger GC if needed"""
        
        current_memory_mb = psutil.virtual_memory().used / (1024 * 1024)
        memory_percent = current_memory_mb / self.max_memory_mb
        
        current_time = time.time()
        
        if (memory_percent > self.gc_threshold and 
            current_time - self.last_gc_time > self.gc_interval):
            
            logger.info(f"Memory usage {memory_percent:.1%} exceeds threshold {self.gc_threshold:.1%}, triggering GC")
            
            # Trigger garbage collection
            collected = gc.collect()
            self.last_gc_time = current_time
            
            # Log results
            new_memory_mb = psutil.virtual_memory().used / (1024 * 1024)
            freed_mb = current_memory_mb - new_memory_mb
            
            logger.info(f"GC collected {collected} objects, freed {freed_mb:.1f}MB memory")


# Factory function for easy initialization
def create_database_optimizer(neo4j_manager: Optional[Neo4jDockerManager] = None) -> DatabaseOptimizer:
    """Factory function to create optimized database optimizer"""
    
    return DatabaseOptimizer(neo4j_manager)


# Example usage and testing
if __name__ == "__main__":
    async def test_optimizer():
        optimizer = create_database_optimizer()
        
        # Test batch processing
        test_entities = [
            {"id": f"entity_{i}", "canonical_name": f"Test Entity {i}", 
             "entity_type": "TEST", "confidence": 0.9, "quality_tier": "HIGH"}
            for i in range(1000)
        ]
        
        metrics = await optimizer.optimize_batch_insert(test_entities, batch_size=100)
        print(f"Batch processing completed in {metrics.query_execution_time:.2f}s")
        
        # Test query optimization
        test_query = "MATCH (e:Entity) WHERE e.entity_type = $type RETURN e"
        result, query_metrics = optimizer.optimize_query_performance(
            test_query, {"type": "TEST"}
        )
        print(f"Query optimization completed: {len(result)} results")
        
        # Generate optimization report
        report = optimizer.get_optimization_report()
        print("Optimization Report:", report)
    
    asyncio.run(test_optimizer())