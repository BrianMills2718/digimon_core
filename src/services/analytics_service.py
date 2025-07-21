import networkx as nx
import psutil
import numpy as np
from scipy.stats import skew

class AnalyticsService:
    """
    A service for running graph analytics with performance and safety gates.
    """

    def should_gate_pagerank(
        self, 
        graph: nx.DiGraph, 
        available_memory_gb: float = None
    ) -> bool:
        """
        Determines if a full PageRank calculation should be gated based on
        graph size, diameter, edge-weight skew, and available memory.
        
        Returns True if the operation should be gated (i.e., run an approximate version).
        """
        if not available_memory_gb:
            available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)

        node_count = graph.number_of_nodes()
        
        # 1. Simple size check (from original implementation)
        if node_count > 50000:
            return True

        # 2. Memory projection check (from original implementation)
        # Assuming ~0.1 GB per 1000 nodes as a rough heuristic
        projected_memory_gb = (node_count / 1000) * 0.1
        if projected_memory_gb > (available_memory_gb * 0.5):
            return True

        # 3. Graph Diameter Check (New)
        # For large graphs, diameter calculation is slow. We approximate it.
        # If the graph is not strongly connected, diameter is infinite.
        if not nx.is_strongly_connected(graph):
            return True # Disconnected graphs can have poor convergence
        
        # A high diameter suggests PageRank will require more iterations.
        # We check this only for reasonably sized graphs to avoid slow checks.
        if node_count > 1000:
            try:
                # approximation of diameter is much faster
                diameter = nx.diameter(graph)
                if diameter > 15: # Heuristic threshold
                    return True
            except nx.NetworkXError:
                # Graph is not connected, which we already handled, but as a safeguard.
                return True

        # 4. Edge-Weight Skew Check (New)
        weights = [data.get('weight', 1.0) for _, _, data in graph.edges(data=True)]
        if weights:
            weight_skew = skew(np.array(weights))
            # High positive skew means many low-weight edges and a few very high-weight edges,
            # which can slow down convergence.
            if weight_skew > 2.0: # Heuristic threshold
                return True

        return False

    def run_pagerank(self, graph: nx.DiGraph) -> dict:
        """
        Runs PageRank with an appropriate strategy (full or approximate) based on gating checks.
        """
        if self.should_gate_pagerank(graph):
            # Use approximate PageRank for large or complex graphs
            return self._run_approximate_pagerank(graph)
        else:
            # Use full PageRank for smaller, well-behaved graphs
            return self._run_full_pagerank(graph)

    def _run_full_pagerank(self, graph: nx.DiGraph, **kwargs) -> dict:
        """Runs the standard, full NetworkX PageRank."""
        scores = nx.pagerank(graph, **kwargs)
        return {
            "method": "full",
            "scores": scores,
            "nodes_processed": graph.number_of_nodes()
        }

    def _run_approximate_pagerank(self, graph: nx.DiGraph, top_k: int = 1000, **kwargs) -> dict:
        """Runs PageRank with limited iterations and returns only the top K results."""
        # Power iteration with early stopping
        scores = nx.pagerank(graph, max_iter=20, tol=1e-4, **kwargs)
        
        # Return top-k results
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {
            "method": "approximate",
            "scores": dict(sorted_scores[:top_k]),
            "nodes_processed": graph.number_of_nodes()
        } 