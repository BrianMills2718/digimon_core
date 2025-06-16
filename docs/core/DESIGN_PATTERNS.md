# Super-Digimon Design Patterns

This document captures design patterns discovered through mock workflow analysis and implementation planning.

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

### Three-Level Identity Pattern
- **Problem**: Same text can refer to different entities; same entity has multiple surface forms
- **Solution**: Track Surface Form → Mention → Entity hierarchy
- **Implementation**:
  ```python
  # Surface form: "Apple"
  mention = Mention(
      id="mention_001",
      surface_text="Apple",
      document_ref="doc_001",
      position=1234,
      context="Apple announced record profits"
  )
  
  # Entity resolution
  entity = Entity(
      id="ent_apple_inc",
      canonical_name="Apple Inc.",
      mention_refs=["mention_001", "mention_002", "mention_003"],
      surface_forms=["Apple", "AAPL", "Apple Computer"]
  )
  ```

### Universal Quality Tracking Pattern
- **Problem**: Quality degradation invisible until final results
- **Solution**: Every object tracks confidence and quality metadata
- **Implementation**:
  ```python
  class QualityTracked:
      def __init__(self, data, confidence=1.0):
          self.data = data
          self.confidence = confidence
          self.quality_tier = self._compute_tier(confidence)
          self.warnings = []
          self.evidence = []
          self.extraction_method = ""
      
      def _compute_tier(self, conf):
          if conf >= 0.8: return "high"
          elif conf >= 0.6: return "medium"
          else: return "low"
  ```

### Format-Agnostic Processing Pattern
- **Problem**: Different analyses need different data structures
- **Solution**: Seamless conversion between Graph ↔ Table ↔ Vector
- **Implementation**:
  ```python
  # Automatic format selection
  def analyze_data(data_ref, analysis_type):
      optimal_format = T117_format_selector(analysis_type, data_ref)
      
      if optimal_format == "table":
          table_ref = T115_graph_to_table(data_ref)
          return statistical_analysis(table_ref)
      elif optimal_format == "graph":
          return graph_algorithm(data_ref)
      else:  # vector
          return similarity_search(data_ref)
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

### Partial Results Pattern
- **Problem**: All-or-nothing processing loses valuable partial work
- **Solution**: Always return what succeeded, failed, and partially completed
- **Implementation**:
  ```python
  def process_documents(doc_refs):
      results = {
          "successful": [],
          "failed": [],
          "partial": [],
          "summary": {}
      }
      
      for doc_ref in doc_refs:
          try:
              result = process_document(doc_ref)
              results["successful"].append(result)
          except PartialProcessingError as e:
              results["partial"].append({
                  "doc_ref": doc_ref,
                  "completed_steps": e.completed,
                  "failed_at": e.failed_step
              })
          except Exception as e:
              results["failed"].append({
                  "doc_ref": doc_ref,
                  "error": str(e)
              })
      
      results["summary"] = {
          "total": len(doc_refs),
          "successful": len(results["successful"]),
          "failed": len(results["failed"]),
          "partial": len(results["partial"])
      }
      return results
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

## Advanced Patterns

### Confidence Propagation Pattern
- **Problem**: Uncertainty compounds through pipeline but isn't tracked
- **Solution**: Propagate confidence with operation-specific rules
- **Implementation**:
  ```python
  class ConfidencePropagator:
      def propagate(self, upstream_scores, operation_type):
          if operation_type == "extraction":
              # Extraction reduces confidence
              return min(upstream_scores) * 0.95
          elif operation_type == "aggregation":
              # Aggregation averages confidence
              return sum(upstream_scores) / len(upstream_scores)
          elif operation_type == "filtering":
              # Filtering preserves best confidence
              return max(upstream_scores)
          elif operation_type == "inference":
              # Inference compounds uncertainty
              return min(upstream_scores) * 0.85
  ```

### Versioning Pattern
- **Problem**: Changes break reproducibility and knowledge evolves
- **Solution**: Four-level versioning system
- **Implementation**:
  ```python
  class Versioned:
      def __init__(self):
          self.schema_version = "1.0"  # Data structure version
          self.data_version = 1        # Content version
          self.graph_version = None    # Graph snapshot version
          self.analysis_version = None # Analysis result version
      
      def create_version(self, level):
          if level == "data":
              self.data_version += 1
              self.invalidate_downstream()
  ```

### Reference Resolution Pattern
- **Problem**: Tools need data but shouldn't load everything
- **Solution**: Lazy loading through reference resolution
- **Implementation**:
  ```python
  class ReferenceResolver:
      def resolve(self, ref: str, fields: List[str] = None):
          # Parse reference type
          storage, type, id = ref.split("://")[1].split("/")
          
          # Load only requested fields
          if storage == "neo4j":
              return self.neo4j.get_partial(type, id, fields)
          elif storage == "sqlite":
              return self.sqlite.get_partial(type, id, fields)
          
      def resolve_batch(self, refs: List[str], fields: List[str] = None):
          # Group by storage for efficiency
          by_storage = defaultdict(list)
          for ref in refs:
              storage = ref.split("://")[1].split("/")[0]
              by_storage[storage].append(ref)
          
          # Batch load from each storage
          results = {}
          for storage, storage_refs in by_storage.items():
              results.update(self.batch_load(storage, storage_refs, fields))
          return results
  ```

### Tool Variant Selection Pattern
- **Problem**: Multiple tool variants (fast/cheap vs slow/accurate)
- **Solution**: Agent-driven selection based on context
- **Implementation**:
  ```python
  class ToolSelector:
      def select_variant(self, tool_base: str, context: dict) -> str:
          if tool_base == "T23":  # Entity extraction
              if context.get("volume") > 10000:
                  return "T23a"  # Fast spaCy variant
              elif context.get("domain") == "specialized":
                  return "T23b"  # LLM variant for custom entities
              else:
                  # Let agent decide based on quality needs
                  return None  # Agent will choose
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