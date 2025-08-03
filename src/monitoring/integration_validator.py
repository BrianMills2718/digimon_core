#!/usr/bin/env python3
"""
Integration Validation and Monitoring System

Provides real-time health checks, performance monitoring, and alerting
for the integrated KGAS infrastructure and tools.
"""

import asyncio
import logging
import time
import json
import threading
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import psutil
from contextlib import asynccontextmanager
import aiofiles

# Import infrastructure and tool components
from ..core.infrastructure_integration import InfrastructureIntegrator, IntegrationConfiguration, IntegrationMode
from ..core.service_manager import ServiceManager
from ..tools.tool_registry import ToolRegistry, ImplementationStatus
from ..testing.end_to_end_workflow_tester import EndToEndWorkflowTester
from ..testing.performance_benchmarker import PerformanceBenchmarker

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    component: str
    check_name: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    

@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    enabled: bool = True
    interval_seconds: int = 30
    timeout_seconds: int = 10
    retry_count: int = 3
    failure_threshold: int = 3
    recovery_threshold: int = 2


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str  # Python expression evaluated against metrics
    severity: AlertSeverity
    message_template: str
    cooldown_minutes: int = 5
    enabled: bool = True


@dataclass
class Alert:
    """Generated alert"""
    rule_name: str
    severity: AlertSeverity
    message: str
    component: str
    triggered_at: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    resolved_at: Optional[datetime] = None


class IntegrationValidator:
    """Comprehensive integration validation and monitoring system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize integration validator"""
        self.config = self._load_config(config_path)
        self.service_manager = ServiceManager()
        self.tool_registry = ToolRegistry()
        
        # Monitoring state
        self._monitoring = False
        self._monitoring_task = None
        self._health_checks = {}
        self._validation_history = []
        self._alerts = []
        self._alert_cooldowns = {}
        
        # Components to monitor
        self.infrastructure_integrator = None
        self.workflow_tester = None
        self.performance_benchmarker = None
        
        # Health check configurations
        self.health_check_configs = {
            'infrastructure': HealthCheckConfig(interval_seconds=30),
            'services': HealthCheckConfig(interval_seconds=60),
            'tools': HealthCheckConfig(interval_seconds=120),
            'workflows': HealthCheckConfig(interval_seconds=300),
            'performance': HealthCheckConfig(interval_seconds=180)
        }
        
        # Alert rules
        self.alert_rules = self._initialize_alert_rules()
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("Integration validator initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load validation configuration"""
        default_config = {
            'monitoring': {
                'enabled': True,
                'log_level': 'INFO',
                'alert_webhook_url': None,
                'history_retention_days': 7
            },
            'validation': {
                'infrastructure_timeout': 30,
                'service_timeout': 10,
                'tool_timeout': 60,
                'workflow_timeout': 300
            },
            'performance': {
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'response_time_threshold': 5.0,
                'error_rate_threshold': 0.05
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Initialize default alert rules"""
        return [
            AlertRule(
                name="high_cpu_usage",
                condition="cpu_percent > 80",
                severity=AlertSeverity.WARNING,
                message_template="High CPU usage detected: {cpu_percent:.1f}%",
                cooldown_minutes=5
            ),
            AlertRule(
                name="high_memory_usage", 
                condition="memory_percent > 85",
                severity=AlertSeverity.WARNING,
                message_template="High memory usage detected: {memory_percent:.1f}%",
                cooldown_minutes=5
            ),
            AlertRule(
                name="critical_memory_usage",
                condition="memory_percent > 95",
                severity=AlertSeverity.CRITICAL,
                message_template="Critical memory usage: {memory_percent:.1f}%",
                cooldown_minutes=2
            ),
            AlertRule(
                name="slow_response_time",
                condition="avg_response_time > 5.0",
                severity=AlertSeverity.WARNING,
                message_template="Slow response times detected: {avg_response_time:.2f}s",
                cooldown_minutes=10
            ),
            AlertRule(
                name="high_error_rate",
                condition="error_rate > 0.05",
                severity=AlertSeverity.ERROR,
                message_template="High error rate detected: {error_rate:.1%}",
                cooldown_minutes=3
            ),
            AlertRule(
                name="service_failure",
                condition="failed_services > 0",
                severity=AlertSeverity.CRITICAL,
                message_template="{failed_services} service(s) failed health checks",
                cooldown_minutes=1
            ),
            AlertRule(
                name="infrastructure_failure",
                condition="infrastructure_status == 'CRITICAL'",
                severity=AlertSeverity.CRITICAL,
                message_template="Infrastructure integration failure detected",
                cooldown_minutes=1
            )
        ]
    
    async def initialize_components(self) -> bool:
        """Initialize monitoring components"""
        try:
            logger.info("Initializing integration monitoring components...")
            
            # Initialize infrastructure integrator
            config = IntegrationConfiguration(
                mode=IntegrationMode.PERFORMANCE,
                enable_caching=True,
                enable_parallel_processing=True,
                enable_resource_monitoring=True,
                performance_monitoring=True
            )
            self.infrastructure_integrator = InfrastructureIntegrator(config)
            
            # Initialize infrastructure
            if not await self.infrastructure_integrator.initialize():
                logger.error("Failed to initialize infrastructure integrator")
                return False
            
            # Initialize workflow tester
            self.workflow_tester = EndToEndWorkflowTester()
            await self.workflow_tester.initialize()
            
            # Initialize performance benchmarker
            self.performance_benchmarker = PerformanceBenchmarker()
            await self.performance_benchmarker.initialize()
            
            logger.info("Integration monitoring components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring components: {e}", exc_info=True)
            return False
    
    async def start_monitoring(self) -> bool:
        """Start continuous monitoring"""
        if self._monitoring:
            logger.warning("Monitoring already started")
            return True
        
        try:
            # Initialize components if not already done
            if not self.infrastructure_integrator:
                if not await self.initialize_components():
                    return False
            
            self._monitoring = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Integration monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}", exc_info=True)
            self._monitoring = False
            return False
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        logger.info("Integration monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        while self._monitoring:
            try:
                # Run all health checks
                await self._run_health_checks()
                
                # Process alerts
                await self._process_alerts()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Wait for next iteration
                await asyncio.sleep(10)  # Base monitoring interval
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(30)  # Extended wait on error
    
    async def _run_health_checks(self):
        """Run all configured health checks"""
        current_time = datetime.now()
        
        # Check which health checks need to run
        checks_to_run = []
        
        for component, config in self.health_check_configs.items():
            if not config.enabled:
                continue
            
            last_check = self._health_checks.get(component, {}).get('last_check')
            if not last_check or (current_time - last_check).total_seconds() >= config.interval_seconds:
                checks_to_run.append(component)
        
        # Run health checks in parallel
        if checks_to_run:
            tasks = []
            for component in checks_to_run:
                tasks.append(self._run_component_health_check(component))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for component, result in zip(checks_to_run, results):
                if isinstance(result, Exception):
                    logger.error(f"Health check failed for {component}: {result}")
                    self._record_health_check_result(component, ValidationStatus.CRITICAL, str(result))
                else:
                    self._record_health_check_result(component, result.status, result.message, result.details)
    
    async def _run_component_health_check(self, component: str) -> ValidationResult:
        """Run health check for specific component"""
        start_time = time.time()
        
        try:
            if component == 'infrastructure':
                return await self._check_infrastructure_health()
            elif component == 'services':
                return await self._check_services_health()
            elif component == 'tools':
                return await self._check_tools_health()
            elif component == 'workflows':
                return await self._check_workflows_health()
            elif component == 'performance':
                return await self._check_performance_health()
            else:
                return ValidationResult(
                    component=component,
                    check_name="unknown",
                    status=ValidationStatus.UNKNOWN,
                    message=f"Unknown component: {component}",
                    duration_ms=(time.time() - start_time) * 1000
                )
                
        except Exception as e:
            logger.error(f"Health check error for {component}: {e}", exc_info=True)
            return ValidationResult(
                component=component,
                check_name="exception",
                status=ValidationStatus.CRITICAL,
                message=f"Health check exception: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_infrastructure_health(self) -> ValidationResult:
        """Check infrastructure integration health"""
        start_time = time.time()
        
        try:
            if not self.infrastructure_integrator:
                return ValidationResult(
                    component="infrastructure",
                    check_name="integrator_availability",
                    status=ValidationStatus.CRITICAL,
                    message="Infrastructure integrator not initialized",
                    duration_ms=(time.time() - start_time) * 1000
                )
            
            # Get integration metrics
            metrics = self.infrastructure_integrator.get_integration_metrics()
            
            # Check component health
            component_health = metrics.get('component_status', {})
            failed_components = [k for k, v in component_health.items() if not v]
            
            if failed_components:
                status = ValidationStatus.CRITICAL
                message = f"Failed components: {', '.join(failed_components)}"
            else:
                # Check performance metrics
                perf_metrics = metrics.get('performance_metrics', {})
                cache_hit_rate = float(perf_metrics.get('cache_hit_rate', '0%').rstrip('%')) / 100
                
                if cache_hit_rate < 0.3:  # Below 30% cache hit rate
                    status = ValidationStatus.WARNING
                    message = f"Low cache hit rate: {cache_hit_rate:.1%}"
                else:
                    status = ValidationStatus.HEALTHY
                    message = "Infrastructure integration healthy"
            
            return ValidationResult(
                component="infrastructure",
                check_name="integration_health",
                status=status,
                message=message,
                details=metrics,
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return ValidationResult(
                component="infrastructure",
                check_name="integration_health",
                status=ValidationStatus.CRITICAL,
                message=f"Infrastructure health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_services_health(self) -> ValidationResult:
        """Check core services health"""
        start_time = time.time()
        
        try:
            # Check service manager health
            health_status = self.service_manager.health_check()
            failed_services = [name for name, healthy in health_status.items() if not healthy]
            
            if failed_services:
                status = ValidationStatus.CRITICAL
                message = f"Failed services: {', '.join(failed_services)}"
            else:
                status = ValidationStatus.HEALTHY
                message = f"All {len(health_status)} services healthy"
            
            return ValidationResult(
                component="services",
                check_name="service_health",
                status=status,
                message=message,
                details={"service_status": health_status},
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return ValidationResult(
                component="services",
                check_name="service_health",
                status=ValidationStatus.CRITICAL,
                message=f"Service health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_tools_health(self) -> ValidationResult:
        """Check tool registry and implementation health"""
        start_time = time.time()
        
        try:
            # Get implementation status
            status_summary = self.tool_registry.get_implementation_status()
            
            total_tools = sum(status_summary.values())
            implemented_tools = status_summary.get(ImplementationStatus.IMPLEMENTED.value, 0)
            implementation_rate = implemented_tools / total_tools if total_tools > 0 else 0
            
            if implementation_rate < 0.2:  # Less than 20% implemented
                status = ValidationStatus.WARNING
                message = f"Low tool implementation rate: {implementation_rate:.1%} ({implemented_tools}/{total_tools})"
            else:
                status = ValidationStatus.HEALTHY
                message = f"Tool implementation rate: {implementation_rate:.1%} ({implemented_tools}/{total_tools})"
            
            return ValidationResult(
                component="tools",
                check_name="implementation_status",
                status=status,
                message=message,
                details={
                    "status_summary": status_summary,
                    "implementation_rate": implementation_rate
                },
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return ValidationResult(
                component="tools",
                check_name="implementation_status",
                status=ValidationStatus.CRITICAL,
                message=f"Tool health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_workflows_health(self) -> ValidationResult:
        """Check workflow execution health"""
        start_time = time.time()
        
        try:
            if not self.workflow_tester:
                return ValidationResult(
                    component="workflows",
                    check_name="workflow_tester_availability",
                    status=ValidationStatus.WARNING,
                    message="Workflow tester not initialized",
                    duration_ms=(time.time() - start_time) * 1000
                )
            
            # Run a basic workflow test
            test_result = await self.workflow_tester.test_basic_workflow()
            
            if test_result['status'] == 'success':
                status = ValidationStatus.HEALTHY
                message = f"Basic workflow completed in {test_result['execution_time']:.2f}s"
            else:
                status = ValidationStatus.CRITICAL
                message = f"Basic workflow failed: {test_result.get('error', 'Unknown error')}"
            
            return ValidationResult(
                component="workflows",
                check_name="basic_workflow_test",
                status=status,
                message=message,
                details=test_result,
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return ValidationResult(
                component="workflows",
                check_name="basic_workflow_test",
                status=ValidationStatus.CRITICAL,
                message=f"Workflow health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_performance_health(self) -> ValidationResult:
        """Check system performance health"""
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine overall status
            issues = []
            if cpu_percent > self.config['performance']['cpu_threshold']:
                issues.append(f"High CPU: {cpu_percent:.1f}%")
            
            if memory.percent > self.config['performance']['memory_threshold']:
                issues.append(f"High memory: {memory.percent:.1f}%")
            
            if disk.percent > 90:  # High disk usage
                issues.append(f"High disk: {disk.percent:.1f}%")
            
            if issues:
                status = ValidationStatus.WARNING
                message = f"Performance issues: {', '.join(issues)}"
            else:
                status = ValidationStatus.HEALTHY
                message = f"System performance healthy (CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%)"
            
            return ValidationResult(
                component="performance",
                check_name="system_performance",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3)
                },
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return ValidationResult(
                component="performance",
                check_name="system_performance",
                status=ValidationStatus.CRITICAL,
                message=f"Performance health check failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def _record_health_check_result(self, component: str, status: ValidationStatus, 
                                   message: str, details: Dict[str, Any] = None):
        """Record health check result"""
        with self._lock:
            self._health_checks[component] = {
                'last_check': datetime.now(),
                'status': status,
                'message': message,
                'details': details or {}
            }
            
            # Add to validation history
            self._validation_history.append({
                'component': component,
                'status': status.value,
                'message': message,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            })
    
    async def _process_alerts(self):
        """Process alert rules and generate alerts"""
        current_time = datetime.now()
        
        # Gather current metrics
        metrics = await self._gather_alert_metrics()
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert = self._alert_cooldowns.get(rule.name)
            if last_alert and (current_time - last_alert).total_seconds() < rule.cooldown_minutes * 60:
                continue
            
            try:
                # Evaluate alert condition
                if self._evaluate_alert_condition(rule.condition, metrics):
                    alert = Alert(
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.message_template.format(**metrics),
                        component=self._get_component_from_condition(rule.condition),
                        triggered_at=current_time,
                        details=metrics
                    )
                    
                    await self._trigger_alert(alert)
                    self._alert_cooldowns[rule.name] = current_time
                    
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.name}: {e}")
    
    async def _gather_alert_metrics(self) -> Dict[str, Any]:
        """Gather metrics for alert evaluation"""
        metrics = {}
        
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            metrics.update({
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3)
            })
            
            # Health check status
            failed_services = sum(1 for status in self._health_checks.values() 
                                if status['status'] == ValidationStatus.CRITICAL)
            metrics['failed_services'] = failed_services
            
            # Infrastructure status
            if self.infrastructure_integrator:
                integration_metrics = self.infrastructure_integrator.get_integration_metrics()
                perf_metrics = integration_metrics.get('performance_metrics', {})
                
                # Extract numeric values
                cache_hit_rate = float(perf_metrics.get('cache_hit_rate', '0%').rstrip('%')) / 100
                avg_speedup = float(perf_metrics.get('average_speedup', '1.0x').rstrip('x'))
                
                metrics.update({
                    'cache_hit_rate': cache_hit_rate,
                    'average_speedup': avg_speedup,
                    'total_operations': perf_metrics.get('total_operations', 0),
                    'infrastructure_status': 'HEALTHY' if failed_services == 0 else 'CRITICAL'
                })
            
            # Calculate derived metrics
            recent_validations = [v for v in self._validation_history 
                                if datetime.fromisoformat(v['timestamp']) > datetime.now() - timedelta(minutes=10)]
            
            if recent_validations:
                error_count = sum(1 for v in recent_validations if v['status'] == ValidationStatus.CRITICAL.value)
                metrics['error_rate'] = error_count / len(recent_validations)
                
                # Average response time (mock calculation for now)
                metrics['avg_response_time'] = 2.0  # Would be calculated from actual metrics
            else:
                metrics['error_rate'] = 0.0
                metrics['avg_response_time'] = 0.0
            
        except Exception as e:
            logger.error(f"Error gathering alert metrics: {e}")
        
        return metrics
    
    def _evaluate_alert_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition expression"""
        try:
            # Create safe evaluation environment
            safe_globals = {"__builtins__": {}}
            return eval(condition, safe_globals, metrics)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _get_component_from_condition(self, condition: str) -> str:
        """Extract component name from alert condition"""
        if 'infrastructure' in condition.lower():
            return 'infrastructure'
        elif 'service' in condition.lower():
            return 'services'
        elif 'cpu' in condition.lower() or 'memory' in condition.lower():
            return 'performance'
        else:
            return 'system'
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        with self._lock:
            self._alerts.append(alert)
        
        logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.component}: {alert.message}")
        
        # Send webhook notification if configured
        webhook_url = self.config.get('monitoring', {}).get('alert_webhook_url')
        if webhook_url:
            await self._send_webhook_alert(webhook_url, alert)
    
    async def _send_webhook_alert(self, webhook_url: str, alert: Alert):
        """Send alert via webhook"""
        try:
            import aiohttp
            
            payload = {
                'rule_name': alert.rule_name,
                'severity': alert.severity.value,
                'message': alert.message,
                'component': alert.component,
                'triggered_at': alert.triggered_at.isoformat(),
                'details': alert.details
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Alert webhook sent successfully for {alert.rule_name}")
                    else:
                        logger.warning(f"Alert webhook failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old validation history and alerts"""
        retention_days = self.config.get('monitoring', {}).get('history_retention_days', 7)
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        with self._lock:
            # Clean validation history
            self._validation_history = [
                v for v in self._validation_history
                if datetime.fromisoformat(v['timestamp']) > cutoff_time
            ]
            
            # Clean alerts
            self._alerts = [
                a for a in self._alerts
                if a.triggered_at > cutoff_time
            ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        with self._lock:
            overall_status = ValidationStatus.HEALTHY
            component_statuses = {}
            
            for component, health_info in self._health_checks.items():
                status = health_info['status']
                component_statuses[component] = {
                    'status': status.value,
                    'message': health_info['message'],
                    'last_check': health_info['last_check'].isoformat()
                }
                
                # Determine overall status
                if status == ValidationStatus.CRITICAL:
                    overall_status = ValidationStatus.CRITICAL
                elif status == ValidationStatus.WARNING and overall_status == ValidationStatus.HEALTHY:
                    overall_status = ValidationStatus.WARNING
            
            return {
                'overall_status': overall_status.value,
                'components': component_statuses,
                'monitoring_enabled': self._monitoring,
                'last_update': datetime.now().isoformat()
            }
    
    async def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            recent_alerts = [
                {
                    'rule_name': alert.rule_name,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'component': alert.component,
                    'triggered_at': alert.triggered_at.isoformat(),
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in self._alerts
                if alert.triggered_at > cutoff_time
            ]
            
            return sorted(recent_alerts, key=lambda x: x['triggered_at'], reverse=True)
    
    async def export_monitoring_data(self, output_path: str) -> bool:
        """Export monitoring data to file"""
        try:
            monitoring_data = {
                'health_status': await self.get_health_status(),
                'recent_alerts': await self.get_recent_alerts(),
                'validation_history': self._validation_history[-1000:],  # Last 1000 entries
                'alert_rules': [
                    {
                        'name': rule.name,
                        'condition': rule.condition,
                        'severity': rule.severity.value,
                        'enabled': rule.enabled
                    }
                    for rule in self.alert_rules
                ],
                'exported_at': datetime.now().isoformat()
            }
            
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(json.dumps(monitoring_data, indent=2))
            
            logger.info(f"Monitoring data exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export monitoring data: {e}")
            return False
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            await self.stop_monitoring()
            
            if self.infrastructure_integrator:
                await self.infrastructure_integrator.cleanup()
            
            if self.workflow_tester:
                await self.workflow_tester.cleanup()
            
            if self.performance_benchmarker:
                await self.performance_benchmarker.cleanup()
            
            logger.info("Integration validator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)


# Factory functions for common monitoring scenarios
def create_production_validator(config_path: Optional[str] = None) -> IntegrationValidator:
    """Create validator for production monitoring"""
    validator = IntegrationValidator(config_path)
    
    # Configure for production
    validator.health_check_configs['infrastructure'].interval_seconds = 60
    validator.health_check_configs['services'].interval_seconds = 120
    validator.health_check_configs['performance'].interval_seconds = 30
    
    return validator


def create_development_validator(config_path: Optional[str] = None) -> IntegrationValidator:
    """Create validator for development monitoring"""
    validator = IntegrationValidator(config_path)
    
    # Configure for development
    validator.health_check_configs['workflows'].enabled = False  # Skip workflow tests
    validator.health_check_configs['performance'].interval_seconds = 300  # Less frequent
    
    return validator


# Example usage and testing
if __name__ == "__main__":
    async def test_integration_validator():
        """Test integration validator"""
        
        # Create validator
        validator = create_production_validator()
        
        try:
            # Initialize components
            success = await validator.initialize_components()
            if not success:
                print("Failed to initialize validator components")
                return
            
            # Start monitoring
            success = await validator.start_monitoring()
            if not success:
                print("Failed to start monitoring")
                return
            
            print("Integration monitoring started successfully")
            
            # Let it run for a bit
            await asyncio.sleep(60)
            
            # Get health status
            health_status = await validator.get_health_status()
            print(f"Health Status: {health_status['overall_status']}")
            print(f"Components: {len(health_status['components'])}")
            
            # Get recent alerts
            alerts = await validator.get_recent_alerts(hours=1)
            print(f"Recent alerts: {len(alerts)}")
            
            # Export monitoring data
            await validator.export_monitoring_data("monitoring_report.json")
            print("Monitoring data exported")
            
        finally:
            await validator.cleanup()
    
    # Run test
    asyncio.run(test_integration_validator())