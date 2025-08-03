"""
Query Executor

Handles secure query execution, batch processing, and transaction management.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .neo4j_types import Neo4jConfig, QueryError, ValidationError
from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes Neo4j queries with security validation and performance optimization."""
    
    def __init__(self, config: Neo4jConfig, connection_manager: ConnectionManager, input_validator=None):
        self.config = config
        self.connection_manager = connection_manager
        self.input_validator = input_validator
        self.query_stats = {
            "total_queries": 0,
            "total_execution_time": 0.0,
            "error_count": 0,
            "batch_count": 0
        }
    
    def execute_secure_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query with mandatory security validation."""
        if params is None:
            params = {}
        
        # Validate query and parameters for security
        if self.input_validator:
            try:
                validated = self.input_validator.enforce_parameterized_execution(query, params)
                safe_query = validated['query']
                safe_params = validated['params']
            except ValueError as e:
                logger.error(f"Query validation failed: {e}")
                self.query_stats["error_count"] += 1
                raise ValidationError(f"Query validation failed: {e}")
        else:
            safe_query = query
            safe_params = params
            logger.warning("No input validator available - executing query without validation")
        
        # Execute with validated parameters
        start_time = time.time()
        
        try:
            driver = self.connection_manager.get_driver()
            with driver.session() as session:
                result = session.run(safe_query, safe_params)
                records = [dict(record) for record in result]
                
                # Update statistics
                execution_time = time.time() - start_time
                self.query_stats["total_queries"] += 1
                self.query_stats["total_execution_time"] += execution_time
                
                logger.debug(f"Query executed successfully in {execution_time:.3f}s, returned {len(records)} records")
                return records
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.query_stats["error_count"] += 1
            logger.error(f"Query execution failed after {execution_time:.3f}s: {e}")
            raise QueryError(f"Query execution failed: {e}")
    
    def execute_secure_write_transaction(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute write transaction with security validation."""
        if params is None:
            params = {}
        
        # Validate query and parameters
        if self.input_validator:
            try:
                validated = self.input_validator.enforce_parameterized_execution(query, params)
                safe_query = validated['query']
                safe_params = validated['params']
            except ValueError as e:
                logger.error(f"Write transaction validation failed: {e}")
                self.query_stats["error_count"] += 1
                raise ValidationError(f"Write transaction validation failed: {e}")
        else:
            safe_query = query
            safe_params = params
            logger.warning("No input validator available - executing transaction without validation")
        
        start_time = time.time()
        
        try:
            driver = self.connection_manager.get_driver()
            with driver.session() as session:
                with session.begin_transaction() as tx:
                    result = tx.run(safe_query, safe_params)
                    summary = result.consume()
                    tx.commit()
                    
                    execution_time = time.time() - start_time
                    
                    transaction_result = {
                        'nodes_created': summary.counters.nodes_created,
                        'nodes_deleted': summary.counters.nodes_deleted,
                        'relationships_created': summary.counters.relationships_created,
                        'relationships_deleted': summary.counters.relationships_deleted,
                        'properties_set': summary.counters.properties_set,
                        'query_time': summary.result_available_after + summary.result_consumed_after,
                        'execution_time': execution_time
                    }
                    
                    # Update statistics
                    self.query_stats["total_queries"] += 1
                    self.query_stats["total_execution_time"] += execution_time
                    
                    logger.info(f"Write transaction completed in {execution_time:.3f}s: {transaction_result}")
                    return transaction_result
                    
        except Exception as e:
            execution_time = time.time() - start_time
            self.query_stats["error_count"] += 1
            logger.error(f"Write transaction failed after {execution_time:.3f}s: {e}")
            raise QueryError(f"Write transaction failed: {e}")
    
    def execute_optimized_batch(self, queries_with_params: List[Tuple[str, Dict[str, Any]]], 
                               batch_size: int = 1000) -> Dict[str, Any]:
        """Execute queries in optimized batches with security validation."""
        if not queries_with_params:
            raise ValidationError("No queries provided for batch execution")
        
        results = []
        start_time = time.time()
        
        # Pre-validate all queries for security
        validated_queries = []
        for query, params in queries_with_params:
            if self.input_validator:
                try:
                    validated = self.input_validator.enforce_parameterized_execution(query, params or {})
                    validated_queries.append((validated['query'], validated['params']))
                except ValueError as e:
                    logger.error(f"Batch query validation failed: {e}")
                    self.query_stats["error_count"] += 1
                    raise ValidationError(f"Batch query validation failed: {e}")
            else:
                validated_queries.append((query, params or {}))
        
        logger.info(f"Starting batch execution of {len(validated_queries)} queries in batches of {batch_size}")
        
        try:
            driver = self.connection_manager.get_driver()
            with driver.session() as session:
                batch_count = 0
                
                for i in range(0, len(validated_queries), batch_size):
                    batch = validated_queries[i:i + batch_size]
                    batch_start = time.time()
                    
                    # Use transaction for better performance
                    with session.begin_transaction() as tx:
                        batch_results = []
                        for query, params in batch:
                            result = tx.run(query, params)
                            batch_results.append(list(result))
                        tx.commit()
                        results.extend(batch_results)
                    
                    batch_time = time.time() - batch_start
                    batch_count += 1
                    
                    logger.debug(f"Processed batch {batch_count} of {len(batch)} queries in {batch_time:.3f}s")
            
            total_time = time.time() - start_time
            avg_time = total_time / len(queries_with_params)
            
            # Update statistics
            self.query_stats["total_queries"] += len(queries_with_params)
            self.query_stats["total_execution_time"] += total_time
            self.query_stats["batch_count"] += 1
            
            batch_result = {
                "results": results,
                "total_queries": len(queries_with_params),
                "execution_time": total_time,
                "avg_time_per_query": avg_time,
                "batches_processed": batch_count,
                "batch_size": batch_size
            }
            
            logger.info(f"Batch execution completed: {len(queries_with_params)} queries in {total_time:.3f}s (avg: {avg_time:.4f}s per query)")
            return batch_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.query_stats["error_count"] += 1
            logger.error(f"Batch execution failed after {execution_time:.3f}s: {e}")
            raise QueryError(f"Batch execution failed: {e}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Legacy method name - redirects to secure execution."""
        logger.warning("execute_query() is deprecated. Use execute_secure_query() for explicit security validation")
        return self.execute_secure_query(query, params)
    
    def execute_read_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute read-only query with optimizations."""
        if params is None:
            params = {}
        
        # Add read-only hints to query if not present
        if not query.strip().upper().startswith(('MATCH', 'RETURN', 'WITH', 'UNWIND', 'CALL')):
            logger.warning(f"Query may not be read-only: {query[:50]}...")
        
        return self.execute_secure_query(query, params)
    
    def execute_write_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute write query using transaction."""
        if params is None:
            params = {}
        
        # Verify query appears to be a write operation
        write_keywords = ['CREATE', 'MERGE', 'SET', 'DELETE', 'REMOVE']
        query_upper = query.strip().upper()
        
        if not any(keyword in query_upper for keyword in write_keywords):
            logger.warning(f"Query may not be a write operation: {query[:50]}...")
        
        return self.execute_secure_write_transaction(query, params)
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query execution statistics."""
        avg_execution_time = (
            self.query_stats["total_execution_time"] / self.query_stats["total_queries"]
            if self.query_stats["total_queries"] > 0 else 0.0
        )
        
        error_rate = (
            self.query_stats["error_count"] / self.query_stats["total_queries"]
            if self.query_stats["total_queries"] > 0 else 0.0
        )
        
        return {
            "total_queries_executed": self.query_stats["total_queries"],
            "total_execution_time": self.query_stats["total_execution_time"],
            "average_execution_time": avg_execution_time,
            "error_count": self.query_stats["error_count"],
            "error_rate": error_rate,
            "batch_operations": self.query_stats["batch_count"],
            "queries_per_second": (
                self.query_stats["total_queries"] / self.query_stats["total_execution_time"]
                if self.query_stats["total_execution_time"] > 0 else 0.0
            )
        }
    
    def reset_statistics(self) -> None:
        """Reset query execution statistics."""
        self.query_stats = {
            "total_queries": 0,
            "total_execution_time": 0.0,
            "error_count": 0,
            "batch_count": 0
        }
        logger.info("Query execution statistics reset")
    
    def validate_query_syntax(self, query: str) -> bool:
        """Validate Cypher query syntax without executing."""
        try:
            # Basic syntax validation - could be enhanced with a proper Cypher parser
            query = query.strip()
            
            if not query:
                return False
            
            # Check for balanced parentheses and brackets
            paren_count = query.count('(') - query.count(')')
            bracket_count = query.count('[') - query.count(']')
            brace_count = query.count('{') - query.count('}')
            
            if paren_count != 0 or bracket_count != 0 or brace_count != 0:
                return False
            
            # Check for basic Cypher keywords
            cypher_keywords = [
                'MATCH', 'RETURN', 'WHERE', 'CREATE', 'MERGE', 'SET', 'DELETE',
                'WITH', 'UNWIND', 'CALL', 'YIELD', 'ORDER', 'LIMIT', 'SKIP'
            ]
            
            query_upper = query.upper()
            has_cypher_keyword = any(keyword in query_upper for keyword in cypher_keywords)
            
            return has_cypher_keyword
            
        except Exception as e:
            logger.error(f"Query syntax validation failed: {e}")
            return False