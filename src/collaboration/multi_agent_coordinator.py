"""
Multi-Agent Coordinator for Collaborative Intelligence - Task C.6

Coordinates multiple specialized agents for complex document analysis tasks.
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random
import time

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Represents a specialized agent"""
    agent_id: str
    specialization: str
    capacity: int = 10
    current_load: int = 0
    performance_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents a task to be executed"""
    task_id: str
    task_type: str
    content: Any
    priority: int = 1
    estimated_effort: int = 1
    assigned_to: Optional[str] = None


@dataclass
class AgentResult:
    """Result from an agent execution"""
    agent_id: str
    task_id: str
    result: Any
    confidence: float
    execution_time: float
    status: str = "completed"


class MultiAgentCoordinator:
    """Coordinates multiple agents for collaborative intelligence"""
    
    def __init__(self):
        self.logger = logger
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[Task] = []
        self.results: List[AgentResult] = []
        self.performance_metrics: Dict[str, Dict] = defaultdict(dict)
        self.communication_protocol = "async_message_passing"
        self.failure_config = {"max_retries": 3, "fallback_strategy": "reassign"}
        self.learning_enabled = False
        self.learned_strategies: Dict[str, Dict] = {}
        self.monitoring_active = False
        
    async def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose complex task into subtasks"""
        self.logger.info(f"Decomposing task: {task.get('type')}")
        
        subtasks = []
        
        if task["type"] == "analyze_controversy":
            # Break down controversy analysis into subtasks
            subtasks.append({
                "type": "extract_claims",
                "documents": task["documents"],
                "parent_task": task["type"]
            })
            
            subtasks.append({
                "type": "identify_contradictions",
                "documents": task["documents"],
                "parent_task": task["type"]
            })
            
            subtasks.append({
                "type": "synthesize_viewpoints",
                "documents": task["documents"],
                "parent_task": task["type"]
            })
            
            # Add optional subtasks based on document count
            if len(task.get("documents", [])) > 2:
                subtasks.append({
                    "type": "build_consensus",
                    "documents": task["documents"],
                    "parent_task": task["type"]
                })
        
        else:
            # Generic decomposition
            subtasks.append({
                "type": "analyze",
                "content": task,
                "parent_task": "generic"
            })
        
        return subtasks
    
    async def execute_parallel(self, 
                              tasks: List[Dict[str, Any]], 
                              max_workers: int = 3) -> List[Dict[str, Any]]:
        """Execute tasks in parallel"""
        self.logger.info(f"Executing {len(tasks)} tasks in parallel with {max_workers} workers")
        
        results = []
        start_time = time.time()
        
        # Simulate parallel execution with asyncio
        async def execute_task(task):
            task_start = time.time()
            
            # Simulate task execution with varying times
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            return {
                "task_id": task.get("doc_id", task.get("type", "unknown")),
                "status": "completed",
                "result": f"Processed {task.get('type', 'task')}",
                "execution_time": time.time() - task_start
            }
        
        # Execute in parallel with limited concurrency
        semaphore = asyncio.Semaphore(max_workers)
        
        async def bounded_execute(task):
            async with semaphore:
                return await execute_task(task)
        
        results = await asyncio.gather(*[bounded_execute(task) for task in tasks])
        
        total_time = time.time() - start_time
        self.logger.info(f"Parallel execution completed in {total_time:.2f}s")
        
        return results
    
    async def aggregate_confidence(self, 
                                  agent_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate confidence scores from multiple agents"""
        self.logger.info(f"Aggregating confidence from {len(agent_scores)} agents")
        
        if not agent_scores:
            return {"overall_confidence": 0, "method": "none"}
        
        # Calculate weighted average
        total_confidence = 0
        contributions = {}
        
        for score in agent_scores:
            confidence = score["confidence"]
            agent = score["agent"]
            
            # Weight by confidence itself (higher confidence = more weight)
            weight = confidence
            total_confidence += confidence * weight
            contributions[agent] = confidence
        
        # Normalize
        total_weight = sum(score["confidence"] for score in agent_scores)
        overall = total_confidence / total_weight if total_weight > 0 else 0
        
        return {
            "overall_confidence": min(1.0, overall),
            "method": "weighted",
            "per_agent_contribution": contributions
        }
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.logger.info("Starting agent performance monitoring")
        self.monitoring_active = True
        self.performance_metrics = defaultdict(lambda: {
            "success_count": 0,
            "failure_count": 0,
            "total_time": 0,
            "task_count": 0
        })
    
    async def record_agent_execution(self,
                                    agent_id: str,
                                    task_type: str,
                                    execution_time: float,
                                    success: bool):
        """Record agent execution metrics"""
        if not self.monitoring_active:
            return
        
        metrics = self.performance_metrics[agent_id]
        
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1
        
        metrics["total_time"] += execution_time
        metrics["task_count"] += 1
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        agent_stats = {}
        
        for agent_id, metrics in self.performance_metrics.items():
            total_tasks = metrics["task_count"]
            
            if total_tasks > 0:
                agent_stats[agent_id] = {
                    "success_rate": metrics["success_count"] / total_tasks,
                    "avg_execution_time": metrics["total_time"] / total_tasks,
                    "task_count": total_tasks
                }
        
        return {"agent_stats": agent_stats}
    
    async def configure_failure_handling(self,
                                        max_retries: int,
                                        fallback_strategy: str):
        """Configure failure handling strategy"""
        self.failure_config = {
            "max_retries": max_retries,
            "fallback_strategy": fallback_strategy
        }
        self.logger.info(f"Configured failure handling: {self.failure_config}")
    
    async def execute_with_recovery(self,
                                   task: Dict[str, Any],
                                   agent_id: str,
                                   failure_probability: float = 0.0) -> Dict[str, Any]:
        """Execute task with failure recovery"""
        attempts = 0
        max_attempts = self.failure_config["max_retries"] + 1
        
        while attempts < max_attempts:
            attempts += 1
            
            # Simulate execution with possible failure
            if random.random() > failure_probability:
                # Success
                return {
                    "status": "completed",
                    "attempts": attempts,
                    "agent": agent_id,
                    "result": f"Task {task['id']} completed"
                }
            
            # Failure - try recovery
            if attempts < max_attempts:
                self.logger.info(f"Attempt {attempts} failed, retrying...")
                await asyncio.sleep(0.1 * attempts)  # Exponential backoff
        
        # All retries failed - use fallback
        if self.failure_config["fallback_strategy"] == "reassign":
            fallback_agent = f"fallback_agent_{random.randint(1, 3)}"
            return {
                "status": "completed_with_fallback",
                "attempts": attempts,
                "fallback_agent": fallback_agent,
                "result": f"Task {task['id']} completed by fallback"
            }
        
        return {
            "status": "failed",
            "attempts": attempts,
            "error": "Max retries exceeded"
        }
    
    async def create_hierarchy(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent hierarchy"""
        hierarchy = {}
        
        for role, details in config.items():
            if role == "supervisor":
                hierarchy["supervisor"] = {
                    "id": details["id"],
                    "subordinates": details["subordinates"]
                }
        
        self.logger.info(f"Created hierarchy with supervisor: {hierarchy['supervisor']['id']}")
        return hierarchy
    
    async def delegate_hierarchically(self,
                                     task: Dict[str, Any],
                                     hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task through hierarchy"""
        supervisor = hierarchy["supervisor"]
        
        # Supervisor analyzes and delegates
        subtask_assignments = []
        
        # Assign analysis tasks to analysts
        for subordinate in supervisor["subordinates"]:
            if subordinate["type"] == "data_analyst":
                subtask_assignments.append({
                    "agent_id": subordinate["id"],
                    "task_type": "data_analysis",
                    "priority": "high"
                })
        
        # Assign review task
        for subordinate in supervisor["subordinates"]:
            if subordinate["type"] == "quality_reviewer":
                subtask_assignments.append({
                    "agent_id": subordinate["id"],
                    "task_type": "quality_review",
                    "priority": "medium"
                })
        
        return {
            "delegated_to": supervisor["id"],
            "subtask_assignments": subtask_assignments
        }
    
    async def setup_communication(self,
                                 protocol: str,
                                 max_message_size: int):
        """Set up agent communication"""
        self.communication_protocol = protocol
        self.max_message_size = max_message_size
        self.logger.info(f"Communication setup: {protocol}, max size: {max_message_size}")
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message between agents"""
        start_time = time.time()
        
        # Simulate message delivery
        await asyncio.sleep(0.01)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "status": "delivered",
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat()
        }
    
    async def broadcast(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast message to all agents"""
        # Simulate broadcast to multiple agents
        agent_count = len(self.agents) if self.agents else 3
        
        return {
            "status": "broadcast_complete",
            "delivered_to_count": agent_count,
            "timestamp": datetime.now().isoformat()
        }
    
    async def enable_collaborative_learning(self):
        """Enable collaborative learning between agents"""
        self.learning_enabled = True
        self.learned_strategies = {}
        self.logger.info("Collaborative learning enabled")
    
    async def record_success(self,
                            agent_id: str,
                            task_type: str,
                            strategy: str,
                            performance_gain: float):
        """Record successful strategy"""
        if not self.learning_enabled:
            return
        
        key = f"{task_type}_{strategy}"
        self.learned_strategies[key] = {
            "agent_id": agent_id,
            "strategy": strategy,
            "performance_gain": performance_gain,
            "timestamp": datetime.now()
        }
    
    async def get_strategy_recommendation(self,
                                         agent_id: str,
                                         task_type: str) -> Dict[str, Any]:
        """Get strategy recommendation based on learned strategies"""
        # Look for successful strategies for this task type
        for key, strategy_info in self.learned_strategies.items():
            if task_type in key:
                return {
                    "suggested_strategy": strategy_info["strategy"],
                    "expected_gain": strategy_info["performance_gain"] * 0.8,  # Conservative estimate
                    "learned_from": strategy_info["agent_id"]
                }
        
        return {
            "suggested_strategy": "default",
            "expected_gain": 0,
            "learned_from": None
        }
    
    async def distribute_workload(self,
                                 tasks: List[Dict[str, Any]],
                                 agents: List[Dict[str, Any]],
                                 optimization_goal: str = "balanced") -> List[Dict[str, Any]]:
        """Distribute workload across agents"""
        distribution = []
        
        # Initialize agent workloads
        for agent in agents:
            distribution.append({
                "agent_id": agent["id"],
                "tasks": [],
                "total_effort": 0
            })
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t["priority"], reverse=True)
        
        # Distribute tasks
        for task in sorted_tasks:
            # Find agent with least load under capacity
            best_agent_idx = None
            min_load = float('inf')
            
            for i, agent_work in enumerate(distribution):
                agent = agents[i]
                current_load = agent_work["total_effort"]
                
                if current_load + task["estimated_effort"] <= agent["capacity"]:
                    if current_load < min_load:
                        min_load = current_load
                        best_agent_idx = i
            
            if best_agent_idx is not None:
                distribution[best_agent_idx]["tasks"].append(task)
                distribution[best_agent_idx]["total_effort"] += task["estimated_effort"]
        
        return distribution
    
    async def synthesize_results(self,
                                agent_results: List[Dict[str, Any]],
                                synthesis_strategy: str = "comprehensive") -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        self.logger.info(f"Synthesizing results from {len(agent_results)} agents")
        
        synthesis = {
            "contributing_agents": [],
            "overall_confidence": 0
        }
        
        # Extract and combine results
        entities = []
        sentiments = {}
        summaries = []
        total_confidence = 0
        
        for result in agent_results:
            agent = result["agent"]
            confidence = result["confidence"]
            
            synthesis["contributing_agents"].append(agent)
            total_confidence += confidence
            
            # Process based on agent type
            if "entities" in result:
                entities.extend(result["entities"])
            
            if "sentiments" in result:
                sentiments.update(result["sentiments"])
            
            if "summary" in result:
                summaries.append(result["summary"])
        
        # Build comprehensive synthesis
        synthesis["key_entities"] = list(set(entities))  # Deduplicate
        synthesis["sentiment_overview"] = sentiments
        
        # Combine summaries
        if summaries:
            synthesis["unified_summary"] = " ".join(summaries)
        else:
            synthesis["unified_summary"] = "Analysis complete"
        
        # Calculate overall confidence
        synthesis["overall_confidence"] = total_confidence / len(agent_results) if agent_results else 0
        
        return synthesis