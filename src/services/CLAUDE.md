# Services Module - CLAUDE.md

## Overview
The `src/services/` directory contains specialized services that provide analytics, monitoring, and utility functionality to the GraphRAG system. These services implement performance optimization, safety gates, and advanced analytics capabilities.

## Services Architecture

### Service Pattern
Services in this directory follow a focused, single-responsibility pattern:
- **AnalyticsService**: Graph analytics with performance and safety gates
- **Future Services**: Additional services for monitoring, caching, etc.

### Performance-First Design
All services prioritize performance and safety:
- **Safety Gates**: Prevent resource exhaustion
- **Performance Monitoring**: Track resource usage
- **Graceful Degradation**: Fallback to approximate methods
- **Memory Management**: Monitor and manage memory usage

## Individual Service Patterns

### AnalyticsService (`analytics_service.py`)
**Purpose**: Graph analytics with performance and safety gates

**Key Patterns**:
- **Safety Gates**: Prevent resource exhaustion on large graphs
- **Performance Optimization**: Use approximate methods for large graphs
- **Memory Management**: Monitor available memory and project usage
- **Graph Analysis**: Analyze graph properties for optimization decisions

**Usage**:
```python
from src.services.analytics_service import AnalyticsService

analytics = AnalyticsService()

# Check if PageRank should be gated
should_gate = analytics.should_gate_pagerank(graph, available_memory_gb=8.0)

# Run PageRank with automatic strategy selection
result = analytics.run_pagerank(graph)
print(f"Method: {result['method']}")
print(f"Nodes processed: {result['nodes_processed']}")
```

**Core Components**:

#### Safety Gate Analysis
```python
def should_gate_pagerank(self, graph: nx.DiGraph, available_memory_gb: float = None) -> bool:
    """Determines if PageRank should use approximate method"""
```

**Gate Criteria**:
- **Size Check**: Gate if > 50,000 nodes
- **Memory Projection**: Gate if projected memory > 50% available
- **Graph Diameter**: Gate if diameter > 15 (slow convergence)
- **Edge Weight Skew**: Gate if skew > 2.0 (convergence issues)
- **Connectivity**: Gate if graph not strongly connected

#### PageRank Strategies
```python
def run_pagerank(self, graph: nx.DiGraph) -> dict:
    """Runs PageRank with appropriate strategy based on gating checks"""
```

**Strategies**:
- **Full PageRank**: Standard NetworkX PageRank for small graphs
- **Approximate PageRank**: Limited iterations with top-K results for large graphs

#### Full PageRank Implementation
```python
def _run_full_pagerank(self, graph: nx.DiGraph, **kwargs) -> dict:
    """Runs the standard, full NetworkX PageRank"""
    scores = nx.pagerank(graph, **kwargs)
    return {
        "method": "full",
        "scores": scores,
        "nodes_processed": graph.number_of_nodes()
    }
```

**Features**:
- **Standard Algorithm**: Uses NetworkX PageRank implementation
- **Complete Results**: Returns scores for all nodes
- **Performance Tracking**: Tracks nodes processed

#### Approximate PageRank Implementation
```python
def _run_approximate_pagerank(self, graph: nx.DiGraph, top_k: int = 1000, **kwargs) -> dict:
    """Runs PageRank with limited iterations and returns only top K results"""
```

**Features**:
- **Limited Iterations**: Max 20 iterations for speed
- **Early Stopping**: Tolerance-based convergence
- **Top-K Results**: Returns only top 1000 results by default
- **Memory Efficient**: Reduces memory usage for large graphs

## Performance Optimization Patterns

### Memory Management
```python
# Memory projection heuristic
projected_memory_gb = (node_count / 1000) * 0.1
if projected_memory_gb > (available_memory_gb * 0.5):
    return True  # Gate the operation
```

**Memory Patterns**:
- **Projection**: Estimate memory usage based on graph size
- **Safety Margin**: Use 50% of available memory as threshold
- **Monitoring**: Use psutil to get actual available memory
- **Heuristics**: ~0.1 GB per 1000 nodes as rough estimate

### Graph Analysis
```python
# Graph diameter check
if node_count > 1000:
    try:
        diameter = nx.diameter(graph)
        if diameter > 15:  # Heuristic threshold
            return True
    except nx.NetworkXError:
        return True  # Graph not connected
```

**Analysis Patterns**:
- **Size Thresholds**: Only analyze graphs above certain sizes
- **Error Handling**: Handle NetworkX errors gracefully
- **Heuristic Thresholds**: Use empirical thresholds for decisions
- **Connectivity Checks**: Ensure graph is strongly connected

### Edge Weight Analysis
```python
# Edge-weight skew check
weights = [data.get('weight', 1.0) for _, _, data in graph.edges(data=True)]
if weights:
    weight_skew = skew(np.array(weights))
    if weight_skew > 2.0:  # Heuristic threshold
        return True
```

**Weight Analysis**:
- **Skew Calculation**: Use scipy.stats.skew for distribution analysis
- **Default Weights**: Use 1.0 as default weight for unweighted edges
- **High Skew Detection**: Identify graphs with convergence issues
- **Threshold-Based**: Use empirical threshold of 2.0

## Common Commands & Workflows

### Development Commands
```bash
# Test analytics service
python -c "from src.services.analytics_service import AnalyticsService; print(AnalyticsService().should_gate_pagerank(nx.DiGraph()))"

# Test with large graph
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.DiGraph([(i, i+1) for i in range(60000)]); print(AnalyticsService().should_gate_pagerank(g))"

# Test PageRank execution
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.DiGraph([(0,1), (1,2), (2,0)]); print(AnalyticsService().run_pagerank(g))"
```

