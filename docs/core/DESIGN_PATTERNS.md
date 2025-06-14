# Super-Digimon Design Patterns

## Core Architectural Patterns

### Pass-by-Reference Pattern
- **Problem**: Moving large graph data between tools is expensive
- **Solution**: Tools operate on graph IDs, not full data structures
- **Implementation**:
  ```python
  def analyze_community(graph_id: str, community_id: str) -> Dict:
      # Fetch only what's needed from Neo4j
      graph = get_graph_reference(graph_id)
      return graph.analyze_community(community_id)
  ```

### Attribute-Based Compatibility
- **Problem**: Rigid graph schemas break tool composability
- **Solution**: Tools declare required attributes, graphs provide what they have
- **Implementation**:
  ```python
  @tool(required_attrs=["timestamp", "user_id"])
  def temporal_analysis(graph_id: str) -> Results:
      # Tool validates graph has required attributes
      # Gracefully handles optional attributes
  ```

## Data Handling Patterns

### Streaming-First Design
- **Problem**: Large results consume memory and delay user feedback
- **Solution**: Use async generators everywhere
- **Implementation**:
  ```python
  async def* process_entities(graph_id: str):
      async for entity in graph.stream_entities():
          result = await process_entity(entity)
          yield result  # Stream results as available
  ```

### Lazy Evaluation
- **Problem**: Expensive computations may not be needed
- **Solution**: Defer computation until actually required
- **Implementation**:
  ```python
  def get_embeddings(entity_id: str):
      return LazyEmbedding(entity_id)  # Compute only when accessed
  ```

### Data-Level Lineage
- **Problem**: Operation-level lineage tracking explodes combinatorially
- **Solution**: Track lineage at data creation, not every transformation
- **Implementation**:
  ```python
  entity = {
      "id": "e123",
      "name": "John Doe", 
      "source": {"doc_id": "d456", "chunk": 12, "method": "NER"}
  }
  ```

## Error Handling Patterns

### Graceful Degradation
- **Problem**: Perfect analysis may not be possible
- **Solution**: Fall back to simpler methods that work
- **Implementation**:
  ```python
  try:
      result = advanced_community_detection(graph)
  except MemoryError:
      result = simple_connected_components(graph)
  except:
      result = sample_based_detection(graph, sample_size=1000)
  ```

### Multi-Level Validation
- **Problem**: Late validation failures waste resources
- **Solution**: Validate early and at multiple levels
- **Implementation**:
  ```python
  def validate_graph_operation(graph_id, operation):
      # Level 1: Schema validation
      validate_schema(operation)
      # Level 2: Graph existence
      validate_graph_exists(graph_id)
      # Level 3: Attribute requirements
      validate_attributes(graph_id, operation.required_attrs)
      # Level 4: Resource availability
      validate_resources(operation.estimated_memory)
  ```

## Performance Patterns

### Resource-Aware Planning
- **Problem**: Operations may exceed available resources
- **Solution**: Estimate resources before execution
- **Implementation**:
  ```python
  def plan_analysis(graph_id: str, analysis_type: str):
      stats = get_graph_stats(graph_id)
      memory_needed = estimate_memory(analysis_type, stats)
      if memory_needed > available_memory():
          return suggest_alternatives(analysis_type)
  ```

### Progressive Enhancement
- **Problem**: Complex analyses fail on large data
- **Solution**: Start simple, add complexity as data allows
- **Implementation**:
  ```python
  analyzers = [
      BasicAnalyzer(),      # Always works
      StandardAnalyzer(),   # Works on medium data
      AdvancedAnalyzer()    # Needs lots of resources
  ]
  for analyzer in analyzers:
      if analyzer.can_handle(graph_stats):
          return analyzer.analyze(graph)
  ```

### Parallel Execution Decision
- **Problem**: Parallel execution can cause conflicts
- **Solution**: Simple heuristic - parallel for read-only operations
- **Implementation**:
  ```python
  def execute_tools(tool_calls):
      if all(tool.is_read_only() for tool in tool_calls):
          return execute_parallel(tool_calls)
      else:
          return execute_serial(tool_calls)
  ```

## Integration Patterns

### Tool Interface Consistency
- **Problem**: Heterogeneous tools are hard to compose
- **Solution**: Uniform interface for all tools
- **Implementation**:
  ```python
  class Tool:
      name: str
      description: str
      required_attrs: List[str]
      
      def is_read_only(self) -> bool
      async def execute(self, **kwargs) -> Result
  ```

### Aggregate Tools Pattern
- **Problem**: Complex analyses require multiple tool calls
- **Solution**: Reify analysis workflows as first-class tools
- **Implementation**:
  ```python
  @aggregate_tool(name="influential_users_analysis")
  def find_influential_users(graph_id: str):
      # Composed of multiple atomic tools
      entities = entity_search(graph_id, type="user")
      scores = entity_ppr(graph_id, entities)
      communities = entity_community(graph_id, top_k(scores, 10))
      return summarize_influence(entities, scores, communities)
  ```

### MCP Protocol Abstraction
- **Problem**: Direct tool coupling creates brittle systems
- **Solution**: Tools communicate via protocol, not direct calls
- **Implementation**:
  ```python
  # Tools expose via MCP
  @mcp_tool(name="entity_search")
  async def search(...):
      # Tool implementation
  
  # Claude Code calls via protocol
  result = await mcp_call("entity_search", params)
  ```

## Testing Patterns

### Minimal Test Graphs
- **Problem**: Full datasets too large for rapid testing
- **Solution**: Create minimal graphs that exercise all code paths
- **Implementation**:
  ```python
  def create_test_graph():
      # Minimum viable graph: 5 nodes, 7 edges
      # Tests all relationship types
      # Includes all required attributes
      return Graph(nodes=5, edges=7, attrs=["id", "type", "timestamp"])
  ```

### Tool Isolation Testing
- **Problem**: Integration tests are slow and fragile
- **Solution**: Test tools in isolation with mock data
- **Implementation**:
  ```python
  def test_entity_search():
      mock_graph = MockGraph({"e1": {"name": "test"}})
      result = entity_search(mock_graph, query="test")
      assert result == ["e1"]
  ```

### Progressive Test Suites
- **Problem**: Full test suite takes too long
- **Solution**: Layer tests by execution time
- **Implementation**:
  ```bash
  pytest -m unit      # < 1 second per test
  pytest -m integration  # < 10 seconds per test  
  pytest -m e2e       # < 60 seconds per test
  ```

## Key Implementation Rules

1. **Stream, don't buffer** - Use generators for memory efficiency
2. **Validate early** - Catch errors before expensive operations
3. **Degrade gracefully** - Always have a fallback
4. **Pass references** - Move IDs, not data
5. **Declare requirements** - Tools state what they need
6. **Compose via protocol** - MCP provides loose coupling
7. **Track at creation** - Lineage on data, not operations
8. **Plan before executing** - Estimate resources upfront
9. **Test in layers** - Fast unit → integration → e2e
10. **Reify workflows** - Complex analyses become aggregate tools