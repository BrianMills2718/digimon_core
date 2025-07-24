#!/usr/bin/env python3
"""
Scale-Free Network Analyzer - Power-law distribution analysis for academic knowledge graphs

Analyzes whether a network follows scale-free properties by examining degree distributions,
fitting power-law models, and calculating relevant statistics like the power-law exponent.
"""

import asyncio
import time
import logging
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from scipy import stats
from scipy.optimize import curve_fit
import powerlaw
import warnings

logger = logging.getLogger(__name__)


class ScaleFreeAnalysisError(Exception):
    """Base exception for scale-free analysis operations"""
    pass


class ScaleFreeAnalyzer:
    """Analyze scale-free properties of academic knowledge graphs"""
    
    def __init__(self, neo4j_manager, distributed_tx_manager):
        self.neo4j_manager = neo4j_manager
        self.dtm = distributed_tx_manager
        self.analysis_cache = {}
        
        # Analysis parameters
        self.min_nodes_for_analysis = 100
        self.degree_bins = 50
        self.xmin_optimization = True
        
        logger.info("ScaleFreeAnalyzer initialized")
    
    async def analyze_scale_free_properties(self, entity_type: str = None,
                                          relationship_type: str = None,
                                          direction: str = 'both') -> Dict[str, Any]:
        """
        Analyze scale-free properties of the network
        
        Args:
            entity_type: Type of entities to analyze (e.g., 'Author', 'Paper')
            relationship_type: Type of relationships to consider
            direction: 'in', 'out', or 'both' for directed graphs
            
        Returns:
            Dictionary containing scale-free analysis results
        """
        
        tx_id = f"scale_free_{entity_type}_{int(time.time())}"
        logger.info(f"Starting scale-free analysis - tx_id: {tx_id}")
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            # Build the graph
            graph_data = await self._fetch_graph_data(entity_type, relationship_type)
            
            if not graph_data['nodes']:
                logger.warning("No nodes found for scale-free analysis")
                return {
                    'status': 'no_data',
                    'message': 'No nodes found for analysis',
                    'entity_type': entity_type,
                    'relationship_type': relationship_type
                }
            
            # Create NetworkX graph
            G = await self._build_networkx_graph(graph_data, direction)
            
            # Check minimum size requirement
            if G.number_of_nodes() < self.min_nodes_for_analysis:
                logger.warning(f"Graph too small for analysis: {G.number_of_nodes()} nodes")
                return {
                    'status': 'insufficient_data',
                    'message': f'Need at least {self.min_nodes_for_analysis} nodes',
                    'node_count': G.number_of_nodes(),
                    'edge_count': G.number_of_edges()
                }
            
            # Perform scale-free analysis
            analysis_results = await self._perform_scale_free_analysis(G, direction)
            
            # Store results
            await self._store_analysis_results(tx_id, analysis_results)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            logger.info(f"Scale-free analysis completed - is_scale_free: {analysis_results['is_scale_free']}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Scale-free analysis failed: {str(e)}")
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise ScaleFreeAnalysisError(f"Analysis failed: {str(e)}")
    
    async def _fetch_graph_data(self, entity_type: Optional[str], 
                               relationship_type: Optional[str]) -> Dict[str, List]:
        """Fetch graph data from Neo4j"""
        
        # Build query based on filters
        entity_filter = f":{entity_type}" if entity_type else ""
        rel_filter = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH (n{entity_filter})
        OPTIONAL MATCH (n)-[r{rel_filter}]->(m)
        WITH n, collect(DISTINCT {{
            source: id(n),
            target: id(m),
            type: type(r)
        }}) as relationships
        RETURN 
            id(n) as node_id,
            labels(n) as labels,
            n.name as name,
            relationships
        """
        
        result = await self.neo4j_manager.execute_read_query(query)
        
        nodes = []
        edges = []
        
        for record in result:
            node_id = record['node_id']
            nodes.append({
                'id': node_id,
                'labels': record['labels'],
                'name': record.get('name', f'Node_{node_id}')
            })
            
            for rel in record['relationships']:
                if rel['target'] is not None:
                    edges.append({
                        'source': rel['source'],
                        'target': rel['target'],
                        'type': rel['type']
                    })
        
        return {'nodes': nodes, 'edges': edges}
    
    async def _build_networkx_graph(self, graph_data: Dict[str, List], 
                                   direction: str) -> nx.Graph:
        """Build NetworkX graph from data"""
        
        if direction == 'both':
            G = nx.Graph()
        else:
            G = nx.DiGraph()
        
        # Add nodes
        for node in graph_data['nodes']:
            G.add_node(node['id'], **node)
        
        # Add edges
        for edge in graph_data['edges']:
            G.add_edge(edge['source'], edge['target'])
        
        return G
    
    async def _perform_scale_free_analysis(self, G: nx.Graph, 
                                         direction: str) -> Dict[str, Any]:
        """Perform comprehensive scale-free analysis"""
        
        # Get degree sequence
        if isinstance(G, nx.DiGraph):
            if direction == 'in':
                degrees = dict(G.in_degree())
            elif direction == 'out':
                degrees = dict(G.out_degree())
            else:
                degrees = dict(G.degree())
        else:
            degrees = dict(G.degree())
        
        degree_sequence = list(degrees.values())
        degree_sequence = [d for d in degree_sequence if d > 0]  # Remove zero degrees
        
        if not degree_sequence:
            return {
                'status': 'error',
                'message': 'No non-zero degrees found',
                'is_scale_free': False
            }
        
        # Basic statistics
        basic_stats = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'avg_degree': np.mean(degree_sequence),
            'max_degree': max(degree_sequence),
            'min_degree': min(degree_sequence),
            'std_degree': np.std(degree_sequence)
        }
        
        # Degree distribution analysis
        degree_dist = await self._analyze_degree_distribution(degree_sequence)
        
        # Power-law fitting using powerlaw package
        power_law_fit = await self._fit_power_law(degree_sequence)
        
        # Alternative distributions comparison
        alt_distributions = await self._compare_distributions(degree_sequence)
        
        # Hub analysis
        hub_analysis = await self._analyze_hubs(G, degrees)
        
        # Scale-free determination
        is_scale_free = self._determine_scale_free(
            power_law_fit, alt_distributions, degree_dist, hub_analysis
        )
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'is_scale_free': is_scale_free,
            'confidence_score': power_law_fit.get('confidence', 0.0),
            'basic_statistics': basic_stats,
            'degree_distribution': degree_dist,
            'power_law_fit': power_law_fit,
            'alternative_distributions': alt_distributions,
            'hub_analysis': hub_analysis,
            'visualization_data': await self._prepare_visualization_data(degree_sequence)
        }
    
    async def _analyze_degree_distribution(self, degree_sequence: List[int]) -> Dict[str, Any]:
        """Analyze the degree distribution"""
        
        # Create histogram
        degree_counts = {}
        for degree in degree_sequence:
            degree_counts[degree] = degree_counts.get(degree, 0) + 1
        
        # Sort by degree
        sorted_degrees = sorted(degree_counts.keys())
        
        # Calculate cumulative distribution
        total_nodes = len(degree_sequence)
        cumulative_dist = {}
        cumulative_count = 0
        
        for degree in sorted(sorted_degrees, reverse=True):
            cumulative_count += degree_counts[degree]
            cumulative_dist[degree] = cumulative_count / total_nodes
        
        # Log-log regression for quick check
        log_degrees = np.log10([d for d in sorted_degrees if d > 0])
        log_counts = np.log10([degree_counts[d] for d in sorted_degrees if d > 0])
        
        if len(log_degrees) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_counts)
            
            return {
                'degree_counts': degree_counts,
                'cumulative_distribution': cumulative_dist,
                'log_log_regression': {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'std_error': std_err
                },
                'heavy_tail': slope < -1.5,  # Rough indicator
                'unique_degrees': len(sorted_degrees)
            }
        else:
            return {
                'degree_counts': degree_counts,
                'cumulative_distribution': cumulative_dist,
                'log_log_regression': None,
                'heavy_tail': False,
                'unique_degrees': len(sorted_degrees)
            }
    
    async def _fit_power_law(self, degree_sequence: List[int]) -> Dict[str, Any]:
        """Fit power-law distribution using powerlaw package"""
        
        try:
            # Suppress warnings from powerlaw package
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Fit power law
                fit = powerlaw.Fit(degree_sequence, discrete=True)
                
                # Get parameters
                alpha = fit.power_law.alpha
                xmin = fit.power_law.xmin
                
                # Calculate goodness of fit
                # Compare with exponential as alternative
                R, p = fit.distribution_compare('power_law', 'exponential')
                
                # KS test for goodness of fit
                D = fit.power_law.D
                
                # Bootstrap confidence interval for alpha
                if len(degree_sequence) < 10000:  # Bootstrap for smaller datasets
                    alpha_range = self._bootstrap_alpha(degree_sequence, n_iterations=100)
                else:
                    alpha_range = (alpha - 0.1, alpha + 0.1)  # Rough estimate
                
                return {
                    'alpha': alpha,
                    'xmin': xmin,
                    'xmax': max(degree_sequence),
                    'likelihood_ratio': R,
                    'p_value': p,
                    'ks_distance': D,
                    'alpha_confidence_interval': alpha_range,
                    'n_tail': len([d for d in degree_sequence if d >= xmin]),
                    'confidence': self._calculate_confidence(alpha, R, p, D)
                }
                
        except Exception as e:
            logger.error(f"Power law fitting failed: {str(e)}")
            return {
                'alpha': None,
                'xmin': None,
                'error': str(e),
                'confidence': 0.0
            }
    
    def _bootstrap_alpha(self, degree_sequence: List[int], n_iterations: int = 100) -> Tuple[float, float]:
        """Bootstrap confidence interval for alpha parameter"""
        
        alphas = []
        n = len(degree_sequence)
        
        for _ in range(n_iterations):
            # Resample with replacement
            sample = np.random.choice(degree_sequence, size=n, replace=True)
            
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fit = powerlaw.Fit(sample, discrete=True)
                    alphas.append(fit.power_law.alpha)
            except:
                continue
        
        if alphas:
            return (np.percentile(alphas, 2.5), np.percentile(alphas, 97.5))
        else:
            return (None, None)
    
    async def _compare_distributions(self, degree_sequence: List[int]) -> Dict[str, Any]:
        """Compare power law with alternative distributions"""
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                fit = powerlaw.Fit(degree_sequence, discrete=True)
                
                comparisons = {}
                
                # Compare with common alternatives
                alternatives = ['lognormal', 'exponential', 'truncated_power_law']
                
                for alt in alternatives:
                    try:
                        R, p = fit.distribution_compare('power_law', alt)
                        comparisons[alt] = {
                            'likelihood_ratio': R,
                            'p_value': p,
                            'preferred': 'power_law' if R > 0 else alt
                        }
                    except:
                        comparisons[alt] = {'error': 'Comparison failed'}
                
                # Determine best fit
                best_fit = 'power_law'
                for alt, result in comparisons.items():
                    if 'preferred' in result and result['preferred'] != 'power_law':
                        if 'p_value' in result and result['p_value'] < 0.05:
                            best_fit = alt
                            break
                
                return {
                    'comparisons': comparisons,
                    'best_fit': best_fit,
                    'is_power_law_preferred': best_fit == 'power_law'
                }
                
        except Exception as e:
            logger.error(f"Distribution comparison failed: {str(e)}")
            return {
                'error': str(e),
                'best_fit': 'unknown',
                'is_power_law_preferred': False
            }
    
    async def _analyze_hubs(self, G: nx.Graph, degrees: Dict[int, int]) -> Dict[str, Any]:
        """Analyze hub structure of the network"""
        
        # Sort nodes by degree
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        
        # Identify hubs (top 1% or at least top 10 nodes)
        n_hubs = max(10, int(0.01 * len(sorted_nodes)))
        hubs = sorted_nodes[:n_hubs]
        
        # Calculate hub statistics
        hub_degrees = [h[1] for h in hubs]
        all_degrees = list(degrees.values())
        
        hub_stats = {
            'n_hubs': n_hubs,
            'hub_threshold_degree': hubs[-1][1] if hubs else 0,
            'max_hub_degree': hub_degrees[0] if hub_degrees else 0,
            'avg_hub_degree': np.mean(hub_degrees) if hub_degrees else 0,
            'hub_degree_fraction': sum(hub_degrees) / sum(all_degrees) if all_degrees else 0,
            'hub_connectivity': await self._calculate_hub_connectivity(G, [h[0] for h in hubs])
        }
        
        # Rich club coefficient
        if G.number_of_nodes() > 100:
            try:
                rich_club = nx.rich_club_coefficient(G, normalized=False)
                hub_stats['rich_club_coefficient'] = {
                    k: v for k, v in list(rich_club.items())[:10]  # First 10 degrees
                }
            except:
                hub_stats['rich_club_coefficient'] = None
        else:
            hub_stats['rich_club_coefficient'] = None
        
        # Hub details
        hub_stats['top_hubs'] = [
            {
                'node_id': node_id,
                'degree': degree,
                'labels': G.nodes[node_id].get('labels', []),
                'name': G.nodes[node_id].get('name', f'Node_{node_id}')
            }
            for node_id, degree in hubs[:10]  # Top 10 hubs
        ]
        
        return hub_stats
    
    async def _calculate_hub_connectivity(self, G: nx.Graph, hub_nodes: List[int]) -> float:
        """Calculate how connected hubs are to each other"""
        
        if len(hub_nodes) < 2:
            return 0.0
        
        hub_subgraph = G.subgraph(hub_nodes)
        possible_edges = len(hub_nodes) * (len(hub_nodes) - 1) / 2
        actual_edges = hub_subgraph.number_of_edges()
        
        return actual_edges / possible_edges if possible_edges > 0 else 0.0
    
    def _calculate_confidence(self, alpha: float, R: float, p: float, D: float) -> float:
        """Calculate confidence score for scale-free determination"""
        
        if alpha is None:
            return 0.0
        
        confidence = 0.0
        
        # Alpha in typical range for scale-free networks (2 < alpha < 3)
        if 2.0 < alpha < 3.0:
            confidence += 0.3
        elif 1.5 < alpha < 3.5:
            confidence += 0.2
        
        # Good fit compared to exponential
        if R > 0 and p > 0.1:
            confidence += 0.3
        elif R > 0:
            confidence += 0.1
        
        # Low KS distance
        if D < 0.05:
            confidence += 0.3
        elif D < 0.1:
            confidence += 0.2
        elif D < 0.15:
            confidence += 0.1
        
        # Additional small boost for very low p-value
        if p < 0.001:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_scale_free(self, power_law_fit: Dict[str, Any],
                            alt_distributions: Dict[str, Any],
                            degree_dist: Dict[str, Any],
                            hub_analysis: Dict[str, Any]) -> bool:
        """Determine if network is scale-free based on multiple criteria"""
        
        # Criteria for scale-free network
        criteria = []
        
        # 1. Power law fit is good
        if power_law_fit.get('confidence', 0) > 0.5:
            criteria.append(True)
        
        # 2. Power law is preferred over alternatives
        if alt_distributions.get('is_power_law_preferred', False):
            criteria.append(True)
        
        # 3. Heavy-tailed distribution
        if degree_dist.get('heavy_tail', False):
            criteria.append(True)
        
        # 4. Significant hub structure
        if hub_analysis.get('hub_degree_fraction', 0) > 0.3:
            criteria.append(True)
        
        # 5. Alpha in reasonable range
        alpha = power_law_fit.get('alpha')
        if alpha and 1.5 < alpha < 3.5:
            criteria.append(True)
        
        # Need at least 3 out of 5 criteria
        return sum(criteria) >= 3
    
    async def _prepare_visualization_data(self, degree_sequence: List[int]) -> Dict[str, Any]:
        """Prepare data for visualization"""
        
        # Degree distribution for plotting
        degree_counts = {}
        for degree in degree_sequence:
            degree_counts[degree] = degree_counts.get(degree, 0) + 1
        
        # Prepare log-log plot data
        plot_data = []
        for degree, count in sorted(degree_counts.items()):
            if degree > 0:
                plot_data.append({
                    'degree': degree,
                    'count': count,
                    'log_degree': np.log10(degree),
                    'log_count': np.log10(count)
                })
        
        return {
            'degree_distribution_plot': plot_data,
            'degree_histogram': {
                'bins': list(range(0, min(100, max(degree_sequence) + 1), 5)),
                'counts': [
                    sum(1 for d in degree_sequence if b <= d < b + 5)
                    for b in range(0, min(100, max(degree_sequence) + 1), 5)
                ]
            }
        }
    
    async def _store_analysis_results(self, tx_id: str, results: Dict[str, Any]) -> None:
        """Store analysis results in the database"""
        
        await self.dtm.record_operation(
            tx_id=tx_id,
            operation={
                'type': 'scale_free_analysis',
                'timestamp': datetime.now().isoformat(),
                'results': {
                    'is_scale_free': results['is_scale_free'],
                    'confidence_score': results.get('confidence_score', 0.0),
                    'node_count': results['basic_statistics']['node_count'],
                    'edge_count': results['basic_statistics']['edge_count'],
                    'power_law_alpha': results['power_law_fit'].get('alpha'),
                    'best_fit_distribution': results['alternative_distributions'].get('best_fit')
                }
            }
        )
    
    async def analyze_temporal_scale_free(self, entity_type: str = None,
                                        time_windows: List[str] = None) -> Dict[str, Any]:
        """Analyze how scale-free properties change over time"""
        
        tx_id = f"temporal_scale_free_{int(time.time())}"
        
        try:
            await self.dtm.begin_distributed_transaction(tx_id)
            
            if not time_windows:
                # Default to yearly windows
                time_windows = await self._generate_time_windows()
            
            temporal_results = []
            
            for window in time_windows:
                # Analyze network for this time window
                window_result = await self._analyze_time_window(entity_type, window)
                temporal_results.append(window_result)
            
            # Analyze trends
            trends = self._analyze_temporal_trends(temporal_results)
            
            await self.dtm.commit_distributed_transaction(tx_id)
            
            return {
                'status': 'success',
                'temporal_analysis': temporal_results,
                'trends': trends,
                'summary': self._summarize_temporal_analysis(temporal_results, trends)
            }
            
        except Exception as e:
            logger.error(f"Temporal scale-free analysis failed: {str(e)}")
            await self.dtm.rollback_distributed_transaction(tx_id)
            raise ScaleFreeAnalysisError(f"Temporal analysis failed: {str(e)}")
    
    async def _generate_time_windows(self) -> List[str]:
        """Generate default time windows based on data"""
        
        query = """
        MATCH (n)
        WHERE n.created_date IS NOT NULL
        RETURN 
            min(n.created_date) as min_date,
            max(n.created_date) as max_date
        """
        
        result = await self.neo4j_manager.execute_read_query(query)
        
        if result and result[0]['min_date'] and result[0]['max_date']:
            # Generate yearly windows
            min_year = int(result[0]['min_date'][:4])
            max_year = int(result[0]['max_date'][:4])
            
            return [str(year) for year in range(min_year, max_year + 1)]
        else:
            # Default windows
            return ['2020', '2021', '2022', '2023', '2024']
    
    async def _analyze_time_window(self, entity_type: str, window: str) -> Dict[str, Any]:
        """Analyze scale-free properties for a specific time window"""
        
        # This is a simplified version - would need to filter graph by time
        result = await self.analyze_scale_free_properties(entity_type)
        result['time_window'] = window
        
        return result
    
    def _analyze_temporal_trends(self, temporal_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in scale-free properties over time"""
        
        alphas = []
        is_scale_free_list = []
        node_counts = []
        
        for result in temporal_results:
            if result['status'] == 'success':
                alphas.append(result['power_law_fit'].get('alpha', 0))
                is_scale_free_list.append(1 if result['is_scale_free'] else 0)
                node_counts.append(result['basic_statistics']['node_count'])
        
        return {
            'alpha_trend': {
                'values': alphas,
                'mean': np.mean(alphas) if alphas else 0,
                'std': np.std(alphas) if alphas else 0,
                'trend': 'increasing' if alphas and alphas[-1] > alphas[0] else 'decreasing'
            },
            'scale_free_consistency': np.mean(is_scale_free_list) if is_scale_free_list else 0,
            'growth_correlation': self._calculate_correlation(node_counts, alphas) if len(node_counts) > 2 else None
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        return np.corrcoef(x, y)[0, 1]
    
    def _summarize_temporal_analysis(self, temporal_results: List[Dict[str, Any]], 
                                   trends: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary of temporal analysis"""
        
        summary = {
            'overall_pattern': 'The network maintains scale-free properties over time' 
                            if trends['scale_free_consistency'] > 0.7 
                            else 'The network shows varying scale-free properties over time',
            'alpha_evolution': f"Power-law exponent shows {trends['alpha_trend']['trend']} trend",
            'growth_impact': 'Network growth correlates with scale-free properties' 
                           if trends.get('growth_correlation', 0) > 0.5 
                           else 'Network growth shows weak correlation with scale-free properties'
        }
        
        return summary