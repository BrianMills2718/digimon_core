# Task 2.1: Advanced Graph Analytics

**Duration**: Days 11-12 (Week 4)  
**Owner**: Data Science Lead  
**Priority**: HIGH - Core analytical capabilities

## Objective

Implement 7 advanced graph analytics tools that provide deep insights into knowledge graph structure, relationships, and patterns for academic research analysis.

## Tools to Implement

### T69: Community Detection
**Purpose**: Identify clusters of related entities/concepts
**Algorithm**: Louvain community detection
**Input**: Knowledge graph
**Output**: Community assignments with modularity scores

### T70: Graph Centrality Suite  
**Purpose**: Calculate importance metrics for entities
**Algorithms**: Betweenness, closeness, eigenvector centrality
**Input**: Knowledge graph
**Output**: Centrality scores for all nodes

### T71: Similarity Analysis
**Purpose**: Find similar entities based on graph structure
**Algorithm**: Node2Vec embeddings + cosine similarity
**Input**: Graph + target entities
**Output**: Similarity rankings

### T72: Temporal Analysis
**Purpose**: Analyze how relationships change over time
**Algorithm**: Dynamic graph analysis
**Input**: Graph with temporal metadata
**Output**: Evolution patterns

### T73: Anomaly Detection
**Purpose**: Identify unusual patterns or outliers
**Algorithm**: Isolation Forest on graph features
**Input**: Knowledge graph
**Output**: Anomaly scores

### T74: Graph Comparison
**Purpose**: Compare different knowledge graphs
**Algorithm**: Graph edit distance + structural metrics
**Input**: Two graphs
**Output**: Comparison report

### T75: Network Statistics
**Purpose**: Comprehensive graph metrics
**Metrics**: Density, clustering coefficient, diameter
**Input**: Knowledge graph
**Output**: Statistical summary

## Implementation Plan

### Day 11 Morning: Core Analytics (T69, T70, T71)

#### T69: Community Detection Implementation
```python
# File: src/tools/phase2/t69_community_detection.py

from src.core.kgas_tool_interface import KGASTool, ToolMetadata
import networkx as nx
import community.community_louvain as community_louvain
from typing import Dict, Any, Optional, List

class T69CommunityDetection(KGASTool):
    """Community detection using Louvain algorithm"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_id="T69",
            name="Community Detection",
            description="Detect communities in knowledge graphs using Louvain algorithm",
            category="graph_analytics",
            tags=["community", "clustering", "graph", "analysis"]
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize community detection parameters"""
        self.config = config or {}
        self.resolution = self.config.get('resolution', 1.0)
        self.random_state = self.config.get('random_state', 42)
    
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute community detection"""
        try:
            self.ensure_initialized()
            
            # Handle validation mode
            if context and context.get('validation_mode'):
                return self.create_result(
                    status='success',
                    results={'communities': {}, 'modularity': 0.5, 'validation': True}
                )
            
            # Extract graph data
            graph_data = input_data.get('graph', {})
            if not graph_data:
                return self.create_result(
                    status='error',
                    error='Graph data required'
                )
            
            # Convert to NetworkX graph
            G = self._build_networkx_graph(graph_data)
            
            # Detect communities
            communities = community_louvain.best_partition(
                G, 
                resolution=self.resolution,
                random_state=self.random_state
            )
            
            # Calculate modularity
            modularity = community_louvain.modularity(communities, G)
            
            # Group nodes by community
            community_groups = {}
            for node, comm_id in communities.items():
                if comm_id not in community_groups:
                    community_groups[comm_id] = []
                community_groups[comm_id].append(node)
            
            # Calculate community statistics
            community_stats = {}
            for comm_id, nodes in community_groups.items():
                subgraph = G.subgraph(nodes)
                community_stats[comm_id] = {
                    'size': len(nodes),
                    'internal_edges': subgraph.number_of_edges(),
                    'density': nx.density(subgraph) if len(nodes) > 1 else 0
                }
            
            return self.create_result(
                status='success',
                results={
                    'communities': communities,
                    'community_groups': community_groups,
                    'community_stats': community_stats,
                    'modularity': modularity,
                    'num_communities': len(community_groups),
                    'largest_community': max(community_groups.keys(), 
                                           key=lambda x: len(community_groups[x]))
                }
            )
            
        except Exception as e:
            return self.create_result(
                status='error',
                error=f'Community detection failed: {str(e)}'
            )
    
    def _build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        """Convert graph data to NetworkX format"""
        G = nx.Graph()
        
        # Add nodes
        nodes = graph_data.get('nodes', [])
        for node in nodes:
            node_id = node.get('id') or node.get('name')
            G.add_node(node_id, **node)
        
        # Add edges
        edges = graph_data.get('edges', [])
        for edge in edges:
            source = edge.get('source') or edge.get('from')
            target = edge.get('target') or edge.get('to')
            weight = edge.get('weight', 1.0)
            G.add_edge(source, target, weight=weight, **edge)
        
        return G
```

