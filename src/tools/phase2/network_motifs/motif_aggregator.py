"""Network Motifs Results Aggregator

Aggregates and formats motif detection results for output.
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict, Counter

from .motif_data_models import MotifInstance, MotifStats
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class MotifResultsAggregator:
    """Aggregate and format motif detection results"""
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
    
    def generate_pattern_catalog(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Generate comprehensive pattern catalog from motif instances"""
        try:
            pattern_catalog = {
                "motif_types": {},
                "pattern_frequencies": {},
                "node_participation": {},
                "edge_participation": {},
                "connectivity_patterns": {}
            }
            
            # Group motifs by type
            motifs_by_type = defaultdict(list)
            for motif in motif_instances:
                motifs_by_type[motif.motif_type].append(motif)
            
            # Analyze each motif type
            for motif_type, motifs in motifs_by_type.items():
                type_analysis = {
                    "count": len(motifs),
                    "average_significance": sum(m.significance_score for m in motifs) / len(motifs) if motifs else 0,
                    "node_size_distribution": Counter(len(m.nodes) for m in motifs),
                    "edge_count_distribution": Counter(len(m.edges) for m in motifs),
                    "pattern_variations": self._analyze_pattern_variations(motifs)
                }
                pattern_catalog["motif_types"][motif_type] = type_analysis
            
            # Pattern frequency analysis
            pattern_catalog["pattern_frequencies"] = self._calculate_pattern_frequencies(motif_instances)
            
            # Node participation analysis
            pattern_catalog["node_participation"] = self._analyze_node_participation(motif_instances)
            
            # Edge participation analysis
            pattern_catalog["edge_participation"] = self._analyze_edge_participation(motif_instances)
            
            # Connectivity patterns
            pattern_catalog["connectivity_patterns"] = self._analyze_connectivity_patterns(motif_instances)
            
            return pattern_catalog
            
        except Exception as e:
            logger.error(f"Pattern catalog generation failed: {e}")
            return {}
    
    def store_motif_results(self, motif_instances: List[MotifInstance], 
                           stats: MotifStats, source_document: str) -> bool:
        """Store motif results in Neo4j database"""
        try:
            if not self.service_manager or not hasattr(self.service_manager, 'neo4j_service'):
                logger.warning("Neo4j service not available for storing results")
                return False
            
            neo4j_service = self.service_manager.neo4j_service
            
            with neo4j_service.get_driver().session() as session:
                # Store motif analysis metadata
                session.run("""
                    MERGE (analysis:MotifAnalysis {document_id: $doc_id, timestamp: $timestamp})
                    SET analysis.total_motifs = $total_motifs,
                        analysis.motif_types = $motif_types,
                        analysis.analysis_date = $analysis_date
                """, {
                    "doc_id": source_document,
                    "timestamp": datetime.now().isoformat(),
                    "total_motifs": stats.total_motifs,
                    "motif_types": list(stats.motif_types.keys()),
                    "analysis_date": datetime.now().date().isoformat()
                })
                
                # Store individual motif instances
                for i, motif in enumerate(motif_instances[:1000]):  # Limit storage
                    session.run("""
                        MATCH (analysis:MotifAnalysis {document_id: $doc_id})
                        CREATE (motif:NetworkMotif {
                            motif_id: $motif_id,
                            motif_type: $motif_type,
                            pattern_id: $pattern_id,
                            nodes: $nodes,
                            edge_count: $edge_count,
                            significance_score: $significance_score,
                            frequency: $frequency
                        })
                        CREATE (analysis)-[:CONTAINS_MOTIF]->(motif)
                    """, {
                        "doc_id": source_document,
                        "motif_id": f"{source_document}_motif_{i}",
                        "motif_type": motif.motif_type,
                        "pattern_id": motif.pattern_id,
                        "nodes": motif.nodes,
                        "edge_count": len(motif.edges),
                        "significance_score": motif.significance_score,
                        "frequency": motif.frequency
                    })
                
                logger.info(f"Stored {min(len(motif_instances), 1000)} motif instances in Neo4j")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store motif results: {e}")
            return False
    
    def format_output(self, motif_instances: List[MotifInstance], stats: MotifStats,
                     output_format: str, confidence_score: float) -> Dict[str, Any]:
        """Format motif analysis output"""
        try:
            if output_format == "academic":
                return self._format_academic_output(motif_instances, stats, confidence_score)
            elif output_format == "summary":
                return self._format_summary_output(motif_instances, stats)
            elif output_format == "detailed":
                return self._format_detailed_output(motif_instances, stats, confidence_score)
            else:
                return self._format_standard_output(motif_instances, stats)
                
        except Exception as e:
            logger.error(f"Output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_academic_output(self, motif_instances: List[MotifInstance], 
                               stats: MotifStats, confidence_score: float) -> Dict[str, Any]:
        """Format output for academic research"""
        try:
            academic_output = {
                "research_summary": {
                    "analysis_type": "Network Motifs Detection",
                    "methodological_approach": self._describe_methodology(motif_instances, stats),
                    "key_findings": self._extract_key_findings(stats),
                    "statistical_significance": self._assess_statistical_significance(stats)
                },
                "quantitative_results": {
                    "motif_enumeration": stats.motif_types,
                    "significance_testing": {
                        "z_scores": stats.z_scores,
                        "p_values": stats.p_values,
                        "enrichment_ratios": stats.enrichment_ratios
                    },
                    "pattern_analysis": self.generate_pattern_catalog(motif_instances)
                },
                "data_quality_assessment": {
                    "sample_size": len(motif_instances),
                    "confidence_score": confidence_score,
                    "reliability_indicators": self._assess_reliability(stats),
                    "methodological_limitations": self._identify_limitations(stats)
                },
                "recommendations": {
                    "further_analysis": self._suggest_further_analysis(stats),
                    "methodological_considerations": self._suggest_methodological_improvements()
                }
            }
            
            return academic_output
            
        except Exception as e:
            logger.error(f"Academic output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_summary_output(self, motif_instances: List[MotifInstance], 
                              stats: MotifStats) -> Dict[str, Any]:
        """Format summary output"""
        try:
            # Get most significant motifs
            significant_motifs = sorted(motif_instances, 
                                      key=lambda x: x.significance_score, 
                                      reverse=True)[:10]
            
            summary = {
                "overview": {
                    "total_motifs_detected": stats.total_motifs,
                    "unique_motif_types": len(stats.motif_types),
                    "most_common_motif": max(stats.motif_types.items(), 
                                          key=lambda x: x[1])[0] if stats.motif_types else None
                },
                "motif_breakdown": stats.motif_types,
                "top_significant_motifs": [
                    {
                        "type": motif.motif_type,
                        "pattern_id": motif.pattern_id,
                        "significance": motif.significance_score,
                        "nodes": len(motif.nodes)
                    }
                    for motif in significant_motifs
                ],
                "statistical_summary": {
                    "significant_types": sum(1 for p in stats.p_values.values() if p < 0.05),
                    "highest_enrichment": max(stats.enrichment_ratios.values()) if stats.enrichment_ratios else 0,
                    "average_significance": sum(m.significance_score for m in motif_instances) / len(motif_instances) if motif_instances else 0
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_detailed_output(self, motif_instances: List[MotifInstance], 
                               stats: MotifStats, confidence_score: float) -> Dict[str, Any]:
        """Format detailed output with all information"""
        try:
            detailed_output = {
                "complete_results": {
                    "motif_instances": [motif.to_dict() for motif in motif_instances[:500]],  # Limit for size
                    "statistics": stats.to_dict(),
                    "confidence_score": confidence_score
                },
                "pattern_catalog": self.generate_pattern_catalog(motif_instances),
                "analysis_metadata": {
                    "total_instances": len(motif_instances),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "result_truncated": len(motif_instances) > 500
                },
                "export_information": {
                    "formats_available": ["json", "csv", "graphml"],
                    "visualization_ready": True,
                    "academic_citation_ready": True
                }
            }
            
            return detailed_output
            
        except Exception as e:
            logger.error(f"Detailed output formatting failed: {e}")
            return {"error": str(e)}
    
    def _format_standard_output(self, motif_instances: List[MotifInstance], 
                               stats: MotifStats) -> Dict[str, Any]:
        """Format standard output"""
        return {
            "motif_instances": [motif.to_dict() for motif in motif_instances],
            "statistics": stats.to_dict(),
            "summary": {
                "total_motifs": stats.total_motifs,
                "motif_types": stats.motif_types
            }
        }
    
    # Helper methods for analysis
    def _analyze_pattern_variations(self, motifs: List[MotifInstance]) -> Dict[str, Any]:
        """Analyze variations within a motif type"""
        variations = {
            "node_size_patterns": Counter(len(m.nodes) for m in motifs),
            "edge_patterns": Counter(len(m.edges) for m in motifs),
            "unique_patterns": len(set(m.pattern_id for m in motifs))
        }
        return variations
    
    def _calculate_pattern_frequencies(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Calculate pattern frequency statistics"""
        frequencies = Counter(m.pattern_id for m in motif_instances)
        return {
            "most_frequent": frequencies.most_common(10),
            "frequency_distribution": dict(frequencies),
            "unique_patterns": len(frequencies)
        }
    
    def _analyze_node_participation(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Analyze which nodes participate in motifs"""
        node_counts = Counter()
        for motif in motif_instances:
            for node in motif.nodes:
                node_counts[node] += 1
        
        return {
            "most_active_nodes": node_counts.most_common(20),
            "participation_distribution": dict(node_counts),
            "total_unique_nodes": len(node_counts)
        }
    
    def _analyze_edge_participation(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Analyze which edges participate in motifs"""
        edge_counts = Counter()
        for motif in motif_instances:
            for edge in motif.edges:
                edge_counts[edge] += 1
        
        return {
            "most_active_edges": edge_counts.most_common(20),
            "participation_distribution": dict(edge_counts),
            "total_unique_edges": len(edge_counts)
        }
    
    def _analyze_connectivity_patterns(self, motif_instances: List[MotifInstance]) -> Dict[str, Any]:
        """Analyze connectivity patterns in motifs"""
        connectivity_patterns = {
            "density_distribution": [],
            "size_distribution": Counter(len(m.nodes) for m in motif_instances),
            "edge_density_stats": {}
        }
        
        for motif in motif_instances:
            n_nodes = len(motif.nodes)
            n_edges = len(motif.edges)
            if n_nodes > 1:
                max_edges = n_nodes * (n_nodes - 1) // 2
                density = n_edges / max_edges if max_edges > 0 else 0
                connectivity_patterns["density_distribution"].append(density)
        
        return connectivity_patterns
    
    # Helper methods for academic formatting
    def _describe_methodology(self, motif_instances: List[MotifInstance], stats: MotifStats) -> str:
        """Describe the methodological approach used"""
        motif_types = list(stats.motif_types.keys())
        return f"Comprehensive network motif detection using {len(motif_types)} motif types: {', '.join(motif_types)}. Statistical significance assessed using random graph null models."
    
    def _extract_key_findings(self, stats: MotifStats) -> List[str]:
        """Extract key findings from the analysis"""
        findings = []
        
        if stats.total_motifs > 1000:
            findings.append(f"High motif density detected ({stats.total_motifs} instances)")
        
        significant_types = [mt for mt, p in stats.p_values.items() if p < 0.05]
        if significant_types:
            findings.append(f"Statistically significant motif types: {', '.join(significant_types)}")
        
        enriched_types = [mt for mt, ratio in stats.enrichment_ratios.items() if ratio > 2.0]
        if enriched_types:
            findings.append(f"Highly enriched motif types: {', '.join(enriched_types)}")
        
        return findings
    
    def _assess_statistical_significance(self, stats: MotifStats) -> str:
        """Assess statistical significance of results"""
        significant_count = sum(1 for p in stats.p_values.values() if p < 0.05)
        total_count = len(stats.p_values)
        
        if total_count == 0:
            return "No statistical testing performed"
        elif significant_count == 0:
            return "No statistically significant motifs detected"
        elif significant_count == total_count:
            return f"All {total_count} motif types statistically significant (p < 0.05)"
        else:
            return f"{significant_count}/{total_count} motif types statistically significant (p < 0.05)"
    
    def _assess_reliability(self, stats: MotifStats) -> Dict[str, Any]:
        """Assess reliability of results"""
        return {
            "sample_size_adequacy": "adequate" if stats.total_motifs >= 100 else "limited",
            "statistical_power": "high" if len(stats.p_values) >= 3 else "moderate",
            "motif_diversity": "high" if len(stats.motif_types) >= 5 else "moderate"
        }
    
    def _identify_limitations(self, stats: MotifStats) -> List[str]:
        """Identify methodological limitations"""
        limitations = []
        
        if stats.total_motifs < 100:
            limitations.append("Limited sample size may affect statistical power")
        
        if len(stats.motif_types) < 3:
            limitations.append("Limited motif type diversity")
        
        if not stats.p_values:
            limitations.append("No statistical significance testing performed")
        
        return limitations
    
    def _suggest_further_analysis(self, stats: MotifStats) -> List[str]:
        """Suggest further analysis opportunities"""
        suggestions = []
        
        if "temporal" not in str(stats.motif_types):
            suggestions.append("Temporal motif analysis for dynamic networks")
        
        if len(stats.motif_types) < 5:
            suggestions.append("Extended motif catalog analysis")
        
        suggestions.append("Motif-based network comparison analysis")
        suggestions.append("Higher-order motif detection (5+ nodes)")
        
        return suggestions
    
    def _suggest_methodological_improvements(self) -> List[str]:
        """Suggest methodological improvements"""
        return [
            "Increase random graph iterations for robust statistical testing",
            "Consider edge-colored motifs for multi-layer networks",
            "Implement approximate motif counting for large networks",
            "Add motif centrality analysis for node importance"
        ]