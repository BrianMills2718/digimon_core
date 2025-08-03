"""
Execution Controller

Controls and monitors execution flow with real-time status tracking,
event handling, and execution coordination.
"""

import asyncio
import logging
import time
from typing import Dict, List, Set, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict

from .execution_planner import ExecutionPlan, ExecutionStep

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status values"""
    PENDING = "pending"           # Not yet started
    INITIALIZING = "initializing" # Setting up for execution
    RUNNING = "running"           # Currently executing
    PAUSED = "paused"             # Temporarily paused
    COMPLETED = "completed"       # Successfully completed
    FAILED = "failed"             # Failed with errors
    CANCELLED = "cancelled"       # Cancelled by user/system
    TIMEOUT = "timeout"           # Timed out


class ExecutionEvent(Enum):
    """Types of execution events"""
    EXECUTION_STARTED = "execution_started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    EXECUTION_PAUSED = "execution_paused"
    EXECUTION_RESUMED = "execution_resumed"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_CANCELLED = "execution_cancelled"
    RESOURCE_WARNING = "resource_warning"
    QUALITY_ALERT = "quality_alert"
    PERFORMANCE_ALERT = "performance_alert"


@dataclass
class ExecutionEventData:
    """Data associated with execution events"""
    event_type: ExecutionEvent
    timestamp: float
    plan_id: str
    step_id: Optional[str] = None
    tool_ids: List[str] = field(default_factory=list)
    status: Optional[ExecutionStatus] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class StepStatus:
    """Status information for an execution step"""
    step_id: str
    status: ExecutionStatus
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    estimated_duration: float = 0.0
    actual_duration: Optional[float] = None
    progress: float = 0.0  # 0.0 to 1.0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    resource_usage: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ExecutionMonitoringData:
    """Comprehensive execution monitoring data"""
    plan_id: str
    overall_status: ExecutionStatus
    start_time: float
    estimated_end_time: Optional[float] = None
    actual_end_time: Optional[float] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    step_statuses: Dict[str, StepStatus] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    events: List[ExecutionEventData] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


class ExecutionController:
    """Controls and monitors execution flow with real-time coordination"""
    
    def __init__(self):
        """Initialize execution controller"""
        self.logger = logger
        
        # Execution state
        self.current_executions: Dict[str, ExecutionMonitoringData] = {}
        self.event_handlers: Dict[ExecutionEvent, List[Callable]] = defaultdict(list)
        
        # Monitoring configuration
        self.monitoring_interval = 1.0  # seconds
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Resource limits and thresholds
        self.resource_thresholds = {
            'cpu': 0.8,      # 80% CPU usage warning
            'memory': 0.85,  # 85% memory usage warning
            'disk_io': 0.9   # 90% disk I/O warning
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'step_timeout_multiplier': 2.0,  # Alert if step takes >2x estimated time
            'quality_minimum': 0.6,          # Alert if quality drops below 60%
            'progress_stall_time': 30.0      # Alert if no progress for 30 seconds
        }
        
        # Execution coordination
        self.execution_lock = asyncio.Lock()
        self.pause_events: Dict[str, asyncio.Event] = {}
        self.cancellation_events: Dict[str, asyncio.Event] = {}
        
        self.logger.info("Initialized execution controller with real-time monitoring")
    
    async def start_execution_monitoring(self, execution_plan: ExecutionPlan) -> None:
        """Start monitoring an execution plan"""
        
        plan_id = execution_plan.plan_id
        
        self.logger.info(f"Starting execution monitoring for plan {plan_id}")
        
        # Initialize monitoring data
        monitoring_data = ExecutionMonitoringData(
            plan_id=plan_id,
            overall_status=ExecutionStatus.INITIALIZING,
            start_time=time.time(),
            total_steps=len(execution_plan.steps),
            estimated_end_time=time.time() + execution_plan.total_estimated_time
        )
        
        # Initialize step statuses
        for step in execution_plan.steps:
            step_status = StepStatus(
                step_id=step.step_id,
                status=ExecutionStatus.PENDING,
                estimated_duration=step.estimated_duration
            )
            monitoring_data.step_statuses[step.step_id] = step_status
        
        self.current_executions[plan_id] = monitoring_data
        
        # Initialize pause and cancellation events
        self.pause_events[plan_id] = asyncio.Event()
        self.pause_events[plan_id].set()  # Start unpaused
        self.cancellation_events[plan_id] = asyncio.Event()
        
        # Start monitoring task if not already running
        if not self.monitoring_active:
            await self._start_monitoring_loop()
        
        # Fire execution started event
        await self._fire_event(ExecutionEventData(
            event_type=ExecutionEvent.EXECUTION_STARTED,
            timestamp=time.time(),
            plan_id=plan_id,
            status=ExecutionStatus.INITIALIZING,
            message=f"Started monitoring execution plan with {len(execution_plan.steps)} steps"
        ))
        
        # Update status to running
        monitoring_data.overall_status = ExecutionStatus.RUNNING
    
    async def stop_execution_monitoring(self, plan_id: Optional[str] = None) -> None:
        """Stop monitoring execution(s)"""
        
        if plan_id:
            # Stop monitoring specific execution
            if plan_id in self.current_executions:
                self.logger.info(f"Stopping execution monitoring for plan {plan_id}")
                
                monitoring_data = self.current_executions[plan_id]
                if monitoring_data.overall_status == ExecutionStatus.RUNNING:
                    monitoring_data.overall_status = ExecutionStatus.COMPLETED
                    monitoring_data.actual_end_time = time.time()
                
                # Clean up events
                if plan_id in self.pause_events:
                    del self.pause_events[plan_id]
                if plan_id in self.cancellation_events:
                    del self.cancellation_events[plan_id]
                
                # Fire completion event
                await self._fire_event(ExecutionEventData(
                    event_type=ExecutionEvent.EXECUTION_COMPLETED,
                    timestamp=time.time(),
                    plan_id=plan_id,
                    status=monitoring_data.overall_status,
                    message="Execution monitoring stopped"
                ))
        else:
            # Stop all monitoring
            self.logger.info("Stopping all execution monitoring")
            
            for plan_id in list(self.current_executions.keys()):
                await self.stop_execution_monitoring(plan_id)
            
            # Stop monitoring loop
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
                self.monitoring_active = False
    
    async def update_step_status(self, plan_id: str, step_id: str, 
                               status: ExecutionStatus, **kwargs) -> None:
        """Update status of an execution step"""
        
        if plan_id not in self.current_executions:
            self.logger.warning(f"Cannot update step status - execution {plan_id} not found")
            return
        
        monitoring_data = self.current_executions[plan_id]
        
        if step_id not in monitoring_data.step_statuses:
            self.logger.warning(f"Cannot update step status - step {step_id} not found")
            return
        
        step_status = monitoring_data.step_statuses[step_id]
        old_status = step_status.status
        step_status.status = status
        
        current_time = time.time()
        
        # Update step timing
        if status == ExecutionStatus.RUNNING and step_status.start_time is None:
            step_status.start_time = current_time
        elif status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
            if step_status.end_time is None:
                step_status.end_time = current_time
                if step_status.start_time:
                    step_status.actual_duration = current_time - step_status.start_time
        
        # Update progress
        if 'progress' in kwargs:
            step_status.progress = kwargs['progress']
        elif status == ExecutionStatus.COMPLETED:
            step_status.progress = 1.0
        
        # Update error message
        if 'error' in kwargs:
            step_status.error_message = kwargs['error']
        
        # Update resource usage
        if 'resource_usage' in kwargs:
            step_status.resource_usage.update(kwargs['resource_usage'])
        
        # Update quality metrics
        if 'quality_metrics' in kwargs:
            step_status.quality_metrics.update(kwargs['quality_metrics'])
        
        # Update overall execution counters
        self._update_execution_counters(monitoring_data)
        
        # Fire appropriate event
        event_type = self._get_event_type_for_status(status)
        if event_type:
            await self._fire_event(ExecutionEventData(
                event_type=event_type,
                timestamp=current_time,
                plan_id=plan_id,
                step_id=step_id,
                status=status,
                message=kwargs.get('message', f"Step {step_id} status changed to {status.value}"),
                error=kwargs.get('error'),
                metadata=kwargs.get('metadata', {})
            ))
        
        self.logger.debug(f"Updated step {step_id} status: {old_status.value} -> {status.value}")
    
    async def update_resource_usage(self, plan_id: str, resource_usage: Dict[str, float]) -> None:
        """Update resource usage metrics"""
        
        if plan_id not in self.current_executions:
            return
        
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.resource_usage.update(resource_usage)
        
        # Check for resource warnings
        for resource, usage in resource_usage.items():
            threshold = self.resource_thresholds.get(resource, 1.0)
            if usage > threshold:
                warning_msg = f"High {resource} usage: {usage:.1%} (threshold: {threshold:.1%})"
                monitoring_data.warnings.append(warning_msg)
                
                await self._fire_event(ExecutionEventData(
                    event_type=ExecutionEvent.RESOURCE_WARNING,
                    timestamp=time.time(),
                    plan_id=plan_id,
                    message=warning_msg,
                    metadata={'resource': resource, 'usage': usage, 'threshold': threshold}
                ))
    
    async def update_performance_metrics(self, plan_id: str, metrics: Dict[str, float]) -> None:
        """Update performance metrics"""
        
        if plan_id not in self.current_executions:
            return
        
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.performance_metrics.update(metrics)
        
        # Check for performance alerts
        if 'average_step_time' in metrics:
            avg_time = metrics['average_step_time']
            if avg_time > 60.0:  # Steps taking more than 1 minute on average
                alert = {
                    'type': 'slow_execution',
                    'message': f'Average step execution time is high: {avg_time:.1f}s',
                    'severity': 'medium',
                    'timestamp': time.time()
                }
                monitoring_data.alerts.append(alert)
                
                await self._fire_event(ExecutionEventData(
                    event_type=ExecutionEvent.PERFORMANCE_ALERT,
                    timestamp=time.time(),
                    plan_id=plan_id,
                    message=alert['message'],
                    metadata=alert
                ))
    
    async def update_quality_metrics(self, plan_id: str, metrics: Dict[str, float]) -> None:
        """Update quality metrics"""
        
        if plan_id not in self.current_executions:
            return
        
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.quality_metrics.update(metrics)
        
        # Check for quality alerts
        for metric_name, quality_value in metrics.items():
            threshold = self.performance_thresholds['quality_minimum']
            if quality_value < threshold:
                alert = {
                    'type': 'low_quality',
                    'metric': metric_name,
                    'value': quality_value,
                    'threshold': threshold,
                    'message': f'Quality metric {metric_name} below threshold: {quality_value:.2f} < {threshold:.2f}',
                    'severity': 'high' if quality_value < threshold * 0.8 else 'medium',
                    'timestamp': time.time()
                }
                monitoring_data.alerts.append(alert)
                
                await self._fire_event(ExecutionEventData(
                    event_type=ExecutionEvent.QUALITY_ALERT,
                    timestamp=time.time(),
                    plan_id=plan_id,
                    message=alert['message'],
                    metadata=alert
                ))
    
    async def pause_execution(self, plan_id: str) -> bool:
        """Pause execution"""
        
        if plan_id not in self.current_executions:
            return False
        
        if plan_id not in self.pause_events:
            return False
        
        self.logger.info(f"Pausing execution {plan_id}")
        
        # Clear pause event to pause execution
        self.pause_events[plan_id].clear()
        
        # Update status
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.overall_status = ExecutionStatus.PAUSED
        
        # Fire pause event
        await self._fire_event(ExecutionEventData(
            event_type=ExecutionEvent.EXECUTION_PAUSED,
            timestamp=time.time(),
            plan_id=plan_id,
            status=ExecutionStatus.PAUSED,
            message="Execution paused by request"
        ))
        
        return True
    
    async def resume_execution(self, plan_id: str) -> bool:
        """Resume paused execution"""
        
        if plan_id not in self.current_executions:
            return False
        
        if plan_id not in self.pause_events:
            return False
        
        self.logger.info(f"Resuming execution {plan_id}")
        
        # Set pause event to resume execution
        self.pause_events[plan_id].set()
        
        # Update status
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.overall_status = ExecutionStatus.RUNNING
        
        # Fire resume event
        await self._fire_event(ExecutionEventData(
            event_type=ExecutionEvent.EXECUTION_RESUMED,
            timestamp=time.time(),
            plan_id=plan_id,
            status=ExecutionStatus.RUNNING,
            message="Execution resumed"
        ))
        
        return True
    
    async def cancel_execution(self, plan_id: str) -> bool:
        """Cancel execution"""
        
        if plan_id not in self.current_executions:
            return False
        
        self.logger.info(f"Cancelling execution {plan_id}")
        
        # Set cancellation event
        if plan_id in self.cancellation_events:
            self.cancellation_events[plan_id].set()
        
        # Update status
        monitoring_data = self.current_executions[plan_id]
        monitoring_data.overall_status = ExecutionStatus.CANCELLED
        monitoring_data.actual_end_time = time.time()
        
        # Update all pending/running steps to cancelled
        for step_status in monitoring_data.step_statuses.values():
            if step_status.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
                step_status.status = ExecutionStatus.CANCELLED
                if step_status.end_time is None:
                    step_status.end_time = time.time()
        
        # Fire cancellation event
        await self._fire_event(ExecutionEventData(
            event_type=ExecutionEvent.EXECUTION_CANCELLED,
            timestamp=time.time(),
            plan_id=plan_id,
            status=ExecutionStatus.CANCELLED,
            message="Execution cancelled by request"
        ))
        
        return True
    
    async def wait_for_pause_or_cancel(self, plan_id: str) -> str:
        """Wait for pause or cancel signal, returns 'pause', 'cancel', or 'continue'"""
        
        if plan_id not in self.pause_events or plan_id not in self.cancellation_events:
            return 'continue'
        
        # Check if cancelled
        if self.cancellation_events[plan_id].is_set():
            return 'cancel'
        
        # Wait for pause event (set = continue, clear = pause)
        if not self.pause_events[plan_id].is_set():
            return 'pause'
        
        return 'continue'
    
    async def wait_for_resume(self, plan_id: str) -> bool:
        """Wait for execution to be resumed (returns False if cancelled)"""
        
        if plan_id not in self.pause_events or plan_id not in self.cancellation_events:
            return True
        
        # Wait for either resume (pause event set) or cancel (cancel event set)
        done, pending = await asyncio.wait([
            asyncio.create_task(self.pause_events[plan_id].wait()),
            asyncio.create_task(self.cancellation_events[plan_id].wait())
        ], return_when=asyncio.FIRST_COMPLETED)
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
        
        # Check which event was triggered
        if self.cancellation_events[plan_id].is_set():
            return False  # Cancelled
        else:
            return True   # Resumed
    
    async def handle_execution_failure(self, execution_plan: ExecutionPlan, error: str) -> None:
        """Handle execution failure"""
        
        plan_id = execution_plan.plan_id
        
        self.logger.error(f"Execution {plan_id} failed: {error}")
        
        if plan_id in self.current_executions:
            monitoring_data = self.current_executions[plan_id]
            monitoring_data.overall_status = ExecutionStatus.FAILED
            monitoring_data.actual_end_time = time.time()
            
            # Fire failure event
            await self._fire_event(ExecutionEventData(
                event_type=ExecutionEvent.EXECUTION_FAILED,
                timestamp=time.time(),
                plan_id=plan_id,
                status=ExecutionStatus.FAILED,
                message=f"Execution failed: {error}",
                error=error
            ))
    
    def get_execution_status(self, plan_id: str) -> Optional[ExecutionMonitoringData]:
        """Get current execution status"""
        return self.current_executions.get(plan_id)
    
    def get_all_execution_statuses(self) -> Dict[str, ExecutionMonitoringData]:
        """Get all current execution statuses"""
        return self.current_executions.copy()
    
    def register_event_handler(self, event_type: ExecutionEvent, 
                             handler: Callable[[ExecutionEventData], None]) -> None:
        """Register event handler"""
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered handler for {event_type.value} events")
    
    def unregister_event_handler(self, event_type: ExecutionEvent,
                                handler: Callable[[ExecutionEventData], None]) -> None:
        """Unregister event handler"""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            self.logger.debug(f"Unregistered handler for {event_type.value} events")
    
    async def _start_monitoring_loop(self) -> None:
        """Start the monitoring loop"""
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started execution monitoring loop")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        
        try:
            while self.monitoring_active:
                await asyncio.sleep(self.monitoring_interval)
                
                # Check all active executions
                for plan_id, monitoring_data in list(self.current_executions.items()):
                    await self._check_execution_health(plan_id, monitoring_data)
                    await self._check_execution_timeouts(plan_id, monitoring_data)
                    await self._check_execution_progress(plan_id, monitoring_data)
                
                # Remove completed executions after some time
                await self._cleanup_old_executions()
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.monitoring_active = False
    
    async def _check_execution_health(self, plan_id: str, 
                                    monitoring_data: ExecutionMonitoringData) -> None:
        """Check execution health and detect issues"""
        
        current_time = time.time()
        
        # Check for stalled execution
        if monitoring_data.overall_status == ExecutionStatus.RUNNING:
            # Find if any steps are taking too long
            for step_id, step_status in monitoring_data.step_statuses.items():
                if step_status.status == ExecutionStatus.RUNNING and step_status.start_time:
                    elapsed_time = current_time - step_status.start_time
                    timeout_threshold = step_status.estimated_duration * self.performance_thresholds['step_timeout_multiplier']
                    
                    if elapsed_time > timeout_threshold:
                        warning_msg = f"Step {step_id} taking longer than expected: {elapsed_time:.1f}s > {timeout_threshold:.1f}s"
                        monitoring_data.warnings.append(warning_msg)
                        
                        await self._fire_event(ExecutionEventData(
                            event_type=ExecutionEvent.PERFORMANCE_ALERT,
                            timestamp=current_time,
                            plan_id=plan_id,
                            step_id=step_id,
                            message=warning_msg,
                            metadata={'elapsed_time': elapsed_time, 'threshold': timeout_threshold}
                        ))
    
    async def _check_execution_timeouts(self, plan_id: str,
                                      monitoring_data: ExecutionMonitoringData) -> None:
        """Check for execution timeouts"""
        
        current_time = time.time()
        
        # Check overall execution timeout
        if (monitoring_data.estimated_end_time and 
            current_time > monitoring_data.estimated_end_time and
            monitoring_data.overall_status == ExecutionStatus.RUNNING):
            
            # Execution has exceeded estimated time
            overtime = current_time - monitoring_data.estimated_end_time
            
            if overtime > 60.0:  # More than 1 minute overtime
                monitoring_data.overall_status = ExecutionStatus.TIMEOUT
                monitoring_data.actual_end_time = current_time
                
                await self._fire_event(ExecutionEventData(
                    event_type=ExecutionEvent.EXECUTION_FAILED,
                    timestamp=current_time,
                    plan_id=plan_id,
                    status=ExecutionStatus.TIMEOUT,
                    message=f"Execution timed out after {overtime:.1f}s overtime",
                    error="Execution timeout"
                ))
    
    async def _check_execution_progress(self, plan_id: str,
                                      monitoring_data: ExecutionMonitoringData) -> None:
        """Check execution progress and detect stalls"""
        
        current_time = time.time()
        
        # Calculate overall progress
        total_progress = 0.0
        active_steps = 0
        
        for step_status in monitoring_data.step_statuses.values():
            total_progress += step_status.progress
            if step_status.status in [ExecutionStatus.RUNNING, ExecutionStatus.PENDING]:
                active_steps += 1
        
        overall_progress = total_progress / len(monitoring_data.step_statuses) if monitoring_data.step_statuses else 0.0
        
        # Check for progress stalls
        last_progress_time = getattr(monitoring_data, 'last_progress_time', monitoring_data.start_time)
        last_progress_value = getattr(monitoring_data, 'last_progress_value', 0.0)
        
        if overall_progress > last_progress_value:
            # Progress made
            monitoring_data.last_progress_time = current_time
            monitoring_data.last_progress_value = overall_progress
        elif (current_time - last_progress_time > self.performance_thresholds['progress_stall_time'] and
              active_steps > 0):
            # Progress stalled
            warning_msg = f"Execution progress stalled for {current_time - last_progress_time:.1f}s"
            monitoring_data.warnings.append(warning_msg)
            
            await self._fire_event(ExecutionEventData(
                event_type=ExecutionEvent.PERFORMANCE_ALERT,
                timestamp=current_time,
                plan_id=plan_id,
                message=warning_msg,
                metadata={'stall_time': current_time - last_progress_time, 'progress': overall_progress}
            ))
    
    async def _cleanup_old_executions(self) -> None:
        """Clean up old completed executions"""
        
        current_time = time.time()
        cleanup_threshold = 3600.0  # 1 hour
        
        to_remove = []
        
        for plan_id, monitoring_data in self.current_executions.items():
            if (monitoring_data.overall_status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED] and
                monitoring_data.actual_end_time and
                current_time - monitoring_data.actual_end_time > cleanup_threshold):
                to_remove.append(plan_id)
        
        for plan_id in to_remove:
            self.logger.debug(f"Cleaning up old execution {plan_id}")
            del self.current_executions[plan_id]
            
            # Clean up events
            if plan_id in self.pause_events:
                del self.pause_events[plan_id]
            if plan_id in self.cancellation_events:
                del self.cancellation_events[plan_id]
    
    def _update_execution_counters(self, monitoring_data: ExecutionMonitoringData) -> None:
        """Update execution counters based on step statuses"""
        
        completed = 0
        failed = 0
        skipped = 0
        
        for step_status in monitoring_data.step_statuses.values():
            if step_status.status == ExecutionStatus.COMPLETED:
                completed += 1
            elif step_status.status == ExecutionStatus.FAILED:
                failed += 1
            elif step_status.status == ExecutionStatus.CANCELLED:
                skipped += 1
        
        monitoring_data.completed_steps = completed
        monitoring_data.failed_steps = failed
        monitoring_data.skipped_steps = skipped
        
        # Update overall status based on step completion
        if completed + failed + skipped == monitoring_data.total_steps:
            # All steps finished
            if failed > 0:
                monitoring_data.overall_status = ExecutionStatus.FAILED
            else:
                monitoring_data.overall_status = ExecutionStatus.COMPLETED
            
            if monitoring_data.actual_end_time is None:
                monitoring_data.actual_end_time = time.time()
    
    def _get_event_type_for_status(self, status: ExecutionStatus) -> Optional[ExecutionEvent]:
        """Get event type for step status change"""
        
        status_to_event = {
            ExecutionStatus.RUNNING: ExecutionEvent.STEP_STARTED,
            ExecutionStatus.COMPLETED: ExecutionEvent.STEP_COMPLETED,
            ExecutionStatus.FAILED: ExecutionEvent.STEP_FAILED,
            ExecutionStatus.CANCELLED: ExecutionEvent.STEP_SKIPPED
        }
        
        return status_to_event.get(status)
    
    async def _fire_event(self, event_data: ExecutionEventData) -> None:
        """Fire an execution event"""
        
        # Add to execution events if plan exists
        if event_data.plan_id in self.current_executions:
            self.current_executions[event_data.plan_id].events.append(event_data)
        
        # Call registered handlers
        handlers = self.event_handlers.get(event_data.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_data.event_type.value}: {e}")
        
        self.logger.debug(f"Fired event: {event_data.event_type.value} for plan {event_data.plan_id}")
    
    def get_execution_summary(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get execution summary"""
        
        if plan_id not in self.current_executions:
            return None
        
        monitoring_data = self.current_executions[plan_id]
        current_time = time.time()
        
        # Calculate execution time
        if monitoring_data.actual_end_time:
            execution_time = monitoring_data.actual_end_time - monitoring_data.start_time
        else:
            execution_time = current_time - monitoring_data.start_time
        
        # Calculate progress
        total_progress = sum(step.progress for step in monitoring_data.step_statuses.values())
        overall_progress = total_progress / len(monitoring_data.step_statuses) if monitoring_data.step_statuses else 0.0
        
        return {
            'plan_id': plan_id,
            'status': monitoring_data.overall_status.value,
            'progress': overall_progress,
            'execution_time': execution_time,
            'total_steps': monitoring_data.total_steps,
            'completed_steps': monitoring_data.completed_steps,
            'failed_steps': monitoring_data.failed_steps,
            'skipped_steps': monitoring_data.skipped_steps,
            'warnings_count': len(monitoring_data.warnings),
            'alerts_count': len(monitoring_data.alerts),
            'events_count': len(monitoring_data.events),
            'resource_usage': monitoring_data.resource_usage,
            'performance_metrics': monitoring_data.performance_metrics,
            'quality_metrics': monitoring_data.quality_metrics
        }
    
    def get_detailed_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed execution status"""
        
        if plan_id not in self.current_executions:
            return None
        
        monitoring_data = self.current_executions[plan_id]
        
        # Convert step statuses to dict format
        step_statuses = {}
        for step_id, step_status in monitoring_data.step_statuses.items():
            step_statuses[step_id] = {
                'status': step_status.status.value,
                'progress': step_status.progress,
                'start_time': step_status.start_time,
                'end_time': step_status.end_time,
                'estimated_duration': step_status.estimated_duration,
                'actual_duration': step_status.actual_duration,
                'error_message': step_status.error_message,
                'retry_count': step_status.retry_count,
                'resource_usage': step_status.resource_usage,
                'quality_metrics': step_status.quality_metrics
            }
        
        # Convert events to dict format
        events = []
        for event in monitoring_data.events[-10:]:  # Last 10 events
            events.append({
                'event_type': event.event_type.value,
                'timestamp': event.timestamp,
                'step_id': event.step_id,
                'status': event.status.value if event.status else None,
                'message': event.message,
                'error': event.error
            })
        
        return {
            'plan_id': plan_id,
            'overall_status': monitoring_data.overall_status.value,
            'start_time': monitoring_data.start_time,
            'estimated_end_time': monitoring_data.estimated_end_time,
            'actual_end_time': monitoring_data.actual_end_time,
            'step_statuses': step_statuses,
            'resource_usage': monitoring_data.resource_usage,
            'performance_metrics': monitoring_data.performance_metrics,
            'quality_metrics': monitoring_data.quality_metrics,
            'warnings': monitoring_data.warnings[-5:],  # Last 5 warnings
            'alerts': monitoring_data.alerts[-5:],       # Last 5 alerts
            'recent_events': events
        }