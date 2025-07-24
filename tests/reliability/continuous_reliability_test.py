#!/usr/bin/env python3
"""
24-HOUR CONTINUOUS RELIABILITY TEST
Runs distributed transaction manager continuously for 24 hours
with real databases to detect any stability issues, memory leaks,
or degradation over time.
"""

import asyncio
import time
import uuid
import json
import logging
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import traceback

from tests.reliability.real_db_managers import (
    RealNeo4jManager, 
    RealSQLiteManager,
    ConnectionHealthMonitor,
    DatabasePerformanceMonitor
)
from src.core.distributed_transaction_manager import (
    DistributedTransactionManager,
    TransactionOperation
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ContinuousReliabilityTester:
    """24-hour continuous reliability testing"""
    
    def __init__(self, test_duration_hours: int = 24):
        self.test_duration_hours = test_duration_hours
        self.test_duration_seconds = test_duration_hours * 3600
        
        # Managers
        self.neo4j_manager = None
        self.sqlite_manager = None
        self.dtm = None
        self.health_monitor = None
        self.perf_monitor = DatabasePerformanceMonitor()
        
        # Test state
        self.start_time = None
        self.test_running = False
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        
        # Metrics collection
        self.hourly_metrics = []
        self.memory_samples = []
        self.performance_samples = []
        self.error_log = []
        
        # System monitoring
        self.process = psutil.Process()
        self.initial_memory = None
        
    async def setup_test_environment(self):
        """Setup test environment with real databases"""
        logger.info("Setting up 24-hour test environment...")
        
        # Initialize database managers
        self.neo4j_manager = RealNeo4jManager(
            uri="bolt://localhost:7687",
            auth=("neo4j", "reliabilitytest123"),
            max_connection_pool_size=100  # Larger pool for long-running test
        )
        
        # Use a persistent SQLite database for 24-hour test
        sqlite_path = "/tmp/reliability_test_24h.db"
        self.sqlite_manager = RealSQLiteManager(
            database_path=sqlite_path,
            max_connections=100
        )
        
        # Initialize managers
        await self.neo4j_manager.initialize()
        await self.sqlite_manager.initialize()
        
        # Create distributed transaction manager
        self.dtm = DistributedTransactionManager(
            neo4j_manager=self.neo4j_manager,
            sqlite_manager=self.sqlite_manager
        )
        
        # Setup health monitoring
        self.health_monitor = ConnectionHealthMonitor(
            self.neo4j_manager,
            self.sqlite_manager
        )
        
        # Record initial system state
        self.initial_memory = self.process.memory_info().rss
        
        logger.info("Test environment ready for 24-hour run")
    
    async def run_continuous_test(self):
        """Run 24-hour continuous reliability test"""
        logger.info(f"Starting {self.test_duration_hours}-hour continuous reliability test")
        
        self.start_time = time.time()
        self.test_running = True
        
        try:
            # Start background tasks
            tasks = [
                asyncio.create_task(self._transaction_workload()),
                asyncio.create_task(self._system_monitoring()),
                asyncio.create_task(self._health_monitoring()),
                asyncio.create_task(self._metrics_collection()),
                asyncio.create_task(self._progress_reporting())
            ]
            
            # Wait for test duration or failure
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.test_duration_seconds + 60  # Extra time for cleanup
            )
            
        except asyncio.TimeoutError:
            logger.info("Test completed after designated time")
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            self.error_log.append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        finally:
            self.test_running = False
            await self._cleanup()
        
        # Generate final report
        return await self._generate_final_report()
    
    async def _transaction_workload(self):
        """Main transaction workload"""
        transaction_counter = 0
        
        while self.test_running and self._time_remaining() > 0:
            try:
                # Create varied transaction workload
                if transaction_counter % 100 == 0:
                    # Every 100th transaction: complex multi-operation
                    await self._create_complex_transaction(transaction_counter)
                elif transaction_counter % 10 == 0:
                    # Every 10th transaction: update operation
                    await self._create_update_transaction(transaction_counter)
                else:
                    # Regular transaction: simple create
                    await self._create_simple_transaction(transaction_counter)
                
                transaction_counter += 1
                
                # Variable delay to simulate realistic load
                if transaction_counter % 1000 == 0:
                    await asyncio.sleep(1)  # Brief pause every 1000 transactions
                else:
                    await asyncio.sleep(0.01)  # 10ms base delay
                
            except Exception as e:
                self.failed_transactions += 1
                self.error_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'transaction_id': transaction_counter,
                    'error': str(e),
                    'type': 'transaction_workload'
                })
                
                # Continue on error, but log it
                await asyncio.sleep(0.1)
        
        logger.info(f"Transaction workload completed. Total: {transaction_counter}")
    
    async def _create_simple_transaction(self, counter: int):
        """Create simple transaction with entity + mention"""
        start_time = time.time()
        
        try:
            tx_id = await self.dtm.begin_distributed_transaction()
            
            entity_id = f"entity-{counter}-{int(time.time())}"
            
            # Entity operation
            entity_op = TransactionOperation(
                operation_id=str(uuid.uuid4()),
                database="neo4j",
                operation_type="create",
                table_or_label="Entity",
                data={
                    "id": entity_id,
                    "name": f"Continuous Test Entity {counter}",
                    "type": "continuous-test",
                    "counter": counter
                }
            )
            await self.dtm.add_operation(tx_id, entity_op)
            
            # Mention operation
            mention_op = TransactionOperation(
                operation_id=str(uuid.uuid4()),
                database="sqlite",
                operation_type="create",
                table_or_label="mentions",
                data={
                    "id": f"mention-{counter}-{int(time.time())}",
                    "entity_id": entity_id,
                    "text": f"Continuous test mention {counter}",
                    "confidence": 0.9
                }
            )
            await self.dtm.add_operation(tx_id, mention_op)
            
            # Commit
            result = await self.dtm.commit_distributed_transaction(tx_id)
            
            duration = time.time() - start_time
            
            if result:
                self.successful_transactions += 1
                self.perf_monitor.record_neo4j_query(duration, True)
                self.perf_monitor.record_sqlite_query(duration, True)
            else:
                self.failed_transactions += 1
                self.perf_monitor.record_neo4j_query(duration, False)
                self.perf_monitor.record_sqlite_query(duration, False)
            
            self.total_transactions += 1
            
        except Exception as e:
            duration = time.time() - start_time
            self.failed_transactions += 1
            self.total_transactions += 1
            self.perf_monitor.record_neo4j_query(duration, False)
            self.perf_monitor.record_sqlite_query(duration, False)
            raise
    
    async def _create_complex_transaction(self, counter: int):
        """Create complex transaction with multiple operations"""
        start_time = time.time()
        
        try:
            tx_id = await self.dtm.begin_distributed_transaction()
            
            # Create multiple entities and mentions
            for i in range(3):  # 3 entities per complex transaction
                entity_id = f"complex-entity-{counter}-{i}-{int(time.time())}"
                
                entity_op = TransactionOperation(
                    operation_id=str(uuid.uuid4()),
                    database="neo4j",
                    operation_type="create",
                    table_or_label="Entity",
                    data={
                        "id": entity_id,
                        "name": f"Complex Entity {counter}-{i}",
                        "type": "complex-test",
                        "counter": counter,
                        "sub_counter": i
                    }
                )
                await self.dtm.add_operation(tx_id, entity_op)
                
                # Create multiple mentions per entity
                for j in range(2):  # 2 mentions per entity
                    mention_op = TransactionOperation(
                        operation_id=str(uuid.uuid4()),
                        database="sqlite",
                        operation_type="create",
                        table_or_label="mentions",
                        data={
                            "id": f"complex-mention-{counter}-{i}-{j}-{int(time.time())}",
                            "entity_id": entity_id,
                            "text": f"Complex mention {counter}-{i}-{j}",
                            "confidence": 0.8 + (j * 0.1)
                        }
                    )
                    await self.dtm.add_operation(tx_id, mention_op)
            
            # Commit complex transaction
            result = await self.dtm.commit_distributed_transaction(tx_id)
            
            duration = time.time() - start_time
            
            if result:
                self.successful_transactions += 1
            else:
                self.failed_transactions += 1
            
            self.total_transactions += 1
            
        except Exception as e:
            duration = time.time() - start_time
            self.failed_transactions += 1
            self.total_transactions += 1
            raise
    
    async def _create_update_transaction(self, counter: int):
        """Create update transaction (requires existing data)"""
        # For simplicity, just create a new entity
        # In real implementation, this would update existing entities
        await self._create_simple_transaction(counter)
    
    async def _system_monitoring(self):
        """Monitor system resources"""
        while self.test_running:
            try:
                # Memory monitoring
                memory_info = self.process.memory_info()
                memory_percent = self.process.memory_percent()
                
                # CPU monitoring
                cpu_percent = self.process.cpu_percent()
                
                # System-wide monitoring
                system_memory = psutil.virtual_memory()
                system_cpu = psutil.cpu_percent()
                
                self.memory_samples.append({
                    'timestamp': time.time(),
                    'rss': memory_info.rss,
                    'vms': memory_info.vms,
                    'memory_percent': memory_percent,
                    'cpu_percent': cpu_percent,
                    'system_memory_percent': system_memory.percent,
                    'system_cpu_percent': system_cpu
                })
                
                # Alert on high memory usage
                if memory_percent > 80:
                    logger.warning(f"High memory usage: {memory_percent:.1f}%")
                
                # Alert on memory growth
                if len(self.memory_samples) > 10:
                    recent_growth = memory_info.rss - self.memory_samples[-10]['rss']
                    if recent_growth > 50 * 1024 * 1024:  # 50MB growth
                        logger.warning(f"Memory increased by {recent_growth / 1024 / 1024:.1f}MB in last 10 samples")
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _health_monitoring(self):
        """Monitor database health"""
        # Start health monitoring task
        monitor_task = asyncio.create_task(
            self.health_monitor.start_monitoring(check_interval=60)
        )
        
        try:
            await monitor_task
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
        finally:
            self.health_monitor.stop_monitoring()
    
    async def _metrics_collection(self):
        """Collect hourly metrics"""
        while self.test_running:
            try:
                # Wait for next hour mark
                await asyncio.sleep(3600)  # 1 hour
                
                # Collect metrics
                elapsed_hours = (time.time() - self.start_time) / 3600
                
                hourly_metric = {
                    'hour': len(self.hourly_metrics) + 1,
                    'elapsed_hours': elapsed_hours,
                    'total_transactions': self.total_transactions,
                    'successful_transactions': self.successful_transactions,
                    'failed_transactions': self.failed_transactions,
                    'success_rate': (self.successful_transactions / max(1, self.total_transactions)) * 100,
                    'transactions_per_hour': self.total_transactions / elapsed_hours,
                    'health_status': self.health_monitor.get_health_status(),
                    'performance_stats': self.perf_monitor.get_performance_stats(),
                    'memory_usage_mb': self.process.memory_info().rss / 1024 / 1024,
                    'memory_growth_mb': (self.process.memory_info().rss - self.initial_memory) / 1024 / 1024
                }
                
                self.hourly_metrics.append(hourly_metric)
                
                logger.info(f"Hour {hourly_metric['hour']} completed:")
                logger.info(f"  Transactions: {hourly_metric['total_transactions']}")
                logger.info(f"  Success rate: {hourly_metric['success_rate']:.1f}%")
                logger.info(f"  Memory: {hourly_metric['memory_usage_mb']:.1f}MB (+{hourly_metric['memory_growth_mb']:.1f}MB)")
                
                # Reset performance metrics for next hour
                self.perf_monitor.reset_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    async def _progress_reporting(self):
        """Report progress periodically"""
        while self.test_running:
            try:
                elapsed = time.time() - self.start_time
                remaining = self.test_duration_seconds - elapsed
                
                if remaining > 0:
                    elapsed_hours = elapsed / 3600
                    remaining_hours = remaining / 3600
                    
                    logger.info(f"Test progress: {elapsed_hours:.1f}h elapsed, {remaining_hours:.1f}h remaining")
                    logger.info(f"Transactions: {self.total_transactions} ({self.successful_transactions} success, {self.failed_transactions} failed)")
                    
                    if self.total_transactions > 0:
                        success_rate = (self.successful_transactions / self.total_transactions) * 100
                        logger.info(f"Current success rate: {success_rate:.1f}%")
                
                await asyncio.sleep(1800)  # Report every 30 minutes
                
            except Exception as e:
                logger.error(f"Progress reporting error: {e}")
                await asyncio.sleep(1800)
    
    def _time_remaining(self) -> float:
        """Get remaining test time in seconds"""
        if not self.start_time:
            return self.test_duration_seconds
        
        elapsed = time.time() - self.start_time
        return max(0, self.test_duration_seconds - elapsed)
    
    async def _cleanup(self):
        """Cleanup test environment"""
        logger.info("Cleaning up test environment...")
        
        try:
            if self.dtm:
                await self.dtm.shutdown()
            
            if self.neo4j_manager:
                await self.neo4j_manager.shutdown()
            
            if self.sqlite_manager:
                await self.sqlite_manager.shutdown()
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        total_duration = time.time() - self.start_time
        
        # Calculate memory statistics
        if self.memory_samples:
            memory_values = [s['rss'] for s in self.memory_samples]
            memory_stats = {
                'initial_mb': self.initial_memory / 1024 / 1024,
                'final_mb': memory_values[-1] / 1024 / 1024,
                'peak_mb': max(memory_values) / 1024 / 1024,
                'average_mb': statistics.mean(memory_values) / 1024 / 1024,
                'growth_mb': (memory_values[-1] - self.initial_memory) / 1024 / 1024
            }
        else:
            memory_stats = {}
        
        # Calculate overall success rate
        success_rate = (self.successful_transactions / max(1, self.total_transactions)) * 100
        
        # Determine reliability score
        reliability_score = self._calculate_reliability_score(success_rate, memory_stats)
        
        report = {
            'test_configuration': {
                'duration_hours': self.test_duration_hours,
                'actual_duration_hours': total_duration / 3600,
                'test_completed': not self.test_running
            },
            'transaction_summary': {
                'total_transactions': self.total_transactions,
                'successful_transactions': self.successful_transactions,
                'failed_transactions': self.failed_transactions,
                'success_rate_percent': success_rate,
                'transactions_per_second': self.total_transactions / total_duration if total_duration > 0 else 0,
                'transactions_per_hour': self.total_transactions / (total_duration / 3600) if total_duration > 0 else 0
            },
            'memory_analysis': memory_stats,
            'performance_analysis': self.perf_monitor.get_performance_stats(),
            'hourly_breakdown': self.hourly_metrics,
            'error_analysis': {
                'total_errors': len(self.error_log),
                'error_rate_percent': (len(self.error_log) / max(1, self.total_transactions)) * 100,
                'errors': self.error_log[-50:]  # Last 50 errors
            },
            'reliability_assessment': {
                'reliability_score': reliability_score,
                'bulletproof_certified': reliability_score >= 99.5 and total_duration >= 24 * 3600,
                'production_ready': reliability_score >= 95.0,
                'memory_stable': memory_stats.get('growth_mb', 0) < 100,  # Less than 100MB growth
                'performance_stable': success_rate > 99.0,
                'long_term_stable': total_duration >= 12 * 3600  # At least 12 hours
            },
            'final_database_state': await self._get_final_database_state()
        }
        
        # Save report
        report_path = Path(f"tests/reliability/continuous_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Final report saved to {report_path}")
        
        return report
    
    def _calculate_reliability_score(self, success_rate: float, memory_stats: Dict[str, Any]) -> float:
        """Calculate overall reliability score"""
        # Base score from success rate
        base_score = success_rate
        
        # Deduct for memory growth
        memory_growth = memory_stats.get('growth_mb', 0)
        if memory_growth > 100:  # 100MB threshold
            memory_deduction = min(10, memory_growth / 100)  # Up to 10 point deduction
            base_score -= memory_deduction
        
        # Deduct for errors
        if self.error_log:
            error_rate = len(self.error_log) / max(1, self.total_transactions)
            error_deduction = min(5, error_rate * 100)  # Up to 5 point deduction
            base_score -= error_deduction
        
        return max(0, min(100, base_score))
    
    async def _get_final_database_state(self) -> Dict[str, Any]:
        """Get final database state for verification"""
        try:
            # Neo4j state
            async with self.neo4j_manager.get_session() as session:
                neo4j_result = await session.run("""
                    MATCH (e:Entity) 
                    RETURN count(e) as total_entities,
                           count(CASE WHEN e.type = 'continuous-test' THEN 1 END) as continuous_entities,
                           count(CASE WHEN e.type = 'complex-test' THEN 1 END) as complex_entities
                """)
                neo4j_stats = await neo4j_result.single()
            
            # SQLite state  
            async with self.sqlite_manager.get_read_connection() as conn:
                cursor = await conn.execute("""
                    SELECT 
                        COUNT(*) as total_mentions,
                        COUNT(CASE WHEN text LIKE '%Continuous%' THEN 1 END) as continuous_mentions,
                        COUNT(CASE WHEN text LIKE '%Complex%' THEN 1 END) as complex_mentions
                    FROM mentions
                """)
                sqlite_stats = await cursor.fetchone()
            
            return {
                'neo4j': {
                    'total_entities': neo4j_stats['total_entities'],
                    'continuous_entities': neo4j_stats['continuous_entities'],
                    'complex_entities': neo4j_stats['complex_entities']
                },
                'sqlite': {
                    'total_mentions': sqlite_stats[0],
                    'continuous_mentions': sqlite_stats[1],
                    'complex_mentions': sqlite_stats[2]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting final database state: {e}")
            return {'error': str(e)}


async def run_24_hour_continuous_test():
    """Run the 24-hour continuous reliability test"""
    logger.info("STARTING 24-HOUR CONTINUOUS RELIABILITY TEST")
    
    tester = ContinuousReliabilityTester(test_duration_hours=24)
    
    try:
        await tester.setup_test_environment()
        report = await tester.run_continuous_test()
        
        # Print final summary
        print("\n" + "="*80)
        print("24-HOUR CONTINUOUS RELIABILITY TEST RESULTS")
        print("="*80)
        print(f"Duration: {report['test_configuration']['actual_duration_hours']:.1f} hours")
        print(f"Total Transactions: {report['transaction_summary']['total_transactions']:,}")
        print(f"Success Rate: {report['transaction_summary']['success_rate_percent']:.2f}%")
        print(f"Transactions/Hour: {report['transaction_summary']['transactions_per_hour']:.0f}")
        print(f"Memory Growth: {report['memory_analysis'].get('growth_mb', 0):.1f}MB")
        print(f"Reliability Score: {report['reliability_assessment']['reliability_score']:.1f}/100")
        
        if report['reliability_assessment']['bulletproof_certified']:
            print("\n🏆 BULLETPROOF CERTIFICATION: ACHIEVED")
            print("✅ System reliability: 10/10")
        elif report['reliability_assessment']['production_ready']:
            print("\n⚠️  PRODUCTION READY: YES")
            print("✅ System reliability: 9/10")
        else:
            print("\n❌ REQUIRES IMPROVEMENT")
            print("❌ System reliability: <9/10")
        
        print("="*80)
        
        return report
        
    except Exception as e:
        logger.error(f"24-hour test failed: {e}")
        raise


if __name__ == "__main__":
    # Run shorter test for development (1 hour)
    import sys
    
    duration = 1  # Default 1 hour for testing
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    
    tester = ContinuousReliabilityTester(test_duration_hours=duration)
    
    async def run_test():
        await tester.setup_test_environment()
        return await tester.run_continuous_test()
    
    asyncio.run(run_test())