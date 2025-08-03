"""
Enhanced Resource Manager

Manages computational resources during execution to optimize performance while
preventing resource exhaustion. Provides real-time monitoring and adaptive allocation.
"""

import logging
import time
import threading
import asyncio
import psutil
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import queue

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of computational resources"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    GPU = "gpu"
    DATABASE_CONNECTIONS = "db_connections"
    FILE_HANDLES = "file_handles"
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    FAIR_SHARE = "fair_share"          # Equal allocation to all requesters
    PRIORITY_BASED = "priority_based"   # Allocate based on priority
    DEMAND_BASED = "demand_based"      # Allocate based on demand
    ADAPTIVE = "adaptive"              # Adapt based on usage patterns
    GREEDY = "greedy"                  # Give maximum to highest priority


@dataclass
class ResourceLimit:
    """Resource limits and thresholds"""
    soft_limit: float                  # Warning threshold
    hard_limit: float                  # Maximum allowed
    emergency_limit: float             # Emergency threshold
    unit: str = "percentage"           # percentage, bytes, count, etc.


@dataclass
class ResourceRequest:
    """Request for resource allocation"""
    requester_id: str
    resource_type: ResourceType
    amount: float
    priority: int = 5                  # 1-10, higher is more important
    duration_estimate: float = 0.0     # seconds
    can_wait: bool = True
    timeout: float = 30.0              # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Allocated resource"""
    allocation_id: str
    requester_id: str
    resource_type: ResourceType
    allocated_amount: float
    allocation_time: float
    expires_at: Optional[float] = None
    is_active: bool = True
    actual_usage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceUsageMetrics:
    """Resource usage metrics"""
    resource_type: ResourceType
    current_usage: float
    peak_usage: float
    average_usage: float
    allocation_efficiency: float       # actual_usage / allocated_amount
    contention_level: float           # 0.0 = no contention, 1.0 = high contention
    wait_time_avg: float              # average wait time for allocations
    rejection_rate: float             # percentage of rejected requests
    timestamp: float = field(default_factory=time.time)


