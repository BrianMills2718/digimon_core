"""Community Detection Results Aggregator

Aggregates and formats community detection results for output.
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from datetime import datetime

from .community_data_models import CommunityResult, CommunityStats, CommunityDetails
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityResultsAggregator:
    """Aggregate and format community detection results"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
    
    def store_community_results(self, community_results: List[CommunityResult], 
                               source_document: str = "unknown") -> Dict[str, Any]:
        """Store community detection results in Neo4j database"""
        try:
            if not self.service_manager or not hasattr(self.service_manager, 'neo4j_service'):
                logger.warning("Neo4j service not available for storing results")
                return {"stored": False, "reason": "Neo4j service not available"}
            
            neo4j_service = self.service_manager.neo4j_service
            stored_count = 0
            
            with neo4j_service.get_driver().session() as session:
                # Store community analysis metadata
                session.run("""
                    MERGE (analysis:CommunityAnalysis {document_id: $doc_id, timestamp: $timestamp})
                    SET analysis.algorithms_used = $algorithms,
                        analysis.analysis_date = $analysis_date,
                        analysis.best_modularity = $best_modularity
                """, {
                    "doc_id": source_document,
                    "timestamp": datetime.now().isoformat(),
                    "algorithms": [r.algorithm for r in community_results],
                    "analysis_date": datetime.now().date().isoformat(),
                    "best_modularity": max((r.modularity for r in community_results), default=0.0)
                })
                
                # Store community detection results
                for result in community_results:
                    if result.communities:
                        # Store algorithm result
                        session.run("""
                            MATCH (analysis:CommunityAnalysis {document_id: $doc_id})
                            CREATE (algo_result:CommunityDetectionResult {
                                algorithm: $algorithm,
                                modularity: $modularity,
                                performance: $performance,
                                num_communities: $num_communities,
                                calculation_time: $calculation_time
                            })
                            CREATE (analysis)-[:HAS_ALGORITHM_RESULT]->(algo_result)
                        """, {
                            "doc_id": source_document,
                            "algorithm": result.algorithm,
                            "modularity": result.modularity,
                            "performance": result.performance,
                            "num_communities": result.num_communities,
                            "calculation_time": result.calculation_time
                        })
                        
                        # Store individual community assignments (sample for large graphs)
                        community_items = list(result.communities.items())
                        sample_size = min(1000, len(community_items))
                        
                        for node_id, community_id in community_items[:sample_size]:
                            try:
                                session.run("""
                                    MATCH (analysis:CommunityAnalysis {document_id: $doc_id})
                                    MERGE (node:Node {entity_id: $node_id})
                                    MERGE (community:Community {
                                        community_id: $community_id,
                                        algorithm: $algorithm,
                                        analysis_id: $doc_id
                                    })
                                    MERGE (node)-[:BELONGS_TO_COMMUNITY]->(community)
                                    MERGE (analysis)-[:HAS_COMMUNITY]->(community)
                                """, {
                                    "doc_id": source_document,
                                    "node_id": node_id,
                                    "community_id": community_id,
                                    "algorithm": result.algorithm
                                })
                                stored_count += 1
                            except Exception as e:
                                logger.warning(f"Failed to store community assignment for {node_id}: {e}")
                                continue
                
                logger.info(f"Stored {stored_count} community assignments in Neo4j")
                return {
                    "stored": True,
                    "count": stored_count,
                    "algorithms": [r.algorithm for r in community_results]
                }
                
        except Exception as e:
            logger.error(f"Failed to store community results: {e}")
            return {"stored": False, "reason": str(e)}
    
    def format_community_output(self, community_results: List[CommunityResult],
                               community_details: List[CommunityDetails],
                               stats: CommunityStats,
                               output_format: str,
                               confidence_score: float) -> Dict[str, Any]:
        """Format community detection output"""
        try:
            if output_format == "academic":
                return self._format_academic_output(community_results, community_details, stats, confidence_score)
            elif output_format == "summary":
                return self._format_summary_output(community_results, stats)
            elif output_format == "detailed":
                return self._format_detailed_output(community_results, community_details, stats, confidence_score)
            else:
                return self._format_standard_output(community_results, stats)
                
        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_academic_output(self, community_results: List[CommunityResult],
                               community_details: List[CommunityDetails],
                               stats: CommunityStats,
                               confidence_score: float) -> Dict[str, Any]:
        """Format output for academic research"""
        try:
            academic_output = {
                "research_summary": {
                    "analysis_type": "Multi-Algorithm Community Detection",
                    "methodological_approach": self._describe_methodology(community_results),
                    "key_findings": self._extract_key_findings(stats),
                    "statistical_significance": self._assess_statistical_significance(stats)
                },
                "quantitative_results": {
                    "algorithm_comparison": {
                        result.algorithm: {
                            "modularity": result.modularity,
                            "performance": result.performance,
                            "num_communities": result.num_communities,
                            "calculation_time": result.calculation_time
                        }
                        for result in community_results if result.communities
                    },
                    "best_partition": {
                        "algorithm": stats.best_algorithm,
                        "modularity": stats.best_modularity,
                        "num_communities": stats.quality_metrics.get(stats.best_algorithm, {}).get("num_communities", 0)
                    },
                    "community_structure_analysis": {
                        "size_distributions": stats.community_size_distribution,
                        "average_sizes": stats.average_community_sizes,
                        "detailed_communities": [cd.to_dict() for cd in community_details[:20]]  # Top 20
                    }
                },
                "data_quality_assessment": {
                    "confidence_score": confidence_score,
                    "graph_characteristics": self._assess_graph_characteristics(stats.graph_statistics),
                    "algorithm_agreement": self._assess_algorithm_agreement(community_results),
                    "methodological_considerations": self._identify_methodological_considerations(stats)
                },
                "network_properties": {
                    "structural_characteristics": stats.graph_statistics,
                    "community_quality_metrics": stats.quality_metrics,
                    "scalability_assessment": self._assess_scalability(stats.graph_statistics)
                },
                "recommendations": {
                    "interpretation_guidelines": self._provide_interpretation_guidelines(stats),
                    "further_analysis_suggestions": self._suggest_further_analysis(stats),
                    "methodological_improvements": self._suggest_methodological_improvements(community_results)
                }
            }
            
            return academic_output
            
        except Exception as e:
            logger.error(f"Academic output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_summary_output(self, community_results: List[CommunityResult],
                              stats: CommunityStats) -> Dict[str, Any]:
        """Format summary output"""
        try:
            summary = {
                "overview": {
                    "algorithms_tested": len(community_results),
                    "successful_algorithms": len([r for r in community_results if r.communities]),
                    "best_algorithm": stats.best_algorithm,
                    "best_modularity": stats.best_modularity
                },
                "community_summary": {
                    "num_communities_by_algorithm": {
                        result.algorithm: result.num_communities 
                        for result in community_results if result.communities
                    },
                    "average_community_sizes": stats.average_community_sizes,
                    "quality_ranking": self._rank_algorithms_by_quality(community_results)
                },
                "graph_summary": {
                    "nodes": stats.graph_statistics.get("nodes", 0),
                    "edges": stats.graph_statistics.get("edges", 0),
                    "density": stats.graph_statistics.get("density", 0),
                    "connected": stats.graph_statistics.get("connected", False)
                },
                "computational_summary": {
                    "total_computation_time": sum(r.calculation_time for r in community_results),
                    "fastest_algorithm": min(community_results, key=lambda x: x.calculation_time).algorithm if community_results else "none",
                    "most_communities": max(community_results, key=lambda x: x.num_communities).algorithm if community_results else "none"
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_detailed_output(self, community_results: List[CommunityResult],
                               community_details: List[CommunityDetails],
                               stats: CommunityStats,
                               confidence_score: float) -> Dict[str, Any]:
        """Format detailed output with all information"""
        try:
            detailed_output = {
                "complete_results": {
                    "community_results": [result.to_dict() for result in community_results],
                    "community_details": [detail.to_dict() for detail in community_details],
                    "statistics": stats.to_dict(),
                    "confidence_score": confidence_score
                },
                "algorithm_comparison": {
                    "performance_matrix": self._create_performance_matrix(community_results),
                    "quality_metrics": stats.quality_metrics,
                    "computational_efficiency": {
                        result.algorithm: {
                            "time": result.calculation_time,
                            "time_per_node": result.calculation_time / max(1, len(result.communities))
                        }
                        for result in community_results if result.communities
                    }
                },
                "visualization_data": {
                    "community_size_histograms": self._prepare_size_histograms(stats),
                    "modularity_comparison": {r.algorithm: r.modularity for r in community_results},
                    "network_layout_data": self._prepare_layout_data(community_results, stats)
                },
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "processing_summary": {
                        "successful_detections": len([r for r in community_results if r.communities]),
                        "failed_detections": len([r for r in community_results if not r.communities]),
                        "total_communities_found": sum(r.num_communities for r in community_results)
                    }
                },
                "export_options": {
                    "formats_available": ["json", "csv", "gml", "neo4j"],
                    "visualization_ready": True,
                    "research_ready": True
                }
            }
            
            return detailed_output
            
        except Exception as e:
            logger.error(f"Detailed output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_standard_output(self, community_results: List[CommunityResult],
                               stats: CommunityStats) -> Dict[str, Any]:
        """Format standard output"""
        return {
            "community_results": [result.to_dict() for result in community_results],
            "statistics": stats.to_dict(),
            "summary": {
                "best_algorithm": stats.best_algorithm,
                "best_modularity": stats.best_modularity,
                "algorithms_tested": len(community_results)
            }
        }
    
    # Helper methods for analysis and formatting
    def _describe_methodology(self, community_results: List[CommunityResult]) -> str:
        """Describe the methodological approach used"""
        algorithms = [result.algorithm for result in community_results]
        return f"Multi-algorithm community detection using {len(algorithms)} algorithms: {', '.join(algorithms)}. Quality assessed using modularity and performance metrics."
    
    def _extract_key_findings(self, stats: CommunityStats) -> List[str]:
        """Extract key findings from the analysis"""
        findings = []
        
        if stats.best_modularity > 0.3:
            findings.append(f"Strong community structure detected (modularity = {stats.best_modularity:.3f})")
        elif stats.best_modularity > 0.1:
            findings.append(f"Moderate community structure detected (modularity = {stats.best_modularity:.3f})")
        else:
            findings.append(f"Weak community structure (modularity = {stats.best_modularity:.3f})")
        
        if len(stats.algorithms_used) >= 3:
            findings.append(f"Comprehensive analysis with {len(stats.algorithms_used)} algorithms")
        
        # Analyze consistency across algorithms
        if stats.quality_metrics:
            modularities = [metrics["modularity"] for metrics in stats.quality_metrics.values()]
            if len(modularities) > 1:
                std_mod = np.std(modularities)
                if std_mod < 0.05:
                    findings.append("High agreement between algorithms")
                elif std_mod > 0.2:
                    findings.append("Significant disagreement between algorithms")
        
        return findings
    
    def _assess_statistical_significance(self, stats: CommunityStats) -> str:
        """Assess statistical significance of results"""
        graph_size = stats.graph_statistics.get("nodes", 0)
        
        if graph_size >= 1000:
            return "High statistical power (n >= 1000 nodes)"
        elif graph_size >= 100:
            return "Moderate statistical power (n >= 100 nodes)"
        elif graph_size >= 50:
            return "Limited statistical power (n >= 50 nodes)"
        else:
            return "Insufficient sample size for robust statistical inference"
    
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
        if graph_stats.get("connected", False):
            characteristics["connectivity"] = "connected"
        else:
            characteristics["connectivity"] = "disconnected"
        
        return characteristics
    
    def _assess_algorithm_agreement(self, community_results: List[CommunityResult]) -> Dict[str, Any]:
        """Assess agreement between different algorithms"""
        agreement = {"high_agreement": [], "disagreement": []}
        
        successful_results = [r for r in community_results if r.communities]
        if len(successful_results) >= 2:
            modularities = [r.modularity for r in successful_results]
            community_counts = [r.num_communities for r in successful_results]
            
            # Check modularity agreement
            mod_cv = np.std(modularities) / np.mean(modularities) if np.mean(modularities) > 0 else 1
            if mod_cv < 0.2:
                agreement["high_agreement"].append("modularity_scores")
            else:
                agreement["disagreement"].append("modularity_scores")
            
            # Check community count agreement
            count_cv = np.std(community_counts) / np.mean(community_counts) if np.mean(community_counts) > 0 else 1
            if count_cv < 0.3:
                agreement["high_agreement"].append("community_counts")
            else:
                agreement["disagreement"].append("community_counts")
        
        return agreement
    
    def _identify_methodological_considerations(self, stats: CommunityStats) -> List[str]:
        """Identify methodological considerations"""
        considerations = []
        
        # Failed algorithms
        failed_count = stats.analysis_metadata.get("failed_algorithms", 0)
        if failed_count > 0:
            considerations.append(f"{failed_count} algorithms failed to complete")
        
        # Graph characteristics
        if not stats.graph_statistics.get("connected", True):
            considerations.append("Disconnected graph may affect community detection quality")
        
        # Size considerations
        if stats.graph_statistics.get("nodes", 0) < 50:
            considerations.append("Small graph may limit community detection reliability")
        
        return considerations
    
    def _assess_scalability(self, graph_stats: Dict[str, Any]) -> Dict[str, str]:
        """Assess scalability of analysis"""
        nodes = graph_stats.get("nodes", 0)
        edges = graph_stats.get("edges", 0)
        
        scalability = {}
        
        if nodes > 10000:
            scalability["node_scalability"] = "large_scale"
        elif nodes > 1000:
            scalability["node_scalability"] = "medium_scale"
        else:
            scalability["node_scalability"] = "small_scale"
        
        if edges > 100000:
            scalability["edge_scalability"] = "high_density"
        elif edges > 10000:
            scalability["edge_scalability"] = "medium_density"
        else:
            scalability["edge_scalability"] = "low_density"
        
        return scalability
    
    def _provide_interpretation_guidelines(self, stats: CommunityStats) -> List[str]:
        """Provide interpretation guidelines"""
        guidelines = [
            "Higher modularity indicates stronger community structure",
            "Multiple algorithms provide validation of community structure",
            "Consider both modularity and performance metrics for evaluation"
        ]
        
        if stats.best_modularity > 0.3:
            guidelines.append("Strong community structure suggests meaningful network organization")
        
        return guidelines
    
    def _suggest_further_analysis(self, stats: CommunityStats) -> List[str]:
        """Suggest further analysis opportunities"""
        suggestions = [
            "Hierarchical community detection for multi-level analysis",
            "Dynamic community detection if temporal data available",
            "Community-based network analysis and prediction"
        ]
        
        if len(stats.algorithms_used) < 4:
            suggestions.append("Additional community detection algorithms for validation")
        
        return suggestions
    
    def _suggest_methodological_improvements(self, community_results: List[CommunityResult]) -> List[str]:
        """Suggest methodological improvements"""
        suggestions = []
        
        failed_algorithms = [r.algorithm for r in community_results if not r.communities]
        if failed_algorithms:
            suggestions.append(f"Investigate failures in: {', '.join(failed_algorithms)}")
        
        suggestions.extend([
            "Parameter optimization for algorithm-specific settings",
            "Ensemble methods for robust community detection",
            "Statistical validation using null models"
        ])
        
        return suggestions
    
    # Additional helper methods
    def _rank_algorithms_by_quality(self, community_results: List[CommunityResult]) -> List[tuple]:
        """Rank algorithms by quality metrics"""
        successful_results = [r for r in community_results if r.communities]
        ranked = sorted(successful_results, key=lambda x: x.modularity, reverse=True)
        return [(r.algorithm, r.modularity) for r in ranked]
    
    def _create_performance_matrix(self, community_results: List[CommunityResult]) -> Dict[str, Dict[str, float]]:
        """Create performance comparison matrix"""
        matrix = {}
        for result in community_results:
            if result.communities:
                matrix[result.algorithm] = {
                    "modularity": result.modularity,
                    "performance": result.performance,
                    "num_communities": result.num_communities,
                    "calculation_time": result.calculation_time
                }
        return matrix
    
    def _prepare_size_histograms(self, stats: CommunityStats) -> Dict[str, List]:
        """Prepare community size histograms for visualization"""
        histograms = {}
        for algorithm, size_dist in stats.community_size_distribution.items():
            histograms[algorithm] = [{"size": size, "count": count} 
                                   for size, count in size_dist.items()]
        return histograms
    
    def _prepare_layout_data(self, community_results: List[CommunityResult], 
                           stats: CommunityStats) -> Dict[str, Any]:
        """Prepare layout data for network visualization"""
        best_result = None
        for result in community_results:
            if result.algorithm == stats.best_algorithm and result.communities:
                best_result = result
                break
        
        if best_result:
            return {
                "algorithm": best_result.algorithm,
                "communities": best_result.communities,
                "modularity": best_result.modularity,
                "num_communities": best_result.num_communities
            }
        else:
            return {}