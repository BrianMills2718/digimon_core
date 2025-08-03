"""
Communicating Agent - Base class for agents with full communication capabilities

Extends ReasoningAgent with inter-agent communication, enabling:
- Direct messaging between agents
- Topic-based publish/subscribe
- Request/reply patterns
- Agent discovery and collaboration
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from src.orchestration.reasoning_agent import ReasoningAgent
from src.orchestration.communication import (
    MessageBus, AgentCommunicator, Message, MessageType, 
    MessagePriority, AgentInfo
)

logger = logging.getLogger(__name__)


class CommunicatingAgent(ReasoningAgent):
    """
    Base class for agents with communication capabilities.
    
    Combines reasoning, memory, and communication to enable
    intelligent agent collaboration.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = "generic",
                 memory_config: Dict[str, Any] = None,
                 reasoning_config: Dict[str, Any] = None,
                 communication_config: Dict[str, Any] = None,
                 message_bus: MessageBus = None):
        """
        Initialize communicating agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (e.g., "document", "analysis")
            memory_config: Memory system configuration
            reasoning_config: Reasoning engine configuration
            communication_config: Communication configuration
            message_bus: Shared message bus instance
        """
        super().__init__(agent_id, memory_config, reasoning_config)
        
        self.agent_type = agent_type
        self.communication_config = communication_config or {}
        self.message_bus = message_bus
        self.communicator = None
        
        # Agent capabilities (for discovery)
        self.capabilities = []
        
        # Collaboration state
        self.collaborators: Dict[str, AgentInfo] = {}
        self.active_conversations: Dict[str, List[Message]] = {}
        
        # Communication statistics
        self.comm_stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "requests_sent": 0,
            "responses_sent": 0,
            "collaborations": 0
        }
    
    async def initialize_communication(self, message_bus: MessageBus = None):
        """Initialize agent communication."""
        if message_bus:
            self.message_bus = message_bus
        
        if not self.message_bus:
            raise ValueError("Message bus required for communication")
        
        # Register with message bus
        success = await self.message_bus.register_agent(
            self.agent_id,
            self.agent_type,
            self.capabilities,
            {"reasoning_enabled": hasattr(self, "reasoning_engine")}
        )
        
        if not success:
            raise RuntimeError(f"Failed to register agent {self.agent_id}")
        
        # Create communicator
        self.communicator = AgentCommunicator(self.agent_id, self.message_bus)
        
        # Register message handlers
        self._register_message_handlers()
        
        # Start message processing
        await self.communicator.start()
        
        # Subscribe to default topics
        await self._subscribe_to_default_topics()
        
        logger.info(f"Communication initialized for agent {self.agent_id}")
    
    async def cleanup_communication(self):
        """Clean up communication resources."""
        if self.communicator:
            await self.communicator.stop()
        
        if self.message_bus and self.agent_id:
            await self.message_bus.unregister_agent(self.agent_id)
    
    def _register_message_handlers(self):
        """Register handlers for different message types."""
        
        @self.communicator.on_message(MessageType.REQUEST)
        async def handle_request(message: Message):
            await self._handle_request(message)
        
        @self.communicator.on_message(MessageType.DATA)
        async def handle_data(message: Message):
            await self._handle_data(message)
        
        @self.communicator.on_message(MessageType.QUERY)
        async def handle_query(message: Message):
            await self._handle_query(message)
        
        @self.communicator.on_message(MessageType.NOTIFICATION)
        async def handle_notification(message: Message):
            await self._handle_notification(message)
    
    async def _subscribe_to_default_topics(self):
        """Subscribe to default topics based on agent type."""
        # All agents subscribe to system events
        await self.communicator.subscribe("system_events")
        await self.communicator.subscribe("agent_events")
        
        # Type-specific subscriptions
        if self.agent_type:
            await self.communicator.subscribe(f"{self.agent_type}_updates")
    
    async def collaborate_with(self, agent_id: str, task: str, 
                             context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Collaborate with another agent on a task.
        
        Args:
            agent_id: ID of agent to collaborate with
            task: Task description
            context: Task context and parameters
            
        Returns:
            Collaboration result or None if failed
        """
        self.comm_stats["collaborations"] += 1
        
        # Use reasoning to plan collaboration
        reasoning_context = {
            "current_state": self.get_state(),
            "memory_context": self.memory.get_context_summary() if self.memory else {},
            "collaborator": agent_id,
            "task": task
        }
        
        reasoning_result = await self.reasoning_engine.reason(
            "tactical",
            f"Plan collaboration with {agent_id} for: {task}",
            reasoning_context
        )
        
        # Prepare collaboration request
        request_data = {
            "task": task,
            "context": context,
            "reasoning": reasoning_result.reasoning if reasoning_result.success else None,
            "requester_capabilities": self.capabilities
        }
        
        # Send collaboration request
        response = await self.communicator.request(agent_id, request_data)
        
        if response:
            # Store collaboration in memory
            if self.memory:
                self.memory.store({
                    "type": "collaboration",
                    "collaborator": agent_id,
                    "task": task,
                    "result": response,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Track conversation
            conversation_id = f"{self.agent_id}_{agent_id}_{task}"
            if conversation_id not in self.active_conversations:
                self.active_conversations[conversation_id] = []
            
            return response
        
        return None
    
    async def broadcast_insight(self, insight: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL):
        """
        Broadcast an insight to all interested agents.
        
        Args:
            insight: The insight to broadcast
            priority: Message priority
        """
        # Add reasoning context to insight
        if self.reasoning_engine:
            reasoning_result = await self.reasoning_engine.reason(
                "diagnostic",
                "Assess insight importance and relevance",
                {"insight": insight}
            )
            
            if reasoning_result.success:
                insight["reasoning_assessment"] = reasoning_result.reasoning
                insight["confidence"] = reasoning_result.confidence
        
        # Broadcast to all agents
        count = await self.communicator.broadcast({
            "type": "insight",
            "source": self.agent_id,
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Broadcast insight to {count} agents")
    
    async def query_agents(self, query: str, agent_type: Optional[str] = None,
                          capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query multiple agents and aggregate responses.
        
        Args:
            query: Query string
            agent_type: Filter by agent type
            capability: Filter by capability
            
        Returns:
            List of responses from agents
        """
        # Discover matching agents
        agents = self.communicator.discover_agents(agent_type, capability)
        
        if not agents:
            return []
        
        # Send queries in parallel
        responses = []
        tasks = []
        
        for agent in agents:
            if agent.agent_id != self.agent_id:  # Don't query self
                task = self.communicator.request(
                    agent.agent_id,
                    {
                        "type": "query",
                        "query": query,
                        "requester": self.agent_id
                    },
                    timeout=10.0
                )
                tasks.append((agent.agent_id, task))
        
        # Gather responses
        for agent_id, task in tasks:
            try:
                response = await task
                if response:
                    responses.append({
                        "agent_id": agent_id,
                        "response": response
                    })
            except Exception as e:
                logger.error(f"Failed to get response from {agent_id}: {e}")
        
        return responses
    
    async def form_team(self, task: str, required_capabilities: List[str]) -> List[str]:
        """
        Form a team of agents for a complex task.
        
        Args:
            task: Task description
            required_capabilities: List of required capabilities
            
        Returns:
            List of agent IDs in the team
        """
        team = [self.agent_id]  # Include self
        
        # Use reasoning to determine team composition
        reasoning_result = await self.reasoning_engine.reason(
            "strategic",
            f"Determine optimal team composition for: {task}",
            {
                "required_capabilities": required_capabilities,
                "available_agents": [a.__dict__ for a in self.communicator.discover_agents()]
            }
        )
        
        # Find agents with required capabilities
        for capability in required_capabilities:
            agents = self.communicator.discover_agents(capability=capability)
            for agent in agents:
                if agent.agent_id not in team and agent.status == "active":
                    # Invite agent to team
                    response = await self.communicator.request(
                        agent.agent_id,
                        {
                            "type": "team_invitation",
                            "task": task,
                            "team_lead": self.agent_id,
                            "required_capability": capability
                        }
                    )
                    
                    if response and response.get("accepted"):
                        team.append(agent.agent_id)
                        break
        
        logger.info(f"Formed team of {len(team)} agents for task: {task}")
        return team
    
    async def _handle_request(self, message: Message):
        """Handle incoming request messages."""
        self.comm_stats["messages_received"] += 1
        
        request_type = message.payload.get("type", "unknown")
        
        try:
            if request_type == "collaboration":
                response = await self._handle_collaboration_request(message)
            elif request_type == "query":
                response = await self._handle_query_request(message)
            elif request_type == "team_invitation":
                response = await self._handle_team_invitation(message)
            else:
                response = await self._handle_generic_request(message)
            
            # Send response
            await self.communicator.reply(message, response)
            self.comm_stats["responses_sent"] += 1
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            await self.communicator.reply(message, {
                "error": str(e),
                "success": False
            })
    
    async def _handle_collaboration_request(self, message: Message) -> Dict[str, Any]:
        """Handle collaboration request from another agent."""
        task = message.payload.get("task")
        context = message.payload.get("context", {})
        
        # Use reasoning to decide on collaboration
        reasoning_result = await self.reasoning_engine.reason(
            "adaptive",
            f"Evaluate collaboration request for: {task}",
            {
                "requester": message.sender_id,
                "task": task,
                "context": context,
                "current_workload": self.get_state()
            }
        )
        
        if reasoning_result.success and reasoning_result.confidence > 0.7:
            # Accept collaboration
            result = await self.execute_task(task, context)
            
            return {
                "accepted": True,
                "result": result,
                "reasoning": reasoning_result.reasoning
            }
        else:
            return {
                "accepted": False,
                "reason": "Unable to collaborate at this time",
                "reasoning": reasoning_result.reasoning if reasoning_result.success else None
            }
    
    async def _handle_query_request(self, message: Message) -> Dict[str, Any]:
        """Handle query request from another agent."""
        query = message.payload.get("query")
        
        # Use memory to find relevant information
        if self.memory:
            memories = self.memory.search(query, top_k=5)
            
            # Use reasoning to synthesize response
            reasoning_result = await self.reasoning_engine.reason(
                "diagnostic",
                f"Synthesize response to query: {query}",
                {
                    "query": query,
                    "memories": memories,
                    "requester": message.sender_id
                }
            )
            
            return {
                "response": reasoning_result.reasoning if reasoning_result.success else "No relevant information",
                "confidence": reasoning_result.confidence if reasoning_result.success else 0.0,
                "sources": len(memories)
            }
        
        return {
            "response": "No memory system available",
            "confidence": 0.0,
            "sources": 0
        }
    
    async def _handle_team_invitation(self, message: Message) -> Dict[str, Any]:
        """Handle team invitation from another agent."""
        task = message.payload.get("task")
        team_lead = message.payload.get("team_lead")
        required_capability = message.payload.get("required_capability")
        
        # Check if we have the required capability
        if required_capability in self.capabilities:
            # Use reasoning to decide
            reasoning_result = await self.reasoning_engine.reason(
                "strategic",
                f"Evaluate team invitation for: {task}",
                {
                    "task": task,
                    "team_lead": team_lead,
                    "required_capability": required_capability,
                    "current_state": self.get_state()
                }
            )
            
            if reasoning_result.success and reasoning_result.confidence > 0.6:
                return {
                    "accepted": True,
                    "agent_id": self.agent_id,
                    "capabilities": self.capabilities
                }
        
        return {
            "accepted": False,
            "reason": "Cannot join team at this time"
        }
    
    async def _handle_generic_request(self, message: Message) -> Dict[str, Any]:
        """Handle generic request messages."""
        # Override in subclasses for specific handling
        return {
            "received": True,
            "agent_id": self.agent_id,
            "message": "Request received but no specific handler"
        }
    
    async def _handle_data(self, message: Message):
        """Handle incoming data messages."""
        self.comm_stats["messages_received"] += 1
        
        # Store in memory if relevant
        if self.memory and message.topic:
            self.memory.store({
                "type": "received_data",
                "topic": message.topic,
                "sender": message.sender_id,
                "data": message.payload,
                "timestamp": message.timestamp.isoformat()
            })
    
    async def _handle_query(self, message: Message):
        """Handle query messages."""
        # Queries are handled as requests
        await self._handle_request(message)
    
    async def _handle_notification(self, message: Message):
        """Handle notification messages."""
        notification_type = message.payload.get("event_type")
        
        if notification_type == "agent_registered":
            # New agent joined - update collaborators
            agent_id = message.payload.get("agent_id")
            if agent_id != self.agent_id:
                agents = self.communicator.discover_agents()
                for agent in agents:
                    if agent.agent_id == agent_id:
                        self.collaborators[agent_id] = agent
                        break
        
        elif notification_type == "agent_unregistered":
            # Agent left - remove from collaborators
            agent_id = message.payload.get("agent_id")
            if agent_id in self.collaborators:
                del self.collaborators[agent_id]
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with communication support.
        
        Override in subclasses for specific task execution.
        """
        return {
            "status": "completed",
            "task": task,
            "agent": self.agent_id,
            "result": "Task executed successfully"
        }
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics."""
        return {
            **self.comm_stats,
            "active_conversations": len(self.active_conversations),
            "known_collaborators": len(self.collaborators)
        }