class EnhancedResourceManager:
    """Enhanced resource manager with real-time monitoring and adaptive allocation"""
    
    def __init__(self, allocation_strategy: AllocationStrategy = AllocationStrategy.ADAPTIVE):
        """Initialize enhanced resource manager"""
        self.allocation_strategy = allocation_strategy
        self.logger = logger
        
        # Resource limits and configuration
        self.resource_limits = self._initialize_resource_limits()
        self.allocation_pools: Dict[ResourceType, float] = self._initialize_allocation_pools()
        
        # Active allocations and requests
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.pending_requests: queue.PriorityQueue = queue.PriorityQueue()
        self.allocation_counter = 0
        
        # Monitoring and metrics
        self.usage_history: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=100))
        self.performance_metrics: Dict[ResourceType, ResourceUsageMetrics] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        self._allocation_event = threading.Event()
        
        # Background monitoring
        self._monitoring_enabled = True
        self._monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info(f"Initialized enhanced resource manager with {allocation_strategy.value} strategy")
    
    def _initialize_resource_limits(self) -> Dict[ResourceType, ResourceLimit]:
        """Initialize resource limits based on system capabilities"""
        
        # Get system information
        cpu_count = psutil.cpu_count()
        memory_total = psutil.virtual_memory().total
        
        return {
            ResourceType.CPU: ResourceLimit(
                soft_limit=70.0,    # 70% CPU utilization warning
                hard_limit=90.0,    # 90% maximum
                emergency_limit=95.0 # 95% emergency
            ),
            ResourceType.MEMORY: ResourceLimit(
                soft_limit=70.0,    # 70% memory warning
                hard_limit=85.0,    # 85% maximum
                emergency_limit=95.0 # 95% emergency
            ),
            ResourceType.DISK_IO: ResourceLimit(
                soft_limit=70.0,
                hard_limit=90.0,
                emergency_limit=95.0
            ),
            ResourceType.NETWORK_IO: ResourceLimit(
                soft_limit=70.0,
                hard_limit=90.0,
                emergency_limit=95.0
            ),
            ResourceType.DATABASE_CONNECTIONS: ResourceLimit(
                soft_limit=80.0,
                hard_limit=95.0,
                emergency_limit=100.0,
                unit="count"
            ),
            ResourceType.THREAD_POOL: ResourceLimit(
                soft_limit=float(cpu_count * 4),
                hard_limit=float(cpu_count * 8),
                emergency_limit=float(cpu_count * 12),
                unit="count"
            ),
            ResourceType.PROCESS_POOL: ResourceLimit(
                soft_limit=float(cpu_count),
                hard_limit=float(cpu_count * 2),
                emergency_limit=float(cpu_count * 3),
                unit="count"
            )
        }
    
    def _initialize_allocation_pools(self) -> Dict[ResourceType, float]:
        """Initialize allocation pools for each resource type"""
        
        return {
            ResourceType.CPU: 100.0,           # 100% available
            ResourceType.MEMORY: 100.0,        # 100% available
            ResourceType.DISK_IO: 100.0,       # 100% bandwidth
            ResourceType.NETWORK_IO: 100.0,    # 100% bandwidth
            ResourceType.DATABASE_CONNECTIONS: 50.0,  # 50 connections
            ResourceType.THREAD_POOL: float(psutil.cpu_count() * 4),
            ResourceType.PROCESS_POOL: float(psutil.cpu_count())
        }
    
    async def request_resource(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Request resource allocation"""
        
        self.logger.debug(f"Resource request from {request.requester_id}: "
                         f"{request.amount} {request.resource_type.value}")
        
        with self._lock:
            # Check if immediate allocation is possible
            if self._can_allocate_immediately(request):
                allocation = self._create_allocation(request)
                return allocation
            
            # Add to pending requests if can wait
            if request.can_wait:
                priority_score = self._calculate_priority_score(request)
                self.pending_requests.put((priority_score, time.time(), request))
                self.logger.debug(f"Added request to pending queue with priority {priority_score}")
            
            # Try to process pending requests
            await self._process_pending_requests()
            
            # Check if the request was fulfilled
            for allocation_id, allocation in self.active_allocations.items():
                if (allocation.requester_id == request.requester_id and 
                    allocation.resource_type == request.resource_type):
                    return allocation
            
            return None
    
    def release_resource(self, allocation_id: str) -> bool:
        """Release allocated resource"""
        
        with self._lock:
            if allocation_id in self.active_allocations:
                allocation = self.active_allocations[allocation_id]
                allocation.is_active = False
                
                # Return resource to pool
                self.allocation_pools[allocation.resource_type] += allocation.allocated_amount
                
                # Update usage metrics
                self._update_usage_metrics(allocation)
                
                # Remove from active allocations
                del self.active_allocations[allocation_id]
                
                self.logger.debug(f"Released allocation {allocation_id}")
                
                # Trigger processing of pending requests
                self._allocation_event.set()
                
                return True
        
        return False
    
    def update_resource_usage(self, allocation_id: str, actual_usage: float) -> None:
        """Update actual resource usage for an allocation"""
        
        with self._lock:
            if allocation_id in self.active_allocations:
                self.active_allocations[allocation_id].actual_usage = actual_usage
    
    def get_resource_metrics(self, resource_type: Optional[ResourceType] = None) -> Dict[str, Any]:
        """Get current resource metrics"""
        
        with self._lock:
            if resource_type:
                return self._get_single_resource_metrics(resource_type)
            else:
                return self._get_all_resource_metrics()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system resource status"""
        
        system_info = {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }
        
        with self._lock:
            system_info.update({
                'active_allocations': len(self.active_allocations),
                'pending_requests': self.pending_requests.qsize(),
                'allocation_pools': dict(self.allocation_pools),
                'resource_limits': {rt.value: {
                    'soft': limit.soft_limit,
                    'hard': limit.hard_limit,
                    'emergency': limit.emergency_limit
                } for rt, limit in self.resource_limits.items()}
            })
        
        return system_info
    
    def set_resource_limit(self, resource_type: ResourceType, 
                          soft_limit: float, hard_limit: float, 
                          emergency_limit: float) -> None:
        """Update resource limits"""
        
        with self._lock:
            self.resource_limits[resource_type] = ResourceLimit(
                soft_limit=soft_limit,
                hard_limit=hard_limit,
                emergency_limit=emergency_limit
            )
        
        self.logger.info(f"Updated limits for {resource_type.value}: "
                        f"soft={soft_limit}, hard={hard_limit}, emergency={emergency_limit}")
    
    def _can_allocate_immediately(self, request: ResourceRequest) -> bool:
        """Check if resource can be allocated immediately"""
        
        available = self.allocation_pools.get(request.resource_type, 0.0)
        limit = self.resource_limits.get(request.resource_type)
        
        if available < request.amount:
            return False
        
        # Check against hard limits
        if limit:
            current_usage = self._get_current_usage_percentage(request.resource_type)
            if current_usage + (request.amount / self.allocation_pools[request.resource_type] * 100) > limit.hard_limit:
                return False
        
        return True
    
    def _create_allocation(self, request: ResourceRequest) -> ResourceAllocation:
        """Create resource allocation"""
        
        self.allocation_counter += 1
        allocation_id = f"alloc_{self.allocation_counter:06d}"
        
        # Deduct from pool
        self.allocation_pools[request.resource_type] -= request.amount
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            requester_id=request.requester_id,
            resource_type=request.resource_type,
            allocated_amount=request.amount,
            allocation_time=time.time(),
            expires_at=time.time() + request.duration_estimate if request.duration_estimate > 0 else None,
            metadata=request.metadata
        )
        
        self.active_allocations[allocation_id] = allocation
        
        self.logger.debug(f"Created allocation {allocation_id} for {request.requester_id}")
        return allocation
    
    def _calculate_priority_score(self, request: ResourceRequest) -> float:
        """Calculate priority score for request (lower scores = higher priority)"""
        
        base_priority = 10 - request.priority  # Invert so lower is better
        
        # Add urgency factor based on timeout
        urgency_factor = max(0, (30.0 - request.timeout) / 30.0)
        
        # Add resource scarcity factor
        availability = self.allocation_pools.get(request.resource_type, 0.0)
        scarcity_factor = max(0, (100.0 - availability) / 100.0)
        
        return base_priority + urgency_factor + scarcity_factor
    
    async def _process_pending_requests(self) -> None:
        """Process pending resource requests"""
        
        processed = []
        
        while not self.pending_requests.empty():
            try:
                priority_score, timestamp, request = self.pending_requests.get_nowait()
                
                # Check timeout
                if time.time() - timestamp > request.timeout:
                    self.logger.debug(f"Request from {request.requester_id} timed out")
                    continue
                
                # Try to allocate
                if self._can_allocate_immediately(request):
                    allocation = self._create_allocation(request)
                    processed.append(allocation)
                else:
                    # Put back in queue
                    self.pending_requests.put((priority_score, timestamp, request))
                    break  # Can't process more right now
                    
            except queue.Empty:
                break
        
        if processed:
            self.logger.debug(f"Processed {len(processed)} pending requests")
    
    def _get_current_usage_percentage(self, resource_type: ResourceType) -> float:
        """Get current usage percentage for a resource type"""
        
        if resource_type == ResourceType.CPU:
            return psutil.cpu_percent(interval=0.1)
        elif resource_type == ResourceType.MEMORY:
            return psutil.virtual_memory().percent
        else:
            # For other resources, calculate based on allocations
            total_pool = self.allocation_pools[resource_type] + sum(
                alloc.allocated_amount for alloc in self.active_allocations.values()
                if alloc.resource_type == resource_type
            )
            used = sum(
                alloc.allocated_amount for alloc in self.active_allocations.values()
                if alloc.resource_type == resource_type
            )
            return (used / total_pool * 100) if total_pool > 0 else 0.0
    
    def _update_usage_metrics(self, allocation: ResourceAllocation) -> None:
        """Update usage metrics when resource is released"""
        
        duration = time.time() - allocation.allocation_time
        efficiency = (allocation.actual_usage / allocation.allocated_amount 
                     if allocation.allocated_amount > 0 else 0.0)
        
        # Add to history
        self.usage_history[allocation.resource_type].append({
            'timestamp': time.time(),
            'duration': duration,
            'allocated': allocation.allocated_amount,
            'actual_usage': allocation.actual_usage,
            'efficiency': efficiency
        })
    
    def _get_single_resource_metrics(self, resource_type: ResourceType) -> Dict[str, Any]:
        """Get metrics for a single resource type"""
        
        history = list(self.usage_history[resource_type])
        if not history:
            return {'resource_type': resource_type.value, 'no_data': True}
        
        # Calculate metrics
        efficiencies = [h['efficiency'] for h in history if h['efficiency'] is not None]
        durations = [h['duration'] for h in history]
        
        return {
            'resource_type': resource_type.value,
            'current_usage': self._get_current_usage_percentage(resource_type),
            'available_in_pool': self.allocation_pools[resource_type],
            'active_allocations': len([a for a in self.active_allocations.values() 
                                     if a.resource_type == resource_type]),
            'average_efficiency': sum(efficiencies) / len(efficiencies) if efficiencies else 0.0,
            'average_duration': sum(durations) / len(durations) if durations else 0.0,
            'total_allocations': len(history)
        }
    
    def _get_all_resource_metrics(self) -> Dict[str, Any]:
        """Get metrics for all resource types"""
        
        metrics = {}
        for resource_type in ResourceType:
            metrics[resource_type.value] = self._get_single_resource_metrics(resource_type)
        
        return metrics
    
    def _monitor_resources(self) -> None:
        """Background thread for resource monitoring"""
        
        while self._monitoring_enabled:
            try:
                # Clean up expired allocations
                self._cleanup_expired_allocations()
                
                # Process pending requests periodically
                asyncio.run(self._process_pending_requests())
                
                # Update system metrics
                self._update_system_metrics()
                
                # Check for resource emergencies
                self._check_resource_emergencies()
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring: {e}")
                time.sleep(5.0)  # Back off on error
    
    def _cleanup_expired_allocations(self) -> None:
        """Clean up expired allocations"""
        
        current_time = time.time()
        expired = []
        
        with self._lock:
            for allocation_id, allocation in self.active_allocations.items():
                if (allocation.expires_at and 
                    current_time > allocation.expires_at):
                    expired.append(allocation_id)
        
        for allocation_id in expired:
            self.release_resource(allocation_id)
            self.logger.debug(f"Auto-released expired allocation {allocation_id}")
    
    def _update_system_metrics(self) -> None:
        """Update system-level metrics"""
        
        # Update performance metrics for each resource type
        for resource_type in ResourceType:
            current_usage = self._get_current_usage_percentage(resource_type)
            
            if resource_type not in self.performance_metrics:
                self.performance_metrics[resource_type] = ResourceUsageMetrics(
                    resource_type=resource_type,
                    current_usage=current_usage,
                    peak_usage=current_usage,
                    average_usage=current_usage,
                    allocation_efficiency=0.0,
                    contention_level=0.0,
                    wait_time_avg=0.0,
                    rejection_rate=0.0
                )
            else:
                metrics = self.performance_metrics[resource_type]
                metrics.current_usage = current_usage
                metrics.peak_usage = max(metrics.peak_usage, current_usage)
                # Update other metrics based on recent history
                # ... (detailed implementation would go here)
    
    def _check_resource_emergencies(self) -> None:
        """Check for resource emergency conditions"""
        
        for resource_type, limit in self.resource_limits.items():
            current_usage = self._get_current_usage_percentage(resource_type)
            
            if current_usage > limit.emergency_limit:
                self.logger.critical(f"EMERGENCY: {resource_type.value} usage at {current_usage:.1f}% "
                                   f"(emergency limit: {limit.emergency_limit:.1f}%)")
                # In a real implementation, this might trigger emergency resource freeing
                
            elif current_usage > limit.hard_limit:
                self.logger.error(f"HIGH USAGE: {resource_type.value} usage at {current_usage:.1f}% "
                                f"(hard limit: {limit.hard_limit:.1f}%)")
                
            elif current_usage > limit.soft_limit:
                self.logger.warning(f"Resource warning: {resource_type.value} usage at {current_usage:.1f}% "
                                  f"(soft limit: {limit.soft_limit:.1f}%)")
    
    def shutdown(self) -> None:
        """Shutdown resource manager"""
        
        self.logger.info("Shutting down resource manager")
        self._monitoring_enabled = False
        
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        # Release all active allocations
        with self._lock:
            for allocation_id in list(self.active_allocations.keys()):
                self.release_resource(allocation_id)


# Factory function for easy instantiation
def create_resource_manager(strategy: AllocationStrategy = AllocationStrategy.ADAPTIVE) -> EnhancedResourceManager:
    """Create an enhanced resource manager"""
    return EnhancedResourceManager(strategy)