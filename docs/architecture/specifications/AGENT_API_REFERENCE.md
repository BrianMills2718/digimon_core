# Agent API Reference

## Overview

This document provides comprehensive API documentation for all agent interfaces in the KGAS agent architecture. It covers base agent interfaces, memory-aware agents, reasoning agents, communicating agents, and specialized agents.

## Table of Contents

1. [Base Agent Interface](#base-agent-interface)
2. [Memory-Aware Agent API](#memory-aware-agent-api)
3. [Reasoning Agent API](#reasoning-agent-api)
4. [Communicating Agent API](#communicating-agent-api)
5. [Specialized Agent APIs](#specialized-agent-apis)
6. [Enhanced Tool APIs](#enhanced-tool-apis)
7. [Communication Protocol](#communication-protocol)
8. [Configuration Reference](#configuration-reference)

---

## Base Agent Interface

### Agent

Base interface that all agents must implement.

#### Methods

##### `execute(task: Task) -> Result`

Execute a task and return results.

**Parameters:**
- `task` (Task): Task to execute with type, parameters, and context

**Returns:**
- `Result`: Execution result with success status, data, and metadata

**Example:**
```python
from src.orchestration.base import Task, Result

task = Task(
    task_type="document_processing",
    parameters={"document_paths": ["file.pdf"]},
    context={"priority": "high"}
)

result = await agent.execute(task)
print(f"Success: {result.success}")
print(f"Data: {result.data}")
```

##### `can_handle(task_type: str) -> bool`

Check if agent can handle a specific task type.

**Parameters:**
- `task_type` (str): Type of task to check

**Returns:**
- `bool`: True if agent can handle the task type

**Example:**
```python
if agent.can_handle("document_processing"):
    result = await agent.execute(task)
```

##### `get_capabilities() -> List[str]`

Get list of capabilities supported by the agent.

**Returns:**
- `List[str]`: List of supported task types and capabilities

**Example:**
```python
capabilities = agent.get_capabilities()
print(f"Agent supports: {', '.join(capabilities)}")
```

### Task

Represents a unit of work for an agent.

#### Properties

```python
@dataclass
class Task:
    task_type: str                    # Type of task (e.g., "document_processing")
    parameters: Dict[str, Any]        # Task-specific parameters
    context: Optional[Dict[str, Any]] # Additional context information
    priority: str = "medium"          # Task priority: "low", "medium", "high"
    timeout: Optional[int] = None     # Task timeout in seconds
    metadata: Dict[str, Any] = None   # Additional metadata
```

#### Example

```python
task = Task(
    task_type="entity_extraction",
    parameters={
        "text": "Apple Inc. is based in Cupertino.",
        "chunk_ref": "doc_chunk_1"
    },
    context={
        "domain": "technology",
        "document_type": "news"
    },
    priority="high",
    timeout=30
)
```

### Result

Represents the result of task execution.

#### Properties

```python
@dataclass
class Result:
    success: bool                     # Whether execution was successful
    data: Any                        # Result data
    error: Optional[str] = None      # Error message if unsuccessful
    execution_time: float = 0.0      # Execution time in seconds
    metadata: Dict[str, Any] = None  # Additional result metadata
    task: Optional[Task] = None      # Original task reference
```

#### Example

```python
result = Result(
    success=True,
    data={
        "entities": [...],
        "total_entities": 5
    },
    execution_time=1.23,
    metadata={
        "extraction_method": "spacy",
        "confidence": 0.95
    }
)
```

---

## Memory-Aware Agent API

### MemoryAwareAgent

Extends base agent with memory capabilities for learning and adaptation.

#### Initialization

```python
from src.orchestration.memory import MemoryAwareAgent

agent = MemoryAwareAgent(
    agent_id="memory_agent",
    agent_type="document",
    memory_config={
        "enable_memory": True,
        "max_memories": 1000,
        "consolidation_threshold": 100
    }
)
```

#### Memory Methods

##### `store_execution(execution_data: Dict[str, Any]) -> None`

Store execution results in memory for learning.

**Parameters:**
- `execution_data` (dict): Execution data including task details and results

**Example:**
```python
await agent.store_execution({
    "task_type": "document_processing",
    "parameters": {"chunk_size": 1000},
    "result_quality": 0.95,
    "execution_time": 2.1,
    "success": True
})
```

##### `get_relevant_memories(task: Task, top_k: int = 5) -> List[Dict[str, Any]]`

Retrieve relevant memories for a task.

**Parameters:**
- `task` (Task): Task to find relevant memories for
- `top_k` (int): Maximum number of memories to return

**Returns:**
- `List[dict]`: List of relevant memory entries

**Example:**
```python
memories = await agent.get_relevant_memories(task, top_k=3)
for memory in memories:
    print(f"Similar task: {memory['task_type']}, Score: {memory['score']}")
```

##### `get_learned_strategies(task_type: str) -> List[Dict[str, Any]]`

Get learned strategies for a specific task type.

**Parameters:**
- `task_type` (str): Type of task to get strategies for

**Returns:**
- `List[dict]`: List of learned strategies

**Example:**
```python
strategies = await agent.get_learned_strategies("document_processing")
if strategies:
    best_strategy = strategies[0]
    print(f"Best strategy: {best_strategy['name']}")
```

##### `get_parameter_recommendations(task_type: str) -> Dict[str, Any]`

Get parameter recommendations based on learned patterns.

**Parameters:**
- `task_type` (str): Type of task to get recommendations for

**Returns:**
- `dict`: Parameter recommendations with confidence scores

**Example:**
```python
recommendations = await agent.get_parameter_recommendations("text_chunking")
if recommendations["confidence"] > 0.7:
    chunk_size = recommendations["recommended_parameters"]["chunk_size"]
```

#### Memory Configuration

```python
memory_config = {
    "enable_memory": True,              # Enable memory system
    "max_memories": 1000,               # Maximum stored memories
    "consolidation_threshold": 100,      # When to consolidate memories
    "cleanup_interval": 3600,           # Memory cleanup interval (seconds)
    "similarity_threshold": 0.7,        # Similarity threshold for retrieval
    "storage_backend": "sqlite"          # Storage backend type
}
```

---

## Reasoning Agent API

### ReasoningAgent

Extends memory-aware agent with LLM-powered reasoning capabilities.

#### Initialization

```python
from src.orchestration.reasoning import ReasoningAgent

agent = ReasoningAgent(
    agent_id="reasoning_agent",
    agent_type="analysis",
    memory_config={...},
    reasoning_config={
        "enable_reasoning": True,
        "confidence_threshold": 0.7,
        "default_reasoning_type": "tactical"
    }
)
```

#### Reasoning Methods

##### `reason_about_task(task: Task, memory_context: Dict[str, Any]) -> ReasoningResult`

Apply reasoning to optimize task execution.

**Parameters:**
- `task` (Task): Task to reason about
- `memory_context` (dict): Relevant memory context

**Returns:**
- `ReasoningResult`: Reasoning result with decisions and confidence

**Example:**
```python
reasoning_result = await agent.reason_about_task(task, memory_context)
if reasoning_result.success and reasoning_result.confidence > 0.8:
    # Apply reasoning decisions
    optimized_params = reasoning_result.decision["parameter_adjustments"]
```

##### `make_decision(query: str, context: Dict[str, Any], reasoning_type: ReasoningType) -> ReasoningResult`

Make a decision using LLM reasoning.

**Parameters:**
- `query` (str): Reasoning query
- `context` (dict): Context for reasoning
- `reasoning_type` (ReasoningType): Type of reasoning to apply

**Returns:**
- `ReasoningResult`: Decision result

**Example:**
```python
from src.orchestration.llm_reasoning import ReasoningType

decision = await agent.make_decision(
    query="What chunk size should I use for this document?",
    context={
        "document_length": 50000,
        "complexity": "high",
        "domain": "technical"
    },
    reasoning_type=ReasoningType.TACTICAL
)
```

#### Reasoning Types

```python
class ReasoningType(Enum):
    STRATEGIC = "strategic"      # Long-term planning
    TACTICAL = "tactical"        # Task optimization  
    ADAPTIVE = "adaptive"        # Dynamic adjustment
    DIAGNOSTIC = "diagnostic"    # Problem solving
    PREDICTIVE = "predictive"    # Outcome forecasting
    CREATIVE = "creative"        # Novel solutions
```

#### ReasoningResult

```python
@dataclass
class ReasoningResult:
    success: bool                    # Whether reasoning succeeded
    reasoning: str                   # Reasoning explanation
    decision: Dict[str, Any]         # Decision data
    confidence: float                # Confidence in decision (0-1)
    reasoning_type: ReasoningType    # Type of reasoning used
    execution_time: float            # Time taken for reasoning
    error: Optional[str] = None      # Error message if failed
```

#### Reasoning Configuration

```python
reasoning_config = {
    "enable_reasoning": True,           # Enable reasoning system
    "confidence_threshold": 0.7,        # Minimum confidence for decisions
    "default_reasoning_type": "tactical", # Default reasoning type
    "max_reasoning_time": 30,           # Maximum reasoning time (seconds)
    "temperature": 0.1,                 # LLM temperature for consistency
    "model": "gpt-4",                   # LLM model to use
    "fallback_on_failure": True         # Use fallback if reasoning fails
}
```

---

## Communicating Agent API

### CommunicatingAgent

Extends reasoning agent with inter-agent communication capabilities.

#### Initialization

```python
from src.orchestration.communicating_agent import CommunicatingAgent
from src.orchestration.communication import MessageBus

message_bus = MessageBus()

agent = CommunicatingAgent(
    agent_id="comm_agent",
    agent_type="document",
    memory_config={...},
    reasoning_config={...},
    communication_config={
        "topics": ["entity_insights", "collaboration_requests"],
        "enable_broadcast": True
    },
    message_bus=message_bus
)
```

#### Communication Methods

##### `send_message(recipient_id: str, payload: Dict[str, Any]) -> bool`

Send a direct message to another agent.

**Parameters:**
- `recipient_id` (str): ID of recipient agent
- `payload` (dict): Message payload

**Returns:**
- `bool`: True if message sent successfully

**Example:**
```python
success = await agent.send_message(
    recipient_id="analysis_agent",
    payload={
        "task": "analyze_entities",
        "entities": entity_list,
        "priority": "high"
    }
)
```

##### `broadcast(payload: Dict[str, Any], topic: str = None) -> int`

Broadcast a message to all agents or a specific topic.

**Parameters:**
- `payload` (dict): Message payload
- `topic` (str, optional): Topic to broadcast to

**Returns:**
- `int`: Number of agents that received the message

**Example:**
```python
recipients = await agent.broadcast(
    payload={
        "type": "insights_available",
        "domain": "technology",
        "entities": 150
    },
    topic="entity_insights"
)
```

##### `request(recipient_id: str, payload: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]`

Send a request and wait for response.

**Parameters:**
- `recipient_id` (str): ID of recipient agent
- `payload` (dict): Request payload
- `timeout` (int): Timeout in seconds

**Returns:**
- `Optional[dict]`: Response payload or None if timeout

**Example:**
```python
response = await agent.request(
    recipient_id="graph_agent",
    payload={
        "action": "build_subgraph",
        "entities": entity_subset
    },
    timeout=60
)

if response:
    subgraph = response["subgraph"]
```

##### `collaborate_with(agent_id: str, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]`

Collaborate with another agent on a task.

**Parameters:**
- `agent_id` (str): ID of collaborating agent
- `task` (str): Collaboration task
- `context` (dict): Task context

**Returns:**
- `Optional[dict]`: Collaboration result

**Example:**
```python
result = await agent.collaborate_with(
    agent_id="analysis_agent",
    task="extract_relationships",
    context={
        "text": document_text,
        "entities": entity_list,
        "domain": "medical"
    }
)
```

##### `form_team(task_description: str, required_capabilities: List[str]) -> List[str]`

Form a team of agents for collaborative work.

**Parameters:**
- `task_description` (str): Description of the task
- `required_capabilities` (List[str]): Required agent capabilities

**Returns:**
- `List[str]`: List of agent IDs in the formed team

**Example:**
```python
team = await agent.form_team(
    task_description="Process large medical document",
    required_capabilities=[
        "document_processing",
        "medical_entity_extraction", 
        "graph_building"
    ]
)
```

##### `discover_agents(agent_type: str = None, capability: str = None) -> List[AgentInfo]`

Discover available agents by type or capability.

**Parameters:**
- `agent_type` (str, optional): Type of agents to discover
- `capability` (str, optional): Required capability

**Returns:**
- `List[AgentInfo]`: List of discovered agents

**Example:**
```python
document_agents = await agent.discover_agents(agent_type="document")
analysis_capable = await agent.discover_agents(capability="entity_extraction")
```

#### Communication Events

Agents can handle various communication events:

```python
async def handle_collaboration_request(self, message: Message) -> Dict[str, Any]:
    """Handle incoming collaboration requests."""
    task_type = message.payload.get("task")
    
    if task_type == "entity_extraction":
        # Process collaboration request
        result = await self.extract_entities(message.payload["text"])
        return {"accepted": True, "result": result}
    
    return {"accepted": False, "reason": "Task not supported"}
```

#### Message Types

```python
class MessageType(Enum):
    REQUEST = "request"              # Request-response pattern
    RESPONSE = "response"            # Response to request
    BROADCAST = "broadcast"          # One-to-all message
    NOTIFICATION = "notification"    # System notification
    QUERY = "query"                 # Information query
    DATA = "data"                   # Data sharing
    HEARTBEAT = "heartbeat"         # Health check
    DISCOVERY = "discovery"         # Agent discovery
```

---

## Specialized Agent APIs

### DocumentAgent

Specialized agent for document processing with enhanced capabilities.

#### Methods

##### `process_large_document_collaboratively(document_path: str, team_agents: List[str] = None) -> Result`

Process large documents using collaborative approach.

**Parameters:**
- `document_path` (str): Path to document
- `team_agents` (List[str], optional): Specific agents to collaborate with

**Returns:**
- `Result`: Processing result with collaborative metadata

**Example:**
```python
result = await document_agent.process_large_document_collaboratively(
    document_path="large_report.pdf",
    team_agents=["doc_agent_2", "doc_agent_3"]
)

print(f"Processed {result.data['total_chunks']} chunks")
print(f"Team size: {result.data['team_size']}")
```

#### Supported Task Types

- `document_processing`: Load and chunk documents
- `load_documents`: Load documents without chunking
- `text_chunking`: Chunk provided text
- `collaborative_processing`: Process with other agents

### AnalysisAgent

Specialized agent for entity and relationship analysis.

#### Methods

##### `extract_entities_enhanced(text: str, context: Dict[str, Any]) -> Result`

Extract entities with enhanced processing.

**Parameters:**
- `text` (str): Text to analyze
- `context` (dict): Analysis context

**Returns:**
- `Result`: Enhanced extraction results

**Example:**
```python
result = await analysis_agent.extract_entities_enhanced(
    text="Apple Inc. announced new products.",
    context={
        "domain": "technology",
        "confidence_threshold": 0.8,
        "focus_types": ["ORG", "PRODUCT"]
    }
)
```

#### Supported Task Types

- `entity_extraction`: Extract named entities
- `relationship_extraction`: Extract entity relationships
- `confidence_scoring`: Score extraction confidence
- `pattern_recognition`: Recognize entity patterns

### GraphAgent

Specialized agent for knowledge graph construction and analysis.

#### Methods

##### `build_graph_collaboratively(entities: List[Dict], relationships: List[Dict]) -> Result`

Build knowledge graph collaboratively.

**Parameters:**
- `entities` (List[dict]): Entities to add to graph
- `relationships` (List[dict]): Relationships to create

**Returns:**
- `Result`: Graph building results

**Example:**
```python
result = await graph_agent.build_graph_collaboratively(
    entities=extracted_entities,
    relationships=discovered_relationships
)

print(f"Created {result.data['nodes_created']} nodes")
print(f"Created {result.data['edges_created']} edges")
```

#### Supported Task Types

- `graph_building`: Build knowledge graph
- `node_creation`: Create graph nodes
- `edge_creation`: Create graph edges
- `graph_queries`: Query graph data
- `graph_analysis`: Analyze graph structure

---

## Enhanced Tool APIs

### EnhancedMCPTools

Wrapper for enhanced KGAS tools with agent capabilities.

#### Initialization

```python
from src.tools.enhanced_mcp_tools import EnhancedMCPTools

enhanced_tools = EnhancedMCPTools(
    service_manager=service_manager,
    agent_id="enhanced_tools",
    memory_config={"enable_memory": True},
    reasoning_config={"enable_reasoning": True},
    communication_config={"enable_broadcast": True},
    message_bus=message_bus
)
```

#### Methods

##### `extract_entities_enhanced(text: str, chunk_ref: str, context_metadata: Dict, reasoning_guidance: Dict) -> Dict`

Enhanced entity extraction with memory and reasoning.

**Parameters:**
- `text` (str): Text to extract entities from
- `chunk_ref` (str): Reference to source chunk
- `context_metadata` (dict): Context for reasoning
- `reasoning_guidance` (dict): Reasoning parameters

**Returns:**
- `dict`: Enhanced extraction results

**Example:**
```python
result = await enhanced_tools.extract_entities_enhanced(
    text="Microsoft Corporation is based in Redmond.",
    chunk_ref="doc_chunk_1",
    context_metadata={
        "domain": "technology",
        "document_type": "news"
    },
    reasoning_guidance={
        "extraction_strategy": "high_precision",
        "focus_types": ["ORG", "GPE"]
    }
)

entities = result["entities"]
reasoning_applied = result["reasoning_applied"]
```

##### `discover_relationships_enhanced(text: str, entities: List[Dict], chunk_ref: str, context_metadata: Dict) -> Dict`

Enhanced relationship discovery with reasoning validation.

**Parameters:**
- `text` (str): Source text
- `entities` (List[dict]): Extracted entities
- `chunk_ref` (str): Source chunk reference
- `context_metadata` (dict): Additional context

**Returns:**
- `dict`: Enhanced relationship results

**Example:**
```python
relationships = await enhanced_tools.discover_relationships_enhanced(
    text=document_text,
    entities=extracted_entities,
    chunk_ref="doc_chunk_1",
    context_metadata={
        "domain": "business",
        "validation_level": "high"
    }
)
```

##### `build_graph_collaboratively(entities: List[Dict], relationships: List[Dict], source_refs: List[str], collaboration_agents: List[str]) -> Dict`

Collaborative graph building with distributed processing.

**Parameters:**
- `entities` (List[dict]): Entities to build
- `relationships` (List[dict]): Relationships to create
- `source_refs` (List[str]): Source references
- `collaboration_agents` (List[str]): Collaborating agents

**Returns:**
- `dict`: Graph building results

**Example:**
```python
result = await enhanced_tools.build_graph_collaboratively(
    entities=all_entities,
    relationships=all_relationships,
    source_refs=["doc1", "doc2"],
    collaboration_agents=["agent1", "agent2"]
)
```

---

## Communication Protocol

### Message Structure

```python
@dataclass
class Message:
    message_id: str                      # Unique message identifier
    message_type: MessageType            # Type of message
    sender_id: str                       # Sending agent ID
    recipient_id: Optional[str]          # Recipient agent ID (None for broadcast)
    topic: Optional[str]                 # Topic for pub/sub
    payload: Dict[str, Any]              # Message payload
    priority: MessagePriority            # Message priority
    timestamp: datetime                  # Message timestamp
    correlation_id: Optional[str]        # For request-response correlation
    reply_to: Optional[str]              # Reply channel
    ttl: Optional[int]                   # Time to live in seconds
    metadata: Dict[str, Any]             # Additional metadata
```

### Communication Patterns

#### 1. Direct Messaging

```python
# Send direct message
await agent.send_message("recipient_agent", {"data": "value"})

# Handle incoming messages
async def handle_message(self, message: Message):
    if message.payload.get("action") == "process":
        # Handle processing request
        pass
```

#### 2. Request-Reply

```python
# Send request and wait for reply
response = await agent.request("target_agent", {
    "action": "analyze",
    "data": analysis_data
})

# Handle requests
async def handle_request(self, message: Message) -> Dict[str, Any]:
    # Process request
    result = self.process_data(message.payload["data"])
    return {"result": result, "status": "success"}
```

#### 3. Publish-Subscribe

```python
# Subscribe to topic
await agent.subscribe("entity_insights")

# Publish to topic
await agent.publish("entity_insights", {
    "entities_found": 25,
    "domain": "medical",
    "confidence": 0.92
})

# Handle published messages
async def handle_entity_insights(self, message: Message):
    insights = message.payload
    # Process insights
```

#### 4. Broadcast

```python
# Broadcast to all agents
count = await agent.broadcast({
    "announcement": "Processing complete",
    "results_available": True
})

# Handle broadcasts
async def handle_broadcast(self, message: Message):
    if message.payload.get("announcement"):
        # Handle announcement
        pass
```

---

## Configuration Reference

### Agent Configuration

```python
agent_config = {
    # Basic configuration
    "agent_id": "my_agent",
    "agent_type": "document",
    
    # Memory configuration
    "memory": {
        "enable_memory": True,
        "max_memories": 1000,
        "consolidation_threshold": 100,
        "cleanup_interval": 3600,
        "similarity_threshold": 0.7
    },
    
    # Reasoning configuration
    "reasoning": {
        "enable_reasoning": True,
        "confidence_threshold": 0.7,
        "default_reasoning_type": "tactical",
        "max_reasoning_time": 30,
        "temperature": 0.1,
        "model": "gpt-4"
    },
    
    # Communication configuration
    "communication": {
        "topics": ["insights", "collaboration"],
        "enable_broadcast": True,
        "message_timeout": 30,
        "max_queue_size": 1000
    },
    
    # Tool configuration
    "tools": {
        "enable_enhanced_tools": True,
        "tool_timeout": 60,
        "max_concurrent_tools": 5
    }
}
```

### Service Manager Configuration

```python
service_config = {
    "identity_service": {
        "enable": True,
        "entity_similarity_threshold": 0.8
    },
    "provenance_service": {
        "enable": True,
        "storage_backend": "sqlite"
    },
    "quality_service": {
        "enable": True,
        "confidence_threshold": 0.7
    }
}
```

### Message Bus Configuration

```python
message_bus_config = {
    "max_message_size": 10240,      # Maximum message size in bytes
    "message_timeout": 30,          # Message timeout in seconds
    "max_queue_size": 1000,         # Maximum queue size per topic
    "cleanup_interval": 300,        # Cleanup interval in seconds
    "retry_attempts": 3,            # Number of retry attempts
    "retry_delay": 1.0             # Delay between retries in seconds
}
```

---

## Error Handling

### Common Exceptions

```python
class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class TaskExecutionError(AgentError):
    """Task execution failed."""
    pass

class MemoryError(AgentError):
    """Memory operation failed."""
    pass

class ReasoningError(AgentError):
    """Reasoning operation failed."""
    pass

class CommunicationError(AgentError):
    """Communication operation failed."""
    pass
```

### Error Handling Patterns

```python
try:
    result = await agent.execute(task)
    if not result.success:
        logger.error(f"Task failed: {result.error}")
except TaskExecutionError as e:
    logger.error(f"Execution error: {e}")
except CommunicationError as e:
    logger.error(f"Communication error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Loose Coupling**: Agents should be independent and communicate through messages
- **Error Recovery**: Implement robust error handling and recovery mechanisms
- **Resource Management**: Properly manage memory, connections, and other resources

### 2. Memory Usage

- **Selective Storage**: Only store valuable execution data in memory
- **Regular Cleanup**: Configure appropriate cleanup intervals
- **Similarity Thresholds**: Tune similarity thresholds for optimal retrieval
- **Memory Limits**: Set appropriate memory limits to prevent resource exhaustion

### 3. Reasoning

- **Appropriate Types**: Choose the right reasoning type for each task
- **Confidence Thresholds**: Set appropriate confidence thresholds
- **Fallback Strategies**: Implement fallbacks when reasoning fails
- **Context Quality**: Provide rich, relevant context for better reasoning

### 4. Communication

- **Message Size**: Keep messages reasonably sized for performance
- **Timeouts**: Set appropriate timeouts for requests
- **Error Handling**: Handle communication failures gracefully
- **Topic Organization**: Use clear, hierarchical topic naming

### 5. Performance

- **Async Operations**: Use async/await for all I/O operations
- **Batching**: Batch similar operations when possible
- **Caching**: Cache frequently accessed data
- **Monitoring**: Monitor agent performance and resource usage

---

## Examples

### Complete Agent Implementation

```python
from src.orchestration.communicating_agent import CommunicatingAgent
from src.orchestration.base import Task, Result

class MyCustomAgent(CommunicatingAgent):
    def __init__(self, **kwargs):
        super().__init__(
            agent_id="custom_agent",
            agent_type="custom",
            **kwargs
        )
        self.capabilities = ["custom_processing", "data_analysis"]
    
    def can_handle(self, task_type: str) -> bool:
        return task_type in self.capabilities
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities.copy()
    
    async def _execute_with_memory(self, task: Task, memory_context: Dict[str, Any]) -> Result:
        # Get relevant memories
        memories = await self.get_relevant_memories(task)
        
        # Apply reasoning if needed
        if self.reasoning_engine:
            reasoning_result = await self.reason_about_task(task, memory_context)
            if reasoning_result.success:
                # Apply reasoning decisions
                task.parameters.update(reasoning_result.decision.get("parameters", {}))
        
        # Execute task
        if task.task_type == "custom_processing":
            result = await self._custom_processing(task)
        elif task.task_type == "data_analysis":
            result = await self._data_analysis(task)
        else:
            result = Result(success=False, error=f"Unknown task type: {task.task_type}")
        
        # Store execution in memory
        if result.success:
            await self.store_execution({
                "task_type": task.task_type,
                "parameters": task.parameters,
                "success": True,
                "execution_time": result.execution_time
            })
        
        return result
    
    async def _custom_processing(self, task: Task) -> Result:
        # Custom processing logic
        data = task.parameters.get("data", [])
        processed_data = [item.upper() for item in data]
        
        return Result(
            success=True,
            data={"processed": processed_data},
            execution_time=0.1
        )
    
    async def _data_analysis(self, task: Task) -> Result:
        # Data analysis logic
        data = task.parameters.get("data", [])
        analysis = {
            "count": len(data),
            "average": sum(data) / len(data) if data else 0
        }
        
        return Result(
            success=True,
            data={"analysis": analysis},
            execution_time=0.2
        )
```

### Agent Usage

```python
# Initialize agent with full capabilities
agent = MyCustomAgent(
    memory_config={"enable_memory": True},
    reasoning_config={"enable_reasoning": True},
    communication_config={"enable_broadcast": True},
    message_bus=message_bus
)

# Execute tasks
task1 = Task(
    task_type="custom_processing",
    parameters={"data": ["hello", "world"]}
)

result1 = await agent.execute(task1)
print(f"Result: {result1.data}")

# Collaborate with other agents
collaboration_result = await agent.collaborate_with(
    agent_id="analysis_agent",
    task="analyze_results",
    context={"data": result1.data}
)
```

This comprehensive API reference provides detailed documentation for all agent interfaces, methods, configurations, and usage patterns in the KGAS agent architecture.