#### T70: Centrality Suite Implementation
```python
# File: src/tools/phase2/t70_centrality_suite.py

from src.core.kgas_tool_interface import KGASTool, ToolMetadata
import networkx as nx
from typing import Dict, Any, Optional

class T70CentralitySuite(KGASTool):
    """Calculate multiple centrality measures"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_id="T70",
            name="Graph Centrality Suite",
            description="Calculate betweenness, closeness, and eigenvector centrality",
            category="graph_analytics", 
            tags=["centrality", "importance", "graph", "metrics"]
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize centrality parameters"""
        self.config = config or {}
        self.measures = self.config.get('measures', ['betweenness', 'closeness', 'eigenvector'])
        self.normalize = self.config.get('normalize', True)
    
    def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate centrality measures"""
        try:
            self.ensure_initialized()
            
            # Handle validation mode
            if context and context.get('validation_mode'):
                return self.create_result(
                    status='success',
                    results={'centrality_scores': {}, 'validation': True}
                )
            
            # Extract graph
            graph_data = input_data.get('graph', {})
            if not graph_data:
                return self.create_result(
                    status='error',
                    error='Graph data required'
                )
            
            G = self._build_networkx_graph(graph_data)
            
            # Calculate centralities
            centrality_results = {}
            
            if 'betweenness' in self.measures:
                centrality_results['betweenness'] = nx.betweenness_centrality(
                    G, normalized=self.normalize
                )
            
            if 'closeness' in self.measures:
                centrality_results['closeness'] = nx.closeness_centrality(
                    G, normalized=self.normalize
                )
            
            if 'eigenvector' in self.measures:
                try:
                    centrality_results['eigenvector'] = nx.eigenvector_centrality(
                        G, max_iter=1000
                    )
                except nx.PowerIterationFailedConvergence:
                    # Fallback to PageRank if eigenvector fails
                    centrality_results['pagerank'] = nx.pagerank(G)
            
            if 'degree' in self.measures:
                centrality_results['degree'] = dict(G.degree())
                if self.normalize:
                    max_degree = max(centrality_results['degree'].values())
                    centrality_results['degree'] = {
                        node: degree / max_degree 
                        for node, degree in centrality_results['degree'].items()
                    }
            
            # Find top nodes for each measure
            top_nodes = {}
            for measure, scores in centrality_results.items():
                sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                top_nodes[measure] = sorted_nodes[:10]  # Top 10
            
            # Calculate summary statistics
            summary_stats = {}
            for measure, scores in centrality_results.items():
                values = list(scores.values())
                summary_stats[measure] = {
                    'mean': sum(values) / len(values),
                    'max': max(values),
                    'min': min(values),
                    'nodes_above_mean': sum(1 for v in values if v > sum(values) / len(values))
                }
            
            return self.create_result(
                status='success',
                results={
                    'centrality_scores': centrality_results,
                    'top_nodes': top_nodes,
                    'summary_stats': summary_stats,
                    'measures_calculated': list(centrality_results.keys()),
                    'graph_info': {
                        'nodes': G.number_of_nodes(),
                        'edges': G.number_of_edges(),
                        'density': nx.density(G)
                    }
                }
            )
            
        except Exception as e:
            return self.create_result(
                status='error',
                error=f'Centrality calculation failed: {str(e)}'
            )
    
    def _build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        """Convert graph data to NetworkX format"""
        # Same implementation as T69
        G = nx.Graph()
        
        nodes = graph_data.get('nodes', [])
        for node in nodes:
            node_id = node.get('id') or node.get('name')
            G.add_node(node_id, **node)
        
        edges = graph_data.get('edges', [])
        for edge in edges:
            source = edge.get('source') or edge.get('from')
            target = edge.get('target') or edge.get('to')
            weight = edge.get('weight', 1.0)
            G.add_edge(source, target, weight=weight, **edge)
        
        return G
```

### Day 11 Afternoon: Complete Remaining Tools (T72-T75)

Following the same pattern, implement:
- T71: Similarity Analysis using Node2Vec
- T72: Temporal Analysis for dynamic graphs
- T73: Anomaly Detection using graph features
- T74: Graph Comparison metrics
- T75: Network Statistics calculator

### Day 12: Testing and Integration

#### Comprehensive Test Suite
```python
# File: tests/phase2/test_graph_analytics.py

import pytest
from src.tools.phase2.t69_community_detection import T69CommunityDetection
from src.tools.phase2.t70_centrality_suite import T70CentralitySuite

class TestGraphAnalytics:
    """Test suite for graph analytics tools"""
    
    @pytest.fixture
    def sample_graph(self):
        """Sample graph for testing"""
        return {
            'nodes': [
                {'id': 'A', 'type': 'concept'},
                {'id': 'B', 'type': 'concept'},
                {'id': 'C', 'type': 'concept'},
                {'id': 'D', 'type': 'concept'},
                {'id': 'E', 'type': 'concept'}
            ],
            'edges': [
                {'source': 'A', 'target': 'B', 'weight': 1.0},
                {'source': 'B', 'target': 'C', 'weight': 1.0},
                {'source': 'C', 'target': 'D', 'weight': 1.0},
                {'source': 'D', 'target': 'E', 'weight': 1.0},
                {'source': 'A', 'target': 'E', 'weight': 0.5}
            ]
        }
    
    def test_community_detection(self, sample_graph):
        """Test community detection tool"""
        tool = T69CommunityDetection()
        tool.initialize()
        
        result = tool.execute({'graph': sample_graph})
        
        assert result['status'] == 'success'
        assert 'communities' in result['results']
        assert 'modularity' in result['results']
        assert isinstance(result['results']['num_communities'], int)
    
    def test_centrality_suite(self, sample_graph):
        """Test centrality calculation tool"""
        tool = T70CentralitySuite()
        tool.initialize()
        
        result = tool.execute({'graph': sample_graph})
        
        assert result['status'] == 'success'
        assert 'centrality_scores' in result['results']
        assert 'betweenness' in result['results']['centrality_scores']
        assert len(result['results']['centrality_scores']['betweenness']) == 5
    
    def test_validation_mode(self, sample_graph):
        """Test validation mode for all tools"""
        tools = [T69CommunityDetection(), T70CentralitySuite()]
        
        for tool in tools:
            tool.initialize()
            result = tool.execute(
                {'graph': sample_graph},
                {'validation_mode': True}
            )
            assert result['status'] == 'success'
            assert result['results']['validation'] is True
```

## Success Criteria

- [ ] All 7 tools implemented and tested
- [ ] Tools work with standard graph formats
- [ ] Performance within acceptable limits (<10s per tool)
- [ ] Integration with existing tool factory
- [ ] Comprehensive test coverage (>90%)

## Deliverables

1. **7 Graph Analytics Tools** (T69-T75)
2. **Test Suite** for all analytics tools  
3. **Performance Benchmarks** for each tool
4. **Integration Examples** showing tool orchestration
5. **Documentation** with usage examples