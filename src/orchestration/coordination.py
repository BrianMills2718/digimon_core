"""
Agent Coordination and Synchronization Mechanisms.

Provides coordination primitives and patterns for parallel agent execution,
including barriers, locks, event propagation, and shared state management.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Set, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class CoordinationEventType(Enum):
    """Types of coordination events."""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    RESOURCE_ACQUIRED = "resource_acquired"
    RESOURCE_RELEASED = "resource_released"
    CHECKPOINT_REACHED = "checkpoint_reached"
    DATA_AVAILABLE = "data_available"
    BARRIER_REACHED = "barrier_reached"
    WORKFLOW_EVENT = "workflow_event"


@dataclass
class CoordinationEvent:
    """Event for agent coordination."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: CoordinationEventType = CoordinationEventType.WORKFLOW_EVENT
    source_agent: str = ""
    target_agents: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    requires_ack: bool = False
    ack_timeout: float = 30.0


@dataclass
class SharedState:
    """Shared state container for agent coordination."""
    state_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: Dict[str, Any] = field(default_factory=dict)
    version: int = 0
    last_modified: datetime = field(default_factory=datetime.now)
    locked_by: Optional[str] = None
    readers: Set[str] = field(default_factory=set)


class CoordinationManager:
    """
    Manages coordination and synchronization between parallel agents.
    
    Provides coordination primitives like barriers, locks, events,
    and shared state management for parallel agent execution.
    """
    
    def __init__(self):
        """Initialize coordination manager."""
        # Event management
        self._event_bus: Dict[str, List[Callable]] = defaultdict(list)
        self._pending_events: asyncio.Queue = asyncio.Queue()
        self._event_history: List[CoordinationEvent] = []
        
        # Synchronization primitives
        self._barriers: Dict[str, asyncio.Barrier] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._conditions: Dict[str, asyncio.Condition] = {}
        
        # Shared state management
        self._shared_states: Dict[str, SharedState] = {}
        self._state_locks: Dict[str, asyncio.Lock] = {}
        
        # Agent coordination
        self._agent_checkpoints: Dict[str, Set[str]] = defaultdict(set)
        self._agent_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._agent_status: Dict[str, str] = {}
        
        # Coordination configuration
        self.max_event_history = 1000
        self.event_propagation_delay = 0.01
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._running = False
        self._event_processor_task = None
    
    async def start(self):
        """Start the coordination manager."""
        if not self._running:
            self._running = True
            self._event_processor_task = asyncio.create_task(self._process_events())
            self.logger.info("Coordination manager started")
    
    async def stop(self):
        """Stop the coordination manager."""
        if self._running:
            self._running = False
            if self._event_processor_task:
                self._event_processor_task.cancel()
                try:
                    await self._event_processor_task
                except asyncio.CancelledError:
                    pass
            self.logger.info("Coordination manager stopped")
    
    async def create_barrier(self, barrier_id: str, parties: int) -> asyncio.Barrier:
        """
        Create a barrier for agent synchronization.
        
        Args:
            barrier_id: Unique barrier identifier
            parties: Number of agents that must reach the barrier
            
        Returns:
            Barrier instance
        """
        if barrier_id not in self._barriers:
            self._barriers[barrier_id] = asyncio.Barrier(parties)
            self.logger.debug(f"Created barrier '{barrier_id}' for {parties} parties")
        
        return self._barriers[barrier_id]
    
    async def wait_at_barrier(self, barrier_id: str, agent_id: str, timeout: float = None) -> int:
        """
        Wait at a barrier until all agents arrive.
        
        Args:
            barrier_id: Barrier identifier
            agent_id: Agent waiting at barrier
            timeout: Maximum wait time
            
        Returns:
            Index of this agent at the barrier
        """
        barrier = self._barriers.get(barrier_id)
        if not barrier:
            raise ValueError(f"Barrier '{barrier_id}' not found")
        
        try:
            # Record checkpoint
            self._agent_checkpoints[barrier_id].add(agent_id)
            
            # Emit barrier event
            await self.emit_event(CoordinationEvent(
                event_type=CoordinationEventType.BARRIER_REACHED,
                source_agent=agent_id,
                data={"barrier_id": barrier_id}
            ))
            
            # Wait at barrier
            if timeout:
                index = await asyncio.wait_for(barrier.wait(), timeout)
            else:
                index = await barrier.wait()
            
            self.logger.debug(f"Agent {agent_id} passed barrier '{barrier_id}' at index {index}")
            return index
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent_id} timed out at barrier '{barrier_id}'")
            raise
        except Exception as e:
            self.logger.error(f"Error at barrier '{barrier_id}': {e}")
            raise
    
    async def acquire_lock(self, lock_id: str, agent_id: str, timeout: float = None) -> asyncio.Lock:
        """
        Acquire a distributed lock.
        
        Args:
            lock_id: Lock identifier
            agent_id: Agent acquiring the lock
            timeout: Maximum wait time
            
        Returns:
            Lock instance
        """
        if lock_id not in self._locks:
            self._locks[lock_id] = asyncio.Lock()
        
        lock = self._locks[lock_id]
        
        try:
            if timeout:
                await asyncio.wait_for(lock.acquire(), timeout)
            else:
                await lock.acquire()
            
            self.logger.debug(f"Agent {agent_id} acquired lock '{lock_id}'")
            
            # Emit lock event
            await self.emit_event(CoordinationEvent(
                event_type=CoordinationEventType.RESOURCE_ACQUIRED,
                source_agent=agent_id,
                data={"resource_type": "lock", "resource_id": lock_id}
            ))
            
            return lock
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent_id} timed out acquiring lock '{lock_id}'")
            raise
    
    def release_lock(self, lock_id: str, agent_id: str):
        """Release a distributed lock."""
        lock = self._locks.get(lock_id)
        if lock and lock.locked():
            lock.release()
            self.logger.debug(f"Agent {agent_id} released lock '{lock_id}'")
            
            # Emit release event asynchronously
            asyncio.create_task(self.emit_event(CoordinationEvent(
                event_type=CoordinationEventType.RESOURCE_RELEASED,
                source_agent=agent_id,
                data={"resource_type": "lock", "resource_id": lock_id}
            )))
    
    async def create_shared_state(self, state_id: str, initial_data: Dict[str, Any] = None) -> SharedState:
        """
        Create a shared state container.
        
        Args:
            state_id: Unique state identifier
            initial_data: Initial state data
            
        Returns:
            SharedState instance
        """
        if state_id not in self._shared_states:
            state = SharedState(
                state_id=state_id,
                data=initial_data or {}
            )
            self._shared_states[state_id] = state
            self._state_locks[state_id] = asyncio.Lock()
            
            self.logger.debug(f"Created shared state '{state_id}'")
        
        return self._shared_states[state_id]
    
    async def read_shared_state(self, state_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Read shared state (non-blocking for readers).
        
        Args:
            state_id: State identifier
            agent_id: Agent reading the state
            
        Returns:
            Current state data
        """
        state = self._shared_states.get(state_id)
        if not state:
            raise ValueError(f"Shared state '{state_id}' not found")
        
        # Track reader
        state.readers.add(agent_id)
        
        # Return copy to prevent modifications
        return state.data.copy()
    
    async def update_shared_state(
        self,
        state_id: str,
        agent_id: str,
        updates: Dict[str, Any],
        merge: bool = True
    ) -> SharedState:
        """
        Update shared state with locking.
        
        Args:
            state_id: State identifier
            agent_id: Agent updating the state
            updates: Updates to apply
            merge: Whether to merge with existing data
            
        Returns:
            Updated SharedState
        """
        state = self._shared_states.get(state_id)
        if not state:
            raise ValueError(f"Shared state '{state_id}' not found")
        
        lock = self._state_locks[state_id]
        
        async with lock:
            # Check if already locked by another agent
            if state.locked_by and state.locked_by != agent_id:
                raise RuntimeError(f"State '{state_id}' is locked by {state.locked_by}")
            
            # Lock state
            state.locked_by = agent_id
            
            try:
                # Update state
                if merge:
                    state.data.update(updates)
                else:
                    state.data = updates
                
                state.version += 1
                state.last_modified = datetime.now()
                
                # Emit update event
                await self.emit_event(CoordinationEvent(
                    event_type=CoordinationEventType.DATA_AVAILABLE,
                    source_agent=agent_id,
                    data={
                        "state_id": state_id,
                        "version": state.version,
                        "updates": updates
                    }
                ))
                
                self.logger.debug(f"Agent {agent_id} updated shared state '{state_id}' to version {state.version}")
                
                return state
                
            finally:
                # Unlock state
                state.locked_by = None
    
    async def wait_for_state_change(
        self,
        state_id: str,
        agent_id: str,
        predicate: Callable[[Dict[str, Any]], bool],
        timeout: float = None
    ) -> Dict[str, Any]:
        """
        Wait for shared state to meet a condition.
        
        Args:
            state_id: State identifier
            agent_id: Agent waiting
            predicate: Condition function
            timeout: Maximum wait time
            
        Returns:
            State data when condition is met
        """
        state = self._shared_states.get(state_id)
        if not state:
            raise ValueError(f"Shared state '{state_id}' not found")
        
        # Create condition variable if needed
        condition_key = f"{state_id}_condition"
        if condition_key not in self._conditions:
            self._conditions[condition_key] = asyncio.Condition()
        
        condition = self._conditions[condition_key]
        
        async def check_condition():
            async with condition:
                while not predicate(state.data):
                    await condition.wait()
                return state.data.copy()
        
        try:
            if timeout:
                result = await asyncio.wait_for(check_condition(), timeout)
            else:
                result = await check_condition()
            
            self.logger.debug(f"Agent {agent_id} condition met for state '{state_id}'")
            return result
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent_id} timed out waiting for state '{state_id}'")
            raise
    
    async def emit_event(self, event: CoordinationEvent):
        """
        Emit a coordination event.
        
        Args:
            event: Event to emit
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self.max_event_history:
            self._event_history.pop(0)
        
        # Queue for processing
        await self._pending_events.put(event)
    
    def subscribe_to_event(
        self,
        event_type: CoordinationEventType,
        handler: Callable[[CoordinationEvent], Awaitable[None]]
    ):
        """
        Subscribe to coordination events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Async event handler function
        """
        self._event_bus[event_type.value].append(handler)
        self.logger.debug(f"Subscribed handler to {event_type.value} events")
    
    async def _process_events(self):
        """Process coordination events asynchronously."""
        while self._running:
            try:
                # Get next event with timeout
                event = await asyncio.wait_for(
                    self._pending_events.get(),
                    timeout=1.0
                )
                
                # Small delay for event propagation
                await asyncio.sleep(self.event_propagation_delay)
                
                # Notify all handlers
                handlers = self._event_bus.get(event.event_type.value, [])
                
                if handlers:
                    # Execute handlers concurrently
                    await asyncio.gather(
                        *[handler(event) for handler in handlers],
                        return_exceptions=True
                    )
                
                # Notify state condition waiters if data event
                if event.event_type == CoordinationEventType.DATA_AVAILABLE:
                    state_id = event.data.get("state_id")
                    if state_id:
                        condition_key = f"{state_id}_condition"
                        condition = self._conditions.get(condition_key)
                        if condition:
                            async with condition:
                                condition.notify_all()
                
            except asyncio.TimeoutError:
                # No events to process
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def register_agent(self, agent_id: str, dependencies: List[str] = None):
        """
        Register an agent with the coordination manager.
        
        Args:
            agent_id: Agent identifier
            dependencies: List of agents this agent depends on
        """
        self._agent_status[agent_id] = "registered"
        
        if dependencies:
            self._agent_dependencies[agent_id] = set(dependencies)
        
        self.logger.info(f"Registered agent {agent_id} with {len(dependencies or [])} dependencies")
    
    async def update_agent_status(self, agent_id: str, status: str):
        """Update agent status."""
        old_status = self._agent_status.get(agent_id, "unknown")
        self._agent_status[agent_id] = status
        
        # Emit status change event
        await self.emit_event(CoordinationEvent(
            event_type=CoordinationEventType.WORKFLOW_EVENT,
            source_agent=agent_id,
            data={
                "status_change": {
                    "from": old_status,
                    "to": status
                }
            }
        ))
    
    async def wait_for_dependencies(self, agent_id: str, timeout: float = None) -> bool:
        """
        Wait for all agent dependencies to complete.
        
        Args:
            agent_id: Agent waiting for dependencies
            timeout: Maximum wait time
            
        Returns:
            True if all dependencies completed
        """
        dependencies = self._agent_dependencies.get(agent_id, set())
        if not dependencies:
            return True
        
        async def check_dependencies():
            while True:
                completed = all(
                    self._agent_status.get(dep_id) == "completed"
                    for dep_id in dependencies
                )
                if completed:
                    return True
                await asyncio.sleep(0.1)
        
        try:
            if timeout:
                result = await asyncio.wait_for(check_dependencies(), timeout)
            else:
                result = await check_dependencies()
            
            self.logger.debug(f"All dependencies satisfied for agent {agent_id}")
            return result
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent_id} timed out waiting for dependencies")
            return False
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination statistics."""
        return {
            "total_events": len(self._event_history),
            "active_barriers": len(self._barriers),
            "active_locks": sum(1 for lock in self._locks.values() if lock.locked()),
            "shared_states": len(self._shared_states),
            "registered_agents": len(self._agent_status),
            "agent_status": dict(self._agent_status),
            "event_types": {
                event_type.value: sum(
                    1 for e in self._event_history 
                    if e.event_type == event_type
                )
                for event_type in CoordinationEventType
            }
        }
    
    async def cleanup(self):
        """Cleanup coordination resources."""
        # Stop event processing
        await self.stop()
        
        # Clear all resources
        self._barriers.clear()
        self._locks.clear()
        self._semaphores.clear()
        self._conditions.clear()
        self._shared_states.clear()
        self._state_locks.clear()
        self._agent_checkpoints.clear()
        self._agent_dependencies.clear()
        self._agent_status.clear()
        self._event_history.clear()
        
        self.logger.info("Coordination manager cleaned up")