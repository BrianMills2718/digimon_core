"""Evolution Analysis

Analyzes temporal evolution, change detection, and trend analysis.
"""

from typing import Dict, List, Any
import numpy as np
from collections import defaultdict

from .temporal_data_models import TemporalSnapshot, ChangeEvent, ChangeType, TemporalTrend
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class EvolutionAnalyzer:
    """Analyzes temporal evolution and changes"""
    
    def analyze_evolution(self, snapshots: List[TemporalSnapshot], 
                         analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal evolution of graph structure"""
        try:
            evolution_results = {
                "evolution_summary": {},
                "metric_evolution": {},
                "structural_changes": []
            }
            
            if len(snapshots) < 2:
                return evolution_results
            
            # Track metric evolution
            metrics_over_time = defaultdict(list)
            timestamps = []
            
            for snapshot in snapshots:
                timestamps.append(snapshot.timestamp)
                for metric_name, value in snapshot.metrics.items():
                    if isinstance(value, (int, float)):
                        metrics_over_time[metric_name].append(value)
            
            # Calculate evolution statistics
            evolution_results["metric_evolution"] = {}
            for metric_name, values in metrics_over_time.items():
                if len(values) >= 2:
                    evolution_results["metric_evolution"][metric_name] = {
                        "values": values,
                        "timestamps": timestamps,
                        "initial_value": values[0],
                        "final_value": values[-1],
                        "change_absolute": values[-1] - values[0],
                        "change_relative": ((values[-1] - values[0]) / values[0]) if values[0] != 0 else 0,
                        "trend": self._calculate_trend(values),
                        "volatility": np.std(values) if len(values) > 1 else 0
                    }
            
            # Analyze structural changes
            for i in range(1, len(snapshots)):
                prev_snapshot = snapshots[i-1]
                curr_snapshot = snapshots[i]
                
                structural_change = self._analyze_structural_change(
                    prev_snapshot, curr_snapshot
                )
                evolution_results["structural_changes"].append(structural_change)
            
            # Create evolution summary
            evolution_results["evolution_summary"] = {
                "time_span": {
                    "start": snapshots[0].timestamp,
                    "end": snapshots[-1].timestamp,
                    "duration": len(snapshots)
                },
                "overall_growth": {
                    "nodes": snapshots[-1].metrics.get("node_count", 0) - snapshots[0].metrics.get("node_count", 0),
                    "edges": snapshots[-1].metrics.get("edge_count", 0) - snapshots[0].metrics.get("edge_count", 0)
                },
                "stability_score": self._calculate_stability_score(snapshots)
            }
            
            return evolution_results
            
        except Exception as e:
            logger.error(f"Evolution analysis failed: {e}")
            raise
    
    def detect_changes(self, snapshots: List[TemporalSnapshot], 
                      analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect significant changes between temporal snapshots"""
        try:
            change_results = {
                "change_events": [],
                "change_statistics": {},
                "anomalies": []
            }
            
            change_threshold = analysis_params.get("change_threshold", 0.1)
            
            for i in range(1, len(snapshots)):
                prev_snapshot = snapshots[i-1]
                curr_snapshot = snapshots[i]
                
                # Detect node changes
                node_changes = self._detect_node_changes(prev_snapshot, curr_snapshot)
                change_results["change_events"].extend(node_changes)
                
                # Detect edge changes
                edge_changes = self._detect_edge_changes(prev_snapshot, curr_snapshot)
                change_results["change_events"].extend(edge_changes)
                
                # Detect metric changes
                metric_changes = self._detect_metric_changes(
                    prev_snapshot, curr_snapshot, change_threshold
                )
                change_results["change_events"].extend(metric_changes)
                
                # Detect anomalies
                anomalies = self._detect_anomalies(prev_snapshot, curr_snapshot)
                change_results["anomalies"].extend(anomalies)
            
            # Calculate change statistics
            change_results["change_statistics"] = self._calculate_change_statistics(
                change_results["change_events"]
            )
            
            return change_results
            
        except Exception as e:
            logger.error(f"Change detection failed: {e}")
            raise
    
    def analyze_trends(self, snapshots: List[TemporalSnapshot], 
                      analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal trends in graph metrics"""
        try:
            trend_results = {
                "temporal_trends": [],
                "trend_summary": {},
                "predictions": {}
            }
            
            if len(snapshots) < 3:
                return trend_results
            
            # Extract time series for each metric
            metrics_series = defaultdict(list)
            timestamps = []
            
            for snapshot in snapshots:
                timestamps.append(snapshot.timestamp)
                for metric_name, value in snapshot.metrics.items():
                    if isinstance(value, (int, float)):
                        metrics_series[metric_name].append(value)
            
            # Analyze trends for each metric
            for metric_name, values in metrics_series.items():
                if len(values) >= 3:
                    trend = self._analyze_metric_trend(metric_name, values, timestamps)
                    trend_results["temporal_trends"].append(trend)
            
            # Create trend summary
            trend_results["trend_summary"] = self._create_trend_summary(
                trend_results["temporal_trends"]
            )
            
            # Generate simple predictions
            if analysis_params.get("generate_predictions", False):
                trend_results["predictions"] = self._generate_trend_predictions(
                    trend_results["temporal_trends"]
                )
            
            return trend_results
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise
    
    # Helper methods
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _analyze_structural_change(self, prev_snapshot: TemporalSnapshot, 
                                 curr_snapshot: TemporalSnapshot) -> Dict[str, Any]:
        """Analyze structural changes between two snapshots"""
        prev_nodes = set(prev_snapshot.graph.nodes)
        curr_nodes = set(curr_snapshot.graph.nodes)
        prev_edges = set(prev_snapshot.graph.edges)
        curr_edges = set(curr_snapshot.graph.edges)
        
        return {
            "timestamp": curr_snapshot.timestamp,
            "nodes_added": len(curr_nodes - prev_nodes),
            "nodes_removed": len(prev_nodes - curr_nodes),
            "edges_added": len(curr_edges - prev_edges),
            "edges_removed": len(prev_edges - curr_edges),
            "stability_score": len(curr_nodes & prev_nodes) / len(curr_nodes | prev_nodes) if (curr_nodes | prev_nodes) else 1.0
        }
    
    def _calculate_stability_score(self, snapshots: List[TemporalSnapshot]) -> float:
        """Calculate overall stability score across all snapshots"""
        if len(snapshots) < 2:
            return 1.0
        
        stability_scores = []
        for i in range(1, len(snapshots)):
            prev_nodes = set(snapshots[i-1].graph.nodes)
            curr_nodes = set(snapshots[i].graph.nodes)
            
            if prev_nodes or curr_nodes:
                jaccard = len(prev_nodes & curr_nodes) / len(prev_nodes | curr_nodes)
                stability_scores.append(jaccard)
        
        return np.mean(stability_scores) if stability_scores else 1.0
    
    def _detect_node_changes(self, prev_snapshot: TemporalSnapshot, 
                           curr_snapshot: TemporalSnapshot) -> List[ChangeEvent]:
        """Detect node additions and removals"""
        changes = []
        
        prev_nodes = set(prev_snapshot.graph.nodes)
        curr_nodes = set(curr_snapshot.graph.nodes)
        
        # Node additions
        added_nodes = curr_nodes - prev_nodes
        if added_nodes:
            changes.append(ChangeEvent(
                timestamp=curr_snapshot.timestamp,
                change_type=ChangeType.NODE_ADDITION,
                affected_elements=list(added_nodes),
                magnitude=len(added_nodes),
                details={"added_nodes": list(added_nodes)}
            ))
        
        # Node removals
        removed_nodes = prev_nodes - curr_nodes
        if removed_nodes:
            changes.append(ChangeEvent(
                timestamp=curr_snapshot.timestamp,
                change_type=ChangeType.NODE_REMOVAL,
                affected_elements=list(removed_nodes),
                magnitude=len(removed_nodes),
                details={"removed_nodes": list(removed_nodes)}
            ))
        
        return changes
    
    def _detect_edge_changes(self, prev_snapshot: TemporalSnapshot, 
                           curr_snapshot: TemporalSnapshot) -> List[ChangeEvent]:
        """Detect edge additions and removals"""
        changes = []
        
        prev_edges = set(prev_snapshot.graph.edges)
        curr_edges = set(curr_snapshot.graph.edges)
        
        # Edge additions
        added_edges = curr_edges - prev_edges
        if added_edges:
            changes.append(ChangeEvent(
                timestamp=curr_snapshot.timestamp,
                change_type=ChangeType.EDGE_ADDITION,
                affected_elements=[f"{e[0]}-{e[1]}" for e in added_edges],
                magnitude=len(added_edges),
                details={"added_edges": list(added_edges)}
            ))
        
        # Edge removals
        removed_edges = prev_edges - curr_edges
        if removed_edges:
            changes.append(ChangeEvent(
                timestamp=curr_snapshot.timestamp,
                change_type=ChangeType.EDGE_REMOVAL,
                affected_elements=[f"{e[0]}-{e[1]}" for e in removed_edges],
                magnitude=len(removed_edges),
                details={"removed_edges": list(removed_edges)}
            ))
        
        return changes
    
    def _detect_metric_changes(self, prev_snapshot: TemporalSnapshot, 
                             curr_snapshot: TemporalSnapshot, 
                             threshold: float) -> List[ChangeEvent]:
        """Detect significant metric changes"""
        changes = []
        
        for metric_name in prev_snapshot.metrics:
            if metric_name in curr_snapshot.metrics:
                prev_value = prev_snapshot.metrics[metric_name]
                curr_value = curr_snapshot.metrics[metric_name]
                
                if isinstance(prev_value, (int, float)) and isinstance(curr_value, (int, float)):
                    if prev_value != 0:
                        relative_change = abs(curr_value - prev_value) / prev_value
                        if relative_change > threshold:
                            changes.append(ChangeEvent(
                                timestamp=curr_snapshot.timestamp,
                                change_type=ChangeType.ATTRIBUTE_CHANGE,
                                affected_elements=[metric_name],
                                magnitude=relative_change,
                                details={
                                    "metric": metric_name,
                                    "previous_value": prev_value,
                                    "current_value": curr_value,
                                    "relative_change": relative_change
                                }
                            ))
        
        return changes
    
    def _detect_anomalies(self, prev_snapshot: TemporalSnapshot, 
                         curr_snapshot: TemporalSnapshot) -> List[Dict[str, Any]]:
        """Detect anomalous changes"""
        anomalies = []
        
        # Simple anomaly detection based on extreme changes
        node_change_ratio = abs(len(curr_snapshot.graph.nodes) - len(prev_snapshot.graph.nodes))
        if len(prev_snapshot.graph.nodes) > 0:
            node_change_ratio /= len(prev_snapshot.graph.nodes)
        
        if node_change_ratio > 0.5:  # 50% change threshold
            anomalies.append({
                "timestamp": curr_snapshot.timestamp,
                "type": "extreme_node_change",
                "severity": "high",
                "details": {
                    "change_ratio": node_change_ratio,
                    "previous_nodes": len(prev_snapshot.graph.nodes),
                    "current_nodes": len(curr_snapshot.graph.nodes)
                }
            })
        
        return anomalies
    
    def _calculate_change_statistics(self, change_events: List[ChangeEvent]) -> Dict[str, Any]:
        """Calculate statistics from change events"""
        if not change_events:
            return {}
        
        change_type_counts = defaultdict(int)
        total_magnitude = 0
        
        for event in change_events:
            change_type_counts[event.change_type.value] += 1
            total_magnitude += event.magnitude
        
        return {
            "total_changes": len(change_events),
            "change_type_distribution": dict(change_type_counts),
            "average_magnitude": total_magnitude / len(change_events),
            "most_frequent_change": max(change_type_counts.items(), key=lambda x: x[1])[0] if change_type_counts else None
        }
    
    def _analyze_metric_trend(self, metric_name: str, values: List[float], 
                            timestamps: List[str]) -> TemporalTrend:
        """Analyze trend for a specific metric"""
        # Calculate trend direction and strength
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Determine trend direction
        if abs(slope) < 0.01 * np.mean(values):
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Calculate trend strength (R-squared)
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        trend_strength = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Detect change points (simplified)
        change_points = []
        if len(values) > 5:
            for i in range(2, len(values) - 2):
                before_trend = np.polyfit(range(i), values[:i], 1)[0]
                after_trend = np.polyfit(range(i, len(values)), values[i:], 1)[0]
                if abs(before_trend - after_trend) > 0.1 * np.std(values):
                    change_points.append(timestamps[i])
        
        return TemporalTrend(
            metric_name=metric_name,
            values=values,
            timestamps=timestamps,
            trend_direction=direction,
            trend_strength=trend_strength,
            change_points=change_points
        )
    
    def _create_trend_summary(self, trends: List[TemporalTrend]) -> Dict[str, Any]:
        """Create summary of all trends"""
        if not trends:
            return {}
        
        direction_counts = defaultdict(int)
        avg_strength = 0
        
        for trend in trends:
            direction_counts[trend.trend_direction] += 1
            avg_strength += trend.trend_strength
        
        return {
            "total_metrics": len(trends),
            "trend_distribution": dict(direction_counts),
            "average_trend_strength": avg_strength / len(trends),
            "most_common_trend": max(direction_counts.items(), key=lambda x: x[1])[0] if direction_counts else None
        }
    
    def _generate_trend_predictions(self, trends: List[TemporalTrend]) -> Dict[str, Any]:
        """Generate simple trend predictions"""
        predictions = {}
        
        for trend in trends:
            if len(trend.values) >= 3 and trend.trend_strength > 0.5:
                # Simple linear extrapolation
                x = np.arange(len(trend.values))
                slope, intercept = np.polyfit(x, trend.values, 1)
                
                # Predict next value
                next_value = slope * len(trend.values) + intercept
                
                predictions[trend.metric_name] = {
                    "predicted_next_value": next_value,
                    "confidence": trend.trend_strength,
                    "trend_direction": trend.trend_direction
                }
        
        return predictions