"""
Stability Testing Components

Comprehensive stability testing for database, tools, and memory operations.
"""

import asyncio
import logging
import time
import uuid
import psutil
import gc
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from .data_models import (
    StabilityTestResult, StabilityClass, PerformanceMetrics, ErrorAnalysis
)

logger = logging.getLogger(__name__)


class StabilityTester(ABC):
    """Base class for stability testing"""
    
    def __init__(self, test_iterations: int = 50):
        self.test_iterations = test_iterations
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def run_stability_test(self) -> StabilityTestResult:
        """Run stability test and return results"""
        pass
    
    def _calculate_performance_metrics(self, times: List[float]) -> PerformanceMetrics:
        """Calculate performance metrics from timing data"""
        if not times:
            return PerformanceMetrics(
                average_time=float('inf'),
                max_time=float('inf'),
                min_time=float('inf'),
                variance=float('inf'),
                total_operations=0
            )
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        variance = self._calculate_variance(times)
        
        return PerformanceMetrics(
            average_time=avg_time,
            max_time=max_time,
            min_time=min_time,
            variance=variance,
            total_operations=len(times)
        )
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        squared_diffs = [(x - mean) ** 2 for x in values]
        return sum(squared_diffs) / (len(values) - 1)
    
    def _analyze_errors(self, error_patterns: Dict[str, int], total_attempts: int) -> ErrorAnalysis:
        """Analyze error patterns"""
        total_errors = sum(error_patterns.values())
        error_rate = total_errors / total_attempts if total_attempts > 0 else 0.0
        
        most_common_error = None
        if error_patterns:
            most_common_error = max(error_patterns.items(), key=lambda x: x[1])[0]
        
        return ErrorAnalysis(
            error_patterns=error_patterns,
            total_errors=total_errors,
            error_rate=error_rate,
            most_common_error=most_common_error
        )
    
    def _classify_stability(self, stability_score: float) -> StabilityClass:
        """Classify stability based on score"""
        if stability_score >= 0.98:
            return StabilityClass.EXCELLENT
        elif stability_score >= 0.95:
            return StabilityClass.GOOD
        elif stability_score >= 0.90:
            return StabilityClass.ACCEPTABLE
        elif stability_score >= 0.80:
            return StabilityClass.MARGINAL
        else:
            return StabilityClass.POOR


class DatabaseStabilityTester(StabilityTester):
    """Test database connection stability"""
    
    def __init__(self, test_iterations: int = 50):
        super().__init__(test_iterations)
        self.neo4j_manager = None
    
    async def run_stability_test(self) -> StabilityTestResult:
        """Test database stability with comprehensive validation"""
        successful_connections = 0
        connection_times = []
        error_patterns = {}
        performance_metrics_list = []
        
        self.logger.info(f"Starting database stability test with {self.test_iterations} iterations")
        
        for attempt in range(self.test_iterations):
            try:
                start_time = time.time()
                
                # Test full connection lifecycle
                from src.core.neo4j_manager import Neo4jDockerManager
                neo4j_manager = Neo4jDockerManager()
                
                # Test connection acquisition
                session = neo4j_manager.get_session()
                connection_time = time.time() - start_time
                
                # Test basic operations
                with session:
                    # Test 1: Simple query
                    result = session.run("RETURN 1 as test, $timestamp as ts", 
                                       timestamp=datetime.now().isoformat())
                    record = result.single()
                    
                    if record["test"] != 1:
                        raise ValueError(f"Query returned incorrect result: {record['test']}")
                    
                    query_time = time.time() - start_time
                    
                    # Test 2: Write operation
                    test_id = str(uuid.uuid4())
                    session.run("CREATE (n:StabilityTest {id: $id, attempt: $attempt}) RETURN n.id",
                               id=test_id, attempt=attempt)
                    
                    # Test 3: Read verification
                    verify_result = session.run("MATCH (n:StabilityTest {id: $id}) RETURN n.id as found_id", 
                                              id=test_id)
                    found_record = verify_result.single()
                    
                    if found_record["found_id"] != test_id:
                        raise ValueError(f"Write verification failed")
                    
                    # Test 4: Cleanup
                    session.run("MATCH (n:StabilityTest {id: $id}) DELETE n", id=test_id)
                    
                    total_time = time.time() - start_time
                
                connection_times.append(total_time)
                performance_metrics_list.append({
                    "attempt": attempt + 1,
                    "connection_time": connection_time,
                    "query_time": query_time,
                    "total_time": total_time
                })
                
                successful_connections += 1
                
            except Exception as e:
                error_type = type(e).__name__
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                self.logger.warning(f"Database stability test {attempt + 1} failed: {e}")
            
            # Brief delay between attempts
            await asyncio.sleep(0.1)
        
        # Calculate results
        stability_score = successful_connections / self.test_iterations
        performance_metrics = self._calculate_performance_metrics(connection_times)
        error_analysis = self._analyze_errors(error_patterns, self.test_iterations)
        stability_class = self._classify_stability(stability_score)
        
        # Generate recommendations
        recommendations = []
        if stability_score < 0.95:
            recommendations.append("Database stability below production threshold")
        if performance_metrics.average_time > 1.0:
            recommendations.append("Database response times too slow for production")
        if error_analysis.error_rate > 0.05:
            recommendations.append("Error rate too high for production use")
        
        return StabilityTestResult(
            test_name="database_stability",
            successful_operations=successful_connections,
            total_attempts=self.test_iterations,
            stability_score=stability_score,
            stability_class=stability_class,
            performance_metrics=performance_metrics,
            error_analysis=error_analysis,
            recommendations=recommendations
        )


