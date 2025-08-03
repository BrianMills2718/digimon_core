"""Path Statistics Calculator

Calculates comprehensive statistics for path analysis results.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

from .path_data_models import PathStats
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PathStatisticsCalculator:
    """Calculate comprehensive path analysis statistics"""
    
    def calculate_path_statistics(self, graph: nx.Graph, result_data: Dict[str, Any]) -> PathStats:
        """Calculate comprehensive path analysis statistics"""
        try:
            # Extract all path lengths from results
            all_path_lengths = []
            reachable_pairs = 0
            total_pairs = 0
            
            # Process shortest path results
            if "shortest_paths" in result_data:
                for algorithm, paths in result_data["shortest_paths"].items():
                    if isinstance(paths, list):
                        for path_result in paths:
                            if isinstance(path_result, dict) and "length" in path_result:
                                total_pairs += 1
                                length = path_result["length"]
                                if length != float('inf') and path_result.get("path"):
                                    all_path_lengths.append(length)
                                    reachable_pairs += 1
            
            # Process all-pairs results
            if "all_pairs_paths" in result_data:
                all_pairs_data = result_data["all_pairs_paths"]
                if "statistics" in all_pairs_data:
                    stats = all_pairs_data["statistics"]
                    total_pairs += stats.get("total_node_pairs", 0)
                    reachable_pairs += stats.get("reachable_pairs", 0)
                    
                    # Extract path lengths from all-pairs data
                    if "all_pairs_lengths" in all_pairs_data:
                        for source, targets in all_pairs_data["all_pairs_lengths"].items():
                            for target, length in targets.items():
                                if source != target and length != float('inf'):
                                    all_path_lengths.append(length)
            
            # Calculate statistics
            if all_path_lengths:
                avg_length = float(np.mean(all_path_lengths))
                median_length = float(np.median(all_path_lengths))
                std_length = float(np.std(all_path_lengths))
                min_length = float(min(all_path_lengths))
                max_length = float(max(all_path_lengths))
            else:
                avg_length = median_length = std_length = min_length = max_length = 0.0
            
            # Calculate connectivity ratio
            connectivity_ratio = reachable_pairs / total_pairs if total_pairs > 0 else 0.0
            
            return PathStats(
                total_paths=len(all_path_lengths),
                avg_path_length=avg_length,
                median_path_length=median_length,
                std_path_length=std_length,
                min_path_length=min_length,
                max_path_length=max_length,
                reachable_pairs=reachable_pairs,
                unreachable_pairs=total_pairs - reachable_pairs,
                connectivity_ratio=connectivity_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating path statistics: {e}")
            return PathStats(
                total_paths=0, avg_path_length=0.0, median_path_length=0.0,
                std_path_length=0.0, min_path_length=0.0, max_path_length=0.0,
                reachable_pairs=0, unreachable_pairs=0, connectivity_ratio=0.0
            )
    
    def format_output(self, result_data: Dict[str, Any], output_format: str) -> Dict[str, Any]:
        """Format path analysis output"""
        try:
            if output_format == "academic":
                return self._format_academic_output(result_data)
            elif output_format == "summary":
                return self._format_summary_output(result_data)
            elif output_format == "detailed":
                return self._format_detailed_output(result_data)
            else:
                return result_data
                
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return {"error": str(e), "original_data": result_data}
    
    def _format_academic_output(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for academic research"""
        try:
            academic_output = {
                "research_summary": {
                    "analysis_type": "Comprehensive Path Analysis",
                    "methodological_approach": self._describe_methodology(result_data),
                    "key_findings": self._extract_key_findings(result_data),
                    "statistical_significance": self._assess_statistical_significance(result_data)
                },
                "quantitative_results": {
                    "path_metrics": self._extract_path_metrics(result_data),
                    "connectivity_analysis": self._extract_connectivity_metrics(result_data),
                    "algorithmic_comparison": self._compare_algorithms(result_data)
                },
                "data_quality_assessment": {
                    "sample_size": self._assess_sample_size(result_data),
                    "coverage_analysis": self._assess_coverage(result_data),
                    "reliability_indicators": self._assess_reliability(result_data)
                },
                "recommendations": {
                    "further_analysis": self._suggest_further_analysis(result_data),
                    "methodological_considerations": self._suggest_methodological_improvements(result_data)
                }
            }
            
            return academic_output
            
        except Exception as e:
            logger.error(f"Error formatting academic output: {e}")
            return {"error": str(e)}
    
    def _format_summary_output(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output as summary"""
        try:
            # Extract key metrics
            path_stats = result_data.get("statistics", {})
            
            summary = {
                "overview": {
                    "total_paths_analyzed": path_stats.get("total_paths", 0),
                    "connectivity_ratio": path_stats.get("connectivity_ratio", 0),
                    "average_path_length": path_stats.get("avg_path_length", 0)
                },
                "key_metrics": {
                    "shortest_average_distance": path_stats.get("min_path_length", 0),
                    "longest_path_distance": path_stats.get("max_path_length", 0),
                    "path_length_variability": path_stats.get("std_path_length", 0)
                },
                "algorithms_used": list(result_data.get("shortest_paths", {}).keys()),
                "analysis_scope": {
                    "reachable_node_pairs": path_stats.get("reachable_pairs", 0),
                    "unreachable_node_pairs": path_stats.get("unreachable_pairs", 0)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error formatting summary output: {e}")
            return {"error": str(e)}
    
    def _format_detailed_output(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output with full details"""
        try:
            detailed_output = {
                "complete_results": result_data,
                "analysis_metadata": {
                    "algorithms_executed": list(result_data.get("shortest_paths", {}).keys()),
                    "analysis_components": list(result_data.keys()),
                    "result_types": [type(v).__name__ for v in result_data.values()],
                    "timestamp": datetime.now().isoformat()
                },
                "data_structure_info": {
                    "shortest_paths_count": sum(len(paths) if isinstance(paths, list) else 0 
                                              for paths in result_data.get("shortest_paths", {}).values()),
                    "flow_analysis_count": len(result_data.get("flow_analysis", [])),
                    "reachability_sources": len(result_data.get("reachability_analysis", {}).get("source_reachability", {}))
                }
            }
            
            return detailed_output
            
        except Exception as e:
            logger.error(f"Error formatting detailed output: {e}")
            return {"error": str(e)}
    
    def calculate_academic_confidence(self, result_data: Dict[str, Any], graph: nx.Graph) -> float:
        """Calculate confidence score for academic use"""
        try:
            confidence_factors = []
            
            # Graph size factor
            n_nodes = len(graph.nodes)
            if n_nodes >= 100:
                confidence_factors.append(0.9)
            elif n_nodes >= 50:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Connectivity factor
            path_stats = result_data.get("statistics", {})
            connectivity_ratio = path_stats.get("connectivity_ratio", 0)
            confidence_factors.append(0.3 + 0.7 * connectivity_ratio)
            
            # Algorithm diversity factor
            algorithms_used = len(result_data.get("shortest_paths", {}))
            if algorithms_used >= 3:
                confidence_factors.append(0.9)
            elif algorithms_used >= 2:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Analysis completeness factor
            analysis_components = len(result_data.keys())
            if analysis_components >= 4:
                confidence_factors.append(0.9)
            elif analysis_components >= 3:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Data quality factor
            total_paths = path_stats.get("total_paths", 0)
            if total_paths >= 100:
                confidence_factors.append(0.9)
            elif total_paths >= 50:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors)
            
            return min(0.95, max(0.1, overall_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating academic confidence: {e}")
            return 0.5
    
    # Helper methods for academic formatting
    def _describe_methodology(self, result_data: Dict[str, Any]) -> str:
        """Describe the methodological approach used"""
        algorithms = list(result_data.get("shortest_paths", {}).keys())
        components = list(result_data.keys())
        
        methodology = f"Multi-algorithm path analysis employing {len(algorithms)} pathfinding algorithms"
        if "all_pairs_paths" in components:
            methodology += " with comprehensive all-pairs analysis"
        if "flow_analysis" in components:
            methodology += " and network flow examination"
        if "reachability_analysis" in components:
            methodology += " enhanced by reachability pattern assessment"
        
        return methodology
    
    def _extract_key_findings(self, result_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from the analysis"""
        findings = []
        
        path_stats = result_data.get("statistics", {})
        connectivity_ratio = path_stats.get("connectivity_ratio", 0)
        avg_path_length = path_stats.get("avg_path_length", 0)
        
        if connectivity_ratio > 0.8:
            findings.append("High network connectivity observed (>80% node pairs reachable)")
        elif connectivity_ratio < 0.3:
            findings.append("Low network connectivity detected (<30% node pairs reachable)")
        
        if avg_path_length < 3:
            findings.append("Short average path lengths suggest small-world characteristics")
        elif avg_path_length > 10:
            findings.append("Long average path lengths indicate potential network inefficiency")
        
        return findings
    
    def _assess_statistical_significance(self, result_data: Dict[str, Any]) -> str:
        """Assess statistical significance of results"""
        path_stats = result_data.get("statistics", {})
        total_paths = path_stats.get("total_paths", 0)
        
        if total_paths >= 1000:
            return "High statistical power (n >= 1000)"
        elif total_paths >= 100:
            return "Moderate statistical power (n >= 100)"
        elif total_paths >= 30:
            return "Limited statistical power (n >= 30)"
        else:
            return "Insufficient sample size for robust statistical inference"
    
    def _extract_path_metrics(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quantitative path metrics"""
        return result_data.get("statistics", {})
    
    def _extract_connectivity_metrics(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract connectivity metrics"""
        connectivity_metrics = {}
        
        if "reachability_analysis" in result_data:
            reachability = result_data["reachability_analysis"]
            if "global_statistics" in reachability:
                connectivity_metrics.update(reachability["global_statistics"])
        
        return connectivity_metrics
    
    def _compare_algorithms(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance of different algorithms"""
        comparison = {}
        
        if "shortest_paths" in result_data:
            for algorithm, results in result_data["shortest_paths"].items():
                if isinstance(results, list):
                    successful_paths = [r for r in results if r.get("path")]
                    comparison[algorithm] = {
                        "total_computations": len(results),
                        "successful_paths": len(successful_paths),
                        "success_rate": len(successful_paths) / len(results) if results else 0
                    }
        
        return comparison
    
    def _assess_sample_size(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess sample size adequacy"""
        path_stats = result_data.get("statistics", {})
        total_paths = path_stats.get("total_paths", 0)
        
        return {
            "total_paths_analyzed": total_paths,
            "sample_size_adequacy": "adequate" if total_paths >= 100 else "limited",
            "recommended_minimum": 100
        }
    
    def _assess_coverage(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess analysis coverage"""
        components = list(result_data.keys())
        algorithms = list(result_data.get("shortest_paths", {}).keys())
        
        return {
            "analysis_components": len(components),
            "algorithms_used": len(algorithms),
            "coverage_score": min(1.0, (len(components) * len(algorithms)) / 12)  # Normalized score
        }
    
    def _assess_reliability(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess result reliability"""
        path_stats = result_data.get("statistics", {})
        
        return {
            "connectivity_ratio": path_stats.get("connectivity_ratio", 0),
            "data_completeness": 1.0 if path_stats.get("total_paths", 0) > 0 else 0.0,
            "algorithmic_consistency": len(result_data.get("shortest_paths", {})) >= 2
        }
    
    def _suggest_further_analysis(self, result_data: Dict[str, Any]) -> List[str]:
        """Suggest further analysis opportunities"""
        suggestions = []
        
        if "flow_analysis" not in result_data:
            suggestions.append("Network flow analysis to understand capacity constraints")
        
        if "reachability_analysis" not in result_data:
            suggestions.append("Reachability analysis for comprehensive connectivity assessment")
        
        path_stats = result_data.get("statistics", {})
        if path_stats.get("total_paths", 0) < 100:
            suggestions.append("Expanded sampling for improved statistical robustness")
        
        return suggestions
    
    def _suggest_methodological_improvements(self, result_data: Dict[str, Any]) -> List[str]:
        """Suggest methodological improvements"""
        suggestions = []
        
        algorithms_used = len(result_data.get("shortest_paths", {}))
        if algorithms_used < 3:
            suggestions.append("Include additional pathfinding algorithms for comparison")
        
        if "all_pairs_paths" not in result_data:
            suggestions.append("Consider all-pairs analysis for complete path characterization")
        
        return suggestions