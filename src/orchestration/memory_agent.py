"""
Memory-Aware Agent Base Class.

Extends BaseAgent with persistent memory capabilities, enabling agents to learn
from previous executions and maintain context across tasks.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseAgent, Task, Result
from .memory import AgentMemory, MemoryType, MemoryQuery

logger = logging.getLogger(__name__)


class MemoryAwareAgent(BaseAgent):
    """
    Base class for agents with memory capabilities.
    
    Provides persistent memory for learning from previous executions,
    storing successful strategies, and maintaining context awareness.
    """
    
    def __init__(self, agent_id: str = None, memory_config: Dict[str, Any] = None):
        """
        Initialize memory-aware agent.
        
        Args:
            agent_id: Unique agent identifier
            memory_config: Memory system configuration
        """
        super().__init__(agent_id)
        
        # Initialize memory system
        memory_config = memory_config or {}
        self.memory = AgentMemory(
            agent_id=self.agent_id,
            db_path=memory_config.get("db_path")
        )
        
        # Memory configuration
        self.max_context_memories = memory_config.get("max_context_memories", 5)
        self.memory_importance_threshold = memory_config.get("importance_threshold", 0.3)
        self.enable_learning = memory_config.get("enable_learning", True)
        
        self.logger = logging.getLogger(f"{__name__}.{self.agent_id}")
        self.logger.info(f"Initialized memory-aware agent: {self.agent_id}")
    
    async def execute(self, task: Task) -> Result:
        """
        Execute task with memory-enhanced context.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        start_time = time.time()
        
        try:
            # Get relevant memory context
            memory_context = await self.memory.get_relevant_context(
                task, 
                max_results=self.max_context_memories
            )
            
            # Update working memory with current task
            await self.memory.update_working_memory({
                "current_task": task.task_type,
                "current_parameters": task.parameters,
                "execution_start": datetime.now().isoformat()
            })
            
            # Execute with memory context
            result = await self._execute_with_memory(task, memory_context)
            
            # Store execution in memory
            if self.enable_learning:
                await self.memory.store_task_execution(task, result, memory_context)
                
                # Learn from execution
                await self._learn_from_execution(task, result, memory_context)
            
            # Update execution time
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            # Create error result and store it for learning
            error_result = self._create_result(
                success=False,
                error=f"Memory-aware execution failed: {str(e)}",
                task=task,
                execution_time=time.time() - start_time
            )
            
            if self.enable_learning:
                await self.memory.store_task_execution(task, error_result)
            
            return error_result
    
    async def _execute_with_memory(self, task: Task, memory_context: Dict[str, Any]) -> Result:
        """
        Execute task with memory context (to be implemented by subclasses).
        
        Args:
            task: Task to execute
            memory_context: Relevant memory context
            
        Returns:
            Task execution result
        """
        # Default implementation calls the original execute method
        # Subclasses should override this to use memory context
        return await self._execute_without_memory(task)
    
    async def _execute_without_memory(self, task: Task) -> Result:
        """
        Fallback execution without memory (placeholder for subclasses).
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        # This should be overridden by subclasses
        return self._create_result(
            success=False,
            error="Memory-aware execution not implemented",
            task=task
        )
    
    async def _learn_from_execution(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """
        Learn patterns from task execution.
        
        Args:
            task: Executed task
            result: Execution result
            memory_context: Memory context used
        """
        try:
            # Learn from successful executions
            if result.success:
                await self._learn_success_patterns(task, result, memory_context)
            else:
                await self._learn_failure_patterns(task, result, memory_context)
            
            # Learn general patterns
            await self._learn_execution_patterns(task, result, memory_context)
            
        except Exception as e:
            self.logger.warning(f"Failed to learn from execution: {e}")
    
    async def _learn_success_patterns(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """Learn patterns from successful executions."""
        # Check if this was a repeated successful pattern
        similar_successes = [
            exec_mem for exec_mem in memory_context.get("relevant_executions", [])
            if exec_mem.get("task_type") == task.task_type and exec_mem.get("success")
        ]
        
        if len(similar_successes) >= 2:
            # This is a proven successful strategy
            await self.memory.store_procedure(
                procedure_name=f"{task.task_type}_successful_strategy",
                procedure_steps=[
                    {"step": "prepare_parameters", "parameters": task.parameters},
                    {"step": "execute_task", "task_type": task.task_type},
                    {"step": "validate_result", "expected_success": True}
                ],
                success_rate=min(0.9, len(similar_successes) / (len(similar_successes) + 1))
            )
        
        # Learn parameter patterns
        if task.parameters:
            await self.memory.store_learned_pattern(
                pattern_type=f"{task.task_type}_successful_parameters",
                pattern_data={
                    "parameters": task.parameters,
                    "execution_time": result.execution_time,
                    "confidence": 0.7 if result.execution_time < 5.0 else 0.5
                },
                importance=0.6
            )
    
    async def _learn_failure_patterns(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """Learn patterns from failed executions."""
        # Store failure pattern for avoidance
        await self.memory.store_learned_pattern(
            pattern_type=f"{task.task_type}_failure_pattern",
            pattern_data={
                "parameters": task.parameters,
                "error": result.error,
                "execution_time": result.execution_time,
                "context": memory_context.get("working_memory", {}),
                "confidence": 0.8
            },
            importance=0.8  # Failures are important to remember
        )
    
    async def _learn_execution_patterns(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """Learn general execution patterns."""
        # Learn timing patterns
        execution_times = [
            exec_mem.get("execution_time", 0) 
            for exec_mem in memory_context.get("relevant_executions", [])
            if exec_mem.get("task_type") == task.task_type
        ]
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            
            # If this execution was significantly different, store as pattern
            if abs(result.execution_time - avg_time) > avg_time * 0.5:
                await self.memory.store_learned_pattern(
                    pattern_type=f"{task.task_type}_timing_anomaly",
                    pattern_data={
                        "execution_time": result.execution_time,
                        "average_time": avg_time,
                        "parameters": task.parameters,
                        "success": result.success,
                        "confidence": 0.6
                    },
                    importance=0.5
                )
    
    async def get_learned_strategies(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get learned strategies for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            List of learned strategies
        """
        query = MemoryQuery(
            agent_id=self.agent_id,
            memory_types=[MemoryType.PROCEDURAL],
            content_keywords=[task_type],
            min_importance=0.5,
            max_results=5
        )
        
        memories = await self.memory.query_memories(query)
        
        strategies = []
        for memory in memories:
            if memory.content.get("procedure_name", "").startswith(task_type):
                strategies.append({
                    "name": memory.content.get("procedure_name"),
                    "steps": memory.content.get("steps", []),
                    "success_rate": memory.content.get("success_rate", 0.5),
                    "usage_count": memory.content.get("usage_count", 0),
                    "importance": memory.importance
                })
        
        return sorted(strategies, key=lambda x: x["success_rate"], reverse=True)
    
    async def get_parameter_recommendations(self, task_type: str) -> Dict[str, Any]:
        """
        Get parameter recommendations based on learned patterns.
        
        Args:
            task_type: Type of task
            
        Returns:
            Parameter recommendations
        """
        query = MemoryQuery(
            agent_id=self.agent_id,
            memory_types=[MemoryType.SEMANTIC],
            content_keywords=[task_type, "parameters"],
            min_importance=0.4,
            max_results=10
        )
        
        memories = await self.memory.query_memories(query)
        
        # Analyze successful parameter patterns
        successful_params = []
        failure_params = []
        
        for memory in memories:
            pattern_data = memory.content.get("pattern_data", {})
            if "successful_parameters" in memory.content.get("pattern_type", ""):
                successful_params.append(pattern_data)
            elif "failure_pattern" in memory.content.get("pattern_type", ""):
                failure_params.append(pattern_data)
        
        recommendations = {
            "recommended_parameters": {},
            "avoid_parameters": {},
            "confidence": 0.0
        }
        
        # Extract common successful parameters
        if successful_params:
            param_counts = {}
            for params in successful_params:
                for key, value in params.get("parameters", {}).items():
                    param_key = f"{key}={value}"
                    param_counts[param_key] = param_counts.get(param_key, 0) + 1
            
            # Recommend parameters that appear frequently in successes
            total_successful = len(successful_params)
            for param_key, count in param_counts.items():
                if count / total_successful >= 0.5:  # Appears in at least 50% of successes
                    key, value = param_key.split("=", 1)
                    recommendations["recommended_parameters"][key] = value
        
        # Extract parameters to avoid
        if failure_params:
            failure_param_counts = {}
            for params in failure_params:
                for key, value in params.get("parameters", {}).items():
                    param_key = f"{key}={value}"
                    failure_param_counts[param_key] = failure_param_counts.get(param_key, 0) + 1
            
            # Avoid parameters that appear frequently in failures
            total_failures = len(failure_params)
            for param_key, count in failure_param_counts.items():
                if count / total_failures >= 0.7:  # Appears in at least 70% of failures
                    key, value = param_key.split("=", 1)
                    recommendations["avoid_parameters"][key] = value
        
        # Calculate confidence
        total_memories = len(successful_params) + len(failure_params)
        if total_memories > 0:
            recommendations["confidence"] = min(1.0, total_memories / 10.0)
        
        return recommendations
    
    async def should_use_strategy(self, strategy_name: str, confidence_threshold: float = 0.7) -> bool:
        """
        Determine if a learned strategy should be used.
        
        Args:
            strategy_name: Name of the strategy
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            True if strategy should be used
        """
        query = MemoryQuery(
            agent_id=self.agent_id,
            memory_types=[MemoryType.PROCEDURAL],
            content_keywords=[strategy_name],
            max_results=1
        )
        
        memories = await self.memory.query_memories(query)
        
        if not memories:
            return False
        
        strategy = memories[0]
        success_rate = strategy.content.get("success_rate", 0.0)
        usage_count = strategy.content.get("usage_count", 0)
        
        # Use strategy if it has good success rate and has been used enough
        return success_rate >= confidence_threshold and usage_count >= 2
    
    async def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's memory state."""
        stats = await self.memory.get_memory_stats()
        
        # Get recent learning activity
        recent_patterns = await self.memory.query_memories(MemoryQuery(
            agent_id=self.agent_id,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            time_range=(datetime.now().replace(hour=0, minute=0, second=0), datetime.now()),
            max_results=5
        ))
        
        return {
            "agent_id": self.agent_id,
            "memory_stats": stats,
            "recent_learning": [
                {
                    "type": mem.memory_type.value,
                    "content_type": mem.content.get("pattern_type") or mem.content.get("procedure_name"),
                    "importance": mem.importance,
                    "timestamp": mem.timestamp.isoformat()
                }
                for mem in recent_patterns
            ],
            "learning_enabled": self.enable_learning
        }
    
    async def cleanup_memory(self, max_age_days: int = 30) -> int:
        """
        Clean up old memories.
        
        Args:
            max_age_days: Maximum age for memories to keep
            
        Returns:
            Number of memories cleaned up
        """
        return await self.memory.cleanup_old_memories(
            max_age_days=max_age_days,
            min_importance=self.memory_importance_threshold
        )