class ToolConsistencyTester(StabilityTester):
    """Test tool consistency and reliability"""
    
    async def run_stability_test(self) -> StabilityTestResult:
        """Test tool consistency with multiple invocations"""
        successful_operations = 0
        operation_times = []
        error_patterns = {}
        
        self.logger.info(f"Starting tool consistency test with {self.test_iterations} iterations")
        
        for attempt in range(self.test_iterations):
            try:
                start_time = time.time()
                
                # Test tool factory availability
                from src.core.tool_factory import ToolFactory
                tool_factory = ToolFactory()
                
                # Test tool creation and basic operations
                available_tools = tool_factory.get_available_tools()
                if not available_tools:
                    raise ValueError("No tools available")
                
                # Test tool instantiation
                tool_name = list(available_tools.keys())[0]
                tool_instance = tool_factory.create_tool(tool_name)
                
                if not tool_instance:
                    raise ValueError(f"Failed to create tool: {tool_name}")
                
                # Test tool interface consistency
                if not hasattr(tool_instance, 'get_tool_info'):
                    raise ValueError(f"Tool {tool_name} missing required interface")
                
                tool_info = tool_instance.get_tool_info()
                if not isinstance(tool_info, dict):
                    raise ValueError(f"Tool {tool_name} returned invalid info format")
                
                operation_time = time.time() - start_time
                operation_times.append(operation_time)
                successful_operations += 1
                
            except Exception as e:
                error_type = type(e).__name__
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                self.logger.warning(f"Tool consistency test {attempt + 1} failed: {e}")
            
            await asyncio.sleep(0.05)
        
        # Calculate results
        stability_score = successful_operations / self.test_iterations
        performance_metrics = self._calculate_performance_metrics(operation_times)
        error_analysis = self._analyze_errors(error_patterns, self.test_iterations)
        stability_class = self._classify_stability(stability_score)
        
        # Generate recommendations
        recommendations = []
        if stability_score < 0.98:
            recommendations.append("Tool consistency below production threshold")
        if error_analysis.error_rate > 0.02:
            recommendations.append("Tool error rate too high for production")
        
        return StabilityTestResult(
            test_name="tool_consistency",
            successful_operations=successful_operations,
            total_attempts=self.test_iterations,
            stability_score=stability_score,
            stability_class=stability_class,
            performance_metrics=performance_metrics,
            error_analysis=error_analysis,
            recommendations=recommendations
        )


class MemoryStabilityTester(StabilityTester):
    """Test memory stability and leak detection"""
    
    def __init__(self, test_iterations: int = 20):
        super().__init__(test_iterations)
    
    async def run_stability_test(self) -> StabilityTestResult:
        """Test memory stability with leak detection"""
        successful_operations = 0
        memory_measurements = []
        error_patterns = {}
        initial_memory = psutil.Process().memory_info().rss
        
        self.logger.info(f"Starting memory stability test with {self.test_iterations} iterations")
        
        for attempt in range(self.test_iterations):
            try:
                start_time = time.time()
                
                # Measure memory before operation
                pre_memory = psutil.Process().memory_info().rss
                
                # Simulate memory-intensive operations
                test_data = []
                for i in range(1000):
                    test_data.append({
                        "id": str(uuid.uuid4()),
                        "data": "x" * 1000,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Process the data
                processed_data = []
                for item in test_data:
                    processed_item = {
                        **item,
                        "processed": True,
                        "processed_at": datetime.now().isoformat()
                    }
                    processed_data.append(processed_item)
                
                # Clear data
                del test_data
                del processed_data
                
                # Force garbage collection
                gc.collect()
                
                # Measure memory after operation
                post_memory = psutil.Process().memory_info().rss
                operation_time = time.time() - start_time
                
                memory_measurements.append({
                    "attempt": attempt + 1,
                    "pre_memory": pre_memory,
                    "post_memory": post_memory,
                    "memory_delta": post_memory - pre_memory,
                    "operation_time": operation_time
                })
                
                successful_operations += 1
                
            except Exception as e:
                error_type = type(e).__name__
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                self.logger.warning(f"Memory stability test {attempt + 1} failed: {e}")
            
            await asyncio.sleep(0.1)
        
        # Analyze memory usage patterns
        final_memory = psutil.Process().memory_info().rss
        memory_growth = final_memory - initial_memory
        memory_growth_mb = memory_growth / (1024 * 1024)
        
        # Calculate performance metrics from operation times
        operation_times = [m["operation_time"] for m in memory_measurements]
        performance_metrics = self._calculate_performance_metrics(operation_times)
        
        # Memory stability analysis
        stability_score = successful_operations / self.test_iterations
        if memory_growth_mb > 50:  # More than 50MB growth indicates potential leak
            stability_score *= 0.5
        
        error_analysis = self._analyze_errors(error_patterns, self.test_iterations)
        stability_class = self._classify_stability(stability_score)
        
        # Generate recommendations
        recommendations = []
        if memory_growth_mb > 50:
            recommendations.append(f"Memory leak detected: {memory_growth_mb:.1f}MB growth")
        if stability_score < 0.95:
            recommendations.append("Memory stability below production threshold")
        
        return StabilityTestResult(
            test_name="memory_stability",
            successful_operations=successful_operations,
            total_attempts=self.test_iterations,
            stability_score=stability_score,
            stability_class=stability_class,
            performance_metrics=performance_metrics,
            error_analysis=error_analysis,
            recommendations=recommendations
        )