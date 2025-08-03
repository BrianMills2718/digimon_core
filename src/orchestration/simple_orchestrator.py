"""
Simple sequential orchestrator for KGAS agent coordination.

This orchestrator executes agent tasks sequentially, passing context
between steps. It's designed to be easy to understand, debug, and replace.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .base import Orchestrator, Task, Result, TaskPriority
from .mcp_adapter import MCPToolAdapter
from .agents import (
    DocumentAgent,
    AnalysisAgent,
    SimpleGraphAgent,
    SimpleInsightAgent
)

logger = logging.getLogger(__name__)


class SimpleSequentialOrchestrator(Orchestrator):
    """
    Simple sequential orchestrator - easy to understand and modify.
    
    Executes workflow steps one after another, passing context between steps.
    Configuration-driven to enable easy workflow modification without code changes.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize orchestrator.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.mcp_adapter = MCPToolAdapter()
        self.agents: Dict[str, Any] = {}
        self._initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Workflow tracking
        self._current_workflow_id = None
        self._workflow_start_time = None
    
    async def initialize(self) -> bool:
        """
        Initialize orchestrator and all dependencies.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("Initializing SimpleSequentialOrchestrator")
            
            # Initialize MCP adapter
            adapter_initialized = await self.mcp_adapter.initialize()
            if not adapter_initialized:
                self.logger.warning("MCP adapter initialization failed - running in limited mode")
            
            # Create agents based on configuration
            self._create_agents()
            
            # Start message bus if enabled
            if self.message_bus:
                await self.message_bus.start()
                self.logger.info("Message bus started")
            
            # Initialize all agents
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'initialize'):
                    await agent.initialize()
                    self.logger.debug(f"Initialized agent: {agent_name}")
                
                # Initialize communication for communicating agents
                if hasattr(agent, 'initialize_communication') and self.message_bus:
                    await agent.initialize_communication(self.message_bus)
                    self.logger.debug(f"Initialized communication for agent: {agent_name}")
            
            self._initialized = True
            self.logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Orchestrator initialization failed: {e}")
            self._initialized = False
            return False
    
    def _create_agents(self):
        """Create agents based on configuration."""
        # Default agents if not specified in config
        default_agents = {
            "document": DocumentAgent,
            "analysis": AnalysisAgent,
            "graph": SimpleGraphAgent,
            "insight": SimpleInsightAgent
        }
        
        # Get agent config
        agent_config = self.config.get("agents", {})
        self.agent_classes = default_agents  # Store for later use
        
        # Initialize message bus if communication is enabled
        self.message_bus = None
        if self.config.get("communication", {}).get("enabled", False):
            from .communication import MessageBus
            self.message_bus = MessageBus()
            
        # Initialize agents with memory, reasoning, and communication configuration
        for agent_name, agent_class in self.agent_classes.items():
            memory_config = self.config.get("memory", {}).get(agent_name, {})
            
            # Handle enhanced agents with reasoning and communication capabilities
            if agent_class in [DocumentAgent, AnalysisAgent]:
                reasoning_config = self.config.get("reasoning", {}).get(agent_name, {})
                communication_config = self.config.get("communication", {}).get(agent_name, {})
                
                # Check if agent needs communication capabilities
                if hasattr(agent_class, '__init__') and 'message_bus' in agent_class.__init__.__code__.co_varnames:
                    self.agents[agent_name] = agent_class(
                        self.mcp_adapter, 
                        f"{agent_name}_agent", 
                        memory_config, 
                        reasoning_config,
                        communication_config,
                        self.message_bus
                    )
                else:
                    # Fallback for agents not yet updated
                    self.agents[agent_name] = agent_class(
                        self.mcp_adapter, 
                        f"{agent_name}_agent", 
                        memory_config, 
                        reasoning_config
                    )
            else:
                # Legacy agents without memory or reasoning
                self.agents[agent_name] = agent_class(self.mcp_adapter, f"{agent_name}_agent")
            
            self.logger.debug(f"Created agent: {agent_name}")
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Result:
        """
        Process user request using configurable workflow.
        
        Args:
            request: User request string
            context: Optional initial context
            
        Returns:
            Result of request processing
        """
        start_time = time.time()
        self._current_workflow_id = str(uuid.uuid4())
        self._workflow_start_time = datetime.now()
        
        try:
            # Validate request
            if not await self.validate_request(request):
                return Result(
                    success=False,
                    error="Invalid request",
                    execution_time=time.time() - start_time
                )
            
            # Determine workflow based on request
            workflow = self._determine_workflow(request)
            self.logger.info(f"Selected workflow: {workflow['name']} with {len(workflow['steps'])} steps")
            
            # Initialize context
            workflow_context = context or {}
            workflow_context["original_request"] = request
            workflow_context["workflow_id"] = self._current_workflow_id
            workflow_context["workflow_name"] = workflow["name"]
            
            # Execute workflow steps
            results = []
            completed_steps = []
            
            for i, step in enumerate(workflow["steps"]):
                step_result = await self._execute_step(i, step, workflow_context, results)
                
                if not step_result.success and step.get("required", True):
                    # Required step failed - abort workflow
                    return Result(
                        success=False,
                        error=f"Required step {i+1} failed: {step_result.error}",
                        data={
                            "completed_steps": completed_steps,
                            "failed_step": i + 1,
                            "partial_results": results
                        },
                        execution_time=time.time() - start_time,
                        metadata={
                            "orchestrator": self.orchestrator_type,
                            "workflow": workflow["name"]
                        }
                    )
                
                results.append(step_result)
                completed_steps.append({
                    "step": i + 1,
                    "agent": step["agent"],
                    "task_type": step["task_type"],
                    "success": step_result.success
                })
                
                # Add result to context for next steps
                if step_result.success:
                    context_key = f"{step['agent']}_result"
                    workflow_context[context_key] = step_result.data
            
            # Compile final result
            final_insights = self._compile_final_insights(results, workflow_context)
            
            return Result(
                success=True,
                data={
                    "workflow_results": results,
                    "final_insights": final_insights,
                    "completed_steps": completed_steps,
                    "workflow_context": workflow_context
                },
                execution_time=time.time() - start_time,
                metadata={
                    "orchestrator": self.orchestrator_type,
                    "workflow": workflow["name"],
                    "total_steps": len(workflow["steps"])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            return Result(
                success=False,
                error=f"Orchestration failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _execute_step(self, step_index: int, step: Dict[str, Any],
                          context: Dict[str, Any], previous_results: List[Result]) -> Result:
        """Execute a single workflow step."""
        agent_name = step["agent"]
        task_type = step["task_type"]
        
        self.logger.info(f"Executing step {step_index + 1}: {agent_name}.{task_type}")
        
        # Check if agent exists
        if agent_name not in self.agents:
            return Result(
                success=False,
                error=f"Agent '{agent_name}' not available"
            )
        
        agent = self.agents[agent_name]
        
        # Check if agent can handle task
        if not agent.can_handle(task_type):
            return Result(
                success=False,
                error=f"Agent '{agent_name}' cannot handle task type '{task_type}'"
            )
        
        # Create task with context from previous steps
        task = Task(
            task_type=task_type,
            parameters=step.get("parameters", {}),
            context=context,
            timeout=step.get("timeout", 300),
            priority=TaskPriority[step.get("priority", "MEDIUM").upper()],
            task_id=f"{self._current_workflow_id}_step_{step_index + 1}"
        )
        
        # Execute with agent
        try:
            result = await agent.execute(task)
            self.logger.info(f"Step {step_index + 1} completed: success={result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Step {step_index + 1} execution error: {e}")
            return Result(
                success=False,
                error=f"Agent execution failed: {str(e)}"
            )
    
    def _determine_workflow(self, request: str) -> Dict[str, Any]:
        """
        Determine workflow based on request.
        
        This is a simple implementation that can be made much smarter later.
        Future versions could use:
        - LLM to analyze request and select workflow
        - Keyword matching with configured patterns
        - User-specified workflow names
        
        Args:
            request: User request
            
        Returns:
            Workflow definition
        """
        # Check configured workflows
        workflows = self.config.get("workflows", {})
        
        # Simple keyword matching (can be enhanced)
        request_lower = request.lower()
        
        # Check for specific workflow requests
        for workflow_name, workflow_def in workflows.items():
            if workflow_name.lower() in request_lower:
                return {
                    "name": workflow_name,
                    "steps": workflow_def.get("steps", [])
                }
        
        # Default to research workflow
        return {
            "name": "basic_research",
            "steps": [
                {
                    "agent": "document",
                    "task_type": "document_processing",
                    "parameters": {},
                    "required": True
                },
                {
                    "agent": "analysis",
                    "task_type": "entity_extraction",
                    "parameters": {},
                    "required": True
                },
                {
                    "agent": "graph",
                    "task_type": "graph_building",
                    "parameters": {},
                    "required": True
                },
                {
                    "agent": "insight",
                    "task_type": "insight_generation",
                    "parameters": {"query": request},
                    "required": False
                }
            ]
        }
    
    def _compile_final_insights(self, results: List[Result], context: Dict[str, Any]) -> Dict[str, Any]:
        """Compile insights from all workflow steps."""
        insights = {
            "summary": "Workflow completed successfully",
            "key_findings": [],
            "statistics": {}
        }
        
        # Extract insights from each step
        for i, result in enumerate(results):
            if result.success and result.data:
                # Document processing insights
                if "total_documents" in result.data:
                    insights["statistics"]["documents_processed"] = result.data["total_documents"]
                    insights["statistics"]["chunks_created"] = result.data.get("total_chunks", 0)
                
                # Analysis insights
                if "total_entities" in result.data:
                    insights["statistics"]["entities_found"] = result.data["total_entities"]
                    insights["statistics"]["relationships_found"] = result.data.get("total_relationships", 0)
                
                # Graph insights
                if "nodes_created" in result.data:
                    insights["statistics"]["graph_nodes"] = result.data["nodes_created"]
                    insights["statistics"]["graph_edges"] = result.data.get("edges_created", 0)
                
                # Query insights
                if "insights" in result.data:
                    query_insights = result.data["insights"]
                    if "key_findings" in query_insights:
                        insights["key_findings"].extend(query_insights["key_findings"])
        
        # Add workflow metadata
        insights["workflow_metadata"] = {
            "workflow_id": context.get("workflow_id"),
            "workflow_name": context.get("workflow_name"),
            "original_request": context.get("original_request")
        }
        
        return insights
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {config_path}")
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        # Default configuration
        return {
            "orchestration_type": "simple_sequential",
            "max_workflow_time": 300,  # 5 minutes
            "enable_parallel": False,  # Can enable later
            "retry_strategy": {
                "enabled": False,
                "max_retries": 3,
                "backoff_multiplier": 2.0
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status and health."""
        status = {
            "orchestrator_type": self.orchestrator_type,
            "initialized": self._initialized,
            "agents_available": list(self.agents.keys()),
            "total_agents": len(self.agents),
            "configuration": {
                "orchestration_type": self.config.get("orchestration_type"),
                "max_workflow_time": self.config.get("max_workflow_time"),
                "enable_parallel": self.config.get("enable_parallel")
            }
        }
        
        # Add current workflow info if active
        if self._current_workflow_id:
            status["current_workflow"] = {
                "workflow_id": self._current_workflow_id,
                "start_time": self._workflow_start_time.isoformat() if self._workflow_start_time else None
            }
        
        # Add MCP adapter status
        if self.mcp_adapter:
            mcp_status = self.mcp_adapter.health_check()
            status["mcp_adapter"] = mcp_status
        
        status["status"] = "healthy" if self._initialized else "not_initialized"
        
        return status
    
    def get_supported_workflows(self) -> List[str]:
        """Get list of supported workflow types."""
        workflows = self.config.get("workflows", {})
        default_workflows = ["basic_research", "document_analysis", "graph_analysis"]
        
        configured_workflows = list(workflows.keys())
        
        return list(set(default_workflows + configured_workflows))
    
    async def validate_request(self, request: str) -> bool:
        """Validate if request can be processed."""
        # Basic validation
        if not request or not isinstance(request, str):
            return False
        
        if len(request.strip()) < 3:
            return False
        
        # Future: Add more sophisticated validation
        # - Check for supported intent
        # - Validate against workflow requirements
        # - Check resource availability
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        # Cleanup communication for agents
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'cleanup_communication'):
                await agent.cleanup_communication()
                self.logger.debug(f"Cleaned up communication for agent: {agent_name}")
        
        # Cleanup agents
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
                self.logger.debug(f"Cleaned up agent: {agent_name}")
        
        # Stop message bus if running
        if self.message_bus:
            await self.message_bus.stop()
            self.logger.info("Message bus stopped")
        
        # Cleanup MCP adapter
        if self.mcp_adapter:
            await self.mcp_adapter.cleanup()
        
        self.agents.clear()
        self._initialized = False
        self.logger.info("Orchestrator cleaned up")