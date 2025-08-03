"""
Agent Communication System for KGAS Orchestration

Provides inter-agent communication capabilities including:
- Message passing protocol
- Pub/sub messaging patterns
- Request-reply patterns
- Agent discovery and registration
"""

import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can exchange."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    QUERY = "query"
    COMMAND = "command"
    DATA = "data"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    REGISTRATION = "registration"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4


@dataclass
class Message:
    """Communication message between agents."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.REQUEST
    sender_id: str = ""
    recipient_id: Optional[str] = None  # None for broadcasts
    topic: Optional[str] = None  # For pub/sub
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # For request-response
    reply_to: Optional[str] = None  # Reply channel/topic
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "ttl": self.ttl,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=MessageType(data.get("message_type", "request")),
            sender_id=data.get("sender_id", ""),
            recipient_id=data.get("recipient_id"),
            topic=data.get("topic"),
            payload=data.get("payload", {}),
            priority=MessagePriority(data.get("priority", 1)),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            ttl=data.get("ttl"),
            metadata=data.get("metadata", {})
        )


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent_id: str
    agent_type: str
    capabilities: List[str] = field(default_factory=list)
    topics: Set[str] = field(default_factory=set)  # Subscribed topics
    status: str = "active"
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    Central message bus for agent communication.
    
    Supports multiple communication patterns:
    - Direct messaging (point-to-point)
    - Publish/Subscribe (topic-based)
    - Request/Reply
    - Broadcast
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._message_queues: Dict[str, asyncio.Queue] = {}
        self._topic_subscribers: Dict[str, Set[str]] = {}  # topic -> set of agent_ids
        self._message_handlers: Dict[str, Dict[MessageType, Callable]] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}  # correlation_id -> Future
        self._running = False
        self._message_router_task = None
        
        # Statistics
        self._stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_failed": 0,
            "broadcasts_sent": 0,
            "requests_sent": 0,
            "responses_sent": 0
        }
    
    async def start(self):
        """Start the message bus."""
        self._running = True
        self._message_router_task = asyncio.create_task(self._message_router())
        logger.info("Message bus started")
    
    async def stop(self):
        """Stop the message bus."""
        self._running = False
        if self._message_router_task:
            self._message_router_task.cancel()
            try:
                await self._message_router_task
            except asyncio.CancelledError:
                pass
        logger.info("Message bus stopped")
    
    async def register_agent(self, agent_id: str, agent_type: str, 
                           capabilities: List[str] = None,
                           metadata: Dict[str, Any] = None) -> bool:
        """Register an agent with the message bus."""
        if agent_id in self._agents:
            logger.warning(f"Agent {agent_id} already registered")
            return False
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or [],
            metadata=metadata or {}
        )
        
        self._agents[agent_id] = agent_info
        self._message_queues[agent_id] = asyncio.Queue()
        self._message_handlers[agent_id] = {}
        
        logger.info(f"Registered agent: {agent_id} (type: {agent_type})")
        
        # Broadcast agent registration
        await self._broadcast_agent_event("agent_registered", agent_info)
        
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the message bus."""
        if agent_id not in self._agents:
            return False
        
        # Remove from all topic subscriptions
        for topic, subscribers in self._topic_subscribers.items():
            subscribers.discard(agent_id)
        
        # Clean up agent data
        agent_info = self._agents[agent_id]
        del self._agents[agent_id]
        del self._message_queues[agent_id]
        del self._message_handlers[agent_id]
        
        # Broadcast agent unregistration
        await self._broadcast_agent_event("agent_unregistered", agent_info)
        
        logger.info(f"Unregistered agent: {agent_id}")
        return True
    
    async def subscribe(self, agent_id: str, topic: str) -> bool:
        """Subscribe an agent to a topic."""
        if agent_id not in self._agents:
            return False
        
        if topic not in self._topic_subscribers:
            self._topic_subscribers[topic] = set()
        
        self._topic_subscribers[topic].add(agent_id)
        self._agents[agent_id].topics.add(topic)
        
        logger.debug(f"Agent {agent_id} subscribed to topic: {topic}")
        return True
    
    async def unsubscribe(self, agent_id: str, topic: str) -> bool:
        """Unsubscribe an agent from a topic."""
        if agent_id not in self._agents:
            return False
        
        if topic in self._topic_subscribers:
            self._topic_subscribers[topic].discard(agent_id)
        
        self._agents[agent_id].topics.discard(topic)
        
        logger.debug(f"Agent {agent_id} unsubscribed from topic: {topic}")
        return True
    
    def register_handler(self, agent_id: str, message_type: MessageType, handler: Callable):
        """Register a message handler for an agent."""
        if agent_id not in self._message_handlers:
            self._message_handlers[agent_id] = {}
        
        self._message_handlers[agent_id][message_type] = handler
        logger.debug(f"Registered handler for {agent_id}: {message_type.value}")
    
    async def send_message(self, message: Message) -> bool:
        """Send a message to specific agent or topic."""
        self._stats["messages_sent"] += 1
        
        try:
            if message.recipient_id:
                # Direct message
                if message.recipient_id in self._message_queues:
                    await self._message_queues[message.recipient_id].put(message)
                    logger.debug(f"Sent message {message.message_id} to {message.recipient_id}")
                    return True
                else:
                    logger.warning(f"Recipient {message.recipient_id} not found")
                    self._stats["messages_failed"] += 1
                    return False
                    
            elif message.topic:
                # Topic-based message
                subscribers = self._topic_subscribers.get(message.topic, set())
                for subscriber_id in subscribers:
                    if subscriber_id in self._message_queues:
                        await self._message_queues[subscriber_id].put(message)
                
                logger.debug(f"Published message to topic {message.topic} ({len(subscribers)} subscribers)")
                return True
                
            else:
                logger.warning("Message has no recipient or topic")
                self._stats["messages_failed"] += 1
                return False
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self._stats["messages_failed"] += 1
            return False
    
    async def broadcast(self, sender_id: str, payload: Dict[str, Any], 
                       exclude: List[str] = None) -> int:
        """Broadcast a message to all agents."""
        self._stats["broadcasts_sent"] += 1
        exclude = exclude or []
        
        message = Message(
            message_type=MessageType.BROADCAST,
            sender_id=sender_id,
            payload=payload
        )
        
        count = 0
        for agent_id in self._agents:
            if agent_id != sender_id and agent_id not in exclude:
                await self._message_queues[agent_id].put(message)
                count += 1
        
        logger.debug(f"Broadcast from {sender_id} to {count} agents")
        return count
    
    async def request(self, sender_id: str, recipient_id: str, 
                     payload: Dict[str, Any], timeout: float = 30.0) -> Optional[Message]:
        """Send a request and wait for response."""
        self._stats["requests_sent"] += 1
        
        correlation_id = str(uuid.uuid4())
        future = asyncio.Future()
        self._pending_requests[correlation_id] = future
        
        request = Message(
            message_type=MessageType.REQUEST,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            correlation_id=correlation_id,
            reply_to=sender_id
        )
        
        # Send request
        success = await self.send_message(request)
        if not success:
            del self._pending_requests[correlation_id]
            return None
        
        try:
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Request {correlation_id} timed out")
            return None
        finally:
            if correlation_id in self._pending_requests:
                del self._pending_requests[correlation_id]
    
    async def reply(self, original_message: Message, payload: Dict[str, Any]) -> bool:
        """Reply to a request message."""
        if not original_message.correlation_id or not original_message.reply_to:
            logger.warning("Cannot reply - missing correlation_id or reply_to")
            return False
        
        self._stats["responses_sent"] += 1
        
        response = Message(
            message_type=MessageType.RESPONSE,
            sender_id=original_message.recipient_id,
            recipient_id=original_message.reply_to,
            payload=payload,
            correlation_id=original_message.correlation_id
        )
        
        return await self.send_message(response)
    
    async def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Receive next message for an agent."""
        if agent_id not in self._message_queues:
            return None
        
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self._message_queues[agent_id].get(), 
                    timeout=timeout
                )
            else:
                message = await self._message_queues[agent_id].get()
            
            self._stats["messages_delivered"] += 1
            
            # Update agent heartbeat
            if agent_id in self._agents:
                self._agents[agent_id].last_heartbeat = datetime.now()
            
            return message
            
        except asyncio.TimeoutError:
            return None
    
    async def _message_router(self):
        """Route response messages to pending requests."""
        while self._running:
            try:
                # Check all agent queues for responses
                for agent_id, queue in list(self._message_queues.items()):
                    if not queue.empty():
                        message = queue._queue[0]  # Peek at message
                        
                        if (message.message_type == MessageType.RESPONSE and 
                            message.correlation_id in self._pending_requests):
                            # Route response to waiting request
                            await queue.get()  # Remove from queue
                            future = self._pending_requests[message.correlation_id]
                            if not future.done():
                                future.set_result(message)
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy loop
                
            except Exception as e:
                logger.error(f"Error in message router: {e}")
    
    async def _broadcast_agent_event(self, event_type: str, agent_info: AgentInfo):
        """Broadcast agent lifecycle events."""
        event_message = Message(
            message_type=MessageType.NOTIFICATION,
            sender_id="message_bus",
            topic="agent_events",
            payload={
                "event_type": event_type,
                "agent_id": agent_info.agent_id,
                "agent_type": agent_info.agent_type,
                "capabilities": agent_info.capabilities,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        await self.send_message(event_message)
    
    def get_agents(self, agent_type: Optional[str] = None, 
                   capability: Optional[str] = None) -> List[AgentInfo]:
        """Get list of registered agents, optionally filtered."""
        agents = list(self._agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if capability:
            agents = [a for a in agents if capability in a.capabilities]
        
        return agents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        return {
            **self._stats,
            "registered_agents": len(self._agents),
            "active_topics": len(self._topic_subscribers),
            "pending_requests": len(self._pending_requests)
        }


class CommunicationPattern:
    """Base class for communication patterns."""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus


class RequestReplyPattern(CommunicationPattern):
    """Request-Reply communication pattern."""
    
    async def request(self, sender_id: str, recipient_id: str, 
                     request_data: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send request and wait for reply."""
        response = await self.message_bus.request(
            sender_id, recipient_id, request_data, timeout
        )
        
        if response:
            return response.payload
        return None


