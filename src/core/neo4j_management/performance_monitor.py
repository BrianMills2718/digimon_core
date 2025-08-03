"""
Performance Monitor

Handles Neo4j performance monitoring, index optimization, and metrics collection.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .neo4j_types import Neo4jConfig, PerformanceMetrics, QueryError
from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors Neo4j database performance and handles optimization."""
    
    def __init__(self, config: Neo4jConfig, connection_manager: ConnectionManager):
        self.config = config
        self.connection_manager = connection_manager
        self.performance_history: List[PerformanceMetrics] = []
        self.optimization_history: List[Dict[str, Any]] = []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Neo4j database."""
        try:
            # Try to get a driver and execute a simple query
            driver = self.connection_manager.get_driver()
            
            start_time = time.time()
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()['test']
            
            response_time = time.time() - start_time
            
            if test_value == 1:
                status = {
                    'status': 'healthy',
                    'message': 'Neo4j database is responding normally',
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add detailed health metrics
                status.update(self._get_detailed_health_metrics())
                return status
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Neo4j database returned unexpected result',
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Neo4j database connection failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_detailed_health_metrics(self) -> Dict[str, Any]:
        """Get detailed health metrics for the database."""
        try:
            driver = self.connection_manager.get_driver()
            metrics = {}
            
            with driver.session() as session:
                # Get basic counts
                start_time = time.time()
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = result.single()["node_count"]
                node_query_time = time.time() - start_time
                
                start_time = time.time()
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()["rel_count"]
                rel_query_time = time.time() - start_time
                
                # Get memory info if available
                try:
                    result = session.run("CALL dbms.listConfig() YIELD name, value WHERE name CONTAINS 'memory' RETURN name, value")
                    memory_config = {record["name"]: record["value"] for record in result}
                except Exception:
                    memory_config = {}
                
                metrics.update({
                    'node_count': node_count,
                    'relationship_count': rel_count,
                    'node_count_query_time': node_query_time,
                    'relationship_count_query_time': rel_query_time,
                    'memory_config': memory_config
                })
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to get detailed health metrics: {e}")
            return {}
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current database performance metrics."""
        driver = self.connection_manager.get_driver()
        
        metrics_data = {
            "operation": "performance_assessment",
            "execution_time": 0.0,
            "timestamp": datetime.now()
        }
        
        total_start_time = time.time()
        
        with driver.session() as session:
            try:
                # Test basic query performance
                start_time = time.time()
                result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                node_count = result.single()["total_nodes"]
                node_count_time = time.time() - start_time
                
                # Test relationship count performance
                start_time = time.time()
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
                rel_count = result.single()["total_relationships"]
                rel_count_time = time.time() - start_time
                
                # Test index usage
                start_time = time.time()
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                index_query_time = time.time() - start_time
                
                # Calculate total execution time
                total_execution_time = time.time() - total_start_time
                
                metrics = PerformanceMetrics(
                    operation="performance_assessment",
                    execution_time=total_execution_time,
                    node_count=node_count,
                    relationship_count=rel_count,
                    index_count=len(indexes),
                    query_complexity="basic_assessment",
                    timestamp=datetime.now()
                )
                
                # Store in history
                self.performance_history.append(metrics)
                
                # Keep only last 100 measurements
                if len(self.performance_history) > 100:
                    self.performance_history = self.performance_history[-100:]
                
                logger.info(f"Performance assessment completed in {total_execution_time:.3f}s")
                return metrics
                
            except Exception as e:
                logger.error(f"Performance metrics collection failed: {e}")
                raise QueryError(f"Performance metrics collection failed: {e}")
    
    def create_optimized_indexes(self) -> Dict[str, Any]:
        """Create optimized indexes for production scale performance."""
        driver = self.connection_manager.get_driver()
        
        index_queries = [
            "CREATE INDEX entity_id_index IF NOT EXISTS FOR (n:Entity) ON (n.entity_id)",
            "CREATE INDEX entity_canonical_name_index IF NOT EXISTS FOR (n:Entity) ON (n.canonical_name)",
            "CREATE INDEX relationship_type_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.type)",
            "CREATE INDEX relationship_confidence_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.confidence)",
            "CREATE INDEX mention_surface_form_index IF NOT EXISTS FOR (m:Mention) ON (m.surface_form)",
            "CREATE INDEX pagerank_score_index IF NOT EXISTS FOR (n:Entity) ON (n.pagerank_score)",
            "CREATE INDEX document_source_index IF NOT EXISTS FOR (d:Document) ON (d.source_ref)",
            "CREATE INDEX chunk_reference_index IF NOT EXISTS FOR (c:Chunk) ON (c.chunk_ref)"
        ]
        
        created_indexes = []
        failed_indexes = []
        start_time = time.time()
        
        with driver.session() as session:
            for query in index_queries:
                try:
                    index_start = time.time()
                    session.run(query)
                    index_time = time.time() - index_start
                    
                    # Extract index name from query
                    index_name = "unknown"
                    if "FOR" in query and "ON" in query:
                        try:
                            index_name = query.split("FOR")[1].split("ON")[0].strip()
                        except IndexError:
                            pass
                    
                    created_indexes.append({
                        "index": index_name,
                        "creation_time": index_time,
                        "query": query
                    })
                    
                    logger.info(f"Created index '{index_name}' in {index_time:.3f}s")
                    
                except Exception as e:
                    error_msg = str(e)
                    failed_indexes.append({
                        "query": query,
                        "error": error_msg
                    })
                    
                    # Only log as warning if it's not "already exists" error
                    if "already exists" in error_msg.lower():
                        logger.debug(f"Index already exists: {query}")
                    else:
                        logger.warning(f"Index creation failed: {e}")
        
        total_time = time.time() - start_time
        
        optimization_result = {
            "indexes_created": len(created_indexes),
            "indexes_failed": len(failed_indexes),
            "total_time": total_time,
            "created_details": created_indexes,
            "failed_details": failed_indexes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in optimization history
        self.optimization_history.append(optimization_result)
        
        logger.info(f"Index optimization completed in {total_time:.3f}s: {len(created_indexes)} created, {len(failed_indexes)} failed")
        
        return optimization_result
    
    def analyze_query_performance(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze performance of a specific query."""
        if params is None:
            params = {}
        
        driver = self.connection_manager.get_driver()
        
        with driver.session() as session:
            try:
                # Execute query with timing
                start_time = time.time()
                result = session.run(query, params)
                records = list(result)
                execution_time = time.time() - start_time
                
                # Try to get query plan (if supported)
                plan_info = {}
                try:
                    plan_result = session.run(f"EXPLAIN {query}", params)
                    plan_info = {"plan_available": True, "explained": True}
                except Exception:
                    plan_info = {"plan_available": False, "explained": False}
                
                analysis = {
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "execution_time": execution_time,
                    "record_count": len(records),
                    "records_per_second": len(records) / execution_time if execution_time > 0 else 0,
                    "plan_info": plan_info,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Categorize performance
                if execution_time < 0.1:
                    analysis["performance_category"] = "excellent"
                elif execution_time < 1.0:
                    analysis["performance_category"] = "good"
                elif execution_time < 5.0:
                    analysis["performance_category"] = "acceptable"
                else:
                    analysis["performance_category"] = "slow"
                
                return analysis
                
            except Exception as e:
                logger.error(f"Query performance analysis failed: {e}")
                return {
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about database indexes."""
        driver = self.connection_manager.get_driver()
        
        with driver.session() as session:
            try:
                # Get index information
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                
                # Categorize indexes
                btree_indexes = []
                text_indexes = []
                other_indexes = []
                
                for index in indexes:
                    index_type = index.get("type", "unknown")
                    index_info = {
                        "name": index.get("name", "unnamed"),
                        "type": index_type,
                        "state": index.get("state", "unknown"),
                        "labels": index.get("labelsOrTypes", []),
                        "properties": index.get("properties", [])
                    }
                    
                    if "BTREE" in index_type.upper():
                        btree_indexes.append(index_info)
                    elif "TEXT" in index_type.upper():
                        text_indexes.append(index_info)
                    else:
                        other_indexes.append(index_info)
                
                return {
                    "total_indexes": len(indexes),
                    "btree_indexes": btree_indexes,
                    "text_indexes": text_indexes,
                    "other_indexes": other_indexes,
                    "btree_count": len(btree_indexes),
                    "text_count": len(text_indexes),
                    "other_count": len(other_indexes),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get index statistics: {e}")
                return {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    def get_performance_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get performance metrics history."""
        history = self.performance_history
        
        if limit:
            history = history[-limit:]
        
        return [
            {
                "operation": metric.operation,
                "execution_time": metric.execution_time,
                "node_count": metric.node_count,
                "relationship_count": metric.relationship_count,
                "index_count": metric.index_count,
                "query_complexity": metric.query_complexity,
                "timestamp": metric.timestamp.isoformat() if metric.timestamp else None
            }
            for metric in history
        ]
    
    def get_optimization_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get optimization operation history."""
        history = self.optimization_history
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_performance_history(self) -> None:
        """Clear performance metrics history."""
        self.performance_history.clear()
        logger.info("Performance history cleared")
    
    def get_database_size_info(self) -> Dict[str, Any]:
        """Get database size and storage information."""
        driver = self.connection_manager.get_driver()
        
        with driver.session() as session:
            try:
                # Get node and relationship counts
                node_result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = node_result.single()["node_count"]
                
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = rel_result.single()["rel_count"]
                
                # Try to get storage size (may not be available in all Neo4j versions)
                storage_info = {}
                try:
                    storage_result = session.run("CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Store file sizes') YIELD attributes")
                    storage_data = list(storage_result)
                    if storage_data:
                        storage_info = {"jmx_available": True, "details": storage_data}
                except Exception:
                    storage_info = {"jmx_available": False}
                
                return {
                    "node_count": node_count,
                    "relationship_count": rel_count,
                    "total_entities": node_count + rel_count,
                    "storage_info": storage_info,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get database size info: {e}")
                return {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }