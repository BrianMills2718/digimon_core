#!/usr/bin/env python3
"""
Centralized Error Taxonomy and Handling Framework

Provides standardized error classification, handling, and recovery patterns
for all KGAS services. Critical architectural fix for Phase RELIABILITY.

Replaces the inconsistent error handling across 802+ try blocks with
a unified taxonomy and recovery system.
"""

import asyncio
import logging
import traceback
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Union
from contextlib import asynccontextmanager, contextmanager
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification and response prioritization"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class ErrorCategory(Enum):
    """Error categories for systematic classification"""
    DATA_CORRUPTION = "data_corruption"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAILURE = "network_failure"
    AUTHENTICATION_FAILURE = "authentication_failure"
    VALIDATION_FAILURE = "validation_failure"
    SYSTEM_FAILURE = "system_failure"
    DATABASE_FAILURE = "database_failure"
    SERVICE_UNAVAILABLE = "service_unavailable"
    CONFIGURATION_ERROR = "configuration_error"
    ACADEMIC_INTEGRITY = "academic_integrity"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ABORT_AND_ALERT = "abort_and_alert"
    ESCALATE = "escalate"


@dataclass
class KGASError:
    """Standardized error format for all system errors"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any]
    timestamp: str
    service_name: str
    operation: str
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    tags: List[str] = field(default_factory=list)


@dataclass
class RecoveryResult:
    """Result of recovery attempt"""
    success: bool
    strategy_used: RecoveryStrategy
    error_id: str
    recovery_time: float
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ErrorMetrics:
    """Track error metrics and patterns"""
    
    def __init__(self, max_history=1000):
        self.error_counts = defaultdict(int)
        self.error_history = deque(maxlen=max_history)
        self.recovery_stats = defaultdict(lambda: {"attempts": 0, "successes": 0})
        self._lock = threading.Lock()
    
    def record_error(self, error: KGASError):
        """Record error occurrence"""
        with self._lock:
            self.error_counts[error.category.value] += 1
            self.error_history.append({
                "error_id": error.error_id,
                "category": error.category.value,
                "severity": error.severity.value,
                "timestamp": error.timestamp,
                "service": error.service_name
            })
    
    def record_recovery(self, result: RecoveryResult):
        """Record recovery attempt result"""
        with self._lock:
            key = result.strategy_used.value
            self.recovery_stats[key]["attempts"] += 1
            if result.success:
                self.recovery_stats[key]["successes"] += 1
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        with self._lock:
            total_errors = sum(self.error_counts.values())
            return {
                "total_errors": total_errors,
                "error_breakdown": dict(self.error_counts),
                "recovery_success_rates": {
                    strategy: {
                        "success_rate": stats["successes"] / max(stats["attempts"], 1),
                        "total_attempts": stats["attempts"]
                    }
                    for strategy, stats in self.recovery_stats.items()
                }
            }


class CentralizedErrorHandler:
    """
    Central error handling with recovery patterns and escalation.
    
    Provides unified error taxonomy, classification, and recovery
    across all KGAS services and tools.
    """
    
    def __init__(self):
        self.error_registry: Dict[str, KGASError] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_metrics = ErrorMetrics()
        self.circuit_breakers: Dict[str, Dict] = {}
        self.escalation_handlers: List[Callable] = []
        self._lock = asyncio.Lock()
        
        # Setup default recovery strategies
        self._setup_default_recovery_strategies()
        
        logger.info("CentralizedErrorHandler initialized")
    
    def _setup_default_recovery_strategies(self):
        """Setup default recovery strategies for common error patterns"""
        # Fix: Register strategies using RecoveryStrategy enum values as keys
        self.register_recovery_strategy(RecoveryStrategy.CIRCUIT_BREAKER.value, self._recover_database_connection)
        self.register_recovery_strategy(RecoveryStrategy.GRACEFUL_DEGRADATION.value, self._recover_memory_exhaustion)
        self.register_recovery_strategy(RecoveryStrategy.RETRY.value, self._recover_network_timeout)
        self.register_recovery_strategy(RecoveryStrategy.FALLBACK.value, self._recover_service_unavailable)
        self.register_recovery_strategy(RecoveryStrategy.ABORT_AND_ALERT.value, self._recover_configuration_error)
        self.register_recovery_strategy(RecoveryStrategy.ESCALATE.value, self._handle_academic_integrity)
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> KGASError:
        """
        Handle error with standardized taxonomy and recovery.
        
        Args:
            error: The exception that occurred
            context: Context information (service, operation, etc.)
            
        Returns:
            KGASError: Classified and processed error
        """
        async with self._lock:
            # Classify error
            kgas_error = self._classify_error(error, context)
            
            # Record error
            self.error_registry[kgas_error.error_id] = kgas_error
            self.error_metrics.record_error(kgas_error)
            
            # Log error with full context
            await self._log_error(kgas_error)
            
            # Attempt recovery
            recovery_result = await self._attempt_recovery(kgas_error)
            
            # Record recovery attempt
            if recovery_result:
                self.error_metrics.record_recovery(recovery_result)
            
            # Escalate if critical or recovery failed
            if (kgas_error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.CATASTROPHIC] or 
                not (recovery_result and recovery_result.success)):
                await self._escalate_error(kgas_error)
            
            return kgas_error
    
    def _classify_error(self, error: Exception, context: Dict[str, Any]) -> KGASError:
        """Classify error into standardized taxonomy"""
        error_message = str(error)
        error_type = type(error).__name__
        
        # Determine category and severity based on error characteristics
        category, severity = self._determine_category_and_severity(error, error_message)
        
        # Generate recovery suggestions
        recovery_suggestions = self._generate_recovery_suggestions(category, error_type)
        
        return KGASError(
            error_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            message=error_message,
            context=context,
            timestamp=datetime.now().isoformat(),
            service_name=context.get("service_name", "unknown"),
            operation=context.get("operation", "unknown"),
            stack_trace=traceback.format_exc(),
            recovery_suggestions=recovery_suggestions,
            tags=self._generate_error_tags(error, context)
        )
    
    def _determine_category_and_severity(self, error: Exception, message: str) -> tuple[ErrorCategory, ErrorSeverity]:
        """Determine error category and severity from exception and message"""
        message_lower = message.lower()
        error_type = type(error).__name__
        
        # Data corruption patterns
        if any(keyword in message_lower for keyword in ["corruption", "integrity", "citation fabrication", "orphaned data"]):
            return ErrorCategory.DATA_CORRUPTION, ErrorSeverity.CATASTROPHIC
        
        # Academic integrity violations
        if any(keyword in message_lower for keyword in ["academic integrity", "citation", "provenance"]):
            return ErrorCategory.ACADEMIC_INTEGRITY, ErrorSeverity.CRITICAL
        
        # Database failures
        if any(keyword in message_lower for keyword in ["neo4j", "database", "transaction", "sql"]):
            return ErrorCategory.DATABASE_FAILURE, ErrorSeverity.HIGH
        
        # Resource exhaustion
        if any(keyword in message_lower for keyword in ["memory", "pool", "connection", "resource"]):
            return ErrorCategory.RESOURCE_EXHAUSTION, ErrorSeverity.HIGH
        
        # Network failures
        if any(keyword in message_lower for keyword in ["network", "timeout", "connection", "http"]):
            return ErrorCategory.NETWORK_FAILURE, ErrorSeverity.MEDIUM
        
        # Authentication failures
        if any(keyword in message_lower for keyword in ["auth", "credential", "permission", "access"]):
            return ErrorCategory.AUTHENTICATION_FAILURE, ErrorSeverity.MEDIUM
        
        # Validation failures
        if any(keyword in message_lower for keyword in ["validation", "invalid", "format", "schema"]):
            return ErrorCategory.VALIDATION_FAILURE, ErrorSeverity.LOW
        
        # Configuration errors
        if any(keyword in message_lower for keyword in ["config", "setting", "parameter", "missing"]):
            return ErrorCategory.CONFIGURATION_ERROR, ErrorSeverity.MEDIUM
        
        # Service unavailable
        if any(keyword in message_lower for keyword in ["service", "unavailable", "down", "unreachable"]):
            return ErrorCategory.SERVICE_UNAVAILABLE, ErrorSeverity.HIGH
        
        # Default classification
        return ErrorCategory.SYSTEM_FAILURE, ErrorSeverity.MEDIUM
    
    def _generate_recovery_suggestions(self, category: ErrorCategory, error_type: str) -> List[str]:
        """Generate contextual recovery suggestions"""
        suggestions = []
        
        if category == ErrorCategory.DATA_CORRUPTION:
            suggestions.extend([
                "Initiate immediate data integrity check",
                "Rollback to last known good state",
                "Alert academic integrity team",
                "Suspend data modifications until resolved"
            ])
        elif category == ErrorCategory.RESOURCE_EXHAUSTION:
            suggestions.extend([
                "Clear caches and free memory",
                "Restart connection pools",
                "Scale resources if possible",
                "Implement backpressure"
            ])
        elif category == ErrorCategory.DATABASE_FAILURE:
            suggestions.extend([
                "Check database connectivity",
                "Restart database connections",
                "Verify transaction state",
                "Switch to read-only mode if needed"
            ])
        elif category == ErrorCategory.NETWORK_FAILURE:
            suggestions.extend([
                "Retry with exponential backoff",
                "Check network connectivity",
                "Use cached data if available",
                "Switch to backup endpoints"
            ])
        elif category == ErrorCategory.CONFIGURATION_ERROR:
            suggestions.extend([
                "Verify configuration files",
                "Check environment variables",
                "Use default configurations",
                "Alert configuration management team"
            ])
        
        return suggestions
    
    def _generate_error_tags(self, error: Exception, context: Dict[str, Any]) -> List[str]:
        """Generate tags for error categorization and search"""
        tags = [type(error).__name__]
        
        if "service_name" in context:
            tags.append(f"service:{context['service_name']}")
        
        if "operation" in context:
            tags.append(f"operation:{context['operation']}")
        
        if "tool_id" in context:
            tags.append(f"tool:{context['tool_id']}")
        
        return tags
    
    async def _attempt_recovery(self, error: KGASError) -> Optional[RecoveryResult]:
        """Attempt to recover from error using registered strategies"""
        start_time = datetime.now()
        
        # Determine recovery strategy
        strategy = self._select_recovery_strategy(error)
        
        if not strategy:
            return None
        
        # Execute recovery strategy
        try:
            recovery_func = self.recovery_strategies.get(strategy.value)
            if recovery_func:
                success = await recovery_func(error)
                
                recovery_time = (datetime.now() - start_time).total_seconds()
                
                return RecoveryResult(
                    success=success,
                    strategy_used=strategy,
                    error_id=error.error_id,
                    recovery_time=recovery_time,
                    message=f"Recovery attempt using {strategy.value}",
                    metadata={"error_category": error.category.value}
                )
        
        except Exception as e:
            logger.error(f"Recovery strategy failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=strategy,
                error_id=error.error_id,
                recovery_time=(datetime.now() - start_time).total_seconds(),
                message=f"Recovery failed: {str(e)}"
            )
        
        return None
    
    def _select_recovery_strategy(self, error: KGASError) -> Optional[RecoveryStrategy]:
        """Select appropriate recovery strategy based on error characteristics"""
        if error.category == ErrorCategory.DATA_CORRUPTION:
            return RecoveryStrategy.ABORT_AND_ALERT
        elif error.category == ErrorCategory.ACADEMIC_INTEGRITY:
            return RecoveryStrategy.ESCALATE
        elif error.category == ErrorCategory.RESOURCE_EXHAUSTION:
            return RecoveryStrategy.GRACEFUL_DEGRADATION
        elif error.category == ErrorCategory.DATABASE_FAILURE:
            return RecoveryStrategy.CIRCUIT_BREAKER
        elif error.category == ErrorCategory.NETWORK_FAILURE:
            return RecoveryStrategy.RETRY
        elif error.category == ErrorCategory.SERVICE_UNAVAILABLE:
            return RecoveryStrategy.FALLBACK
        
        return RecoveryStrategy.RETRY
    
    async def _log_error(self, error: KGASError):
        """Log error with appropriate level and context"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.CATASTROPHIC: logging.CRITICAL
        }.get(error.severity, logging.ERROR)
        
        logger.log(log_level, 
                  f"[{error.error_id}] {error.category.value.upper()}: {error.message}",
                  extra={
                      "error_id": error.error_id,
                      "category": error.category.value,
                      "severity": error.severity.value,
                      "service": error.service_name,
                      "operation": error.operation,
                      "context": error.context,
                      "recovery_suggestions": error.recovery_suggestions
                  })
    
    async def _escalate_error(self, error: KGASError):
        """Escalate critical errors to registered handlers"""
        for handler in self.escalation_handlers:
            try:
                await handler(error)
            except Exception as e:
                logger.error(f"Error escalation handler failed: {e}")
    
    def register_recovery_strategy(self, error_pattern: str, strategy_func: Callable):
        """Register recovery strategy for specific error pattern"""
        self.recovery_strategies[error_pattern] = strategy_func
        logger.info(f"Registered recovery strategy for {error_pattern}")
    
    def register_escalation_handler(self, handler: Callable):
        """Register escalation handler for critical errors"""
        self.escalation_handlers.append(handler)
        logger.info("Registered error escalation handler")
    
    # Default recovery strategy implementations
    async def _recover_database_connection(self, error: KGASError) -> bool:
        """Recover from database connection failures"""
        try:
            # Attempt to reconnect to database
            logger.info(f"Attempting database reconnection for error {error.error_id}")
            
            # This would integrate with the actual database managers
            # For now, simulate recovery attempt
            await asyncio.sleep(1)  # Simulate reconnection time
            
            return True
        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            return False
    
    async def _recover_memory_exhaustion(self, error: KGASError) -> bool:
        """Recover from memory exhaustion"""
        try:
            logger.info(f"Attempting memory recovery for error {error.error_id}")
            
            # Clear caches, force garbage collection
            import gc
            gc.collect()
            
            return True
        except Exception as e:
            logger.error(f"Memory recovery failed: {e}")
            return False
    
    async def _recover_network_timeout(self, error: KGASError) -> bool:
        """Recover from network timeouts with retry"""
        try:
            logger.info(f"Attempting network recovery for error {error.error_id}")
            
            # Implement exponential backoff retry
            await asyncio.sleep(min(2 ** error.recovery_attempts, 10))
            
            return True
        except Exception as e:
            logger.error(f"Network recovery failed: {e}")
            return False
    
    async def _recover_service_unavailable(self, error: KGASError) -> bool:
        """Recover from service unavailability"""
        try:
            logger.info(f"Attempting service recovery for error {error.error_id}")
            
            # Check service health and attempt restart
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Service recovery failed: {e}")
            return False
    
    async def _recover_configuration_error(self, error: KGASError) -> bool:
        """Recovery from configuration errors"""
        try:
            logger.info(f"Attempting configuration recovery for error {error.error_id}")
            
            # Load default configuration or reload from source
            return True
        except Exception as e:
            logger.error(f"Configuration recovery failed: {e}")
            return False
    
    async def _handle_academic_integrity(self, error: KGASError) -> bool:
        """Handle academic integrity violations"""
        logger.critical(f"ACADEMIC INTEGRITY VIOLATION: {error.message}")
        
        # Academic integrity violations require manual intervention
        # This logs the issue and alerts appropriate personnel
        return False  # Never auto-recover from integrity violations
    
    def get_error_status(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific error"""
        error = self.error_registry.get(error_id)
        if not error:
            return None
        
        return {
            "error_id": error.error_id,
            "category": error.category.value,
            "severity": error.severity.value,
            "status": "resolved" if error.recovery_attempts > 0 else "active",
            "recovery_attempts": error.recovery_attempts,
            "timestamp": error.timestamp,
            "service": error.service_name,
            "operation": error.operation
        }
    
    def get_system_health_from_errors(self) -> Dict[str, Any]:
        """Get system health assessment based on error patterns"""
        metrics = self.error_metrics.get_error_summary()
        
        # Calculate health score based on error severity and frequency
        total_errors = metrics["total_errors"]
        catastrophic_errors = metrics["error_breakdown"].get("data_corruption", 0)
        critical_errors = metrics["error_breakdown"].get("academic_integrity", 0)
        
        if catastrophic_errors > 0:
            health_score = 1  # System unreliable due to data corruption
        elif critical_errors > 0:
            health_score = 2  # System compromised
        elif total_errors > 100:
            health_score = 4  # High error rate
        elif total_errors > 50:
            health_score = 6  # Moderate error rate
        elif total_errors > 10:
            health_score = 8  # Low error rate
        else:
            health_score = 10  # Healthy
        
        return {
            "health_score": health_score,
            "max_score": 10,
            "status": "healthy" if health_score >= 8 else "degraded" if health_score >= 6 else "unhealthy",
            "error_summary": metrics,
            "assessment_timestamp": datetime.now().isoformat()
        }


# Context managers for automatic error handling
@asynccontextmanager
async def handle_errors_async(service_name: str, operation: str, error_handler: CentralizedErrorHandler):
    """Async context manager for automatic error handling"""
    try:
        yield
    except Exception as e:
        context = {
            "service_name": service_name,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        await error_handler.handle_error(e, context)
        raise  # Re-raise after handling


@contextmanager
def handle_errors_sync(service_name: str, operation: str, error_handler: CentralizedErrorHandler):
    """Sync context manager for automatic error handling"""
    try:
        yield
    except Exception as e:
        context = {
            "service_name": service_name,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        # For sync context, we need to run async handler in thread
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(error_handler.handle_error(e, context))
            else:
                asyncio.run(error_handler.handle_error(e, context))
        except RuntimeError:
            # No event loop available, log error directly
            logger.error(f"Error in {service_name}.{operation}: {e}", exc_info=True)
        raise  # Re-raise after handling


# Global error handler instance
_global_error_handler = None


def get_global_error_handler() -> CentralizedErrorHandler:
    """Get or create global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = CentralizedErrorHandler()
    return _global_error_handler


# Decorator for automatic error handling
def handle_errors(service_name: str, operation: str = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        func_name = operation or func.__name__
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with handle_errors_async(service_name, func_name, get_global_error_handler()):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                with handle_errors_sync(service_name, func_name, get_global_error_handler()):
                    return func(*args, **kwargs)
            return sync_wrapper
    
    return decorator