class PublishSubscribePattern(CommunicationPattern):
    """Publish-Subscribe communication pattern."""
    
    async def publish(self, publisher_id: str, topic: str, data: Dict[str, Any]) -> bool:
        """Publish data to a topic."""
        message = Message(
            message_type=MessageType.DATA,
            sender_id=publisher_id,
            topic=topic,
            payload=data
        )
        
        return await self.message_bus.send_message(message)
    
    async def subscribe(self, subscriber_id: str, topic: str) -> bool:
        """Subscribe to a topic."""
        return await self.message_bus.subscribe(subscriber_id, topic)


class BroadcastPattern(CommunicationPattern):
    """Broadcast communication pattern."""
    
    async def broadcast(self, sender_id: str, data: Dict[str, Any], 
                       exclude: List[str] = None) -> int:
        """Broadcast to all agents."""
        return await self.message_bus.broadcast(sender_id, data, exclude)


class AgentCommunicator:
    """
    Communication interface for individual agents.
    
    Provides high-level communication methods using the message bus.
    """
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self._message_handlers: Dict[MessageType, Callable] = {}
        self._running = False
        self._message_processor_task = None
        
        # Communication patterns
        self.request_reply = RequestReplyPattern(message_bus)
        self.pubsub = PublishSubscribePattern(message_bus)
        self.broadcast = BroadcastPattern(message_bus)
    
    async def start(self):
        """Start message processing."""
        self._running = True
        self._message_processor_task = asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop message processing."""
        self._running = False
        if self._message_processor_task:
            self._message_processor_task.cancel()
            try:
                await self._message_processor_task
            except asyncio.CancelledError:
                pass
    
    def on_message(self, message_type: MessageType):
        """Decorator to register message handlers."""
        def decorator(func):
            self._message_handlers[message_type] = func
            self.message_bus.register_handler(self.agent_id, message_type, func)
            return func
        return decorator
    
    async def send(self, recipient_id: str, data: Dict[str, Any], 
                   message_type: MessageType = MessageType.DATA) -> bool:
        """Send a message to another agent."""
        message = Message(
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            payload=data
        )
        
        return await self.message_bus.send_message(message)
    
    async def request(self, recipient_id: str, data: Dict[str, Any], 
                     timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send request and wait for response."""
        return await self.request_reply.request(
            self.agent_id, recipient_id, data, timeout
        )
    
    async def reply(self, original_message: Message, data: Dict[str, Any]) -> bool:
        """Reply to a request."""
        return await self.message_bus.reply(original_message, data)
    
    async def publish(self, topic: str, data: Dict[str, Any]) -> bool:
        """Publish to a topic."""
        return await self.pubsub.publish(self.agent_id, topic, data)
    
    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic."""
        return await self.pubsub.subscribe(self.agent_id, topic)
    
    async def broadcast(self, data: Dict[str, Any], exclude: List[str] = None) -> int:
        """Broadcast to all agents."""
        return await self.broadcast.broadcast(self.agent_id, data, exclude)
    
    async def _process_messages(self):
        """Process incoming messages."""
        while self._running:
            try:
                message = await self.message_bus.receive_message(self.agent_id, timeout=1.0)
                
                if message:
                    # Find and execute handler
                    handler = self._message_handlers.get(message.message_type)
                    if handler:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(message)
                            else:
                                handler(message)
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}")
                    else:
                        logger.debug(f"No handler for message type: {message.message_type.value}")
                
            except Exception as e:
                logger.error(f"Error processing messages: {e}")
    
    def discover_agents(self, agent_type: Optional[str] = None, 
                       capability: Optional[str] = None) -> List[AgentInfo]:
        """Discover other agents."""
        return self.message_bus.get_agents(agent_type, capability)