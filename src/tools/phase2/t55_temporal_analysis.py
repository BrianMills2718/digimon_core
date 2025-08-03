"""T55: Temporal Analysis Tool - Main Interface

Streamlined temporal analysis tool using decomposed components.
Reduced from 1,442 lines to focused interface.
"""

import time
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore

# Import decomposed temporal analysis components
from .temporal import (
    TemporalAnalysisType,
    TemporalDataLoader,
    TemporalAnalyzer
)

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class TemporalAnalysisTool(BaseTool):
    """T55: Advanced Temporal Analysis Tool
    
    Implements real temporal graph analysis using decomposed components:
    - TemporalDataLoader: Load temporal data from various sources
    - TemporalAnalyzer: Core analysis algorithms
    
    Reduced from 1,442 lines to focused tool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize temporal analysis tool with decomposed components"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T55_TEMPORAL_ANALYSIS"
        self.tool_name = "Temporal Analysis Tool"
        self.version = "2.0.0"
        
        # Initialize decomposed components
        self.data_loader = TemporalDataLoader(service_manager)
        self.analyzer = TemporalAnalyzer()
        
        # Configuration
        self.default_analysis_types = [
            TemporalAnalysisType.EVOLUTION,
            TemporalAnalysisType.CHANGE_DETECTION,
            TemporalAnalysisType.TREND_ANALYSIS
        ]
        
        logger.info(f"Initialized {self.tool_id} v{self.version} with decomposed components")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract for temporal analysis"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.tool_name,
            description="Advanced temporal graph analysis with evolution tracking and change detection",
            input_schema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "string",
                        "enum": ["neo4j", "snapshots", "edges", "events"],
                        "description": "Source of temporal data"
                    },
                    "temporal_data": {
                        "type": "object",
                        "description": "Temporal data for non-Neo4j sources"
                    },
                    "time_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                            "interval": {"type": "string"}
                        },
                        "description": "Time range for Neo4j queries"
                    },
                    "analysis_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["evolution", "change_detection", "trend_analysis", 
                                   "snapshot_comparison", "dynamic_centrality", 
                                   "temporal_paths", "community_evolution", "all"]
                        },
                        "description": "Types of temporal analysis to perform"
                    },
                    "analysis_params": {
                        "type": "object",
                        "description": "Parameters for analysis algorithms"
                    }
                },
                "required": ["data_source"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temporal_evolution": {"type": "object"},
                    "change_events": {"type": "array"},
                    "temporal_trends": {"type": "array"},
                    "analysis_summary": {"type": "object"},
                    "confidence_score": {"type": "number"}
                },
                "required": ["analysis_summary"]
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute temporal analysis with decomposed components"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Validate input
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(
                    f"Input validation failed: {validation_result['errors']}",
                    execution_time=time.time() - start_time
                )
            
            # Extract parameters
            data_source = request.input_data["data_source"]
            temporal_data = request.input_data.get("temporal_data")
            time_range = request.input_data.get("time_range")
            analysis_types_input = request.input_data.get("analysis_types", ["evolution", "change_detection"])
            analysis_params = request.input_data.get("analysis_params", {})
            
            # Convert analysis types to enum
            analysis_types = []
            for analysis_type in analysis_types_input:
                try:
                    analysis_types.append(TemporalAnalysisType(analysis_type))
                except ValueError:
                    logger.warning(f"Unknown analysis type: {analysis_type}")
            
            if not analysis_types:
                analysis_types = self.default_analysis_types
            
            logger.info(f"Starting temporal analysis: {data_source} source, {len(analysis_types)} analysis types")
            
            # Step 1: Load temporal data using decomposed loader
            snapshots = self.data_loader.load_temporal_data(
                data_source=data_source,
                temporal_data=temporal_data,
                time_range=time_range
            )
            
            if not snapshots:
                return self._create_error_result(
                    "No temporal snapshots could be loaded",
                    execution_time=time.time() - start_time
                )
            
            logger.info(f"Loaded {len(snapshots)} temporal snapshots")
            
            # Step 2: Perform analysis using decomposed analyzer
            analysis_results = self._perform_temporal_analysis(
                snapshots, analysis_types, analysis_params
            )
            
            # Step 3: Extract and format results
            temporal_evolution = self._extract_temporal_evolution(analysis_results, snapshots)
            change_events = self._extract_change_events(analysis_results)
            temporal_trends = self._extract_temporal_trends(analysis_results)
            
            # Step 4: Calculate summary and confidence
            analysis_summary = self._calculate_analysis_summary(snapshots, analysis_results)
            confidence_score = self._calculate_academic_confidence(analysis_summary, analysis_results)
            
            # Step 5: Store results (optional)
            if analysis_params.get("store_results", False):
                self._store_temporal_results(analysis_results, snapshots)
            
            # Format final output
            formatted_output = self._format_output(
                temporal_evolution, change_events, temporal_trends, 
                analysis_summary, confidence_score
            )
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            logger.info(f"Temporal analysis completed in {execution_time:.2f}s")
            
            return ToolResult(
                tool_id=self.tool_id, status="success", 
                data=formatted_output,
                metadata={
                    "snapshots_analyzed": len(snapshots),
                    "analysis_types": [at.value for at in analysis_types],
                    "execution_time": execution_time,
                    "memory_used": memory_used,
                    "data_source": data_source,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate temporal analysis input"""
        errors = []
        
        # Check required fields
        if "data_source" not in input_data:
            errors.append("data_source is required")
        elif input_data["data_source"] not in ["neo4j", "snapshots", "edges", "events"]:
            errors.append("data_source must be one of: neo4j, snapshots, edges, events")
        
        # Validate data source specific requirements
        data_source = input_data.get("data_source")
        if data_source in ["snapshots", "edges", "events"] and "temporal_data" not in input_data:
            errors.append(f"temporal_data is required for {data_source} source")
        
        # Validate analysis types
        if "analysis_types" in input_data:
            valid_types = [at.value for at in TemporalAnalysisType]
            for analysis_type in input_data["analysis_types"]:
                if analysis_type not in valid_types:
                    errors.append(f"Invalid analysis type: {analysis_type}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _perform_temporal_analysis(self, snapshots, analysis_types, analysis_params):
        """Perform temporal analysis using decomposed analyzer"""
        results = {}
        
        for analysis_type in analysis_types:
            try:
                if analysis_type == TemporalAnalysisType.EVOLUTION:
                    results["evolution"] = self.analyzer.analyze_evolution(snapshots, analysis_params)
                
                elif analysis_type == TemporalAnalysisType.CHANGE_DETECTION:
                    results["change_detection"] = self.analyzer.detect_changes(snapshots, analysis_params)
                
                elif analysis_type == TemporalAnalysisType.TREND_ANALYSIS:
                    results["trend_analysis"] = self.analyzer.analyze_trends(snapshots, analysis_params)
                
                elif analysis_type == TemporalAnalysisType.DYNAMIC_CENTRALITY:
                    results["dynamic_centrality"] = self.analyzer.analyze_dynamic_centrality(snapshots)
                
                elif analysis_type == TemporalAnalysisType.TEMPORAL_PATHS:
                    results["temporal_paths"] = self.analyzer.analyze_temporal_paths(snapshots)
                
                elif analysis_type == TemporalAnalysisType.COMMUNITY_EVOLUTION:
                    results["community_evolution"] = self.analyzer.analyze_community_evolution(snapshots)
                
                elif analysis_type == TemporalAnalysisType.SNAPSHOT_COMPARISON:
                    # Simple snapshot comparison
                    results["snapshot_comparison"] = self._compare_snapshots(snapshots, analysis_params)
                
                logger.info(f"Completed {analysis_type.value} analysis")
                
            except Exception as e:
                logger.error(f"Failed {analysis_type.value} analysis: {e}")
                results[analysis_type.value + "_error"] = str(e)
        
        return results
    
    def _compare_snapshots(self, snapshots, analysis_params):
        """Simple snapshot comparison"""
        if len(snapshots) < 2:
            return {"error": "Need at least 2 snapshots for comparison"}
        
        comparisons = []
        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]
            
            comparison = {
                "from_timestamp": prev.timestamp,
                "to_timestamp": curr.timestamp,
                "node_change": len(curr.graph.nodes) - len(prev.graph.nodes),
                "edge_change": len(curr.graph.edges) - len(prev.graph.edges),
                "density_change": curr.metrics.get("density", 0) - prev.metrics.get("density", 0)
            }
            comparisons.append(comparison)
        
        return {"comparisons": comparisons}
    
    def _extract_temporal_evolution(self, analysis_results, snapshots):
        """Extract temporal evolution information"""
        evolution_data = analysis_results.get("evolution", {})
        
        return {
            "time_span": {
                "start": snapshots[0].timestamp if snapshots else None,
                "end": snapshots[-1].timestamp if snapshots else None,
                "snapshots_count": len(snapshots)
            },
            "metric_evolution": evolution_data.get("metric_evolution", {}),
            "structural_changes": evolution_data.get("structural_changes", []),
            "evolution_summary": evolution_data.get("evolution_summary", {})
        }
    
    def _extract_change_events(self, analysis_results):
        """Extract change events from analysis results"""
        change_data = analysis_results.get("change_detection", {})
        
        change_events = []
        for event in change_data.get("change_events", []):
            change_events.append({
                "timestamp": event.timestamp,
                "change_type": event.change_type.value,
                "affected_elements": event.affected_elements,
                "magnitude": event.magnitude,
                "details": event.details
            })
        
        return change_events
    
    def _extract_temporal_trends(self, analysis_results):
        """Extract temporal trends from analysis results"""
        trend_data = analysis_results.get("trend_analysis", {})
        
        trends = []
        for trend in trend_data.get("temporal_trends", []):
            trends.append({
                "metric_name": trend.metric_name,
                "trend_direction": trend.trend_direction,
                "trend_strength": trend.trend_strength,
                "values": trend.values,
                "timestamps": trend.timestamps,
                "change_points": trend.change_points
            })
        
        return trends
    
    def _calculate_analysis_summary(self, snapshots, analysis_results):
        """Calculate comprehensive analysis summary"""
        return {
            "snapshots_analyzed": len(snapshots),
            "time_period": {
                "start": snapshots[0].timestamp if snapshots else None,
                "end": snapshots[-1].timestamp if snapshots else None
            },
            "analysis_types_completed": list(analysis_results.keys()),
            "overall_stability": analysis_results.get("evolution", {}).get("evolution_summary", {}).get("stability_score", 0),
            "total_changes_detected": len(analysis_results.get("change_detection", {}).get("change_events", [])),
            "trends_identified": len(analysis_results.get("trend_analysis", {}).get("temporal_trends", []))
        }
    
    def _calculate_academic_confidence(self, analysis_summary, analysis_results):
        """Calculate academic confidence score"""
        base_confidence = 0.7
        
        # Adjust based on data quality
        snapshots_count = analysis_summary.get("snapshots_analyzed", 0)
        if snapshots_count >= 10:
            base_confidence += 0.1
        elif snapshots_count >= 5:
            base_confidence += 0.05
        
        # Adjust based on analysis completeness
        analysis_count = len(analysis_summary.get("analysis_types_completed", []))
        if analysis_count >= 3:
            base_confidence += 0.1
        
        # Adjust based on stability of results
        stability = analysis_summary.get("overall_stability", 0)
        if stability > 0.8:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _store_temporal_results(self, analysis_results, snapshots):
        """Store temporal analysis results (placeholder)"""
        # This would store results in Neo4j or other storage
        logger.info("Storing temporal analysis results")
    
    def _format_output(self, temporal_evolution, change_events, temporal_trends, 
                      analysis_summary, confidence_score):
        """Format final output"""
        return {
            "temporal_evolution": temporal_evolution,
            "change_events": change_events,
            "temporal_trends": temporal_trends,
            "analysis_summary": analysis_summary,
            "confidence_score": confidence_score,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Simple input validation"""
        return self._validate_advanced_input(input_data)["valid"]
    
    def _handle_advanced_error(self, error: Exception, request: ToolRequest) -> ToolResult:
        """Handle errors with detailed context"""
        error_message = f"Temporal analysis failed: {str(error)}"
        logger.error(error_message, exc_info=True)
        
        return ToolResult(
            tool_id=self.tool_id, status="error", 
            data=None,
            error_message=error_message,
            metadata={
                "error_type": type(error).__name__,
                "input_data": request.input_data,
                "timestamp": datetime.now().isoformat()
            },
            execution_time=0.0
        )