"""
Reasoning-Enhanced Agent Base Class.

Extends MemoryAwareAgent with LLM-powered reasoning capabilities,
enabling agents to make intelligent decisions and adapt strategies dynamically.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .memory_agent import MemoryAwareAgent
from .base import Task, Result
from .llm_reasoning import LLMReasoningEngine, ReasoningContext, ReasoningType, ReasoningResult

logger = logging.getLogger(__name__)


class ReasoningAgent(MemoryAwareAgent):
    """
    Base class for agents with LLM-powered reasoning capabilities.
    
    Combines memory-based learning with intelligent LLM reasoning to enable
    sophisticated decision-making and adaptive behavior.
    """
    
    def __init__(self, agent_id: str = None, memory_config: Dict[str, Any] = None, 
                 reasoning_config: Dict[str, Any] = None):
        """
        Initialize reasoning-enhanced agent.
        
        Args:
            agent_id: Unique agent identifier
            memory_config: Memory system configuration
            reasoning_config: LLM reasoning configuration
        """
        super().__init__(agent_id, memory_config)
        
        # Initialize reasoning engine
        self.reasoning_engine = LLMReasoningEngine(llm_config=reasoning_config)
        
        # Reasoning configuration
        reasoning_config = reasoning_config or {}
        self.enable_reasoning = reasoning_config.get("enable_reasoning", True)
        self.default_reasoning_type = ReasoningType(reasoning_config.get("default_reasoning_type", "tactical"))
        self.reasoning_threshold = reasoning_config.get("reasoning_threshold", 0.5)
        self.max_reasoning_time = reasoning_config.get("max_reasoning_time", 30.0)
        
        # Enhanced reasoning performance tracking
        self.reasoning_stats = {
            "total_reasonings": 0,
            "successful_reasonings": 0,
            "failed_reasonings": 0,
            "reasoning_time_saved": 0.0,
            "decisions_improved": 0,
            "total_reasoning_time": 0.0,
            "average_reasoning_time": 0.0,
            "memory_hits": 0,
            "memory_misses": 0
        }
        
        self.logger = logging.getLogger(f"{__name__}.{self.agent_id}")
        self.logger.info(f"Initialized reasoning agent: {self.agent_id} with reasoning engine")
    
    def _validate_task(self, task: Task) -> bool:
        """Validate task before execution with comprehensive checks."""
        if not task:
            self.logger.error("Task is None")
            return False
            
        if not hasattr(task, 'task_id') or not task.task_id:
            self.logger.error("Task missing task_id")
            return False
            
        if not hasattr(task, 'task_type') or not task.task_type:
            self.logger.error(f"Task {task.task_id} missing task_type")
            return False
            
        # Validate task parameters if present
        if hasattr(task, 'parameters') and task.parameters:
            if not isinstance(task.parameters, dict):
                self.logger.error(f"Task {task.task_id} has invalid parameters type: {type(task.parameters)}")
                return False
                
        # Check if agent can handle this task type
        if hasattr(self, 'supported_task_types') and self.supported_task_types:
            if task.task_type not in self.supported_task_types:
                self.logger.warning(f"Task type {task.task_type} not in supported types: {self.supported_task_types}")
                # Don't fail validation, just warn
        
        return True
    
    async def execute(self, task: Task) -> Result:
        """
        Execute task with reasoning-enhanced decision-making and comprehensive metrics.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result with reasoning enhancements and performance data
        """
        start_time = time.time()
        execution_metrics = {
            "agent_id": self.agent_id,
            "task_id": task.task_id,
            "task_type": task.task_type,
            "start_time": start_time,
            "reasoning_enabled": self.enable_reasoning
        }
        
        try:
            # Validate task before processing
            if not self._validate_task(task):
                return Result(
                    success=False,
                    error=f"Invalid task: {task.task_id}",
                    task_id=task.task_id,
                    execution_time=time.time() - start_time,
                    metadata={"execution_metrics": execution_metrics}
                )
            
            # Get memory context with timing
            memory_start = time.time()
            memory_context = await self.memory.get_relevant_context(
                task, 
                max_results=self.max_context_memories
            )
            execution_metrics["memory_retrieval_time"] = time.time() - memory_start
            execution_metrics["memory_entries_found"] = len(memory_context.get("relevant_executions", []))
            
            # Determine if reasoning is needed with timing
            decision_start = time.time()
            should_reason = await self._should_apply_reasoning(task, memory_context)
            execution_metrics["reasoning_decision_time"] = time.time() - decision_start
            execution_metrics["reasoning_applied"] = should_reason and self.enable_reasoning
            
            if should_reason and self.enable_reasoning:
                # Execute with reasoning
                self.logger.debug(f"Applying reasoning to task {task.task_id} (type: {task.task_type})")
                result = await self._execute_with_reasoning(task, memory_context, start_time, execution_metrics)
            else:
                # Execute with memory only (fallback to parent class)
                self.logger.debug(f"Executing task {task.task_id} without reasoning")
                result = await self._execute_with_memory(task, memory_context)
                execution_metrics["execution_path"] = "memory_only"
            
            # Store execution in memory with error handling
            if self.enable_learning:
                try:
                    storage_start = time.time()
                    await self.memory.store_task_execution(task, result, memory_context)
                    execution_metrics["memory_storage_time"] = time.time() - storage_start
                    
                    # Learn from reasoning outcomes
                    if should_reason and self.enable_reasoning:
                        learning_start = time.time()
                        await self._learn_from_reasoning(task, result, memory_context)
                        execution_metrics["learning_time"] = time.time() - learning_start
                except Exception as learning_error:
                    self.logger.warning(f"Memory storage/learning failed for task {task.task_id}: {learning_error}")
                    execution_metrics["learning_error"] = str(learning_error)
            
            # Update execution time and add metrics
            total_time = time.time() - start_time
            result.execution_time = total_time
            execution_metrics["total_execution_time"] = total_time
            
            # Add execution metrics to result metadata
            if not result.metadata:
                result.metadata = {}
            result.metadata["execution_metrics"] = execution_metrics
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = self._create_result(
                success=False,
                error=f"Reasoning-enhanced execution failed: {str(e)}",
                task=task,
                execution_time=time.time() - start_time
            )
            
            if self.enable_learning:
                await self.memory.store_task_execution(task, error_result)
            
            return error_result
    
    async def _should_apply_reasoning(self, task: Task, memory_context: Dict[str, Any]) -> bool:
        """
        Determine if LLM reasoning should be applied to this task.
        
        Args:
            task: Current task
            memory_context: Available memory context
            
        Returns:
            True if reasoning should be applied
        """
        # Always reason for complex tasks
        if len(task.parameters) >= 5:
            return True
        
        # Reason if we have previous failures to learn from
        relevant_executions = memory_context.get("relevant_executions", [])
        failure_count = sum(1 for exec_info in relevant_executions if not exec_info.get("success"))
        
        if failure_count > 0:
            return True
        
        # Reason if we have enough memory context to make it valuable
        pattern_count = len(memory_context.get("learned_patterns", []))
        procedure_count = len(memory_context.get("procedures", []))
        
        if pattern_count >= 2 or procedure_count >= 1:
            return True
        
        # Reason if task performance is below threshold
        if relevant_executions:
            avg_execution_time = sum(exec_info.get("execution_time", 0) for exec_info in relevant_executions) / len(relevant_executions)
            if avg_execution_time > self.reasoning_threshold:
                return True
        
        # Default: use reasoning for new or uncommon tasks
        return len(relevant_executions) < 3
    
    async def _execute_with_reasoning(self, task: Task, memory_context: Dict[str, Any], start_time: float) -> Result:
        """
        Execute task with LLM reasoning enhancement.
        
        Args:
            task: Task to execute
            memory_context: Memory context
            start_time: Execution start time
            
        Returns:
            Result with reasoning enhancements
        """
        try:
            # Determine reasoning type
            reasoning_type = await self._determine_reasoning_type(task, memory_context)
            
            # Create reasoning context
            reasoning_context = ReasoningContext(
                agent_id=self.agent_id,
                task=task,
                memory_context=memory_context,
                reasoning_type=reasoning_type,
                constraints=await self._get_task_constraints(task),
                goals=await self._get_task_goals(task),
                previous_reasoning=await self._get_previous_reasoning(task)
            )
            
            # Perform LLM reasoning
            reasoning_result = await self.reasoning_engine.reason(reasoning_context)
            
            # Update reasoning stats
            self.reasoning_stats["total_reasonings"] += 1
            if reasoning_result.success:
                self.reasoning_stats["successful_reasonings"] += 1
            
            # Apply reasoning decisions to task
            if reasoning_result.success:
                enhanced_task = await self._apply_reasoning_decisions(task, reasoning_result)
            else:
                # Fallback to original task if reasoning fails
                enhanced_task = task
                self.logger.warning(f"Reasoning failed, using original task: {reasoning_result.error}")
            
            # Execute with enhanced task
            result = await self._execute_with_memory(enhanced_task, memory_context)
            
            # Enhance result with reasoning information
            if reasoning_result.success:
                result = await self._enhance_result_with_reasoning(result, reasoning_result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Reasoning-enhanced execution failed: {e}")
            
            # Fallback to memory-only execution
            return await self._execute_with_memory(task, memory_context)
    
    async def _determine_reasoning_type(self, task: Task, memory_context: Dict[str, Any]) -> ReasoningType:
        """Determine the most appropriate reasoning type for the task."""
        
        # Use reasoning engine's suggestion capability
        suggested_type = await self.reasoning_engine.suggest_reasoning_type(task, memory_context)
        
        # Override with agent-specific logic if needed
        return await self._customize_reasoning_type(suggested_type, task, memory_context)
    
    async def _customize_reasoning_type(self, suggested_type: ReasoningType, task: Task, memory_context: Dict[str, Any]) -> ReasoningType:
        """
        Customize reasoning type based on agent-specific needs.
        Override in subclasses for specialized behavior.
        """
        return suggested_type
    
    async def _get_task_constraints(self, task: Task) -> Dict[str, Any]:
        """
        Get constraints for the task.
        Override in subclasses for task-specific constraints.
        """
        return {
            "max_execution_time": self.max_reasoning_time,
            "memory_limit": "1GB",
            "quality_threshold": 0.8
        }
    
    async def _get_task_goals(self, task: Task) -> List[str]:
        """
        Get goals for the task.
        Override in subclasses for task-specific goals.
        """
        return [
            "Complete task successfully",
            "Optimize performance based on memory",
            "Learn patterns for future improvement",
            "Maintain high quality output"
        ]
    
    async def _get_previous_reasoning(self, task: Task) -> List[Dict]:
        """Get previous reasoning for similar tasks."""
        # Query memory for previous reasoning results
        # This would be implemented with memory system integration
        return []
    
    async def _apply_reasoning_decisions(self, task: Task, reasoning_result: ReasoningResult) -> Task:
        """
        Apply reasoning decisions to enhance the task.
        
        Args:
            task: Original task
            reasoning_result: LLM reasoning result
            
        Returns:
            Enhanced task with reasoning-based modifications
        """
        # Create enhanced task with reasoning decisions
        enhanced_parameters = task.parameters.copy()
        enhanced_context = (task.context or {}).copy()
        
        # Apply parameter adjustments from reasoning
        decision = reasoning_result.decision
        
        if "parameter_adjustments" in decision:
            enhanced_parameters.update(decision["parameter_adjustments"])
        
        # Add reasoning context
        enhanced_context["reasoning"] = {
            "type": reasoning_result.reasoning_chain[0].get("step", "unknown") if reasoning_result.reasoning_chain else "unknown",
            "confidence": reasoning_result.confidence,
            "explanation": reasoning_result.explanation[:200] + "..." if len(reasoning_result.explanation) > 200 else reasoning_result.explanation,
            "decisions_applied": list(decision.keys())
        }
        
        # Create enhanced task
        enhanced_task = Task(
            task_id=task.task_id,
            task_type=task.task_type,
            parameters=enhanced_parameters,
            context=enhanced_context,
            priority=task.priority,
            metadata=task.metadata
        )
        
        self.logger.debug(f"Applied reasoning decisions: {list(decision.keys())}")
        
        return enhanced_task
    
    async def _enhance_result_with_reasoning(self, result: Result, reasoning_result: ReasoningResult) -> Result:
        """Enhance execution result with reasoning information."""
        
        if not result.metadata:
            result.metadata = {}
        
        # Add reasoning metadata
        result.metadata["reasoning"] = {
            "applied": True,
            "type": reasoning_result.reasoning_chain[0].get("step", "unknown") if reasoning_result.reasoning_chain else "unknown",
            "confidence": reasoning_result.confidence,
            "execution_time": reasoning_result.execution_time,
            "chain_length": len(reasoning_result.reasoning_chain),
            "alternatives_considered": len(reasoning_result.alternatives_considered)
        }
        
        # Add reasoning explanation to result data if successful
        if result.success and result.data:
            result.data["reasoning_applied"] = {
                "explanation": reasoning_result.explanation[:500] + "..." if len(reasoning_result.explanation) > 500 else reasoning_result.explanation,
                "confidence": reasoning_result.confidence,
                "decision_quality": "high" if reasoning_result.confidence > 0.8 else "medium" if reasoning_result.confidence > 0.5 else "low"
            }
        
        return result
    
    async def _learn_from_reasoning(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """Learn from reasoning outcomes to improve future decisions."""
        
        reasoning_metadata = result.metadata.get("reasoning", {}) if result.metadata else {}
        
        if reasoning_metadata.get("applied"):
            confidence = reasoning_metadata.get("confidence", 0.0)
            
            # Store reasoning pattern if successful
            if result.success and confidence > 0.7:
                await self.memory.store_learned_pattern(
                    pattern_type=f"{task.task_type}_successful_reasoning",
                    pattern_data={
                        "reasoning_type": reasoning_metadata.get("type"),
                        "confidence": confidence,
                        "execution_time": result.execution_time,
                        "quality_indicators": self._extract_quality_indicators(result),
                        "task_complexity": len(task.parameters)
                    },
                    importance=0.8
                )
                
                self.reasoning_stats["decisions_improved"] += 1
            
            # Store reasoning procedure if very successful
            if result.success and confidence > 0.8 and not result.warnings:
                await self.memory.store_procedure(
                    procedure_name=f"{task.task_type}_reasoning_procedure",
                    procedure_steps=[
                        {"step": "analyze_context", "type": reasoning_metadata.get("type")},
                        {"step": "apply_reasoning", "confidence_threshold": confidence},
                        {"step": "execute_enhanced", "expected_improvement": "high"}
                    ],
                    success_rate=0.9
                )
    
    def _extract_quality_indicators(self, result: Result) -> Dict[str, Any]:
        """Extract quality indicators from execution result."""
        indicators = {
            "success": result.success,
            "execution_time": result.execution_time,
            "has_warnings": bool(result.warnings),
            "data_completeness": 1.0 if result.data else 0.0
        }
        
        # Add task-specific quality indicators
        if result.data:
            if "total_processed" in result.data:
                indicators["processing_volume"] = result.data["total_processed"]
            if "quality_score" in result.data:
                indicators["quality_score"] = result.data["quality_score"]
        
        return indicators
    
    async def get_reasoning_summary(self) -> Dict[str, Any]:
        """Get summary of reasoning performance and capabilities."""
        
        # Get base memory summary
        memory_summary = await self.get_memory_summary()
        
        # Add reasoning-specific information
        reasoning_engine_stats = self.reasoning_engine.get_reasoning_stats()
        
        return {
            **memory_summary,
            "reasoning_enabled": self.enable_reasoning,
            "reasoning_stats": self.reasoning_stats,
            "reasoning_engine_stats": reasoning_engine_stats,
            "reasoning_config": {
                "default_type": self.default_reasoning_type.value,
                "threshold": self.reasoning_threshold,
                "max_time": self.max_reasoning_time
            }
        }
    
    async def suggest_reasoning_improvements(self) -> List[str]:
        """Suggest improvements to reasoning configuration."""
        suggestions = []
        
        stats = self.reasoning_stats
        total_reasonings = stats["total_reasonings"]
        
        if total_reasonings == 0:
            suggestions.append("No reasoning performed yet - consider enabling reasoning for complex tasks")
            return suggestions
        
        success_rate = stats["successful_reasonings"] / total_reasonings
        
        if success_rate < 0.7:
            suggestions.append("Low reasoning success rate - consider adjusting reasoning threshold or templates")
        
        if stats["decisions_improved"] / total_reasonings < 0.3:
            suggestions.append("Low decision improvement rate - reasoning may not be adding sufficient value")
        
        engine_stats = self.reasoning_engine.get_reasoning_stats()
        if engine_stats["avg_reasoning_time"] > self.max_reasoning_time * 0.8:
            suggestions.append("High reasoning time - consider optimizing templates or reducing complexity")
        
        if not suggestions:
            suggestions.append("Reasoning performance is good - consider expanding reasoning to more task types")
        
        return suggestions
    
    async def enable_reasoning_for_task_type(self, task_type: str, reasoning_type: ReasoningType = None) -> None:
        """Enable reasoning for specific task type."""
        # This would be implemented with more sophisticated configuration
        self.logger.info(f"Enabled reasoning for task type: {task_type}")
    
    async def create_custom_reasoning_template(self, task_type: str, template: str) -> None:
        """Create custom reasoning template for task type."""
        template_name = f"custom_{task_type}_{self.agent_id}"
        await self.reasoning_engine.create_custom_reasoning_template(template_name, template)
        self.logger.info(f"Created custom reasoning template for {task_type}")
    
    # Abstract methods that subclasses should implement
    async def _execute_with_memory(self, task: Task, memory_context: Dict[str, Any]) -> Result:
        """
        Execute task with memory context (from parent class).
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _execute_with_memory")
    
    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_capabilities")
    
    def can_handle(self, task_type: str) -> bool:
        """
        Check if agent can handle task type.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement can_handle")