### Performance Testing Commands
```bash
# Test memory projection
python -c "from src.services.analytics_service import AnalyticsService; print(AnalyticsService().should_gate_pagerank(nx.DiGraph(), available_memory_gb=1.0))"

# Test graph diameter analysis
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.path_graph(2000, create_using=nx.DiGraph); print(AnalyticsService().should_gate_pagerank(g))"

# Test edge weight skew
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.DiGraph(); g.add_edge(0,1,weight=0.1); g.add_edge(1,2,weight=10.0); print(AnalyticsService().should_gate_pagerank(g))"
```

### Debugging Commands
```bash
# Check memory usage
python -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available / (1024**3):.2f} GB')"

# Test graph connectivity
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2)]); print(f'Strongly connected: {nx.is_strongly_connected(g)}')"

# Test PageRank convergence
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2), (2,0)]); print(nx.pagerank(g, max_iter=20, tol=1e-4))"
```

## Code Style & Conventions

### Service Design Patterns
- **Single Responsibility**: Each service has one clear purpose
- **Performance First**: Optimize for speed and memory efficiency
- **Safety Gates**: Prevent resource exhaustion
- **Graceful Degradation**: Fallback to approximate methods

### Naming Conventions
- **Service Names**: Use `Service` suffix for service classes
- **Method Names**: Use descriptive names for analysis methods
- **Variable Names**: Use descriptive names for thresholds and parameters
- **Constants**: Use UPPER_CASE for magic numbers and thresholds

### Error Handling Patterns
- **Graceful Degradation**: Fallback to approximate methods
- **Exception Handling**: Handle NetworkX errors gracefully
- **Safety Checks**: Check resources before expensive operations
- **Validation**: Validate inputs before processing

### Logging Patterns
- **Performance Logging**: Log method selection and performance metrics
- **Resource Logging**: Log memory usage and projections
- **Graph Analysis Logging**: Log graph properties and analysis results
- **Error Logging**: Log errors with context and fallback decisions

## Integration Points

### Core Services Integration
- **Service Manager**: Integration with core service manager
- **Logging**: Integration with core logging configuration
- **Configuration**: Integration with core configuration system
- **Error Handling**: Integration with core error handling

### Graph Processing Integration
- **NetworkX**: Primary graph processing library
- **PageRank**: Integration with PageRank algorithms
- **Graph Analysis**: Integration with graph analysis tools
- **Performance Monitoring**: Integration with performance monitoring

### External Dependencies
- **NetworkX**: Graph processing and analysis
- **NumPy**: Numerical computations
- **SciPy**: Statistical analysis (skew calculation)
- **psutil**: System resource monitoring

## Performance Considerations

### Memory Optimization
- **Memory Projection**: Estimate memory usage before operations
- **Top-K Results**: Return only top results for large graphs
- **Limited Iterations**: Use fewer iterations for approximate methods
- **Resource Monitoring**: Monitor available system resources

### Speed Optimization
- **Early Stopping**: Stop iterations when convergence is reached
- **Approximate Methods**: Use faster approximate algorithms
- **Size-Based Decisions**: Choose methods based on graph size
- **Caching**: Cache analysis results when possible

### Safety Optimization
- **Safety Gates**: Prevent resource exhaustion
- **Graceful Degradation**: Fallback to safer methods
- **Resource Limits**: Respect system resource limits
- **Error Recovery**: Recover gracefully from errors

## Testing Patterns

### Unit Testing
- **Service Isolation**: Test each service independently
- **Method Testing**: Test individual analysis methods
- **Threshold Testing**: Test safety gate thresholds
- **Performance Testing**: Test performance characteristics

### Integration Testing
- **Graph Integration**: Test with various graph types
- **Resource Integration**: Test with different resource levels
- **Algorithm Integration**: Test algorithm selection logic
- **Error Integration**: Test error handling and recovery

### Performance Testing
- **Large Graph Testing**: Test with large graphs
- **Memory Testing**: Test memory usage and projections
- **Speed Testing**: Test algorithm execution speed
- **Resource Testing**: Test resource consumption

## Troubleshooting

### Common Issues
1. **Memory Exhaustion**: Reduce graph size or use approximate methods
2. **Slow Convergence**: Check graph diameter and edge weight distribution
3. **NetworkX Errors**: Handle disconnected or invalid graphs
4. **Performance Issues**: Use appropriate algorithm for graph size

### Debug Commands
```bash
# Check graph properties
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2)]); print(f'Nodes: {g.number_of_nodes()}, Edges: {g.number_of_edges()}, Connected: {nx.is_strongly_connected(g)}')"

# Test memory projection
python -c "node_count = 50000; projected_memory = (node_count / 1000) * 0.1; print(f'Projected memory: {projected_memory:.2f} GB')"

# Test edge weight skew
python -c "import numpy as np; from scipy.stats import skew; weights = [0.1, 0.1, 10.0]; print(f'Skew: {skew(np.array(weights)):.2f}')"
```

## Future Service Patterns

### Monitoring Service
- **Performance Monitoring**: Monitor service performance
- **Resource Monitoring**: Monitor system resources
- **Error Monitoring**: Monitor errors and failures
- **Usage Monitoring**: Monitor service usage patterns

### Caching Service
- **Result Caching**: Cache analysis results
- **Graph Caching**: Cache graph representations
- **Memory Caching**: Cache frequently used data
- **Performance Caching**: Cache performance metrics

### Optimization Service
- **Algorithm Selection**: Select optimal algorithms
- **Parameter Tuning**: Tune algorithm parameters
- **Resource Optimization**: Optimize resource usage
- **Performance Optimization**: Optimize performance characteristics 