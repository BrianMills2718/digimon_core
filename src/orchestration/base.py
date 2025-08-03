"""
Base interfaces for agent orchestration.

These interfaces provide stable contracts that allow complete swapping of implementations
while maintaining compatibility. All orchestration components must implement these interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import time


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    """
    Standardized task representation for agent execution.
    
    This is a stable interface that all agents must accept.
    """
    task_type: str                              # Type of task (document_processing, entity_extraction, etc.)
    parameters: Dict[str, Any] = field(default_factory=dict)  # Task-specific parameters
    context: Dict[str, Any] = field(default_factory=dict)     # Shared context from previous steps
    timeout: int = 300                          # Execution timeout in seconds
    priority: TaskPriority = TaskPriority.MEDIUM  # Task priority
    task_id: Optional[str] = None               # Unique task identifier
    parent_task_id: Optional[str] = None        # Parent task for tracking
    metadata: Dict[str, Any] = field(default_factory=dict)     # Additional metadata


@dataclass
class Result:
    """
    Standardized result representation for agent execution.
    
    This is a stable interface that all agents must return.
    """
    success: bool                               # Execution success flag
    data: Any = None                           # Result data
    metadata: Dict[str, Any] = field(default_factory=dict)     # Execution metadata
    error: Optional[str] = None                # Error message if failed
    warnings: List[str] = field(default_factory=list)          # Non-fatal warnings
    execution_time: float = 0.0                # Execution time in seconds
    timestamp: datetime = field(default_factory=datetime.now)   # Result timestamp
    agent_id: Optional[str] = None             # Agent that produced this result
    task_id: Optional[str] = None              # Task that generated this result


class Agent(ABC):
    """
    Base agent interface - stable contract for all agents.
    
    This interface will remain stable even as we pivot to different
    agent implementations or frameworks.
    """
    
    @abstractmethod
    async def execute(self, task: Task) -> Result:
        """
        Execute a task and return result.
        
        Args:
            task: The task to execute
            
        Returns:
            Result of task execution
        """
        pass
    
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """
        Check if agent can handle specific task type.
        
        Args:
            task_type: Type of task to check
            
        Returns:
            True if agent can handle this task type
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of task types this agent can handle.
        
        Returns:
            List of supported task types
        """
        pass
    
    @property
    @abstractmethod
    def agent_id(self) -> str:
        """
        Unique identifier for this agent.
        
        Returns:
            Agent identifier string
        """
        pass
    
    @property
    def agent_type(self) -> str:
        """
        Type/category of this agent.
        
        Returns class name by default, but can be overridden.
        
        Returns:
            Agent type string
        """
        return getattr(self, '_agent_type', self.__class__.__name__)

    @agent_type.setter  
    def agent_type(self, value: str):
        """
        Set agent type override.
        
        Args:
            value: Agent type string (e.g., "document_processor")
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Agent type must be a non-empty string")
        self._agent_type = value.strip()
    
    async def initialize(self) -> bool:
        """
        Initialize the agent (optional override).
        
        Returns:
            True if initialization successful
        """
        return True
    
    async def cleanup(self) -> None:
        """
        Cleanup agent resources (optional override).
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status (optional override).
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.get_capabilities(),
            "status": "ready"
        }


class Orchestrator(ABC):
    """
    Base orchestrator interface - allows complete strategy swapping.
    
    This interface enables pivoting between different orchestration
    approaches (sequential, parallel, LLM-planned, external frameworks).
    """
    
    @abstractmethod
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Result:
        """
        Process user request and return comprehensive result.
        
        Args:
            request: User request string
            context: Optional context for request processing
            
        Returns:
            Result of request processing
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize orchestrator and all dependencies.
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status and health.
        
        Returns:
            Status dictionary with health information
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Cleanup orchestrator resources (optional override).
        """
        pass
    
    @property
    def orchestrator_type(self) -> str:
        """
        Type of orchestrator implementation.
        
        Returns:
            Orchestrator type string
        """
        return self.__class__.__name__
    
    def get_supported_workflows(self) -> List[str]:
        """
        Get list of supported workflow types (optional override).
        
        Returns:
            List of workflow names
        """
        return []
    
    async def validate_request(self, request: str) -> bool:
        """
        Validate if request can be processed (optional override).
        
        Args:
            request: Request to validate
            
        Returns:
            True if request is valid
        """
        return True


class BaseAgent(Agent):
    """
    Base implementation of Agent with common functionality.
    
    Concrete agents can inherit from this to get standard behavior.
    """
    
    def __init__(self, agent_id: str = None):
        """
        Initialize base agent.
        
        Args:
            agent_id: Optional agent identifier
        """
        self._agent_id = agent_id or f"{self.agent_type}_{int(time.time())}"
        self._initialized = False
    
    @property
    def agent_id(self) -> str:
        """Get agent identifier."""
        return self._agent_id
    
    async def initialize(self) -> bool:
        """Initialize agent."""
        self._initialized = True
        return True
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        self._initialized = False
    
    def _create_result(self, success: bool, data: Any = None, error: str = None,
                      execution_time: float = 0.0, task: Task = None) -> Result:
        """
        Helper to create standardized results.
        
        Args:
            success: Success flag
            data: Result data
            error: Error message
            execution_time: Execution time
            task: Original task
            
        Returns:
            Standardized Result object
        """
        return Result(
            success=success,
            data=data,
            error=error,
            execution_time=execution_time,
            agent_id=self.agent_id,
            task_id=task.task_id if task else None,
            metadata={
                "agent_type": self.agent_type,
                "task_type": task.task_type if task else None
            }
        )