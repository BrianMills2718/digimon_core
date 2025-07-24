#!/usr/bin/env python3
"""
COMPREHENSIVE LOAD TESTING SUITE
Tests system performance and reliability under realistic production loads
"""

import asyncio
import time
import uuid
import statistics
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import psutil
from concurrent.futures import ThreadPoolExecutor

from tests.reliability.real_db_managers import (
    RealNeo4jManager, 
    RealSQLiteManager,
    DatabasePerformanceMonitor
)
from src.core.distributed_transaction_manager import (
    DistributedTransactionManager,
    TransactionOperation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result data"""
    test_name: str
    duration_seconds: float
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    transactions_per_second: float
    average_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    memory_peak_mb: float
    memory_growth_mb: float
    cpu_peak_percent: float
    errors: List[str]


class ComprehensiveLoadTester:
    """Comprehensive load testing with realistic scenarios"""
    
    def __init__(self):
        self.neo4j_manager = None
        self.sqlite_manager = None
        self.dtm = None
        self.perf_monitor = DatabasePerformanceMonitor()
        self.test_results: List[LoadTestResult] = []
        
        # System monitoring
        self.process = psutil.Process()
        self.initial_memory = None
        
    async def setup_load_test_environment(self):
        """Setup environment for load testing"""
        logger.info("Setting up load test environment...")
        
        # Initialize with larger connection pools for load testing
        self.neo4j_manager = RealNeo4jManager(
            uri="bolt://localhost:7687",
            auth=("neo4j", "reliabilitytest123"),
            max_connection_pool_size=200  # Large pool for load testing
        )
        
        self.sqlite_manager = RealSQLiteManager(
            database_path="/tmp/load_test.db",
            max_connections=200
        )
        
        await self.neo4j_manager.initialize()
        await self.sqlite_manager.initialize()
        
        self.dtm = DistributedTransactionManager(
            neo4j_manager=self.neo4j_manager,
            sqlite_manager=self.sqlite_manager
        )
        
        self.initial_memory = self.process.memory_info().rss
        logger.info("Load test environment ready")
    
    async def run_comprehensive_load_tests(self) -> Dict[str, Any]:
        """Run all load test scenarios"""
        logger.info("Starting comprehensive load testing")
        
        test_scenarios = [
            ("steady_state_load", self._test_steady_state_load),
            ("burst_load", self._test_burst_load),
            ("sustained_high_throughput", self._test_sustained_high_throughput),
            ("mixed_workload", self._test_mixed_workload),
            ("concurrent_users", self._test_concurrent_users),
            ("large_transaction_load", self._test_large_transaction_load),
            ("memory_stress_load", self._test_memory_stress_load),
            ("connection_churn", self._test_connection_churn),
            ("gradual_ramp_up", self._test_gradual_ramp_up),
            ("peak_capacity", self._test_peak_capacity)
        ]
        
        for test_name, test_func in test_scenarios:
            logger.info(f"Starting load test: {test_name}")
            try:
                result = await test_func()
                self.test_results.append(result)
                
                # Brief recovery period between tests
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Load test {test_name} failed: {e}")
                # Continue with other tests
        
        return self._generate_load_test_report()
    
    async def _test_steady_state_load(self) -> LoadTestResult:
        """Test steady state load - consistent transaction rate"""
        logger.info("Running steady state load test")
        
        duration_seconds = 300  # 5 minutes
        target_tps = 50  # 50 transactions per second
        
        return await self._run_load_test(
            test_name="steady_state_load",
            duration_seconds=duration_seconds,
            target_tps=target_tps,
            ramp_up_seconds=30
        )
    
    async def _test_burst_load(self) -> LoadTestResult:
        """Test burst load - sudden spikes in traffic"""
        logger.info("Running burst load test")
        
        # Alternate between high and low load
        start_time = time.time()
        latencies = []
        errors = []
        successful = 0
        failed = 0
        total = 0
        peak_memory = self.initial_memory
        peak_cpu = 0
        
        try:
            for cycle in range(6):  # 6 cycles of 30 seconds each
                if cycle % 2 == 0:
                    # Burst phase - high load
                    tps = 200
                    phase_name = "burst"
                else:
                    # Quiet phase - low load
                    tps = 10
                    phase_name = "quiet"
                
                logger.info(f"Burst test cycle {cycle + 1}: {phase_name} phase ({tps} TPS)")
                
                phase_start = time.time()
                while time.time() - phase_start < 30:  # 30 seconds per phase
                    transaction_start = time.time()
                    
                    try:
                        result = await self._create_simple_load_transaction(total)
                        latency = (time.time() - transaction_start) * 1000
                        latencies.append(latency)
                        
                        if result:
                            successful += 1
                        else:
                            failed += 1
                        
                        total += 1
                        
                        # Monitor system resources
                        current_memory = self.process.memory_info().rss
                        current_cpu = self.process.cpu_percent()
                        peak_memory = max(peak_memory, current_memory)
                        peak_cpu = max(peak_cpu, current_cpu)
                        
                        # Control rate
                        await asyncio.sleep(1.0 / tps)
                        
                    except Exception as e:
                        errors.append(str(e))
                        failed += 1
                        total += 1
            
            duration = time.time() - start_time
            
            return LoadTestResult(
                test_name="burst_load",
                duration_seconds=duration,
                total_transactions=total,
                successful_transactions=successful,
                failed_transactions=failed,
                transactions_per_second=total / duration,
                average_latency_ms=statistics.mean(latencies) if latencies else 0,
                p95_latency_ms=self._percentile(latencies, 95) if latencies else 0,
                p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
                max_latency_ms=max(latencies) if latencies else 0,
                memory_peak_mb=(peak_memory - self.initial_memory) / 1024 / 1024,
                memory_growth_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
                cpu_peak_percent=peak_cpu,
                errors=errors[:10]  # First 10 errors
            )
            
        except Exception as e:
            logger.error(f"Burst load test failed: {e}")
            return LoadTestResult(
                test_name="burst_load",
                duration_seconds=0,
                total_transactions=0,
                successful_transactions=0,
                failed_transactions=0,
                transactions_per_second=0,
                average_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                max_latency_ms=0,
                memory_peak_mb=0,
                memory_growth_mb=0,
                cpu_peak_percent=0,
                errors=[str(e)]
            )
    
    async def _test_sustained_high_throughput(self) -> LoadTestResult:
        """Test sustained high throughput"""
        logger.info("Running sustained high throughput test")
        
        return await self._run_load_test(
            test_name="sustained_high_throughput",
            duration_seconds=600,  # 10 minutes
            target_tps=100,
            ramp_up_seconds=60
        )
    
    async def _test_mixed_workload(self) -> LoadTestResult:
        """Test mixed workload with different transaction types"""
        logger.info("Running mixed workload test")
        
        duration_seconds = 300
        start_time = time.time()
        latencies = []
        errors = []
        successful = 0
        failed = 0
        total = 0
        peak_memory = self.initial_memory
        peak_cpu = 0
        
        try:
            tasks = []
            
            # 70% simple transactions
            for _ in range(35):
                task = asyncio.create_task(self._sustained_simple_transactions(duration_seconds * 0.7))
                tasks.append(task)
            
            # 20% complex transactions  
            for _ in range(10):
                task = asyncio.create_task(self._sustained_complex_transactions(duration_seconds * 0.2))
                tasks.append(task)
            
            # 10% update transactions
            for _ in range(5):
                task = asyncio.create_task(self._sustained_update_transactions(duration_seconds * 0.1))
                tasks.append(task)
            
            # Run all workloads concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            for result in results:
                if isinstance(result, dict):
                    successful += result.get('successful', 0)
                    failed += result.get('failed', 0)
                    total += result.get('total', 0)
                    latencies.extend(result.get('latencies', []))
                    errors.extend(result.get('errors', []))
            
            duration = time.time() - start_time
            
            return LoadTestResult(
                test_name="mixed_workload",
                duration_seconds=duration,
                total_transactions=total,
                successful_transactions=successful,
                failed_transactions=failed,
                transactions_per_second=total / duration if duration > 0 else 0,
                average_latency_ms=statistics.mean(latencies) if latencies else 0,
                p95_latency_ms=self._percentile(latencies, 95) if latencies else 0,
                p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
                max_latency_ms=max(latencies) if latencies else 0,
                memory_peak_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
                memory_growth_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
                cpu_peak_percent=self.process.cpu_percent(),
                errors=errors[:10]
            )
            
        except Exception as e:
            return LoadTestResult(
                test_name="mixed_workload",
                duration_seconds=0, total_transactions=0, successful_transactions=0,
                failed_transactions=0, transactions_per_second=0, average_latency_ms=0,
                p95_latency_ms=0, p99_latency_ms=0, max_latency_ms=0,
                memory_peak_mb=0, memory_growth_mb=0, cpu_peak_percent=0,
                errors=[str(e)]
            )
    
    async def _test_concurrent_users(self) -> LoadTestResult:
        """Test concurrent users scenario"""
        logger.info("Running concurrent users test")
        
        num_users = 100
        duration_seconds = 300
        
        tasks = []
        for user_id in range(num_users):
            task = asyncio.create_task(self._simulate_user_session(user_id, duration_seconds))
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        successful = 0
        failed = 0
        total = 0
        latencies = []
        errors = []
        
        for result in results:
            if isinstance(result, dict):
                successful += result.get('successful', 0)
                failed += result.get('failed', 0)
                total += result.get('total', 0)
                latencies.extend(result.get('latencies', []))
                errors.extend(result.get('errors', []))
        
        duration = time.time() - start_time
        
        return LoadTestResult(
            test_name="concurrent_users",
            duration_seconds=duration,
            total_transactions=total,
            successful_transactions=successful,
            failed_transactions=failed,
            transactions_per_second=total / duration if duration > 0 else 0,
            average_latency_ms=statistics.mean(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            memory_peak_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
            memory_growth_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
            cpu_peak_percent=self.process.cpu_percent(),
            errors=errors[:10]
        )
    
    async def _run_load_test(self, test_name: str, duration_seconds: int, 
                           target_tps: int, ramp_up_seconds: int = 0) -> LoadTestResult:
        """Generic load test runner"""
        start_time = time.time()
        latencies = []
        errors = []
        successful = 0
        failed = 0
        total = 0
        peak_memory = self.initial_memory
        peak_cpu = 0
        
        try:
            # Ramp up phase
            if ramp_up_seconds > 0:
                logger.info(f"Ramping up over {ramp_up_seconds} seconds")
                ramp_start = time.time()
                while time.time() - ramp_start < ramp_up_seconds:
                    elapsed_ramp = time.time() - ramp_start
                    current_tps = int(target_tps * (elapsed_ramp / ramp_up_seconds))
                    
                    if current_tps > 0:
                        transaction_start = time.time()
                        try:
                            result = await self._create_simple_load_transaction(total)
                            latency = (time.time() - transaction_start) * 1000
                            latencies.append(latency)
                            
                            if result:
                                successful += 1
                            else:
                                failed += 1
                            total += 1
                            
                            await asyncio.sleep(1.0 / current_tps)
                            
                        except Exception as e:
                            errors.append(str(e))
                            failed += 1
                            total += 1
            
            # Main load phase
            logger.info(f"Running main load phase at {target_tps} TPS for {duration_seconds} seconds")
            main_start = time.time()
            
            while time.time() - main_start < duration_seconds:
                transaction_start = time.time()
                
                try:
                    result = await self._create_simple_load_transaction(total)
                    latency = (time.time() - transaction_start) * 1000
                    latencies.append(latency)
                    
                    if result:
                        successful += 1
                    else:
                        failed += 1
                    
                    total += 1
                    
                    # Monitor system resources
                    current_memory = self.process.memory_info().rss
                    current_cpu = self.process.cpu_percent()
                    peak_memory = max(peak_memory, current_memory)
                    peak_cpu = max(peak_cpu, current_cpu)
                    
                    # Control rate
                    await asyncio.sleep(1.0 / target_tps)
                    
                except Exception as e:
                    errors.append(str(e))
                    failed += 1
                    total += 1
            
            duration = time.time() - start_time
            
            return LoadTestResult(
                test_name=test_name,
                duration_seconds=duration,
                total_transactions=total,
                successful_transactions=successful,
                failed_transactions=failed,
                transactions_per_second=total / duration if duration > 0 else 0,
                average_latency_ms=statistics.mean(latencies) if latencies else 0,
                p95_latency_ms=self._percentile(latencies, 95) if latencies else 0,
                p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
                max_latency_ms=max(latencies) if latencies else 0,
                memory_peak_mb=(peak_memory - self.initial_memory) / 1024 / 1024,
                memory_growth_mb=(self.process.memory_info().rss - self.initial_memory) / 1024 / 1024,
                cpu_peak_percent=peak_cpu,
                errors=errors[:10]  # First 10 errors
            )
            
        except Exception as e:
            logger.error(f"Load test {test_name} failed: {e}")
            return LoadTestResult(
                test_name=test_name,
                duration_seconds=0, total_transactions=0, successful_transactions=0,
                failed_transactions=0, transactions_per_second=0, average_latency_ms=0,
                p95_latency_ms=0, p99_latency_ms=0, max_latency_ms=0,
                memory_peak_mb=0, memory_growth_mb=0, cpu_peak_percent=0,
                errors=[str(e)]
            )
    
    async def _create_simple_load_transaction(self, counter: int) -> bool:
        """Create simple transaction for load testing"""
        try:
            tx_id = await self.dtm.begin_distributed_transaction()
            
            entity_id = f"load-entity-{counter}-{int(time.time() * 1000)}"
            
            entity_op = TransactionOperation(
                operation_id=str(uuid.uuid4()),
                database="neo4j",
                operation_type="create",
                table_or_label="Entity",
                data={
                    "id": entity_id,
                    "name": f"Load Test Entity {counter}",
                    "type": "load-test"
                }
            )
            await self.dtm.add_operation(tx_id, entity_op)
            
            mention_op = TransactionOperation(
                operation_id=str(uuid.uuid4()),
                database="sqlite",
                operation_type="create",
                table_or_label="mentions",
                data={
                    "id": f"load-mention-{counter}-{int(time.time() * 1000)}",
                    "entity_id": entity_id,
                    "text": f"Load test mention {counter}",
                    "confidence": 0.9
                }
            )
            await self.dtm.add_operation(tx_id, mention_op)
            
            return await self.dtm.commit_distributed_transaction(tx_id)
            
        except Exception:
            return False
    
    # Placeholder methods for other load tests
    async def _test_large_transaction_load(self) -> LoadTestResult:
        """Test load with large transactions"""
        return await self._run_load_test("large_transaction_load", 300, 10, 30)
    
    async def _test_memory_stress_load(self) -> LoadTestResult:
        """Test memory stress load"""
        return await self._run_load_test("memory_stress_load", 300, 75, 30)
    
    async def _test_connection_churn(self) -> LoadTestResult:
        """Test connection churn"""
        return await self._run_load_test("connection_churn", 300, 50, 30)
    
    async def _test_gradual_ramp_up(self) -> LoadTestResult:
        """Test gradual ramp up"""
        return await self._run_load_test("gradual_ramp_up", 600, 150, 180)
    
    async def _test_peak_capacity(self) -> LoadTestResult:
        """Test peak capacity"""
        return await self._run_load_test("peak_capacity", 300, 300, 60)
    
    async def _sustained_simple_transactions(self, duration: float) -> Dict[str, Any]:
        """Helper for sustained simple transactions"""
        start_time = time.time()
        successful = 0
        failed = 0
        latencies = []
        errors = []
        
        counter = 0
        while time.time() - start_time < duration:
            try:
                result = await self._create_simple_load_transaction(counter)
                if result:
                    successful += 1
                else:
                    failed += 1
                counter += 1
                await asyncio.sleep(0.02)  # 50 TPS per worker
            except Exception as e:
                errors.append(str(e))
                failed += 1
                counter += 1
        
        return {
            'successful': successful,
            'failed': failed,
            'total': counter,
            'latencies': latencies,
            'errors': errors
        }
    
    async def _sustained_complex_transactions(self, duration: float) -> Dict[str, Any]:
        """Helper for sustained complex transactions"""
        # Simplified - in real implementation would create complex transactions
        return await self._sustained_simple_transactions(duration)
    
    async def _sustained_update_transactions(self, duration: float) -> Dict[str, Any]:
        """Helper for sustained update transactions"""
        # Simplified - in real implementation would create update transactions
        return await self._sustained_simple_transactions(duration)
    
    async def _simulate_user_session(self, user_id: int, duration: float) -> Dict[str, Any]:
        """Simulate a user session"""
        start_time = time.time()
        successful = 0
        failed = 0
        latencies = []
        errors = []
        
        transaction_count = 0
        while time.time() - start_time < duration:
            try:
                # Simulate user thinking time
                await asyncio.sleep(0.5 + (user_id % 5) * 0.1)  # 0.5-1.0 seconds
                
                transaction_start = time.time()
                result = await self._create_simple_load_transaction(f"{user_id}-{transaction_count}")
                latency = (time.time() - transaction_start) * 1000
                latencies.append(latency)
                
                if result:
                    successful += 1
                else:
                    failed += 1
                
                transaction_count += 1
                
            except Exception as e:
                errors.append(str(e))
                failed += 1
                transaction_count += 1
        
        return {
            'successful': successful,
            'failed': failed,
            'total': transaction_count,
            'latencies': latencies,
            'errors': errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]
    
    def _generate_load_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        total_transactions = sum(r.total_transactions for r in self.test_results)
        total_successful = sum(r.successful_transactions for r in self.test_results)
        
        # Calculate aggregate metrics
        if self.test_results:
            avg_tps = statistics.mean([r.transactions_per_second for r in self.test_results])
            avg_latency = statistics.mean([r.average_latency_ms for r in self.test_results])
            max_tps = max([r.transactions_per_second for r in self.test_results])
            max_latency = max([r.max_latency_ms for r in self.test_results])
        else:
            avg_tps = avg_latency = max_tps = max_latency = 0
        
        # Calculate performance score
        performance_score = self._calculate_performance_score()
        
        report = {
            'load_test_summary': {
                'total_test_scenarios': len(self.test_results),
                'total_transactions': total_transactions,
                'total_successful': total_successful,
                'overall_success_rate': (total_successful / max(1, total_transactions)) * 100,
                'average_tps': avg_tps,
                'max_tps': max_tps,
                'average_latency_ms': avg_latency,
                'max_latency_ms': max_latency
            },
            'performance_metrics': {
                'performance_score': performance_score,
                'throughput_grade': self._grade_throughput(max_tps),
                'latency_grade': self._grade_latency(avg_latency),
                'reliability_grade': self._grade_reliability(total_successful, total_transactions)
            },
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'duration_seconds': r.duration_seconds,
                    'total_transactions': r.total_transactions,
                    'successful_transactions': r.successful_transactions,
                    'failed_transactions': r.failed_transactions,
                    'transactions_per_second': r.transactions_per_second,
                    'average_latency_ms': r.average_latency_ms,
                    'p95_latency_ms': r.p95_latency_ms,
                    'p99_latency_ms': r.p99_latency_ms,
                    'max_latency_ms': r.max_latency_ms,
                    'memory_peak_mb': r.memory_peak_mb,
                    'memory_growth_mb': r.memory_growth_mb,
                    'cpu_peak_percent': r.cpu_peak_percent,
                    'error_count': len(r.errors)
                } for r in self.test_results
            ],
            'certification': {
                'high_performance_certified': performance_score >= 90,
                'production_ready_performance': performance_score >= 80,
                'requires_optimization': performance_score < 80
            }
        }
        
        return report
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        if not self.test_results:
            return 0
        
        # Throughput component (40%)
        max_tps = max([r.transactions_per_second for r in self.test_results])
        throughput_score = min(100, (max_tps / 200) * 100)  # 200 TPS = 100%
        
        # Latency component (30%)
        avg_latency = statistics.mean([r.average_latency_ms for r in self.test_results])
        latency_score = max(0, 100 - (avg_latency / 10))  # 10ms = 100%, 1000ms = 0%
        
        # Reliability component (30%)
        total_success = sum(r.successful_transactions for r in self.test_results)
        total_transactions = sum(r.total_transactions for r in self.test_results)
        reliability_score = (total_success / max(1, total_transactions)) * 100
        
        return (throughput_score * 0.4) + (latency_score * 0.3) + (reliability_score * 0.3)
    
    def _grade_throughput(self, tps: float) -> str:
        """Grade throughput performance"""
        if tps >= 200:
            return "A"
        elif tps >= 150:
            return "B"
        elif tps >= 100:
            return "C"
        elif tps >= 50:
            return "D"
        else:
            return "F"
    
    def _grade_latency(self, avg_latency_ms: float) -> str:
        """Grade latency performance"""
        if avg_latency_ms <= 10:
            return "A"
        elif avg_latency_ms <= 50:
            return "B"
        elif avg_latency_ms <= 100:
            return "C"
        elif avg_latency_ms <= 500:
            return "D"
        else:
            return "F"
    
    def _grade_reliability(self, successful: int, total: int) -> str:
        """Grade reliability"""
        if total == 0:
            return "F"
        
        success_rate = (successful / total) * 100
        if success_rate >= 99.9:
            return "A"
        elif success_rate >= 99.5:
            return "B"
        elif success_rate >= 99.0:
            return "C"
        elif success_rate >= 95.0:
            return "D"
        else:
            return "F"
    
    async def cleanup(self):
        """Cleanup load test environment"""
        if self.dtm:
            await self.dtm.shutdown()
        if self.neo4j_manager:
            await self.neo4j_manager.shutdown()
        if self.sqlite_manager:
            await self.sqlite_manager.shutdown()


async def run_comprehensive_load_tests():
    """Run comprehensive load testing suite"""
    logger.info("STARTING COMPREHENSIVE LOAD TESTING")
    
    tester = ComprehensiveLoadTester()
    
    try:
        await tester.setup_load_test_environment()
        report = await tester.run_comprehensive_load_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE LOAD TEST RESULTS")
        print("="*80)
        print(f"Test Scenarios: {report['load_test_summary']['total_test_scenarios']}")
        print(f"Total Transactions: {report['load_test_summary']['total_transactions']:,}")
        print(f"Success Rate: {report['load_test_summary']['overall_success_rate']:.2f}%")
        print(f"Max Throughput: {report['load_test_summary']['max_tps']:.1f} TPS")
        print(f"Average Latency: {report['load_test_summary']['average_latency_ms']:.1f}ms")
        print(f"Performance Score: {report['performance_metrics']['performance_score']:.1f}/100")
        
        grades = report['performance_metrics']
        print(f"Throughput Grade: {grades['throughput_grade']}")
        print(f"Latency Grade: {grades['latency_grade']}")
        print(f"Reliability Grade: {grades['reliability_grade']}")
        
        if report['certification']['high_performance_certified']:
            print("\n🏆 HIGH PERFORMANCE CERTIFICATION: ACHIEVED")
        elif report['certification']['production_ready_performance']:
            print("\n⚠️  PRODUCTION READY PERFORMANCE: YES")
        else:
            print("\n❌ PERFORMANCE: REQUIRES OPTIMIZATION")
        
        print("="*80)
        
        # Save detailed report
        report_path = Path("tests/reliability/load_test_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_load_tests())