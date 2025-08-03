"""
Unit tests for orchestration base classes.
"""

import pytest
from datetime import datetime
from src.orchestration.base import Task, Result, TaskPriority, BaseAgent


class TestTask:
    """Test Task dataclass."""
    
    def test_task_creation_minimal(self):
        """Test creating task with minimal parameters."""
        task = Task(task_type="test_task")
        
        assert task.task_type == "test_task"
        assert task.parameters == {}
        assert task.context == {}
        assert task.timeout == 300
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_id is None
        assert task.parent_task_id is None
        assert task.metadata == {}
    
    def test_task_creation_full(self):
        """Test creating task with all parameters."""
        task = Task(
            task_type="test_task",
            parameters={"param1": "value1"},
            context={"key": "value"},
            timeout=600,
            priority=TaskPriority.HIGH,
            task_id="task_123",
            parent_task_id="parent_123",
            metadata={"meta": "data"}
        )
        
        assert task.task_type == "test_task"
        assert task.parameters == {"param1": "value1"}
        assert task.context == {"key": "value"}
        assert task.timeout == 600
        assert task.priority == TaskPriority.HIGH
        assert task.task_id == "task_123"
        assert task.parent_task_id == "parent_123"
        assert task.metadata == {"meta": "data"}


class TestResult:
    """Test Result dataclass."""
    
    def test_result_creation_success(self):
        """Test creating successful result."""
        result = Result(success=True, data={"key": "value"})
        
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.warnings == []
        assert result.execution_time == 0.0
        assert isinstance(result.timestamp, datetime)
        assert result.agent_id is None
        assert result.task_id is None
    
    def test_result_creation_failure(self):
        """Test creating failure result."""
        result = Result(
            success=False,
            error="Something went wrong",
            warnings=["Warning 1", "Warning 2"],
            execution_time=1.5
        )
        
        assert result.success is False
        assert result.data is None
        assert result.error == "Something went wrong"
        assert result.warnings == ["Warning 1", "Warning 2"]
        assert result.execution_time == 1.5


class TestBaseAgent:
    """Test BaseAgent implementation."""
    
    class ConcreteAgent(BaseAgent):
        """Concrete implementation for testing."""
        
        def get_capabilities(self):
            return ["capability1", "capability2"]
        
        def can_handle(self, task_type: str) -> bool:
            return task_type in self.get_capabilities()
        
        async def execute(self, task: Task) -> Result:
            return self._create_result(
                success=True,
                data={"executed": task.task_type},
                task=task
            )
    
    def test_base_agent_creation(self):
        """Test creating base agent."""
        agent = self.ConcreteAgent("test_agent")
        
        assert agent.agent_id == "test_agent"
        assert agent.agent_type == "ConcreteAgent"
        assert not agent._initialized
    
    def test_base_agent_auto_id(self):
        """Test agent with auto-generated ID."""
        agent = self.ConcreteAgent()
        
        # Should have auto-generated ID
        assert agent.agent_id.startswith("ConcreteAgent_")
        assert "_" in agent.agent_id
    
    def test_base_agent_capabilities(self):
        """Test agent capabilities."""
        agent = self.ConcreteAgent()
        
        capabilities = agent.get_capabilities()
        assert capabilities == ["capability1", "capability2"]
        
        assert agent.can_handle("capability1") is True
        assert agent.can_handle("capability2") is True
        assert agent.can_handle("unknown") is False
    
    def test_base_agent_create_result(self):
        """Test result creation helper."""
        agent = self.ConcreteAgent()
        task = Task(task_type="capability1", task_id="test_123")
        
        result = agent._create_result(
            success=True,
            data={"executed": "capability1"},
            task=task,
            execution_time=1.5
        )
        
        assert result.success is True
        assert result.data == {"executed": "capability1"}
        assert result.agent_id == agent.agent_id
        assert result.task_id == "test_123"
        assert result.execution_time == 1.5
        assert result.metadata["agent_type"] == "ConcreteAgent"
        assert result.metadata["task_type"] == "capability1"
    
    def test_base_agent_status(self):
        """Test agent status."""
        agent = self.ConcreteAgent("test_agent")
        
        status = agent.get_status()
        
        assert status["agent_id"] == "test_agent"
        assert status["agent_type"] == "ConcreteAgent"
        assert status["capabilities"] == ["capability1", "capability2"]
        assert status["status"] == "ready"


class TestTaskPriority:
    """Test TaskPriority enum."""
    
    def test_priority_values(self):
        """Test priority enum values."""
        assert TaskPriority.CRITICAL.value == 0
        assert TaskPriority.HIGH.value == 1
        assert TaskPriority.MEDIUM.value == 2
        assert TaskPriority.LOW.value == 3
    
    def test_priority_comparison(self):
        """Test priority comparison."""
        # Lower value = higher priority
        assert TaskPriority.CRITICAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.MEDIUM.value
        assert TaskPriority.MEDIUM.value < TaskPriority.LOW.value