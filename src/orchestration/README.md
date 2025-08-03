# KGAS Agent Orchestration System

A **flexible, minimal, and pivot-ready** agent orchestration system that enables immediate agent coordination while maintaining the ability to completely change orchestration approaches in the future.

## 🎯 Design Philosophy

1. **Start Simple, Scale Smart**: Working orchestration immediately, complexity only when needed
2. **Interface-Based Flexibility**: All components implement stable contracts that can be swapped
3. **Configuration-Driven**: Change behavior via config files, not code changes
4. **Easy to Pivot**: Designed to support complete strategy changes with minimal effort
5. **Production-Ready**: Comprehensive error handling, logging, and monitoring from day 1

## 🚀 Quick Start

```python
from src.orchestration import initialize_orchestration_system

# Initialize with default settings
orchestrator = await initialize_orchestration_system()

# Process a request
result = await orchestrator.process_request(
    "Analyze the key concepts in these documents",
    context={"document_paths": ["doc1.pdf", "doc2.pdf"]}
)

# Check results
if result.success:
    print(f"Analysis complete: {result.data['final_insights']}")
```

## 📁 Architecture

```
src/orchestration/
├── base.py                  # Core interfaces (Agent, Orchestrator, Task, Result)
├── mcp_adapter.py          # Adapter to existing KGAS MCP tools
├── simple_orchestrator.py  # Sequential orchestrator implementation
├── factory.py              # Factory for creating orchestrators
├── agents/                 # Agent implementations
│   ├── document_agent.py   # Document processing (T01, T15A)
│   ├── analysis_agent.py   # Entity/relationship extraction (T23A, T27)
│   ├── graph_agent.py      # Graph building (T31, T34, T68)
│   └── insight_agent.py    # Insight generation (T49)
└── README.md              # This file
```

## 🔧 Configuration

### Default Configuration (`config/orchestration/default_config.json`)

```json
{
  "orchestration_type": "simple_sequential",
  "max_workflow_time": 600,
  "agents": {
    "document": {
      "class": "SimpleDocumentAgent",
      "tools": ["load_documents", "chunk_text"],
      "timeout": 120
    },
    // ... other agents
  },
  "workflows": {
    "research_analysis": {
      "steps": [
        {"agent": "document", "task_type": "document_processing"},
        {"agent": "analysis", "task_type": "entity_extraction"},
        {"agent": "graph", "task_type": "graph_building"},
        {"agent": "insight", "task_type": "insight_generation"}
      ]
    }
  }
}
```

## 🤖 Available Agents

### Document Agent
- **Capabilities**: Document loading, text chunking
- **KGAS Tools**: T01 (PDF Loader), T15A (Text Chunker)
- **Task Types**: `document_processing`, `load_documents`, `text_chunking`

### Analysis Agent
- **Capabilities**: Entity and relationship extraction
- **KGAS Tools**: T23A (Entity Extractor), T27 (Relationship Extractor)
- **Task Types**: `entity_extraction`, `relationship_extraction`, `analysis`

### Graph Agent
- **Capabilities**: Graph construction and analysis
- **KGAS Tools**: T31 (Entity Builder), T34 (Edge Builder), T68 (PageRank)
- **Task Types**: `graph_building`, `entity_building`, `edge_building`, `pagerank_calculation`

### Insight Agent
- **Capabilities**: Query execution and insight generation
- **KGAS Tools**: T49 (Multi-hop Query)
- **Task Types**: `insight_generation`, `graph_querying`, `analysis_summary`

## 🔄 Easy Pivoting

The system is designed for easy pivoting to different approaches:

### 1. Change Orchestration Strategy

```python
# Current: Sequential execution
orchestrator = create_orchestrator("simple")

# Future: Parallel execution
orchestrator = create_orchestrator("parallel")

# Future: LLM-planned workflows
orchestrator = create_orchestrator("llm_planned")
```

### 2. Replace Agent Implementations

```python
# Register a new agent type
class AdvancedDocumentAgent(Agent):
    # Your implementation
    pass

# Use in config
{
  "agents": {
    "document": {
      "class": "AdvancedDocumentAgent"
    }
  }
}
```

### 3. Add External Frameworks

```python
# Register LangChain orchestrator
from orchestration.factory import register_orchestrator

class LangChainOrchestrator(Orchestrator):
    # LangChain integration
    pass

register_orchestrator("langchain", LangChainOrchestrator)

# Use it
orchestrator = create_orchestrator("langchain")
```

## 📊 Workflows

### Pre-configured Workflows

1. **research_analysis**: Full document analysis pipeline
2. **quick_analysis**: Fast analysis without graph building
3. **graph_only**: Build graph from existing entities

### Custom Workflows

Add custom workflows to your config file:

```json
{
  "workflows": {
    "custom_workflow": {
      "steps": [
        {"agent": "document", "task_type": "load_documents"},
        {"agent": "insight", "task_type": "analysis_summary"}
      ]
    }
  }
}
```

## 🧪 Testing

```bash
# Run the test script
python test_orchestration.py

# Run unit tests
pytest tests/unit/orchestration/
```

## 🔮 Future Enhancements

### Phase 2: Parallel Execution
- Execute independent steps concurrently
- Resource management and throttling
- Dependency graph resolution

### Phase 3: LLM-Driven Planning
- Dynamic workflow generation
- Adaptive tool selection
- Self-improving workflows

### Phase 4: External Integrations
- LangChain support
- CrewAI integration
- AutoGen compatibility

## 💡 Best Practices

1. **Start with Simple Sequential**: Get working quickly
2. **Use Configuration**: Modify workflows via config, not code
3. **Monitor Execution**: Check step results and timing
4. **Handle Errors Gracefully**: Use the built-in error handling
5. **Plan for Growth**: Design agents with future capabilities in mind

## 🆘 Troubleshooting

### MCP Tools Not Found
```
Error: MCP adapter not initialized
```
**Solution**: Ensure MCP server dependencies are installed and Neo4j is running

### Agent Not Available
```
Error: Agent 'document' not available
```
**Solution**: Check agent registration in orchestrator initialization

### Workflow Timeout
```
Error: Workflow exceeded max_workflow_time
```
**Solution**: Increase timeout in config or optimize slow steps

## 📚 Examples

See `test_orchestration.py` for comprehensive examples of:
- Basic orchestration usage
- Different workflow configurations
- Pivot flexibility demonstrations
- Error handling patterns

---

**Remember**: This system is designed to be **immediately useful** while remaining **completely replaceable**. Start simple, pivot when needed! 🚀