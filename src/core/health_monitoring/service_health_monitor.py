"""
Service Health Monitor

Monitors health of individual services and endpoints.
"""

import asyncio
import aiohttp
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List

from .data_models import (
    HealthCheckResult, HealthStatus, ServiceEndpoint, 
    ServiceStatus, HealthThresholds
)

logger = logging.getLogger(__name__)


class ServiceHealthMonitor:
    """Monitor health of individual services"""
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.service_statuses: Dict[str, ServiceStatus] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.thresholds = thresholds or HealthThresholds()
        
        # HTTP session for service checks
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Monitoring state
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._monitoring_active = False
    
    async def initialize(self):
        """Initialize the service health monitor"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        logger.info("Service health monitor initialized")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.stop_monitoring()
        
        if self._session:
            await self._session.close()
            self._session = None
        
        logger.info("Service health monitor cleaned up")
    
    def register_service(self, service_name: str, endpoint: ServiceEndpoint):
        """Register a service for health monitoring"""
        self.services[service_name] = endpoint
        self.service_statuses[service_name] = ServiceStatus(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.now()
        )
        logger.info(f"Registered service for monitoring: {service_name}")
    
    def register_health_check(self, service_name: str, check_function: Callable):
        """Register a custom health check function"""
        self.health_checks[service_name] = check_function
        logger.info(f"Registered health check function for: {service_name}")
    
    def unregister_service(self, service_name: str):
        """Unregister a service from monitoring"""
        if service_name in self.services:
            del self.services[service_name]
        if service_name in self.service_statuses:
            del self.service_statuses[service_name]
        if service_name in self.health_checks:
            del self.health_checks[service_name]
        
        # Stop monitoring task if running
        if service_name in self._monitoring_tasks:
            self._monitoring_tasks[service_name].cancel()
            del self._monitoring_tasks[service_name]
        
        logger.info(f"Unregistered service: {service_name}")
    
    async def check_service_health(self, service_name: str) -> HealthCheckResult:
        """Check health of a specific service"""
        start_time = time.time()
        
        try:
            # Try custom health check function first
            if service_name in self.health_checks:
                result = await self._run_custom_health_check(service_name)
                if result:
                    self._update_service_status(service_name, result)
                    return result
            
            # Try HTTP endpoint check
            if service_name in self.services:
                result = await self._check_http_endpoint(service_name)
                self._update_service_status(service_name, result)
                return result
            
            # No check method available
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                message="No health check method configured",
                timestamp=datetime.now(),
                response_time=response_time
            )
            self._update_service_status(service_name, result)
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=response_time
            )
            self._update_service_status(service_name, result)
            return result
    
    async def _run_custom_health_check(self, service_name: str) -> Optional[HealthCheckResult]:
        """Run custom health check function"""
        try:
            check_function = self.health_checks[service_name]
            
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            # Ensure result is HealthCheckResult
            if isinstance(result, HealthCheckResult):
                return result
            elif isinstance(result, dict):
                return HealthCheckResult(**result)
            else:
                logger.warning(f"Invalid health check result type for {service_name}")
                return None
                
        except Exception as e:
            logger.error(f"Custom health check failed for {service_name}: {e}")
            return None
    
    async def _check_http_endpoint(self, service_name: str) -> HealthCheckResult:
        """Check HTTP endpoint health"""
        endpoint = self.services[service_name]
        start_time = time.time()
        
        try:
            if not self._session:
                await self.initialize()
            
            async with self._session.request(
                method=endpoint.method,
                url=endpoint.url,
                headers=endpoint.headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == endpoint.expected_status:
                    status = HealthStatus.HEALTHY
                    message = f"HTTP {response.status} - OK"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"HTTP {response.status} - Expected {endpoint.expected_status}"
                
                return HealthCheckResult(
                    service_name=service_name,
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    metadata={
                        "url": endpoint.url,
                        "method": endpoint.method,
                        "status_code": response.status,
                        "expected_status": endpoint.expected_status
                    }
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Request timeout after {endpoint.timeout}s",
                timestamp=datetime.now(),
                response_time=response_time,
                metadata={"url": endpoint.url, "timeout": endpoint.timeout}
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Request failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=response_time,
                metadata={"url": endpoint.url, "error": str(e)}
            )
    
    def _update_service_status(self, service_name: str, result: HealthCheckResult):
        """Update service status from health check result"""
        if service_name not in self.service_statuses:
            self.service_statuses[service_name] = ServiceStatus(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now()
            )
        
        status = self.service_statuses[service_name]
        status.update_from_check(result)
        
        # Calculate uptime percentage
        if status.total_checks > 0:
            healthy_checks = status.total_checks - status.consecutive_failures
            status.uptime_percentage = (healthy_checks / status.total_checks) * 100
    
    async def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered services"""
        results = {}
        
        if not self._session:
            await self.initialize()
        
        # Check all services concurrently
        tasks = []
        service_names = list(self.services.keys()) + list(self.health_checks.keys())
        unique_services = list(set(service_names))
        
        for service_name in unique_services:
            task = asyncio.create_task(self.check_service_health(service_name))
            tasks.append((service_name, task))
        
        # Wait for all tasks to complete
        for service_name, task in tasks:
            try:
                result = await task
                results[service_name] = result
            except Exception as e:
                logger.error(f"Error checking {service_name}: {e}")
                results[service_name] = HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    timestamp=datetime.now(),
                    response_time=0.0
                )
        
        return results
    
    async def start_monitoring(self):
        """Start continuous monitoring of all services"""
        if self._monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self._monitoring_active = True
        
        # Start monitoring task for each service
        for service_name in self.services:
            task = asyncio.create_task(self._monitor_service_continuously(service_name))
            self._monitoring_tasks[service_name] = task
        
        logger.info(f"Started continuous monitoring for {len(self.services)} services")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self._monitoring_active = False
        
        # Cancel all monitoring tasks
        for task in self._monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete cancellation
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks.values(), return_exceptions=True)
        
        self._monitoring_tasks.clear()
        logger.info("Stopped continuous monitoring")
    
    async def _monitor_service_continuously(self, service_name: str):
        """Continuously monitor a specific service"""
        endpoint = self.services.get(service_name)
        if not endpoint:
            return
        
        check_interval = endpoint.check_interval
        
        while self._monitoring_active:
            try:
                await self.check_service_health(service_name)
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring for {service_name}: {e}")
                await asyncio.sleep(check_interval)
    
    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Get current status of a service"""
        return self.service_statuses.get(service_name)
    
    def get_all_service_statuses(self) -> Dict[str, ServiceStatus]:
        """Get status of all monitored services"""
        return self.service_statuses.copy()
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy services"""
        unhealthy = []
        for service_name, status in self.service_statuses.items():
            if status.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                unhealthy.append(service_name)
        return unhealthy
    
    def get_degraded_services(self) -> List[str]:
        """Get list of degraded services"""
        degraded = []
        for service_name, status in self.service_statuses.items():
            if status.status == HealthStatus.DEGRADED:
                degraded.append(service_name)
        return degraded
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring status"""
        total_services = len(self.service_statuses)
        healthy_count = len([s for s in self.service_statuses.values() 
                           if s.status == HealthStatus.HEALTHY])
        degraded_count = len([s for s in self.service_statuses.values() 
                            if s.status == HealthStatus.DEGRADED])
        unhealthy_count = len([s for s in self.service_statuses.values() 
                             if s.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]])
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_count,
            "degraded_services": degraded_count,
            "unhealthy_services": unhealthy_count,
            "monitoring_active": self._monitoring_active,
            "monitoring_tasks": len(self._monitoring_tasks),
            "registered_endpoints": len(self.services),
            "registered_health_checks": len(self.health_checks)
        }
    
    def reset_service_status(self, service_name: str):
        """Reset status for a specific service"""
        if service_name in self.service_statuses:
            self.service_statuses[service_name] = ServiceStatus(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now()
            )
            logger.info(f"Reset status for service: {service_name}")
    
    def update_service_endpoint(self, service_name: str, endpoint: ServiceEndpoint):
        """Update endpoint configuration for a service"""
        self.services[service_name] = endpoint
        logger.info(f"Updated endpoint configuration for: {service_name}")


# Built-in health check functions

async def neo4j_health_check() -> HealthCheckResult:
    """Built-in Neo4j health check"""
    try:
        from src.core.service_manager import ServiceManager
        service_manager = ServiceManager()
        neo4j_service = service_manager.get_neo4j_manager()
        
        start_time = time.time()
        
        with neo4j_service.get_driver().session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            
        response_time = (time.time() - start_time) * 1000
        
        if record and record["test"] == 1:
            return HealthCheckResult(
                service_name="neo4j",
                status=HealthStatus.HEALTHY,
                message="Neo4j database is accessible",
                timestamp=datetime.now(),
                response_time=response_time
            )
        else:
            return HealthCheckResult(
                service_name="neo4j",
                status=HealthStatus.UNHEALTHY,
                message="Neo4j query returned unexpected result",
                timestamp=datetime.now(),
                response_time=response_time
            )
            
    except Exception as e:
        return HealthCheckResult(
            service_name="neo4j",
            status=HealthStatus.UNHEALTHY,
            message=f"Neo4j connection failed: {str(e)}",
            timestamp=datetime.now(),
            response_time=0.0
        )


async def sqlite_health_check() -> HealthCheckResult:
    """Built-in SQLite health check"""
    try:
        import sqlite3
        import tempfile
        import os
        
        start_time = time.time()
        
        # Test with temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            if result and result[0] == 1:
                return HealthCheckResult(
                    service_name="sqlite",
                    status=HealthStatus.HEALTHY,
                    message="SQLite database is accessible",
                    timestamp=datetime.now(),
                    response_time=response_time
                )
            else:
                return HealthCheckResult(
                    service_name="sqlite",
                    status=HealthStatus.UNHEALTHY,
                    message="SQLite query returned unexpected result",
                    timestamp=datetime.now(),
                    response_time=response_time
                )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        return HealthCheckResult(
            service_name="sqlite",
            status=HealthStatus.UNHEALTHY,
            message=f"SQLite connection failed: {str(e)}",
            timestamp=datetime.now(),
            response_time=0.0
        )