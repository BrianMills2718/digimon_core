# Dynamic Orchestration Initiative

Created: 2025-07-31
Status: PLANNED
Priority: HIGH

## Problem Statement

The current vertical slice demonstrates tool functionality but uses a hardcoded, sequential pipeline that doesn't leverage the sophisticated orchestration capabilities built into KGAS:

1. **No MCP Integration**: Tools are invoked directly via Python instead of through the Model Context Protocol
2. **Static Pipeline**: Fixed sequence with no ability to adapt based on results
3. **No Agent Integration**: WorkflowAgent can generate workflows but doesn't execute them
4. **Sequential Only**: No parallel execution despite having parallel engines available
5. **Transient Provenance**: Tracking data is lost between runs

## Goal

Transform the vertical slice from a proof-of-concept into a production-ready system that demonstrates:
- Dynamic workflow planning and execution
- MCP-based tool access
- Agent-driven orchestration
- Adaptive execution based on results
- Persistent provenance tracking

## Technical Approach

### 1. Enable MCP Tool Access

**Current State**:
```python
# Direct invocation
tool = T01PDFLoaderUnified(service_manager)
result = tool.execute(request)
```

**Target State**:
```python
# MCP protocol
mcp_bridge.invoke_tool("T01_PDF_LOADER", request)
```

**Implementation**:
- Create MCP server that wraps existing tools
- Implement tool discovery via MCP
- Add MCP client to orchestrator
- Maintain backward compatibility

### 2. Implement DAG-Based Execution

**Current State**:
```python
# Hardcoded sequence
result1 = t01.execute(request1)
result2 = t15a.execute(request2)
# etc...
```

**Target State**:
```python
# DAG execution
dag = WorkflowDAG()
dag.add_node("load", "T01")
dag.add_node("chunk", "T15A", depends_on=["load"])
dag.add_parallel_nodes(["ner", "rel"], ["T23A", "T27"], depends_on=["chunk"])
executor.execute_dag(dag)
```

**Implementation**:
- Create DAG data structure
- Implement topological sort
- Add parallel execution support
- Handle data passing between nodes

### 3. Connect WorkflowAgent to Execution

**Current State**:
```python
# Agent generates YAML but doesn't execute
workflow_yaml = agent.generate_workflow(request)
# Manual execution required
```

**Target State**:
```python
# Agent drives entire pipeline
result = agent.process_request(
    "Analyze these documents for key relationships",
    documents=["doc1.pdf", "doc2.pdf"]
)
```

**Implementation**:
- Parse WorkflowAgent YAML to DAG
- Add execution monitoring to agent
- Implement feedback loop for results
- Enable multi-iteration workflows

### 4. Add Adaptive Execution

**Current State**:
```python
# Fixed pipeline regardless of results
```

**Target State**:
```python
# Adaptive based on results
if len(entities) < threshold:
    # Try different extraction method
    dag.add_conditional_node("enhanced_ner", "T23B")
elif confidence < threshold:
    # Add validation step
    dag.add_validation_node("validate", "T95")
```

**Implementation**:
- Add conditional nodes to DAG
- Implement decision functions
- Create feedback mechanisms
- Add workflow templates for common patterns

### 4. Persist Provenance Data

**Current State**:
```python
# In-memory only
provenance_service.operations  # Lost on restart
```

**Target State**:
```python
# Persistent storage
provenance_db.query(
    "SELECT * FROM operations WHERE workflow_id = ?",
    workflow_id
)
```

**Implementation**:
- Add SQLite/PostgreSQL backend
- Create provenance schema
- Implement query interface
- Add visualization tools

## Success Criteria

1. **MCP Integration**: All tools accessible via MCP protocol
2. **Dynamic Workflows**: Can generate and execute workflows from natural language
3. **Parallel Execution**: Independent steps run concurrently
4. **Adaptive Logic**: Pipeline adjusts based on intermediate results
5. **Persistent Tracking**: Full provenance queryable after execution

## Timeline

### Phase 1: MCP Integration (2 weeks)
- Week 1: Create MCP server wrapper
- Week 2: Test with existing tools

### Phase 2: DAG Execution (2 weeks)
- Week 3: Implement DAG structure
- Week 4: Add parallel executor

### Phase 3: Agent Integration (2 weeks)
- Week 5: Connect agent to DAG builder
- Week 6: End-to-end testing

### Phase 4: Adaptive Logic (1 week)
- Week 7: Add conditional execution

### Phase 5: Provenance Persistence (1 week)
- Week 8: Database backend and queries

**Total: 8 weeks**

## Risks and Mitigations

1. **Risk**: Breaking existing functionality
   - **Mitigation**: Maintain backward compatibility, comprehensive testing

2. **Risk**: Performance degradation from MCP overhead
   - **Mitigation**: Benchmark and optimize, allow direct fallback

3. **Risk**: Complex debugging with dynamic workflows
   - **Mitigation**: Enhanced logging, visualization tools

## Dependencies

- MCP protocol implementation
- WorkflowAgent must be functional
- Provenance service must be stable
- Neo4j must be running for graph tools

## Validation Plan

1. **Unit Tests**: Each component tested independently
2. **Integration Tests**: Full pipeline with all features
3. **Performance Tests**: Ensure no regression
4. **User Acceptance**: Natural language to results

## Expected Impact

- **Flexibility**: Any workflow possible, not just hardcoded pipeline
- **Performance**: Parallel execution speeds up processing
- **Usability**: Natural language interface for non-technical users
- **Reliability**: Full audit trail for debugging and compliance
- **Scalability**: Foundation for distributed execution
