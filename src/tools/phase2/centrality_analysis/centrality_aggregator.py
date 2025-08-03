"""Centrality Results Aggregator

Aggregates and formats centrality analysis results for output.
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from datetime import datetime

from .centrality_data_models import CentralityResult, CentralityStats
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityResultsAggregator:
    """Aggregate and format centrality analysis results"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
    
    def store_centrality_results(self, all_scores: Dict[str, Dict[str, float]], 
                                source_document: str = "unknown") -> Dict[str, Any]:
        """Store centrality results in Neo4j database"""
        try:
            if not self.service_manager or not hasattr(self.service_manager, 'neo4j_service'):
                logger.warning("Neo4j service not available for storing results")
                return {"stored": False, "reason": "Neo4j service not available"}
            
            neo4j_service = self.service_manager.neo4j_service
            stored_count = 0
            
            with neo4j_service.get_driver().session() as session:
                # Store centrality analysis metadata
                session.run("""
                    MERGE (analysis:CentralityAnalysis {document_id: $doc_id, timestamp: $timestamp})
                    SET analysis.metrics_calculated = $metrics,
                        analysis.analysis_date = $analysis_date,
                        analysis.total_nodes = $total_nodes
                """, {
                    "doc_id": source_document,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": list(all_scores.keys()),
                    "analysis_date": datetime.now().date().isoformat(),
                    "total_nodes": len(next(iter(all_scores.values()), {}))
                })
                
                # Store centrality scores for each node
                for metric, scores in all_scores.items():
                    for node_id, score in scores.items():
                        try:
                            session.run("""
                                MATCH (analysis:CentralityAnalysis {document_id: $doc_id})
                                MERGE (node:Node {entity_id: $node_id})
                                MERGE (centrality:CentralityScore {
                                    node_id: $node_id,
                                    metric: $metric,
                                    analysis_id: $doc_id
                                })
                                SET centrality.score = $score,
                                    centrality.calculated_at = $timestamp
                                MERGE (analysis)-[:HAS_CENTRALITY_SCORE]->(centrality)
                                MERGE (centrality)-[:SCORE_FOR]->(node)
                            """, {
                                "doc_id": source_document,
                                "node_id": node_id,
                                "metric": metric,
                                "score": score,
                                "timestamp": datetime.now().isoformat()
                            })
                            stored_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to store centrality score for {node_id}: {e}")
                            continue
                
                logger.info(f"Stored {stored_count} centrality scores in Neo4j")
                return {
                    "stored": True,
                    "count": stored_count,
                    "metrics": list(all_scores.keys())
                }
                
        except Exception as e:
            logger.error(f"Failed to store centrality results: {e}")
            return {"stored": False, "reason": str(e)}
    
    def format_centrality_output(self, results: List[CentralityResult], 
                               stats: CentralityStats, 
                               output_format: str, 
                               confidence_score: float) -> Dict[str, Any]:
        """Format centrality analysis output"""
        try:
            if output_format == "academic":
                return self._format_academic_output(results, stats, confidence_score)
            elif output_format == "summary":
                return self._format_summary_output(results, stats)
            elif output_format == "detailed":
                return self._format_detailed_output(results, stats, confidence_score)
            else:
                return self._format_standard_output(results, stats)
                
        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_academic_output(self, results: List[CentralityResult], 
                               stats: CentralityStats, 
                               confidence_score: float) -> Dict[str, Any]:
        """Format output for academic research"""
        try:
            academic_output = {
                "research_summary": {
                    "analysis_type": "Comprehensive Centrality Analysis",
                    "methodological_approach": self._describe_methodology(results),
                    "key_findings": self._extract_key_findings(results, stats),
                    "statistical_reliability": self._assess_statistical_reliability(stats)
                },
                "quantitative_results": {
                    "centrality_metrics": {
                        result.metric: {
                            "node_count": result.node_count,
                            "calculation_time": result.calculation_time,
                            "top_nodes": sorted(result.normalized_scores.items(), 
                                              key=lambda x: x[1], reverse=True)[:10]
                        }
                        for result in results if result.scores
                    },
                    "correlation_analysis": stats.correlation_matrix,
                    "graph_properties": stats.graph_statistics
                },
                "data_quality_assessment": {
                    "confidence_score": confidence_score,
                    "calculation_success_rate": len([r for r in results if r.scores]) / len(results) if results else 0,
                    "graph_characteristics": self._assess_graph_characteristics(stats.graph_statistics),
                    "methodological_considerations": self._identify_methodological_considerations(results, stats)
                },
                "comparative_analysis": {
                    "metric_agreements": self._analyze_metric_agreements(stats.correlation_matrix),
                    "consensus_ranking": stats.top_nodes_by_metric.get("consensus", [])[:20],
                    "centrality_diversity": self._assess_centrality_diversity(results)
                },
                "recommendations": {
                    "interpretation_guidelines": self._provide_interpretation_guidelines(results, stats),
                    "further_analysis_suggestions": self._suggest_further_analysis(results, stats)
                }
            }
            
            return academic_output
            
        except Exception as e:
            logger.error(f"Academic output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_summary_output(self, results: List[CentralityResult], 
                              stats: CentralityStats) -> Dict[str, Any]:
        """Format summary output"""
        try:
            summary = {
                "overview": {
                    "metrics_calculated": len(results),
                    "successful_calculations": len([r for r in results if r.scores]),
                    "total_nodes_analyzed": max((r.node_count for r in results), default=0),
                    "total_calculation_time": sum(r.calculation_time for r in results)
                },
                "top_nodes_summary": {
                    metric: nodes[:5]  # Top 5 nodes per metric
                    for metric, nodes in stats.top_nodes_by_metric.items()
                },
                "correlation_summary": {
                    "highest_correlation": self._find_highest_correlation(stats.correlation_matrix),
                    "lowest_correlation": self._find_lowest_correlation(stats.correlation_matrix),
                    "average_correlation": self._calculate_average_correlation(stats.correlation_matrix)
                },
                "graph_summary": {
                    "nodes": stats.graph_statistics.get("nodes", 0),
                    "edges": stats.graph_statistics.get("edges", 0),
                    "density": stats.graph_statistics.get("density", 0),
                    "connectivity": self._summarize_connectivity(stats.graph_statistics)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_detailed_output(self, results: List[CentralityResult], 
                               stats: CentralityStats, 
                               confidence_score: float) -> Dict[str, Any]:
        """Format detailed output with all information"""
        try:
            detailed_output = {
                "complete_results": {
                    "centrality_results": [result.to_dict() for result in results],
                    "statistics": stats.to_dict(),
                    "confidence_score": confidence_score
                },
                "analysis_metadata": {
                    "calculation_summary": {
                        "total_metrics": len(results),
                        "successful_metrics": len([r for r in results if r.scores]),
                        "failed_metrics": len([r for r in results if not r.scores]),
                        "total_runtime": sum(r.calculation_time for r in results)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "graph_preparation_notes": self._generate_preparation_notes(results)
                },
                "visualization_data": {
                    "node_rankings": self._prepare_visualization_rankings(results),
                    "correlation_heatmap_data": self._prepare_correlation_heatmap(stats.correlation_matrix),
                    "centrality_distributions": self._prepare_distribution_data(results)
                },
                "export_options": {
                    "formats_available": ["json", "csv", "graphml", "neo4j"],
                    "visualization_ready": True,
                    "research_ready": True
                }
            }
            
            return detailed_output
            
        except Exception as e:
            logger.error(f"Detailed output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_standard_output(self, results: List[CentralityResult], 
                               stats: CentralityStats) -> Dict[str, Any]:
        """Format standard output"""
        return {
            "centrality_results": [result.to_dict() for result in results],
            "statistics": stats.to_dict(),
            "summary": {
                "metrics_calculated": len(results),
                "top_nodes_by_metric": stats.top_nodes_by_metric
            }
        }
    
    # Helper methods for analysis and formatting
    def _describe_methodology(self, results: List[CentralityResult]) -> str:
        """Describe the methodological approach used"""
        metrics = [result.metric for result in results if result.scores]
        return f"Multi-metric centrality analysis using {len(metrics)} centrality measures: {', '.join(metrics)}. Graph prepared with metric-specific preprocessing."
    
    def _extract_key_findings(self, results: List[CentralityResult], stats: CentralityStats) -> List[str]:
        """Extract key findings from the analysis"""
        findings = []
        
        successful_metrics = [r.metric for r in results if r.scores]
        if len(successful_metrics) >= 5:
            findings.append(f"Comprehensive analysis completed with {len(successful_metrics)} centrality metrics")
        
        # Analyze correlation patterns
        if stats.correlation_matrix:
            high_correlations = []
            for metric1, correlations in stats.correlation_matrix.items():
                for metric2, corr in correlations.items():
                    if metric1 != metric2 and abs(corr) > 0.8:
                        high_correlations.append((metric1, metric2, corr))
            
            if high_correlations:
                findings.append(f"Strong correlations detected between {len(high_correlations)} metric pairs")
        
        # Graph characteristics
        graph_stats = stats.graph_statistics
        if graph_stats.get("density", 0) > 0.1:
            findings.append("Dense network structure detected")
        elif graph_stats.get("density", 0) < 0.01:
            findings.append("Sparse network structure detected")
        
        return findings
    
    def _assess_statistical_reliability(self, stats: CentralityStats) -> str:
        """Assess statistical reliability of results"""
        if stats.graph_statistics.get("nodes", 0) >= 100:
            return "High statistical reliability (n >= 100 nodes)"
        elif stats.graph_statistics.get("nodes", 0) >= 50:
            return "Moderate statistical reliability (n >= 50 nodes)"
        else:
            return "Limited statistical reliability (small network)"
    
    def _assess_graph_characteristics(self, graph_stats: Dict[str, Any]) -> Dict[str, str]:
        """Assess graph characteristics for academic context"""
        characteristics = {}
        
        # Size assessment
        nodes = graph_stats.get("nodes", 0)
        if nodes >= 1000:
            characteristics["size"] = "large"
        elif nodes >= 100:
            characteristics["size"] = "medium"
        else:
            characteristics["size"] = "small"
        
        # Density assessment
        density = graph_stats.get("density", 0)
        if density > 0.1:
            characteristics["density"] = "dense"
        elif density > 0.01:
            characteristics["density"] = "moderate"
        else:
            characteristics["density"] = "sparse"
        
        # Connectivity assessment
        if graph_stats.get("connected", False) or graph_stats.get("strongly_connected", False):
            characteristics["connectivity"] = "fully_connected"
        elif graph_stats.get("weakly_connected", False):
            characteristics["connectivity"] = "weakly_connected"
        else:
            characteristics["connectivity"] = "disconnected"
        
        return characteristics
    
    def _identify_methodological_considerations(self, results: List[CentralityResult], 
                                              stats: CentralityStats) -> List[str]:
        """Identify methodological considerations"""
        considerations = []
        
        # Failed calculations
        failed_metrics = [r.metric for r in results if not r.scores]
        if failed_metrics:
            considerations.append(f"Failed calculations: {', '.join(failed_metrics)}")
        
        # Graph connectivity issues
        if not stats.graph_statistics.get("connected", True):
            considerations.append("Disconnected graph may affect path-based centrality measures")
        
        # Large graph approximations
        if stats.graph_statistics.get("nodes", 0) > 1000:
            considerations.append("Large graph may require approximation algorithms")
        
        return considerations
    
    def _analyze_metric_agreements(self, correlation_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze agreements between metrics"""
        try:
            agreements = {
                "high_agreement": [],
                "low_agreement": [],
                "average_correlation": 0.0
            }
            
            all_correlations = []
            for metric1, correlations in correlation_matrix.items():
                for metric2, corr in correlations.items():
                    if metric1 != metric2:
                        all_correlations.append(abs(corr))
                        
                        if abs(corr) > 0.8:
                            agreements["high_agreement"].append((metric1, metric2, corr))
                        elif abs(corr) < 0.3:
                            agreements["low_agreement"].append((metric1, metric2, corr))
            
            if all_correlations:
                agreements["average_correlation"] = sum(all_correlations) / len(all_correlations)
            
            return agreements
            
        except Exception as e:
            logger.error(f"Metric agreement analysis failed: {e}")
            return {}
    
    def _assess_centrality_diversity(self, results: List[CentralityResult]) -> Dict[str, Any]:
        """Assess diversity of centrality results"""
        diversity = {
            "metric_types": len(results),
            "calculation_success_rate": len([r for r in results if r.scores]) / len(results) if results else 0,
            "coverage_assessment": "comprehensive" if len(results) >= 8 else "partial"
        }
        return diversity
    
    def _provide_interpretation_guidelines(self, results: List[CentralityResult], 
                                         stats: CentralityStats) -> List[str]:
        """Provide interpretation guidelines"""
        guidelines = [
            "Higher centrality scores indicate greater structural importance",
            "Consider multiple metrics for comprehensive node importance assessment",
            "Correlation patterns reveal relationships between different centrality concepts"
        ]
        
        if stats.graph_statistics.get("directed", False):
            guidelines.append("Directed graph allows distinction between in- and out-centrality")
        
        return guidelines
    
    def _suggest_further_analysis(self, results: List[CentralityResult], 
                                stats: CentralityStats) -> List[str]:
        """Suggest further analysis opportunities"""
        suggestions = [
            "Community detection to understand structural organization",
            "Temporal analysis if dynamic network data available",
            "Centrality-based node classification and prediction"
        ]
        
        if len(results) < 8:
            suggestions.append("Additional centrality metrics for comprehensive analysis")
        
        return suggestions
    
    # Additional helper methods for formatting
    def _find_highest_correlation(self, correlation_matrix: Dict[str, Dict[str, float]]) -> tuple:
        """Find highest correlation pair"""
        max_corr = -1
        max_pair = ("", "", 0)
        
        for metric1, correlations in correlation_matrix.items():
            for metric2, corr in correlations.items():
                if metric1 != metric2 and abs(corr) > max_corr:
                    max_corr = abs(corr)
                    max_pair = (metric1, metric2, corr)
        
        return max_pair
    
    def _find_lowest_correlation(self, correlation_matrix: Dict[str, Dict[str, float]]) -> tuple:
        """Find lowest correlation pair"""
        min_corr = 1
        min_pair = ("", "", 0)
        
        for metric1, correlations in correlation_matrix.items():
            for metric2, corr in correlations.items():
                if metric1 != metric2 and abs(corr) < min_corr:
                    min_corr = abs(corr)
                    min_pair = (metric1, metric2, corr)
        
        return min_pair
    
    def _calculate_average_correlation(self, correlation_matrix: Dict[str, Dict[str, float]]) -> float:
        """Calculate average correlation"""
        correlations = []
        for metric1, correlations_dict in correlation_matrix.items():
            for metric2, corr in correlations_dict.items():
                if metric1 != metric2:
                    correlations.append(abs(corr))
        
        return sum(correlations) / len(correlations) if correlations else 0.0
    
    def _summarize_connectivity(self, graph_stats: Dict[str, Any]) -> str:
        """Summarize graph connectivity"""
        if graph_stats.get("strongly_connected", False):
            return "strongly connected"
        elif graph_stats.get("weakly_connected", False):
            return "weakly connected"
        elif graph_stats.get("connected", False):
            return "connected"
        else:
            return "disconnected"
    
    def _generate_preparation_notes(self, results: List[CentralityResult]) -> List[str]:
        """Generate notes about graph preparation"""
        notes = []
        
        for result in results:
            if result.metadata.get("error"):
                notes.append(f"{result.metric}: {result.metadata['error']}")
            elif result.metadata.get("graph_type"):
                notes.append(f"{result.metric}: used {result.metadata['graph_type']} graph")
        
        return notes
    
    def _prepare_visualization_rankings(self, results: List[CentralityResult]) -> Dict[str, List]:
        """Prepare ranking data for visualization"""
        rankings = {}
        for result in results:
            if result.normalized_scores:
                sorted_scores = sorted(result.normalized_scores.items(), 
                                     key=lambda x: x[1], reverse=True)
                rankings[result.metric] = sorted_scores[:20]  # Top 20 for visualization
        return rankings
    
    def _prepare_correlation_heatmap(self, correlation_matrix: Dict[str, Dict[str, float]]) -> List[List]:
        """Prepare correlation matrix data for heatmap visualization"""
        if not correlation_matrix:
            return []
        
        metrics = list(correlation_matrix.keys())
        heatmap_data = []
        
        for metric1 in metrics:
            row = []
            for metric2 in metrics:
                corr = correlation_matrix.get(metric1, {}).get(metric2, 0.0)
                row.append(corr)
            heatmap_data.append(row)
        
        return heatmap_data
    
    def _prepare_distribution_data(self, results: List[CentralityResult]) -> Dict[str, List]:
        """Prepare centrality score distributions for visualization"""
        distributions = {}
        for result in results:
            if result.normalized_scores:
                distributions[result.metric] = list(result.normalized_scores.values())
        return distributions